"""
regions.py — Load and query per-scene HSSD region volume annotations.

Replaces the prefix-derived `known_rooms` string set used by the semantic
grounder with actual data from the HSSD semantic_config.json files, one per
scene. Region names are normalised (lowercase, spaces→underscores, .001-style
suffixes stripped) so that LLM-proposed anchors like "bedroom" match any of
"bedroom", "bedroom.001", "bedroom.002", etc.

For `in_region` proposals, the semantic grounder calls `anchor_matches_region`
which does a normalised-name lookup against the scene's actual region list. This
is purely name-based (no geometry) and therefore works without Habitat-sim.

The full 3D point-in-region test uses `poly_loop` + floor/extrusion geometry
from the JSON (or `SemanticRegion.contains()` at runtime), but is only needed
for sim-based grounding where object positions are available.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

from ..rooms import normalise_room_name as _normalise_region_name, rooms_match

# ---------------------------------------------------------------------------
# HSSD path — mirrors env/inventory.py
# ---------------------------------------------------------------------------

from dynamic_home_eqa.paths import HSSD_DIR as _HSSD_DIR
_SEMANTICS_DIR = _HSSD_DIR / "semantics" / "scenes"

# ---------------------------------------------------------------------------
# Region data
# ---------------------------------------------------------------------------

@dataclass
class RegionVolume:
    """One semantic region from HSSD's semantic_config.json."""
    name: str                          # Raw name from JSON, e.g. "bedroom.001"
    label: str                         # Semantic label, e.g. "bedroom/guest"
    normalised: str                    # Normalised: "bedroom"
    poly_loop: list[tuple[float, float]]  # [(x, z), ...] floor polygon (Y dropped)
    floor_height: float
    extrusion_height: float
    min_bounds: list[float]            # [xmin, ymin, zmin]
    max_bounds: list[float]            # [xmax, ymax, zmax]


@dataclass
class SceneRegions:
    """All region volumes for one HSSD scene."""
    scene_id: str
    regions: list[RegionVolume] = field(default_factory=list)
    # Set of normalised names for fast lookup
    _norm_names: set[str] = field(default_factory=set, repr=False)

    def has_region(self, name: str) -> bool:
        """Return True if any region in this scene matches `name` after normalisation."""
        return _normalise_region_name(name) in self._norm_names

    def matching_regions(self, name: str) -> list[RegionVolume]:
        """Return all RegionVolume entries whose normalised name matches `name`."""
        norm = _normalise_region_name(name)
        return [r for r in self.regions if r.normalised == norm]

    @property
    def all_normalised(self) -> set[str]:
        return set(self._norm_names)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

@lru_cache(maxsize=256)
def load_scene_regions(scene_id: str) -> Optional[SceneRegions]:
    """Load region annotations for one HSSD scene.

    Returns None if the semantic_config.json doesn't exist for this scene.
    Results are cached so repeated calls for the same scene are free.
    """
    cfg_path = _SEMANTICS_DIR / f"{scene_id}.semantic_config.json"
    if not cfg_path.exists():
        return None

    try:
        data = json.loads(cfg_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    regions: list[RegionVolume] = []
    for entry in data.get("region_annotations", []):
        name  = entry.get("name", "")
        label = entry.get("label", "")
        poly  = [(pt[0], pt[2]) for pt in entry.get("poly_loop", [])]  # drop Y
        floor_h = float(entry.get("floor_height", 0.0))
        ext_h   = float(entry.get("extrusion_height", 2.8))
        mn = entry.get("min_bounds", [0.0, 0.0, 0.0])
        mx = entry.get("max_bounds", [0.0, 0.0, 0.0])
        regions.append(RegionVolume(
            name=name,
            label=label,
            normalised=_normalise_region_name(name),
            poly_loop=poly,
            floor_height=floor_h,
            extrusion_height=ext_h,
            min_bounds=list(mn),
            max_bounds=list(mx),
        ))

    sr = SceneRegions(scene_id=scene_id, regions=regions)
    sr._norm_names = {r.normalised for r in regions}
    return sr


# ---------------------------------------------------------------------------
# Semantic anchor check (no sim required)
# ---------------------------------------------------------------------------

def anchor_matches_region(anchor: str, scene_regions: SceneRegions) -> bool:
    """Return True if `anchor` maps to any region present in this scene.

    Normalises both sides so "Living Room" matches "living room" or
    "living room.001".  Also tries common aliases (see rooms_match).
    """
    return any(rooms_match(anchor, r) for r in scene_regions.all_normalised)


# rooms_match is imported from ..rooms (see module docstring) — re-exported
# here since inventory.py and grounding.py import it from this module.

# ---------------------------------------------------------------------------
# 3D point-in-region test (for sim-based grounding)
# ---------------------------------------------------------------------------

def point_in_region(point: tuple[float, float, float],
                    region: RegionVolume) -> bool:
    """Return True if point (x, y, z) lies within the region's 3D volume.

    The volume is defined as the extrusion of the poly_loop polygon from
    floor_height to floor_height + extrusion_height, tested via AABB first
    (fast rejection) then point-in-polygon on the XZ plane.
    """
    x, y, z = point
    # AABB fast rejection
    mn, mx = region.min_bounds, region.max_bounds
    if not (mn[0] <= x <= mx[0] and mn[1] <= y <= mx[1] and mn[2] <= z <= mx[2]):
        return False
    # Height range
    if not (region.floor_height <= y <= region.floor_height + region.extrusion_height):
        return False
    # Point-in-polygon on XZ plane (ray casting)
    return _point_in_polygon_xz(x, z, region.poly_loop)


def region_for_point(
    point: tuple[float, float, float],
    scene_regions: SceneRegions,
) -> Optional[RegionVolume]:
    """Return the RegionVolume containing `point`, or None if it falls in none.

    Real per-scene geometry, not slot-name string matching — this is what lets
    room assignment work for every HSSD region (bathroom, office, closet, ...),
    not just the handful with a hand-picked slot-prefix mapping.

    Region volumes can overlap at coarse boundaries (open-plan kitchen/dining,
    adjoining hallways); the first match wins, so ties are resolved by
    region_annotations order in the source JSON. This is a documented,
    accepted source of residual noise, not a claim of perfect disambiguation.
    """
    for region in scene_regions.regions:
        if point_in_region(point, region):
            return region
    return None


def _point_in_polygon_xz(px: float, pz: float,
                          polygon: list[tuple[float, float]]) -> bool:
    """Ray-casting point-in-polygon test on the XZ plane."""
    n = len(polygon)
    if n < 3:
        return False
    inside = False
    j = n - 1
    for i in range(n):
        xi, zi = polygon[i]
        xj, zj = polygon[j]
        if ((zi > pz) != (zj > pz)) and (px < (xj - xi) * (pz - zi) / (zj - zi) + xi):
            inside = not inside
        j = i
    return inside
