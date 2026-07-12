"""
inventory.py — Load initial SceneState from HSSD scene JSON + semantics CSV.

Two backends:
  Standalone (no Habitat-sim): reads HSSD scene_instance.json and semantics/objects.csv.
  WorldGraph-backed: converts a PARTNR WorldGraph to SceneState via world_graph_adapter.

The standalone path reads the same files as the original moving-object-eqa loader.
No pre-computed CSV cache files are required.

Object tiers
------------
Every object belongs to one of three tiers (see generation/README.md for the
full rationale). This module owns the tier vocabulary; which tier an object
belongs to determines whether it's present at scene-init, whether activities
can spawn/despawn it, and whether it's move_existing or insert_new in the
Change-log (generation/manifest.py). Collapsing tiers is exactly the bug this
split fixes: an object appearing because the generation schedule invented it
partway through the day was indistinguishable from an object appearing
because someone genuinely moved it.

  Tier 1 — TIER1_FURNITURE: real HSSD furniture (table, counter, bed, ...).
           Present from scene-init, never spawned/despawned/moved by
           activities. Anchors only — other tiers place onto these.

  Tier 2 — static clutter: present at scene-init, moved (never spawned or
           despawned) by activities. Two sub-sources, because HSSD's
           "uncluttered" scene variant (deliberately) omits small clutter:
             TIER2_HSSD_NATIVE — chair/stool/potted_plant/cushion. HSSD
               *does* place these in scenes-uncluttered/, with real
               positions, so they're loaded the same way Tier 1 is
               (load_scene_state). Chairs/stools are Tier 2 (not Tier 1)
               because they're still move-eligible (pulled out for a meal,
               tidiness governs whether they get tucked back) — the
               "anchor, never moved" property is specifically a Tier 1 thing.
             TIER2_CLUTTER_CATALOG — book/candle/vase/bowl/cup/drinkware/
               bottle. Not in HSSD's uncluttered scene JSON at all, so they
               have no ground-truth starting position; generation/clutter/
               invents one (a single LLM pass, before any activity/
               displacement stage runs) so they enter the scene the same way
               Tier 1/2-native furniture does — a real slot from t=0, not an
               insert_new event mid-timeline.

  Tier 3 — TIER3_MOBILE: phone/wallet/keys/laptop. Carried items that
           genuinely leave and re-enter observable space. Spawn/despawn
           mechanics are not yet implemented in the generation stages (still
           inserted once, like the old flat model) — see generation/README.md
           for that as an explicit follow-up, not silently assumed done.
"""
from __future__ import annotations

import csv
import json
import pathlib
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from .deltas import STATE_VARIABLES
from .state import SceneState, ObjectInstance

# --- Tier 1: static furniture — anchors only, never spawned/despawned/moved ---
# A curated subset of HSSD's ~85 main_category values: furniture-shaped and
# large enough to serve as a placement anchor, excluding small movable
# objects (cup, phone, ...) and non-anchor architecture (window, door, lamps,
# pictures, vehicles).
TIER1_FURNITURE: set[str] = {
    "table", "counter", "cabinet", "bed", "bench", "couch", "stand", "shelves",
    "wardrobe", "chest_of_drawers", "filing_cabinet", "fireplace", "sink",
    "tv", "toilet", "bathtub", "shower", "fridge", "dishwasher", "oven",
    "microwave", "range_hood", "washer_dryer", "trashcan",
}

# Tier 1 categories that additionally get an ObjectInstance + `states` dict
# tracked (M3: state-change dynamics) — category -> the one STATE_VARIABLES
# variable it carries. Tier 1 furniture is otherwise anchors-only (never
# spawned/despawned/moved by activities, see module docstring); this adds
# state tracking without adding location tracking — these instances never
# get a move_existing event, only state_change ones (generation/manifest.py).
STATEFUL_FURNITURE: dict[str, str] = {
    cat: variable for variable, spec in STATE_VARIABLES.items() for cat in spec["cats"]
}

# --- Tier 2a: static clutter HSSD already places (real position from JSON) ---
TIER2_HSSD_NATIVE: set[str] = {"chair", "stool", "potted_plant", "cushion"}

# Floor-Bound Realization round: categories that live on the FLOOR — a
# chair/stool gets pushed in next to a table, never lifted onto it. For
# these, surface relations (on/on_top/inside/within) are dropped at
# generation time (generation/pipeline.py, counted) and rejected by
# semantic grounding (defense-in-depth), and the builder realizes every
# event as a floor placement beside the anchor instance regardless of
# what a legacy manifest says. Deliberately NOT including potted_plant/
# cushion: a plant on a table or a cushion on a couch is normal life.
FLOOR_BOUND_CATEGORIES: set[str] = {"chair", "stool"}

# --- Tier 2b: static clutter HSSD's uncluttered variant omits — needs the
# clutter-generation pass (generation/clutter/) to invent a starting slot.
TIER2_CLUTTER_CATALOG: dict[str, int] = {
    "book":      3,
    "candle":    1,
    "vase":      1,
    "bowl":      2,
    "cup":       3,
    "drinkware": 2,
    "bottle":    2,
}

# --- Tier 3: mobile — carried, meant to spawn/despawn with activities ---
# (spawn/despawn not yet implemented — see module docstring)
TIER3_MOBILE: dict[str, int] = {
    "phone":  1,
    "wallet": 1,
    "keys":   1,
    "laptop": 1,
}

# HSSD dataset location.
from dynamic_home_eqa.paths import HSSD_DIR
_SEMANTICS_CSV = HSSD_DIR / "semantics" / "objects.csv"

# Heuristic initial semantic slot by Tier 2a (HSSD-native) category.
_DEFAULT_SEMANTIC: dict[str, str] = {
    "chair":        "dining.table_tucked",
    "stool":        "kitchen.counter_tucked",
    "potted_plant": "living_room.corner",
    "cushion":      "living_room.sofa",
}


@lru_cache(maxsize=1)
def _load_semantics() -> dict[str, str]:
    """Return {template_hash: main_category} from HSSD objects.csv."""
    mapping: dict[str, str] = {}
    if not _SEMANTICS_CSV.exists():
        return mapping
    with open(_SEMANTICS_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            h   = row.get("id", "").strip()
            cat = row.get("main_category", "").strip()
            if h and cat:
                mapping[h] = cat
    return mapping


@lru_cache(maxsize=1)
def _load_found_in() -> dict[str, set[str]]:
    """Return {main_category: {normalised room tag, ...}} from HSSD objects.csv's
    'foundIn' column (a knowledge-base annotation of the rooms a category is
    typically found in — not per-instance ground truth).

    Aggregated across every template of a category, since our own instances
    are only resolved to category granularity. Categories with no foundIn
    data anywhere (most of them) are simply absent — callers must treat
    missing data as "no signal", not "inconsistent".
    """
    tags: dict[str, set[str]] = {}
    if not _SEMANTICS_CSV.exists():
        return tags
    with open(_SEMANTICS_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row.get("main_category", "").strip()
            found_in = row.get("foundIn", "").strip()
            if not cat or not found_in:
                continue
            rooms = {r.strip().lower().replace(" ", "_") for r in found_in.split(",") if r.strip()}
            tags.setdefault(cat, set()).update(rooms)
    return tags


def found_in_rooms(category: str) -> set[str]:
    """Normalised room-tag set HSSD associates with `category`, or empty if unknown."""
    return _load_found_in().get(category, set())


@lru_cache(maxsize=256)
def load_scene_state(scene_id: str) -> SceneState:
    """Build initial SceneState from Tier 2a (TIER2_HSSD_NATIVE) instances in
    the HSSD scene_instance.json — the only tier HSSD's uncluttered scene
    variant actually places for us — plus one ObjectInstance per present
    STATEFUL_FURNITURE category (M3: state-change dynamics; Tier 1,
    anchors-only, never move_existing — see STATEFUL_FURNITURE's docstring).

    No Habitat-sim required. Each Tier 2a instance gets a heuristic semantic
    slot based on category; generation/manifest.py overwrites these from the
    day's from_semantic field on first occurrence. Tier 2b clutter (not in
    this JSON at all) is added separately by generation/clutter/ and merged
    in by generation/manifest.py — this function only ever returns Tier 2a
    plus the stateful-furniture instances described above.
    """
    scene_path = HSSD_DIR / "scenes-uncluttered" / f"{scene_id}.scene_instance.json"
    if not scene_path.exists():
        return SceneState()

    with open(scene_path) as f:
        data = json.load(f)

    sem      = _load_semantics()
    state    = SceneState()
    counters: dict[str, int] = {}
    stateful_seen: set[str] = set()  # only the first real instance per category is tracked

    for obj in data.get("object_instances", []):
        template_hash = obj.get("template_name", "")
        category      = sem.get(template_hash)
        translation   = obj.get("translation")
        position      = tuple(translation) if translation and len(translation) == 3 else None

        if category in STATEFUL_FURNITURE and category not in stateful_seen:
            stateful_seen.add(category)
            variable = STATEFUL_FURNITURE[category]
            off_value = STATE_VARIABLES[variable]["values"][0]
            state.instances[f"{category}_1"] = ObjectInstance(
                instance_id=f"{category}_1",
                category=category,
                current_semantic=category,  # bare category name -> rooms.slot_room()
                                             # resolves it via CATEGORY_ROOM_HINT; never
                                             # moves, so no dotted slot is needed.
                position=position,
                states={variable: off_value},
            )

        if category is None or category not in TIER2_HSSD_NATIVE:
            continue
        n  = counters.get(category, 0) + 1
        counters[category] = n
        iid = f"{category}_{n}"
        state.instances[iid] = ObjectInstance(
            instance_id=iid,
            category=category,
            current_semantic=_DEFAULT_SEMANTIC.get(category, ""),
            position=position,
        )

    return state


@lru_cache(maxsize=256)
def load_furniture_census(scene_id: str) -> dict[str, list[tuple[float, float, float]]]:
    """Return {main_category: [position, ...]} for every TIER1_FURNITURE
    object in the scene.

    This is ground truth for "does this scene actually have a desk/counter/bed
    to place something on" — used to validate a displacement's target_anchor
    for on/within/next_to relations, and as the anchor vocabulary for the
    Tier 2b clutter-placement pass. Tier 1 only: Tier 2 objects are never
    anchors (see module docstring) and have their own position source.
    """
    scene_path = HSSD_DIR / "scenes-uncluttered" / f"{scene_id}.scene_instance.json"
    if not scene_path.exists():
        return {}

    with open(scene_path) as f:
        data = json.load(f)

    sem = _load_semantics()
    census: dict[str, list[tuple[float, float, float]]] = {}
    for obj in data.get("object_instances", []):
        category = sem.get(obj.get("template_name", ""))
        if category is None or category not in TIER1_FURNITURE:
            continue
        translation = obj.get("translation")
        if not translation or len(translation) != 3:
            continue
        census.setdefault(category, []).append(tuple(translation))
    return census


def anchor_inventory(scene_id: str) -> dict[str, int]:
    """{category: count} view of load_furniture_census, for schema/grounding use."""
    return {cat: len(positions) for cat, positions in load_furniture_census(scene_id).items()}


@dataclass(frozen=True)
class FurnitureInstance:
    """One real TIER1_FURNITURE object, at instance (not category)
    granularity — supplements load_furniture_census (kept unchanged, both
    of its existing callers want the category->position-list shape) for
    the anchor census (env/anchor_census.py), which needs to join a
    receptacle set and a room label onto ONE specific furniture piece.

    `index` is this instance's position in scene_instance.json's
    object_instances array — stable and deterministic across runs of the
    same scene file (the file doesn't reorder itself), used only as a
    secondary/debugging identifier. `position` is the real join key: the
    same "resolve the live rigid object at this position"
    (find_live_object_at_xz) mechanism build_realized_day.py already uses
    everywhere else in this codebase, not a persisted live habitat_sim
    handle string (those are session-ephemeral — safe to use as a sort
    key at census-BUILD time, unsafe to persist into a cross-session
    JSON cache and expect to resolve later)."""
    index: int
    category: str
    position: tuple[float, float, float]


@lru_cache(maxsize=256)
def load_furniture_instances(scene_id: str) -> tuple[FurnitureInstance, ...]:
    """Instance-level sibling of load_furniture_census: one FurnitureInstance
    per real TIER1_FURNITURE object_instances entry, in file order. Same
    source data (scene_instance.json + HSSD semantics CSV), same TIER1_FURNITURE
    filter, same position/translation validity check — this does not
    reimplement the read, it just stops collapsing to category->positions
    before returning."""
    scene_path = HSSD_DIR / "scenes-uncluttered" / f"{scene_id}.scene_instance.json"
    if not scene_path.exists():
        return ()

    with open(scene_path) as f:
        data = json.load(f)

    sem = _load_semantics()
    instances: list[FurnitureInstance] = []
    for idx, obj in enumerate(data.get("object_instances", [])):
        category = sem.get(obj.get("template_name", ""))
        if category is None or category not in TIER1_FURNITURE:
            continue
        translation = obj.get("translation")
        if not translation or len(translation) != 3:
            continue
        instances.append(FurnitureInstance(index=idx, category=category, position=tuple(translation)))
    return tuple(instances)


def inventory_for_generation(scene_id: str) -> dict[str, int]:
    """Return {category: count} for the LLM generation stages, *before* the
    Tier 2b clutter-placement pass has run.

    Combines Tier 2a instances actually found in the HSSD scene with assumed
    Tier 3 mobile items (phone, keys, ...) — this is deliberately narrower
    than the old flat model: Tier 2b clutter (book, candle, vase, ...) is
    NOT assumed present here anymore. It only enters the inventory once
    generation/clutter/ has actually placed it in this specific scene (see
    generation/pipeline.py, which merges the clutter pass's output into this
    dict before the displacement stage runs). Assuming Tier 2b items exist
    unconditionally was exactly the bug the tier split fixes: an object
    "existing" only because a hardcoded catalog said so, not because
    anything actually placed it.
    """
    state  = load_scene_state(scene_id)
    counts: dict[str, int] = {}
    for inst in state.instances.values():
        counts[inst.category] = counts.get(inst.category, 0) + 1
    # Tier 3 is still a flat per-scene assumption (spawn/despawn not yet
    # implemented — see module docstring), so it's fine to merge unconditionally.
    for cat, n in TIER3_MOBILE.items():
        counts[cat] = max(counts.get(cat, 0), n)
    return counts


def load_scene_state_from_world_graph(world_graph) -> SceneState:
    """Convert a PARTNR WorldGraph to SceneState."""
    from .world_graph_adapter import world_graph_to_scene_state
    return world_graph_to_scene_state(world_graph)
