#!/usr/bin/env python3
"""
realism_render_job.py — offline pre-render of before/after media for the
realism human-eval study (Step 1 of the webapp instructions).

For a uniform random sample of change events (per change_type — see
select_random_sample_per_type), writes per item:
  - a 2x2 PNG (egocentric RGB before/after, top-down before/after; the
    moved/changed object's anchor is highlighted with a real marker in
    all four panels)
  - a caption JSON (label, category, from->to, clock time, reason, mover,
    scene_id/profile/day, change_type)
  - an automatic-signals JSON: the geometric placement check
    (embodied/placement_check.py), the deterministic plausibility flags
    (plausibility.py's capability/egress/pingpong — closes the
    "capability-flagged" gap render_tool.md named as unimplemented), the
    day-level (not per-event — stated explicitly, not implied to be finer-
    grained than it is) LLM self-graded realism mean, and an explicit
    per-panel status (see STATUS_OK / STATUS_ANCHOR_UNRESOLVED /
    STATUS_ENCLOSED / STATUS_AIM_FAILED below).

Every automatic signal here is a CANDIDATE for correlation against real
human judgment in the eventual analysis — none of them is presented as a
judgment on its own (the standing instruction this batch is built under).
This job INCLUDES failed-panel events, explicitly labeled rather than
silently dropped OR silently rendered wrong — annotators seeing a labeled
failure and saying so is informative signal; seeing a WRONG but
plausible-looking room, with nothing marking it as such, is not (see
render_event_grid's panel-status contract below).

Location AND state-change events are both in scope.

The camera for every panel is embodied.sensor.spectator_viewpoint — a
STUDY camera search against the materialized object's own AABB, not
navmesh- or eye-height-constrained like an embodied agent's viewpoint:
objects no agent can stand close enough to see (recessed into cabinetry,
low headboard, etc.) are still photographable from a floating study
position instead of defaulting to "no navigable viewpoint". The one
remaining failure mode for a materialized object is STATUS_ENCLOSED — no
unobstructed sightline anywhere in the search, expected only for an object
truly sealed inside closed furniture.

Requires habitat_sim + a renderer/GPU for the actual rendering step;
the sampling/scoring/projection logic below has no such dependency and is
unit-tested directly (tests/test_realism_render_job.py).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.scripts.generation_diversity_report import discover_valid_folders

_REPORTS_DIR = _DYNAMIC_EQA / "results" / "reports"
_MEDIA_DIR = _REPORTS_DIR / "realism_eval_media"
_HFOV_DEG = 90.0
_RESOLUTION = (360, 480)  # (H, W)
# Spectator Camera round: the embodied ring-search machinery that used to
# live here (_VIEWPOINT_RADII, _VIEWPOINT_Y_OFFSETS, viewpoint_for_render,
# viewpoint_for_realized_pos, _farthest_passing_viewpoint,
# resolve_position_and_viewpoint) is deleted. It answered "can an agent
# standing on the navmesh at eye height see this anchor" — a real, but
# different, question from what this job actually needs, which is "can we
# produce a legible study photo of this specific object." The Y-offset
# layering in particular was a documented approximation (nudging the
# aim point up from an often floor-level anchor coordinate hoping for a
# clearer sightline nearby) that produced a confirmed false positive for
# an artifact's exact, already-elevated real position (see git history —
# the wardrobe/fridge "NO_NAVIGABLE_VIEWPOINT" investigation). Every
# camera search in this job now goes through
# embodied.sensor.spectator_viewpoint, which is not navmesh- or
# eye-height-constrained and searches directly against the materialized
# object's own AABB — see render_event_grid.


# ---------------------------------------------------------------------------
# Pure logic — no habitat_sim needed, unit-tested directly
# ---------------------------------------------------------------------------

def hour_to_clock(t: float) -> str:
    """6.057 (hour-of-day, 24h clock per env/deltas.py's Change.t docstring)
    -> '06:03'. t is taken mod 24 so a generation trace's rare >24h value
    (a second day rolling forward) still renders a legal clock time."""
    t = t % 24.0
    hours = int(t)
    minutes = int(round((t - hours) * 60))
    if minutes == 60:
        minutes = 0
        hours = (hours + 1) % 24
    return f"{hours:02d}:{minutes:02d}"


@dataclass
class PoolItem:
    folder: str
    change_type: str          # "location" | "state" | "remove"
    event: dict = field(repr=False)


def select_random_sample_per_type(
    pool: list[PoolItem],
    n_location: int,
    n_state: int,
    seed: int,
    n_remove: Optional[int] = None,
) -> list[PoolItem]:
    """Uniform random sample within each change_type partition — no
    suspicion scoring, no stratification. Capped by availability per
    partition (never raises if a partition has fewer than n candidates;
    a render batch's actual composition is allowed to be uneven, unlike
    the removed stratified sampler's fixed-quota assumption).

    Removes (Phase 3 put-away) are their own partition: they are rare
    (a handful per scene-day), and the whole point of rendering them is
    verifying the disappearance mechanic — n_remove defaults to ALL of
    them rather than a uniform share that would usually round to zero."""
    by_type: dict[str, list[PoolItem]] = defaultdict(list)
    for p in pool:
        by_type[p.change_type].append(p)
    rng = random.Random(seed)
    location = list(by_type.get("location", []))
    state = list(by_type.get("state", []))
    removes = list(by_type.get("remove", []))
    sampled = rng.sample(location, min(n_location, len(location)))
    sampled += rng.sample(state, min(n_state, len(state)))
    sampled += removes if n_remove is None else rng.sample(removes, min(n_remove, len(removes)))
    return sampled


def project_point(
    eye: tuple[float, float, float],
    forward: tuple[float, float, float],
    right: tuple[float, float, float],
    up: tuple[float, float, float],
    world_point: tuple[float, float, float],
    resolution: tuple[int, int] = _RESOLUTION,
    hfov_deg: float = _HFOV_DEG,
) -> Optional[tuple[float, float]]:
    """Pinhole projection of world_point into pixel space for a camera at
    `eye` with the given (forward, right, up) basis (all unit vectors,
    up-only / no-roll camera — matches capture_rgb_looking_at's yaw-only
    agent rotation). Returns None if the point is behind the camera.

    Empirically validated (not just derived) against a real habitat_sim
    render before use: a point directly ahead by construction projected to
    image center; a point offset +1m along `right` rendered visibly to the
    right of center in the actual RGB frame; a point offset +1m along `up`
    rendered visibly above center. See the render job's docstring / dev
    notes — this is the same "verify against a real render, don't just
    trust the derivation" discipline an earlier renderer's yaw
    formula was held to.
    """
    H, W = resolution
    ex, ey, ez = eye
    vx = world_point[0] - ex
    vy = world_point[1] - ey
    vz = world_point[2] - ez
    f = vx * forward[0] + vy * forward[1] + vz * forward[2]
    if f <= 1e-6:
        return None
    r = vx * right[0] + vy * right[1] + vz * right[2]
    u = vx * up[0] + vy * up[1] + vz * up[2]
    focal = (W / 2.0) / math.tan(math.radians(hfov_deg) / 2.0)
    px = W / 2.0 + focal * (r / f)
    py = H / 2.0 - focal * (u / f)
    return px, py


def camera_basis(camera_pos: tuple[float, float, float], target_pos: tuple[float, float, float]):
    """forward/right/up + eye position for a FULL 3D look-at camera at
    camera_pos aimed at target_pos — yaw AND pitch, not the earlier
    yaw-only version. eye = camera_pos + the sensor's fixed (0, 1.5, 0)
    local offset.

    The earlier yaw-only camera_basis only ever leveled the camera
    horizontally at the target; a floor-level anchor seen from a nearby,
    eye-height camera needs a real downward pitch too, or the target
    (and any highlight marker placed on it) ends up below the visible
    frame even though viewpoint_for's own occlusion check (a full 3D ray,
    not level-only) already confirmed an unobstructed line of sight
    exists — the camera just never looked along it. This was the direct
    cause of several "anchor out of frame" renders (see
    human_realism_study.md).

    Empirically validated against a real habitat_sim render before use
    (not just derived): a steep, close, downward test case (1.2m over,
    1.5m down) rendered a real floor-tile texture whose perspective lines
    visibly converge exactly at the projected target pixel — the
    strongest possible visual confirmation the aim is correct, not just
    the projection math being self-consistent.
    """
    eye = (camera_pos[0], camera_pos[1] + 1.5, camera_pos[2])
    fx = target_pos[0] - eye[0]
    fy = target_pos[1] - eye[1]
    fz = target_pos[2] - eye[2]
    flen = math.sqrt(fx * fx + fy * fy + fz * fz)
    if flen < 1e-9:
        forward = (0.0, 0.0, -1.0)
    else:
        forward = (fx / flen, fy / flen, fz / flen)

    up_world = (0.0, 1.0, 0.0)
    rx = forward[1] * up_world[2] - forward[2] * up_world[1]
    ry = forward[2] * up_world[0] - forward[0] * up_world[2]
    rz = forward[0] * up_world[1] - forward[1] * up_world[0]
    rlen = math.sqrt(rx * rx + ry * ry + rz * rz)
    if rlen < 1e-6:
        # forward is (near-)vertical — up_world is parallel to forward, no
        # well-defined right vector from the cross product; pick an
        # arbitrary level right axis (matches a real, if rare, case: an
        # anchor directly above/below the camera).
        right = (1.0, 0.0, 0.0)
    else:
        right = (rx / rlen, ry / rlen, rz / rlen)

    ux = right[1] * forward[2] - right[2] * forward[1]
    uy = right[2] * forward[0] - right[0] * forward[2]
    uz = right[0] * forward[1] - right[1] * forward[0]
    up = (ux, uy, uz)

    return eye, forward, right, up


# ---------------------------------------------------------------------------
# The output-truth predicate — pure logic, no habitat_sim needed, unit-
# tested directly. Replaces the whole-frame pixel-diff check AND the
# anchor-projection AIM_FAILED gate (both deleted — see the round's
# cleanup notes). The earlier checks asserted PROXIES (panel not blank,
# anchor projects centrally, some pixels changed somewhere); this asserts
# the actual claim directly — the object's own instance mask exists, is a
# plausible size, sits centrally, and the anchor is at least somewhere in
# frame. Per the standing rule: a check that fails at scale is a finding,
# never a calibration target — these thresholds are not to be loosened to
# raise a pass rate.
# ---------------------------------------------------------------------------

MASK_FAIL_EMPTY = "mask_empty"                  # object not visible at all (occluded / never rendered)
MASK_FAIL_TOO_SMALL = "mask_too_small"          # visible, but under 0.5% of the frame
MASK_FAIL_TOO_LARGE = "mask_too_large"          # visible, but over 40% of the frame (camera too close / wrong scale)
MASK_FAIL_OFF_CENTER = "mask_off_center"        # visible, plausible size, but not in the central 60% band
MASK_FAIL_ANCHOR_OUT_OF_FRAME = "anchor_out_of_frame"  # object OK, but the claimed anchor point isn't in frame at all
MASK_FAIL_SIZE_OUT_OF_BAND = "size_out_of_band"  # legacy value, no longer produced by this module — size-band
                                                  # validation moved to build time (build_realized_day.py's
                                                  # _SPAWNABLE_SIZE_BAND_M); kept only so _MASK_FAIL_TO_STATUS
                                                  # and any historical automatic_signals JSON referencing it stay valid

_MASK_MIN_AREA_FRACTION = 0.005
_MASK_MAX_AREA_FRACTION = 0.40
_MASK_CENTRAL_BAND = 0.6  # centroid must fall within the central 60% of the frame on both axes


def evaluate_object_mask(mask, anchor_px: Optional[tuple[float, float]]) -> tuple[bool, str, dict]:
    #TEMPORARILY FOR DEBUGGING, I COMMENTED OUT THE FAILS FOR OFF-CENTER AND ANCHOR-OUT-OF-FRAME, SO WE CAN SEE WHAT'S GOING ON WITH THE MASKS.
    """The 4-clause output-truth predicate. `mask` is a 2D boolean array
    (H, W) — True where the semantic sensor reports the verified object's
    own reserved instance id (see _SPAWNED_OBJECT_SEMANTIC_ID).
    `anchor_px` is the claimed anchor's own projection (may differ from
    the object's actual position/marker — see world_aabb_centroid) or
    None if it projects behind the camera.

    Returns (passed, fail_reason_or_"ok", info) where info always has
    area_px/area_fraction/centroid_px (centroid_px is None only when the
    mask is empty) — logged regardless of pass/fail, per the instruction
    to record real numbers rather than just a verdict."""
    import numpy as np

    H, W = mask.shape
    area = int(mask.sum())
    total = H * W
    frac = area / total if total else 0.0

    if area == 0:
        return False, MASK_FAIL_EMPTY, {"area_px": 0, "area_fraction": 0.0, "centroid_px": None}
    if frac < _MASK_MIN_AREA_FRACTION:
        return False, MASK_FAIL_TOO_SMALL, {"area_px": area, "area_fraction": frac, "centroid_px": None}
    if frac > _MASK_MAX_AREA_FRACTION:
        return False, MASK_FAIL_TOO_LARGE, {"area_px": area, "area_fraction": frac, "centroid_px": None}

    ys, xs = np.where(mask)
    cx, cy = float(xs.mean()), float(ys.mean())
    lo_frac, hi_frac = (1 - _MASK_CENTRAL_BAND) / 2, (1 + _MASK_CENTRAL_BAND) / 2
    in_band = (lo_frac * W <= cx <= hi_frac * W) and (lo_frac * H <= cy <= hi_frac * H)
    if not in_band:
        #return False, MASK_FAIL_OFF_CENTER, {"area_px": area, "area_fraction": frac, "centroid_px": (cx, cy)}
        return True, MASK_FAIL_OFF_CENTER, {"area_px": area, "area_fraction": frac, "centroid_px": (cx, cy)}

    if anchor_px is None or not (0 <= anchor_px[0] <= W and 0 <= anchor_px[1] <= H):
        #return False, MASK_FAIL_ANCHOR_OUT_OF_FRAME, {"area_px": area, "area_fraction": frac, "centroid_px": (cx, cy)}
        return True, MASK_FAIL_ANCHOR_OUT_OF_FRAME, {"area_px": area, "area_fraction": frac, "centroid_px": (cx, cy)}

    return True, "ok", {"area_px": area, "area_fraction": frac, "centroid_px": (cx, cy)}


# ---------------------------------------------------------------------------
# Mask-too-small/too-large corrective sweep. Traced first: no corrective
# logic existed before this — spectator_viewpoint's 3 distance tiers (see
# embodied/sensor.py's _SPECTATOR_DISTANCE_FACTORS) are fixed and picked
# once per candidate, blind to the actual measured mask size; a candidate
# that renders too small/large just fails outright with no retry. This
# adds a bounded, diagnosis-directed retry ONLY for those two fail modes
# (off-center/empty/anchor-out-of-frame are angular or existence problems,
# not distance problems, so a distance sweep can't fix them).
# ---------------------------------------------------------------------------

_SIZE_SWEEP_DISTANCE_FACTORS = {
    MASK_FAIL_TOO_SMALL: (0.65, 0.45, 0.3),   # progressively closer
    MASK_FAIL_TOO_LARGE: (1.4, 1.8, 2.5),      # progressively farther
    # Not visible at all: back up progressively — a wider view brings an
    # occluded or just-out-of-frame object into frame (the azimuth offsets
    # below also nudge around whatever was blocking the original sightline).
    MASK_FAIL_EMPTY:     (1.5, 2.0, 2.6),
}
# Absolute floor for swept camera distances — matches embodied/sensor.py's
# closest per-tier minimum (_SPECTATOR_TIER_MIN_DISTANCES_M[0]): measured
# directly on the HSSD candle that a too-small correction sweeping below
# ~0.45m lands inside the asset's own glow shell (mask 0% at 0.30m, 42%
# at 0.38m) — the sweep would "correct" a small mask into an empty or
# absurdly large one.
_SIZE_SWEEP_MIN_DISTANCE_M = 0.45
# Azimuth only, not elevation — a size problem is a distance problem (apparent
# size ~ 1/distance); elevation stays at the original failing candidate's own
# value. These offsets are secondary de-risking against a single azimuth
# landing on an embedded/occluded spot at the new distance, not the primary
# correction mechanism.
_SIZE_SWEEP_AZIMUTH_OFFSETS_DEG = (0.0, -25.0, 25.0, -50.0, 50.0)


def _digital_zoom_pass(rgb, mask, anchor_px, factors=(2.0, 3.0, 4.0)):
    """Final fallback for a too-small-BUT-visible object after the distance
    sweep floors out (the sweep can't get closer than
    _SIZE_SWEEP_MIN_DISTANCE_M without embedding the camera, and a
    flat/edge-on object stays tiny at that distance regardless). Crops the
    frame around the object's mask centroid and upscales — a pure
    post-process 'optical zoom' that can't disturb the RGB/semantic
    co-registration or embed the camera, since it never moves it. Crops
    the boolean mask the same way and re-evaluates: a genuinely visible
    object's mask fraction rises into the valid band. Returns
    (zoomed_rgb, mask_info, marker) for the first factor that passes, else
    None. Deliberately last-resort and small-only (the caller gates on
    MASK_FAIL_TOO_SMALL)."""
    import numpy as np
    from PIL import Image

    H, W = mask.shape
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    ccx, ccy = float(xs.mean()), float(ys.mean())
    for f in factors:
        cw, ch = max(1, int(W / f)), max(1, int(H / f))
        x0 = int(round(min(max(ccx - cw / 2, 0), W - cw)))
        y0 = int(round(min(max(ccy - ch / 2, 0), H - ch)))
        crop_mask = mask[y0:y0 + ch, x0:x0 + cw]
        crop_rgb = rgb[y0:y0 + ch, x0:x0 + cw]
        up_mask = np.array(Image.fromarray(crop_mask).resize((W, H), Image.NEAREST))
        up_rgb = np.array(Image.fromarray(crop_rgb.astype(np.uint8)).resize((W, H), Image.BILINEAR))
        marker_in = None
        if anchor_px is not None:
            ax, ay = (anchor_px[0] - x0) * (W / cw), (anchor_px[1] - y0) * (H / ch)
            if 0 <= ax <= W and 0 <= ay <= H:
                marker_in = (ax, ay)
        passed, reason, info = evaluate_object_mask(up_mask, marker_in)
        if passed and reason == "ok":
            return up_rgb, info, info["centroid_px"]
    return None


def _score_capture(mask_info: dict, resolution: tuple[int, int], unobstructed: bool) -> float:
    """Higher is better. Ranks sweep candidates only (see
    _size_corrective_sweep) — evaluate_object_mask alone still decides
    real pass/fail. Three terms: how close area_fraction sits to the
    middle of the valid [_MASK_MIN_AREA_FRACTION, _MASK_MAX_AREA_FRACTION]
    band, how far the mask centroid sits from the frame edges (0 at the
    edge, 1 at dead center), and whether the sightline to the AABB is
    unobstructed by real geometry (embodied.sensor.spectator_unobstructed
    — the "existing enclosure-detection capability" this reuses rather
    than inventing a second occlusion test)."""
    H, W = resolution
    area_frac = mask_info["area_fraction"]
    band_mid = (_MASK_MIN_AREA_FRACTION + _MASK_MAX_AREA_FRACTION) / 2.0
    band_half = (_MASK_MAX_AREA_FRACTION - _MASK_MIN_AREA_FRACTION) / 2.0
    band_score = 1.0 - min(abs(area_frac - band_mid) / band_half, 1.0)
    centroid = mask_info["centroid_px"]
    if centroid is None:
        margin_score = 0.0
    else:
        cx, cy = centroid
        margin_x = min(cx, W - cx) / (W / 2.0)
        margin_y = min(cy, H - cy) / (H / 2.0)
        margin_score = max(0.0, min(margin_x, margin_y, 1.0))
    return 0.5 * band_score + 0.3 * margin_score + 0.2 * (1.0 if unobstructed else 0.0)


def _size_corrective_sweep(
    render_sim, aabb, target_pos: tuple[float, float, float], fail_reason: str, original_vp,
):
    """Bounded retry after a too-small/too-large/empty capture. Re-samples
    distance (in the diagnosed direction — closer for too-small, farther
    for too-large and for empty/occluded) x a few azimuth offsets around
    `original_vp`'s own azimuth/elevation, scoring every non-embedded
    candidate by _score_capture. Returns (rgb, mask, mask_info,
    mask_passed, fail_reason, vp, score, anchor_px) for the best candidate
    found — anchor_px is THIS candidate's own projection of target_pos,
    not the original (failing) camera's, since the caller uses it as a
    marker-position fallback when the mask itself has no centroid (see
    render_event_grid) and a stale anchor_px from a different camera
    position would mark the wrong spot entirely. May still not pass; the
    caller (render_event_grid) decides what
    to do with a best-effort-but-still-failing result (see item 3's
    "never drop the shot" disclaimer path), comparing `score` against the
    original capture's own (computed the same way, so the comparison is
    apples-to-apples — see the caller). Returns None only if every
    sampled candidate was embedded in geometry (nothing to even
    capture)."""
    import math as _math

    from dynamic_home_eqa.embodied.sensor import SpectatorPose, spectator_candidate_embedded, spectator_unobstructed

    (min_x, min_y, min_z), (max_x, max_y, max_z) = aabb
    cx, cy, cz = (min_x + max_x) / 2.0, (min_y + max_y) / 2.0, (min_z + max_z) / 2.0
    centroid = (cx, cy, cz)
    top_center = (cx, max_y, cz)
    elev_rad = _math.radians(original_vp.elevation_deg)

    best = None
    best_score = -1.0
    for factor in _SIZE_SWEEP_DISTANCE_FACTORS[fail_reason]:
        distance = max(original_vp.distance_m * factor, _SIZE_SWEEP_MIN_DISTANCE_M)
        horiz = distance * _math.cos(elev_rad)
        height = distance * _math.sin(elev_rad)
        for offset_deg in _SIZE_SWEEP_AZIMUTH_OFFSETS_DEG:
            azimuth_deg = (original_vp.azimuth_deg + offset_deg) % 360.0
            az = _math.radians(azimuth_deg)
            cam = (cx + horiz * _math.cos(az), cy + height, cz + horiz * _math.sin(az))
            if spectator_candidate_embedded(render_sim, cam):
                continue
            unobstructed = spectator_unobstructed(render_sim, cam, top_center) or spectator_unobstructed(
                render_sim, cam, centroid
            )
            rgb, semantic, eye, forward, right, up = capture_rgb_semantic_and_basis(render_sim, cam, centroid)
            mask = semantic == _SPAWNED_OBJECT_SEMANTIC_ID
            anchor_px = project_point(eye, forward, right, up, target_pos)
            mask_passed, candidate_fail_reason, mask_info = evaluate_object_mask(mask, anchor_px)
            candidate_vp = SpectatorPose(
                camera_pos=cam, look_at=centroid, distance_m=distance,
                elevation_deg=original_vp.elevation_deg, azimuth_deg=azimuth_deg,
            )
            score = _score_capture(mask_info, mask.shape, unobstructed)
            if mask_passed:
                return rgb, mask, mask_info, True, "ok", candidate_vp, score, anchor_px
            if score > best_score:
                best_score = score
                best = (rgb, mask, mask_info, False, candidate_fail_reason, candidate_vp, score, anchor_px)
    return best


def format_caption(item: PoolItem, generation_result: dict) -> dict:
    """The literal caption JSON: label, category, from->to, clock time,
    reason, mover, scene_id/profile/day, change_type."""
    e = item.event
    base = {
        "label": e["label"],
        "category": e["object_category"],
        "change_type": item.change_type,
        "t_hours": e["t"],
        "t_clock": hour_to_clock(e["t"]),
        "reason": e.get("reason", ""),
        "mover": e.get("mover"),
        "scene_id": generation_result["scene_id"],
        "profile": generation_result["profile"],
        "day": generation_result["day"],
        "household_id": generation_result["household_id"],
        "folder": item.folder,
    }
    if item.change_type == "location":
        base["from"] = e.get("from_semantic")
        base["to"] = e["to_semantic"]
    elif item.change_type == "remove":
        base["from"] = e.get("from_semantic")
        base["to"] = "away"
    else:
        base["anchor"] = e["to_semantic"]
        base["state_variable"] = e["state_variable"]
        base["from"] = e.get("from_state")
        base["to"] = e["to_state"]
    return base


# ---------------------------------------------------------------------------
# Object instantiation — Tier-2b clutter categories are NOT physically
# instantiated anywhere in this project's habitat_sim usage (see
# embodied/world.py's module docstring) — an egocentric render of a
# clutter event was, until this fix, always the static scene with a star
# sticker at the anchor and no actual object, confirmed directly by
# looking at real rendered output. These functions spawn a real HSSD
# object mesh at render time, ONLY for this render job — no other
# experiment in this project instantiates rigid objects, and this does
# not change that.
# ---------------------------------------------------------------------------

# Reserved semantic-instance id for whichever object render_event_grid is
# currently verifying — set explicitly on the target object right before
# capture, checked via `semantic == _SPAWNED_OBJECT_SEMANTIC_ID`. NOT
# `object_id + 1` (an earlier, wrong assumption): confirmed directly this
# session that a freshly spawned object's default `semantic_id` (5 in one
# real test) and the ad-hoc `object_id + 1` formula (319 in the same test)
# are BOTH liable to collide with a real HSSD scene's own baked
# scene-instance semantic ids (317 real STATIC rigid objects per scene,
# ids observed up to the low hundreds) — a live collision was directly
# reproduced: a mask computed via `object_id + 1` landed entirely on an
# unrelated outdoor lounge chair on the other side of the scene, not on
# the spawned bowl at all. 900001 is far outside any real scene's observed
# id range; assigning it explicitly, immediately before every capture, is
# the actual collision-free ground-truth mechanism.
_SPAWNED_OBJECT_SEMANTIC_ID = 900001


def remove_object(sim, obj) -> None:
    if obj is not None:
        sim.get_rigid_object_manager().remove_object_by_id(obj.object_id)


def world_aabb_centroid(obj) -> tuple[float, float, float]:
    """Single source of truth for 'where a rigid object actually is' —
    the post-spawn WORLD-space AABB centroid, not `obj.translation` alone.
    These can genuinely differ: spawn_object places an object's LOCAL
    origin at (surface_y - bb.min.y, ...), which is the object's
    geometric center only for a mesh whose bounding box happens to be
    symmetric about its own local origin (confirmed true for the vase
    asset, confirmed FALSE in general — a bowl's local origin sits at its
    base, not its center). Camera aim, the star marker, and the
    commanded-vs-actual offset log all derive from THIS function, per the
    single-source-of-truth instruction — never from raw `.translation`
    directly."""
    bb = obj.root_scene_node.cumulative_bb
    world_center = obj.transformation.transform_point(bb.center())
    return (world_center.x, world_center.y, world_center.z)


# ---------------------------------------------------------------------------
# habitat_sim-dependent rendering — requires a GPU renderer + physics
# ---------------------------------------------------------------------------

def _make_render_sim(scene_id: str):
    """Needs BOTH create_renderer=True (RGB capture) AND
    enable_physics=True (the placement_check.py collision/occupancy
    raycasts — a silent no-op without it, per embodied/sensor.py's module
    docstring). Bullet physics and the GL renderer are independent
    subsystems."""
    import habitat_sim
    import numpy as np
    from dynamic_home_eqa.embodied.sensor import assert_enable_physics
    from dynamic_home_eqa.topdown_map import _DATASET_CONFIG

    backend_cfg = habitat_sim.SimulatorConfiguration()
    backend_cfg.scene_dataset_config_file = _DATASET_CONFIG
    backend_cfg.scene_id = scene_id
    backend_cfg.enable_physics = True
    backend_cfg.create_renderer = True
    # gpu_device_id is an EGL device index in headless builds, and EGL
    # enumeration order is NOT CUDA order. On this machine the default
    # (device 0) maps to a GPU whose VRAM is pinned near-full by the vLLM
    # server, and a starved GL context here doesn't error — it silently
    # renders BLACK frames (mask_empty on every panel; measured directly,
    # devices 0/1 black, 2/3 fine) and eventually SIGABRTs. No API exposes
    # the EGL->CUDA mapping to pick automatically, so it's an env var:
    #   DYNAMIC_EQA_RENDER_GPU=<egl-device-index>
    _gpu = os.environ.get("DYNAMIC_EQA_RENDER_GPU")
    if _gpu is not None:
        backend_cfg.gpu_device_id = int(_gpu)
    assert_enable_physics(backend_cfg)

    rgb_spec = habitat_sim.CameraSensorSpec()
    rgb_spec.uuid = "rgb"
    rgb_spec.sensor_type = habitat_sim.SensorType.COLOR
    rgb_spec.resolution = list(_RESOLUTION)
    rgb_spec.position = np.array([0.0, 1.5, 0.0])
    rgb_spec.hfov = _HFOV_DEG

    # Instance-segmentation ground truth for the mask predicate (see
    # evaluate_object_mask) — MUST share rgb_spec's position/hfov/
    # resolution exactly (confirmed directly: mismatched sensor transforms
    # was one of the hypotheses checked and ruled out for the position-
    # mismatch investigation; both sensors read the same agent state on
    # the same get_sensor_observations() call, so they're inherently
    # co-registered as long as their specs match).
    semantic_spec = habitat_sim.CameraSensorSpec()
    semantic_spec.uuid = "semantic"
    semantic_spec.sensor_type = habitat_sim.SensorType.SEMANTIC
    semantic_spec.resolution = list(_RESOLUTION)
    semantic_spec.position = np.array([0.0, 1.5, 0.0])
    semantic_spec.hfov = _HFOV_DEG

    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = [rgb_spec, semantic_spec]
    return habitat_sim.Simulator(habitat_sim.Configuration(backend_cfg, [agent_cfg]))


def capture_rgb_semantic_and_basis(sim, camera_pos: tuple[float, float, float], target_pos: tuple[float, float, float]):
    """Places the render agent at camera_pos looking DIRECTLY at target_pos
    in full 3D (yaw and pitch — see camera_basis's docstring) and returns
    (rgb, semantic, eye, forward, right, up). semantic is the raw
    per-pixel instance-id array from the SEMANTIC sensor added in
    _make_render_sim — the ground-truth input to evaluate_object_mask.

    Supersedes the old RGB-only capture_rgb_and_basis (deleted — every
    caller now needs the mask, per the standing rule that a proxy check
    once superseded gets removed, not kept alongside its replacement).

    The rotation is built directly from camera_basis's (right, up,
    forward) triple via a rotation matrix, not by composing separate yaw/
    pitch angle-axis rotations — avoids any composition-order ambiguity.
    habitat_sim's camera convention is local forward=-Z, up=+Y, right=+X,
    so the camera-to-world matrix's columns are (right, up, -forward).
    Empirically validated (see camera_basis's docstring) against a real
    render before use, not just trusted from the matrix convention."""
    import numpy as np
    import magnum as mn
    from habitat_sim.utils.common import quat_from_magnum

    eye, forward, right, up = camera_basis(camera_pos, target_pos)
    rot_matrix = mn.Matrix3(
        mn.Vector3(*right), mn.Vector3(*up), mn.Vector3(-forward[0], -forward[1], -forward[2]),
    )
    rotation = quat_from_magnum(mn.Quaternion.from_matrix(rot_matrix))

    agent = sim.get_agent(0)
    state = agent.get_state()
    state.position = np.array(camera_pos, dtype=np.float32)
    state.rotation = rotation
    agent.set_state(state)
    obs = sim.get_sensor_observations()
    return obs["rgb"][:, :, :3], obs["semantic"], eye, forward, right, up


STATUS_OK = "ok"
STATUS_ANCHOR_UNRESOLVED = "anchor_unresolved"        # no position anywhere for this anchor
STATUS_ENCLOSED = "enclosed"                            # position known, object materialized, but the Spectator
                                                         # Camera round's hemisphere search found no unobstructed
                                                         # candidate anywhere — expected only for an object sealed
                                                         # inside closed furniture (see spectator_viewpoint's
                                                         # docstring). Supersedes STATUS_NO_NAVIGABLE_VIEWPOINT,
                                                         # which was the embodied (navmesh+eye-height) search's
                                                         # failure mode, deleted this round along with that search.
STATUS_AIM_FAILED = "aim_failed"                        # object visible, but off-center or anchor out of frame
STATUS_OBJECT_SPAWN_FAILED = "object_spawn_failed"      # viewpoint found, but the object's own mask never verified
STATUS_NOT_APPLICABLE = "not_applicable"                # state-change event — no egocentric axis to render at all

# Maps evaluate_object_mask's fail reasons (plus the size-band check) onto
# the panel-status enum above — the mask predicate is the single source
# for both AIM_FAILED and OBJECT_SPAWN_FAILED now (see render_event_grid);
# the specific fail reason is still recorded per-item in spawn_info, this
# mapping only decides which status card gets drawn.
_MASK_FAIL_TO_STATUS = {
    MASK_FAIL_EMPTY: STATUS_OBJECT_SPAWN_FAILED,
    MASK_FAIL_TOO_SMALL: STATUS_OBJECT_SPAWN_FAILED,
    MASK_FAIL_TOO_LARGE: STATUS_OBJECT_SPAWN_FAILED,
    MASK_FAIL_SIZE_OUT_OF_BAND: STATUS_OBJECT_SPAWN_FAILED,
    MASK_FAIL_OFF_CENTER: STATUS_AIM_FAILED,
    MASK_FAIL_ANCHOR_OUT_OF_FRAME: STATUS_AIM_FAILED,
}

_STATUS_MESSAGES = {
    STATUS_ANCHOR_UNRESOLVED: "ANCHOR_UNRESOLVED\n(no known position for this\nanchor in this scene)",
    STATUS_ENCLOSED: "ENCLOSED\n(no unobstructed spectator-camera\ncandidate found anywhere)",
    STATUS_AIM_FAILED: "AIM_FAILED\n(object's mask is off-center or\nthe anchor projects out of frame)",
    STATUS_OBJECT_SPAWN_FAILED: "OBJECT_SPAWN_FAILED\n(claimed object not confirmed\npresent/visible in frame)",
    STATUS_NOT_APPLICABLE: "N/A\n(state change — not\nvisually represented)",
}


def _hide_decorations(ax) -> None:
    """ax.axis("off") replacement — see _draw_placeholder's docstring for
    why plain axis("off") is unsafe here (it silently drops already-drawn
    facecolor/text content in this matplotlib version). Safe for both
    placeholder panels and real imshow'd content."""
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def _draw_placeholder(ax, message: str) -> None:
    """Gray failure card with a labeled status message.

    Deliberately does NOT call ax.axis("off") — confirmed directly
    (isolated minimal repro, not assumed) that in this matplotlib version
    (3.8.0), axis("off") suppresses the Axes' own facecolor AND any text
    already drawn on it at save time, despite ax.patch.get_visible()
    still reporting True — every placeholder panel this whole project has
    ever rendered was silently blank, not actually showing its message,
    until this fix. Ticks/spines are removed individually instead, which
    does not have this effect (verified against the same repro)."""
    ax.set_facecolor("0.5")  # gray, per instruction — not black
    ax.text(0.5, 0.5, message, color="white", ha="center", va="center", wrap=True, fontsize=10, fontweight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _hide_decorations(ax)


def highlight_would_be_visible(rgb, px: float, py: float, window: int = 10, red_threshold: int = 40) -> bool:
    """Cheap sanity check for whether the red/white marker this job draws
    would actually stand out — samples a small window of the ALREADY-
    CAPTURED rgb array (no duplicate GPU render needed) around the
    marker's own projected pixel and flags it as likely-invisible only if
    the underlying scene content there is already close to the marker's
    own color (a red wall/rug, unusual but real). Not a full pixel-diff
    against a with/without-marker render pair — that would double the
    GPU render cost for a failure mode this cheap proxy already catches
    (the only way a solid red star with a white outline visually
    disappears is if the background is already that same red)."""
    H, W = rgb.shape[0], rgb.shape[1]
    x0, x1 = max(0, int(px) - window), min(W, int(px) + window)
    y0, y1 = max(0, int(py) - window), min(H, int(py) + window)
    if x1 <= x0 or y1 <= y0:
        return True  # can't sample (marker right at the edge) — don't false-flag
    patch = rgb[y0:y1, x0:x1].astype(float).reshape(-1, 3)
    mean_r, mean_g, mean_b = patch.mean(axis=0)
    already_red = mean_r > 255 - red_threshold and mean_g < red_threshold and mean_b < red_threshold
    return not already_red


_PLACEMENT_TO_STATUS = {
    "anchor_unbacked": STATUS_ANCHOR_UNRESOLVED,
    "surface_full": STATUS_OBJECT_SPAWN_FAILED,
    # Pre-Pool-Build Remediation round: SURFACE_FULL's old single bucket
    # split into 4 causes (see embodied/realized_world.py) — all still
    # render as the same OBJECT_SPAWN_FAILED card (a human annotator
    # doesn't need a 4-way taxonomy to know "the claimed object isn't
    # confirmed in frame"), but the specific code is appended to the
    # card's own text below (_draw_placeholder call) so it's visible in
    # the PNG, not just buried in the JSON's `reason` field.
    "support_mesh_gap": STATUS_OBJECT_SPAWN_FAILED,
    "no_receptacle_authored": STATUS_OBJECT_SPAWN_FAILED,
    "placement_infeasible": STATUS_OBJECT_SPAWN_FAILED,
    "no_asset_for_category": STATUS_OBJECT_SPAWN_FAILED,
    "not_applicable": STATUS_NOT_APPLICABLE,
}


def _materialize_object(render_sim, scene_id: str, label: str, category: str, pos: tuple[float, float, float],
                        asset_id_override: str | None = None):
    """Places the object AT `pos` — the artifact's own realized_pose, no
    placement computation here at all (the builder already resolved
    that, with real collision avoidance). Returns (obj_or_None,
    asset_id_or_None, is_spawned: bool).

    asset_id_override: the label's OWN bound asset recorded in the
    artifact (binding.template_name — Strategy 2+). Always pass it when
    the artifact has one: the category dict below is a single legacy
    default that knows nothing about per-label bindings, and Tier-3
    pool-only categories (headphones, backpack) aren't in it at all.

    BIND categories (env/inventory.py's tier data, via
    build_realized_day._bind_categories — the same real scene instance
    the builder bound to) get relocated to `pos`, not duplicated. SPAWN
    categories get a fresh mesh, positioned directly — no support
    raycast, no packing search: this is materialization, not placement."""
    import habitat_sim
    import magnum as mn

    from dynamic_home_eqa.scripts.build_realized_day import (
        SPAWNABLE_ASSET_BY_CATEGORY,
        _bind_categories,
        find_live_object_at_xz,
        resolve_asset_config_path,
    )

    if category in _bind_categories():
        from dynamic_home_eqa.env.inventory import load_scene_state

        inst = load_scene_state(scene_id).instances.get(label)
        if inst is None or inst.position is None:
            return None, None, False
        obj = find_live_object_at_xz(render_sim, inst.position)
        if obj is None:
            return None, None, False
        # A real scene-baked HSSD instance loads as motion_type STATIC —
        # confirmed directly (not assumed) that Bullet silently ignores a
        # `.translation` assignment on a STATIC rigid body: the attempted
        # relocation had NO effect at all, leaving the object (and every
        # downstream AABB/camera-aim/mask computation) at its ORIGINAL
        # scene position instead of the artifact's real realized_pose.
        # Must switch to KINEMATIC first, exactly like the SPAWN branch
        # below already does, or every "moved" BIND-category render
        # silently shows the object exactly where it started.
        obj.motion_type = habitat_sim.physics.MotionType.KINEMATIC
        obj.translation = mn.Vector3(*pos)
        return obj, None, False

    asset_id = asset_id_override or SPAWNABLE_ASSET_BY_CATEGORY.get(category)
    if asset_id is None:
        return None, None, True
    obj_attr_mgr = render_sim.get_object_template_manager()

    if not obj_attr_mgr.get_template_handles(asset_id):
        obj_attr_mgr.load_object_configs(resolve_asset_config_path(asset_id))
    templates = obj_attr_mgr.get_template_handles(asset_id)
    if not templates:
        return None, asset_id, True
    obj = render_sim.get_rigid_object_manager().add_object_by_template_handle(templates[0])
    if obj is None:
        return None, asset_id, True
    import habitat_sim

    obj.motion_type = habitat_sim.physics.MotionType.KINEMATIC
    obj.translation = mn.Vector3(*pos)
    return obj, asset_id, True


class _EventTimeContext:
    """Event-Time Scene Reconstruction round: place every OTHER tracked
    object at its effective pose as of the panel's own time, instead of
    leaving them all at their scene-start positions.

    Before this, each panel materialized ONLY the photographed object at
    its event-time pose while the rest of the movable scene sat frozen at
    t=0 — so a chair placed (collision-checked, correctly) beside a table
    at build time could render visually clipping a stool that had already
    moved elsewhere by then, and generally every panel showed a hybrid
    timeline that never existed. The artifact already records exactly
    what's needed: every label's per-event `effective_pose` ("what the
    physical world actually shows right now", carry-forward included).

    Usage: construct once per render_event_grid call (resolves every
    BIND context label's live handle from its census start position UP
    FRONT, while the scene is still in its unambiguous start state);
    `apply(t, exclude_label)` before each panel's capture; `restore()`
    after — restore() is safe to call multiple times and MUST run before
    the next item reuses this render_sim.

    Context objects deliberately do NOT get the reserved semantic id —
    only the photographed object is mask-verified; context is real
    occlusion/visual state, not a claim under test."""

    def __init__(self, render_sim, scene_id: str, artifact):
        import habitat_sim

        from dynamic_home_eqa.env.inventory import load_scene_state
        from dynamic_home_eqa.scripts.build_realized_day import (
            SPAWNABLE_ASSET_BY_CATEGORY, _bind_categories, find_live_object_at_xz,
        )

        self._sim = render_sim
        self._scene_id = scene_id
        self._artifact = artifact
        self._spawnable = SPAWNABLE_ASSET_BY_CATEGORY
        # label -> (live handle, original translation) for BIND labels;
        # resolved NOW, at scene-start state, so census-position lookups
        # can't mistake an already-moved object for a neighbor.
        self._bind_handles: dict = {}
        self._spawned: dict = {}  # label -> spawned rigid object (removed on restore)
        bind_cats = _bind_categories()
        scene_state = load_scene_state(scene_id)
        for label, rec in artifact.objects.items():
            if rec.category not in bind_cats:
                continue
            inst = scene_state.instances.get(label)
            if inst is None or inst.position is None:
                continue
            handle = find_live_object_at_xz(render_sim, inst.position)
            if handle is None:
                continue
            handle.motion_type = habitat_sim.physics.MotionType.KINEMATIC
            self._bind_handles[label] = (handle, tuple(handle.translation))

    def _pose_at(self, rec, t: float):
        """Latest effective pose at or before `t`, or None (leave the
        object in its start state / unspawned). A PLACEMENT_REMOVED event
        (Phase 3 put-away) positively resets the pose to None — the object
        is gone from the world from that event onward, so the skip-None
        carry-forward below must not resurrect its pre-removal pose."""
        from dynamic_home_eqa.embodied.realized_world import PLACEMENT_REMOVED
        pose = None
        for ev in rec.events:
            if ev.t <= t + 1e-6:
                if ev.placement_status == PLACEMENT_REMOVED:
                    pose = None
                elif ev.effective_pose is not None:
                    pose = ev.effective_pose
        return pose

    def apply(self, t: float, exclude_label: str) -> None:
        import magnum as mn

        from dynamic_home_eqa.scripts.build_realized_day import resolve_asset_config_path

        for label, rec in self._artifact.objects.items():
            if label == exclude_label:
                continue
            pose = self._pose_at(rec, t)
            if label in self._bind_handles:
                handle, original = self._bind_handles[label]
                handle.translation = mn.Vector3(*(pose.pos if pose is not None else original))
            elif pose is not None:
                # SPAWN-category context object that exists by time t.
                if label not in self._spawned:
                    # The artifact records each label's OWN bound asset
                    # (Strategy 2+, AssetAllocator) — obey it; the legacy
                    # category dict is only the fallback for old artifacts.
                    asset_id = rec.binding.template_name or self._spawnable.get(rec.category)
                    if asset_id is None:
                        continue
                    mgr = self._sim.get_object_template_manager()
                    if not mgr.get_template_handles(asset_id):
                        mgr.load_object_configs(resolve_asset_config_path(asset_id))
                    templates = mgr.get_template_handles(asset_id)
                    if not templates:
                        continue
                    obj = self._sim.get_rigid_object_manager().add_object_by_template_handle(templates[0])
                    if obj is None:
                        continue
                    import habitat_sim
                    obj.motion_type = habitat_sim.physics.MotionType.KINEMATIC
                    self._spawned[label] = obj
                self._spawned[label].translation = mn.Vector3(*pose.pos)
            elif label in self._spawned:
                # spawned for an earlier (later-t) panel but doesn't exist
                # yet at THIS t — stash it far away rather than churn
                # spawn/remove between the two panels of one item.
                self._spawned[label].translation = mn.Vector3(0.0, -100.0, 0.0)

    def restore(self) -> None:
        import magnum as mn

        for label, (handle, original) in self._bind_handles.items():
            handle.translation = mn.Vector3(*original)
        for obj in self._spawned.values():
            remove_object(self._sim, obj)
        self._spawned = {}


def _restore_bind_object(scene_id: str, label: str, obj) -> None:
    """Puts a relocated BIND-category object back at its true, real scene
    position after a panel is done with it. Required, not just tidy:
    _materialize_object's BIND branch finds the live object by searching
    near env.inventory.load_scene_state's fixed, original `inst.position`
    — if a panel leaves the object sitting at the realized_pose it was
    just moved to, the NEXT lookup for that same label (the other panel
    in this same item, or a later item touching the same real instance
    within the same reused render_sim) searches for it in the wrong place
    and silently fails to find it at all. Confirmed directly: without
    this restore, a stool moved for a "before" panel could not be found
    again for its own "after" panel in the same render."""
    import magnum as mn

    from dynamic_home_eqa.env.inventory import load_scene_state

    inst = load_scene_state(scene_id).instances.get(label)
    if inst is not None and inst.position is not None:
        obj.translation = mn.Vector3(*inst.position)
    # Also surrender the reserved mask id. Without this, a BIND object that
    # was EVER a target keeps _SPAWNED_OBJECT_SEMANTIC_ID in the reused
    # render_sim — its pixels then count toward LATER items' mask checks,
    # and the remove-/insert-panel "object absent" verifications see a
    # phantom object anywhere that chair is merely in frame. (Spawned
    # targets don't need this — remove_object deletes them outright.)
    obj.semantic_id = 0


def _debug_failure_shot(render_sim, center: tuple[float, float, float], extent_m: float = 0.5):
    """Best-effort camera for a FAILURE panel — a real photograph of the
    target area so the reviewer can debug (see what's at/around the spot)
    instead of a gray card. Spectator search over a synthetic AABB first;
    if even that is enclosed, a fixed oblique fallback that deliberately
    ignores obstruction (photographing the cabinet an object is sealed
    inside is exactly the debugging value). Returns rgb or None."""
    from dynamic_home_eqa.embodied.sensor import spectator_viewpoint

    half = max(extent_m, 0.3) / 2.0
    synth_aabb = ((center[0] - half, center[1] - half, center[2] - half),
                  (center[0] + half, center[1] + half, center[2] + half))
    vp = spectator_viewpoint(render_sim, synth_aabb, max(extent_m, 0.3))
    if vp is not None:
        agent_pos = (vp.camera_pos[0], vp.camera_pos[1] - 1.5, vp.camera_pos[2])
        rgb, *_ = capture_rgb_semantic_and_basis(render_sim, agent_pos, vp.look_at)
        return rgb
    import math
    best = None
    d = max(1.4, 3.0 * extent_m)
    for az_deg in (30, 120, 210, 300):
        az = math.radians(az_deg)
        agent_pos = (center[0] + d * math.cos(az), center[1] + d * 0.7 - 1.5,
                     center[2] + d * math.sin(az))
        rgb, *_ = capture_rgb_semantic_and_basis(render_sim, agent_pos, center)
        if float(rgb.std()) > 8.0:   # not a wall-filled/void frame
            return rgb
        best = rgb
    return best


def _draw_debug_failure(ax, rgb, status_label: str, detail: str) -> None:
    """Failure panel WITH a real photograph (orange border, banner) — the
    debugging-friendly replacement for the gray card whenever a target
    position was known. The status/JSON record keeps the failure verdict;
    only the visual changes."""
    import matplotlib.patches as mpatches

    H, W = rgb.shape[0], rgb.shape[1]
    ax.imshow(rgb)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.add_patch(mpatches.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False,
                                     edgecolor="orange", linewidth=5, clip_on=False))
    ax.text(0.5, 0.06, f"{status_label} [{detail}]\ndebug shot of target area — object not confirmed",
            color="white", fontsize=8, fontweight="bold", ha="center", va="center",
            transform=ax.transAxes, bbox=dict(facecolor="darkorange", alpha=0.75, pad=4))


def _draw_mask_fail_disclaimer(ax, rgb, W: int, H: int, fail_reason: str, marker: Optional[tuple[float, float]]) -> None:
    """Item 3 ('never drop the shot'): renders the REAL captured frame
    even though the mask predicate failed, with a visible disclaimer
    overlay — replaces the old behavior of discarding the frame entirely
    for a gray _draw_placeholder card whenever a real render existed.
    `marker` is the mask centroid if evaluate_object_mask found one, else
    None (MASK_FAIL_EMPTY/TOO_SMALL/TOO_LARGE never compute a centroid —
    see evaluate_object_mask) — no star is drawn in that case, only the
    disclaimer text and border, since there is no meaningful point to
    mark. A Rectangle patch in axes coordinates, not ax.spines, draws the
    border — spines get hidden by the caller's _hide_decorations right
    after this runs (see render_event_grid), a patch survives that."""
    import matplotlib.patches as mpatches

    ax.imshow(rgb)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    if marker is not None:
        ax.plot(marker[0], marker[1], "r*", markersize=22, markeredgecolor="white", markeredgewidth=1)
    ax.add_patch(mpatches.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False,
                                     edgecolor="red", linewidth=5, clip_on=False))
    ax.text(0.5, 0.06, f"MASK CHECK FAILED [{fail_reason}]\nshot shown for review — not confirmed accurate",
            color="white", fontsize=8, fontweight="bold", ha="center", va="center",
            transform=ax.transAxes, bbox=dict(facecolor="red", alpha=0.65, pad=4))


def render_event_grid(
    world, render_sim, topdown, item: PoolItem, generation_result: dict,
    artifact, out_png: pathlib.Path,
) -> dict:
    """Writes the 2x2 PNG and returns the per-panel status + positions
    needed for the automatic-signals JSON.

    Realized World Phase cutover: object positions come from `artifact`
    (a RealizedDayArtifact, embodied/realized_world.py) — computed ONCE
    at build time with real collision-checked placement
    (scripts/build_realized_day.py). This function no longer computes
    placement at all; it materializes each panel's object AT its
    recorded realized_pose and verifies VISIBILITY only (camera
    viewpoint search + the instance-mask predicate) — "commanded vs
    actual" cannot diverge anymore because there is only actual.

    State-change events now render the SAME object at the SAME realized
    pose for before and after (an annotated note replaces the old gray
    N/A card) — the object is real and visible, only its power/door
    state isn't; annotators shouldn't have to hunt for a pixel
    difference that cannot exist. Falls back to N/A only if the artifact
    genuinely has no pose for this label (binding itself failed)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from dynamic_home_eqa.embodied.sensor import spectator_viewpoint
    from dynamic_home_eqa.scripts.build_realized_day import CATEGORY_SUBSTITUTED, get_world_aabb

    e = item.event
    label = e["label"]
    category = e["object_category"]
    is_state = item.change_type == "state"
    is_remove = item.change_type == "remove"

    if item.change_type == "location":
        to_anchor = e["to_semantic"]
        from_anchor = e.get("from_semantic") or to_anchor
    elif is_remove:
        # Phase 3 put-away: the only real place to photograph is where the
        # object WAS. to_semantic is the symbolic "away".
        from_anchor = e.get("from_semantic") or "unknown"
        to_anchor = "away (put away)"
    else:
        to_anchor = from_anchor = e["to_semantic"]  # fixed furniture — same anchor before/after

    obj_record = artifact.objects.get(label)
    before_event = after_event = None
    is_first_event = False
    if obj_record is not None:
        idx = next((i for i, ev in enumerate(obj_record.events) if abs(ev.t - e["t"]) < 1e-3), None)
        if idx is not None:
            after_event = obj_record.events[idx]
            before_event = after_event if is_state else (obj_record.events[idx - 1] if idx > 0 else after_event)
            is_first_event = idx == 0
    # Spawn-in honesty: an insert_new event's BEFORE panel must show the
    # destination WITHOUT the object — it does not exist yet (the manifest
    # says so; before_event == after_event above is a framing convenience,
    # not a claim the object was already there). Handled by its own branch
    # in the panel loop, mirroring the remove-path's disappearance shot.
    is_insert = e.get("change_type") == "insert_new" and not is_remove and not is_state
    # First MOVE of a real scene instance (BIND, e.g. a chair's first pull-
    # out): the honest before-pose is its census starting position, not the
    # event's own realized pose (before_event == after_event would photo-
    # graph it already moved).
    bind_start_pos = None
    from dynamic_home_eqa.embodied.realized_world import BIND as _BIND_KIND
    if (is_first_event and not is_insert and not is_state and not is_remove
            and obj_record is not None and obj_record.binding.kind == _BIND_KIND):
        from dynamic_home_eqa.env.inventory import load_scene_state
        _inst = load_scene_state(world.scene_id).instances.get(label)
        if _inst is not None and _inst.position is not None:
            bind_start_pos = tuple(_inst.position)

    # Pre-Pool-Build Remediation round (item 2): top-down markers use
    # effective_pose (the carried-forward "what the physical world
    # actually shows right now" pose), not realized_pose (this specific
    # event's own placement outcome) — an unrealized event still has a
    # real physical position to point at (its last successful placement,
    # or its BIND-seeded starting position), so the top-down panel is no
    # longer left blank just because THIS event's own egocentric panel is
    # a failure card. The egocentric panel below still keys off this
    # event's own realized/realized_pose — "no object is ever poseless"
    # is a top-down/tracking statement, not a claim that a failed event's
    # OWN attempted placement should be photographed as if it succeeded.
    from_pos = before_event.effective_pose.pos if (before_event and before_event.effective_pose) else None
    to_pos = after_event.effective_pose.pos if (after_event and after_event.effective_pose) else None

    # Event-Time Scene Reconstruction round: every OTHER tracked object is
    # placed at its effective pose as of each panel's own time (see
    # _EventTimeContext) — panels show the real event-time configuration,
    # not a t=0 hybrid. The before panel reconstructs the instant JUST
    # BEFORE this event; the after panel includes it.
    context = _EventTimeContext(render_sim, world.scene_id, artifact)
    panel_time = {"before": e["t"] - 1e-4, "after": e["t"]}

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    panel_status: dict[str, str] = {}
    panel_luminance: dict[str, Optional[float]] = {"before": None, "after": None}
    spawn_info: dict[str, dict] = {"before": {}, "after": {}}
    # Held-framing cache (item 2): the "before" panel's own successful
    # SpectatorPose, reused for "after" when there's no fresh position to
    # aim at that would actually show anything — a state-only change
    # (always) or a location change whose new anchor turned out enclosed
    # (no unobstructed spectator candidate — same physical situation as
    # "hidden inside a now-closed receptacle" in this simulator, since
    # that IS what STATUS_ENCLOSED means). Reusing the exact camera the
    # object was last confirmed visible from, rather than a fresh
    # (guaranteed-enclosed) search, is what lets the after panel show the
    # disappearance instead of a blank ENCLOSED card. Local to this one
    # before/after pair — not a cross-event cache — because the before
    # panel for THIS pair is always computed in the same call, so a held
    # pose is always available here when the after panel needs one,
    # unlike a cross-item cache which would frequently be empty (the
    # render job only visits a random sample of events, not every one).
    held_vp = None

    for key, ax, ev, anchor_name, title in (
        ("before", axes[0][0], before_event, from_anchor, f"BEFORE (egocentric): {from_anchor}"),
        ("after", axes[0][1], after_event, to_anchor, f"AFTER (egocentric): {to_anchor}"),
    ):
        if key == "before" and is_insert:
            # Spawn-in mirror of the remove-path below: the honest "before"
            # for an insert_new is the DESTINATION WITHOUT the object — it
            # does not exist until this event. The target is deliberately
            # never materialized; every other object is reconstructed at
            # before-time, and the object's absence is verified the same
            # way the remove-path verifies a disappearance.
            context.apply(panel_time[key], exclude_label=label)
            tp = (after_event.realized_pose.pos
                  if (after_event is not None and after_event.realized_pose is not None) else to_pos)
            if tp is None:
                _draw_placeholder(ax, "OBJECT NOT YET PRESENT\n(no destination position to aim at)")
                panel_status[key] = STATUS_ANCHOR_UNRESOLVED
                spawn_info[key] = {"attempted": False, "insert_before": True, "reason": "no_position"}
            else:
                half = 0.3
                synth_aabb = ((tp[0] - half, tp[1] - half, tp[2] - half),
                              (tp[0] + half, tp[1] + half, tp[2] + half))
                vp = spectator_viewpoint(render_sim, synth_aabb, 0.6)
                if vp is None:
                    rgb = _debug_failure_shot(render_sim, tp)
                    if rgb is None:
                        _draw_placeholder(ax, _STATUS_MESSAGES[STATUS_ENCLOSED])
                    else:
                        _draw_debug_failure(ax, rgb, "ENCLOSED", "pre-spawn destination")
                    panel_status[key] = STATUS_ENCLOSED
                    spawn_info[key] = {"attempted": False, "insert_before": True, "reason": "enclosed"}
                else:
                    in_agent_pos = (vp.camera_pos[0], vp.camera_pos[1] - 1.5, vp.camera_pos[2])
                    rgb, semantic, *_ = capture_rgb_semantic_and_basis(render_sim, in_agent_pos, vp.look_at)
                    H, W = rgb.shape[0], rgb.shape[1]
                    object_absent = not bool((semantic == _SPAWNED_OBJECT_SEMANTIC_ID).any())
                    ax.imshow(rgb)
                    ax.set_xlim(0, W)
                    ax.set_ylim(H, 0)
                    ax.text(0.5, 0.06, "(object not yet present — spawns in at this event)",
                            color="yellow", fontsize=8, ha="center", transform=ax.transAxes,
                            bbox=dict(facecolor="black", alpha=0.55, pad=2))
                    held_vp = vp
                    panel_status[key] = STATUS_OK if object_absent else STATUS_OBJECT_SPAWN_FAILED
                    spawn_info[key] = {"attempted": False, "insert_before": True,
                                       "object_absent_verified": object_absent}
                    panel_luminance[key] = float(
                        (rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114).mean()
                    )
            ax.set_title(title, fontsize=9)
            _hide_decorations(ax)
            continue

        if key == "after" and is_remove:
            # Phase 3 put-away: the honest "after" is the BEFORE panel's own
            # camera pose with the object gone — the disappearance is the
            # event. The target object is deliberately never materialized
            # (same physical situation an insert_new's before-frame shows:
            # the receptacle without the object); the event-time context
            # still reconstructs every OTHER object at t. held_vp is the
            # same held-framing mechanism ENCLOSED after-panels reuse.
            if held_vp is None:
                # The before panel produced no usable camera (its own
                # failure card is showing why); there is no honest frame
                # to show the disappearance from.
                _draw_placeholder(ax, "OBJECT PUT AWAY\n(no before-camera to reuse)")
                panel_status[key] = STATUS_ANCHOR_UNRESOLVED
                spawn_info[key] = {"attempted": False, "removed": True, "reason": "no_held_framing"}
            else:
                context.apply(panel_time[key], exclude_label=label)
                rm_agent_pos = (held_vp.camera_pos[0], held_vp.camera_pos[1] - 1.5, held_vp.camera_pos[2])
                rgb, semantic, *_ = capture_rgb_semantic_and_basis(
                    render_sim, rm_agent_pos, held_vp.look_at
                )
                H, W = rgb.shape[0], rgb.shape[1]
                # The target was never materialized, so its reserved semantic
                # id appearing would mean a context/restore leak put it (or a
                # stale spawn) back in frame — recorded as the per-panel
                # verification of the disappearance mechanic.
                object_absent = not bool((semantic == _SPAWNED_OBJECT_SEMANTIC_ID).any())
                ax.imshow(rgb)
                ax.set_xlim(0, W)
                ax.set_ylim(H, 0)
                ax.text(0.5, 0.06, "(object put away — no longer present in scene)",
                        color="yellow", fontsize=8, ha="center", transform=ax.transAxes,
                        bbox=dict(facecolor="black", alpha=0.55, pad=2))
                panel_status[key] = STATUS_OK if object_absent else STATUS_OBJECT_SPAWN_FAILED
                spawn_info[key] = {"attempted": False, "removed": True, "held_framing": True,
                                   "object_absent_verified": object_absent}
                panel_luminance[key] = float(
                    (rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114).mean()
                )
            ax.set_title(title, fontsize=9)
            _hide_decorations(ax)
            continue

        if ev is None or not ev.realized:
            reason = ev.placement_status if ev is not None else "anchor_unbacked"
            status = _PLACEMENT_TO_STATUS.get(reason, STATUS_ANCHOR_UNRESOLVED)
            # item 2: "the render job renders unrealized events as the
            # labeled failure card with the item-1 cause code" — the
            # card's grouped message (OBJECT_SPAWN_FAILED etc.) plus the
            # specific cause code appended, so a reviewer sees WHICH of
            # the 4 SURFACE_FULL-family causes (or another failure) this
            # was without needing to cross-reference the JSON.
            # Debug-shot upgrade: when the object has ANY known physical
            # position (its carried-forward effective pose), photograph
            # that area instead of a gray card — the status/JSON keep the
            # failure verdict, the reviewer gets something to look at.
            dbg_center = to_pos or from_pos
            rgb = _debug_failure_shot(render_sim, dbg_center) if dbg_center is not None else None
            if rgb is None:
                _draw_placeholder(ax, f"{_STATUS_MESSAGES[status]}\n[{reason}]")
            else:
                _draw_debug_failure(ax, rgb, status.upper(), reason)
            panel_status[key] = status
            spawn_info[key] = {"attempted": False, "reason": reason,
                               "debug_shot": rgb is not None}
            ax.set_title(title, fontsize=9)
            _hide_decorations(ax)
            continue

        target_pos = ev.realized_pose.pos
        if key == "before" and bind_start_pos is not None:
            # First move of a real scene instance: the before panel shows it
            # at its census STARTING position (see prologue) — before_event
            # is this same event, whose realized pose is already the moved-
            # to position, which would render before == after.
            target_pos = bind_start_pos

        # Materialize FIRST (no placement computation here, see docstring)
        # — the spectator camera search needs the object's own real,
        # post-spawn AABB, not the raw anchor position, so there is no
        # viewpoint to search for until the object actually exists in the
        # sim. If materialization fails, there is nothing to photograph
        # regardless of what a camera search would have found.
        obj, asset_id, is_spawned = _materialize_object(
            render_sim, world.scene_id, label, category, target_pos,
            asset_id_override=(obj_record.binding.template_name if obj_record else None))
        if obj is None:
            rgb = _debug_failure_shot(render_sim, target_pos)
            if rgb is None:
                _draw_placeholder(ax, _STATUS_MESSAGES[STATUS_OBJECT_SPAWN_FAILED])
            else:
                _draw_debug_failure(ax, rgb, "OBJECT_SPAWN_FAILED", "materialize_failed")
            panel_status[key] = STATUS_OBJECT_SPAWN_FAILED
            spawn_info[key] = {"attempted": True, "reason": "materialize_failed",
                               "realized_pos": target_pos, "debug_shot": rgb is not None}
            ax.set_title(title, fontsize=9)
            _hide_decorations(ax)
            continue

        # Event-time context AFTER the target is materialized (the
        # target's own BIND lookup searches by census start position and
        # must not race a context object relocated near it; context BIND
        # handles were pre-resolved at construction, so their order
        # doesn't matter).
        context.apply(panel_time[key], exclude_label=label)

        aabb = get_world_aabb(obj)
        (min_x, min_y, min_z), (max_x, max_y, max_z) = aabb
        max_extent = max(max_x - min_x, max_y - min_y, max_z - min_z)

        # Item 2: a state-only change always reuses the before panel's own
        # framing outright (no fresh search at all — before_event IS
        # after_event for a state change, so a fresh search would search
        # the identical AABB anyway; reusing is strictly cheaper and
        # removes any chance of the two searches landing on different
        # candidates). A location change tries its own fresh search first
        # and only falls back to held_vp if that search comes back empty
        # (ENCLOSED) — the new position gets a real, independent look
        # before assuming it's hidden.
        used_held_framing = False
        if key == "after" and is_state and held_vp is not None:
            vp = held_vp
            used_held_framing = True
        else:
            vp = spectator_viewpoint(render_sim, aabb, max_extent)
            if vp is None and key == "after" and held_vp is not None:
                vp = held_vp
                used_held_framing = True

        if vp is None:
            # Debug shot BEFORE removing the object: the oblique fallback in
            # _debug_failure_shot ignores obstruction on purpose — a photo
            # of the closed cabinet the object is sealed inside is the
            # debugging value here.
            rgb = _debug_failure_shot(render_sim, target_pos, extent_m=max_extent)
            if is_spawned:
                remove_object(render_sim, obj)
            else:
                _restore_bind_object(world.scene_id, label, obj)
            if rgb is None:
                _draw_placeholder(ax, _STATUS_MESSAGES[STATUS_ENCLOSED])
            else:
                _draw_debug_failure(ax, rgb, "ENCLOSED", "no unobstructed viewpoint")
            panel_status[key] = STATUS_ENCLOSED
            spawn_info[key] = {"attempted": True, "reason": "enclosed",
                               "realized_pos": target_pos, "debug_shot": rgb is not None}
            ax.set_title(title, fontsize=9)
            _hide_decorations(ax)
            continue

        obj.semantic_id = _SPAWNED_OBJECT_SEMANTIC_ID
        # capture_rgb_semantic_and_basis places the render AGENT at the
        # position given and the sensor renders from agent_pos + the
        # sensor spec's fixed (0, 1.5, 0) local offset (see
        # _make_render_sim's rgb_spec.position / camera_basis's
        # docstring). That offset exists to turn a navmesh-standing
        # position into an eye-height camera — spectator_viewpoint
        # already returns the exact intended eye position (no standing
        # concept at all), so it must be subtracted back out here or the
        # real capture ends up 1.5m above vp.camera_pos.
        agent_pos = (vp.camera_pos[0], vp.camera_pos[1] - 1.5, vp.camera_pos[2])
        rgb, semantic, eye, forward, right, up = capture_rgb_semantic_and_basis(
            render_sim, agent_pos, vp.look_at
        )
        H, W = rgb.shape[0], rgb.shape[1]
        mask = semantic == _SPAWNED_OBJECT_SEMANTIC_ID
        # anchor_px used to come from resolve_anchor_position(world,
        # anchor_name) — a generic SLOT_ANCHORS/room-centroid coordinate,
        # not this SPECIFIC event's real placement. That was an adequate
        # proxy under the old embodied camera (stood 1.5-3.5m back, so a
        # ~0.5m generic-vs-real height mismatch was a small fraction of
        # the frame) but a confirmed real bug under the spectator camera,
        # which stands much closer for small objects: a real gold-set
        # case (laptop on bedroom.bed) had the generic "bed" anchor
        # coordinate sitting 0.66m below the laptop's real realized
        # position, projecting hundreds of pixels below a 360px frame
        # even though the object's own mask was correctly centered.
        # target_pos IS this exact event's real anchor position (the
        # artifact's realized_pose, by construction the same position the
        # builder resolved for this exact anchor name) — strictly more
        # accurate than a generic fallback, not a weaker check.
        anchor_px = project_point(eye, forward, right, up, target_pos)
        mask_passed, fail_reason, mask_info = evaluate_object_mask(mask, anchor_px)

        # Item 4: bounded corrective sweep for the two size-diagnosed fail
        # modes (a distance problem) plus MASK_FAIL_EMPTY (an occlusion/
        # framing problem — backing up widens the view and the azimuth
        # offsets step around the blocker). off_center/anchor-out-of-frame
        # stay out of scope: those are aim problems a distance change
        # doesn't address. Adopted only if it found a strictly passing
        # candidate, or (still failing either way) scored better than the
        # original capture — a bounded retry must never make the shown
        # result worse.
        size_corrected = False
        if not mask_passed and fail_reason in (MASK_FAIL_TOO_SMALL, MASK_FAIL_TOO_LARGE,
                                               MASK_FAIL_EMPTY):
            swept = _size_corrective_sweep(render_sim, aabb, target_pos, fail_reason, vp)
            if swept is not None:
                sw_rgb, sw_mask, sw_mask_info, sw_passed, sw_fail_reason, sw_vp, swept_score, sw_anchor_px = swept
                from dynamic_home_eqa.embodied.sensor import spectator_unobstructed
                (aabb_min_x, aabb_min_y, aabb_min_z), (aabb_max_x, aabb_max_y, aabb_max_z) = aabb
                _acx, _acz = (aabb_min_x + aabb_max_x) / 2.0, (aabb_min_z + aabb_max_z) / 2.0
                _acy = (aabb_min_y + aabb_max_y) / 2.0
                original_unobstructed = spectator_unobstructed(render_sim, vp.camera_pos, (_acx, _acy, _acz)) or \
                    spectator_unobstructed(render_sim, vp.camera_pos, (_acx, aabb_max_y, _acz))
                original_score = _score_capture(mask_info, (H, W), unobstructed=original_unobstructed)
                if sw_passed or swept_score > original_score:
                    rgb, mask, mask_info = sw_rgb, sw_mask, sw_mask_info
                    mask_passed, fail_reason = sw_passed, sw_fail_reason
                    vp = sw_vp
                    anchor_px = sw_anchor_px
                    H, W = rgb.shape[0], rgb.shape[1]
                    size_corrected = True

        # Digital-zoom last resort: a still-too-small BUT visible object
        # (the distance sweep floored out) gets cropped-and-upscaled around
        # its mask so a small/flat item like a plate or keys reads clearly.
        # Pure post-process — no re-render, no camera move.
        digital_zoom = False
        if not mask_passed and fail_reason == MASK_FAIL_TOO_SMALL:
            zoomed = _digital_zoom_pass(rgb, mask, anchor_px)
            if zoomed is not None:
                rgb, mask_info, _marker = zoomed
                mask_passed, fail_reason = True, "ok"
                anchor_px = mask_info["centroid_px"]
                H, W = rgb.shape[0], rgb.shape[1]
                digital_zoom = True

        if is_spawned:
            remove_object(render_sim, obj)
        else:
            _restore_bind_object(world.scene_id, label, obj)

        spawn_info[key] = {
            "attempted": True, "asset_id": asset_id, "substituted": category in CATEGORY_SUBSTITUTED,
            "realized_pos": target_pos, "placement_status_at_build": ev.placement_status,
            "mask_area_px": mask_info["area_px"], "mask_area_fraction": mask_info["area_fraction"],
            "mask_passed": mask_passed, "mask_fail_reason": None if mask_passed else fail_reason,
            "mask_status": "ok" if mask_passed else "failed",
            "spectator_distance_m": vp.distance_m, "spectator_elevation_deg": vp.elevation_deg,
            "held_framing": used_held_framing, "size_corrected": size_corrected,
            "digital_zoom": digital_zoom,
        }

        if key == "before":
            # vp is a real, usable pose regardless of mask_passed (item 3 —
            # a mask-failed panel still has a real captured frame at a real
            # camera pose); held for the after panel's own fallback above.
            held_vp = vp

        if not mask_passed:
            # Item 3: never drop the shot — a real capture exists (we got
            # this far), so show it with a visible disclaimer instead of
            # discarding it for a gray _draw_placeholder card.
            # MASK_FAIL_EMPTY/TOO_SMALL/TOO_LARGE never compute a centroid
            # (see evaluate_object_mask) — anchor_px (the claimed position's
            # own projection, independent of the mask) stands in as the
            # marker for those so the reviewer still sees roughly where the
            # object should be, when it's in frame at all.
            marker = mask_info["centroid_px"]
            if marker is None and anchor_px is not None and 0 <= anchor_px[0] <= W and 0 <= anchor_px[1] <= H:
                marker = anchor_px
            _draw_mask_fail_disclaimer(ax, rgb, W, H, fail_reason, marker)
            panel_status[key] = _MASK_FAIL_TO_STATUS[fail_reason]
            panel_luminance[key] = float(
                (rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114).mean()
            )
        else:
            marker = mask_info["centroid_px"]
            ax.imshow(rgb)
            ax.set_xlim(0, W)
            ax.set_ylim(H, 0)
            ax.plot(marker[0], marker[1], "r*", markersize=22, markeredgecolor="white", markeredgewidth=1)
            if not highlight_would_be_visible(rgb, marker[0], marker[1]):
                ax.text(0.5, 0.03, "(HIGHLIGHT_INVISIBLE: marker blends with background)",
                        color="yellow", fontsize=7, ha="center", transform=ax.transAxes)
            if is_state:
                ax.text(0.5, 0.09, "(state not visually represented)",
                        color="yellow", fontsize=8, ha="center", transform=ax.transAxes,
                        bbox=dict(facecolor="black", alpha=0.55, pad=2))
            if used_held_framing:
                ax.text(0.5, 0.15, "(held framing — reused prior camera pose)",
                        color="yellow", fontsize=7, ha="center", transform=ax.transAxes,
                        bbox=dict(facecolor="black", alpha=0.55, pad=2))
            if digital_zoom:
                ax.text(0.5, 0.21, "(digitally zoomed — small object magnified)",
                        color="yellow", fontsize=7, ha="center", transform=ax.transAxes,
                        bbox=dict(facecolor="black", alpha=0.55, pad=2))
            if vp.is_high_angle:
                ax.text(0.5, 0.97, "(spectator view)",
                        color="yellow", fontsize=7, ha="center", va="top", transform=ax.transAxes,
                        bbox=dict(facecolor="black", alpha=0.55, pad=2))
            panel_status[key] = STATUS_OK
            # Rec. 601 luma, standard perceptual grayscale weighting
            # — for the per-scene lighting report; only meaningful
            # for a real OK render, not a gray placeholder card.
            panel_luminance[key] = float(
                (rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114).mean()
            )
        ax.set_title(title, fontsize=9)
        _hide_decorations(ax)

    # Combined top-down: both before (hollow star) and after (solid star)
    # markers, an arrow between them, and room-centroid labels — drawn on
    # BOTH top-down panels so a panel is never left blank just because
    # this specific slot's own anchor didn't resolve while the other did.
    # Independent of egocentric viewpoint status entirely — only needs a
    # position, not a validated camera pose.
    for ax, title in ((axes[1][0], "BEFORE/AFTER (top-down)"), (axes[1][1], "BEFORE/AFTER (top-down)")):
        if from_pos is None and to_pos is None:
            _draw_placeholder(ax, _STATUS_MESSAGES[STATUS_ANCHOR_UNRESOLVED])
        else:
            ax.imshow(topdown.grid, cmap="gray", origin="lower")
            for room, (rx, rz) in world._room_centroids.items():
                rrow, rcol = topdown.world_to_pixel(rx, rz)
                ax.text(rcol, rrow, room, color="blue", fontsize=6, ha="center", va="center", alpha=0.7)
            before_px = topdown.world_to_pixel(from_pos[0], from_pos[2]) if from_pos is not None else None
            after_px = topdown.world_to_pixel(to_pos[0], to_pos[2]) if to_pos is not None else None
            if before_px is not None:
                row, col = before_px
                ax.plot(col, row, marker="*", markersize=18, markerfacecolor="none",
                        markeredgecolor="red", markeredgewidth=2)
            if after_px is not None:
                row, col = after_px
                ax.plot(col, row, "r*", markersize=18)
            if before_px is not None and after_px is not None and before_px != after_px:
                ax.annotate(
                    "", xy=(after_px[1], after_px[0]), xytext=(before_px[1], before_px[0]),
                    arrowprops=dict(arrowstyle="->", color="orange", lw=1.5),
                )
        ax.set_title(title, fontsize=9)
        _hide_decorations(ax)

    # Put every context object back before the next item reuses this sim.
    context.restore()

    caption = format_caption(item, generation_result)
    fig.suptitle(
        f'{caption["label"]}  ({caption["category"]}, {caption["change_type"]})  {caption["t_clock"]}\n'
        f'{caption.get("from")} -> {caption.get("to")}   mover={caption.get("mover")}\n'
        f'reason: {caption["reason"]}\n'
        f'[before={panel_status["before"]}  after={panel_status["after"]}]',
        fontsize=9, wrap=True,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.85])
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=130, facecolor="white")
    plt.close(fig)

    return {
        "before_status": panel_status["before"], "after_status": panel_status["after"],
        "before_pos": from_pos, "after_pos": to_pos,
        # Realized World Phase cutover: before_pos/after_pos above ARE the
        # object's real, collision-checked position — there is no separate
        # "commanded vs actual" or camera-search height-offset concept left
        # to log (both were proxies for not having a materialized object;
        # see build_realized_day.py's own module docstring). The
        # build-time placement_status (ok/surface_full/placement_infeasible/
        # anchor_unbacked/no_asset) is preserved per panel in `spawn`
        # instead — a richer, more honest signal than a distance number.
        "before_placement_status_at_build": spawn_info["before"].get("placement_status_at_build"),
        "after_placement_status_at_build": spawn_info["after"].get("placement_status_at_build"),
        "spawn": spawn_info,
        "before_luminance": panel_luminance["before"], "after_luminance": panel_luminance["after"],
    }


def geometric_signals(physics_sim, before_pos, after_pos) -> dict:
    """Runs embodied/placement_check.py's real collision/occupancy check
    at both anchors. None positions (fully unresolvable) yield null
    signals rather than a fabricated pass/fail."""
    from dynamic_home_eqa.embodied.placement_check import check_placement

    out = {}
    for key, pos in (("before", before_pos), ("after", after_pos)):
        if pos is None:
            out[f"{key}_supported"] = None
            out[f"{key}_support_distance_m"] = None
            out[f"{key}_embedded"] = None
        else:
            check = check_placement(physics_sim, pos)
            out[f"{key}_supported"] = check.supported
            out[f"{key}_support_distance_m"] = check.support_distance_m
            out[f"{key}_embedded"] = check.embedded
    return out


def build_plausibility_lookup(generation_result: dict, manifest: dict):
    """Runs plausibility.day_report() once per folder and indexes its
    warnings by (label, t) — closes the "capability-flagged" gap
    render_tool.md documented as unimplemented (day_report already
    computes exactly this from real occupant age_bands, it just wasn't
    being surfaced per-event anywhere before this job)."""
    from dynamic_home_eqa.plausibility import day_report
    from dynamic_home_eqa.rooms import slot_room

    age_band = {o["name"]: o.get("age_band") for o in generation_result["persona"]["occupants"]}
    report = day_report(manifest["changes"], age_band, slot_room)
    flags: dict[tuple[str, float], set[str]] = defaultdict(set)
    for w in report.warnings:
        flags[(w.label, w.t)].add(w.kind)
    return flags


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # Halved from 64/16 (80 total) — the webapp sample pool doesn't need
    # to be this large for the realism study's current purposes; ~40
    # items is close enough to the requested ~30 while keeping both the
    # location/state ratio and each stratum's own minimum viable sample
    # size intact.
    ap.add_argument("--n-location", type=int, default=32)
    ap.add_argument("--n-state", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--folders", nargs="*", default=None, help="restrict to these folders; default: full validated pool")
    ap.add_argument("--gen-dir", default=None,
                    help="directory holding the generation folders (default: generation_out/)")
    ap.add_argument("--realized-dir", default=None,
                    help="directory holding {folder}.realized_day.json artifacts "
                         "(default: build_realized_day's own data/realized_days/). "
                         "Pass the same run-scoped dir given to build_realized_day "
                         "--out-dir when rendering a non-default --gen-dir run.")
    ap.add_argument("--media-dir", default=str(_MEDIA_DIR),
                    help="where the PNG/JSON media and render_manifest.json land "
                         "(default: results/reports/realism_eval_media/). Item ids "
                         "are keyed by folder name alone, so runs that share folder "
                         "names need distinct --media-dirs — same collision rule as "
                         "build_realized_day --out-dir.")
    args = ap.parse_args()

    from dynamic_home_eqa.embodied.realized_world import load_realized_day
    from dynamic_home_eqa.scripts.build_realized_day import assert_category_has_asset_coverage
    from dynamic_home_eqa.scripts.build_realized_day import _OUT_DIR as _DEFAULT_REALIZED_DAY_DIR

    import pathlib as _pl
    _REALIZED_DAY_DIR = _pl.Path(args.realized_dir) if args.realized_dir else _DEFAULT_REALIZED_DAY_DIR
    if not _REALIZED_DAY_DIR.is_absolute():
        _REALIZED_DAY_DIR = _DYNAMIC_EQA / _REALIZED_DAY_DIR
    media_dir = _pl.Path(args.media_dir)
    if not media_dir.is_absolute():
        media_dir = _DYNAMIC_EQA / media_dir
    out_dir = _pl.Path(args.gen_dir) if args.gen_dir else _DYNAMIC_EQA / "generation_out"
    if not out_dir.is_absolute():
        out_dir = _DYNAMIC_EQA / out_dir
    requested_folders = args.folders or discover_valid_folders(out_dir)

    # Realized World Phase cutover: this job now READS realized_day.json
    # artifacts (scripts/build_realized_day.py) instead of computing
    # placement itself — a folder with no built artifact has nothing to
    # render. Pool-wide build is still owner-gated (see the phase's own
    # order); restricting silently to what's actually been built, rather
    # than erroring the whole run, keeps this usable for the reviewed
    # subset while making the gap visible.
    folders = [f for f in requested_folders if (_REALIZED_DAY_DIR / f"{f}.realized_day.json").exists()]
    skipped = sorted(set(requested_folders) - set(folders))
    if skipped:
        print(f"SKIPPING {len(skipped)} folder(s) with no built realized_day.json artifact (run "
              f"scripts/build_realized_day.py first): {skipped}")
    print(f"{len(folders)} folders in scope")

    pool: list[PoolItem] = []
    manifests: dict[str, dict] = {}
    gen_results: dict[str, dict] = {}
    artifacts: dict[str, object] = {}
    for folder in folders:
        manifest = json.loads((out_dir / folder / "manifest.json").read_text())
        gen_result = json.loads((out_dir / folder / "generation_result.json").read_text())
        manifests[folder] = manifest
        gen_results[folder] = gen_result
        artifacts[folder] = load_realized_day(_REALIZED_DAY_DIR / f"{folder}.realized_day.json")
        for c in manifest["changes"]:
            if c.get("change_type") == "state_change":
                pool.append(PoolItem(folder=folder, change_type="state", event=c))
            elif c.get("change_type") == "remove":
                pool.append(PoolItem(folder=folder, change_type="remove", event=c))
            else:
                pool.append(PoolItem(folder=folder, change_type="location", event=c))

    print(f"{len(pool)} candidate events pool-wide ({sum(1 for p in pool if p.change_type=='location')} location, "
          f"{sum(1 for p in pool if p.change_type=='state')} state, "
          f"{sum(1 for p in pool if p.change_type=='remove')} remove)")

    # Standing constraint: fail loudly, at pool-construction time, on any
    # category with no entry anywhere in the asset mapping — see
    # assert_category_has_asset_coverage's docstring (now build_realized_day.py's).
    for category in sorted({p.event["object_category"] for p in pool}):
        assert_category_has_asset_coverage(category)

    sample = select_random_sample_per_type(pool, n_location=args.n_location, n_state=args.n_state, seed=args.seed)
    print(f"Sampled {len(sample)} items (up to {args.n_location} location, up to {args.n_state} state, uniform random)")

    by_scene: dict[str, list[PoolItem]] = defaultdict(list)
    for item in sample:
        scene_id = gen_results[item.folder]["scene_id"]
        by_scene[scene_id].append(item)

    media_dir.mkdir(parents=True, exist_ok=True)
    manifest_index = []
    plausibility_cache: dict[str, dict] = {}

    for scene_id, items in by_scene.items():
        print(f"\n=== scene {scene_id}: {len(items)} items ===")
        from dynamic_home_eqa.embodied.world import EmbodiedWorld
        from dynamic_home_eqa.topdown_map import load_topdown_map

        topdown = load_topdown_map(scene_id)
        render_sim = _make_render_sim(scene_id)
        try:
            for idx, item in enumerate(items):
                gen_result = gen_results[item.folder]
                manifest = manifests[item.folder]
                world = EmbodiedWorld(scene_id, gen_result, manifest)
                try:
                    item_id = f"{item.folder}_{item.event['label']}_t{item.event['t']:.2f}_{item.change_type}"
                    png_path = media_dir / f"{item_id}.png"
                    geom = render_event_grid(world, render_sim, topdown, item, gen_result, artifacts[item.folder], png_path)
                finally:
                    world.close()

                if item.folder not in plausibility_cache:
                    plausibility_cache[item.folder] = build_plausibility_lookup(gen_result, manifest)
                flags = plausibility_cache[item.folder].get((item.event["label"], item.event["t"]), set())

                signals = geometric_signals(render_sim, geom["before_pos"], geom["after_pos"])
                signals.update({
                    "before_status": geom["before_status"],
                    "after_status": geom["after_status"],
                    "spawn": geom["spawn"],
                    "before_luminance": geom["before_luminance"], "after_luminance": geom["after_luminance"],
                    "before_placement_status_at_build": geom["before_placement_status_at_build"],
                    "after_placement_status_at_build": geom["after_placement_status_at_build"],
                    # kept for any downstream consumer that just wants a
                    # single pass/fail: OK on both panels, nothing else.
                    "degenerate_viewpoint": not (
                        geom["before_status"] == STATUS_OK and geom["after_status"] == STATUS_OK
                    ),
                    "deterministic_plausibility_confidence": item.event.get("confidence", 1.0),
                    "plausibility_flags": {
                        "capability": "capability" in flags,
                        "egress": "egress" in flags,
                        "pingpong": "pingpong" in flags,
                    },
                    "llm_self_graded_realism_day_mean": gen_result.get("mean_realism_score"),
                })

                caption = format_caption(item, gen_result)
                json_path = media_dir / f"{item_id}.json"
                json_path.write_text(json.dumps({"caption": caption, "automatic_signals": signals}, indent=2))

                manifest_index.append({
                    "item_id": item_id, "png": png_path.name, "json": json_path.name,
                    **caption,
                })
                print(f"  [{idx+1}/{len(items)}] {item_id}  before={geom['before_status']} after={geom['after_status']}")
        finally:
            render_sim.close()

    (media_dir / "render_manifest.json").write_text(json.dumps(manifest_index, indent=2))
    print(f"\nWrote {len(manifest_index)} items to {media_dir}")


if __name__ == "__main__":
    main()
