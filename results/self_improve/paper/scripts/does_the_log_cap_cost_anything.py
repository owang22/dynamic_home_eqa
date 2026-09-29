#!/usr/bin/env python3
"""Does the 40-sighting cap cost our arm accuracy? Two tests, same homes, no new runs.

WHY NOT JUST COMPARE THE BUDGETS. Cut rate and evidence move together: at 4 questions a day the
cap bites 5% of questions and the robot has seen little, at 24 a day it bites 75% and the robot has
seen a lot. Nothing in that comparison separates the cap from the looking.

WHY NOT JUST COMPARE CUT AGAINST UNCUT QUESTIONS. A question is cut when the robot already holds
more than 40 sightings of that object, which happens to objects it sees constantly - the easy ones.
Cut questions would look better whatever the cap did.

So both tests use last-seen as the ruler. last-seen never reads the log, so its accuracy on the same
question measures how hard that question is, and the quantity of interest is our arm's LEAD over it:

  test 1, difference in differences: is our lead over last-seen smaller on cut questions than on
          uncut ones, paired within household?
  test 2, the discontinuity: the cap is a step at exactly 40. Comparing questions just below it
          (25 to 39 sightings held) with questions just above (41 to 60) holds the object's
          familiarity roughly fixed, and last-seen over the same two bands is the placebo - it has
          no cap, so its own step across 40 is what "no effect" looks like.

`cut` is a property of OUR arm's own history, because it is our arm's looks that build the record
it is shown. last-seen's accuracy is read off its own run of the same questions.

    python3 results/self_improve/paper/scripts/does_the_log_cap_cost_anything.py
"""
import collections
import json
import pathlib
import statistics

CAP = 40
RUNS = [("ten homes, 8 a day", "overnight_wave"),
        ("five wider homes, 24 a day", "wave_wider_five"),
        ("five wider homes, 8 a day", "wave_the_budget_sweep_q8"),
        ("five wider homes, 4 a day", "wave_the_budget_sweep_q4"),
        ("three homes, 24 a day, 50 days", "wave_the_second_illness")]
OURS = "the_log_and_notes_about_the_routine"
RULE = "last_seen_no_model"
MEAS = {"first room right": lambda r: r.get("found_at_step") == 1,
        "found within 3": lambda r: bool(r.get("found_it"))}


def held_before(cell):
    """question_id -> how many sightings of that object this arm already held."""
    seen = collections.defaultdict(list)
    for line in (cell / "looks.jsonl").open():
        for s in json.loads(line).get("sightings", []):
            seen[s["object_id"]].append(s["time"])
    out = {}
    for line in (cell / "searches.jsonl").open():
        r = json.loads(line)
        if r.get("kind") == "search":
            out[r["question_id"]] = sum(1 for t in seen.get(r["object_id"], []) if t <= r["time"])
    return out


def rows_by_id(cell):
    out = {}
    for line in (cell / "searches.jsonl").open():
        r = json.loads(line)
        if r.get("kind") == "search":
            out[r["question_id"]] = r
    return out


def mean_or_none(values):
    return statistics.mean(values) if values else None


# ------------------------------------------------------- can this test see anything --
def power_check():
    """Feed the same machinery a split that is KNOWN to change our arm's lead.

    A null from a comparison with no power says nothing, and this project has been caught by that
    before. So the identical difference-in-differences is run over a split where the answer is
    already known - questions about objects the illness moves against the rest, and days inside
    the illness against the settled fortnight. If the machinery reports a difference there, its
    silence about the cap is informative.
    """
    root = pathlib.Path("results/self_improve/wave_wider_five/cells")
    homes = sorted(p.name for p in (root / OURS).iterdir() if p.is_dir())
    print("\n\n===== can this test see a difference it should see?"
          "   (five wider homes, 24 a day, the same homes and machinery)")
    splits = {"a moved object vs any other": lambda r: bool(r.get("is_a_mover")),
              "inside the illness vs settled": lambda r: 14 <= r["day"] <= 23,
              "held over 40 sightings vs not": None}
    for name, pick in splits.items():
        for measure, fn in MEAS.items():
            groups = {True: [], False: []}
            for home in homes:
                ours, rule = rows_by_id(root / OURS / home), rows_by_id(root / RULE / home)
                held = held_before(root / OURS / home)
                shared = [q for q in ours if q in rule and q in held]
                for flag in (True, False):
                    qs = [q for q in shared
                          if (held[q] > CAP if pick is None else pick(ours[q])) == flag]
                    if len(qs) < 8:
                        continue
                    a = 100 * sum(1 for q in qs if fn(ours[q])) / len(qs)
                    b = 100 * sum(1 for q in qs if fn(rule[q])) / len(qs)
                    groups[flag].append(a - b)
            if len(groups[True]) == len(groups[False]) and len(groups[True]) > 1:
                d = [x - y for x, y in zip(groups[True], groups[False])]
                tse = 2 * statistics.stdev(d) / len(d) ** 0.5
                verdict = "SEES IT" if abs(statistics.mean(d)) > tse else "no difference"
                print(f"  {name:32s}{measure:18s} our lead differs by "
                      f"{statistics.mean(d):+6.1f}  2 SE {tse:5.1f}   {verdict}")


def main() -> int:
    for label, wave in RUNS:
        root = pathlib.Path("results/self_improve") / wave / "cells"
        homes = sorted(p.name for p in (root / OURS).iterdir() if p.is_dir())
        print(f"\n===== {label}   ({len(homes)} households)")
        per_home = {}
        for home in homes:
            ours, rule = rows_by_id(root / OURS / home), rows_by_id(root / RULE / home)
            held = held_before(root / OURS / home)
            shared = [q for q in ours if q in rule and q in held]
            per_home[home] = (ours, rule, held, shared)

        for measure, fn in MEAS.items():
            print(f"\n  --- {measure}")
            print(f"  {'':26s}{'our arm':>10s}{'last-seen':>10s}{'our lead':>10s}{'questions':>11s}")
            lead = {}
            for group, keep in (("cut (over 40 held)", lambda n: n > CAP),
                                ("not cut", lambda n: n <= CAP)):
                per = []
                a_all, b_all, n_all = [], [], 0
                for home, (ours, rule, held, shared) in per_home.items():
                    qs = [q for q in shared if keep(held[q])]
                    if len(qs) < 8:
                        continue
                    a = 100 * sum(1 for q in qs if fn(ours[q])) / len(qs)
                    b = 100 * sum(1 for q in qs if fn(rule[q])) / len(qs)
                    per.append(a - b)
                    a_all.append(a)
                    b_all.append(b)
                    n_all += len(qs)
                lead[group] = per
                if per:
                    print(f"  {group:26s}{statistics.mean(a_all):10.1f}"
                          f"{statistics.mean(b_all):10.1f}{statistics.mean(per):+10.1f}"
                          f"{n_all:11d}   (homes with at least 8: {len(per)})")
            if all(lead.get(g) for g in ("cut (over 40 held)", "not cut")):
                homes_both = min(len(lead["cut (over 40 held)"]), len(lead["not cut"]))
                if homes_both > 1 and len(lead["cut (over 40 held)"]) == len(lead["not cut"]):
                    d = [u - c for c, u in zip(lead["cut (over 40 held)"], lead["not cut"])]
                    tse = 2 * statistics.stdev(d) / len(d) ** 0.5
                    print(f"  {'lead lost to the cap':26s}{statistics.mean(d):+20.1f}"
                          f"   2 SE {tse:.1f}, same sign in "
                          f"{sum(1 for v in d if v > 0)} of {len(d)}")

        # --- test 2, the step at exactly 40
        print("\n  --- the step at 40: questions holding 25-39 sightings against 41-60")
        for arm_label, which in (("our arm", 0), ("last-seen (placebo, no cap)", 1)):
            for measure, fn in MEAS.items():
                below, above = [], []
                nb = na = 0
                for home, (ours, rule, held, shared) in per_home.items():
                    table = ours if which == 0 else rule
                    lo = [q for q in shared if 25 <= held[q] <= 39]
                    hi = [q for q in shared if 41 <= held[q] <= 60]
                    if len(lo) < 8 or len(hi) < 8:
                        continue
                    below.append(100 * sum(1 for q in lo if fn(table[q])) / len(lo))
                    above.append(100 * sum(1 for q in hi if fn(table[q])) / len(hi))
                    nb += len(lo)
                    na += len(hi)
                if len(below) > 1:
                    d = [a - b for b, a in zip(below, above)]
                    tse = 2 * statistics.stdev(d) / len(d) ** 0.5
                    print(f"    {arm_label:28s}{measure:18s} below {statistics.mean(below):5.1f}"
                          f"  above {statistics.mean(above):5.1f}  step {statistics.mean(d):+5.1f}"
                          f"  2 SE {tse:4.1f}  ({nb} and {na} questions, {len(d)} homes)")
    power_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


