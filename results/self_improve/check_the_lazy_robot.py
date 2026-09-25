#!/usr/bin/env python3
"""Could a robot that never learns anything already pass this scenario?

Opening three rooms out of seven is a lot of house. In two of the ten households a
robot that simply always opens the three busiest rooms finds the object about nine
times in ten, which leaves eight to eleven points for any clever method to win in.
A scenario like that cannot tell two methods apart however well the rest of it is
built, and the only way to know is to compute it before spending a GPU on it.

The number that matters is the last one: what the lazy robot scores on the objects
the disruption MOVES, during the disruption. If the upset pushes things into rooms
the robot was going to open anyway, no amount of memory or reasoning shows up.

    python3 results/self_improve/check_the_lazy_robot.py results/self_improve/runs/illness_v1
"""
import collections
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
from self_improve.frozen_household import FrozenHousehold

# A scenario is uninformative when the lazy robot already succeeds this often on the
# objects the upset moved. Set from what the three live households showed: 19% (a
# home that discriminates) against 73% and 81% (two that cannot).
LAZY_ROBOT_ON_MOVERS_MUST_BE_UNDER = 0.50
ROOMS_A_LOOK_OPENS = 3
SETTLED, DISRUPTED = range(1, 14), range(14, 24)


def room_of(household, place):
    rooms = household.place_room
    return rooms.get(place) if isinstance(rooms, dict) else rooms(place)


def modal_place_per_object(household, days):
    counts = collections.defaultdict(collections.Counter)
    for day in days:
        for question in household.questions_on_day(day):
            true_place = household.true_place_for_question(question)
            if true_place:
                counts[question["object_id"]][true_place] += 1
    return {o: c.most_common(1)[0][0] for o, c in counts.items() if c}


def look_at(household):
    """What the busiest rooms are, and how often they already hold the answer."""
    everything = collections.Counter()
    for day in range(1, household.n_days + 1):
        for question in household.questions_on_day(day):
            true_place = household.true_place_for_question(question)
            if true_place:
                everything[room_of(household, true_place)] += 1
    busiest = {room for room, _ in everything.most_common(ROOMS_A_LOOK_OPENS)}

    settled = modal_place_per_object(household, SETTLED)
    disrupted = modal_place_per_object(household, DISRUPTED)
    movers = {o for o in settled if o in disrupted and settled[o] != disrupted[o]}

    all_hits = all_n = mover_hits = mover_n = 0
    for day in range(1, household.n_days + 1):
        for question in household.questions_on_day(day):
            true_place = household.true_place_for_question(question)
            if not true_place:
                continue
            hit = room_of(household, true_place) in busiest
            all_n += 1
            all_hits += hit
            if day in DISRUPTED and question["object_id"] in movers:
                mover_n += 1
                mover_hits += hit
    return {"rooms": len(household.rooms), "busiest": sorted(busiest),
            "n_movers": len(movers),
            "lazy_all": all_hits / all_n if all_n else None,
            "lazy_movers": mover_hits / mover_n if mover_n else None,
            "chance": min(1.0, ROOMS_A_LOOK_OPENS / len(household.rooms))}


def main(run_dir):
    banks = pathlib.Path(run_dir) / "banks"
    if not banks.is_dir():
        print(f"no banks directory under {run_dir}")
        return 2
    print(f"THE LAZY ROBOT: it never learns, and always opens the "
          f"{ROOMS_A_LOOK_OPENS} busiest rooms in the house.\n")
    head = (f"{'household':12s}{'rooms':>6}{'movers':>8}{'chance':>8}"
            f"{'lazy, all objects':>19}{'lazy, on the movers':>21}")
    print(head)
    print("-" * len(head))
    rows = []
    for bank in sorted(banks.glob("*.jsonl")):
        household = FrozenHousehold(bank)
        row = look_at(household)
        rows.append((household.name, row))
        movers = row["lazy_movers"]
        flag = "" if movers is None or movers < LAZY_ROBOT_ON_MOVERS_MUST_BE_UNDER \
               else "   <-- too easy"
        print(f"{household.name.replace('_t03',''):12s}{row['rooms']:>6}{row['n_movers']:>8}"
              f"{row['chance']*100:>7.0f}%{row['lazy_all']*100:>18.0f}%"
              f"{(movers * 100 if movers is not None else float('nan')):>20.0f}%{flag}")

    on_movers = [r["lazy_movers"] for _, r in rows if r["lazy_movers"] is not None]
    too_easy = [n for n, r in rows
                if r["lazy_movers"] is not None
                and r["lazy_movers"] >= LAZY_ROBOT_ON_MOVERS_MUST_BE_UNDER]
    print(f"\nmean over households, on the objects the upset moved: "
          f"{statistics.mean(on_movers)*100:.0f}%")
    print(f"the bar: a household is uninformative when this is "
          f"{LAZY_ROBOT_ON_MOVERS_MUST_BE_UNDER*100:.0f}% or more\n")
    if too_easy:
        print(f"TOO EASY in {len(too_easy)} of {len(rows)} households: "
              f"{', '.join(n.replace('_t03','') for n in too_easy)}")
        print("  In these homes the upset moves things into rooms the robot was going to")
        print("  open anyway, so no memory or reasoning can show a difference. Move the")
        print("  destinations out of the busiest rooms, spread the answers over more")
        print("  rooms, or give the robot fewer looks.")
        return 1
    print(f"USABLE: in every household the lazy robot misses more than "
          f"{(1-LAZY_ROBOT_ON_MOVERS_MUST_BE_UNDER)*100:.0f}% of the moved objects,")
    print("so there is room for a method to show what it is worth.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1
                  else "results/self_improve/runs/illness_v1"))
