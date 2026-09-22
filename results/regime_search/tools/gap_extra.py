#!/usr/bin/env python3
"""Per-day calibration GAP (stated confidence minus accuracy), pooled over households, for three populations:
"household" (sick10_all, 10 households, full-house shift), "person" (sick10_owner, 10 households, owner-framed
routines), "partial" (sick10_partial, 10 households, only some residents shift — adds the global-vs-per-person
shared-state agents alongside the same global roster).

For every non-conformal method: fits a monotone map from stated confidence to observed accuracy on LEAD DAYS ONLY
(days 1-13, pooled across households) — bin by confidence (20 bins), then pool-adjacent-violators (PAV) over the
ordered bin means so the map is guaranteed non-decreasing — and applies that map to every day's answers (lead
included) to get a "lead-calibrated confidence". This separates the definition-level offset (a method that always
says ~45% because it is a mixture over ~38 places, even though it is right ~75% of the time under a smoothing
floor) from real day-to-day tracking (does the gap stay flat through the shift once the definition-level offset is
removed?). Both raw and lead-calibrated cells are stored so the page can draw either gap curve.

For conformal-style methods (conf_of() = 1/|set|, not a probability): stores per-day coverage (share of questions
where the truth was in the predicted set) against the 0.90 target, and mean set size, instead of a confidence gap.

No re-run of any model: every number here already sits in the classical/UQ jsonl logs this study already produced.

    python3 tools/gap_extra.py  (run from results/regime_search)
"""
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load, SHORT  # noqa
from story_data import CLASSICAL, UQA, conf_of  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UQ = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "regime")
LABEL = "t03"
LEAD_DAYS = set(range(1, 14))
REPORT_WINDOWS = {"lead": set(range(1, 14)), "d14_16": {14, 15, 16}, "d24_26": {24, 25, 26}}
N_BINS = 20

CONFORMAL_KEYS = {"conformal", "nexcp", "conformal_person"}

POPULATIONS = {
    "household": "sick10_all",
    "person": "sick10_owner",
    "partial": "sick10_partial",
    "person2x": "sick2x_owner",   # the one-person spell twice (42 days); lead-day fit still days 1-13
}
# extra per-person / oracle agents, present only where roster.sh ran them (sick10_partial today) — mapped to their
# own gap keys so they sit alongside the global roster rather than colliding with it
PERSON_UQA = {
    "bma_person": ("bma_person", False),
    "ocpperson_tt": ("conformal_person", True),
    "detperson_tt72": ("detector3d_person", False),
    "oracle_tt72": ("oracle72", False),
}


def sources(pop_dir, hh):
    d = f"{ROOT}/{pop_dir}"
    uqa = dict(UQA)
    srcs = [(f"{d}/classical/{hh}_{LABEL}.jsonl", None)] + [(f"{UQ}/{pop_dir}/{a}/{hh}_{LABEL}.jsonl", a) for a in uqa]
    for a in PERSON_UQA:
        p = f"{UQ}/{pop_dir}/{a}/{hh}_{LABEL}.jsonl"
        if os.path.exists(p):
            srcs.append((p, a))
    return srcs, uqa


def key_of(forced, belief, uqa):
    if forced is None:
        return CLASSICAL.get(SHORT.get(belief, ""))
    if forced in PERSON_UQA:
        return PERSON_UQA[forced][0]
    return uqa.get(forced)


def pav(bin_stats):
    """bin_stats: ordered list of (mean_x, mean_y, weight) for populated bins, ordered by mean_x ascending.
    Returns knots: list of (xmin, xmax, calibrated_y), non-decreasing calibrated_y, covering all of bin_stats."""
    stack = []  # each: [sum_y*w, weight, xmin, xmax]
    for x, y, w in bin_stats:
        stack.append([y * w, w, x, x])
        while len(stack) >= 2 and (stack[-2][0] / stack[-2][1]) > (stack[-1][0] / stack[-1][1]):
            b = stack.pop()
            a = stack.pop()
            stack.append([a[0] + b[0], a[1] + b[1], a[2], b[3]])
    return [(a[2], a[3], a[0] / a[1]) for a in stack]


def fit_lead_map(points):
    """points: list of (conf, ok) from lead days, pooled over households. -> knots (see pav()), or None."""
    bins = [[0, 0, 0.0] for _ in range(N_BINS)]  # n, ok, sum_conf
    for c, ok in points:
        b = min(N_BINS - 1, max(0, int(c * N_BINS)))
        cell = bins[b]
        cell[0] += 1
        cell[1] += ok
        cell[2] += c
    bin_stats = [(sc / n, ok / n, n) for n, ok, sc in bins if n >= 5]
    if not bin_stats:
        return None
    return pav(bin_stats)


def apply_map(knots, c):
    if not knots:
        return c
    for xmin, xmax, y in knots:
        if c <= xmax:
            return y
    return knots[-1][2]


def collect(pop_dir):
    """-> {key: {hh: [(day, conf, ok), ...]}}, plus which keys are conformal (coverage/set_size instead)."""
    per_key = collections.defaultdict(lambda: collections.defaultdict(list))
    conf_extra = collections.defaultdict(lambda: collections.defaultdict(list))  # key -> hh -> [(day, covered, set_size)]
    n_days = 0
    for bp in sorted(glob.glob(f"{ROOT}/{pop_dir}/banks/hh_s*_{LABEL}.jsonl")):
        hh = os.path.basename(bp).split(f"_{LABEL}")[0]
        h, qs = load(bp, 2)
        n_days = h["n_days"]
        srcs, uqa = sources(pop_dir, hh)
        for cp, forced in srcs:
            if not os.path.exists(cp):
                continue
            for l in open(cp):
                r = json.loads(l)
                q = qs.get(r["question_id"])
                if not q:
                    continue
                key = key_of(forced, r.get("belief", ""), uqa)
                if not key:
                    continue
                ok = int(r["correct"])
                if key in CONFORMAL_KEYS:
                    conf_extra[key][hh].append((q["day"], int(r.get("covered") in (True, "True")), float(r.get("set_size", 0))))
                else:
                    per_key[key][hh].append((q["day"], conf_of(r), ok))
    return per_key, conf_extra, n_days


def build_population(pop_dir):
    per_key, conf_extra, n_days = collect(pop_dir)
    methods = {}
    for key, by_hh in per_key.items():
        lead_pts = [(c, ok) for hh, rows in by_hh.items() for (d, c, ok) in rows if d in LEAD_DAYS]
        knots = fit_lead_map(lead_pts)
        cells = {}
        for hh, rows in by_hh.items():
            arr = [[0, 0, 0.0, 0.0] for _ in range(n_days)]  # n, ok, sum_conf_raw, sum_conf_leadcal
            for d, c, ok in rows:
                if d >= n_days:
                    continue
                cell = arr[d]
                cell[0] += 1
                cell[1] += ok
                cell[2] += c
                cell[3] += apply_map(knots, c)
            cells[hh] = arr
        methods[key] = {"cells": cells, "lead_map": [[round(a, 4), round(b, 4), round(c, 4)] for a, b, c in (knots or [])]}
    conformal = {}
    for key, by_hh in conf_extra.items():
        cells = {}
        for hh, rows in by_hh.items():
            arr = [[0, 0, 0.0] for _ in range(n_days)]  # n, n_covered, sum_set_size
            for d, cov, sz in rows:
                if d >= n_days:
                    continue
                cell = arr[d]
                cell[0] += 1
                cell[1] += cov
                cell[2] += sz
            cells[hh] = arr
        conformal[key] = cells
    return {"methods": methods, "conformal": conformal, "days": n_days}


def stage_gap(cells, days, raw):
    """cells: {hh: [[n,ok,sum_raw,sum_leadcal],...]}. -> per-household-mean gap (pp), sd across households, n hh."""
    idx = 2 if raw else 3
    vals = []
    for hh, arr in cells.items():
        n = ok = sc = 0
        for d in days:
            if d >= len(arr):
                continue
            n += arr[d][0]
            ok += arr[d][1]
            sc += arr[d][idx]
        if n:
            vals.append(100 * (sc - ok) / n)
    if not vals:
        return None
    m = sum(vals) / len(vals)
    s = (sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5 if len(vals) > 1 else 0.0
    return {"gap": round(m, 1), "sd": round(s, 1), "n_hh": len(vals)}


def main():
    out = {"populations": {}, "windows": {k: sorted(v) for k, v in REPORT_WINDOWS.items()}}
    lines = []
    for pop_key, pop_dir in POPULATIONS.items():
        if not os.path.isdir(f"{ROOT}/{pop_dir}"):
            lines.append(f"{pop_key} ({pop_dir}): directory missing, skipped")
            continue
        built = build_population(pop_dir)
        out["populations"][pop_key] = built
        lines.append(f"{pop_key} ({pop_dir}): {built['days']} days, {len(built['methods'])} gap methods, {len(built['conformal'])} conformal methods")
        for key, m in sorted(built["methods"].items()):
            summ = {}
            for wname, days in REPORT_WINDOWS.items():
                summ[wname] = {"raw": stage_gap(m["cells"], out["windows"][wname], True),
                                "leadcal": stage_gap(m["cells"], out["windows"][wname], False)}
            m["summary"] = summ
            r = summ["lead"]["raw"]; l = summ["lead"]["leadcal"]
            s16 = summ["d14_16"]["raw"]; s16c = summ["d14_16"]["leadcal"]
            s26 = summ["d24_26"]["raw"]; s26c = summ["d24_26"]["leadcal"]
            lines.append(f"  {key:20s} lead raw {r['gap'] if r else 'NA'}±{r['sd'] if r else 0}  leadcal {l['gap'] if l else 'NA'}  |"
                          f"  d14-16 raw {s16['gap'] if s16 else 'NA'}  leadcal {s16c['gap'] if s16c else 'NA'}  |"
                          f"  d24-26 raw {s26['gap'] if s26 else 'NA'}  leadcal {s26c['gap'] if s26c else 'NA'}")
        for key, cells in sorted(built["conformal"].items()):
            n = ncov = 0
            for hh, arr in cells.items():
                for d in REPORT_WINDOWS["lead"]:
                    if d < len(arr):
                        n += arr[d][0]; ncov += arr[d][1]
            lines.append(f"  {key:20s} (conformal) lead coverage {100*ncov/n:.1f}% (target 90%)" if n else f"  {key} (conformal) no lead data")

    path = f"{ROOT}/story_extra.json"
    data = json.load(open(path)) if os.path.exists(path) else {}
    data["gap"] = out
    json.dump(data, open(path, "w"), separators=(",", ":"))
    lines.append(f"merged gap into {path}: other keys kept: {[k for k in data if k != 'gap']}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
