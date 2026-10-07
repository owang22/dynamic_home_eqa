#!/usr/bin/env python3
"""Could one sentence of common sense answer for every home, or does each home differ?

We measured that a language model's common-sense guess alone finds objects 92% of the
time in the settled fortnight. That is a fact about the homes, not about the model: if
the mug is in the kitchen and the book is on the nightstand in every single home, then
one general sentence answers everywhere and a memory of THIS home has nothing to add.

So, per asked-about object class, this counts the homes by where that class's answer
usually is in the settled fortnight, and reports the share of homes that agree with
the commonest room. No model is called; this is counting.

  agreement 100%  one sentence covers every home: a prior gets it for free.
  agreement  50%  the room depends on the home: only a memory of this home gets it.

    python3 results/self_improve/varied_homes/is_it_the_same_in_every_home.py \
        results/self_improve/runs/illness_v1 results/self_improve/varied_homes/selected
"""
import collections
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from self_improve.frozen_household import FrozenHousehold  # noqa: E402
from which_lever_is_wrong import modal_place_per_object, room_of, SETTLED  # noqa: E402


def per_class_rooms(run_dir):
    """class -> Counter of the room its answer usually sits in, one vote per home."""
    votes = collections.defaultdict(collections.Counter)
    homes = 0
    for bank in sorted((pathlib.Path(run_dir) / "banks").glob("*.jsonl")):
        hh = FrozenHousehold(bank)
        homes += 1
        settled = modal_place_per_object(hh, SETTLED)
        by_class = collections.defaultdict(collections.Counter)
        for obj, place in settled.items():
            by_class[hh.object_class.get(obj, "?")][room_of(hh, place)] += 1
        for cls, rooms in by_class.items():
            votes[cls][rooms.most_common(1)[0][0]] += 1
    return votes, homes


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    for run_dir in argv:
        votes, homes = per_class_rooms(run_dir)
        print(f"\n{run_dir}  ({homes} homes)")
        print(f"  {'class':14s}{'homes':>7}{'agreement':>11}  where the answer usually is")
        agreements = []
        for cls in sorted(votes, key=lambda c: -sum(votes[c].values())):
            rooms = votes[cls]
            n = sum(rooms.values())
            top, top_n = rooms.most_common(1)[0]
            share = top_n / n
            agreements.append(share)
            spread = ", ".join(f"{r} {v}" for r, v in rooms.most_common(4))
            print(f"  {cls:14s}{n:>7}{share*100:>10.0f}%  {spread}")
        print(f"  mean agreement over classes: {statistics.mean(agreements)*100:.0f}% "
              f"(100% would mean one sentence answers for every home)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
