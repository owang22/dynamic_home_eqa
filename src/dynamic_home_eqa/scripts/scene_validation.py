"""
scene_validation.py — shared "load a scene-day folder and validate it"
helper (Suite Buildout phase A's contamination-audit primitive).

Every artifact that consumes scene-pool data (yield_projector.py,
e2_headline_comparison.py, generate_state_stratum.py) uses this same
function rather than N reimplementations of the same read+validate glue,
so the trace_validate status hash recorded in each artifact's own output
is computed identically everywhere — the whole point of "close the hole
permanently": a scene-day that fails validation must be detectable
mechanically by every consumer, not remembered by whoever found it first.
"""
from __future__ import annotations

import json
import pathlib

from dynamic_home_eqa.trace_validate import Report, validate


def validate_folder(out_dir: pathlib.Path, folder: str) -> Report:
    """Load {out_dir}/{folder}/generation_result.json + manifest.json and
    run trace_validate.validate() against them."""
    gr = json.loads((out_dir / folder / "generation_result.json").read_text())
    manifest = json.loads((out_dir / folder / "manifest.json").read_text())
    return validate(manifest["changes"], gr.get("traces", []))


def validate_folders(out_dir: pathlib.Path, folders: list[str]) -> dict[str, Report]:
    """{folder: Report} for every folder — callers combine per-folder
    .ok/.validation_hash() into whatever manifest field their own output
    format uses (see e2_headline_comparison.SceneDescriptor.validation_hashes,
    yield_projector's per-scene exclusion log)."""
    return {folder: validate_folder(out_dir, folder) for folder in folders}
