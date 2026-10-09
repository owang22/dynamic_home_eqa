"""Is there anything to learn? Simple predictors of where things are, scored on a
finished run.

Positions at fixed times each day are rebuilt by replaying the run's event log
from the household's start positions. A question is "where is object o at day d,
time T?", asked for every object that moves at least once in the run. The answer
is its base place: the spot it is at (through any bag it is in), "with <person>"
when someone holds, wears or pockets it at home, or "out of the house".

Each predictor sees the true positions at all earlier question times, as if
the robot had looked at everything then. That is far more than a robot sees, so
these are ceilings for history-based methods, not robot results:
- last known: where it was at the previous question time (2 hours earlier)
- usual place: the place it was at most often so far
- usual at this hour: the place it was at most often at this time on earlier
  days (falls back to last known before there is a day to learn from)
- mix: usual at this hour when the earlier days agree on it, else last known

Usage: python -m lived_home.baselines <run folder>
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

TIMES = [h * 60 for h in range(8, 23, 2)]


def replay(run: pathlib.Path) -> dict:
    """{(day, minute): {object: base place}} at each question time."""
    spec_path = run / "household_created.json"
    spec = json.loads((spec_path if spec_path.exists() else run / "household.json").read_text())
    where = {o["id"]: dict(o["start"]) for o in spec["objects"]}
    events = [json.loads(l) for l in (run / "events.jsonl").read_text().splitlines() if l.strip()]
    out_of_house = {}                       # person -> True while out
    days = sorted({e["day"] for e in events})
    states, i = {}, 0
    events.sort(key=lambda e: (e["day"], e["minute"]))     # stable: same-minute order kept
    for d in days:
        for t in TIMES:
            while i < len(events) and (events[i]["day"], events[i]["minute"]) < (d, t):
                e = events[i]
                if e.get("object") in where and e.get("to_pos"):
                    where[e["object"]] = dict(e["to_pos"])
                if e["verb"] == "leave_home":
                    out_of_house[e["resident"]] = True
                elif e["verb"] in ("come_home", "go") and out_of_house.get(e["resident"]):
                    out_of_house[e["resident"]] = False
                i += 1
            states[(d, t)] = {o: base(o, where, out_of_house) for o in where}
    return states


def base(o: str, where: dict, out: dict) -> str:
    seen, pos = set(), where[o]
    while pos.get("at") == "inside" and pos["carrier"] in where and pos["carrier"] not in seen:
        seen.add(pos["carrier"])
        pos = where[pos["carrier"]]
    if pos.get("at") == "place":
        return pos["place"]
    if pos.get("at") in ("hand", "worn", "pocket"):
        return "out of the house" if out.get(pos["person"]) else f"with {pos['person']}"
    return "unknown"


def predictors(history: list, slot_history: list) -> dict:
    last = history[-1]
    usual = collections.Counter(history).most_common(1)[0][0]
    if slot_history:
        slot_counts = collections.Counter(slot_history).most_common()
        usual_hour = slot_counts[0][0]
        agree = slot_counts[0][1] >= 2 and slot_counts[0][1] / len(slot_history) > 0.5
    else:
        usual_hour, agree = last, False
    return {"last known": last, "usual place": usual, "usual at this hour": usual_hour,
            "mix": usual_hour if agree else last}


def score(run: pathlib.Path) -> dict:
    states = replay(run)
    keys = sorted(states)
    movers = sorted({o for k in keys for o in states[k] if states[k][o] != states[keys[0]][o]})
    room_of = {}
    spec = json.loads((run / "household.json").read_text())
    for p in spec["layout"]["places"]:
        room_of[p["id"]] = p["room"]
    names = ["last known", "usual place", "usual at this hour", "mix"]
    by_day = collections.defaultdict(lambda: collections.Counter())
    moved_since = collections.defaultdict(lambda: collections.Counter())
    for idx, k in enumerate(keys):
        if idx == 0:
            continue
        d, t = k
        for o in movers:
            hist = [states[keys[j]][o] for j in range(idx)]
            slot = [states[(dd, t)][o] for dd in range(1, d) if (dd, t) in states]
            pred = predictors(hist, slot)
            truth = states[k][o]
            changed = truth != hist[-1]
            by_day[d]["n"] += 1
            moved_since[d]["n"] += changed
            for n in names:
                hit = pred[n] == truth
                room_hit = room_of.get(pred[n], pred[n]) == room_of.get(truth, truth)
                by_day[d][n] += hit
                by_day[d][n + " (room)"] += room_hit
                if changed:
                    moved_since[d][n] += hit
    return {"movers": len(movers), "objects": len(states[keys[0]]), "names": names,
            "by_day": {d: dict(c) for d, c in sorted(by_day.items())},
            "moved_since": {d: dict(c) for d, c in sorted(moved_since.items())}}


def main() -> None:
    run = pathlib.Path(sys.argv[1])
    s = score(run)
    names = s["names"]
    lines = [f"# Simple predictors on {run.name}", "",
             f"{s['movers']} of {s['objects']} objects move at least once; questions are about "
             f"those, at {len(TIMES)} times a day (08:00 to 22:00, every 2 hours). Each predictor "
             "sees the true positions at all earlier question times (a ceiling, not a robot).", "",
             "Share of questions answered with the right spot (in brackets: right room):", "",
             "| day | questions | " + " | ".join(names) + " |",
             "|---|---|" + "---|" * len(names)]
    tot = collections.Counter()
    for d, c in s["by_day"].items():
        lines.append(f"| {d} | {c['n']} | " + " | ".join(
            f"{100 * c[n] / c['n']:.0f}% ({100 * c[n + ' (room)'] / c['n']:.0f}%)" for n in names) + " |")
        if d >= 2:
            tot.update(c)
    lines.append(f"| 2-7 | {tot['n']} | " + " | ".join(
        f"{100 * tot[n] / tot['n']:.0f}% ({100 * tot[n + ' (room)'] / tot['n']:.0f}%)" for n in names) + " |")
    lines += ["", "Only the questions where the object moved since the previous question time "
              "(the cases where looking 2 hours ago does not help):", "",
              "| day | questions | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    tot = collections.Counter()
    for d, c in s["moved_since"].items():
        if not c["n"]:
            continue
        lines.append(f"| {d} | {c['n']} | " + " | ".join(f"{100 * c[n] / c['n']:.0f}%" for n in names) + " |")
        if d >= 2:
            tot.update(c)
    if tot["n"]:
        lines.append(f"| 2-7 | {tot['n']} | " + " | ".join(f"{100 * tot[n] / tot['n']:.0f}%" for n in names) + " |")
    text = "\n".join(lines) + "\n"
    (run / "baselines.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
