#!/usr/bin/env python3
"""The six-method comparison, run again on the waves that reasoned BEFORE choosing a room.

Table 1 of the draft comes from the ten-household run, where the schema named the room first and
thinking was off, so every memory-guided arm picked its room after zero tokens of deliberation
(see questions_left_open.md section 2). These are the same comparisons on waves that do not have
that flaw. Different households and a different question budget, so the levels are not comparable
with Table 1 - only the ORDERING and the paired differences are.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/reason_first_comparison.py
"""
import json
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import paper_data as D  # noqa: E402

MEAS = {"first room right": lambda r: r.get("found_at_step") == 1,
        "found within 3": lambda r: bool(r.get("found_it"))}
FLOOR = {"first room right": 1.9, "found within 3": 2.2}


def report(title, wave, arms, homes, movers_of, days):
    print(f"\n\n===== {title}")
    rows = {}
    for directory, label in arms.items():
        rows[label] = {}
        for home in homes:
            movers = movers_of(home)
            rs = [r for r in D.rows(wave, directory, home) if r["day"] in days]
            rows[label][home] = (rs, [r for r in rs if r["object_id"] in movers])
    for measure, fn in MEAS.items():
        for which, index in (("every question", 0), ("moved objects", 1)):
            print(f"\n  --- {measure}, {which}")
            print(f"  {'method':22s}{'level':>8s}{'vs last-seen':>13s}{'2 SE':>7s}"
                  f"{'same sign':>11s}{'questions':>11s}")
            base = {h: rows["last-seen"][h][index] for h in homes}
            for label in arms.values():
                per_home, diffs, n = [], [], 0
                for home in homes:
                    mine = rows[label][home][index]
                    theirs = base[home]
                    if len(mine) < 8:
                        continue
                    a = 100 * sum(1 for r in mine if fn(r)) / len(mine)
                    b = 100 * sum(1 for r in theirs if fn(r)) / len(theirs)
                    per_home.append(a)
                    diffs.append(a - b)
                    n += len(mine)
                if not per_home:
                    continue
                tse = 2 * statistics.stdev(diffs) / len(diffs) ** 0.5 if len(diffs) > 1 else 0.0
                mark = ""
                if label != "last-seen":
                    clears = abs(statistics.mean(diffs)) > tse and \
                        abs(statistics.mean(diffs)) > FLOOR[measure]
                    mark = "  clears" if clears else ""
                print(f"  {label:22s}{statistics.mean(per_home):8.1f}"
                      + (f"{statistics.mean(diffs):+13.1f}{tse:7.1f}"
                         f"{sum(1 for v in diffs if v > 0):>6d} of {len(diffs)}{n:11d}{mark}"
                         if label != "last-seen" else f"{'-':>13s}{'-':>7s}{'-':>11s}{n:11d}"))


def main() -> int:
    report("the 50-day run, days 1 to 31 (three homes, 24 a day)",
           D.WAVE_50, D.ARM_50, D.HOMES_50,
           lambda h: D.spell_1_movers(h, D.BANKS_50), set(range(1, 32)))
    wider = pathlib.Path("results/self_improve/wave_wider_five/cells")
    banks = pathlib.Path("results/self_improve/varied_homes/headline_five/banks")
    report("wave_wider_five, 31 days, 24 a day (five wider homes)",
           wider, {"last_seen_no_model": "last-seen",
                   "the_log_and_notes_about_the_routine": "log and notes",
                   "ACE_as_published": "ACE"},
           ("hh_s32_t03", "hh_s48_t03", "hh_s63_t03", "hh_s93_t03", "hh_s151_t03"),
           lambda h: D.spell_1_movers(h, banks), set(range(1, 32)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
