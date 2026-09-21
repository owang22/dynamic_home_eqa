"""Replay a patrol bank against the classical belief models.

    python3 -m baselines.patrol.run --bank hh_s0_p4.jsonl --out run_log.jsonl [--no-look]

Per question: deliver every patrol visit up to the question instant, ask
the belief, take the one free look (the room with the largest one-step
value of information under the belief; no threshold, no price), fold the
look into the belief, ask again, answer with the argmax. The answer and
the top probability are logged; the ABSTAIN rule (top probability under
a threshold) is applied at summary time because it changes nothing
downstream, so one run serves every threshold.

Room value of information under the base pipeline's semantics: a look at
room R finds the object with probability p(R) = sum of p over R's spots
(worth 1), otherwise every spot in R is zeroed and the best remaining
guess is worth max over spots outside R, so
    voi(R) = p(R) + max_{s not in R} p(s) - max(p).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys
from typing import Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.registry import build_registered_belief
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE, Episode, SenseResult

BELIEFS: Tuple[Dict[str, object], ...] = (
    {"name": "last_observation"},
    {"name": "most_frequent"},
    {"name": "timetable"},
    {"name": "markov1"},
    {"name": "periodic_persistence"},
    {"name": "smoothed_recency"},
    {"name": "hierarchy_backoff"},
    {"name": "daytype_mixture"},
    {"name": "perpetua"},
    {"name": "perpetua_star"},
)


def room_voi(p: Dict[str, float], rooms: Dict[str, List[str]]) -> Dict[str, float]:
    best = max(p.values())
    out = {}
    for room in sorted(rooms):
        inside = set(rooms[room])
        p_room = sum(p.get(r, 0.0) for r in inside)
        outside = max((v for s, v in p.items() if s not in inside), default=0.0)
        out[room] = p_room + outside - best
    return out


def choose_room(p: Dict[str, float], rooms: Dict[str, List[str]], mode: str) -> str:
    """``voi``: the room with the largest one-step value of information;
    ``top``: the room holding the belief's argmax spot (the room with the
    most belief mass when the argmax is ON_PERSON or OUT_OF_HOUSE). Ties
    go to the first room in sorted order."""
    if mode == "voi":
        score = room_voi(p, rooms)
    elif mode == "top":
        best = max(p, key=lambda r: (p[r], r))
        score = {room: (1.0 if best in recs else sum(p.get(r, 0.0) for r in recs)) for room, recs in rooms.items()}
    else:
        raise ValueError(f"unknown look mode {mode!r}")
    top = max(score.values())
    return sorted(r for r, v in score.items() if v == top)[0]


def look_results(episode: Episode, room: str, recs: Sequence[str], t: int) -> List[SenseResult]:
    present = episode.residents_in_room(room, t)
    out = []
    for rec in recs:
        contents = episode.receptacle_contents(rec, t)
        out.append(SenseResult(receptacle_id=rec, t=t, contents=contents,
                               object_classes={o: episode.object_classes.get(o, "") for o in contents},
                               residents_present=present))
    return out


SPOTS_ONLY = "spots"
"""Answer set for the confidence study: in-house spots only. The belief's
distribution is conditioned on the object being in the house (mass on
ON_PERSON / OUT_OF_HOUSE dropped, the rest renormalized); the answer is
the argmax of that and the confidence its probability. The raw top
probability and the dropped mass are logged too."""


def spots_only(dist: Dict[str, float]) -> Tuple[Dict[str, float], float]:
    dropped = sum(v for k, v in dist.items() if k in (ON_PERSON, OUT_OF_HOUSE))
    kept = {k: v for k, v in dist.items() if k not in (ON_PERSON, OUT_OF_HOUSE)}
    z = sum(kept.values())
    if z <= 0:
        n = len(kept) or 1
        return {k: 1.0 / n for k in kept}, dropped
    return {k: v / z for k, v in kept.items()}, dropped


def run_belief(spec: dict, episode: Episode, look: str, seed: int, tag: dict, answers: str = "all") -> List[dict]:
    """``look`` is ``off``, ``voi`` or ``top``; ``answers`` is ``all`` or
    :data:`SPOTS_ONLY`."""
    rng = random.Random(f"{seed}:{json.dumps(spec, sort_keys=True)}:{look}")
    belief = build_registered_belief(dict(spec), rng)
    context = episode.agent_view()
    belief.reset(context)
    for obs in episode.initial_observations:
        belief.update(obs)
    rooms: Dict[str, List[str]] = {}
    for rec in context.sensable_receptacle_ids:
        room = episode.receptacle_rooms.get(rec)
        if room is not None and rec not in (ON_PERSON, OUT_OF_HOUSE):   # pockets are never looked into
            rooms.setdefault(room, []).append(rec)
    rooms = {r: sorted(v) for r, v in sorted(rooms.items())}
    evidence = episode.evidence_stream()
    cursor = 0
    records = []
    for day_questions in episode.questions_by_day:
        for q in day_questions:
            while cursor < len(evidence) and evidence[cursor].t <= q.t_query:
                item = evidence[cursor]
                if isinstance(item, SenseResult):
                    for o in item.contents:
                        belief.ensure_object(o, item.object_classes.get(o, ""))
                belief.update(item)
                cursor += 1
            belief.ensure_object(q.object_id, q.object_class)
            pred = belief.predict(q.object_id, q.t_query)
            rec = {**tag, "belief": belief.name, "day_index": q.day_index, "question_id": q.question_id,
                   "object_id": q.object_id, "object_class": q.object_class, "t_query": q.t_query,
                   "answer_before_look": pred.argmax,
                   "top_prob_before_look": round(pred.distribution.get(pred.argmax, 0.0), 4)}
            if look != "off":
                room = choose_room(dict(pred.distribution), rooms, look)
                results = look_results(episode, room, rooms[room], q.t_query)
                found = any(q.object_id in r.contents for r in results)
                for r in results:
                    for o in r.contents:
                        belief.ensure_object(o, r.object_classes.get(o, ""))
                    belief.update(r)
                pred = belief.predict(q.object_id, q.t_query)
                rec.update({"look_room": room, "found_in_look": found})
            truth = episode.true_location(q.object_id, q.t_query)
            if answers == SPOTS_ONLY:
                dist, dropped = spots_only(dict(pred.distribution))
                answer = max(dist, key=lambda r: (dist[r], r)) if dist else pred.argmax
                rec.update({"raw_top_prob": round(pred.distribution.get(pred.argmax, 0.0), 4),
                            "raw_answer": pred.argmax, "p_outside": round(dropped, 4),
                            "answer": answer, "top_prob": round(dist.get(answer, 0.0), 4)})
            else:
                answer = pred.argmax
                rec.update({"answer": answer, "top_prob": round(pred.distribution.get(answer, 0.0), 4)})
            rec.update({"truth": truth, "correct": answer == truth,
                        "correct_before_look": rec["answer_before_look"] == truth})
            records.append(rec)
    return records


def run_bank(bank_path: pathlib.Path, look: str, beliefs=BELIEFS, seed: int = 0, answers: str = "all") -> List[dict]:
    header = json.loads(bank_path.read_text().splitlines()[0])
    episode = next(iter(JsonlBank(bank_path).episodes()))
    tag = {"household": header["household_id"], "patrol_hours": header["patrol_hours"], "look": look,
           "patrol_label": header.get("patrol_label", f"p{header['patrol_hours']}"),
           "seed": int(header.get("seed", seed))}
    out = []
    for spec in beliefs:
        try:
            recs = run_belief(spec, episode, look, seed, tag, answers)
        except Exception as e:  # a model that cannot build here is reported, not fatal
            print(f"  skip {spec['name']}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        n_ok = sum(r["correct"] for r in recs)
        print(f"  {tag['household']} p{tag['patrol_hours']} look={look} {recs[0]['belief']:50s} "
              f"{n_ok:3d}/{len(recs)}", file=sys.stderr, flush=True)
        out.extend(recs)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--look", default="voi", choices=("off", "voi", "top"))
    ap.add_argument("--beliefs", nargs="*", default=None)
    ap.add_argument("--answers", default="all", choices=("all", SPOTS_ONLY))
    a = ap.parse_args(argv)
    beliefs = tuple(b for b in BELIEFS if a.beliefs is None or b["name"] in a.beliefs)
    recs = run_bank(a.bank, a.look, beliefs, answers=a.answers)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
