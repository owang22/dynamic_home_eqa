#!/usr/bin/env python3
"""
make_summary_figures.py — Regenerate summary/dataset.png from results.

No difficulty bins — shows staleness (Δ) distribution and dataset composition.

Usage:
  python -m dynamic_home_eqa.scripts.make_summary_figures
  python -m dynamic_home_eqa.scripts.make_summary_figures --results results_subset/ --out summary/dataset.png
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import sys

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

FONT_TITLE   = dict(fontsize=15, fontweight="bold")
FONT_AXIS    = dict(fontsize=13, fontweight="bold")
FONT_TICK    = dict(labelsize=11)
FONT_ANNOT   = dict(fontsize=10, fontweight="bold")
BAR_COLOR    = "#4878CF"
BAR2_COLOR   = "#6ACC65"
ACCENT_COLOR = "#D65F5F"
GRID_KW      = dict(color="#cccccc", linewidth=0.7, zorder=0)

LABEL_BBOX = dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.85)


def label(ax, x, y, text, **kw):
    kw.setdefault("ha", "center")
    kw.setdefault("va", "bottom")
    kw.setdefault("fontsize", FONT_ANNOT["fontsize"])
    kw.setdefault("fontweight", FONT_ANNOT["fontweight"])
    ax.text(x, y, text, bbox=LABEL_BBOX, **kw)


def load_all(results_dir: pathlib.Path) -> tuple[list[dict], list[dict], list[dict]]:
    questions, changes, manifests = [], [], []
    for qp in sorted(results_dir.glob("*/questions.json")):
        mp = qp.parent / "manifest.json"
        if not mp.exists():
            continue
        d = json.loads(qp.read_text())
        questions.extend(d["questions"])
        m = json.loads(mp.read_text())
        changes.extend(m["changes"])
        manifests.append(m)
    return questions, changes, manifests


def panel_staleness(ax, questions):
    elapsed = [q["metadata"]["elapsed"] for q in questions]
    bins = np.arange(0, max(elapsed) + 0.5, 0.5)
    counts, edges = np.histogram(elapsed, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    ax.bar(centers, counts, width=0.45, color=BAR_COLOR, edgecolor="white", linewidth=0.5, zorder=3)
    ax.yaxis.grid(True, **GRID_KW)
    ax.set_xlabel("Staleness Δ (hours)", **FONT_AXIS)
    ax.set_ylabel("Questions", **FONT_AXIS)
    ax.set_title("Staleness distribution", **FONT_TITLE)
    ax.tick_params(labelsize=FONT_TICK["labelsize"])
    ax.set_xlim(-0.3, max(elapsed) + 0.4)
    mu = np.mean(elapsed)
    ymax = ax.get_ylim()[1]
    ax.axvline(mu, color=ACCENT_COLOR, linewidth=1.8, linestyle="--", zorder=4)
    label(ax, mu + 0.15, ymax * 0.88, f"mean {mu:.1f}h",
          ha="left", color=ACCENT_COLOR)
    ax.set_facecolor("#f9f9f9")


def panel_object_categories(ax, changes):
    cat_counts = collections.Counter(c["object_category"] for c in changes)
    cats   = sorted(cat_counts, key=lambda k: cat_counts[k])
    counts = [cat_counts[c] for c in cats]
    y = np.arange(len(cats))
    bars = ax.barh(y, counts, color=BAR2_COLOR, edgecolor="white", linewidth=0.5, zorder=3)
    ax.xaxis.grid(True, **GRID_KW)
    ax.set_yticks(y)
    ax.set_yticklabels(cats, fontsize=FONT_TICK["labelsize"])
    ax.tick_params(axis="x", labelsize=FONT_TICK["labelsize"])
    ax.set_xlabel("Change events", **FONT_AXIS)
    ax.set_title("Events by object category", **FONT_TITLE)
    for bar, cnt in zip(bars, counts):
        ax.text(cnt + max(counts) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(cnt), va="center", **FONT_ANNOT, bbox=LABEL_BBOX)
    ax.set_xlim(0, max(counts) * 1.18)
    ax.set_facecolor("#f9f9f9")


def panel_change_types(ax, changes):
    ct = collections.Counter(c["change_type"] for c in changes)
    labels_order = ["insert_new", "move_existing"]
    counts = [ct.get(k, 0) for k in labels_order]
    colors = [BAR_COLOR, BAR2_COLOR]
    bars = ax.bar(labels_order, counts, color=colors, edgecolor="white", linewidth=0.5, zorder=3)
    ax.yaxis.grid(True, **GRID_KW)
    ax.set_title("Change types", **FONT_TITLE)
    ax.set_ylabel("Events", **FONT_AXIS)
    ax.tick_params(labelsize=FONT_TICK["labelsize"])
    total = sum(counts)
    for bar, cnt in zip(bars, counts):
        label(ax, bar.get_x() + bar.get_width() / 2,
              bar.get_height() + total * 0.01,
              f"{cnt}\n({cnt/total:.0%})")
    ax.set_ylim(0, max(counts) * 1.25)
    ax.set_facecolor("#f9f9f9")


def panel_profiles(ax, manifests):
    prof   = collections.Counter(m["resident_profile"] for m in manifests)
    labels = sorted(prof)
    short  = [l.replace("_", "\n") for l in labels]
    counts = [prof[l] for l in labels]
    colors = [BAR_COLOR, ACCENT_COLOR]
    bars   = ax.bar(short, counts, color=colors, edgecolor="white", linewidth=0.5, zorder=3)
    ax.yaxis.grid(True, **GRID_KW)
    ax.set_title("Resident profiles", **FONT_TITLE)
    ax.set_ylabel("Scenes", **FONT_AXIS)
    ax.tick_params(labelsize=FONT_TICK["labelsize"])
    total = sum(counts)
    for bar, cnt in zip(bars, counts):
        label(ax, bar.get_x() + bar.get_width() / 2,
              bar.get_height() + total * 0.01,
              f"{cnt} ({cnt/total:.0%})")
    ax.set_ylim(0, max(counts) * 1.25)
    ax.set_facecolor("#f9f9f9")


def panel_questions_per_scene(ax, questions, manifests):
    per_scene = collections.defaultdict(int)
    for q in questions:
        hid = q["metadata"]["household_id"]
        per_scene[hid] += 1
    counts = list(per_scene.values())
    bins = np.arange(min(counts), max(counts) + 5, 5)
    ax.hist(counts, bins=bins, color=BAR_COLOR, edgecolor="white", linewidth=0.5, zorder=3)
    ax.yaxis.grid(True, **GRID_KW)
    ax.set_xlabel("Questions per scene", **FONT_AXIS)
    ax.set_ylabel("Scenes", **FONT_AXIS)
    ax.set_title("Questions per scene", **FONT_TITLE)
    ax.tick_params(labelsize=FONT_TICK["labelsize"])
    mu = np.mean(counts)
    ax.axvline(mu, color=ACCENT_COLOR, linewidth=1.8, linestyle="--", zorder=4)
    ymax = ax.get_ylim()[1]
    label(ax, mu + 0.5, ymax * 0.88, f"mean {mu:.1f}",
          ha="left", color=ACCENT_COLOR)
    ax.set_facecolor("#f9f9f9")


def panel_obs_time(ax, questions):
    ot_bins = collections.Counter(math.floor(q["metadata"]["observed_at"])
                                   for q in questions)
    hours  = sorted(ot_bins)
    counts = [ot_bins[h] for h in hours]
    ax.bar(hours, counts, width=0.8, color=BAR2_COLOR, edgecolor="white", linewidth=0.5, zorder=3)
    ax.yaxis.grid(True, **GRID_KW)
    ax.set_xlabel("Hour of day (observed_at)", **FONT_AXIS)
    ax.set_ylabel("Questions", **FONT_AXIS)
    ax.set_title("Observation time distribution", **FONT_TITLE)
    ax.tick_params(labelsize=FONT_TICK["labelsize"])
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.set_facecolor("#f9f9f9")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results_subset",
                    help="Source results dir (default: results_subset/)")
    ap.add_argument("--out", default="summary/dataset.png",
                    help="Output PNG path (default: summary/dataset.png)")
    args = ap.parse_args()

    results_dir = pathlib.Path(args.results)
    out_path    = pathlib.Path(args.out)
    if not results_dir.is_absolute():
        results_dir = (_DYNAMIC_EQA / results_dir).resolve()
    if not out_path.is_absolute():
        out_path = (_DYNAMIC_EQA / out_path).resolve()

    print(f"Loading data from {results_dir} …")
    questions, changes, manifests = load_all(results_dir)
    print(f"  {len(questions)} questions, {len(changes)} change events, {len(manifests)} scenes")

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.patch.set_facecolor("white")
    plt.subplots_adjust(hspace=0.45, wspace=0.35, left=0.07, right=0.97,
                        top=0.93, bottom=0.09)

    fig.suptitle(
        f"Dynamic EQA dataset  ·  {len(manifests)} scenes  ·  {len(questions):,} questions",
        fontsize=17, fontweight="bold", y=0.98,
    )

    panel_staleness(          axes[0, 0], questions)
    panel_object_categories(  axes[0, 1], changes)
    panel_change_types(       axes[0, 2], changes)
    panel_profiles(           axes[1, 0], manifests)
    panel_questions_per_scene(axes[1, 1], questions, manifests)
    panel_obs_time(           axes[1, 2], questions)

    for ax in axes.flat:
        ax.set_ylim(bottom=0)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
