#!/usr/bin/env python3
"""Aggregate bake-off leaderboards across realizations (seeds).

A single seed's ranking is not a result: the per-model spread across
seeds measured on the 20-household set (up to 0.034 accuracy) is as
large as the spread BETWEEN models within one seed (0.030), so which
belief "wins" changes with the seed. This reads the per-seed
leaderboards and reports, per model, the mean over realizations with
the seed range as the error bar — the honest headline.

Usage:
  python -m baselines.multiseed_report --seeds 0 1 2 3 4
"""
from __future__ import annotations

import argparse
import pathlib
import re
import statistics


def headline_cell(path: pathlib.Path) -> dict:
    """model -> (accuracy, log-loss) from the headline D=7,h=1 table."""
    text = path.read_text()
    if "## Headline cell" not in text:
        raise ValueError(f"{path}: no headline cell section")
    section = text.split("## Headline cell")[1].split("\n## ")[0]
    out = {}
    for line in section.splitlines():
        if not line.startswith("| ") or "[" not in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        acc = re.match(r"([\d.]+)", cells[1])
        loss = re.match(r"([\d.]+)", cells[3]) if len(cells) > 3 else None
        if acc:
            out[cells[0]] = (float(acc.group(1)),
                             float(loss.group(1)) if loss else None)
    return out


def report_dir(seed: int, root: pathlib.Path) -> pathlib.Path:
    return root / ("bakeoff" if seed == 0 else f"bakeoff_seed{seed}")


def render(seeds: list, root: pathlib.Path) -> str:
    runs = {s: headline_cell(report_dir(s, root) / "leaderboard.md")
            for s in seeds}
    models = sorted(runs[seeds[0]],
                    key=lambda m: -statistics.mean(
                        runs[s][m][0] for s in seeds if m in runs[s]))
    lines = [
        f"# Bake-off across {len(seeds)} realizations (seeds "
        f"{', '.join(map(str, seeds))})",
        "",
        "Headline cell D=7,h=1. Each seed re-runs the SAME households "
        "through the seeded simulator: same personas, stories and object "
        "rules, different jitter and misplacement draws. Accuracy is the "
        "mean over realizations; +/- is half the seed range, so it is the "
        "spread a single-seed number hides, not a bootstrap interval.",
        "",
        "| model | accuracy (mean +/- half-range) | per-seed | mean "
        "log-loss |",
        "|---|---|---|---|",
    ]
    for m in models:
        acc = [runs[s][m][0] for s in seeds if m in runs[s]]
        loss = [runs[s][m][1] for s in seeds
                if m in runs[s] and runs[s][m][1] is not None]
        half = (max(acc) - min(acc)) / 2
        per = " / ".join(f"{a:.3f}" for a in acc)
        lines.append(f"| {m} | {statistics.mean(acc):.3f} +/- {half:.3f} "
                     f"| {per} | "
                     f"{statistics.mean(loss):.3f} |" if loss else
                     f"| {m} | {statistics.mean(acc):.3f} +/- {half:.3f} "
                     f"| {per} | - |")
    best = {s: max(runs[s], key=lambda m: runs[s][m][0]) for s in seeds}
    lines += ["", "## Which model wins, per seed", ""]
    for s in seeds:
        lines.append(f"- seed {s}: {best[s]} ({runs[s][best[s]][0]:.3f})")
    distinct = len(set(best.values()))
    spread_within = max(
        max(runs[s][m][0] for m in runs[s]) - min(runs[s][m][0]
                                                  for m in runs[s])
        for s in seeds)
    spread_across = max(
        max(runs[s][m][0] for s in seeds if m in runs[s])
        - min(runs[s][m][0] for s in seeds if m in runs[s])
        for m in models)
    lines += [
        "",
        f"{distinct} distinct winners across {len(seeds)} seeds. "
        f"Model spread within a seed: {spread_within:.3f}. Seed spread "
        f"within a model (max): {spread_across:.3f}.",
        "",
        "A ranking claim is only safe when the gap between two models "
        "exceeds the seed spread above.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seeds", type=int, nargs="+",
                    default=[0, 1, 2, 3, 4])
    ap.add_argument("--reports-root", type=pathlib.Path,
                    default=pathlib.Path("reports/baselines"))
    ap.add_argument("--out", type=pathlib.Path, default=None)
    args = ap.parse_args()
    text = render(args.seeds, args.reports_root)
    out = args.out or (args.reports_root / "bakeoff_multiseed.md")
    out.write_text(text)
    print(text)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
