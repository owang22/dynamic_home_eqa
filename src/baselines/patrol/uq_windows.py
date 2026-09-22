"""Affected-vs-unaffected accuracy in WINDOWS around each shift boundary, not whole-stage means (whole-stage means
wash the effect out — it lives in the first few days after each change, before re-learning catches up).

    python3 -m baselines.patrol.uq_windows --regimes sick10_partial,sick10_partial_s10_19 \
        --agents none_tt,none_tt72,detperson_tt72,oracle_tt72,none_mf72,none_lastseen \
        --out ../results/confidence_shift_2026-09-20/uq/windows.json

Windows (day_index, 1-indexed; lead 1-13, sick 14-23, return 24-31): last5lead (9-13), first3sick (14-16),
restsick (17-23), first3return (24-26), restreturn (27-31). "affected" = owner resident_1 (the sick resident on
these partial-shift banks); "unaffected" = every other owner. Per household: accuracy in each window; per-household
CHANGE = window accuracy - the reference window's accuracy (first3sick vs last5lead; first3return vs restsick).
gap = unaffected's change - affected's change (positive = the affected person's things suffered more, relative to
their own baseline, than the unaffected person's things did relative to theirs) — the paired, within-household
number Oliver's own spot check used. Reports mean +- sd across households for each group and window, the paired
change mean +- sd, and how many of N households clear a fixed gap bar (default 15 points).
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
UQ_DIR = ROOT / "results" / "confidence_shift_2026-09-20" / "uq" / "regime"

WINDOWS = {"last5lead": range(9, 14), "first3sick": range(14, 17), "restsick": range(17, 24),
           "first3return": range(24, 27), "restreturn": range(27, 32)}
WINDOW_ORDER = ["last5lead", "first3sick", "restsick", "first3return", "restreturn"]
PAIRS = [("first3sick", "last5lead"), ("first3return", "restsick")]   # (window, its reference window)
DAY_OF = {d: w for w, ds in WINDOWS.items() for d in ds}


def stats(vals):
    n = len(vals)
    if n == 0:
        return {"mean": float("nan"), "sd": float("nan"), "n": 0}
    mu = sum(vals) / n
    sd = (sum((v - mu) ** 2 for v in vals) / (n - 1)) ** 0.5 if n > 1 else 0.0
    return {"mean": mu, "sd": sd, "n": n}


def household_window_acc(regime: str, agent: str) -> dict:
    """{household: {"affected": {window: [n, ok, sum_conf, sum_set]}, "unaffected": {window: [...]}}} — sum_conf is
    top_prob (0 if absent), sum_set is set_size (0 if absent, i.e. not a conformal agent)."""
    out: dict = collections.defaultdict(lambda: {"affected": collections.defaultdict(lambda: [0, 0, 0.0, 0.0]),
                                                  "unaffected": collections.defaultdict(lambda: [0, 0, 0.0, 0.0])})
    for p in sorted(glob.glob(str(UQ_DIR / regime / agent / "hh_s*_t03.jsonl"))):
        hh = pathlib.Path(p).stem.split("_t03")[0]
        with open(p) as f:
            for l in f:
                r = json.loads(l)
                w = DAY_OF.get(r["day_index"])
                if w is None:
                    continue
                group = "affected" if r.get("owner") == "resident_1" else "unaffected"
                cell = out[hh][group][w]
                cell[0] += 1
                cell[1] += int(r["correct"])
                cell[2] += r.get("top_prob", 0.0)
                cell[3] += r.get("set_size", 0)
    return out


def analyze(regimes: list, agent: str, gap_bar: float) -> dict:
    hh_acc: dict = {}
    for regime in regimes:
        hh_acc.update(household_window_acc(regime, agent))
    windows_out = {}
    for w in WINDOW_ORDER:
        for group in ("affected", "unaffected"):
            vals = []
            for hh, d in hh_acc.items():
                n, ok = d[group][w][0], d[group][w][1]
                if n > 0:
                    vals.append(100 * ok / n)
            windows_out.setdefault(w, {})[group] = stats(vals)
    pairs_out = {}
    for w, ref in PAIRS:
        changes = {"affected": [], "unaffected": []}
        gaps = []
        for hh, d in hh_acc.items():
            ok_group = True
            per_group = {}
            for group in ("affected", "unaffected"):
                n_w, ok_w = d[group][w][0], d[group][w][1]
                n_r, ok_r = d[group][ref][0], d[group][ref][1]
                if n_w == 0 or n_r == 0:
                    ok_group = False
                    break
                per_group[group] = 100 * ok_w / n_w - 100 * ok_r / n_r
            if not ok_group:
                continue
            changes["affected"].append(per_group["affected"])
            changes["unaffected"].append(per_group["unaffected"])
            gaps.append(per_group["unaffected"] - per_group["affected"])
        pairs_out[f"{w}_vs_{ref}"] = {
            "affected_change": stats(changes["affected"]), "unaffected_change": stats(changes["unaffected"]),
            "gap": stats(gaps), "n_clear_bar": sum(1 for g in gaps if g >= gap_bar), "n_total": len(gaps),
            "gap_bar": gap_bar,
        }
    n_hh = len(hh_acc)
    return {"windows": windows_out, "pairs": pairs_out, "n_households": n_hh}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--regimes", required=True, help="comma-separated regime dirs to pool households from")
    ap.add_argument("--agents", required=True, help="comma-separated agent dir names")
    ap.add_argument("--gap-bar", type=float, default=15.0)
    ap.add_argument("--out", type=pathlib.Path, default=None)
    a = ap.parse_args(argv)
    regimes = a.regimes.split(",")
    agents = a.agents.split(",")

    result = {}
    for agent in agents:
        r = analyze(regimes, agent, a.gap_bar)
        result[agent] = r
        w = r["windows"]
        print(f"\n== {agent} (n={r['n_households']} households) ==", file=sys.stderr)
        print("  window        affected            unaffected", file=sys.stderr)
        for win in WINDOW_ORDER:
            af, un = w[win]["affected"], w[win]["unaffected"]
            print(f"  {win:13s} {af['mean']:5.1f}±{af['sd']:4.1f} (n={af['n']})   {un['mean']:5.1f}±{un['sd']:4.1f} (n={un['n']})", file=sys.stderr)
        for key, p in r["pairs"].items():
            ac, uc, g = p["affected_change"], p["unaffected_change"], p["gap"]
            print(f"  {key}: affected change {ac['mean']:+5.1f}±{ac['sd']:4.1f}  unaffected change {uc['mean']:+5.1f}±{uc['sd']:4.1f}  "
                  f"gap {g['mean']:+5.1f}±{g['sd']:4.1f}  clears >={p['gap_bar']:.0f}: {p['n_clear_bar']}/{p['n_total']}", file=sys.stderr)

    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(result, indent=1, sort_keys=True))
        print(f"\nwrote {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
