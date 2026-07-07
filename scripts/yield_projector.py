#!/usr/bin/env python3
"""
yield_projector.py — M4 pre-suite: projects per-stratum (hazard_class x
question_type) scored-answer totals for E1-E4 as scene-pool scenes land.

Raw count = qualified labels in that stratum x eval days x
questions-per-label (len(FROZEN_WAIT_HOURS_SWEEP)) x n_policies — the exact
trial-count formula scripts/embodied_m3_gate.py's rerun_frozen_e0/
rerun_frozen_state_e0 loops already realize per scene, summed here across
every scene the pool has qualified so far (plus the frozen scene's own
already-locked-in contribution) without re-running any of them.

Effective-N (Suite Buildout phase B3): raw count is NOT the right
denominator for the >=100-per-stratum bar, because questions within a
scene-day are not independent (same house, same routine, same fitted
decay rates) — multiplying by more eval days from the SAME scene, or by
more waits/policies (deterministic re-derivations of the same underlying
question), inflates the raw count without adding independent information.
This script reports n_clusters (the count of distinct qualifying scenes
contributing to that stratum) alongside raw_N as an explicit, conservative
floor on effective sample size — the honest lower bound, not a fabricated
design-effect-adjusted point estimate (that would require an intra-cluster
correlation this codebase has no data to estimate). The >=100 bar is
assessed against n_clusters, not raw_N: closing a state-stratum shortfall
therefore means more qualified SCENES, not more days per existing scene
(see this phase's own note on why days-per-scene is the wrong lever).

hazard_class is data-dependent (embodied.policy.classify_hazard: a
category's fitted decay rate vs. the MEDIAN rate across all fitted
categories in that scene's own train days) — computed per scene from real
train-day statistics here, not assumed 50/50, so the projection reflects
each scene's actual hazard-rate distribution, not a guess.

Contamination guard (Suite Buildout phase A): every scene's consumed
folders are validated (scripts.scene_validation.validate_folder) before
being counted — a scene with any failing folder is excluded from the
tally entirely (reported, not silently dropped), so a stale/corrupted
day like the pre-fix 102344022/102344049 day0 folders can never again
silently inflate a projection the way it did before this phase.

Pure Python — no habitat_sim needed (qualified_labels is read from
scripts/expand_scene_pool.py's checkpoint, already computed there; this
script only needs each label's category + train-day dwell/flip stats to
classify hazard, plus trace_validate on each consumed folder). Safe to run
repeatedly / mid-pool-generation — read-only, never writes the checkpoint.

Usage:
    python3 scripts/yield_projector.py
    python3 scripts/yield_projector.py --eval-days 2   # project a 2-eval-day suite
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass, field

_DYNAMIC_EQA = pathlib.Path(__file__).parent.parent.resolve()
_REPO_ROOT = _DYNAMIC_EQA.parent
sys.path.insert(0, str(_REPO_ROOT))

from dynamic_home_eqa.embodied.attribution import aggregate_flip_stats
from dynamic_home_eqa.embodied.belief import aggregate_category_stats, fit_decay_models
from dynamic_home_eqa.embodied.experiment_config import FROZEN
from dynamic_home_eqa.embodied.policy import classify_hazard
from dynamic_home_eqa.generation.exports import category_location_change_stats, category_state_flip_stats
from dynamic_home_eqa.scripts.expand_scene_pool import ScenePoolEntry, load_state, _folder_names  # noqa: E402
from dynamic_home_eqa.scripts.scene_validation import validate_folder

_STATE_BAR = 100
# M3's current gate policy roster (scripts/embodied_m3_gate.py): 7 shared
# policies + tod_prior (location only, no state-axis variant yet).
_N_POLICIES_LOCATION = 8
_N_POLICIES_STATE = 7
_N_WAIT_HOURS = len(FROZEN.wait_hours_sweep)


@dataclass
class StratumTally:
    location_stable:   int = 0
    location_volatile: int = 0
    state_stable:       int = 0
    state_volatile:     int = 0
    # n_clusters (Suite Buildout phase B3): distinct qualifying scenes
    # contributing to each stratum — the effective-N floor, tracked
    # separately from the raw label counts above.
    location_stable_scenes:   set = field(default_factory=set)
    location_volatile_scenes: set = field(default_factory=set)
    state_stable_scenes:       set = field(default_factory=set)
    state_volatile_scenes:     set = field(default_factory=set)

    def add(self, question_type: str, hazard: str, n_labels: int, scene_id: str) -> None:
        attr = f"{question_type}_{hazard}"
        setattr(self, attr, getattr(self, attr) + n_labels)
        if n_labels > 0:
            getattr(self, f"{attr}_scenes").add(scene_id)


def _label_categories(manifests: list[dict]) -> dict[str, str]:
    """{label: category} from every changes-list entry across manifests —
    a label's category is fixed for its lifetime, so first occurrence wins."""
    out: dict[str, str] = {}
    for m in manifests:
        for c in m.get("changes", []):
            out.setdefault(c["label"], c["object_category"])
    return out


def _validate_all(out_dir: pathlib.Path, folders: list[str]) -> tuple[bool, list[str]]:
    """(all_ok, failing_folder_names) — a scene is excluded from the tally
    entirely if any of its consumed folders fails trace_validate (see
    module docstring's contamination guard)."""
    failing = []
    for folder in folders:
        if not (out_dir / folder / "manifest.json").exists():
            continue  # not generated yet, not a validation failure
        if not validate_folder(out_dir, folder).ok:
            failing.append(folder)
    return (not failing, failing)


def _location_hazard_counts(
    scene: str, profile: str, qualified_labels: list[str], out_dir: pathlib.Path,
) -> tuple[dict[str, int], list[str]]:
    """(hazard counts, excluded-folder reasons). Empty counts + a non-empty
    reasons list means this scene's location contribution was excluded
    entirely for failing validation, not silently zero because it had no data."""
    _day0, train_folders, _eval_folder = _folder_names(scene, profile)
    existing_folders = [f for f in train_folders if (out_dir / f / "manifest.json").exists()]
    if not existing_folders:
        return {}, []

    all_ok, failing = _validate_all(out_dir, existing_folders)
    if not all_ok:
        return {}, failing

    train_manifests = [json.loads((out_dir / f / "manifest.json").read_text()) for f in existing_folders]
    category_stats = aggregate_category_stats([category_location_change_stats(m["changes"]) for m in train_manifests])
    decay_models = fit_decay_models(category_stats)
    label_cat = _label_categories(train_manifests)

    counts = {"stable": 0, "volatile": 0}
    for label in qualified_labels:
        cat = label_cat.get(label)
        if cat is None:
            continue
        counts[classify_hazard(cat, decay_models)] += 1
    return counts, []


def _state_folder_name(name: str) -> str:
    for i in range(1, 5):
        suffix = f"_day{i}"
        if name.endswith(suffix):
            return name[: -len(suffix)] + "_state" + suffix
    return name + "_state"


def _state_hazard_counts(scene: str, profile: str, out_dir: pathlib.Path) -> tuple[dict[str, int], list[str]]:
    """Qualifying (label, variable) pairs (has a state_change event in the
    state eval day — the same "moved/flipped at least once" property
    FROZEN_STATE_LABELS uses) and their hazard split, computed directly
    from the *_state folders scripts/generate_state_stratum.py wrote.
    (These folders are only ever written after a clean trace_validate pass
    — see that script's own docstring — so no separate validation gate is
    needed here beyond confirming they exist.)"""
    _day0, train_folders, eval_folder = _folder_names(scene, profile)
    state_train_folders = [_state_folder_name(f) for f in train_folders]
    state_eval_folder = _state_folder_name(eval_folder)

    existing = [f for f in state_train_folders if (out_dir / f / "manifest.json").exists()]
    eval_path = out_dir / state_eval_folder / "manifest.json"
    if not existing or not eval_path.exists():
        return {}, []

    state_train_manifests = [json.loads((out_dir / f / "manifest.json").read_text()) for f in existing]
    eval_manifest = json.loads(eval_path.read_text())
    qualifying_keys = sorted({
        c["object_category"] + "::" + c["state_variable"]
        for c in eval_manifest["changes"] if c.get("change_type") == "state_change"
    })
    if not qualifying_keys:
        return {}, []

    flip_stats = aggregate_flip_stats(
        [category_state_flip_stats(m["changes"]) for m in state_train_manifests]
    )
    category_stats = {k: {"location_changes": v["flip_count"], "mean_dwell_hours": v["mean_dwell_hours"]}
                       for k, v in flip_stats.items()}
    decay_models = fit_decay_models(category_stats)

    counts = {"stable": 0, "volatile": 0}
    for key in qualifying_keys:
        counts[classify_hazard(key, decay_models)] += 1
    return counts, []


def project(state: dict[str, ScenePoolEntry], out_dir: pathlib.Path) -> tuple[StratumTally, list[str]]:
    tally = StratumTally()
    excluded: list[str] = []

    frozen_loc, frozen_loc_fail = _location_hazard_counts(FROZEN.scene, FROZEN.profile, list(FROZEN.labels), out_dir)
    for hazard, n in frozen_loc.items():
        tally.add("location", hazard, n, FROZEN.scene)
    if frozen_loc_fail:
        excluded.append(f"{FROZEN.scene} (location): failing folders {frozen_loc_fail}")
    frozen_state, frozen_state_fail = _state_hazard_counts(FROZEN.scene, FROZEN.profile, out_dir)
    for hazard, n in frozen_state.items():
        tally.add("state", hazard, n, FROZEN.scene)

    for scene_id, entry in state.items():
        if entry.qualified_labels:
            counts, fail = _location_hazard_counts(scene_id, entry.profile, entry.qualified_labels, out_dir)
            for hazard, n in counts.items():
                tally.add("location", hazard, n, scene_id)
            if fail:
                excluded.append(f"{scene_id} (location): failing folders {fail}")
        # Checked unconditionally (not gated on entry.state_generated) —
        # _state_hazard_counts already checks folder existence on disk
        # directly and returns empty if the state stratum isn't there yet;
        # gating on the pool orchestrator's own flag would undercount a
        # scene whose _state folders exist from a manual
        # generate_state_stratum.py run the orchestrator's flag hasn't
        # caught up to yet.
        counts, fail = _state_hazard_counts(scene_id, entry.profile, out_dir)
        for hazard, n in counts.items():
            tally.add("state", hazard, n, scene_id)
        if fail:
            excluded.append(f"{scene_id} (state): failing folders {fail}")

    return tally, excluded


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=str(_DYNAMIC_EQA / "generation_out"))
    ap.add_argument("--state", default=str(_DYNAMIC_EQA / "generation_out" / "_expand_scene_pool_state.json"))
    ap.add_argument("--eval-days", type=int, default=1, help="Projected eval days per scene (default: 1, today's actual)")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out_dir)
    state = load_state(pathlib.Path(args.state))
    tally, excluded = project(state, out_dir)

    print(f"Scenes in pool: {len(state)} (+ frozen scene {FROZEN.scene}) — projecting at eval_days={args.eval_days}")
    if excluded:
        print(f"\nEXCLUDED (failed trace_validate, not counted): {len(excluded)}")
        for line in excluded:
            print(f"  - {line}")
    print()

    strata = [
        ("location", "stable",   tally.location_stable,   tally.location_stable_scenes,   _N_POLICIES_LOCATION),
        ("location", "volatile", tally.location_volatile, tally.location_volatile_scenes, _N_POLICIES_LOCATION),
        ("state",    "stable",   tally.state_stable,      tally.state_stable_scenes,      _N_POLICIES_STATE),
        ("state",    "volatile", tally.state_volatile,    tally.state_volatile_scenes,    _N_POLICIES_STATE),
    ]
    header = f"{'question_type':<12} {'hazard':<10} {'raw_N':>9} {'n_clusters':>10}  bar(effective)"
    print(header)
    print("-" * len(header))
    shortfalls = []
    for qtype, hazard, n_labels, scenes, n_policies in strata:
        raw_n = n_labels * args.eval_days * _N_WAIT_HOURS * n_policies
        n_clusters = len(scenes)
        status = "OK" if n_clusters >= _STATE_BAR else "SHORT"
        print(f"{qtype:<12} {hazard:<10} {raw_n:>9} {n_clusters:>10}  [{status}]")
        if n_clusters < _STATE_BAR:
            shortfalls.append((qtype, hazard, n_clusters))

    print()
    if not shortfalls:
        print(f"All 4 strata clear the >={_STATE_BAR} bar on n_clusters (effective-N).")
    else:
        print(f"{len(shortfalls)}/4 strata short of the >={_STATE_BAR} bar on n_clusters (effective-N — "
              f"see module docstring for why raw_N is not the right denominator):")
        for qtype, hazard, n_clusters in shortfalls:
            print(f"  {qtype}/{hazard}: {n_clusters}/{_STATE_BAR} qualifying scenes — "
                  f"needs {_STATE_BAR - n_clusters} more qualifying scenes, NOT more eval_days "
                  f"per existing scene (see module docstring).")


if __name__ == "__main__":
    main()
