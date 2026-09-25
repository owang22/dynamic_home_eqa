"""What the notes of the older arms are about: places, or how the household works?

This recomputes the baseline that the new arm's gate is read against, with the SAME
regular expressions the gate uses, over whatever claim-store cells are on disk now. It
exists because a threshold quoted as a constant drifts away from the estimator and the
population that produced it, and then two different things are being compared.

Run: python3 results/self_improve/what_the_old_notes_were_about.py
"""
import collections
import glob
import json
import pathlib
import sys

sys.path.insert(0, "src")
from self_improve.write_the_notes_about_the_routine import A_PLACE, A_TIME_OR_A_CHANGE


def main() -> int:
    counts = collections.Counter()
    for f in glob.glob("results/self_improve/**/notes.json", recursive=True):
        if "superseded" in f or "stopped_early" in f:
            continue
        try:
            d = json.loads(pathlib.Path(f).read_text())
        except ValueError:
            continue
        if d.get("how_memory_is_written") in ("wholesale rewrite",
                                              "the log and notes about the routine"):
            continue
        for c in d.get("claims") or []:
            if c.get("folded_into"):
                continue
            statement = c.get("statement") or ""
            counts["claims"] += 1
            if A_PLACE.search(statement):
                counts["names a place"] += 1
            if A_TIME_OR_A_CHANGE.search(statement):
                counts["names a time, a condition or a change"] += 1
            if (c.get("holds_under") or "").strip().lower() in ("current", "", "not said"):
                counts["condition is just current"] += 1
            if c.get("contradicting_observation_ids"):
                counts["cites evidence against itself"] += 1
    n = counts["claims"]
    if not n:
        print("no claim-store cells on disk")
        return 1
    print(f"{n} claims, in the arms that were free to write about places")
    for k in ("names a place", "names a time, a condition or a change",
              "condition is just current", "cites evidence against itself"):
        print(f"  {k:40} {counts[k]:5}  {counts[k]/n:6.2%}")
    print("\nThese are the numbers the new arm's gate is read against. It has to move the "
          "first one down and the second one up.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
