#!/usr/bin/env python3
"""Residents, rooms, tracked objects and asked-about objects per household, from the banks.

    python3 results/self_improve/paper/scripts/household_table.py
"""
import json
import pathlib
import sys

sys.path.insert(0, "src")
from self_improve.frozen_household import FrozenHousehold  # noqa: E402
from self_improve.search_driven import the_movers  # noqa: E402

SETS = {"the pilot ten (8 and 24 a day)": "results/self_improve/varied_homes/ten_homes/banks",
        "the five wider homes (budget sweep, wider five, told)":
            "results/self_improve/varied_homes/headline_five/banks",
        "the two-illness bank (50 days)":
            "results/self_improve/varied_homes/all_generated_v2_twice/banks"}


def main() -> int:
    for label, banks in SETS.items():
        print(f"\n== {label}: {banks}")
        print(f"{'household':14s}{'type':10s}{'residents':>10s}{'rooms':>7s}{'tracked':>9s}"
              f"{'asked':>7s}{'kinds':>7s}{'movers':>8s}  occupations")
        for bank in sorted(pathlib.Path(banks).glob("*.jsonl")):
            home = FrozenHousehold(bank)
            header = json.loads(bank.read_text().splitlines()[0])
            people = header.get("protocol", {}).get("residents", [])
            kinds = {home.object_class.get(o, "") for o in home.asked_objects}
            print(f"{bank.stem:14s}{header.get('household_type',''):10s}{len(people):10d}"
                  f"{len(home.rooms):7d}{len(header.get('object_classes') or {}):9d}"
                  f"{len(home.asked_objects):7d}{len(kinds):7d}{len(the_movers(home)):8d}  "
                  + ", ".join(f"{p['name']} ({p.get('occupation','?')}, {p.get('age_band','?')})"
                              for p in people))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
