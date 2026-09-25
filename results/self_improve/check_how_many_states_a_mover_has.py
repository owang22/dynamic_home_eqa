"""How many different spots one object needs a claim for, over the month.

The third way of writing notes is told it should be able to fit its notes into a few
lines for each object the robot is asked about. That number cannot be picked: it has
to come from how many spots an object actually has. A mover has two if it goes back to
exactly where it started when ordinary life returns, and three if it does not.

Run: python3 results/self_improve/check_how_many_states_a_mover_has.py
"""
import pathlib
import sys

sys.path.insert(0, "src")
from self_improve.frozen_household import load_every_frozen_household
from self_improve.search_driven import _commonest_place_over, the_movers

BANKS = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks")
SETTLED, BACK = range(1, 14), range(24, 32)


def main() -> int:
    homes = load_every_frozen_household(BANKS)
    homes = homes if isinstance(homes, list) else list(homes.values())
    total = exact = 0
    for home in homes:
        movers = sorted(the_movers(home))
        same = sum(1 for o in movers
                   if _commonest_place_over(home, o, SETTLED)
                   == _commonest_place_over(home, o, BACK))
        print(f"{home.name}: {same} of {len(movers)} movers end the month in exactly "
              f"the spot they started in")
        total += len(movers)
        exact += same
    print(f"\nall {len(homes)} homes: {exact} of {total} = {exact/total:.0%} revert "
          f"exactly, so {total - exact} movers need a third claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
