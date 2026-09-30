#!/usr/bin/env python3
"""Last-seen replayed with the first illness deleted from its memory. No model call anywhere.

The question Section 3.2 turns on is whether last-seen's smaller drop at the second onset is
RETAINED KNOWLEDGE from the first illness or just a shorter distance to fall. This answers it by
taking the knowledge away: every sighting dated day 14 to 23 is dropped on the floor as it arrives,
so the trail for each object skips the first illness entirely. Everything else is identical - same
bank, same questions, same seed, same three-room budget, same room-opening rule - and sightings
from day 24 on accumulate exactly as they always did.

The deletion is done by patching `_remember_where_it_was_seen` IN THIS PROCESS ONLY, so the arm's
own source is untouched and anything else running at the same time is unaffected. The robot still
LOOKS in those rooms on days 14 to 23 and still scores those days; it just does not carry what it
saw out of them.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/last_seen_without_the_first_illness.py
"""
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import paper_data as D                                              # noqa: E402
from baselines.types import DAY_SECONDS                             # noqa: E402
from self_improve import search_driven as sd                        # noqa: E402
from self_improve import overnight_wave as ow                       # noqa: E402
from self_improve.frozen_household import FrozenHousehold           # noqa: E402

BANKS = pathlib.Path("results/self_improve/varied_homes/all_generated_v2_twice/banks")
OUT = pathlib.Path("results/self_improve/wave_last_seen_no_first_illness")
FORGET = range(14, 24)
_original = sd._remember_where_it_was_seen


def forgetful(where_it_has_been, object_id, at_time, place_id, room):
    if (at_time // DAY_SECONDS) in FORGET:
        return
    _original(where_it_has_been, object_id, at_time, place_id, room)


def by_day(cells, arm_dir, home, movers):
    out = {}
    for r in D.rows(cells, arm_dir, home):
        if r["object_id"] in movers:
            out.setdefault(r["day"], []).append(r)
    return out


def main() -> int:
    sd._remember_where_it_was_seen = forgetful
    OUT.mkdir(parents=True, exist_ok=True)
    for home in D.HOMES_50:
        cell = OUT / "cells" / "last_seen_no_model" / home
        if (cell / "searches.jsonl").exists():
            print(f"{home}: already replayed")
            continue
        print(f"{home}: replaying with days 14-23 deleted from the trail ...", flush=True)
        # the module's own entry point, so the cell is written exactly as any other run writes it
        ow.main(["--arm", "last seen, no model", "--household", home,
                 "--banks", str(BANKS), "--last-day", "49", "--questions-per-day", "24",
                 "--budget", "3", "--seed", "0", "--out", str(OUT),
                 "--cache", "llm_prior_cache/self_improve"])
    print("\n=== day 32, the 14 objects that change room in both illnesses ===")
    print(f"  {'household':14s} {'measure':18s} {'original d14':>12s} {'original d32':>12s} "
          f"{'no 1st illness d32':>19s}")
    rows = []
    for home in D.HOMES_50:
        movers = D.both_spell_movers(home)
        orig = by_day(D.WAVE_50, "last_seen_no_model", home, movers)
        gone = by_day(OUT / "cells", "last_seen_no_model", home, movers)
        for label, key in (("first room right", "first"), ("found within 3", "found")):
            o14, o32 = D.share(orig.get(14, []), key), D.share(orig.get(32, []), key)
            g32 = D.share(gone.get(32, []), key)
            base_o = statistics.mean([D.share(orig.get(d, []), key) for d in range(28, 32)])
            base_g = statistics.mean([D.share(gone.get(d, []), key) for d in range(28, 32)])
            base14 = statistics.mean([D.share(orig.get(d, []), key) for d in range(10, 14)])
            rows.append((home, label, o14, o32, g32, base_o - o32, base_g - g32,
                         base14 - o14))
            print(f"  {home:14s} {label:18s} {o14:12.0f} {o32:12.0f} {g32:19.0f}")
    print("\n=== the drop against each run's own days 28-31 mean, same rule as "
          "the_drop_at_each_onset.py ===")
    print(f"  {'measure':18s} {'original drop at 32':>20s} {'no-first-illness drop':>22s} "
          f"{'original drop at 14':>20s}")
    for label in ("first room right", "found within 3"):
        these = [r for r in rows if r[1] == label]
        d32 = statistics.mean(r[5] for r in these)
        gone = statistics.mean(r[6] for r in these)
        d14 = statistics.mean(r[7] for r in these)
        print(f"  {label:18s} {d32:20.1f} {gone:22.1f} {d14:20.1f}")
        print(f"    deleting the first illness moves the day-32 drop from {d32:.1f} to "
              f"{gone:.1f}; the day-14 drop is {d14:.1f}, so it lands "
              f"{'ON' if abs(gone - d14) < 5 else 'NOT ON'} the day-14 level "
              f"(difference {gone - d14:+.1f}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
