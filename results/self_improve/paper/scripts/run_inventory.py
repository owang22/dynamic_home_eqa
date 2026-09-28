#!/usr/bin/env python3
"""Every finished cell on disk: wave, arm directory, household, questions a day, last day,
scored rows. Keyed on the CELL DIRECTORY, never on `how_memory_is_written`: the LastSeen and
prior-only arms both record `how_memory_is_written = "incremental edits"`
(src/self_improve/overnight_wave.py:124-125), so keying on that field silently merges three
different arms into one row.

    python3 results/self_improve/paper/scripts/run_inventory.py
"""
import collections
import glob
import json


def main() -> int:
    rows = []
    for f in glob.glob("results/self_improve/**/cells/*/*/cell.json", recursive=True):
        d = json.load(open(f))
        p = f.split("results/self_improve/")[1]
        rows.append((p.split("/cells/")[0], p.split("/cells/")[1].split("/")[0],
                     d.get("household"), d.get("questions_per_day"), d.get("last_day"),
                     len(d.get("searches", [])), d.get("sensing_arm"),
                     d.get("how_memory_is_written")))
    by_run = collections.defaultdict(list)
    for r in rows:
        by_run[(r[0], r[3], r[4])].append(r)
    for key in sorted(by_run):
        print(f"\n== wave={key[0]}  questions_a_day={key[1]}  last_day={key[2]}")
        by_arm = collections.defaultdict(list)
        for r in by_run[key]:
            by_arm[r[1]].append((r[2], r[5], r[6], r[7]))
        for arm, cells in sorted(by_arm.items()):
            print(f"   {arm:56s} {len(cells)} homes, {sum(c[1] for c in cells):5d} rows"
                  f" | sensing={cells[0][2]} | memory={cells[0][3]}"
                  f" | {' '.join(sorted(c[0] for c in cells))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
