"""
anchor_admission.py — read-side schema + cache accessors for the
per-scene anchor admission map (Anchor Admission round, Version B).

Pure, no habitat imports — this module is consumed by generation/*.py,
which must stay habitat_sim-free at runtime (see generation/inventory.py's
own module docstring for the same constraint). The map itself is
PRODUCED by scripts/compute_anchor_admission_map.py, which does need a
real sim (needs habitat-lab — capacity estimation reuses
build_realized_day.py's receptacle machinery) and is never imported
from here.

Two facts per anchor, both fed by the one precomputation pass:
  - reachable: whether the anchor's real position sits on a navmesh
    island at or above NavMeshConfig.min_component_area_m2 (the same
    threshold embodied/world.py's EmbodiedWorld._ensure_sim() prunes
    _anchor_positions with) — closes the class of anchor_unbacked
    failures a category-count census can never see (e.g. a real `tv`
    instance sitting on a disconnected navmesh island).
  - capacity: an approximate object-count budget for an "instance"-kind
    anchor's placement surface (None for a region anchor, or an
    instance anchor with no usable receptacle at all — see the
    precomputation script's own docstring for the receptacle-vs-
    synthetic-AABB-top precedence this mirrors from build_realized_day.py).

ADMISSION_VERSION is a manual constant, not a content hash of
build_realized_day.py — every unrelated builder edit would otherwise
silently invalidate every cached map under this feature's fail-open
design (a missing/stale map degrades generation back to today's
behavior, not a hard failure), which would quietly erase the whole
feature's benefit far more often than the cache's own logic actually
changes. Bump this by hand when compute_anchor_admission_map.py's
reachability or capacity computation changes in a way that should
invalidate every existing cache.
"""
from __future__ import annotations

import json
import logging
import pathlib
from typing import Optional

_logger = logging.getLogger(__name__)

ADMISSION_VERSION = 5  # v1 -> v2: TYPICAL_OBJECT_FOOTPRINT_M2 recalibrated 0.06 -> 0.25 m^2
                        # (0.06 gave implausible capacities like bed=25-33 on real scenes).
                        # v2 -> v3: 0.25 -> 0.10 m^2 (0.25 was ALSO wrong, confirmed by a
                        # real live-LLM generation run rejecting 34/46 otherwise-valid
                        # proposals as over-capacity). v3 -> v4: synthetic-source capacities
                        # get a floor of 8 (fridge's tiny AABB-top area was still 100% of
                        # remaining rejections after the v3 fix). v4 -> v5: the curated-out
                        # capacity=None branch removed along with
                        # PLACEMENT_RECEPTACLE_CURATED_OUT (Realizable-Anchor Vocabulary
                        # round) — a curated-out anchor now gets a synthetic-top budget,
                        # matching the builder's own new fallback behavior — see
                        # compute_anchor_admission_map.py's own comments for the full story.

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA
_OUT_DIR = _DYNAMIC_EQA / "data" / "anchor_admission_maps"


def save_anchor_admission_map(admission_map: dict, out_dir: pathlib.Path = _OUT_DIR) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{admission_map['scene_id']}.json"
    path.write_text(json.dumps(admission_map, indent=2))
    return path


def load_anchor_admission_map(scene_id: str, out_dir: pathlib.Path = _OUT_DIR) -> Optional[dict]:
    """None if this scene has no cached map yet, OR its admission_version
    doesn't match this module's ADMISSION_VERSION (stale — computed
    against an old capacity/reachability definition). Both cases log one
    WARNING naming the scene and the specific reason, per this feature's
    "fail open, warn loud" rule — absence must never be silent, even
    though every caller is required to degrade gracefully when this
    returns None (see generation/anchor_reachability_filter.py and
    generation/manifest.py's build_manifest)."""
    path = out_dir / f"{scene_id}.json"
    if not path.exists():
        _logger.warning("anchor_admission: no cached map for scene %s (%s) — "
                         "reachability/capacity gates disabled for this generation run, "
                         "run scripts/compute_anchor_admission_map.py first", scene_id, path)
        return None
    admission_map = json.loads(path.read_text())
    version = admission_map.get("admission_version")
    if version != ADMISSION_VERSION:
        _logger.warning("anchor_admission: cached map for scene %s is stale "
                         "(admission_version=%r, expected %r) — "
                         "reachability/capacity gates disabled for this generation run, "
                         "rerun scripts/compute_anchor_admission_map.py",
                         scene_id, version, ADMISSION_VERSION)
        return None
    return admission_map


def is_reachable(admission_map: Optional[dict], anchor: str) -> Optional[bool]:
    """True/False if `anchor` is in the map, None if the map itself is
    None (no cache) or has no entry for this specific anchor (a
    genuinely unknown anchor — callers must treat this the same as "no
    cache", not as "known reachable" or "known unreachable")."""
    if admission_map is None:
        return None
    entry = admission_map["anchors"].get(anchor)
    return entry["reachable"] if entry is not None else None


def anchor_capacity(admission_map: Optional[dict], anchor: str) -> Optional[int]:
    """Object-count capacity for `anchor`, or None if the map is missing,
    the anchor is absent, or the anchor genuinely has no capacity budget
    (a region anchor — see this module's own docstring). None always
    means "no capacity gate applies here", never "zero capacity"."""
    if admission_map is None:
        return None
    entry = admission_map["anchors"].get(anchor)
    return entry["capacity"] if entry is not None else None
