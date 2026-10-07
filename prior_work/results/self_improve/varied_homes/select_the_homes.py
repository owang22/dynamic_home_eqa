#!/usr/bin/env python3
"""Stage 2 of the selection: which generated homes are kept, and where the rest went.

Stage 1 (pick_the_seeds.py) chose which seeds to simulate from the floor plan and the
residents. This stage looks at the month that came out and applies the four bars in
which_lever_is_wrong.py - rooms, how concentrated the answers are, how many objects
the illness moves, how many of those land outside the busiest three rooms - plus one
completeness test, because a bank that generated but is empty in a window would
otherwise look like a pass.

Every bar is a property of the world. Not one of them is any arm's score: no learner,
no counting method and no language model is run anywhere in this file. The lazy-robot
check is run afterwards, on the selected set, as an independent verification - it is
not consulted here.

Nothing is deleted. Every generated bank stays in all_generated/banks; the selected
and rejected directories are hard links to those same files, so a reader can see the
whole population and the reason each home is in the pile it is in.

    python3 results/self_improve/varied_homes/select_the_homes.py
"""
import argparse
import collections
import json
import os
import pathlib
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from self_improve.frozen_household import FrozenHousehold  # noqa: E402
from which_lever_is_wrong import levers, verdict            # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
EXPECTED_QUESTIONS = 744          # per_day 24 over the scored days
QUESTION_TOLERANCE = 0.97         # the bank builder cannot always place 24 a day inside
                                  # the 30-minute gap rule, and three homes came out at
                                  # 738-740 of 744. Five missing questions is not an
                                  # incomplete run; an empty window is. Set after seeing
                                  # that, and it is a completeness test, not a lever:
                                  # nothing about the world is being selected here.
MIN_ASKED_OBJECTS = 8             # check_scenario's power bar, applied per home


def completeness(household):
    """What every bank must contain. A run that looks complete because everything it
    did do succeeded is the failure mode this catches."""
    problems = []
    n_q = len(household.questions)
    if n_q < EXPECTED_QUESTIONS * QUESTION_TOLERANCE:
        problems.append(f"{n_q} questions, expected about {EXPECTED_QUESTIONS}")
    by_window = collections.Counter()
    for q in household.questions:
        by_window[q.get("stage")] += 1
    for window in ("lead", "sick", "return"):
        if by_window.get(window, 0) == 0:
            problems.append(f"no questions in the {window} window")
    if len(household.asked_objects) < MIN_ASKED_OBJECTS:
        problems.append(f"only {len(household.asked_objects)} asked-about objects, "
                        f"needs {MIN_ASKED_OBJECTS}")
    return problems


def link(src: pathlib.Path, dst_dir: pathlib.Path):
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if dst.exists():
        return dst
    try:
        os.link(src, dst)
    except OSError:
        dst.write_bytes(src.read_bytes())
    return dst


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--generated", default=str(HERE / "all_generated"))
    ap.add_argument("--selected", default=str(HERE / "selected"))
    ap.add_argument("--rejected", default=str(HERE / "rejected"))
    ap.add_argument("--json", dest="json_out", default=str(HERE / "SELECTION.json"))
    a = ap.parse_args(argv)

    gen = pathlib.Path(a.generated) / "banks"
    paths = sorted(gen.glob("*.jsonl"), key=lambda p: int(p.stem.split("_")[1][1:]))
    if not paths:
        print(f"no banks under {gen}")
        return 2

    rows, kept, dropped = [], [], []
    for path in paths:
        hh = FrozenHousehold(path)
        row = levers(hh)
        row["incomplete"] = completeness(hh)
        bad = verdict(row)
        if row["incomplete"]:
            row["failing_lever"] = "incomplete"
            row["why"] = "; ".join(row["incomplete"])
        else:
            row["failing_lever"] = bad[0] if bad else None
            row["why"] = bad[1] if bad else None
        row["path"] = str(path)
        rows.append(row)
        (kept if row["failing_lever"] is None else dropped).append(row)

    sel, rej = pathlib.Path(a.selected) / "banks", pathlib.Path(a.rejected) / "banks"
    # These two directories are nothing but hard links into all_generated/banks, which
    # holds the only copy of every bank and is never touched. Rebuilding the links from
    # scratch keeps a home from sitting in both piles after a rerun; no output is lost,
    # because the file itself stays in all_generated.
    for d in (sel, rej):
        if d.is_dir():
            for old_link in d.glob("*.jsonl"):
                old_link.unlink()
    for row in kept:
        link(pathlib.Path(row["path"]), sel)
    for row in dropped:
        link(pathlib.Path(row["path"]), rej)

    stage1 = HERE / "stage1_seed_selection.json"
    s1 = json.loads(stage1.read_text()) if stage1.exists() else None

    print("THE SELECTION, both numbers.\n")
    if s1:
        print(f"  seeds looked at (floor plan and residents only): {s1['n_seeds_looked_at']}")
        print(f"  seeds that passed stage 1 and were simulated:    {s1['n_kept']}")
    print(f"  homes generated:                                 {len(rows)}")
    print(f"  homes kept:                                      {len(kept)}")
    if s1:
        print(f"  overall yield from the seeds looked at:           "
              f"{len(kept) / s1['n_seeds_looked_at'] * 100:.1f}%")
    print()
    fails = collections.Counter(r["failing_lever"] for r in dropped)
    print("rejected at stage 2 because:")
    for k, v in fails.most_common():
        print(f"  {k:16s} {v:4d} homes")
    print()
    head = (f"{'home':10s}{'rooms':>6}{'top-3':>7}{'asked':>7}{'movers':>8}"
            f"{'OUT':>9}{'controls':>10}  kept / lever")
    print(head)
    print("-" * len(head))
    for row in rows:
        print(f"{row['household'].replace('_t03',''):10s}{row['rooms']:>6}"
              f"{row['top3_share']*100:>6.0f}%{row['asked_objects']:>7}{row['n_movers']:>8}"
              f"{str(row['n_movers_out']) + '/' + str(row['n_movers']):>9}"
              f"{row['n_controls']:>10}  "
              f"{'KEPT' if row['failing_lever'] is None else 'no: ' + row['failing_lever']}")

    busiest = collections.Counter(r for row in kept for r in row["busiest"])
    dests = collections.Counter(k for row in kept for k in row["destination_rooms"])
    print(f"\namong the {len(kept)} kept homes:")
    print(f"  the busiest three rooms are, counted over homes: "
          f"{dict(busiest.most_common())}")
    print(f"  the illness's destination rooms are:             {dict(dests.most_common())}")
    print(f"  movers per home: "
          f"{min(r['n_movers'] for r in kept)}-{max(r['n_movers'] for r in kept)}; "
          f"controls per home: {min(r['n_controls'] for r in kept)}-"
          f"{max(r['n_controls'] for r in kept)}")

    out = {
        "what_was_selected_on": (
            "stage 1: floor plan and residents (pick_the_seeds.py). stage 2: rooms, "
            "concentration of answers, number of objects the illness moves, how many "
            "of those land outside the busiest three rooms, and completeness "
            "(which_lever_is_wrong.py). No arm's score, no learner and no language "
            "model was used in either stage."),
        "n_seeds_looked_at": s1["n_seeds_looked_at"] if s1 else None,
        "n_seeds_simulated": len(rows),
        "n_homes_kept": len(kept),
        "kept": [r["household"] for r in kept],
        "rejected": {r["household"]: {"lever": r["failing_lever"], "why": r["why"]}
                     for r in dropped},
        "homes": rows,
    }
    pathlib.Path(a.json_out).write_text(json.dumps(out, indent=2))
    print(f"\nselected banks (hard links): {sel}")
    print(f"rejected banks (hard links, nothing deleted): {rej}")
    print(f"wrote {a.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
