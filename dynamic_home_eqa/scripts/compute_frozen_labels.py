#!/usr/bin/env python3
"""
compute_frozen_labels.py — recompute FROZEN_LABELS under the navmesh-
connectivity phase's sampling rule (embodied/sampling.py): a label must
exist at patrol_start AND have every historical anchor slot reachable from
the agent's start pose.

Run once to produce the new literal tuple for experiment_config.py — not
imported at experiment time (see experiment_config.py's own module
docstring on why FROZEN_LABELS is a literal, not a live computation).

compute_qualifying_labels() below is the reusable core of this: parameterized
by scene/eval_folder/train_folders/patrol_start rather than hardcoded to
102343992, so scripts/expand_scene_pool.py (and any future scene) can call
the exact same rule without a copy-pasted reimplementation. main() here is
unchanged — it still only prints 102343992's numbers, via FROZEN's values;
it does not write experiment_config.py, so FROZEN_LABELS stays a hand-frozen
literal exactly as its own docstring requires.

Requires habitat_sim — run from a conda env that has it (e.g. explore-eqa).
"""
from __future__ import annotations

import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.sampling import LabelQualification, qualify_labels


def compute_qualifying_labels(
    scene: str,
    eval_folder: str,
    train_folders: tuple[str, ...],
    patrol_start: float,
    out_dir: pathlib.Path,
) -> list[LabelQualification]:
    """Load one scene's eval + train manifests from out_dir and run
    embodied.sampling.qualify_labels() over them — the same two-property
    rule (exists at patrol_start, every historical anchor slot reachable)
    FROZEN_LABELS was computed from for 102343992, generalized to take the
    scene identity as parameters instead of importing experiment_config.FROZEN
    directly, so it works for any scene with a train+eval day split on disk."""
    eval_result = json.loads((out_dir / eval_folder / "generation_result.json").read_text())
    eval_manifest = json.loads((out_dir / eval_folder / "manifest.json").read_text())
    history_manifests = [eval_manifest] + [
        json.loads((out_dir / folder / "manifest.json").read_text())
        for folder in train_folders
    ]

    return qualify_labels(
        scene=scene,
        eval_result=eval_result,
        eval_manifest=eval_manifest,
        history_manifests=history_manifests,
        patrol_start=patrol_start,
    )


def main() -> None:
    out_dir = _DYNAMIC_EQA / "generation_out"

    results = compute_qualifying_labels(
        scene=FROZEN.scene,
        eval_folder=FROZEN.eval_folder,
        train_folders=FROZEN.train_folders,
        patrol_start=FROZEN.patrol_start,
        out_dir=out_dir,
    )

    print(f"{'label':<12} {'qualifies':<10} reason")
    for r in results:
        print(f"{r.label:<12} {str(r.qualifies):<10} {r.reason()}")

    qualifying = tuple(sorted(r.label for r in results if r.qualifies))
    print(f"\n{len(qualifying)}/{len(results)} labels qualify:")
    print(qualifying)


if __name__ == "__main__":
    main()
