"""Per-day / per-stage tables and expectation checks for the uq roster on a regime bank set.

    python3 -m baselines.patrol.uq_check --dir results/confidence_shift_2026-09-20/uq/regime/sick_owner \
        [--classical results/regime_search/sick_owner/classical] [--md report.md]

Reads whatever households are finished under <dir>/<agent>/hh_s*.jsonl (so it can run while the sweep
runs) and prints: accuracy per day with the stage boundaries marked, accuracy per stage, conformal
coverage / set size per day and per stage, martingale fire days per household, BMA weights per day,
reliability bins, and the E1-E7 checks of uq/regime/EXPECTATIONS.md as PASS / FAIL / n/a lines.
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
from collections import defaultdict
from typing import Dict, List


def load(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def acc(rows) -> float:
    return 100.0 * sum(r["correct"] for r in rows) / len(rows) if rows else float("nan")


def mean(rows, key) -> float:
    return sum(r[key] for r in rows) / len(rows) if rows else float("nan")


def fmt(x, nd=0) -> str:
    return "-" if x != x else f"{x:.{nd}f}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=pathlib.Path, required=True)
    ap.add_argument("--classical", type=pathlib.Path, default=None, help="classical logs for the E1 digit check")
    ap.add_argument("--md", type=pathlib.Path, default=None, help="also write the tables here")
    a = ap.parse_args(argv)
    agents = sorted(d.name for d in a.dir.iterdir() if d.is_dir())
    per: Dict[str, List[dict]] = {}
    sides: Dict[str, List[dict]] = {}
    for ag in agents:
        rows = []
        for p in sorted(glob.glob(str(a.dir / ag / "hh_s*.jsonl"))):
            rows += load(p)
        if rows:
            per[ag] = rows
            sides[ag] = [json.load(open(p)) for p in sorted(glob.glob(str(a.dir / ag / "hh_s*.side.json")))]
    if not per:
        print("no logs yet")
        return 0
    days = sorted({r["day_index"] for rows in per.values() for r in rows})
    stage_of = {}
    for rows in per.values():
        for r in rows:
            if "stage" in r:
                stage_of[r["day_index"]] = r["stage"]
    stages = []
    for d in days:
        s = stage_of.get(d, "?")
        if not stages or stages[-1] != s:
            stages.append(s)
    # stages in calendar order: the first is the lead, the second the shift, a third (if any) the return
    named = [s for s in stages if s != "?"]
    shift_days = sorted(d for d, s in stage_of.items() if len(named) > 1 and s == named[1])
    first_shift = min(shift_days) if shift_days else None
    first_return = min((d for d, s in stage_of.items() if len(named) > 2 and s == named[2]), default=None)
    lead_name = named[0] if named else "lead"

    def bar(d):   # a stage boundary marker before day d
        return "|" if d in (first_shift, first_return) else ""

    out = []
    hdr = "| agent | hh | " + " | ".join(f"{bar(d)}{d}" for d in days) + " | " + " | ".join(stages) + " |"
    out += [f"# uq roster on {a.dir}", "", "stages: " + ", ".join(f"{s}: days {min(d for d in days if stage_of.get(d) == s)}-{max(d for d in days if stage_of.get(d) == s)}" for s in stages if s != "?"), "",
            "## accuracy per day (%), then per stage", "", hdr, "|---|---|" + "---|" * (len(days) + len(stages))]
    by_stage: Dict[str, Dict[str, List[dict]]] = {}
    for ag, rows in per.items():
        by = defaultdict(list)
        st = defaultdict(list)
        for r in rows:
            by[r["day_index"]].append(r)
            st[r.get("stage", "?")].append(r)
        by_stage[ag] = st
        hh = len({r["household"] for r in rows})
        out.append(f"| {ag} | {hh} | " + " | ".join(fmt(acc(by[d])) for d in days) + " | " + " | ".join(fmt(acc(st[s]), 1) for s in stages) + " |")
    # per-stage accuracy: mean +- sd across households
    out += ["", "## accuracy per stage: mean ± 1 sd across households (n hh)", "", "| agent | " + " | ".join(stages) + " |", "|---|" + "---|" * len(stages)]
    for ag, rows in per.items():
        cells = []
        for s in stages:
            hh = defaultdict(list)
            for r in by_stage[ag][s]:
                hh[r["household"]].append(r["correct"])
            vals = [100.0 * sum(v) / len(v) for v in hh.values()]
            mu = sum(vals) / len(vals) if vals else float("nan")
            sd = (sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5 if len(vals) > 1 else 0.0
            cells.append(f"{mu:.1f} ± {sd:.1f} ({len(vals)})")
        out.append(f"| {ag} | " + " | ".join(cells) + " |")
    # confidence per day
    out += ["", "## mean confidence per day (top_prob; ocp: 1/|set|)", "", hdr, "|---|---|" + "---|" * (len(days) + len(stages))]
    for ag, rows in per.items():
        key = "conf_set" if "covered" in rows[0] else "top_prob"
        by = defaultdict(list)
        for r in rows:
            by[r["day_index"]].append(r)
        st = by_stage[ag]
        out.append(f"| {ag} | | " + " | ".join(fmt(mean(by[d], key), 2) for d in days) + " | " + " | ".join(fmt(mean(st[s], key), 2) for s in stages) + " |")
    checks = []
    # ---- E1 digit check against the classical rows
    if a.classical:
        for ag, rows in per.items():
            if not ag.startswith("none"):
                continue
            name = rows[0]["belief"]
            mm = pm = n = 0
            for hh in sorted({r["household"] for r in rows}):
                cp = a.classical / f"{hh}_t03.jsonl"
                if not cp.exists():
                    continue
                cls = {r["question_id"]: r for r in load(cp) if r["belief"] == name}
                if not cls:
                    checks.append(f"E1 {ag}: n/a — no {name} rows in {cp.name}")
                    continue
                for r in rows:
                    if r["household"] != hh:
                        continue
                    c = cls[r["question_id"]]
                    n += 1
                    mm += c["answer"] != r["answer"]
                    pm += abs(c["top_prob"] - r["top_prob"]) > 5e-5
            if n:
                checks.append(f"E1 {ag} vs classical {name}: {n} rows, {mm} answer mismatches, {pm} top_prob mismatches -> {'PASS' if mm == pm == 0 else 'FAIL'}")
    # ---- E2 conformal
    for ag, rows in per.items():
        if "covered" not in rows[0]:
            continue
        by = defaultdict(list)
        for r in rows:
            by[r["day_index"]].append(r)
        st = by_stage[ag]
        out += ["", f"## {ag}: coverage / set size / q_t per day (target 0.90)", "", "| | " + " | ".join(f"{bar(d)}{d}" for d in days) + " | " + " | ".join(stages) + " |", "|---|" + "---|" * (len(days) + len(stages))]
        out.append("| coverage | " + " | ".join(fmt(mean(by[d], "covered"), 3) for d in days) + " | " + " | ".join(fmt(mean(st[s], "covered"), 3) for s in stages) + " |")
        out.append("| set size | " + " | ".join(fmt(mean(by[d], "set_size"), 1) for d in days) + " | " + " | ".join(fmt(mean(st[s], "set_size"), 1) for s in stages) + " |")
        out.append("| q_t | " + " | ".join(fmt(mean(by[d], "q_t"), 3) for d in days) + " | " + " | ".join(fmt(mean(st[s], "q_t"), 3) for s in stages) + " |")
        cov = {s: mean([r for r in st[s] if r["day_index"] >= 3], "covered") for s in stages}
        ok = all(0.85 <= c <= 0.95 for c in cov.values() if c == c)
        checks.append(f"E2 {ag} coverage per stage " + ", ".join(f"{s} {c:.3f}" for s, c in cov.items()) + f" -> {'PASS' if ok else 'FAIL'}")
        if first_shift is not None:
            pre = mean([r for r in rows if r["day_index"] in (first_shift - 2, first_shift - 1)], "set_size")
            post = mean([r for r in rows if r["day_index"] in (first_shift, first_shift + 1)], "set_size")
            late = mean([r for r in rows if r["day_index"] >= days[-1] - 3], "set_size")
            checks.append(f"E2 {ag} set size days {first_shift - 2}-{first_shift - 1}: {pre:.2f} -> days {first_shift}-{first_shift + 1}: {post:.2f} (grow: {'PASS' if post > pre else 'FAIL'}); last 4 days {late:.2f} (shrink again: {'PASS' if late < post else 'FAIL'})")
            checks.append(f"E7 {ag} mean 1/|set| {lead_name} {mean(st.get(lead_name, []), 'conf_set'):.3f} vs shift stage {mean([r for r in rows if r['day_index'] in shift_days], 'conf_set'):.3f}")
    if "ocp_tt" in by_stage and "ocp_tt_norel" in by_stage:
        for s in stages:
            c1, c0 = mean(by_stage["ocp_tt"][s], "covered"), mean(by_stage["ocp_tt_norel"][s], "covered")
            checks.append(f"E2 rel vs norel coverage {s}: {c1:.3f} vs {c0:.3f} -> {'PASS' if c1 >= c0 - 0.02 else 'FAIL'}")
    # ---- E3-E5 martingale fires
    for ag, sd in sides.items():
        if not sd or "fires" not in sd[0] or "martingale" not in per[ag][0]:
            continue
        out += ["", f"## {ag}: fire days per household (shift days {shift_days[:1]}..{shift_days[-1:] if shift_days else ''}; return from {first_return})", ""]
        lead_hh = shift_hh = ret_hh = 0
        for s in sd:
            fd = sorted({f["day"] for f in s["fires"]})
            out.append(f"- {s['household']}: {fd if fd else 'no fires'}")
            if first_shift is not None:
                lead_hh += any(d < first_shift for d in fd)
                shift_hh += any(first_shift <= d <= first_shift + 1 for d in fd)
            if first_return is not None:
                ret_hh += any(first_return <= d <= first_return + 2 for d in fd)
        n = len(sd)
        ret_txt = f"on return days {first_return}-{first_return + 2} {ret_hh}/{n}" if first_return is not None else "no return stage"
        mx = defaultdict(float)
        for r in per[ag]:
            mx[r["day_index"]] = max(mx[r["day_index"]], r["martingale"])
        out.append("- max martingale per day (all hh): " + ", ".join(f"{bar(d)}{d}:{mx[d]:.0f}" for d in days))
        checks.append(f"E3/E4/E5 {ag}: fired in lead (days < {first_shift}) {lead_hh}/{n}; on days {first_shift}-{first_shift + 1 if first_shift is not None else ''} {shift_hh}/{n}; {ret_txt}")
        if "none_tt" in by_stage and first_shift is not None and ag.startswith("mart"):
            d16 = [first_shift + 2, first_shift + 3, first_shift + 4]
            a_m = acc([r for r in per[ag] if r["day_index"] in d16])
            a_n = acc([r for r in per["none_tt"] if r["day_index"] in d16])
            line = f"E5 {ag} vs none_tt: days {d16[0]}-{d16[-1]} {a_m:.1f} vs {a_n:.1f} ({a_m - a_n:+.1f}; want >= +3 -> {'PASS' if a_m - a_n >= 3 else 'FAIL'})"
            if first_return is not None:
                r_m = acc([r for r in per[ag] if r["day_index"] in (first_return, first_return + 1)])
                r_n = acc([r for r in per["none_tt"] if r["day_index"] in (first_return, first_return + 1)])
                line += f"; return days {first_return}-{first_return + 1} {r_m:.1f} vs {r_n:.1f} (drop again: {'PASS' if r_m < r_n else 'FAIL'})"
            checks.append(line)
    # ---- E6 bma weights
    for ag, rows in per.items():
        if "weights" not in rows[0]:
            continue
        by = defaultdict(lambda: defaultdict(list))
        for r in rows:
            for hl, w in r["weights"].items():
                by[r["day_index"]][hl].append(w)
        hls = list(rows[0]["weights"])
        out += ["", f"## {ag}: mean weight per half-life per day", "", "| half-life | " + " | ".join(f"{bar(d)}{d}" for d in days) + " |", "|---|" + "---|" * len(days)]
        wd = {d: {hl: sum(by[d][hl]) / len(by[d][hl]) for hl in hls} for d in days}
        for hl in hls:
            out.append(f"| {hl} | " + " | ".join(f"{wd[d][hl]:.2f}" for d in days) + " |")
        longs = [hl for hl in hls if hl == "None" or float(hl) >= 168]
        shorts = [hl for hl in hls if hl != "None" and float(hl) <= 72]
        if first_shift is not None:
            wl = lambda ds: sum(wd[d][hl] for d in ds for hl in longs) / len(ds)
            ws = lambda ds: sum(wd[d][hl] for d in ds for hl in shorts) / len(ds)
            lead_long = wl([d for d in days if first_shift - 6 <= d < first_shift])
            s13, s1415 = ws([first_shift - 1]), ws([first_shift, first_shift + 1])
            l1516 = wl([first_shift + 1, first_shift + 2])
            l_late = wl([d for d in days if d >= days[-1] - 5])
            checks.append(f"E6 {ag}: long-hl weight lead days {first_shift - 6}-{first_shift - 1} {lead_long:.2f} (>= 0.6: {'PASS' if lead_long >= 0.6 else 'FAIL'}); "
                          f"short-hl weight day {first_shift - 1} {s13:.2f} -> days {first_shift}-{first_shift + 1} {s1415:.2f} (+{s1415 - s13:.2f}, want >= 0.10: {'PASS' if s1415 - s13 >= 0.10 else 'FAIL'}); "
                          f"long-hl days {first_shift + 1}-{first_shift + 2} {l1516:.2f} -> last 6 days {l_late:.2f} (back up: {'PASS' if l_late > l1516 else 'FAIL'})")
            if "none_tt" in per:
                lead = [d for d in days if first_shift - 6 <= d < first_shift]
                d16 = [first_shift + 2, first_shift + 3, first_shift + 4]
                al, an = acc([r for r in rows if r["day_index"] in lead]), acc([r for r in per["none_tt"] if r["day_index"] in lead])
                bl, bn = acc([r for r in rows if r["day_index"] in d16]), acc([r for r in per["none_tt"] if r["day_index"] in d16])
                checks.append(f"E6 {ag} vs none_tt accuracy: lead days {lead[0]}-{lead[-1]} {al:.1f} vs {an:.1f} ({'PASS' if al >= an - 2 else 'FAIL'}); days {d16[0]}-{d16[-1]} {bl:.1f} vs {bn:.1f} ({'PASS' if bl >= bn else 'FAIL'})")
    # ---- reliability
    out += ["", "## reliability: accuracy within confidence bins (share of questions)", "", "| agent | " + " | ".join(f"{lo:.1f}-{lo + 0.2:.1f}" for lo in (0, .2, .4, .6, .8)) + " | ECE |", "|---|" + "---|" * 6]
    for ag, rows in per.items():
        key = "conf_set" if "covered" in rows[0] else "top_prob"
        cells, ece, accs = [], 0.0, {}
        for lo in (0, .2, .4, .6, .8):
            sub = [r for r in rows if lo <= r[key] < lo + 0.2 + (1e-9 if lo == .8 else 0)]
            if sub:
                ac = sum(r["correct"] for r in sub) / len(sub)
                ece += len(sub) / len(rows) * abs(ac - mean(sub, key))
                accs[lo] = ac
                cells.append(f"{100 * ac:.0f}% ({100 * len(sub) / len(rows):.0f}%)")
            else:
                cells.append("-")
        out.append(f"| {ag} | " + " | ".join(cells) + f" | {ece:.3f} |")
        if ag == "none_tt" and .8 in accs and .4 in accs:
            checks.append(f"E7 none_tt reliability slope: bin 0.8-1.0 {100 * accs[.8]:.0f}% vs bin 0.4-0.6 {100 * accs[.4]:.0f}% -> {'PASS' if accs[.8] > accs[.4] else 'FAIL'}")
    out += ["", "## expectation checks (uq/regime/EXPECTATIONS.md)", ""] + [f"- {c}" for c in checks]
    text = "\n".join(out) + "\n"
    print(text)
    if a.md:
        a.md.write_text(text)
    return 0


if __name__ == "__main__":
    main()
