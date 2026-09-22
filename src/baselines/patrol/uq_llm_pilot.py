"""PILOT: does the multiple-choice channel work, and does offering the FULL spot list fix it?

Written 22 Sept after the shipped channel was found to answer "J) somewhere else" on 1480 of 1480 questions -
including when the model's own free-text answer was one of the nine listed options and was correct. That made
``conf_token`` equal to P("somewhere else") throughout (mean 0.756), so the "token probability" confidence line
and every conformal set built on it were measuring a catch-all bucket rather than belief about a place.

This runs a handful of real questions through the real prompt builder and compares option-list variants:

  short9   the shipped form: the 9 spots the 24 h counter ranks highest, plus "J) somewhere else"
  full     every spot in the house, no catch-all
  full_oth every spot in the house, plus "somewhere else" (isolates the catch-all from the truncation)

For each it reports whether the picked letter is the truth, whether it agrees with the model's own free-text
answer, and how much probability mass lands on the truth - which is what a conformal set is actually built from.

    python3 -m baselines.patrol.uq_llm_pilot --bank BANK --memory longcontext --days 16 --n 8
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import sys
import urllib.request
from collections import defaultdict
from typing import Dict, List

from baselines.bank import JsonlBank
from baselines.patrol.bocpd import NEGATIVE, DiscountedMostFrequent
from baselines.patrol.llm import CONF_SCHEMA, ENDPOINT, MODEL, Memory, parse_conf, question_messages
from baselines.patrol.run import spots_only
from baselines.types import ON_PERSON, OUT_OF_HOUSE, SenseResult

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def chat(msgs, max_tokens, temperature=0.0, n=1, schema=None, logprobs=False, endpoint=ENDPOINT, model=MODEL):
    body = {"model": model, "messages": msgs, "max_tokens": max_tokens, "temperature": temperature, "n": n,
            "seed": 0, "chat_template_kwargs": {"enable_thinking": False}}
    if schema is not None:
        body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
    if logprobs:
        body["logprobs"] = True
        body["top_logprobs"] = 20
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=600).read())


def letter_mass(choice, letters):
    """Renormalised probability over the option letters, read off the first generated token."""
    lp = (choice.get("logprobs") or {}).get("content") or []
    if not lp:
        return {}
    out = {}
    for t in lp[0].get("top_logprobs", []):
        tok = t["token"].strip().strip('"').strip("*")
        if tok in letters:
            out[tok] = out.get(tok, 0.0) + math.exp(t["logprob"])
    s = sum(out.values())
    return {k: v / s for k, v in out.items()} if s > 0 else {}


def ask_mcq(msgs, options, with_other, endpoint, model):
    """-> (picked spot or 'other', mass on each spot, raw first-token content)"""
    letters = ALPHABET[:len(options) + (1 if with_other else 0)]
    body = "\n".join(f"{letters[i]}) {s}" for i, s in enumerate(options))
    if with_other:
        body += f"\n{letters[len(options)]}) somewhere else"
    base = msgs[-1]["content"].split("\nReply with JSON")[0]
    mcq = base + "\n\nChoose the single most likely spot:\n" + body + "\nAnswer with the letter only."
    d = chat(msgs[:-1] + [{"role": "user", "content": mcq}], 2, logprobs=True, endpoint=endpoint, model=model)
    ch = d["choices"][0]
    raw = (ch["message"].get("content") or "").strip().strip('"').strip("*")
    lm = letter_mass(ch, set(letters))
    picked = options[letters.index(raw[:1])] if raw[:1] in letters[:len(options)] else "other"
    mass = {options[letters.index(k)] if k in letters[:len(options)] else "other": v for k, v in lm.items()}
    return picked, mass, raw[:1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", type=pathlib.Path, required=True)
    ap.add_argument("--memory", default="longcontext")
    ap.add_argument("--days", type=int, default=16)
    ap.add_argument("--n", type=int, default=8, help="how many questions to pilot (spread over the days)")
    ap.add_argument("--endpoint", default=ENDPOINT)
    ap.add_argument("--model", default=MODEL)
    a = ap.parse_args(argv)

    header = json.loads(a.bank.read_text().splitlines()[0])
    episode = next(iter(JsonlBank(a.bank).episodes()))
    day_names = {int(k): v for k, v in header["day_names"].items()}
    cards = header["protocol"]["residents"]
    names = {c["resident_id"]: c["name"] for c in cards}
    rooms: Dict[str, List[str]] = defaultdict(list)
    for rec, room in sorted(episode.receptacle_rooms.items()):
        if rec not in (ON_PERSON, OUT_OF_HOUSE):
            rooms[room].append(rec)
    rooms = {r: sorted(v) for r, v in rooms.items()}
    rec_room = {rec: room for room, recs in rooms.items() for rec in recs}
    allowed = {r for r in episode.receptacle_ids if r not in (ON_PERSON, OUT_OF_HOUSE)}
    full_spots = sorted(allowed)
    memory = Memory(rooms, rec_room, names)
    counter = DiscountedMostFrequent(random.Random(0), half_life_h=24.0, **NEGATIVE["off"])
    counter.reset(episode.agent_view())
    for obs in episode.initial_observations:
        counter.update(obs)
    tour_t = int(header["tour_t"])
    evidence = list(episode.evidence_stream())
    cursor = 0
    memory.update_group(tour_t, list(episode.initial_observations) + [e for e in evidence if e.t == tour_t], day_names)
    while cursor < len(evidence) and evidence[cursor].t <= tour_t:
        counter.update(evidence[cursor])
        cursor += 1

    picked_qs = []
    for day_questions in episode.questions_by_day:
        for q in day_questions:
            if q.day_index > a.days:
                break
            while cursor < len(evidence) and evidence[cursor].t <= q.t_query:
                t = evidence[cursor].t
                grp = []
                while cursor < len(evidence) and evidence[cursor].t == t:
                    grp.append(evidence[cursor])
                    cursor += 1
                memory.update_group(t, grp, day_names)
                for e in grp:
                    if isinstance(e, SenseResult):
                        for o in e.contents:
                            counter.ensure_object(o, e.object_classes.get(o, ""))
                    counter.update(e)
            counter.ensure_object(q.object_id, q.object_class)
            if q.day_index >= a.days - 3:      # pilot the shift days, where the channel matters most
                msgs = question_messages(memory, a.memory, q, day_names, cards, rooms, int(header["patrol_hours"]),
                                         False, [], None, None, "conf", header.get("patrol_times") or None,
                                         header.get("protocol", {}).get("question_moments", ""),
                                         header.get("protocol", {}).get("feedback_delay_min"))
                dist, _ = spots_only(dict(counter.predict(q.object_id, q.t_query).distribution))
                short9 = [s for s, _ in sorted(dist.items(), key=lambda kv: (-kv[1], kv[0]))[:9]]
                picked_qs.append((q, msgs, short9, episode.true_location(q.object_id, q.t_query)))
                if len(picked_qs) >= a.n:
                    break
        if len(picked_qs) >= a.n:
            break

    print(f"PILOT  bank={a.bank.name}  memory={a.memory}  {len(picked_qs)} questions  "
          f"({len(full_spots)} spots in the house)\n", flush=True)
    tally = defaultdict(lambda: {"right": 0, "agrees": 0, "other": 0, "mass": 0.0, "n": 0})
    for q, msgs, short9, truth in picked_qs:
        d = chat(msgs, 260, 0.0, 1, CONF_SCHEMA, endpoint=a.endpoint, model=a.model)
        free, conf, _, _ = parse_conf(d["choices"][0]["message"]["content"], allowed)
        prompt_chars = sum(len(m["content"]) for m in msgs)
        print(f"day {q.day_index:2d}  {q.object_id:<20s} truth={truth:<22s} free-text={free} "
              f"({'RIGHT' if free == truth else 'wrong'}, says {conf})  prompt~{prompt_chars//4} tok")
        for name, opts, with_other in (("short9  ", short9, True), ("full    ", full_spots, False),
                                       ("full+oth", full_spots, True)):
            picked, mass, raw = ask_mcq(msgs, opts, with_other, a.endpoint, a.model)
            t = tally[name]
            t["n"] += 1
            t["right"] += int(picked == truth)
            t["agrees"] += int(picked == free)
            t["other"] += int(picked == "other")
            t["mass"] += mass.get(truth, 0.0)
            top = sorted(mass.items(), key=lambda kv: -kv[1])[:3]
            print(f"    {name}  letter={raw!r:5s} picked={picked:<22s} "
                  f"{'RIGHT' if picked == truth else 'wrong':5s}  P(truth)={mass.get(truth, 0.0):.3f}  "
                  f"top: {', '.join(f'{k}={v:.2f}' for k, v in top)}")
        print(flush=True)
    print("=" * 100)
    print(f"{'variant':10s} {'n':>3s} {'picks truth':>12s} {'agrees w/ free-text':>20s} "
          f"{'says somewhere-else':>20s} {'mean P(truth)':>14s}")
    for name, t in tally.items():
        n = t["n"]
        print(f"{name:10s} {n:3d} {100*t['right']/n:11.0f}% {100*t['agrees']/n:19.0f}% "
              f"{100*t['other']/n:19.0f}% {t['mass']/n:14.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
