"""Rule baselines (no LLM) on the lab history runs: how hard are the questions, and what must a model beat?

    python -m simulation.lab_history.baselines.rules            # all runs in ../runs, writes rules_results.json

Each rule answers from the dog's events up to the question's t only. An object counts as seen when the camera
named it exactly ("red umbrella"); misnamed sightings ("umbrella") are invisible to the rules, as they would be to
a plain string match. A person counts as seen at a place when their look is in people_notes. The question text
gives the object's description and the person's look, so the rules get the same handle a model would.

Scoring is exact match with the gold place ("not in the lab" is an answer like any other). Results are split by
question kind, history length, stale/fresh (where_now) and time since the last routine shift, each with n and a
95% Wilson interval; cells with n < 30 are marked thin.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from ..generate import split_colour  # noqa: F401  (kept so the naming rule lives in one place)
from ..world import WEEKDAYS

RUNS = Path(__file__).resolve().parents[1] / "runs"
OUT = Path(__file__).resolve().parent / "rules_results.json"
DAY = 86400.0
AWAY = "not in the lab"
MIN_N = 30


def load(path):
    return [json.loads(line) for line in open(path)]


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


class History:
    """The dog's events for one run, indexed for the rules."""

    def __init__(self, events, routines):
        self.events = events
        self.t = [e["t"] for e in events]
        self.desc = {o["name"]: o["desc"] for o in routines["objects"]}
        self.look = {p["name"]: p["look"] for p in routines["people"]}
        self.start = routines["config"]["start"]
        self.desks = {p for p, v in routines["places"].items() if v["kind"] == "desk"}
        self.sight = defaultdict(list)       # object/person -> [(t, place)]
        self.looks_at = defaultdict(list)    # place -> [t] every look at it
        by_desc = {d: n for n, d in self.desc.items()}
        by_look = {l: n for n, l in self.look.items()}
        for e in events:
            self.looks_at[e["place"]].append(e["t"])
            for o in e["seen"]["objects"]:
                name = by_desc.get(f"{o['colour']} {o['name']}".strip())
                if name:
                    self.sight[name].append((e["t"], e["place"]))
            for look in filter(None, e["seen"]["people_notes"].split("; ")):
                if look in by_look:
                    self.sight[by_look[look]].append((e["t"], e["place"]))

    def before(self, entity, t, places=None):
        s = [x for x in self.sight[entity] if x[0] <= t]
        return [x for x in s if x[1] in places] if places else s


def most_frequent(s):
    return Counter(p for _, p in s).most_common(1)[0][0] if s else None


def place_rules(h: History, entity, t, places=None):
    """Answers of each place rule for where an entity is at t. None means the rule has nothing to say."""
    s = h.before(entity, t, places)
    out = {}
    out["last_seen"] = s[-1][1] if s else None
    out["most_frequent_all"] = most_frequent(s)
    out["most_frequent_7d"] = most_frequent([x for x in s if x[0] > t - 7 * DAY]) or out["most_frequent_all"]
    votes = Counter()
    for ts, p in s:
        votes[p] += math.exp(-(t - ts) / (3 * DAY))          # half-weight after about 2 days
    out["recency_vote"] = votes.most_common(1)[0][0] if votes else None
    # claims: last seen, unless that spot was looked at later and the entity wasn't there; then the usual place
    claim = out["last_seen"]
    if s:
        last_t, last_p = s[-1]
        if any(last_t < lt <= t for lt in h.looks_at[last_p]):
            others = Counter(p for _, p in s if p != last_p)
            claim = others.most_common(1)[0][0] if others else last_p
    out["claims"] = claim
    return out


def usual_rules(h: History, entity, t, weekday):
    """Where an object usually is on a weekday: from sightings on that weekday."""
    import datetime as dt
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Los_Angeles")
    s = h.before(entity, t)
    wd = [(ts, p) for ts, p in s if dt.datetime.fromtimestamp(ts, tz).weekday() == weekday]
    recent = [x for x in wd if x[0] > t - 28 * DAY]
    out = {
        "weekday_most_frequent_all": most_frequent(wd),
        "weekday_most_frequent_4w": most_frequent(recent) or most_frequent(wd),
        "most_frequent_all": most_frequent(s),
    }
    # seen on other days in the last 4 weeks but never on this weekday: say it's out on this weekday
    seen_recent = [x for x in s if x[0] > t - 28 * DAY]
    out["weekday_4w_or_away"] = most_frequent(recent) or (AWAY if seen_recent else most_frequent(wd))
    return out


def answer_rules(h: History, q):
    if q["kind"] == "where_now":
        return place_rules(h, q["entity"], q["t"])
    if q["kind"] == "last_in_lab":
        return place_rules(h, q["entity"], q["t"])
    if q["kind"] == "desk_now":
        return place_rules(h, q["entity"], q["t"], places=h.desks)
    if q["kind"] == "usual_place":
        wd = next(i for i, d in enumerate(WEEKDAYS) if f"on a {d}" in q["question"])
        return usual_rules(h, q["entity"], q["t"], wd)
    raise ValueError(q["kind"])


def gold(q):
    return q["answer"]["place"] if q["kind"] == "last_in_lab" else q["answer"]


def shift_phase(q, routines, start_ts):
    days = [start_ts + d * DAY for d in routines["shift_days"]]
    before = [d for d in days if d <= q["t"]]
    if not before:
        return "before_first_shift"
    since = (q["t"] - before[-1]) / DAY
    return "0-7d_after_shift" if since < 7 else "7d+_after_shift"


def run_one(run_dir):
    routines = json.loads((run_dir / "routines.json").read_text())
    events, qs = load(run_dir / "events.jsonl"), load(run_dir / "questions.jsonl")
    h = History(events, routines)
    import datetime as dt
    from zoneinfo import ZoneInfo
    start_ts = dt.datetime.fromisoformat(routines["config"]["start"]).replace(tzinfo=ZoneInfo("America/Los_Angeles")).timestamp()
    rows = []
    for q in qs:
        g = gold(q)
        for rule, ans in answer_rules(h, q).items():
            rows.append({"run": run_dir.name, "days": routines["config"]["days"], "q": q["id"], "kind": q["kind"],
                         "rule": rule, "answer": ans, "gold": g, "correct": ans == g,
                         "stale": q.get("stale") if q["kind"] == "where_now" else None,
                         "gold_away": g == AWAY, "phase": shift_phase(q, routines, start_ts)})
    return rows


def table(rows, keys):
    cells = defaultdict(lambda: [0, 0])
    for r in rows:
        k = tuple(r[x] for x in keys)
        cells[k][0] += r["correct"]
        cells[k][1] += 1
    out = []
    for k, (c, n) in sorted(cells.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        out.append({**dict(zip(keys, k)), "n": n, "correct": c, "acc": round(c / n, 3), "ci95": wilson(c, n),
                    "thin": n < MIN_N})
    return out


def main():
    rows = []
    for d in sorted(RUNS.iterdir()):
        if (d / "questions.jsonl").exists():
            rows += run_one(d)
    where = [r for r in rows if r["kind"] == "where_now"]
    res = {
        "about": __doc__.strip().split("\n\n")[0],
        "runs": sorted({r["run"] for r in rows}),
        "n_questions": len({(r["run"], r["q"]) for r in rows}),
        "by_kind": table(rows, ["kind", "rule"]),
        "by_kind_days": table(rows, ["kind", "days", "rule"]),
        "where_now_by_stale": table(where, ["stale", "rule"]),
        "where_now_by_gold_away": table(where, ["gold_away", "rule"]),
        "by_kind_phase": table(rows, ["kind", "phase", "rule"]),
    }
    OUT.write_text(json.dumps(res, indent=1))
    rows_out = OUT.with_name("rules_answers.jsonl")
    with open(rows_out, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    print(f"{res['n_questions']} questions over {len(res['runs'])} runs -> {OUT.name}, {rows_out.name}")
    for r in res["by_kind"]:
        print(f"  {r['kind']:12} {r['rule']:26} {r['acc']:.3f}  {r['ci95']}  n={r['n']}{'  thin' if r['thin'] else ''}")
    for r in res["where_now_by_stale"]:
        print(f"  where_now stale={r['stale']!s:5} {r['rule']:20} {r['acc']:.3f}  n={r['n']}")


if __name__ == "__main__":
    main()
