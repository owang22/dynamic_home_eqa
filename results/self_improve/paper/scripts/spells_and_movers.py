#!/usr/bin/env python3
"""The two illness spells of the 50-day bank, object by object, and what "moved object" means.

`search_driven.the_movers` (src/self_improve/search_driven.py:261-272) fixes the mover set once
per run from the commonest DAYTIME PLACE over days 0-13 against days 14-23 - so it is defined on
the FIRST spell only, at spot level rather than room level, and it never changes per question.
This prints, per mover, the commonest daytime place in five windows, so the reader can see which
movers move again in the second spell and which do not.

    python3 results/self_improve/paper/scripts/spells_and_movers.py
"""
import collections
import pathlib
import sys

sys.path.insert(0, "src")
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE  # noqa: E402
from self_improve import search_driven as sd  # noqa: E402
from self_improve.frozen_household import FrozenHousehold  # noqa: E402

BANKS = pathlib.Path("results/self_improve/varied_homes/all_generated_v2_twice/banks")
HOMES = ("hh_s2_t03", "hh_s32_t03", "hh_s48_t03")
WINDOWS = {"settled 0-13": range(0, 14), "spell 1 14-23": range(14, 24),
           "back 24-31": range(24, 32), "spell 2 32-41": range(32, 42),
           "back 42-49": range(42, 50)}


def commonest(home, object_id, days):
    counts = collections.Counter()
    for day in days:
        for hour in range(8, 23):
            place = home.place_of_object(object_id, day * DAY_SECONDS + hour * 3600)
            if place and place not in (OUT_OF_HOUSE, ON_PERSON):
                counts[place] += 1
    return counts.most_common(1)[0][0] if counts else None


def main() -> int:
    for name in HOMES:
        home = FrozenHousehold(BANKS / f"{name}.jsonl")
        movers = sorted(sd.the_movers(home))
        room = home.place_room.get
        moves_in_2 = 0
        print(f"\n== {name}: {len(home.asked_objects)} asked objects, {len(movers)} movers")
        for object_id in movers:
            places = {w: commonest(home, object_id, d) for w, d in WINDOWS.items()}
            rooms = {w: room(p) for w, p in places.items()}
            again = rooms["spell 2 32-41"] != rooms["settled 0-13"]
            moves_in_2 += bool(again)
            print(f"   {object_id:22s} " + " ".join(
                f"{w.split()[0]}:{rooms[w]}" for w in WINDOWS)
                + f"   changes room in spell 2: {again}")
        room_level_1 = sum(1 for o in movers
                           if room(commonest(home, o, WINDOWS["spell 1 14-23"]))
                           != room(commonest(home, o, WINDOWS["settled 0-13"])))
        print(f"   of {len(movers)} movers (spot level, spell 1): {room_level_1} change ROOM in "
              f"spell 1, {moves_in_2} change ROOM in spell 2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
