"""
islands.py — shared navmesh-island-area primitive.

Extracted from embodied/world.py's `_on_small_island` and
embodied/reachability.py's `_own_island_area`, which computed the
identical `pf.get_island(pos)` -> `pf.island_area(island)` check
independently (Anchor Admission round, Stage 0). A third caller
(scripts/compute_anchor_admission_map.py) needs the exact same
primitive to precompute reachability, so this stopped being safe to
leave duplicated.

The two original call sites differ in one real respect, preserved here
rather than silently unified: embodied/world.py queries `get_island`
directly on the raw anchor position; embodied/reachability.py snaps to
the navmesh surface first via `pf.snap_point`. Which is correct depends
on whether `get_island` already does an internal nearest-point lookup
for an off-navmesh query (unconfirmed) — `snap_first` makes the choice
explicit per call site instead of guessing, so this dedup changes
neither site's real output.
"""
from __future__ import annotations


def island_area_at(pf, position: tuple[float, float, float], snap_first: bool = False) -> float:
    """Real island area (m^2) at `position`, or 0.0 if `position` has no
    valid island (`get_island` returns < 0 — off-navmesh entirely)."""
    pos = pf.snap_point(list(position)) if snap_first else list(position)
    island = pf.get_island(pos)
    return pf.island_area(island) if island >= 0 else 0.0


def is_reachable_island(
    pf, position: tuple[float, float, float], min_component_area_m2: float, snap_first: bool = False
) -> bool:
    """True if `position` sits on a navmesh island at or above
    `min_component_area_m2` — the connected-interior threshold
    (NavMeshConfig.min_component_area_m2), not a disqualified micro-
    fragment."""
    return island_area_at(pf, position, snap_first=snap_first) >= min_component_area_m2
