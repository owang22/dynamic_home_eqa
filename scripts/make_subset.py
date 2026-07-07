#!/usr/bin/env python3
"""
make_subset.py — Sample a smaller prototype question set from results/.

Writes results_subset/ with manifest.json + questions.json per scene.
Stratifies within each scene across staleness bins so the subset has
natural variation, not just the easiest questions.

Usage:
  python scripts/make_subset.py --n 1000 --seed 7
  python scripts/make_subset.py --n 1000 --out results_subset/
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import shutil

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()


def _staleness_bin(elapsed: float) -> str:
    if elapsed < 1.0:
        return "low"
    elif elapsed < 3.0:
        return "mid"
    else:
        return "high"


def sample_subset(
    results_dir: pathlib.Path,
    out_dir: pathlib.Path,
    n: int,
    seed: int,
) -> None:
    rng = random.Random(seed)

    scene_paths = sorted(results_dir.glob("*/questions.json"))
    if not scene_paths:
        raise RuntimeError(f"No questions.json found under {results_dir}")

    scenes: list[tuple[pathlib.Path, dict, dict]] = []
    for qp in scene_paths:
        mp = qp.parent / "manifest.json"
        if not mp.exists():
            continue
        manifest  = json.loads(mp.read_text())
        questions = json.loads(qp.read_text())
        scenes.append((qp.parent, manifest, questions))

    n_scenes      = len(scenes)
    base_per_scene = n // n_scenes
    remainder      = n - base_per_scene * n_scenes

    quotas = [base_per_scene] * n_scenes
    for i in rng.sample(range(n_scenes), remainder):
        quotas[i] += 1

    out_dir.mkdir(parents=True, exist_ok=True)
    total_written = 0

    for (scene_dir, manifest, questions_data), quota in zip(scenes, quotas):
        qs = questions_data["questions"]

        by_bin: dict[str, list[dict]] = {}
        for q in qs:
            b = _staleness_bin(q["metadata"]["elapsed"])
            by_bin.setdefault(b, []).append(q)

        selected: list[dict] = []
        bins = list(by_bin.keys())
        for b in bins:
            rng.shuffle(by_bin[b])

        bin_iters = {b: iter(by_bin[b]) for b in bins}
        rng.shuffle(bins)
        while len(selected) < quota:
            progress = False
            for b in bins:
                if len(selected) >= quota:
                    break
                try:
                    selected.append(next(bin_iters[b]))
                    progress = True
                except StopIteration:
                    pass
            if not progress:
                break

        if not selected:
            continue

        folder = out_dir / scene_dir.name
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copy(scene_dir / "manifest.json", folder / "manifest.json")

        by_diff: dict[str, int] = {}
        for q in selected:
            d = q["metadata"].get("difficulty_bin", "?")
            by_diff[d] = by_diff.get(d, 0) + 1

        subset_data = {
            "total":         len(selected),
            "by_difficulty": by_diff,
            "questions":     selected,
        }
        (folder / "questions.json").write_text(json.dumps(subset_data, indent=2))
        total_written += len(selected)

    print(f"Wrote {total_written} questions across {n_scenes} scenes → {out_dir}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n",    type=int, default=1000, help="Target question count")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--results", default="results",
                    help="Source results dir (default: results/)")
    ap.add_argument("--out", default="results_subset",
                    help="Output dir (default: results_subset/)")
    args = ap.parse_args()

    results_dir = pathlib.Path(args.results)
    out_dir     = pathlib.Path(args.out)
    if not results_dir.is_absolute():
        results_dir = (_DYNAMIC_EQA / results_dir).resolve()
    if not out_dir.is_absolute():
        out_dir = (_DYNAMIC_EQA / out_dir).resolve()

    sample_subset(results_dir, out_dir, args.n, args.seed)


if __name__ == "__main__":
    main()
