#!/usr/bin/env python3
"""Did this run choose the room after reasoning, or before it?

`choice_schema` declared `room` before `why` until 2026-09-25 and `why` before `room` after
(src/self_improve/search_driven.py:277-305). The server enforces the schema while generating and
every call sets enable_thinking False, so under the old order the room was named after zero tokens
of deliberation. The same change raised the `why` cap from 240 characters to 1,200.

That cap is the discriminator, and it is measurable from the rows on disk: a cell that ran under
the old schema cannot have an explanation longer than 240 characters and piles up at exactly 240,
while a cell under the new one runs past it. No need to date the runs.

    python3 results/self_improve/paper/scripts/reason_before_room.py
"""
import collections
import glob
import json


def main() -> int:
    per_wave = collections.defaultdict(lambda: collections.Counter())
    for f in sorted(glob.glob("results/self_improve/*/cells/*/*/searches.jsonl")):
        wave = f.split("results/self_improve/")[1].split("/cells/")[0]
        arm = f.split("/cells/")[1].split("/")[0]
        if arm in ("last_seen_no_model",):
            continue
        c = per_wave[wave]
        for line in open(f):
            r = json.loads(line)
            if r.get("kind") != "search":
                continue
            for why in r.get("why_each_room") or []:
                n = len(why)
                c["explanations"] += 1
                c["at_exactly_240"] += (n == 240)
                c["over_240"] += (n > 240)
                c["longest"] = max(c["longest"], n)
    print(f"{'wave':30s}{'explanations':>13s}{'at exactly 240':>16s}{'over 240':>10s}"
          f"{'longest':>9s}  verdict")
    for wave in sorted(per_wave):
        c = per_wave[wave]
        verdict = ("reason BEFORE the room (the 1,200 cap)" if c["over_240"]
                   else "room BEFORE the reason (the 240 cap)")
        print(f"{wave:30s}{c['explanations']:13d}{c['at_exactly_240']:16d}{c['over_240']:10d}"
              f"{c['longest']:9d}  {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
