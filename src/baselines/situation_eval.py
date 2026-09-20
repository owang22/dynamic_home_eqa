"""Baselines under the human inspector's protocol, on a situation_sim run.

    cd src && python3 -m baselines.situation_eval --run ../data/situation_sim/runs/hh_s8 \
        --out ../results/situation_sim/hh_s8

The protocol is the one the Situation Sim Inspector page plays with a person:

* one walkthrough of every room on Wednesday at 18:00 and nothing else before it
  (delivered as ``room_visit`` rows, i.e. every spot in every room at once);
* 6 questions a day on Thursday..Sunday, the SAME 24 questions the page asks
  (its PRNG and object pool are ported here, so a human run and these runs
  answer identical questions);
* a look is a whole room: cost 1, plus 3 when the robot must change rooms
  (:class:`baselines.harness.RoomLook`); budget 12 a day; the robot starts each
  day in the home-base room;
* people in a looked room are listed, but pockets are never seen (a person
  sense is refused), exactly as for the human.

Writes ``bank.jsonl`` (the protocol bank), ``run_log.jsonl`` (one record per
agent x question), ``summary.json`` and ``summary.md``.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from typing import Dict, List, Optional, Sequence, Tuple

from baselines.agent import Agent
from baselines.bank import JsonlBank
from baselines.harness import QuestionRecord, RoomLook, run_episode
from baselines.policies.never_sense import NeverSense
from baselines.policies.sequential_search import SequentialSearch
from baselines.policies.voi_sense import VoIBudgetPriceSense, VoIThresholdSense
from baselines.registry import build_registered_belief
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE

DAYS = ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ---------------------------------------------------------------------------
# the page's question sequence, ported bit for bit
# ---------------------------------------------------------------------------
def _u32(x: int) -> int:
    return x & 0xFFFFFFFF


def _i32(x: int) -> int:
    x &= 0xFFFFFFFF
    return x - (1 << 32) if x & 0x80000000 else x


def _imul(a: int, b: int) -> int:
    return _i32(_i32(a) * _i32(b))


def rng32(seed: int):
    """JS: a=seed>>>0; a=a+0x6D2B79F5|0; t=imul(a^a>>>15,1|a); t=t+imul(t^t>>>7,61|t)^t;
    return ((t^t>>>14)>>>0)/2**32"""
    state = {"a": _u32(seed)}

    def nxt() -> float:
        a = _i32(state["a"])
        a = _i32(a + 0x6D2B79F5)
        state["a"] = _u32(a)
        au = _u32(a)
        t = _imul(au ^ (au >> 15), 1 | a)
        tu = _u32(t)
        t = _i32(_i32(t + _imul(tu ^ (tu >> 7), 61 | t)) ^ t)
        tu = _u32(t)
        return _u32(tu ^ (tu >> 14)) / 4294967296.0
    return nxt


_ACT_RE = re.compile(r"^(bring|pickup|trip|carry):(.+)$")


def question_sequence(seed: int, per_day: int, n_days: int, objects: Dict[str, dict],
                      truth_rows: Sequence[dict]) -> List[dict]:
    rows_for: Dict[str, List[dict]] = defaultdict(list)
    for r in truth_rows:
        rows_for[r["object_id"]].append(r)

    def activity_weight(o: str) -> int:
        acts = set()
        for r in rows_for[o]:
            m = _ACT_RE.match(r.get("cause") or "")
            if m:
                acts.add(m.group(2))
        return len(acts)

    items = [(o, activity_weight(o) + (1 if len(rows_for[o]) >= 4 else 0))
             for o in sorted(objects) if not objects[o].get("static")]
    items = [x for x in items if x[1] > 0] or [(o, 1) for o in sorted(objects)]

    def pick(r) -> str:
        tot = sum(w for _, w in items)
        u = r() * tot
        for o, w in items:
            u -= w
            if u <= 0:
                return o
        return items[-1][0]

    r = rng32(7919 * (seed + 1) + per_day)
    qs: List[dict] = []
    prev = None
    for d in range(1, n_days):
        mins = sorted(7 * 60 + int(r() * (16 * 60)) for _ in range(per_day))
        for minute in mins:
            obj = pick(r)
            if obj == prev and len(items) > 1:
                obj = pick(r)
            prev = obj
            qs.append({"obj": obj, "day": d, "minute": minute, "t": d * DAY_SECONDS + minute * 60})
    return qs


# ---------------------------------------------------------------------------
# bank: events.jsonl + walkthrough + questions
# ---------------------------------------------------------------------------
def build_bank(run_dir: pathlib.Path, out: pathlib.Path, budget: int = 12, per_day: int = 6,
               tour_minute: int = 18 * 60) -> Tuple[pathlib.Path, List[dict]]:
    rows = [json.loads(l) for l in (run_dir / "events.jsonl").read_text().splitlines() if l.strip()]
    header = rows[0]
    assert header["kind"] == "episode_header"
    state = json.loads((run_dir / "hidden_state.json").read_text())
    seed = int(state["seed"])
    n_days = int(header["n_days"])
    objects = state["household"]["objects"]
    truth = [r for r in rows if r["kind"] == "truth"]
    eid = header["episode_id"]

    def loc_at(obj: str, t: int) -> str:
        cur = None
        for r in sorted((r for r in truth if r["object_id"] == obj), key=lambda r: r["t"]):
            if r["t"] <= t:
                cur = r["receptacle_id"]
            else:
                break
        return cur

    tour_t = tour_minute * 60
    rooms: Dict[str, List[str]] = defaultdict(list)
    for rec, room in header["receptacle_rooms"].items():
        if rec != ON_PERSON:
            rooms[room].append(rec)
    # The walkthrough: positive sightings as ``initial_tour`` observations (what
    # the LLM prompts' tour tables and every belief's initial evidence read),
    # plus one room_visit per room carrying only the EMPTY spots, so the
    # exclusions reach the beliefs without duplicating the sightings.
    visits = []
    tour_obs = []
    for room in sorted(rooms):
        contents = {rec: sorted(o for o in objects if loc_at(o, tour_t) == rec) for rec in sorted(rooms[room])}
        for rec, objs in contents.items():
            for o in objs:
                tour_obs.append({"kind": "observation", "episode_id": eid, "object_id": o,
                                 "receptacle_id": rec, "t": tour_t, "source": "initial_tour"})
        empties = {rec: [] for rec, objs in contents.items() if not objs}
        if empties:
            visits.append({"kind": "room_visit", "episode_id": eid, "t": tour_t, "room": room, "contents": empties})
    qs = question_sequence(seed, per_day, n_days, objects, truth)
    questions = [{"kind": "question", "episode_id": eid, "question_id": f"q{i + 1:02d}",
                  "object_id": q["obj"], "t_query": q["t"], "day_index": q["day"],
                  "object_class": objects[q["obj"]]["cls"]} for i, q in enumerate(qs)]
    header = dict(header)
    header["budget_per_day"] = budget
    header["tour_t"] = tour_t
    header["protocol"] = {"walkthrough_t": tour_t, "questions_per_day": per_day, "first_question_day": 1,
                          "look_cost": 1, "travel_cost": 3, "room_level_looks": True, "pockets_visible": False,
                          "day0_weekday": "Wednesday"}
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        f.write(json.dumps(header) + "\n")
        for r in rows[1:]:
            f.write(json.dumps(r) + "\n")
        for o in tour_obs:
            f.write(json.dumps(o) + "\n")
        for v in visits:
            f.write(json.dumps(v) + "\n")
        for q in questions:
            f.write(json.dumps(q) + "\n")
    return out, qs


# ---------------------------------------------------------------------------
# roster
# ---------------------------------------------------------------------------
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


class ReservePacing:
    """Wraps a policy: a look is allowed only if, after paying for it, at least
    ``reserve`` budget per remaining question of the day is left. The human's
    own heuristic ("save my budget of 2 for later"); the roster has no pacing
    rule that looks at the question count."""

    def __init__(self, inner, per_day: int, reserve: float = 1.0) -> None:
        self._inner = inner; self._per_day = per_day; self._reserve = reserve
        self._day = None; self._k = 0; self._qid = None; self._ctx = None

    @property
    def name(self) -> str:
        return f"Reserve({self._reserve:g})[{self._inner.name}]"

    def reset(self, context) -> None:
        self._ctx = context; self._inner.reset(context); self._day = None; self._k = 0; self._qid = None

    def decide(self, question, prediction, budget_remaining, t, last_sense=None):
        if question.question_id != self._qid:
            self._qid = question.question_id
            if question.day_index != self._day:
                self._day, self._k = question.day_index, 0
            else:
                self._k += 1
        action = self._inner.decide(question, prediction, budget_remaining, t, last_sense)
        from baselines.types import Sense
        if isinstance(action, Sense) and self._ctx is not None:
            remaining_after = self._per_day - self._k - 1
            if budget_remaining - self._ctx.sense_cost(action.receptacle_id) < self._reserve * remaining_after:
                from baselines.types import AnswerNow
                return AnswerNow()
        return action


def policies(rng: random.Random, budget: int, per_day: int, lams: Sequence[float],
             gammas: Sequence[float], reserve: Optional[float] = None):
    out = [("never", lambda: NeverSense()),
           ("search", lambda: SequentialSearch(rng, confidence_threshold=0.9))]
    for lam in lams:
        out.append((f"voi{lam:g}", (lambda lam=lam: VoIThresholdSense(rng, lam=lam))))
    for g in gammas:
        out.append((f"voiprice{g:g}", (lambda g=g: VoIBudgetPriceSense(rng, gamma=g, budget_per_day=budget,
                                                                        questions_per_day=per_day))))
    if reserve is not None:
        out = [(f"{n}+reserve", (lambda mk=mk: ReservePacing(mk(), per_day, reserve))) for n, mk in out if n != "never"]
    return out


def run_all(bank_path: pathlib.Path, out_dir: pathlib.Path, beliefs=BELIEFS, lams=(0.02, 0.05, 0.1),
            gammas=(0.5, 1.0), seed: int = 0, budget: int = 12, per_day: int = 6,
            pockets: bool = False, reserve: Optional[float] = None) -> List[QuestionRecord]:
    bank = JsonlBank(bank_path)
    episode = next(iter(bank.episodes()))
    records: List[QuestionRecord] = []
    for bspec in beliefs:
        for pname, mk in policies(random.Random(seed), budget, per_day, lams, gammas, reserve):
            rng = random.Random(f"{seed}:{bspec}:{pname}")
            try:
                belief = build_registered_belief(dict(bspec), rng)
            except Exception as e:  # a model that cannot build here is reported, not fatal
                print(f"  skip {bspec['name']}: {type(e).__name__}: {e}", file=sys.stderr)
                break
            agent = Agent(belief=belief, policy=mk())
            rl = RoomLook(look_cost=1.0, travel_cost=3.0, person_sensing=pockets)
            recs = list(run_episode(agent, episode, room_look=rl))
            for r in recs:
                records.append(r)
            print(f"  {agent.name:60s} {sum(r.correct for r in recs):2d}/{len(recs)}  "
                  f"looks {sum(1 for r in recs for a in r.actions if a.get('type') == 'look_room'):3d}  "
                  f"budget {sum(r.budget_spent for r in recs):5.1f}", file=sys.stderr)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "run_log.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r.to_json_dict()) + "\n")
    return records


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------
def kind_of(rec: str) -> str:
    return "on_person" if rec == ON_PERSON else "out" if rec == OUT_OF_HOUSE else "spot"


def summarize(records: Sequence[QuestionRecord], qs: List[dict], human: Optional[dict] = None) -> dict:
    by_agent: Dict[str, List[QuestionRecord]] = defaultdict(list)
    for r in records:
        by_agent[r.agent].append(r)
    rows = []
    for agent, recs in sorted(by_agent.items()):
        n = len(recs)
        looks = sum(1 for r in recs for a in r.actions if a.get("type") == "look_room")
        by_day = Counter(); n_day = Counter(); by_kind = Counter(); n_kind = Counter()
        for r in recs:
            by_day[r.day_index] += int(r.correct); n_day[r.day_index] += 1
            k = kind_of(r.truth_receptacle); by_kind[k] += int(r.correct); n_kind[k] += 1
        rows.append({"agent": agent, "belief": recs[0].belief, "policy": recs[0].policy, "n": n,
                     "correct": sum(r.correct for r in recs), "acc": round(sum(r.correct for r in recs) / n, 3),
                     "looks": looks, "budget": round(sum(r.budget_spent for r in recs), 1),
                     "forced": sum(r.forced_answer for r in recs),
                     "refused_person": sum(1 for r in recs for a in r.actions if a.get("type") == "person_sense_refused"),
                     "by_day": {DAYS[d][:3]: f"{by_day[d]}/{n_day[d]}" for d in sorted(n_day)},
                     "by_truth_kind": {k: f"{by_kind[k]}/{n_kind[k]}" for k in sorted(n_kind)},
                     "wrong": [{"q": r.question_id, "obj": r.object_id, "said": r.answer_receptacle,
                                "truth": r.truth_receptacle} for r in recs if not r.correct]})
    rows.sort(key=lambda x: (-x["acc"], x["looks"]))
    # question difficulty: how many agents got each one
    per_q = defaultdict(list)
    for r in records:
        per_q[r.question_id].append(r.correct)
    difficulty = [{"q": q, "obj": next(r.object_id for r in records if r.question_id == q),
                   "truth": next(r.truth_receptacle for r in records if r.question_id == q),
                   "solved_by": f"{sum(v)}/{len(v)}"} for q, v in sorted(per_q.items())]
    out = {"agents": rows, "questions": difficulty, "n_agents": len(rows)}
    if human:
        out["human"] = human
    return out


def summary_md(s: dict, title: str) -> str:
    L = [f"# {title}", "", f"{s['n_agents']} agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.", ""]
    if s.get("human"):
        h = s["human"]
        L += [f"**Human (Oliver):** {h['correct']}/{h['n']} = {h['acc']:.0%}, {h['looks']} looks, budget {h['budget']}.", ""]
    L += ["| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in s["agents"]:
        bd, bk = a["by_day"], a["by_truth_kind"]
        L.append(f"| {a['agent']} | {a['correct']}/{a['n']} | {a['acc']:.0%} | {a['looks']} | {a['budget']} | {a['forced']} | "
                 f"{bd.get('Thu','')} | {bd.get('Fri','')} | {bd.get('Sat','')} | {bd.get('Sun','')} | "
                 f"{bk.get('spot','-')} | {bk.get('on_person','-')} | {bk.get('out','-')} |")
    L += ["", "## Question difficulty (agents that got it right)", "", "| q | object | truth | solved by |", "|---|---|---|---|"]
    for q in s["questions"]:
        L.append(f"| {q['q']} | {q['obj']} | {q['truth']} | {q['solved_by']} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=pathlib.Path, required=True, help="a situation_sim run dir (events.jsonl, hidden_state.json)")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--budget", type=int, default=12)
    ap.add_argument("--per-day", type=int, default=6)
    ap.add_argument("--pockets", action="store_true", help="allow person senses (NOT the human protocol)")
    ap.add_argument("--beliefs", nargs="*", default=None, help="subset of belief names")
    ap.add_argument("--lams", nargs="*", type=float, default=[0.02, 0.05, 0.1])
    ap.add_argument("--gammas", nargs="*", type=float, default=[0.5, 1.0])
    ap.add_argument("--human", type=pathlib.Path, default=None, help="an exported human run json to print alongside")
    ap.add_argument("--reserve", type=float, default=None, help="wrap policies in ReservePacing(reserve per remaining question)")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    bank_path, qs = build_bank(a.run, a.out / "bank.jsonl", a.budget, a.per_day)
    beliefs = tuple(b for b in BELIEFS if a.beliefs is None or b["name"] in a.beliefs)
    records = run_all(bank_path, a.out, beliefs, a.lams, a.gammas, budget=a.budget, per_day=a.per_day, pockets=a.pockets, reserve=a.reserve)
    human = None
    if a.human and a.human.exists():
        doc = json.loads(a.human.read_text())["run"]
        ans = doc.get("answers", [])
        # the human must have answered THESE questions: the sequence depends on the
        # truth log, so a regenerated household is a different quiz
        mismatch = [i for i, (q, x) in enumerate(zip(qs, ans)) if q["obj"] != x.get("obj") or q["minute"] != x.get("minute")]
        if mismatch or len(ans) != len(qs):
            raise SystemExit(f"--human run answered a different question sequence ({len(mismatch)} of {len(qs)} differ); "
                             f"run against the data the human played (data/situation_sim/as_played/...)")
        human = {"n": len(ans), "correct": sum(1 for x in ans if x.get("hit")), "acc": (sum(1 for x in ans if x.get("hit")) / len(ans)) if ans else 0.0,
                 "looks": sum(1 for l in doc.get("looks", []) if not l.get("failed")),
                 "budget": sum(l.get("cost", 0) for l in doc.get("looks", []) if not l.get("failed"))}
    s = summarize(records, qs, human)
    (a.out / "summary.json").write_text(json.dumps(s, indent=1))
    (a.out / "summary.md").write_text(summary_md(s, f"situation_sim baselines · {a.run.name}"))
    print((a.out / "summary.md").read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
