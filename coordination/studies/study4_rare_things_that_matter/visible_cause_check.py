#!/usr/bin/env python3
"""Was the cause of each rare move in the robot's own record before it was first asked?

For every place change in a cell: the first question about the object asked before the cell had
sighted it at its new place (the "unseen" slice), the looks the cell made between the move and
that question, and whether any of them shows the cause:
  strict   the causing resident seen in the cause room (the ill resident in the bedroom for the
           pill box going out; the ill resident in the room they got up to for it coming back;
           the driver in the landing room for the keys);
  anywhere the causing resident seen in any room (home, when the pill box moves: they are not
           at work; back, when the keys land);
  prior    a look in the 24 h before the move that saw the resident in the cause room (what a
           method would have had to go on before the move happened at all).
A look that sees the resident in the room where the object now is also sees the object, which is
why "strict" can only be true in the minute between the resident arriving and the object following.
Prints the per-move record for the homes named with --detail and the counts over every home.

    python3 coordination/studies/study4_rare_things_that_matter/visible_cause_check.py --load 8 --detail hh_s2_t03 hh_s63_t03
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from score_rare_movers import LOADS, searches  # noqa: E402

DAY = 86400


def hm(t):
    d, s = divmod(int(t), DAY)
    return f"d{d:02d} {s // 3600:02d}:{(s % 3600) // 60:02d}"


def looks_of(cell):
    out = []
    with (cell / "looks.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("kind") == "look":
                out.append(r)
    out.sort(key=lambda r: r["time"])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", type=int, choices=(24, 8), default=8)
    ap.add_argument("--arm", default="last_seen_no_model")
    ap.add_argument("--detail", nargs="*", default=["hh_s2_t03", "hh_s63_t03"])
    a = ap.parse_args(argv)
    banks, wave = LOADS[a.load]["banks"], LOADS[a.load]["wave"]
    cells = wave / "cells" / a.arm
    homes = sorted((p.name for p in cells.iterdir() if (p / "looks.jsonl").exists()),
                   key=lambda n: int(n.split("_")[1][1:]))
    tot = {"moves": 0, "with_unseen_q": 0, "strict": 0, "anywhere": 0, "prior": 0, "looks_between": 0,
           "pill_box": {"moves": 0, "strict": 0, "anywhere": 0, "prior": 0},
           "car_keys": {"moves": 0, "strict": 0, "anywhere": 0, "prior": 0}}
    print(f"ordinary load {a.load} a day; arm {a.arm}")
    for home in homes:
        side = json.loads((banks / f"{home}_rare_moves.json").read_text())
        bank_q = {json.loads(l)["question_id"]: json.loads(l) for l in (banks / f"{home}.jsonl").open()
                  if '"kind": "question"' in l}
        rows = searches(cells / home)
        looks = looks_of(cells / home)
        # the real names, as the looks record them
        names = {}
        for l in looks:
            for who in l["residents_seen"]:
                names.setdefault(who.lower(), who)
        name_of = {}
        for m in side["moves"]:
            pass
        # resident_1 -> name via the bank's objects: the pill box is pill_box_<name> owned by the ill resident
        for oid, o in side["objects"].items():
            if o["owner"]:
                name_of[o["owner"]] = oid.split("_")[-1].capitalize()
        # the others: from the household's own object ids in the cell's searches
        detail = home in a.detail
        if detail:
            print(f"\n=== {home} ===")
        shown = {"pill_box": 0, "car_keys": 0}
        for m in side["moves"]:
            if not m["counts_as_rare_move"]:
                continue
            obj, t_m, cls = m["object_id"], m["t"], side["objects"][m["object_id"]]["cls"]
            who = name_of.get(m["resident"])
            if who is None:
                # keys: the driver's name is not on a rare-mover object; take it from the move words
                who = m["words"].split(" ")[0]
            cause_room = m["cause_room"]
            # first unseen question about this object after the move (within 24 h)
            qs = sorted((r for qid, r in rows.items() if r["object_id"] == obj
                         and bank_q[qid].get("rare_move_t") == t_m), key=lambda r: r["time"])
            seen_times = [s_["time"] for l in looks for s_ in l["sightings"]
                          if s_["object_id"] == obj and s_["place_id"] == m["dest"] and l["time"] > t_m]
            first_seen = min(seen_times) if seen_times else None
            q_star = next((r for r in qs if first_seen is None or r["time"] <= first_seen), None)
            tot["moves"] += 1
            tot[cls]["moves"] += 1
            if q_star is None:
                if detail and shown[cls] < (2 if cls == "pill_box" else 3):
                    print(f"  {hm(t_m)} {obj} -> {m['dest']} ({m['words']}): no unseen question (first sighting at new place {hm(first_seen) if first_seen else 'never'}, first question {hm(qs[0]['time']) if qs else 'none'})")
                    shown[cls] += 1
                continue
            tot["with_unseen_q"] += 1
            between = [l for l in looks if t_m <= l["time"] < q_star["time"]]
            strict = [l for l in between if l["targets"][0]["name"] == cause_room and who in l["residents_seen"]]
            anywhere = [l for l in between if who in l["residents_seen"]]
            prior = [l for l in looks if t_m - DAY <= l["time"] < t_m and l["targets"][0]["name"] == cause_room
                     and who in l["residents_seen"]]
            tot["looks_between"] += len(between)
            for k, v in (("strict", strict), ("anywhere", anywhere), ("prior", prior)):
                if v:
                    tot[k] += 1
                    tot[cls][k] += 1
            if detail and shown[cls] < (2 if cls == "pill_box" else 3):
                shown[cls] += 1
                print(f"  {hm(t_m)} {obj}: {m['src']} -> {m['dest']} in the {cause_room}; cause: {m['words']}")
                print(f"      first unseen question {q_star['question_id']} at {hm(q_star['time'])} "
                      f"({(q_star['time'] - t_m) / 60:.0f} min after); last-seen opened {q_star['rooms_opened']}, "
                      f"first guess {'right' if q_star.get('found_at_step') == 1 else 'wrong'}")
                print(f"      looks between move and question: {len(between)}: "
                      + (", ".join(f"{hm(l['time'])} {l['targets'][0]['name']} (people: {', '.join(l['residents_seen']) or 'nobody'})" for l in between) or "none"))
                print(f"      cause visible before the question: strict {'YES' if strict else 'no'}, "
                      f"{who} seen anywhere at home {'YES' if anywhere else 'no'}, "
                      f"{who} seen in the {cause_room} in the 24 h before the move {'YES (' + str(len(prior)) + ' looks)' if prior else 'no'}")
                if cls == "pill_box":
                    # the illness itself: was the ill resident seen resting by day (bedroom or living) on earlier sick days?
                    rest = [l for l in looks if l["time"] < q_star["time"] and (l["time"] // DAY) >= 14
                            and l["targets"][0]["name"] in (cause_room, "living") and who in l["residents_seen"]
                            and 9 * 3600 <= l["time"] % DAY <= 18 * 3600]
                    print(f"      the illness in the record before this question: {who} seen in the {cause_room} or the living room "
                          f"between 09:00 and 18:00 on a sick day in {len(rest)} looks")
    # every unseen question, not just the first after each move: is the cause in the record by then?
    allq = {"first_hour": {"n": 0, "strict": 0, "anywhere": 0, "prior": 0, "looks": 0},
            "later": {"n": 0, "strict": 0, "anywhere": 0, "prior": 0, "looks": 0}}
    for home in homes:
        side = json.loads((banks / f"{home}_rare_moves.json").read_text())
        bank_q = {json.loads(l)["question_id"]: json.loads(l) for l in (banks / f"{home}.jsonl").open()
                  if '"kind": "question"' in l}
        rows = searches(cells / home)
        looks = looks_of(cells / home)
        name_of = {o["owner"]: oid.split("_")[-1].capitalize() for oid, o in side["objects"].items() if o["owner"]}
        by_t = {m["t"]: m for m in side["moves"] if m["counts_as_rare_move"]}
        for qid, r in rows.items():
            qq = bank_q[qid]
            if not qq.get("within_24h_of_rare_move"):
                continue
            m = by_t[qq["rare_move_t"]]
            t_m = m["t"]
            seen = any(s_["object_id"] == r["object_id"] and s_["place_id"] == m["dest"] and t_m < l["time"] < r["time"]
                       for l in looks for s_ in l["sightings"])
            if seen:
                continue
            who = name_of.get(m["resident"]) or m["words"].split(" ")[0]
            room = m["cause_room"]
            between = [l for l in looks if t_m <= l["time"] < r["time"]]
            k = "first_hour" if qq.get("in_first_hour_after_rare_move") else "later"
            allq[k]["n"] += 1
            allq[k]["looks"] += len(between)
            allq[k]["strict"] += any(l["targets"][0]["name"] == room and who in l["residents_seen"] for l in between)
            allq[k]["anywhere"] += any(who in l["residents_seen"] for l in between)
            allq[k]["prior"] += any(t_m - DAY <= l["time"] < t_m and l["targets"][0]["name"] == room
                                    and who in l["residents_seen"] for l in looks)
    print(f"\n=== every unseen question, over {len(homes)} homes, load {a.load} ===")
    for k, v in allq.items():
        print(f"  {k:10s} n {v['n']:4d}; looks since the move {v['looks'] / max(1, v['n']):.1f} on average; cause in the record by then: "
              f"strict {v['strict']}, resident seen anywhere {v['anywhere']}, resident in the cause room in the 24 h before the move {v['prior']}")
    print(f"\n=== counts over {len(homes)} homes, load {a.load} ===")
    print(f"  place changes {tot['moves']}; with an unseen question {tot['with_unseen_q']}; "
          f"looks between move and first unseen question: {tot['looks_between'] / max(1, tot['with_unseen_q']):.1f} on average")
    print(f"  cause visible before the first unseen question: strict {tot['strict']}, resident seen anywhere {tot['anywhere']}, "
          f"resident seen in the cause room in the 24 h before the move {tot['prior']}")
    for cls in ("pill_box", "car_keys"):
        c = tot[cls]
        print(f"    {cls:9s} moves {c['moves']:3d}: strict {c['strict']}, anywhere {c['anywhere']}, prior {c['prior']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
