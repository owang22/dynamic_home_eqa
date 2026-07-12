#!/usr/bin/env python3
"""
compute_sensability_map.py — scene-qualification pre-flight: for every
real anchor a scene resolves, run the EMBODIED (navmesh-snapped,
eye-height-constrained — embodied.sensor.viewpoint_for/EmbodiedWorld.
viewpoint_for) viewpoint search ONCE and cache the result, instead of
finding out an anchor has no navigable viewpoint mid-render or mid-
experiment.

This is the piece the Spectator Camera round's item 4 exists to add,
directly answering a real critique: the render job could already report
OBJECT_SPAWN_FAILED and (formerly) NO_NAVIGABLE_VIEWPOINT per panel, but
only at render time, deep into a sampled batch — never at generation or
question-tagging time, when a cheaper decision (skip this anchor, don't
even propose a question about it) is still possible. The render job's
OWN camera search is intentionally NOT this one: render_event_grid uses
embodied.sensor.spectator_viewpoint, a study camera with no navmesh/
eye-height constraint, precisely because the render job's question
("can we get a legible photo of this object") is different from the
embodied-agent question this map answers ("can a real embodied agent,
standing on the floor at eye height, ever see this anchor"). Consumers
of THIS map are things that care about the agent question — question
tagging (don't ask about an anchor the agent could never verify),
oracle-v2, and the generation-quality report — not the render job, which
is explicitly out of scope here (see the round's own instruction).

Output: one JSON file per scene, data/sensability_maps/<scene_id>.json:
    {
      "scene_id": "...",
      "code_hash": "...",     # embodied/sensor.py's content hash, for
                                # staleness detection the same way
                                # build_realized_day.py's artifacts do
      "anchors": {
        "<anchor>": {"robot_visible": true,  "pose": {"x":.., "y":.., "z":.., "yaw_rad":..}},
        "<anchor>": {"robot_visible": false, "pose": null},
        ...
      }
    }

Requires habitat_sim — run from a conda env that has it (e.g.
explore-eqa), same convention as qualify_scene.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Optional

from dynamic_home_eqa.paths import PACKAGE_ROOT, REPO_ROOT as _DYNAMIC_EQA

_OUT_DIR = _DYNAMIC_EQA / "data" / "sensability_maps"


def _code_hash() -> str:
    """Content hash of embodied/sensor.py — the same staleness-detection
    convention build_realized_day.py's _code_hash uses (see its
    docstring): a map built against an OLD viewpoint_for implementation
    should be treated as stale, not silently trusted forever."""
    src = (PACKAGE_ROOT / "embodied" / "sensor.py").read_bytes()
    return hashlib.sha256(src).hexdigest()[:16]


def compute_sensability_map(scene_id: str, world) -> dict:
    """Runs the embodied viewpoint search once per anchor in `world`
    (an already-constructed EmbodiedWorld) and returns the map dict
    described in this module's docstring. Pure orchestration over
    world.viewpoint_for — no new visibility logic here, reuses the exact
    mechanism EmbodiedWorld/embodied.sensor already provide and every
    other experiment already trusts."""
    anchors: dict[str, dict] = {}
    for anchor in sorted(world._anchor_positions):
        vp = world.viewpoint_for(anchor)
        if vp is None:
            anchors[anchor] = {"robot_visible": False, "pose": None}
        else:
            anchors[anchor] = {
                "robot_visible": True,
                "pose": {"x": vp.x, "y": vp.y, "z": vp.z, "yaw_rad": vp.yaw_rad},
            }
    return {"scene_id": scene_id, "code_hash": _code_hash(), "anchors": anchors}


def save_sensability_map(scene_map: dict, out_dir: pathlib.Path = _OUT_DIR) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{scene_map['scene_id']}.json"
    path.write_text(json.dumps(scene_map, indent=2))
    return path


def load_sensability_map(scene_id: str, out_dir: pathlib.Path = _OUT_DIR) -> Optional[dict]:
    """None if this scene has no cached map yet — a consumer should treat
    that as "unknown", not "not visible"; run this script first."""
    path = out_dir / f"{scene_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def is_robot_visible(scene_map: dict, anchor: str) -> Optional[bool]:
    """True/False if `anchor` is in the map, None if this scene's map has
    no entry for it at all (a genuinely unknown anchor, not the same as a
    known-unreachable one — callers should distinguish the two)."""
    entry = scene_map["anchors"].get(anchor)
    return entry["robot_visible"] if entry is not None else None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenes", nargs="+", required=True)
    ap.add_argument("--folder-hint", default=None,
                     help="a generation_out/ folder for this scene, to build a real EmbodiedWorld "
                          "(generation_result.json + manifest.json just supply the day-trace scaffolding "
                          "EmbodiedWorld's constructor needs — anchor positions/navmesh are scene-level, "
                          "not folder-level, so any real folder for the scene gives the same map).")
    args = ap.parse_args()

    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    from dynamic_home_eqa.scripts.generation_diversity_report import discover_valid_folders

    out_dir = _DYNAMIC_EQA / "generation_out"
    folders_by_scene: dict[str, str] = {}
    for folder in discover_valid_folders(out_dir):
        gen_result = json.loads((out_dir / folder / "generation_result.json").read_text())
        folders_by_scene.setdefault(gen_result["scene_id"], folder)

    for scene_id in args.scenes:
        folder = args.folder_hint or folders_by_scene.get(scene_id)
        if folder is None:
            print(f"SKIPPING {scene_id}: no generation_out/ folder found for it "
                  f"(pass --folder-hint explicitly).")
            continue

        gen_result = json.loads((out_dir / folder / "generation_result.json").read_text())
        manifest = json.loads((out_dir / folder / "manifest.json").read_text())
        world = EmbodiedWorld(scene_id, gen_result, manifest)
        try:
            world._ensure_sim()
            scene_map = compute_sensability_map(scene_id, world)
        finally:
            world.close()

        n_visible = sum(1 for a in scene_map["anchors"].values() if a["robot_visible"])
        n_total = len(scene_map["anchors"])
        path = save_sensability_map(scene_map)
        print(f"{scene_id} (via {folder!r}): {n_visible}/{n_total} anchors robot-visible -> {path}")


if __name__ == "__main__":
    main()
