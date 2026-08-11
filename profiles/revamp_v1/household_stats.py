#!/usr/bin/env python3
"""Cross-household summary: realized timing marginals + bank-intrinsic stats.

For every household with a 28-day timeline and exported bank, report per
resident the realized wake / first-departure / return / bed timings
(median [p10-p90], from residents.jsonl block realizations, classified by
activity-name keywords), and per bank the intrinsic dynamics stats
(dwell-weighted modal share, moves/day, stint lengths) — one table to spot
a household that came out weird.

ATUS survey marginals: the anchor machinery exists
(src/dynbelief/anchors/) but its raw data is NEEDS_DATA — bls.gov blocks
scripted downloads. Place atusact/atusresp zips in data/anchors/atus/raw/
and run compile_envelope.py to add the survey columns; until then this
report carries realized timings only.

Usage:  python profiles/revamp_v1/household_stats.py \
            --out reports/baselines/households_summary.md
"""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics

SLEEP_KEYS = ("sleep", "bedtime")
MEAL_KEYS = ("meal", "breakfast", "lunch", "dinner", "supper")


def hhmm(minute_of_day: float) -> str:
    m = int(minute_of_day) % 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def spread(values: list[float]) -> str:
    if not values:
        return "—"
    values = sorted(values)
    p10 = values[int(0.1 * (len(values) - 1))]
    p90 = values[int(0.9 * (len(values) - 1))]
    return f"{hhmm(statistics.median(values))} [{hhmm(p10)}–{hhmm(p90)}]"


def resident_timings(blocks: list[dict]) -> dict[str, str]:
    wake, depart, back, meals = [], [], [], []
    by_day: dict[int, list[dict]] = {}
    for b in blocks:
        by_day.setdefault(b["t0"] // 1440, []).append(b)
    for day_blocks in by_day.values():
        day_blocks.sort(key=lambda b: b["t0"])
        sleeps = [b for b in day_blocks
                  if any(k in b["activity"] for k in SLEEP_KEYS)
                  and b["t1"] - b["t0"] > 180]
        if sleeps:
            wake.append(sleeps[0]["t1"] % 1440)
        else:
            # No named sleep block: first realized block of the day is the
            # wake proxy (hh_002-style specs start the day with a morning
            # activity).
            wake.append(day_blocks[0]["t0"] % 1440)
        # Absences: `at: ELSEWHERE` blocks (hh_001 convention) or named
        # depart/return activity pairs (hh_002 convention).
        aways = [b for b in day_blocks if b.get("at") == "ELSEWHERE"]
        departs = ([b["t0"] % 1440 for b in aways]
                   or [b["t0"] % 1440 for b in day_blocks
                       if "depart" in b["activity"]
                       or b["activity"].endswith("_run")])
        returns = ([b["t1"] % 1440 for b in aways]
                   or [b["t0"] % 1440 for b in day_blocks
                       if "return" in b["activity"]])
        if departs:
            depart.append(min(departs))
        if returns:
            back.append(max(returns))
        meals += [b["t0"] % 1440 for b in day_blocks
                  if any(k in b["activity"] for k in MEAL_KEYS)]
    return {"wake": spread(wake), "first_departure": spread(depart),
            "return": spread(back), "meal_starts": spread(meals)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timelines", type=pathlib.Path,
                    default=pathlib.Path("profiles/revamp_v1/claude-fable-5/timelines"))
    ap.add_argument("--banks", type=pathlib.Path,
                    default=pathlib.Path("banks/baselines"))
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    from baselines.bank import JsonlBank
    from baselines.bankstats import compute_bank_stats

    lines = ["# Household summary — realized timings + intrinsic dynamics", "",
             "ATUS survey columns: NEEDS_DATA (bls.gov blocks scripted "
             "downloads; see module docstring for the manual path).", "",
             "NOTE: specs encode absences two ways — `at: ELSEWHERE` blocks "
             "(hh_001 style) or named depart/return pairs (hh_002 style). "
             "Only the former feeds the exporter's person-away projection; "
             "depart/return-pair households keep carried phones ON_PERSON "
             "during absences. Standardization candidate.", "",
             "## Realized timing marginals (median [p10–p90], from 28-day "
             "block realizations)", "",
             "| household | resident | wake | first departure | return | meal starts |",
             "|---|---|---|---|---|---|"]
    stats_rows = []
    for tdir in sorted(args.timelines.glob("hh_0*_seed0_28d")):
        hh = tdir.name.split("_seed0")[0]
        by_res: dict[str, list[dict]] = {}
        for line in open(tdir / "residents.jsonl"):
            b = json.loads(line)
            by_res.setdefault(b["resident"], []).append(b)
        for res, blocks in sorted(by_res.items()):
            t = resident_timings(blocks)
            lines.append(f"| {hh} | {res} | {t['wake']} | "
                         f"{t['first_departure']} | {t['return']} | "
                         f"{t['meal_starts']} |")
        bank_path = args.banks / f"{hh}_28d_uniform.jsonl"
        if bank_path.exists():
            s = compute_bank_stats(JsonlBank(path=bank_path))
            stats_rows.append(
                f"| {hh} | {s.n_objects} | {s.modal_share_time:.3f} | "
                f"{s.modal_share_questions:.3f} | {s.moves_per_day:.1f} | "
                f"{s.displacement_median_h:.1f} / {s.displacement_p90_h:.1f} | "
                f"{'PASS' if s.modal_share_time <= 0.60 else 'FAIL'} |")
    lines += ["", "## Bank-intrinsic dynamics (28-day uniform banks)", "",
              "| household | objects | modal share (time) | at query times | "
              "moves/day | stint med/p90 h | stationarity |",
              "|---|---|---|---|---|---|---|"] + stats_rows + [""]
    args.out.write_text("\n".join(lines))
    print(f"wrote {args.out} ({len(stats_rows)} banks)")


if __name__ == "__main__":
    main()
