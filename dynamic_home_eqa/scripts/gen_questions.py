#!/usr/bin/env python3
"""
gen_questions.py — Generate MCQs from a full-day manifest.

Reads the manifest.json produced by the LLM generation pipeline
(generation/pipeline.py + generation/manifest.py, driven by scripts/gen_dataset.py)
and samples multiple (observed_at, elapsed) windows across the day.  For each
window it generates:
  • LOCATION questions for objects that changed in the window  (stale may be wrong)
  • LOCATION questions for objects that did NOT change         (stale always correct)

Each question's metadata includes observed_at and elapsed so the harness can
reconstruct the stale observation without a hardcoded hour offset.

Usage:
  python -m dynamic_home_eqa.scripts.gen_questions results/102343992_work_from_home_adult/
  python -m dynamic_home_eqa.scripts.gen_questions results/                  # all subdirs
  python -m dynamic_home_eqa.scripts.gen_questions results/ --n-windows 10
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys
from typing import Optional

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.env.state import SceneState
from dynamic_home_eqa.env.deltas import Change
from dynamic_home_eqa.env.replay import initial_state_and_changes_from_manifest, state_at
from dynamic_home_eqa.qa.questions import QuestionSpec, QueryType, build_mcq, _dedup
from dynamic_home_eqa.qa.difficulty import assign_difficulty_bins
from dynamic_home_eqa.qa.export import batch_to_json

# Day boundaries
_DAY_START = 6.0
_DAY_END   = 22.0

# Windows per manifest and stable questions per window
_N_WINDOWS           = 10
_N_STABLE_PER_WINDOW = 2


# ---------------------------------------------------------------------------
# Manifest → initial state + Change list
# ---------------------------------------------------------------------------

# _initial_state_from_manifest / _changes_from_manifest moved to
# env/replay.py::initial_state_and_changes_from_manifest — this file, agents/
# harness.py, and the embodied-agent world all shared this exact conversion.


# ---------------------------------------------------------------------------
# Window sampling
# ---------------------------------------------------------------------------

def _sample_windows(
    changes: list[Change],
    seed: int,
    n: int = _N_WINDOWS,
) -> list[tuple[float, float]]:
    """Return up to n (observed_at, elapsed) pairs spread across the day."""
    change_times = sorted({c.t for c in changes})
    rng          = random.Random(seed)
    candidates: set[tuple[float, float]] = set()

    for ct in change_times:
        for pre in [0.25, 0.5, 1.0, 2.0, 3.0]:
            obs = round(ct - pre, 2)
            if obs < _DAY_START:
                continue
            for elapsed in [pre * 0.5, pre + 0.25, pre + 1.0, pre + 2.5, pre + 4.0]:
                elapsed = round(elapsed, 2)
                qt = obs + elapsed
                if elapsed > 0.1 and qt <= _DAY_END + 2:
                    candidates.add((obs, elapsed))

    for obs in [6.5, 7.5, 9.0, 11.0, 13.5, 14.0, 16.5, 17.0, 19.5, 21.0]:
        for elapsed in [0.5, 1.0, 2.0, 3.0]:
            qt = obs + elapsed
            in_window = any(obs < ct <= qt for ct in change_times)
            if not in_window and qt <= _DAY_END + 1:
                candidates.add((obs, round(elapsed, 2)))

    pool = list(candidates)
    rng.shuffle(pool)
    return pool[:n]


# ---------------------------------------------------------------------------
# Spec generation for a single window
# ---------------------------------------------------------------------------

def _specs_for_window(
    observed_at: float,
    query_time: float,
    initial_state: SceneState,
    changes: list[Change],
    rng: random.Random,
    n_stable: int = _N_STABLE_PER_WINDOW,
) -> list[QuestionSpec]:
    in_window   = [c for c in changes if observed_at < c.t <= query_time]
    changed_ids = {c.instance_id for c in in_window}

    specs: list[QuestionSpec] = []

    seen_ids: set[str] = set()
    for c in in_window:
        if c.instance_id in seen_ids:
            continue
        seen_ids.add(c.instance_id)
        specs.append(QuestionSpec(
            query_type=QueryType.LOCATION,
            t=query_time,
            object_category=c.object_category,
            instance_id=c.instance_id,
            target_slot=None,
            observed_at=observed_at,
            difficulty_bin="",
        ))

    snap = state_at(initial_state, changes, observed_at)
    stable_candidates = [
        (iid, inst)
        for iid, inst in snap.instances.items()
        if iid not in changed_ids and inst.current_semantic
    ]
    rng.shuffle(stable_candidates)
    for iid, inst in stable_candidates[:n_stable]:
        specs.append(QuestionSpec(
            query_type=QueryType.LOCATION,
            t=query_time,
            object_category=inst.category,
            instance_id=iid,
            target_slot=None,
            observed_at=observed_at,
            difficulty_bin="stable",
        ))

    return specs


# ---------------------------------------------------------------------------
# Per-manifest entry point
# ---------------------------------------------------------------------------

def generate_for_manifest(
    manifest_path: pathlib.Path,
    n_windows: int,
    out: Optional[pathlib.Path],
    verbose: bool = True,
) -> list[dict]:
    with open(manifest_path) as f:
        manifest = json.load(f)

    scene_id     = manifest["scene_id"]
    profile      = manifest.get("resident_profile", "unknown")
    seed         = manifest.get("seed", 0)
    household_id = f"{scene_id}_{profile}_s{seed}"

    if verbose:
        print(f"\n{'─'*60}")
        print(f"Scene  : {scene_id}  profile={profile}  seed={seed}")
        n_ch = len(manifest.get("changes", []))
        print(f"Changes: {n_ch} in day timeline")

    initial_state, changes = initial_state_and_changes_from_manifest(manifest)

    if not changes:
        if verbose:
            print("  No changes — skipping.")
        return []

    windows = _sample_windows(changes, seed=seed, n=n_windows)

    rng = random.Random(seed + 1)
    all_specs: list[QuestionSpec] = []

    for obs_at, elapsed in windows:
        qt = round(obs_at + elapsed, 3)
        window_specs = _specs_for_window(obs_at, qt, initial_state, changes, rng)
        all_specs.extend(window_specs)

    seen: set[tuple] = set()
    deduped: list[QuestionSpec] = []
    for s in all_specs:
        key = (s.query_type, round(s.observed_at, 2), round(s.t, 2),
               s.instance_id, s.target_slot)
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    all_specs = deduped

    assign_difficulty_bins(all_specs, changes)

    questions = [
        build_mcq(s, initial_state, changes, household_id, day=0)
        for s in all_specs
    ]

    if verbose:
        bins = {}
        for q in questions:
            b = q.spec.difficulty_bin
            bins[b] = bins.get(b, 0) + 1
        print(f"{len(questions)} questions  " +
              "  ".join(f"{k}={v}" for k, v in sorted(bins.items())))
        print()
        for i, q in enumerate(questions, 1):
            obs  = q.metadata["observed_at"]
            qt   = q.metadata["present_time"]
            ela  = q.metadata["elapsed"]
            diff = q.spec.difficulty_bin
            print(f"  Q{i:02d} [{diff:6}] obs={obs:.2f}h → qt={qt:.2f}h (Δ={ela:.2f}h)  {q.prompt}")
            for j, opt in enumerate(q.options):
                marker = "✓" if j == q.correct_index else " "
                print(f"         {marker} {chr(65+j)}) {opt}")
            print()

    if out is None:
        out = manifest_path.parent / "questions.json"
    batch_to_json(questions, path=out)
    if verbose:
        print(f"Wrote → {out}")

    return [json.loads(batch_to_json(questions))]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _find_manifests(target: pathlib.Path) -> list[pathlib.Path]:
    target = target.expanduser()
    if not target.is_absolute():
        cwd_try  = (pathlib.Path.cwd() / target).resolve()
        root_try = (_DYNAMIC_EQA / target).resolve()
        target   = cwd_try if cwd_try.exists() else root_try
    else:
        target = target.resolve()

    if target.is_file() and target.name == "manifest.json":
        return [target]
    if target.is_dir():
        direct = target / "manifest.json"
        if direct.exists():
            return [direct]
        found = sorted(target.glob("*/manifest.json"))
        if found:
            return found
    sys.exit(f"No manifest.json found at or under: {target}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target",
                    help="manifest.json, a result subfolder, or a results/ parent dir")
    ap.add_argument("--n-windows", type=int, default=_N_WINDOWS,
                    help=f"Windows per manifest (default: {_N_WINDOWS})")
    ap.add_argument("--out", default=None,
                    help="Output JSON path (single-manifest mode only)")
    args = ap.parse_args()

    manifests = _find_manifests(pathlib.Path(args.target))
    out_path  = pathlib.Path(args.out) if args.out else None

    if len(manifests) > 1 and out_path:
        sys.exit("--out only valid for a single manifest")

    print(f"Processing {len(manifests)} manifest(s) …")
    total_q = 0
    for m in manifests:
        generate_for_manifest(m, args.n_windows, out_path,
                              verbose=(len(manifests) == 1))
        if len(manifests) > 1:
            qp = m.parent / "questions.json"
            if qp.exists():
                n = json.loads(qp.read_text()).get("total", 0)
                total_q += n
                print(f"  {m.parent.name}: {n} questions")

    if len(manifests) > 1:
        print(f"\nTotal: {total_q} questions across {len(manifests)} scenes")


if __name__ == "__main__":
    main()
