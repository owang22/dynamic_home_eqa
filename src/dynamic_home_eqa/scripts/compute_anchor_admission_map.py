#!/usr/bin/env python3
"""
compute_anchor_admission_map.py — Anchor Admission round (Version B):
one-time, per-scene precomputation of two facts generation currently
has no visibility into, both closed by a REAL sim query rather than a
category-count census:

  - reachable: is this anchor's real position on a navmesh island at or
    above NavMeshConfig.min_component_area_m2 — the same threshold
    embodied/world.py's EmbodiedWorld._ensure_sim() prunes anchors with.
    Closes the class of anchor_unbacked failures a census can never see
    (confirmed concretely this round: a real `tv` instance sitting on a
    disconnected navmesh island, 40 events across the 3+1 rebuilt
    folders).
  - capacity: an approximate object-count budget for an "instance"-kind
    anchor's placement surface, mirroring build_realized_day.py's own
    receptacle-vs-synthetic-fallback precedence exactly (real receptacle
    area when an active receptacle exists; synthetic-AABB-top area
    otherwise — the Realizable-Anchor Vocabulary round removed the old
    third branch, "None for a curated-out receptacle", along with
    PLACEMENT_RECEPTACLE_CURATED_OUT itself: curation acts at LLM
    generation time now, and the builder's empty-receptacle path is the
    synthetic-top fallback for every cause). Reduces (does not eliminate —
    this is a heuristic, not a real snap_down attempt) the residual
    genuine SURFACE_FULL class.

Iterates topdown_map.anchor_world_positions(scene_id) UNPRUNED, not
EmbodiedWorld._anchor_positions — the latter has already silently
dropped unreachable entries by the time it's built, and this script's
whole job is to RECORD unreachability, not inherit its absence.

Requires habitat-lab, not just habitat_sim (the dynamic_eqa env has both):
capacity estimation reuses build_realized_day.py's real receptacle
machinery (resolve_furniture_receptacles -> habitat-lab's
find_receptacles), the same env constraint build_realized_day.py itself
has. Reachability alone would work under plain habitat_sim, but this
script computes both in one pass over one sim instance.

Output: data/anchor_admission_maps/<scene_id>.json (see
env/anchor_admission.py, which owns the read-side schema/accessors this
script's output must match — ADMISSION_VERSION lives there, not here,
since it's a manual staleness-invalidation constant, not a content hash
of this file).
"""
from __future__ import annotations

import argparse
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

# A mug/book/small-object footprint — the one genuinely invented number
# in this feature. Calibrated by running against real scenes and
# eyeball-checking the result (a nightstand should land low, a counter/
# desk higher), not derived from anything. Recorded in every output
# file's own "footprint_m2" field so a later recalibration is
# self-documenting per cached map, not silently inconsistent across
# scenes computed at different times.
#
# 0.06 (a bare bounding-box mug/book footprint) was the initial guess:
# WRONG by direct calibration against 3 real scenes — gave bed=25-33,
# kitchen.table=33, fireplace=22, areas divided by a tight packing
# footprint rather than a realistic per-anchor budget. 0.25 m^2 (roughly
# a dinner-plate spacing) looked more plausible in isolation but is ALSO
# confirmed wrong, by a stronger test: a real, live Qwen3-32B generation
# run against this exact scene rejected 34 of 46 otherwise-valid
# proposals as "over capacity" (fridge=1, dining.table=4 dominating),
# collapsing a 55-displacement day down to 12 changes — breaking the
# "default args produce a good test" requirement outright, not a minor
# tuning nit. 0.10 m^2 is the corrected value: re-run against the SAME
# real generation_result.json (no new LLM call needed, responses were
# cached from the run that exposed this), keeps a healthy majority of
# the day's real proposals while still rejecting genuine pileups —
# see results/reports/ for the exact before/after counts this was
# checked against. Still a heuristic, not ground truth; recalibrate
# again if a future real run shows it's still off in either direction.
_TYPICAL_OBJECT_FOOTPRINT_M2 = 0.10

# Minimum capacity for a "synthetic" (AABB-top) source — see
# _estimate_capacity's own comment for why area-based math structurally
# undercounts storage/appliance furniture (fridge, oven, dishwasher).
_SYNTHETIC_CAPACITY_FLOOR = 8


def _estimate_capacity(sim, scene_id: str, pos: tuple[float, float, float], active_names_cache: dict):
    """(capacity, capacity_source) for the real furniture instance at
    `pos`, or (None, None) if there's no live object there, no usable
    receptacle at all is authored (curated-out), or the computed area
    is non-positive. Mirrors compliance_place_on_surface's own 3-way
    branch (build_realized_day.py) exactly, so a capacity estimate is
    never claiming a placement mechanism the real build wouldn't
    actually use for this anchor."""
    from dynamic_home_eqa.scripts.build_realized_day import (
        _SYNTHETIC_EDGE_MARGIN_M,
        find_live_object_at_xz,
        get_world_aabb,
        resolve_furniture_receptacles,
    )

    furniture = find_live_object_at_xz(sim, pos)
    if furniture is None:
        return None, None

    receptacles = resolve_furniture_receptacles(sim, scene_id, furniture, active_names_cache)
    if receptacles:
        area = sum(r.bounds.size().x * r.bounds.size().z for r in receptacles)
        source = "receptacle"
    else:
        (min_x, _min_y, min_z), (max_x, _max_y, max_z) = get_world_aabb(furniture)
        lo_x, hi_x = min_x + _SYNTHETIC_EDGE_MARGIN_M, max_x - _SYNTHETIC_EDGE_MARGIN_M
        lo_z, hi_z = min_z + _SYNTHETIC_EDGE_MARGIN_M, max_z - _SYNTHETIC_EDGE_MARGIN_M
        area = max(0.0, hi_x - lo_x) * max(0.0, hi_z - lo_z)
        source = "synthetic"

    if area <= 0:
        return None, None
    capacity = max(1, int(area // _TYPICAL_OBJECT_FOOTPRINT_M2))
    if source == "synthetic":
        # Confirmed a real, distinct problem, not just under-calibration:
        # the item-4 synthetic fallback measures the flat area on TOP of
        # the furniture's own AABB (build_realized_day.py's own
        # _synthetic_top_candidates) — for appliance/storage furniture
        # (fridge, oven, dishwasher) that's a poor proxy for real
        # capacity ("how many groceries fit in a fridge" has nothing to
        # do with the area of its lid). Confirmed via a real live-LLM
        # run: fridge's tiny top-of-appliance area alone accounted for
        # 100% of remaining rejected_over_capacity events even after the
        # general footprint recalibration fixed every other anchor.
        # build_realized_day.py's own synthetic fallback isn't
        # meaningfully volume-limited the way a real receptacle surface
        # is, so the admission-time budget shouldn't be tighter than
        # what the real build can actually do — a generous floor here,
        # not a tight area-derived number.
        capacity = max(capacity, _SYNTHETIC_CAPACITY_FLOOR)
    return capacity, source


def compute_anchor_admission_map(scene_id: str, sim) -> dict:
    """Pure orchestration: embodied.islands for reachability,
    build_realized_day's own classify_anchor/receptacle/AABB helpers for
    capacity — no new placement or navmesh logic invented here."""
    from dynamic_home_eqa.embodied.config import NavMeshConfig
    from dynamic_home_eqa.embodied.islands import is_reachable_island
    from dynamic_home_eqa.env.anchor_admission import ADMISSION_VERSION
    from dynamic_home_eqa.scripts.build_realized_day import classify_anchor
    from dynamic_home_eqa.topdown_map import anchor_world_positions

    navmesh = NavMeshConfig()
    positions = anchor_world_positions(scene_id)  # unpruned, real per-scene census positions
    pf = sim.pathfinder
    active_names_cache: dict = {}

    anchors: dict[str, dict] = {}
    for anchor, pos in sorted(positions.items()):
        reachable = is_reachable_island(pf, pos, navmesh.min_component_area_m2)
        capacity, source = None, None
        if reachable:
            kind, _cats = classify_anchor(anchor)
            if kind == "instance":
                capacity, source = _estimate_capacity(sim, scene_id, pos, active_names_cache)
        anchors[anchor] = {"reachable": reachable, "capacity": capacity, "capacity_source": source}

    return {
        "scene_id": scene_id,
        "admission_version": ADMISSION_VERSION,
        "footprint_m2": _TYPICAL_OBJECT_FOOTPRINT_M2,
        "anchors": anchors,
    }


_DEFAULT_TEST_SCENE = "102343992"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # Default: the same fixture scene build_realized_day.py's own --folders
    # default resolves to (102343992_family_with_kids) — a no-arg run of
    # the whole pipeline stays consistent end to end.
    ap.add_argument("--scenes", nargs="+", default=[_DEFAULT_TEST_SCENE])
    args = ap.parse_args()

    from dynamic_home_eqa.embodied.config import NavMeshConfig
    from dynamic_home_eqa.embodied.reachability import make_sim
    from dynamic_home_eqa.env.anchor_admission import save_anchor_admission_map

    for scene_id in args.scenes:
        sim = make_sim(scene_id, NavMeshConfig())
        try:
            admission_map = compute_anchor_admission_map(scene_id, sim)
        finally:
            sim.close()

        path = save_anchor_admission_map(admission_map)
        anchors = admission_map["anchors"]
        n_total = len(anchors)
        n_reachable = sum(1 for a in anchors.values() if a["reachable"])
        n_capacity = sum(1 for a in anchors.values() if a["capacity"] is not None)
        unreachable = sorted(a for a, v in anchors.items() if not v["reachable"])
        print(f"{scene_id}: {n_reachable}/{n_total} reachable, {n_capacity} with a capacity estimate")
        if unreachable:
            print(f"  unreachable: {', '.join(unreachable)}")
        print(f"  wrote {path}")


if __name__ == "__main__":
    main()
