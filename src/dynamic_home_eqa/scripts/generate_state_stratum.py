#!/usr/bin/env python3
"""
generate_state_stratum.py — build the M3 state-change stratum for any
already-generated scene from data already on disk. No LLM calls, no
habitat_sim.

For each existing day folder of a (scene, profile) pair (e.g.
generation_out/102343992_family_with_kids{,_day1..4}), reads that folder's
generation_result.json (for its real persona/activity traces) and
manifest.json (for its existing location changes), runs
generation.manifest.build_state_changes (the deterministic proposer +
grounding + no-op/attendance threading — see that function's docstring) to
produce new state-change events, merges them into a COPY of that day's
changes list (the original location events are untouched), and writes the
result to a new sibling folder (<name>_state[_dayN]) — the source folders
are never modified in place (see experiment_config.py's module docstring
for why frozen folders in particular are never regenerated in place; the
same non-destructive principle applies to any scene here).

Each day starts its state chain fresh from scene-init (existing_changes=
None) — the same convention build_manifest() already uses for location
(load_scene_state(scene_id) fresh per day, no cross-day carryover; these
are independent daily samples, not one continuous multi-day narrative).

This generalizes the original frozen-scene-only version (hardcoded to
102343992_family_with_kids's 5 folders) so it can run as a second pass over
any scene in the scene-pool expansion, once that scene's location-only
generation (which does not itself call build_state_changes — see
generation/pipeline.py's build_manifest() call, include_state_changes
defaults to False) has finished.

Usage:
    python -m dynamic_home_eqa.scripts.generate_state_stratum --scene 102343992 --profile family_with_kids
    python -m dynamic_home_eqa.scripts.generate_state_stratum --scene 102344049 --profile family_with_kids
    python -m dynamic_home_eqa.scripts.generate_state_stratum --scene 102343992 --profile family_with_kids \\
        --folders 102343992_family_with_kids 102343992_family_with_kids_day1
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import sys

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.generation.manifest import build_state_changes
from dynamic_home_eqa.trace_validate import validate


def _state_folder_name(name: str) -> str:
    for i in range(1, 5):
        suffix = f"_day{i}"
        if name.endswith(suffix):
            return name[: -len(suffix)] + "_state" + suffix
    return name + "_state"


def discover_folders(out_dir: pathlib.Path, scene: str, profile: str) -> list[str]:
    """{scene}_{profile}[, _day1.._day4] — whichever of those exist and have
    both generation_result.json and manifest.json, in day order. Tolerant of
    a scene mid-generation (fewer than 5 days done yet) rather than
    requiring the full set up front."""
    base = f"{scene}_{profile}"
    candidates = [base] + [f"{base}_day{i}" for i in range(1, 5)]
    return [
        name for name in candidates
        if (out_dir / name / "generation_result.json").exists()
        and (out_dir / name / "manifest.json").exists()
    ]


def build_state_stratum_for_folder(scene: str, out_dir: pathlib.Path, folder: str) -> bool:
    """Returns True on success (wrote the _state sibling folder), False if
    trace_validate failed on the merged output (nothing written — see main()
    for why a failure here does not necessarily mean this function is
    wrong; see also the module docstring on non-destructive output)."""
    src_dir = out_dir / folder
    generation_result = json.loads((src_dir / "generation_result.json").read_text())
    manifest = json.loads((src_dir / "manifest.json").read_text())

    state_changes = build_state_changes(scene, generation_result, existing_changes=None)
    merged = sorted(manifest["changes"] + state_changes, key=lambda c: c["t"])

    report = validate(merged, generation_result.get("traces", []))
    status = "OK" if report.ok else "FAIL"
    print(f"{folder:50s} -> {len(state_changes):3d} state events  {report.summary()}  [{status}]")
    if not report.ok:
        return False

    new_manifest = copy.deepcopy(manifest)
    new_manifest["changes"] = merged

    dst_dir = out_dir / _state_folder_name(folder)
    dst_dir.mkdir(parents=True, exist_ok=True)
    (dst_dir / "manifest.json").write_text(json.dumps(new_manifest, indent=2))
    (dst_dir / "generation_result.json").write_text(json.dumps(generation_result, indent=2))
    print(f"  -> wrote {dst_dir}")
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--out", default=str(_DYNAMIC_EQA / "generation_out"))
    ap.add_argument("--folders", nargs="+", default=None,
                    help="Explicit folder names (overrides auto-discovery of "
                         "{scene}_{profile}[_day1..4])")
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out)
    folders = args.folders or discover_folders(out_dir, args.scene, args.profile)
    if not folders:
        sys.exit(f"No generated folders found for scene={args.scene} profile={args.profile} under {out_dir}")

    failures = []
    for folder in folders:
        if not build_state_stratum_for_folder(args.scene, out_dir, folder):
            failures.append(folder)

    if failures:
        sys.exit(
            f"trace_validate failed for {len(failures)}/{len(folders)} folder(s): {failures} — "
            "their location data itself has integrity violations (see the summary lines above); "
            "not a state-generation bug. No _state folder was written for these; fix or "
            "regenerate the underlying location data before retrying."
        )


if __name__ == "__main__":
    main()
