#!/usr/bin/env python3
"""Stage 1 of the selection: which seeds are worth simulating, from the floor plan and
the residents alone.

The generator samples a household from a seed before any day is simulated, so these
three facts are free: they cost no GPU, no simulation and no question bank. Every one
of them is a property of the house and the people in it. None of them can be computed
from any method's answers, so selecting on them cannot select for a method.

  S1  AT LEAST EIGHT ROOMS. Three looks reach 38% of an eight-room home and 50% of a
      six-room one. All three six-room homes in illness_v1 were uninformative and no
      nine-room home was. This is the generator's own distribution: of 500 seeds, 244
      have eight rooms or more, so nothing is being invented - the small floor plans
      are simply not used.
  S2  EVERY RESIDENT A DIFFERENT ROLE. Two residents on the same role run the same
      timetable: the same breakfast hour, the same rooms, the same evening. Their
      objects then pile into the same rooms. Different roles means different hours
      (a commuter leaves at 08:10, the shift worker starts at 13:40, the retired
      resident is home all day) and different rooms.
  S3  A STUDY THAT SOMEBODY ACTUALLY WORKS IN: the home has an office room and at
      least one resident's workspace is it. Otherwise the desk is in a bedroom, the
      bedroom becomes one of the busiest rooms in the house, and the illness then
      moves things into a room the robot was already opening. This is the single
      strongest structural predictor of the four informative homes in illness_v1
      (three of the four had it; none of the six uninformative ones did).

    python3 results/self_improve/varied_homes/pick_the_seeds.py --seeds 0-499
"""
import argparse
import collections
import json
import pathlib
import sys

import yaml

sys.path.insert(0, "src")
HERE = pathlib.Path(__file__).resolve().parent
MIN_ROOMS = 8


def look_at_seed(seed, acts):
    from situation_sim.household import sample_household
    hh = sample_household(seed, acts)
    roles = [r.role for r in sorted(hh.residents.values(), key=lambda r: r.id)]
    workspaces = [r.workspace for r in sorted(hh.residents.values(), key=lambda r: r.id)]
    bedrooms = [r.bedroom for r in sorted(hh.residents.values(), key=lambda r: r.id)]
    tests = {
        "S1_at_least_8_rooms": len(hh.rooms) >= MIN_ROOMS,
        "S2_every_role_different": len(set(roles)) == len(roles),
        "S3_a_study_somebody_works_in": "office" in hh.rooms and "office" in workspaces,
    }
    return {"seed": seed, "household_type": hh.household_type, "n_rooms": len(hh.rooms),
            "rooms": list(hh.rooms), "roles": roles, "workspaces": workspaces,
            "bedrooms": bedrooms, "n_objects": len(hh.objects),
            "tests": tests, "kept": all(tests.values()),
            "rejected_for": sorted(k for k, v in tests.items() if not v)}


def parse_seeds(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0-499")
    ap.add_argument("--activities",
                    default=str(HERE / "scenario" / "activities_varied.yaml"))
    ap.add_argument("--want", type=int, default=None,
                    help="stop after this many kept seeds (the rest are still reported)")
    ap.add_argument("--json", dest="json_out",
                    default=str(HERE / "stage1_seed_selection.json"))
    a = ap.parse_args(argv)

    acts = yaml.safe_load(pathlib.Path(a.activities).read_text())
    seeds = parse_seeds(a.seeds)
    rows = [look_at_seed(s, acts) for s in seeds]
    kept = [r for r in rows if r["kept"]]
    if a.want:
        for r in kept[a.want:]:
            r["kept"] = False
            r["rejected_for"] = ["beyond_the_number_wanted"]
        kept = kept[:a.want]

    fails = collections.Counter(k for r in rows for k in r["rejected_for"])
    print("STAGE 1: the floor plan and the people. No day is simulated to compute any "
          "of this.\n")
    print(f"seeds looked at:      {len(rows)}")
    print(f"seeds kept:           {len(kept)}  ({len(kept)/len(rows)*100:.0f}%)")
    print("rejected because:")
    for k, v in fails.most_common():
        print(f"  {k:32s} {v:4d} seeds")
    print(f"\nrooms among the kept: "
          f"{dict(sorted(collections.Counter(r['n_rooms'] for r in kept).items()))}")
    print("household types kept: "
          + str(dict(collections.Counter(r['household_type'] for r in kept).most_common())))
    print("role sets kept:       "
          + str(dict(collections.Counter(",".join(sorted(r['roles']))
                                         for r in kept).most_common()[:8])))
    print("\nkept seeds: " + ",".join(str(r["seed"]) for r in kept))

    pathlib.Path(a.json_out).write_text(json.dumps(
        {"criteria": {"S1_at_least_8_rooms": f"len(rooms) >= {MIN_ROOMS}",
                      "S2_every_role_different": "len(set(roles)) == len(roles)",
                      "S3_a_study_somebody_works_in":
                          "'office' in rooms and some resident's workspace is the office"},
         "n_seeds_looked_at": len(rows), "n_kept": len(kept),
         "kept_seeds": [r["seed"] for r in kept], "seeds": rows}, indent=2))
    print(f"\nwrote {a.json_out} - every seed, kept or not, with the reason")
    return 0


if __name__ == "__main__":
    sys.exit(main())
