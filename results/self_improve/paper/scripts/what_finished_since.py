#!/usr/bin/env python3
"""Every cell that finished after a date, with the room chooser it ran under.

The chooser is read from the cell's OWN rows, not from its date: the old schema named the room
before the reason and capped the explanation at 240 characters, the new one reasons first and
allows 1,200, so a cell with any explanation past 240 reasoned first
(src/self_improve/search_driven.py:277-305).

    python3 results/self_improve/paper/scripts/what_finished_since.py [YYYY-MM-DD]
"""
import datetime
import glob
import json
import pathlib
import sys


def chooser(cell, sensing_arm):
    # THE MECHANICAL ARMS ALSO FILL `why_each_room`, with the rule's own words - "the room it was
    # last seen in" - so a length test alone calls last seen "room before reason". It made no model
    # call at all and has no schema, so the arm has to be read first.
    if sensing_arm in ("last seen, no model", "fixed rotation", "random"):
        return "no model call (mechanical)"
    longest = 0
    for line in (cell / "searches.jsonl").open():
        r = json.loads(line)
        if r.get("kind") == "search":
            for why in r.get("why_each_room") or []:
                longest = max(longest, len(why))
    if longest == 0:
        return "no model call (mechanical arm)"
    return "reason before room" if longest > 240 else "ROOM BEFORE REASON"


def main(argv) -> int:
    since = datetime.datetime.fromisoformat(argv[1] if len(argv) > 1 else "2026-09-26")
    rows = []
    for path in glob.glob("results/self_improve/**/cells/*/*/cell.json", recursive=True):
        cell = pathlib.Path(path).parent
        when = datetime.datetime.fromtimestamp(cell.joinpath("cell.json").stat().st_mtime)
        if when < since:
            continue
        d = json.load(open(path))
        p = path.split("results/self_improve/")[1]
        rows.append((when, p.split("/cells/")[0], p.split("/cells/")[1].split("/")[0],
                     d.get("household"), d.get("last_day"), d.get("questions_per_day"),
                     chooser(cell, d.get("sensing_arm"))))
    rows.sort()
    print(f"{len(rows)} cells finished on or after {since:%Y-%m-%d}\n")
    print(f"{'finished':17s}{'wave':32s}{'arm':36s}{'home':13s}"
          f"{'last day':>9s}{'q/day':>7s}  chooser")
    for when, wave, arm, home, last, qpd, how in rows:
        print(f"{when:%Y-%m-%d %H:%M}  {wave:32s}{arm:36s}{home:13s}{last:9d}{qpd:7d}  {how}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
