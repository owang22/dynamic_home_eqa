#!/usr/bin/env python3
"""Score the mode memory against last seen and our arm, on the runs it was given.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/score_household_mode.py
"""
import glob
import json
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import paper_data as D                                            # noqa: E402
from self_improve import search_driven as sd                      # noqa: E402
from self_improve.frozen_household import FrozenHousehold         # noqa: E402

SAVED = pathlib.Path("results/self_improve/paper/household_mode")
RUNS = {"ten homes, 8 a day": ("results/self_improve/overnight_wave/cells", "ten_homes",
                               D.HOMES_10, range(1, 32)),
        "three homes, 50 days, 24 a day": ("results/self_improve/wave_the_second_illness/cells",
                                           "all_generated_v2_twice", D.HOMES_50, range(1, 50)),
        "five wider homes, 24 a day": ("results/self_improve/wave_wider_five/cells",
                                       "headline_five",
                                       ("hh_s32_t03", "hh_s48_t03", "hh_s63_t03", "hh_s93_t03",
                                        "hh_s151_t03"), range(1, 32)),
        "five wider homes, 8 a day": ("results/self_improve/wave_the_budget_sweep_q8/cells",
                                      "headline_five",
                                      ("hh_s32_t03", "hh_s48_t03", "hh_s63_t03", "hh_s93_t03",
                                       "hh_s151_t03"), range(1, 32)),
        "five wider homes, 4 a day": ("results/self_improve/wave_the_budget_sweep_q4/cells",
                                      "headline_five",
                                      ("hh_s32_t03", "hh_s48_t03", "hh_s63_t03", "hh_s93_t03",
                                       "hh_s151_t03"), range(1, 32))}
MEAS = {"first room right": lambda r: r.get("found_at_step") == 1,
        "found within 3": lambda r: bool(r.get("found_it"))}


def mode_rows(run, home, alpha=1.0, stay=0.9):
    tag = f"{run.replace(' ', '_').replace(',', '')}~{home}~a{alpha}~s{stay}.json"
    path = SAVED / tag
    return json.loads(path.read_text())["rows"] if path.exists() else None


def main() -> int:
    for run, (cells_dir, banks, homes, days) in RUNS.items():
        cells = pathlib.Path(cells_dir)
        banks_dir = pathlib.Path(f"results/self_improve/varied_homes/{banks}/banks")
        arms = {"last seen": lambda h: D.rows(cells, "last_seen_no_model", h)}
        if (cells / "the_log_and_notes_about_the_routine").exists():
            arms["log and notes"] = lambda h: D.rows(
                cells, "the_log_and_notes_about_the_routine", h)
        arms["household mode"] = lambda h: mode_rows(run, h)
        print(f"\n===== {run}")
        for measure, fn in MEAS.items():
            for movers_only in (False, True):
                print(f"\n  --- {measure}, "
                      f"{'moved objects' if movers_only else 'every question'}")
                base = {}
                for label, get in arms.items():
                    levels, diffs, n = [], [], 0
                    for home in homes:
                        movers = (sd.the_movers(FrozenHousehold(banks_dir / f"{home}.jsonl"))
                                  if movers_only else None)
                        rs = [r for r in (get(home) or []) if r["day"] in days
                              and (not movers_only or r["object_id"] in movers)]
                        if len(rs) < 8:
                            continue
                        value = 100 * sum(1 for r in rs if fn(r)) / len(rs)
                        levels.append(value)
                        n += len(rs)
                        if label == "last seen":
                            base[home] = value
                        elif home in base:
                            diffs.append(value - base[home])
                    if not levels:
                        continue
                    extra = ""
                    if diffs:
                        tse = 2 * statistics.stdev(diffs) / len(diffs) ** 0.5
                        extra = (f"  vs last seen {statistics.mean(diffs):+6.1f}  2 SE {tse:5.1f}"
                                 f"  same sign {sum(1 for v in diffs if v > 0)} of {len(diffs)}")
                    print(f"    {label:18s}{statistics.mean(levels):7.1f}{n:9d} questions{extra}")

    # --- the recurrence table on both-spell movers
    print("\n\n===== day 14 against day 32, both-spell movers, 50-day run")
    for measure, fn in MEAS.items():
        print(f"\n  --- {measure}")
        for label in ("last seen", "log and notes", "household mode"):
            per = []
            for home in D.HOMES_50:
                both = D.both_spell_movers(home)
                if label == "household mode":
                    rs = mode_rows("three homes, 50 days, 24 a day", home) or []
                else:
                    arm = ("last_seen_no_model" if label == "last seen"
                           else "the_log_and_notes_about_the_routine")
                    rs = D.rows(D.WAVE_50, arm, home)
                a = [r for r in rs if r["day"] == 14 and r["object_id"] in both]
                b = [r for r in rs if r["day"] == 32 and r["object_id"] in both]
                per.append((100 * sum(1 for r in a if fn(r)) / len(a),
                            100 * sum(1 for r in b if fn(r)) / len(b), len(a), len(b)))
            change = [b - a for a, b, _, _ in per]
            tse = 2 * statistics.stdev(change) / len(change) ** 0.5
            print(f"    {label:16s} " + "  ".join(f"{a:.0f}->{b:.0f} ({na}/{nb})"
                                                  for a, b, na, nb in per)
                  + f"   mean {statistics.mean(change):+.1f}, 2 SE {tse:.1f}")

    print("\n\n===== modes created, every setting, every household")
    grid = {}
    for path in sorted(glob.glob(str(SAVED / "*.json"))):
        d = json.loads(pathlib.Path(path).read_text())
        grid.setdefault((d["alpha"], d["stay"]), []).append(d["n_modes"])
    for (alpha, stay), counts in sorted(grid.items()):
        print(f"    alpha {alpha:<4} stay {stay:<5} -> modes per household: "
              f"{sorted(set(counts))} across {len(counts)} cells")
    any_cell = json.loads(next(iter(sorted(glob.glob(str(SAVED / '*50_days*'))))).replace(
        "\\", "") if False else pathlib.Path(
        sorted(glob.glob(str(SAVED / "*~a1.0~s0.9.json")))[0]).read_text())
    print(f"\n    mode-by-day, {any_cell['household']} ({any_cell['run']}): "
          f"every day assigned to mode "
          f"{sorted({m for _, m in any_cell['day_to_mode']})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
