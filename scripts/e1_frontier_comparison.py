#!/usr/bin/env python3
"""
e1_frontier_comparison.py — E1's paired frontier plot + rank-change table.

Reads the real_geodesic arm (embodied_results/m3_result.json's location
rows — EmbodiedWorld's own AgentConfig() default, i.e. cost_model=
"real_geodesic") and the flat arm (embodied_results/e1_flat_<tag>_result.
json, written by scripts/e1_cost_heterogeneity.py — <tag> is "default"
unless that script's own --latency-weight override was used), builds the
same clustered headline_table scripts/e2_headline_comparison.py uses
(accuracy, per-scene-day bootstrap CI), then reports:

  1. A paired frontier plot (accuracy vs. mean travel distance): one point
     per policy per cost model, connected by a line so a rank flip is
     visually a crossing line, not just a table row.
  2. A rank-change table: policies ranked by accuracy (ties broken by
     lower travel) under each cost model, with each policy's rank under
     both and the delta — the direct test of E1's claim ("distance-
     dependent cost changes policy rankings").

REHEARSAL: one scene — every bootstrap CI here is degenerate
(n_clusters=1, "no CI possible"), same caveat as E2's own rehearsal.

Does not require habitat_sim — reads only existing result files.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.scripts.e2_headline_comparison import headline_table  # noqa: E402

_REHEARSAL_TAG = "REHEARSAL"


def _location_rows(result_path: pathlib.Path) -> list[dict]:
    result = json.loads(result_path.read_text())
    return [r for r in result["rows"] if r["question_type"] == "location"]


def _policy_summary(headline: list[dict]) -> dict[str, dict]:
    """Collapse headline_table's (policy, hazard_class, question_type)
    rows to one row per policy — equal-weight mean across hazard classes,
    matching e2_headline_comparison.write_frontier_plots' own single-
    glance convention (the per-hazard numbers stay in the CSV, not lost)."""
    by_policy: dict[str, list[dict]] = {}
    for r in headline:
        by_policy.setdefault(r["policy"], []).append(r)
    out = {}
    for policy, rows in by_policy.items():
        out[policy] = {
            "accuracy": sum(r["accuracy"].point for r in rows) / len(rows),
            "travel_m": sum(r["travel_m"].point for r in rows) / len(rows),
            "n_clusters": max(r["accuracy"].n_clusters for r in rows),
        }
    return out


def rank_change_table(real_summary: dict[str, dict], flat_summary: dict[str, dict]) -> list[dict]:
    """Rank policies by accuracy (ties broken by lower travel_m, i.e. the
    frontier-preferred direction) under each cost model, then report the
    rank delta. rank=1 is best. Only policies present under both arms are
    ranked (a policy missing from one arm can't have a meaningful delta)."""
    policies = sorted(set(real_summary) & set(flat_summary))

    def _ranked(summary: dict[str, dict]) -> dict[str, int]:
        ordered = sorted(policies, key=lambda p: (-summary[p]["accuracy"], summary[p]["travel_m"]))
        return {p: i + 1 for i, p in enumerate(ordered)}

    real_rank = _ranked(real_summary)
    flat_rank = _ranked(flat_summary)

    out = []
    for p in policies:
        out.append({
            "policy": p,
            "real_geodesic_rank": real_rank[p],
            "flat_rank": flat_rank[p],
            "rank_delta": flat_rank[p] - real_rank[p],
            "real_geodesic_accuracy": real_summary[p]["accuracy"],
            "flat_accuracy": flat_summary[p]["accuracy"],
        })
    out.sort(key=lambda r: r["real_geodesic_rank"])
    return out


def write_paired_frontier_plot(real_summary: dict[str, dict], flat_summary: dict[str, dict], out_path: pathlib.Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    policies = sorted(set(real_summary) & set(flat_summary))
    fig, ax = plt.subplots(figsize=(7, 5))
    for policy in policies:
        rx, ry = real_summary[policy]["travel_m"], real_summary[policy]["accuracy"]
        fx, fy = flat_summary[policy]["travel_m"], flat_summary[policy]["accuracy"]
        ax.plot([rx, fx], [ry, fy], color="gray", alpha=0.5, linewidth=1, zorder=1)
        ax.scatter([rx], [ry], marker="o", s=70, label=f"{policy} (real_geodesic)", zorder=2)
        ax.scatter([fx], [fy], marker="^", s=70, label=f"{policy} (flat)", zorder=2)
    ax.set_xlabel("mean travel distance (m)")
    ax.set_ylabel("accuracy")
    ax.set_title(f"E1 accuracy vs. travel — real_geodesic vs. flat cost model ({_REHEARSAL_TAG})")
    ax.legend(fontsize=6, loc="best", ncol=2)
    ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--real-geodesic-result", default=str(_DYNAMIC_EQA / "embodied_results" / "m3_result.json"))
    ap.add_argument("--flat-result", default=str(_DYNAMIC_EQA / "embodied_results" / "e1_flat_default_result.json"))
    ap.add_argument("--out-dir", default=str(_DYNAMIC_EQA / "e1e4_results"))
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    real_rows = _location_rows(pathlib.Path(args.real_geodesic_result))
    flat_rows = _location_rows(pathlib.Path(args.flat_result))

    real_summary = _policy_summary(headline_table(real_rows))
    flat_summary = _policy_summary(headline_table(flat_rows))

    table = rank_change_table(real_summary, flat_summary)
    print(f"\n{'policy':<26}{'real_rank':>10}{'flat_rank':>10}{'delta':>8}{'real_acc':>10}{'flat_acc':>10}")
    for r in table:
        print(f"{r['policy']:<26}{r['real_geodesic_rank']:>10}{r['flat_rank']:>10}{r['rank_delta']:>+8}"
              f"{r['real_geodesic_accuracy']:>10.3f}{r['flat_accuracy']:>10.3f}")

    csv_path = out_dir / f"e1_rank_change_{_REHEARSAL_TAG}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0].keys()) if table else [])
        writer.writeheader()
        for row in table:
            writer.writerow(row)
    print(f"\nWrote {csv_path}")

    plot_path = out_dir / f"e1_paired_frontier_{_REHEARSAL_TAG}.png"
    write_paired_frontier_plot(real_summary, flat_summary, plot_path)
    print(f"Wrote {plot_path}")

    any_flip = any(r["rank_delta"] != 0 for r in table)
    n_clusters = next(iter(real_summary.values()))["n_clusters"] if real_summary else 0
    print(f"\nn_clusters={n_clusters} (REHEARSAL — one scene; a real finding needs the multi-scene pool).")
    if any_flip:
        print("Rank changes observed between cost models — see the table above for which policies moved.")
    else:
        print("No rank changes observed on this single scene — not evidence of no effect, given "
              "n_clusters=1 above.")


if __name__ == "__main__":
    main()
