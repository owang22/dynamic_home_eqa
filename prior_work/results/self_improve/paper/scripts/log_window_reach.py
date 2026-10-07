#!/usr/bin/env python3
"""How far back the sighting log reaches on day 32, for the objects asked about on day 32.

`the_log_the_robot_reads.what_you_have_seen_of` lists the newest
HOW_MANY_SIGHTINGS_TO_SHOW = 40 sightings of the asked object and replaces the rest with one
summary line naming the rooms, their counts and the oldest day
(src/self_improve/the_log_the_robot_reads.py:27, 66-110). By day 32 a frequently seen object has
far more than 40 sightings, so the dated lines may not reach back into the first illness at all.
This measures it from the cell's own looks.jsonl.

    python3 results/self_improve/paper/scripts/log_window_reach.py
"""
import collections
import json
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
from self_improve import search_driven as sd  # noqa: E402
from self_improve.frozen_household import FrozenHousehold  # noqa: E402

CAP = 40
BANKS = pathlib.Path("results/self_improve/varied_homes/all_generated_v2_twice/banks")
WAVE = pathlib.Path("results/self_improve/wave_the_second_illness/cells")
SPELL_1 = range(14, 24)


def main() -> int:
    for arm in ("the_log_and_notes_about_the_routine",):
        for name in ("hh_s2_t03", "hh_s32_t03", "hh_s48_t03"):
            home = FrozenHousehold(BANKS / f"{name}.jsonl")
            movers = sd.the_movers(home)
            seen = collections.defaultdict(list)
            for line in (WAVE / arm / name / "looks.jsonl").open():
                for s in json.loads(line).get("sightings", []):
                    seen[s["object_id"]].append((s["time"], s["day"]))
            rows = []
            for q in home.questions_on_day(32):
                if q["object_id"] not in movers:
                    continue
                past = sorted((d for (t, d) in seen.get(q["object_id"], [])
                               if t <= q["t_query"]), reverse=True)
                shown = past[:CAP]
                rows.append((len(past), min(shown) if shown else None,
                             any(d in SPELL_1 for d in shown)))
            reach = [r[1] for r in rows if r[1] is not None]
            print(f"{arm} {name}: {len(rows)} moved-object questions on day 32; sightings held "
                  f"per object median {statistics.median([r[0] for r in rows]):.0f}; the 40 shown "
                  f"reach back to day median {statistics.median(reach):.0f}, earliest {min(reach)}; "
                  f"{sum(1 for r in rows if r[2])} of {len(rows)} still show a day 14-23 sighting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
