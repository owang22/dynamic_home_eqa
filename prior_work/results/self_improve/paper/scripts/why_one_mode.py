#!/usr/bin/env python3
"""Why the mode memory never splits: the arithmetic of one day's assignment.

The Chinese restaurant process compares an existing mode, weighted by the days already assigned to
it, against a new empty mode weighted by alpha. Both are multiplied by the likelihood of the WHOLE
DAY's sightings. This prints those two numbers on the first day of the illness, which is the day
with the best chance of splitting.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/why_one_mode.py
"""
import math
import pathlib
import sys
import tempfile

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from run_household_mode import build                                   # noqa: E402
from self_improve import search_driven as sd                           # noqa: E402
from self_improve.household_mode import HouseholdModes                 # noqa: E402
from self_improve.looking import LookTarget                            # noqa: E402

scratch = pathlib.Path(tempfile.mkdtemp())


def main() -> int:
    for home in ("hh_s2_t03", "hh_s32_t03", "hh_s48_t03"):
        household, eyes, rotation = build("ten_homes", home, scratch / home)
        memory = HouseholdModes(household.rooms, alpha=1.0, stay=0.9)
        movers = sd.the_movers(household)
        rng = __import__("random").Random(0)
        trail = {}
        for day in range(0, 15):
            memory.start_the_day()
            today = []
            for question in sd.questions_spread_across_the_day(
                    sd.answerable_questions_on_day(household, day), 8):
                rooms_left = list(household.rooms)
                for _ in range(3):
                    room = (memory.rank(question["object_id"], rooms_left)[0]
                            if memory.knows(question["object_id"])
                            else sd._the_next_room_it_was_seen_in(
                                question["object_id"], household, trail, rooms_left, rng)[0])
                    rooms_left.remove(room)
                    look = eyes.look([LookTarget(room, "room")], day,
                                     question["t_query"] % 86400, "diagnosis")
                    for s in look.sightings:
                        sd._remember_where_it_was_seen(trail, s["object_id"], s["time"],
                                                       s["place_id"], s["room"])
                        memory.saw(s["object_id"], s["room"])
                        today.append((s["object_id"], s["room"]))
                    if any(s["object_id"] == question["object_id"] for s in look.sightings):
                        break
            if day == 14:
                mode = memory.modes[0]
                established = math.log(mode.days) + sum(
                    math.log(mode.probability_of(o, r)) for o, r in today)
                fresh = math.log(1.0) + len(today) * math.log(1.0 / len(household.rooms))
                moved = [(o, r) for o, r in today if o in movers]
                print(f"\n{home}: day 14 recorded {len(today)} sightings, "
                      f"{len(moved)} of them of an object the illness moves "
                      f"({100*len(moved)/len(today):.0f}%)")
                print(f"   log score, the one existing mode : {established:9.1f}")
                print(f"   log score, a brand-new empty mode: {fresh:9.1f}")
                print(f"   the existing mode wins by {established - fresh:.0f} in log units — the "
                      f"new mode would need to be e^{established - fresh:.0f} times better")
                worst = sorted(((mode.probability_of(o, r), o, r) for o, r in today))[:3]
                print("   the three least expected sightings of the day, under the old mode:")
                for p, o, r in worst:
                    print(f"      {o:22s} in {r:11s} p={p:.3f}")
            memory.close_the_day(day, today)
        print(f"   modes after day 14: {len(memory.modes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
