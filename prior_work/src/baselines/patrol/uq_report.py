"""Per-day tables, reliability and coverage for the uq roster -> uq/<set>/report.md

    python3 -m baselines.patrol.uq_report --dir results/confidence_shift_2026-09-20/uq/fb --banks results/.../heldout_fb/banks
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
from collections import defaultdict

DAYN = {1: "Wed", 2: "Thu", 3: "Fri", 4: "Sat", 5: "Sun", 6: "Mon", 7: "Tue"}


def load(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=pathlib.Path, required=True)
    ap.add_argument("--banks", type=pathlib.Path, required=True)
    a = ap.parse_args(argv)
    shift = {}
    for b in sorted(a.banks.glob("*.jsonl")):
        h = json.loads(b.open().readline())
        shift[h["household_id"]] = set(h["shift_days"])
    agents = sorted(d.name for d in a.dir.iterdir() if d.is_dir() and d.name != "probe")
    md = [f"# UQ roster on {a.banks}", ""]
    md += ["## Accuracy per day (all questions) | mean confidence per day", "", "| agent | hh | " + " | ".join(DAYN.values()) + " | all | conf: " + " | ".join(DAYN.values()) + " |",
           "|---|---|" + "---|" * 15]
    per_agent = {}
    for ag in agents:
        rows = []
        for p in sorted(glob.glob(str(a.dir / ag / "hh_s*.jsonl"))):
            rows += load(p)
        if not rows:
            continue
        per_agent[ag] = rows
        hh = len({r["household"] for r in rows})
        by = defaultdict(list)
        for r in rows:
            by[r["day_index"]].append(r)
        acc = [f"{100 * sum(x['correct'] for x in by[d]) / len(by[d]):.0f}%" for d in DAYN]
        conf_key = "conf_set" if ag.startswith("ocp") else "top_prob"
        conf = [f"{sum(x[conf_key] for x in by[d]) / len(by[d]):.2f}" for d in DAYN]
        md.append(f"| {ag} | {hh} | " + " | ".join(acc) + f" | {100 * sum(r['correct'] for r in rows) / len(rows):.1f}% | " + " | ".join(conf) + " |")
    # shift vs non-shift days
    md += ["", "## Accuracy on shift days vs non-shift days (per household's own shift days)", "", "| agent | shift days | non-shift days | drop |", "|---|---|---|---|"]
    for ag, rows in per_agent.items():
        s = [r["correct"] for r in rows if r["day_index"] in shift[r["household"]]]
        n = [r["correct"] for r in rows if r["day_index"] not in shift[r["household"]]]
        md.append(f"| {ag} | {100 * sum(s) / len(s):.1f}% ({len(s)}) | {100 * sum(n) / len(n):.1f}% ({len(n)}) | {100 * (sum(n) / len(n) - sum(s) / len(s)):+.1f} |")
    # reliability
    md += ["", "## Reliability: accuracy within confidence bins (share of questions in the bin)", "", "| agent | " + " | ".join(f"{lo:.1f}-{lo + 0.2:.1f}" for lo in (0, .2, .4, .6, .8)) + " | ECE |", "|---|" + "---|" * 6]
    for ag, rows in per_agent.items():
        conf_key = "conf_set" if ag.startswith("ocp") else "top_prob"
        cells, ece = [], 0.0
        for lo in (0, .2, .4, .6, .8):
            sub = [r for r in rows if lo <= r[conf_key] < lo + 0.2 + (1e-9 if lo == .8 else 0)]
            if sub:
                acc = sum(r["correct"] for r in sub) / len(sub)
                mc = sum(r[conf_key] for r in sub) / len(sub)
                ece += len(sub) / len(rows) * abs(acc - mc)
                cells.append(f"{100 * acc:.0f}% ({100 * len(sub) / len(rows):.0f}%)")
            else:
                cells.append("-")
        md.append(f"| {ag} | " + " | ".join(cells) + f" | {ece:.3f} |")
    # conformal coverage and set size per day
    for ag in [x for x in per_agent if x.startswith("ocp")]:
        rows = per_agent[ag]
        by = defaultdict(list)
        for r in rows:
            by[r["day_index"]].append(r)
        md += ["", f"## {ag}: coverage and set size per day (target 0.90)", "", "| | " + " | ".join(DAYN.values()) + " | all |", "|---|" + "---|" * 8]
        md.append("| coverage | " + " | ".join(f"{sum(x['covered'] for x in by[d]) / len(by[d]):.3f}" for d in DAYN) + f" | {sum(r['covered'] for r in rows) / len(rows):.3f} |")
        md.append("| set size | " + " | ".join(f"{sum(x['set_size'] for x in by[d]) / len(by[d]):.1f}" for d in DAYN) + f" | {sum(r['set_size'] for r in rows) / len(rows):.1f} |")
        md.append("| q_t | " + " | ".join(f"{sum(x['q_t'] for x in by[d]) / len(by[d]):.3f}" for d in DAYN) + " | |")
        s = [r for r in rows if r["day_index"] in shift[r["household"]]]
        n = [r for r in rows if r["day_index"] not in shift[r["household"]]]
        md.append(f"| shift vs non-shift | coverage {sum(r['covered'] for r in s) / len(s):.3f} vs {sum(r['covered'] for r in n) / len(n):.3f}; "
                  f"set {sum(r['set_size'] for r in s) / len(s):.1f} vs {sum(r['set_size'] for r in n) / len(n):.1f} | | | | | | | |")
    # martingale fires
    if "martingale" in per_agent:
        tp = fn = fp = tn = 0
        for p in sorted(glob.glob(str(a.dir / "martingale" / "hh_s*.side.json"))):
            side = json.load(open(p))
            fired = {f["day"] for f in side["fires"]}
            for d in range(1, 8):
                if d in side["shift_days"]:
                    tp += d in fired; fn += d not in fired
                else:
                    fp += d in fired; tn += d not in fired
        mx = defaultdict(float)
        for r in per_agent["martingale"]:
            mx[r["day_index"]] = max(mx[r["day_index"]], r["martingale"])
        md += ["", "## martingale: fires", "", f"fired on {tp}/{tp + fn} shift days and {fp}/{fp + tn} non-shift days (threshold 100). "
               f"Max martingale value per day over all households: " + ", ".join(f"{DAYN[d]} {mx[d]:.1f}" for d in DAYN)]
    if "bma" in per_agent:
        by = defaultdict(lambda: defaultdict(list))
        for r in per_agent["bma"]:
            for hl, w in r["weights"].items():
                by[r["day_index"]][hl].append(w)
        md += ["", "## bma: mean weight per half-life per day", "", "| half-life | " + " | ".join(DAYN.values()) + " |", "|---|" + "---|" * 7]
        for hl in by[1]:
            md.append(f"| {hl} | " + " | ".join(f"{sum(by[d][hl]) / len(by[d][hl]):.2f}" for d in DAYN) + " |")
    (a.dir / "report.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    main()
