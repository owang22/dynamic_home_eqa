"""Follow-on figures: confidence and accuracy per day, affected vs unaffected.

    python3 -m baselines.patrol.followon_figs --root results/confidence_shift_2026-09-20 --out results/.../followon/figs

Lines (told arm unless noted), each split into affected (solid) and
unaffected (dashed) questions by ``followon/affected/labels.jsonl``:

* most frequent, no reset           followon/bocpd/hh_s*_none.jsonl
* BOCPD reset (told)                followon/bocpd/hh_s*_told.jsonl
* most frequent + affected list     followon/bocpd/hh_s*_listed.jsonl  (reset only the listed objects)
* conformal-wrapped most frequent   followon/aci/hh_s*_mf_aci.jsonl  (confidence = 1 - threshold)
* Perpetua*, last seen              heldout/classical/hh_s*_p2.jsonl
* hypothesis mixture (told)         heldout/hyp/logs/hh_s*_longleaf_told.jsonl
* mixture told + affected-list reset followon/mixture_reset/hh_s*_told_reset.jsonl (when present)

Secondary: not-told arm, BOCPD detect vs mixture not told.  Third: the
conformal wrapper's set size and coverage per day.  Weekend days are
shaded; event days are household-specific and enter through the split.
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KINDS = ("event_moved", "weekend_moved", "stayed_put", "after_shift", "other_event", "small_cause", "plain")
# pastel palette (Oliver's request: low-saturation lines, soft ground)
KIND_COLOR = dict(zip(KINDS, ("#e79c9c", "#f2b48c", "#e3cf8a", "#b8b3ad", "#c9b8f0", "#f0a8c8", "#8fb5a0")))
PALETTE = {"most frequent": "#9ec5f0", "most frequent, 24 h half-life": "#7fc8c0", "BOCPD detect (not told)": "#c9a98a", "BOCPD reset (told)": "#eb6834", "conformal most frequent": "#1baf7a",
           "Perpetua*": "#eda100", "mixture (told)": "#e87ba4", "last seen": "#008300",
           "mixture told + affected reset": "#4a3aa7", "most frequent + affected list": "#e34948",
           "BOCPD detect (not told)": "#eb6834", "mixture (not told)": "#e87ba4"}
DAY_NAMES = {1: "Wed", 2: "Thu", 3: "Fri", 4: "Sat", 5: "Sun", 6: "Mon", 7: "Tue"}
WEEKEND = (4, 5)


def load_jsonl(path: str) -> List[dict]:
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def load_labels(root: pathlib.Path, tag: str = "p8") -> Dict[Tuple[str, str], dict]:
    """The labels are per patrol density (freshness depends on the patrol times)."""
    return {(r["household"], r["question_id"]): r for r in load_jsonl(str(root / f"followon/affected/labels_{tag}.jsonl"))}


def rows_for(root: pathlib.Path, source: str, conf_field: str = "top_prob", belief_prefix: Optional[str] = None,
             conf_scale: float = 1.0) -> List[dict]:
    """``conf_field`` ``inv_set``: confidence = 1 / prediction-set size (the conformal lines)."""
    out = []
    for p in sorted(glob.glob(str(root / source))):
        for r in load_jsonl(p):
            if belief_prefix and not str(r.get("belief", r.get("agent", ""))).startswith(belief_prefix):
                continue
            hh = r.get("household") or pathlib.Path(p).name.split("_p")[0]
            correct = r.get("correct")
            if correct is None:
                correct = r.get("answer", r.get("argmax")) == r.get("truth")
            conf = (1.0 / max(1, int(r.get("set_size") or 1))) if conf_field == "inv_set" else float(r.get(conf_field, 0.0)) * conf_scale
            out.append({"household": hh, "question_id": r["question_id"], "day_index": int(r.get("day_index", r.get("day"))),
                        "conf": conf, "correct": bool(correct), "set_size": r.get("set_size"), "covered": r.get("covered"),
                        "threshold": r.get("conf_threshold")})
    return out


LINES = [
    # name, arm, source pattern (F = followon/<tag>, H = heldout dir), conf field, belief prefix
    ("most frequent", "told", "{F}/bocpd/hh_s*_none.jsonl", "top_prob", None),
    ("most frequent, 24 h half-life", "told", "{F}/bocpd/hh_s*_none_hl24.jsonl", "top_prob", None),
    ("BOCPD detect (not told)", "not told", "{F}/bocpd/hh_s*_detect.jsonl", "top_prob", None),
    ("BOCPD reset (told)", "told", "{F}/bocpd/hh_s*_told.jsonl", "top_prob", None),
    ("most frequent + affected list", "told", "{F}/bocpd/hh_s*_listed.jsonl", "top_prob", None),
    ("conformal most frequent", "told", "{F}/aci/hh_s*_mf_aci.jsonl", "inv_set", None),
    ("Perpetua*", "told", "{H}/classical/hh_s*_{tag}.jsonl", "top_prob", "Perpetua"),
    ("last seen", "told", "{H}/classical/hh_s*_{tag}.jsonl", "top_prob", "LastObservation"),
    ("mixture (told)", "told", "{H}/hyp/logs/hh_s*_longleaf_told.jsonl", "top_prob", None),
    ("mixture (not told)", "not told", "{H}/hyp/logs/hh_s*_longleaf_not_told.jsonl", "top_prob", None),
    ("mixture told + affected reset", "told", "{F}/mixture_reset/hh_s*_told_reset.jsonl", "top_prob", None),
    ("conformal mixture (told)", "told", "{F}/aci/hh_s*_mix_aci.jsonl", "inv_set", None),
]
LINE_COLOR = {"most frequent": "#9ec5f0", "most frequent, 24 h half-life": "#7fc8c0", "BOCPD detect (not told)": "#c9a98a",
              "BOCPD reset (told)": "#f2b48c", "most frequent + affected list": "#e79c9c", "conformal most frequent": "#8fd3b6",
              "Perpetua*": "#e3cf8a", "last seen": "#b8b3ad", "mixture (told)": "#f0a8c8", "mixture (not told)": "#d4a0b8",
              "mixture told + affected reset": "#c9b8f0", "conformal mixture (told)": "#a8b4e0"}


def collect(root: pathlib.Path, tag: str) -> dict:
    """Per-line, per-split, per-group, per-day aggregates for the live chart:
    {line: {arm, households, color, series: {split: {group: {day: {conf, acc, n, set, cov, thr}}}}}}."""
    labels = load_labels(root, tag)
    F, H = f"followon/{tag}", ("heldout" if tag == "p2" else f"heldout_{tag}")
    out = {}
    for name, arm, pat, cf, prefix in LINES:
        rows = rows_for(root, pat.format(F=F, H=H, tag=tag), conf_field=cf, belief_prefix=prefix)
        if not rows:
            continue
        series = {"affected": defaultdict(lambda: defaultdict(list)), "kind": defaultdict(lambda: defaultdict(list))}
        per_hh: Dict[str, dict] = defaultdict(lambda: {"affected": defaultdict(lambda: defaultdict(list)), "kind": defaultdict(lambda: defaultdict(list))})
        for r in rows:
            lab = labels.get((r["household"], r["question_id"]))
            if lab is None:
                continue
            for tgt in (series, per_hh[r["household"]]):
                tgt["affected"]["affected" if lab["affected"] else "unaffected"][r["day_index"]].append(r)
                tgt["kind"][lab["kind"]][r["day_index"]].append(r)
                tgt["affected"]["all"][r["day_index"]].append(r)

        def agg(v):
            d = {"conf": round(sum(x["conf"] for x in v) / len(v), 4), "acc": round(sum(x["correct"] for x in v) / len(v), 4), "n": len(v)}
            if v[0]["set_size"] is not None:
                d["set"] = round(sum(x["set_size"] for x in v) / len(v), 3)
                d["cov"] = round(sum(bool(x["covered"]) for x in v) / len(v), 4)
                d["thr"] = round(sum(float(x["threshold"] or 0) for x in v) / len(v), 4)
            return d
        pack = lambda ser: {sp: {g: {str(d): agg(v) for d, v in sorted(m.items())} for g, m in gm.items()} for sp, gm in ser.items()}
        out[name] = {"arm": arm, "households": len({r["household"] for r in rows}), "color": LINE_COLOR[name],
                     "series": pack(series), "by_household": {hh: pack(ser) for hh, ser in sorted(per_hh.items())}}
    return out


def per_day(rows: List[dict], labels: Dict[Tuple[str, str], dict], key: str) -> Dict[bool, Dict[int, Tuple[float, int]]]:
    acc: Dict[bool, Dict[int, List[float]]] = {True: defaultdict(list), False: defaultdict(list)}
    for r in rows:
        lab = labels.get((r["household"], r["question_id"]))
        if lab is None or r.get(key) is None:
            continue
        acc[lab["affected"]][r["day_index"]].append(float(r[key]))
    return {a: {d: (sum(v) / len(v), len(v)) for d, v in sorted(m.items())} for a, m in acc.items()}


def shade(ax):
    for d in WEEKEND:
        ax.axvspan(d - 0.5, d + 0.5, color="#f2c46d", alpha=0.25, lw=0)


def draw(ax, series: Dict[bool, Dict[int, Tuple[float, int]]], color: str, label: str):
    for affected, style in ((True, "-"), (False, "--")):
        s = series.get(affected, {})
        days = sorted(s)
        ax.plot(days, [s[d][0] for d in days], style, color=color, lw=2, marker="o", ms=4,
                label=f"{label}, {'affected' if affected else 'unaffected'}")


def style(ax, ylabel: str, ylim=(0, 1)):
    shade(ax)
    ax.set_xticks(sorted(DAY_NAMES))
    ax.set_xticklabels([DAY_NAMES[d] for d in sorted(DAY_NAMES)], fontsize=8)
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(axis="y", color="#e5e5e2", lw=0.8)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(labelsize=8)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--tag", default="p2", help="patrol density: p2 (heldout/, followon/p2/) or p8 (heldout_p8/, followon/p8/)")
    a = ap.parse_args(argv)
    root, out = a.root, a.out
    out.mkdir(parents=True, exist_ok=True)
    labels = load_labels(root, a.tag)
    F = f"followon/{a.tag}"
    H = "heldout" if a.tag == "p2" else f"heldout_{a.tag}"
    hours = {"p2": "2 h", "p8": "8 h"}.get(a.tag, a.tag)

    told = [
        ("most frequent", rows_for(root, f"{F}/bocpd/hh_s*_none.jsonl")),
        ("most frequent, 24 h half-life", rows_for(root, f"{F}/bocpd/hh_s*_none_hl24.jsonl")),
        ("BOCPD detect (not told)", rows_for(root, f"{F}/bocpd/hh_s*_detect.jsonl")),
        ("BOCPD reset (told)", rows_for(root, f"{F}/bocpd/hh_s*_told.jsonl")),
        ("most frequent + affected list", rows_for(root, f"{F}/bocpd/hh_s*_listed.jsonl")),
        ("conformal most frequent", rows_for(root, f"{F}/aci/hh_s*_mf_aci.jsonl", conf_field="inv_set")),
        ("Perpetua*", rows_for(root, f"{H}/classical/hh_s*_{a.tag}.jsonl", belief_prefix="Perpetua")),
        ("last seen", rows_for(root, f"{H}/classical/hh_s*_{a.tag}.jsonl", belief_prefix="LastObservation")),
        ("mixture (told)", rows_for(root, f"{H}/hyp/logs/hh_s*_longleaf_told.jsonl")),
        ("mixture told + affected reset", rows_for(root, f"{F}/mixture_reset/hh_s*_told_reset.jsonl")),
    ]
    told = [(n, r) for n, r in told if r]
    # ---- figure 1: small multiples, one column per method
    n = len(told)
    fig, axes = plt.subplots(2, n, figsize=(3.1 * n, 5.6), sharex=True, sharey="row")
    if n == 1:
        axes = axes.reshape(2, 1)
    tables = []
    for j, (name, rows) in enumerate(told):
        hh = len({r["household"] for r in rows})
        conf = per_day(rows, labels, "conf")
        acc = per_day(rows, labels, "correct")
        draw(axes[0, j], conf, PALETTE[name], name)
        draw(axes[1, j], acc, PALETTE[name], name)
        axes[0, j].set_title(f"{name}\n({hh} households)", fontsize=9)
        tables.append((name, hh, conf, acc))
    style(axes[0, 0], "confidence per day")
    style(axes[1, 0], "accuracy per day")
    for j in range(1, n):
        style(axes[0, j], "")
        style(axes[1, j], "")
    axes[0, 0].plot([], [], "-", color="#52514e", label="affected")
    axes[0, 0].plot([], [], "--", color="#52514e", label="unaffected")
    handles, labs = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles[-2:], labs[-2:], loc="upper right", fontsize=8, frameon=False, ncol=2)
    fig.suptitle(f"Told arm, held-out households, patrol every {hours}: confidence and accuracy per day, affected (solid) vs unaffected (dashed); weekend shaded",
                 fontsize=10, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out / "fig1_affected_split.png", dpi=150)
    plt.close(fig)

    # ---- figure 2: not-told, BOCPD detect vs mixture not told
    nottold = [("BOCPD detect (not told)", rows_for(root, f"{F}/bocpd/hh_s*_detect.jsonl")),
               ("mixture (not told)", rows_for(root, f"{H}/hyp/logs/hh_s*_longleaf_not_told.jsonl"))]
    nottold = [(n_, r) for n_, r in nottold if r]
    fig, axes = plt.subplots(1, 2, figsize=(7, 3), sharex=True)
    for name, rows in nottold:
        draw(axes[0], per_day(rows, labels, "conf"), PALETTE[name], name)
        draw(axes[1], per_day(rows, labels, "correct"), PALETTE[name], name)
    style(axes[0], "confidence")
    style(axes[1], "accuracy")
    axes[0].legend(fontsize=7, frameon=False)
    fig.suptitle(f"Not-told arm, patrol every {hours}: detection (BOCPD) vs interpretation (mixture)", fontsize=10, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(out / "fig2_not_told.png", dpi=150)
    plt.close(fig)

    # ---- figure 3: conformal set size and coverage
    aci_rows = rows_for(root, f"{F}/aci/hh_s*_mf_aci.jsonl", conf_field="inv_set")
    fig, axes = plt.subplots(1, 2, figsize=(7, 3), sharex=True)
    draw(axes[0], per_day(aci_rows, labels, "set_size"), PALETTE["conformal most frequent"], "set size")
    draw(axes[1], per_day(aci_rows, labels, "covered"), PALETTE["conformal most frequent"], "coverage")
    style(axes[0], "prediction-set size (spots)", ylim=(0, 20))
    style(axes[1], "empirical coverage", ylim=(0.6, 1.0))
    axes[1].axhline(0.9, color="#52514e", lw=1, ls=":")
    fig.suptitle(f"Conformal wrapper on most frequent, patrol every {hours} (target 0.9): set size and coverage per day", fontsize=10, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(out / "fig3_conformal.png", dpi=150)
    plt.close(fig)

    # ---- figure 4: every kind of question, for the lines where the split matters
    def per_day_kind(rows, key):
        acc = {k: defaultdict(list) for k in KINDS}
        for r in rows:
            lab = labels.get((r["household"], r["question_id"]))
            if lab is None or r.get(key) is None:
                continue
            acc[lab["kind"]][r["day_index"]].append(float(r[key]))
        return {k: {d: (sum(v) / len(v), len(v)) for d, v in sorted(m.items()) if len(v) >= 8} for k, m in acc.items()}

    kind_lines = [(n_, r) for n_, r in told if n_ in ("most frequent", "most frequent, 24 h half-life", "BOCPD reset (told)",
                                                      "most frequent + affected list", "last seen", "mixture (told)")]
    nk = len(kind_lines)
    fig, axes = plt.subplots(2, nk, figsize=(3.1 * nk, 5.8), sharex=True, sharey="row")
    if nk == 1:
        axes = axes.reshape(2, 1)
    kind_tables = []
    for j, (name, rows) in enumerate(kind_lines):
        conf, acc = per_day_kind(rows, "conf"), per_day_kind(rows, "correct")
        for k in KINDS:
            for row_i, series in ((0, conf[k]), (1, acc[k])):
                days = sorted(series)
                axes[row_i, j].plot(days, [series[d][0] for d in days], "-", color=KIND_COLOR[k], lw=2 if k != "plain" else 1.4,
                                    marker="o", ms=3.5, label=k.replace("_", " "), alpha=0.95)
        axes[0, j].set_title(f"{name}\n({len({r['household'] for r in rows})} households)", fontsize=9)
        kind_tables.append((name, conf, acc))
    style(axes[0, 0], "confidence per day")
    style(axes[1, 0], "accuracy per day")
    for j in range(1, nk):
        style(axes[0, j], "")
        style(axes[1, j], "")
    handles, labs = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles[:len(KINDS)], labs[:len(KINDS)], loc="upper right", fontsize=8, frameon=False, ncol=6)
    fig.suptitle(f"Told arm, patrol every {hours}: every kind of question (points with fewer than 8 questions that day are left out)",
                 fontsize=10, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out / "fig4_kinds.png", dpi=150)
    plt.close(fig)

    # ---- tables
    md = [f"# Per-day numbers behind the figures (patrol every {hours})", ""]
    for name, conf, acc in kind_tables:
        md += [f"## {name}, by kind of question", "", "| kind | " + " | ".join(f"{DAY_NAMES[d]}" for d in sorted(DAY_NAMES)) + " |", "|---|" + "---|" * 7]
        for k in KINDS:
            md.append(f"| {k}: confidence | " + " | ".join(f"{conf[k][d][0]:.2f}" if d in conf[k] else "-" for d in sorted(DAY_NAMES)) + " |")
            md.append(f"| {k}: accuracy (n) | " + " | ".join(f"{100 * acc[k][d][0]:.0f}% ({acc[k][d][1]})" if d in acc[k] else "-" for d in sorted(DAY_NAMES)) + " |")
        md.append("")
    for name, hh, conf, acc in tables:
        md += [f"## {name} ({hh} households)", "", "| | " + " | ".join(f"{DAY_NAMES[d]}" for d in sorted(DAY_NAMES)) + " |", "|---|" + "---|" * 7]
        for affected in (True, False):
            tag = "affected" if affected else "unaffected"
            md.append(f"| confidence, {tag} | " + " | ".join(f"{conf[affected][d][0]:.2f}" if d in conf[affected] else "-" for d in sorted(DAY_NAMES)) + " |")
            md.append(f"| accuracy, {tag} | " + " | ".join(f"{100 * acc[affected][d][0]:.0f}%" if d in acc[affected] else "-" for d in sorted(DAY_NAMES)) + " |")
            md.append(f"| n, {tag} | " + " | ".join(f"{acc[affected][d][1]}" if d in acc[affected] else "-" for d in sorted(DAY_NAMES)) + " |")
        md.append("")
    (out / "tables.md").write_text("\n".join(md))
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    main()
