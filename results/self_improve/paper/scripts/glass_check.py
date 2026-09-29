#!/usr/bin/env python3
"""Where Tomas's glass actually is during the working day, settled against ill.

Checks the claim Figure 3's caption makes: that a glass on the bedroom nightstand through the
working day is the illness rather than a new fact about where the glass lives.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/glass_check.py
"""
import collections
import pathlib
import sys

sys.path.insert(0, "src")
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE       # noqa: E402
from self_improve.frozen_household import FrozenHousehold, plain_place_name  # noqa: E402


def main() -> int:
    hh = FrozenHousehold(pathlib.Path(
        "results/self_improve/varied_homes/ten_homes/banks/hh_s2_t03.jsonl"))
    for label, days in (("settled, days 1-13", range(1, 14)),
                        ("ill, days 14-23", range(14, 24))):
        counts: collections.Counter = collections.Counter()
        for day in days:
            for hour in range(8, 16):
                place = hh.place_of_object("glass_tomas", day * DAY_SECONDS + hour * 3600)
                if place and place not in (OUT_OF_HOUSE, ON_PERSON):
                    counts[f"{plain_place_name(place)} ({hh.place_room.get(place)})"] += 1
        total = sum(counts.values())
        print(f"{label}: glass_tomas between 08:00 and 15:00")
        for where, n in counts.most_common():
            print(f"    {n / total:5.0%}  {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
