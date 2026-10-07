#!/usr/bin/env python3
"""How far each method falls at each onset, and how long it takes to come back.

Two things the draft asserts and one it wants to assert:

  the drops of Section 3.2 - each method's day-14 and day-32 level against its OWN mean over the
  four days before that onset, on the 14 objects that change room in both illnesses.
  the recovery - days after each onset until the method is back within ten points of that same
  pre-onset mean, which decides whether "adapts faster the second time" can be said at all.

The baseline window is stated rather than assumed: days 10-13 before the first onset and days
28-31 before the second, four days each, the same four for every method.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/the_drop_at_each_onset.py
"""
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import paper_data as D                                              # noqa: E402

ONSETS = ((14, range(10, 14)), (32, range(28, 32)))
ARMS = (("last-seen", "last_seen_no_model"), ("log and notes", "the_log_and_notes_about_the_routine"),
        ("claim store", "incremental_edits"), ("ACE-style playbook", "ACE_as_published"))
MEASURES = (("first room right", "first"), ("found within 3", "found"))
WITHIN = 10.0        # "back" means within ten points of the pre-onset mean


def by_day(arm_dir, home, movers):
    out = {}
    for r in D.rows(D.WAVE_50, arm_dir, home):
        if r["object_id"] in movers:
            out.setdefault(r["day"], []).append(r)
    return out


def main() -> int:
    for measure, key in MEASURES:
        print(f"\n===== {measure}, the 14 objects that change room in both illnesses")
        for onset, before in ONSETS:
            print(f"\n  --- onset day {onset}, baseline days {before[0]}-{before[-1]}")
            print(f"    {'method':20s} {'baseline':>9s} {'at onset':>9s} {'drop':>7s}"
                  f"   per household (baseline -> onset)      days back within {WITHIN:.0f}")
            for name, arm_dir in ARMS:
                per_home, drops, backs = [], [], []
                for home in D.HOMES_50:
                    movers = D.both_spell_movers(home)
                    days = by_day(arm_dir, home, movers)
                    base = [D.share(days.get(d, []), key) for d in before]
                    base = [b for b in base if b is not None]
                    if not base:
                        continue
                    base_mean = statistics.mean(base)
                    at = D.share(days.get(onset, []), key)
                    if at is None:
                        continue
                    per_home.append((base_mean, at))
                    drops.append(base_mean - at)
                    back = None
                    for d in range(onset + 1, onset + 18):
                        v = D.share(days.get(d, []), key)
                        if v is not None and v >= base_mean - WITHIN:
                            back = d - onset
                            break
                    backs.append(back)
                mean_drop = statistics.mean(drops)
                two_se = (2 * statistics.stdev(drops) / len(drops) ** 0.5) if len(drops) > 1 else 0
                shown = "  ".join(f"{b:.0f}->{a:.0f}" for b, a in per_home)
                back_text = ", ".join("never" if b is None else str(b) for b in backs)
                print(f"    {name:20s} {statistics.mean(b for b, _ in per_home):9.1f} "
                      f"{statistics.mean(a for _, a in per_home):9.1f} {mean_drop:7.1f}"
                      f"   {shown:36s}  {back_text}")
                print(f"      {'':18s} 2 SE of the drop across the three households: {two_se:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
