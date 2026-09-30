#!/usr/bin/env python3
"""Tables 2 and 3 and the merge audit, for whichever 50-day wave WAVE_50 points at.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/the_rerun_tables.py
    WAVE_50=results/self_improve/wave_the_second_illness_ACE_rerun/cells \\
        PYTHONPATH=src python3 results/self_improve/paper/scripts/the_rerun_tables.py

Table 2 is day 14 against day 32 on the 14 objects that change room in BOTH illnesses; Table 3 is
the same on all 22 that moved in the first. Both are paired within household. The merge audit is
what ACE's grow-and-refine actually did, counting for the first time the verdicts the handler
discarded - see `n_unusable` in write_the_notes_told_if_right.
"""
import collections
import json
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import paper_data as D                                              # noqa: E402
from self_improve import search_driven as sd                        # noqa: E402

ARMS = (("last-seen", "last_seen_no_model"),
        ("log and notes", "the_log_and_notes_about_the_routine"),
        ("claim store", "incremental_edits"),
        ("ACE-style playbook", "ACE_as_published"))


def table(objects_of, title, measures):
    print(f"\n===== {title}   (wave: {D.WAVE_50})")
    for label, key in measures:
        print(f"\n  --- {label}")
        print(f"    {'method':22s} " + "  ".join(f"{h[:9]:>11s}" for h in D.HOMES_50)
              + f" {'mean change':>12s} {'2 SE':>6s} {'never found 14->32':>19s}")
        for name, arm_dir in ARMS:
            if not (D.WAVE_50 / arm_dir).exists():
                print(f"    {name:22s} (not in this wave)")
                continue
            cells, changes, nf14, nf32 = [], [], 0, 0
            for home in D.HOMES_50:
                objs = objects_of(home)
                rows = [r for r in D.rows(D.WAVE_50, arm_dir, home) if r["object_id"] in objs]
                d14 = [r for r in rows if r["day"] == 14]
                d32 = [r for r in rows if r["day"] == 32]
                a, b = D.share(d14, key), D.share(d32, key)
                cells.append(f"{a:.0f}->{b:.0f}")
                changes.append(b - a)
                nf14 += sum(1 for r in d14 if not r.get("found_it"))
                nf32 += sum(1 for r in d32 if not r.get("found_it"))
            two_se = (2 * statistics.stdev(changes) / len(changes) ** 0.5
                      if len(changes) > 1 else 0)
            print(f"    {name:22s} " + "  ".join(f"{c:>11s}" for c in cells)
                  + f" {statistics.mean(changes):+12.1f} {two_se:6.1f} {nf14:>10d} -> {nf32:<5d}")


def merge_audit():
    print(f"\n===== what the merging step did   (wave: {D.WAVE_50})")
    arm = D.WAVE_50 / "ACE_as_published"
    if not arm.exists():
        print("  no ACE_as_published cells in this wave")
        return
    print(f"  {'household':14s} {'nights':>7s} {'proposed':>9s} {'answered':>9s} {'merged':>7s} "
          f"{'rejected':>9s} {'DISCARDED':>10s} {'nights with no verdict':>23s}")
    grand = collections.Counter()
    for cell in sorted(arm.iterdir()):
        f = cell / "cell.json"
        if not f.exists():
            continue
        t, asked, silent = collections.Counter(), 0, 0
        for n in json.load(open(f)).get("nightly") or []:
            m = n.get("how_it_merged") or {}
            t["nights"] += 1
            p = m.get("n_pairs_proposed", 0)
            t["proposed"] += p
            t["answered"] += m.get("n_returned_by_the_model", 0)
            t["merged"] += m.get("n_merged", 0)
            t["rejected"] += m.get("n_rejected", 0)
            t["unusable"] += m.get("n_unusable", 0)
            if p:
                asked += 1
                if m.get("n_merged", 0) + m.get("n_rejected", 0) == 0:
                    silent += 1
        grand.update(t)
        grand["asked"] += asked
        grand["silent"] += silent
        print(f"  {cell.name:14s} {t['nights']:7d} {t['proposed']:9d} {t['answered']:9d} "
              f"{t['merged']:7d} {t['rejected']:9d} {t['unusable']:10d} "
              f"{silent:>13d} of {asked:<6d}")
    print(f"  {'TOTAL':14s} {grand['nights']:7d} {grand['proposed']:9d} {grand['answered']:9d} "
          f"{grand['merged']:7d} {grand['rejected']:9d} {grand['unusable']:10d} "
          f"{grand['silent']:>13d} of {grand['asked']:<6d}")
    reasons = collections.Counter()
    for cell in sorted(arm.iterdir()):
        f = cell / "cell.json"
        if not f.exists():
            continue
        for n in json.load(open(f)).get("nightly") or []:
            for u in (n.get("how_it_merged") or {}).get("unusable") or []:
                reasons[u.get("why_unusable")] += 1
    if reasons:
        print("  why the discarded answers could not be used (a sample of up to six a night):")
        for why, n in reasons.most_common():
            print(f"    {n:5d}  {why}")


def main() -> int:
    table(D.both_spell_movers, "TABLE 2: the 14 objects that change room in both illnesses",
          (("found within three rooms", "found"), ("first room right", "first")))
    table(lambda h: sd.the_movers(D.home(h)),
          "TABLE 3: all 22 objects that moved in the first illness",
          (("found within three rooms", "found"),))
    merge_audit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
