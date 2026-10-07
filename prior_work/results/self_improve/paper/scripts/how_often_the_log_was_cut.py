#!/usr/bin/env python3
"""How often the 40-sighting window actually bound, per run.

`the_log_the_robot_reads.HOW_MANY_SIGHTINGS_TO_SHOW = 40` lists the newest 40 dated sightings of
the asked object and replaces the rest with one summary line naming the rooms, their counts and the
oldest day. This counts, for every question an arm answered, how many sightings of that object the
robot already held - so it says how often the dated lines were cut, and how far back the 40 reached
when they were.

    python3 results/self_improve/paper/scripts/how_often_the_log_was_cut.py
"""
import collections
import json
import pathlib
import statistics

CAP = 40
CELLS = [("ten homes, 8 a day", "overnight_wave", "the_log_and_notes_about_the_routine"),
         ("five wider homes, 24 a day", "wave_wider_five", "the_log_and_notes_about_the_routine"),
         ("five wider homes, 8 a day", "wave_the_budget_sweep_q8",
          "the_log_and_notes_about_the_routine"),
         ("five wider homes, 4 a day", "wave_the_budget_sweep_q4",
          "the_log_and_notes_about_the_routine"),
         ("three homes, 24 a day, 50 days", "wave_the_second_illness",
          "the_log_and_notes_about_the_routine")]


def main() -> int:
    print(f"{'run':34s}{'questions':>10s}{'cut':>8s}{'share':>8s}"
          f"{'held (median)':>15s}{'the 40 reach back':>20s}")
    for label, wave, arm in CELLS:
        cut = total = 0
        held, reach = [], []
        for cell in sorted(pathlib.Path(f"results/self_improve/{wave}/cells/{arm}").iterdir()):
            seen = collections.defaultdict(list)
            for line in (cell / "looks.jsonl").open():
                for s in json.loads(line).get("sightings", []):
                    seen[s["object_id"]].append((s["time"], s["day"]))
            for line in (cell / "searches.jsonl").open():
                r = json.loads(line)
                if r.get("kind") != "search":
                    continue
                past = sorted((d for (t, d) in seen.get(r["object_id"], []) if t <= r["time"]),
                              reverse=True)
                total += 1
                held.append(len(past))
                if len(past) > CAP:
                    cut += 1
                    reach.append(r["day"] - min(past[:CAP]))
        print(f"{label:34s}{total:10d}{cut:8d}{100*cut/total:7.0f}%{statistics.median(held):15.0f}"
              + (f"{statistics.median(reach):17.0f} days" if reach else f"{'-':>20s}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
