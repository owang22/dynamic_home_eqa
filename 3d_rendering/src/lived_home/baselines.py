"""Is there anything to learn? Simple predictors of where things are, scored on a
finished run.

Questions: "where is object o at day d, time T?", for every object that moves, at
10:00, 14:00, 18:00 and 22:00 (between the robot's patrols), from day 2 on. The
answer is a piece of furniture, "with <person>" or "out of the house", scored at
furniture and at room level.

Predictors:
- last known: where it was last seen
- usual place: where it was seen most often so far
- usual at this hour: where it was seen most often at this time on earlier days
  (falls back to last known before there is a day to learn from)
- mix: usual at this hour when the earlier days agree on it, else last known
The table also gives the share of questions with no earlier sighting at all
("no history"); those count as wrong for every predictor.

Each predictor is fed twice, on the same questions:
- the robot's patrol notes (lived_home.play: a patrol at 08:00, 12:00, 16:00 and
  20:00 visits about a third of the rooms and notes what is visible on each piece
  of furniture and what the residents there hold);
- the true position at every earlier 2-hour mark, a ceiling no robot reaches.

    python -m lived_home.baselines <run folder> [--seed S]   -> <run>/baselines_notes.md
    python -m lived_home.baselines <run folder> --truth      -> <run>/baselines.md
--seed is the patrol seed (default: the play session's). --truth writes the older
spot-level table from true positions only (the default before 2026-10-13).
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


NOTE_QUESTION_TIMES = ["1000", "1400", "1800", "2200"]


def score_notes(run: pathlib.Path, seed: int = 0, first_day: int = 2) -> dict:
    """The predictors fed (a) the patrol notes and (b) the true positions at every
    earlier 2-hour mark, on the same questions, scored by furniture and by room."""
    import random
    from lived_home.play import build_layout, furniture_key, load, patrols, phrase
    spec, states = load(run)
    objects = {o["id"]: o for o in spec["objects"]}
    names = {oid: phrase(o) for oid, o in objects.items()}
    layout = build_layout(spec, states)
    first = {r["id"]: r["name"].split()[0] for r in spec["residents"]}
    log = patrols(states, layout, names, random.Random(seed), first)
    by_name = {v: k for k, v in first.items()}
    room_of_f = {f["key"]: f["room"] for f in layout["furniture"]}

    def truth(state, oid):
        o, seen = state["objects"][oid], set()
        while o["relation"] == "inside" and o.get("reference_kind") == "object" \
                and o["reference"] in state["objects"] and o["reference"] not in seen:
            seen.add(o["reference"])
            o = state["objects"][o["reference"]]
        if o["relation"] in ("held_by", "worn_by", "in_pocket_of"):
            who = o["reference"]
            out = state["people"].get(who, {}).get("room") in (None, "out_of_house")
            return "out of the house" if out else f"with {who}"
        return furniture_key(state["places"][o["place"]])

    keys = sorted(states)
    true_at = {k: {oid: truth(states[k], oid) for oid in objects} for k in keys}
    movers = sorted({oid for k in keys for oid in objects if true_at[k][oid] != true_at[keys[0]][oid]})
    # sightings in time order: (day, "HHMM", furniture or "with <rid>")
    sight = collections.defaultdict(list)
    for p in log:
        t = p["time"].replace(":", "")
        for s_ in p["seen"]:
            for th, oid in zip(s_["things"], s_["oids"]):
                w = th.get("where") or ""
                who = by_name.get(w[3:-8]) if w.startswith("in ") and w.endswith("'s hands") else None
                sight[oid].append(((p["day"], t), f"with {who}" if who else s_["furniture"]))
    names_ = ["last known", "usual place", "usual at this hour", "mix"]
    tally = {src: collections.Counter() for src in ("notes", "truth")}
    for k in keys:
        d, t = k
        if d < first_day or t not in NOTE_QUESTION_TIMES:
            continue
        prev_t = f"{int(t[:2]) - 2:02d}00"            # the patrol two hours before
        for oid in movers:
            real = true_at[k][oid]
            hist = {"notes": [x for when, x in sight[oid] if when < k],
                    "truth": [true_at[j][oid] for j in keys if j < k]}
            slot = {"notes": [x for (dd, tt), x in sight[oid] if dd < d and tt == prev_t],
                    "truth": [true_at[(dd, t)][oid] for dd in range(1, d) if (dd, t) in true_at]}
            for src in tally:
                c = tally[src]
                c["n"] += 1
                if not hist[src]:
                    c["no history"] += 1
                    continue
                pred = predictors(hist[src], slot[src])
                for n in names_:
                    c[n] += pred[n] == real
                    c[n + " (room)"] += room_of_f.get(pred[n], pred[n]) == room_of_f.get(real, real)
    return {"movers": len(movers), "names": names_, "tally": {k: dict(v) for k, v in tally.items()},
            "seed": seed, "first_day": first_day}


def notes_table(res: dict, run: pathlib.Path) -> str:
    names = res["names"]
    lines = [f"# Simple predictors on {run.name}: patrol notes against true positions", "",
             f"{res['movers']} objects move at least once; each is asked about at 10:00, 14:00, 18:00 "
             f"and 22:00 from day {res['first_day']} on (between patrols). An answer is a piece of "
             "furniture, \"with <person>\" or \"out of the house\". Notes: only what the robot's "
             f"patrols saw (seed {res['seed']}). True positions: every object's real place at every "
             "earlier 2-hour mark (a ceiling, not a robot).", "",
             "Share of questions with the right furniture (in brackets: right room):", "",
             "| fed | questions | no history | " + " | ".join(names) + " |",
             "|---|---|---|" + "---|" * len(names)]
    for src, label in (("notes", "patrol notes"), ("truth", "true positions")):
        c = res["tally"][src]
        n = c["n"]
        lines.append(f"| {label} | {n} | {100 * c.get('no history', 0) / n:.0f}% | " + " | ".join(
            f"{100 * c.get(x, 0) / n:.0f}% ({100 * c.get(x + ' (room)', 0) / n:.0f}%)" for x in names) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=pathlib.Path)
    ap.add_argument("--seed", type=int, help="patrol seed (default: the play session's)")
    ap.add_argument("--truth", action="store_true", help="the old spot-level table from true positions")
    a = ap.parse_args()
    if not a.truth:
        seed = a.seed
        if seed is None:
            sess = a.run / "play" / "play_data.json"
            seed = int(json.loads(sess.read_text())["session"].rsplit("-s", 1)[1]) if sess.exists() else 0
        text = notes_table(score_notes(a.run, seed), a.run)
        (a.run / "baselines_notes.md").write_text(text)
        print(text)
        return
    run = a.run
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
    lines.append(f"| 2-{max(s['by_day'])} | {tot['n']} | " + " | ".join(
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
        lines.append(f"| 2-{max(s['by_day'])} | {tot['n']} | " + " | ".join(f"{100 * tot[n] / tot['n']:.0f}%" for n in names) + " |")
    text = "\n".join(lines) + "\n"
    (run / "baselines.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
