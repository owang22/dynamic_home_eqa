"""
anchor_census.py — read-side schema + cache accessors for the per-scene
realizable-anchor census (Realizable-Anchor Vocabulary round, Part 1).

Pure, no habitat imports — this module is consumed by generation/*.py,
which must stay habitat_sim-free at runtime (see generation/inventory.py's
own module docstring for the same constraint, and env/anchor_admission.py
for the identical pattern this file mirrors). The census itself is
PRODUCED by scripts/compute_anchor_census.py, which does need a real sim
(receptacle lookup reuses build_realized_day.py's find_receptacles
machinery) and is never imported from here.

One record per real TIER1_FURNITURE instance that geometry could assign
to a region (instances with no region volume at all are recorded
separately, under "excluded_no_region", not silently dropped and not
included in "anchors"):
  - room: the real per-scene HSSD region name (deduplicated — two regions
    normalising to "bedroom" become "bedroom_1"/"bedroom_2", see the
    compute script's own docstring), NOT gated against the foundIn
    consistency check generation/inventory.py's room_inventory_from_scene_state
    applies for movable-object room COUNTING. That gate exists to catch a
    coarse-region-box false positive for something that might genuinely
    be elsewhere; an anchor's geometric room IS where it is — a table
    whose real position is inside the geometric "garage" region is a
    garage anchor, full stop, whatever a hand-authored per-category tag
    list says tables are typically found in.
  - active_receptacles / raw_receptacles: from find_receptacles(sim) +
    the scene's .rec_filter.json curated "active" list — active is what
    the real build (build_realized_day.resolve_furniture_receptacles)
    would actually place on; raw is what geometry alone authored, before
    curation. curated_out = raw>0 and active==0 (receptacle geometry
    exists but every candidate was manually/access/stability filtered by
    the dataset's own curators — a real, human-authored exclusion, not a
    gap in this census).
  - position: the join key for re-resolving this exact instance's live
    rigid object in a fresh sim session (find_live_object_at_xz — the
    same mechanism build_realized_day.py already uses everywhere else for
    "the real object here"), not a persisted live habitat_sim handle
    string (session-ephemeral, unsafe to cache across runs).

Two views generation needs (surface_anchor_labels / proximity_anchor_labels
below) are computed on demand from the one flat `anchors` dict, not stored
as separate duplicated sections — every surface anchor (active_receptacles
>= 1) is also a valid proximity anchor (every room-tagged instance,
receptacle or not), so storing both would just be two copies of overlapping
data that could drift apart.

CENSUS_VERSION is a manual constant, not a content hash of
compute_anchor_census.py — see anchor_admission.py's identical rationale
for why (every unrelated script edit would otherwise silently invalidate
every cached census under this feature's fail-open design).
"""
from __future__ import annotations

import json
import logging
import pathlib
import re
from typing import Optional

_logger = logging.getLogger(__name__)

CENSUS_VERSION = 2  # v1 -> v2: bed rule — a region containing a real `bed`
                     # instance is decisively labeled a bedroom (Checkpoint A1
                     # review outcome; the fixture scene's three HSSD-labeled
                     # "office" regions each hold a bed+wardrobe+stand). See
                     # scripts/compute_anchor_census.py's own docstring.

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA
_OUT_DIR = _DYNAMIC_EQA / "data" / "anchor_census"


def save_anchor_census(census: dict, out_dir: pathlib.Path = _OUT_DIR) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{census['scene_id']}.json"
    path.write_text(json.dumps(census, indent=2))
    return path


def load_anchor_census(scene_id: str, out_dir: pathlib.Path = _OUT_DIR) -> Optional[dict]:
    """None if this scene has no cached census yet, OR its census_version
    doesn't match this module's CENSUS_VERSION (stale). Both cases log one
    WARNING naming the scene and the specific reason, per the same "fail
    open, warn loud" rule anchor_admission.py uses — absence must never be
    silent, even though every caller is required to degrade gracefully
    when this returns None."""
    path = out_dir / f"{scene_id}.json"
    if not path.exists():
        _logger.warning("anchor_census: no cached census for scene %s (%s) — "
                         "run scripts/compute_anchor_census.py first", scene_id, path)
        return None
    census = json.loads(path.read_text())
    version = census.get("census_version")
    if version != CENSUS_VERSION:
        _logger.warning("anchor_census: cached census for scene %s is stale "
                         "(census_version=%r, expected %r) — rerun "
                         "scripts/compute_anchor_census.py",
                         scene_id, version, CENSUS_VERSION)
        return None
    return census


def resolve_anchor(census: Optional[dict], label: str) -> Optional[dict]:
    """The full record for `label` ({category, room, position,
    active_receptacles, raw_receptacles, curated_out}), or None if the
    census is missing or has no such label. build_realized_day.py's
    classify_anchor/resolve_anchor_position use this as the direct
    dictionary lookup that replaces category->nearest-instance guessing —
    the census already did that resolution once, at compute time, with a
    real per-instance join."""
    if census is None:
        return None
    return census["anchors"].get(label)


def surface_anchor_labels(census: Optional[dict], room: str) -> list[str]:
    """Labels in `room` with at least one active (curated-in) receptacle —
    legal targets for on/on_top/inside/within relations. Sorted for a
    deterministic schema enum."""
    if census is None:
        return []
    return sorted(
        label for label, rec in census["anchors"].items()
        if rec["room"] == room and rec["active_receptacles"] >= 1
    )


def proximity_anchor_labels(census: Optional[dict], room: str) -> list[str]:
    """Every room-tagged instance in `room`, receptacle or not — legal
    targets for near/next_to (proximity needs a position, not a surface).
    This is how fridge/tv/oven (structurally receptacle-less, see the
    compute script's own coverage numbers) stay usable for next_to and
    state_change while being impossible to place things ON (never appear
    in surface_anchor_labels). Sorted for a deterministic schema enum."""
    if census is None:
        return []
    return sorted(label for label, rec in census["anchors"].items() if rec["room"] == room)


_ROOM_SUFFIX_RE = re.compile(r"_\d+$")


def census_anchor_vocabulary(census: Optional[dict], location: Optional[str] = None) -> tuple[list[str], list[str]]:
    """(surface_labels, proximity_labels) — the two schema enums, scoped to
    the census rooms matching `location` (a canonical activity location;
    matched against each room's base name with the _N dedup suffix
    stripped, via rooms.rooms_match — so location "bedroom" collects
    bedroom_1/bedroom_2, "living_room" collects the "tv" room via the same
    aliasing everything else uses). location=None -> scene-wide (the
    clutter pass, which has no occupant room to scope by). Census rooms
    that match no canonical location (garage, closet, other_room) are
    simply never offered for a located activity — correct, not a gap.
    Both lists sorted for deterministic schema enums."""
    if census is None:
        return [], []
    from ..rooms import rooms_match

    surface: list[str] = []
    proximity: list[str] = []
    for label, rec in census["anchors"].items():
        if location is not None and not rooms_match(_ROOM_SUFFIX_RE.sub("", rec["room"]), location):
            continue
        proximity.append(label)
        if rec["active_receptacles"] >= 1:
            surface.append(label)
    return sorted(surface), sorted(proximity)


def rooms_present(census: Optional[dict]) -> list[str]:
    """Every real per-scene room name this census has at least one anchor
    for — the room-name vocabulary a caller can validate `location`
    against before calling the two functions above."""
    if census is None:
        return []
    return sorted({rec["room"] for rec in census["anchors"].values()})
