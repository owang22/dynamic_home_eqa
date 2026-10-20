"""
Scene inventory aggregation: category -> count.

The LLM receives a {category: count} dict, not raw instance lists.
This prevents the model from reasoning about specific object handles,
which are PARTNR internal identifiers that the LLM should never see.

Two backends:
  standalone  — reads from the CSV-based SceneState cache (no Habitat-sim).
  world_graph — reads live from a PARTNR WorldGraph (Habitat-sim running).

The LLM never receives object handles, room coordinates, or any geometry.
It receives only category names and counts, plus a room-level breakdown for
context (which rooms have which objects).
"""
from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from habitat_llm.world_model.world_graph import WorldGraph


# ---------------------------------------------------------------------------
# Standalone backend (CSV-based SceneState)
# ---------------------------------------------------------------------------

def inventory_from_scene_state(scene_id: str) -> dict[str, int]:
    """Return {category: count} for the generation stage.

    Combines physical furniture from the HSSD scene with assumed household
    items (phone, wallet, keys, drinkware, etc.) so the LLM can propose them.
    Does not require Habitat-sim.
    """
    from dynamic_home_eqa.env.inventory import inventory_for_generation
    return inventory_for_generation(scene_id)


def anchor_inventory_from_scene_state(scene_id: str) -> dict[str, int]:
    """Return {furniture_category: count} of real anchor-capable furniture in
    this scene (table, counter, bed, ... — see env.inventory.ANCHOR_CATEGORIES).

    This is the ground truth for on/within/next_to target_anchor validity —
    both the displacement schema's enum and the semantic grounder's existence
    check are built from this, so a target_anchor the model emits is
    guaranteed to correspond to furniture that actually exists in this scene.
    """
    from dynamic_home_eqa.env.inventory import anchor_inventory
    return anchor_inventory(scene_id)


def room_inventory_from_scene_state(scene_id: str) -> dict[str, dict[str, int]]:
    """Return {room: {category: count}} for the standalone backend.

    Room assignment is geometric: each instance's real HSSD translation is
    tested against the scene's actual region-volume annotations
    (generation/regions.py, sourced from semantic_config.json) via
    point-in-region. This surfaces every real HSSD region — bathroom, office,
    closet, gym, ... — not just the 3-4 rooms our own slot vocabulary names.

    Eligibility gate: an instance only counts toward a room if BOTH its
    geometric region AND its category's HSSD `foundIn` room tag (when known)
    are consistent. Region volume alone produces false positives at coarse
    region-box boundaries (e.g. a patio chair whose bounding box clips the
    adjoining office). foundIn coverage is sparse, so "unknown" is treated
    as "no signal" — the geometric assignment stands unchallenged rather than
    being dropped.

    Falls back to the old slot-prefix heuristic only when this scene has no
    region annotations, or an instance has no captured position.
    """
    from dynamic_home_eqa.env.inventory import load_scene_state, found_in_rooms
    from dynamic_home_eqa.generation.regions import load_scene_regions, region_for_point, rooms_match

    state = load_scene_state(scene_id)
    scene_regions = load_scene_regions(scene_id)

    room_counts: dict[str, Counter] = {}
    if scene_regions is not None:
        room_counts = {r.normalised: Counter() for r in scene_regions.regions}

    fallback: list = []  # instances geometry couldn't place
    for inst in state.instances.values():
        region = None
        if scene_regions is not None and inst.position is not None:
            region = region_for_point(inst.position, scene_regions)
        if region is None:
            fallback.append(inst)
            continue

        tags = found_in_rooms(inst.category)
        if tags and not any(rooms_match(region.normalised, t) for t in tags):
            # Geometry and category tag disagree — the coarse-region-box false
            # positive this gate exists to catch. Drop the instance from room
            # inventory rather than guessing which signal is right.
            continue

        room_counts.setdefault(region.normalised, Counter())[inst.category] += 1

    if fallback:
        for inst in fallback:
            slot = inst.current_semantic or ""
            room = slot.split(".")[0] if "." in slot else "unknown"
            room_counts.setdefault(room, Counter())[inst.category] += 1

    return {room: dict(c) for room, c in room_counts.items() if c}


# ---------------------------------------------------------------------------
# WorldGraph backend (live PARTNR scene)
# ---------------------------------------------------------------------------

def inventory_from_world_graph(world_graph: "WorldGraph") -> dict[str, int]:
    """Return {category: count} from a live PARTNR WorldGraph.

    Iterates object nodes in the graph. The LLM never receives handles or poses.
    """
    counts: Counter = Counter()
    for node in _iter_object_nodes(world_graph):
        cat = _object_category(node)
        if cat:
            counts[cat] += 1
    return dict(counts)


def room_inventory_from_world_graph(world_graph: "WorldGraph") -> dict[str, dict[str, int]]:
    """Return {room_name: {category: count}} from a live PARTNR WorldGraph."""
    room_counts: dict[str, Counter] = {}
    for node in _iter_object_nodes(world_graph):
        cat  = _object_category(node)
        room = _containing_room(node, world_graph)
        if cat and room:
            room_counts.setdefault(room, Counter())[cat] += 1
    return {room: dict(c) for room, c in room_counts.items()}


def _iter_object_nodes(world_graph: "WorldGraph"):
    """Yield object nodes from a WorldGraph using the available API."""
    # Try direct object_nodes attribute (WorldGraph v1)
    if hasattr(world_graph, "object_nodes"):
        yield from world_graph.object_nodes
        return
    # Try get_all_objects() method
    if hasattr(world_graph, "get_all_objects"):
        yield from world_graph.get_all_objects()
        return
    # Walk the graph from room nodes
    for room in _iter_room_nodes(world_graph):
        if hasattr(room, "object_nodes"):
            yield from room.object_nodes
        elif hasattr(room, "children"):
            for child in room.children:
                if hasattr(child, "object_nodes"):
                    yield from child.object_nodes
                else:
                    yield child


def _iter_room_nodes(world_graph: "WorldGraph"):
    if hasattr(world_graph, "room_nodes"):
        yield from world_graph.room_nodes
    elif hasattr(world_graph, "get_rooms"):
        yield from world_graph.get_rooms()


def _object_category(node) -> str | None:
    for attr in ("category", "object_category", "type", "object_type"):
        v = getattr(node, attr, None)
        if v:
            return str(v)
    return None


def _containing_room(node, world_graph: "WorldGraph") -> str | None:
    # Walk parent chain to find a room node
    parent = getattr(node, "parent", None) or getattr(node, "room", None)
    if parent is None:
        return None
    room_name = getattr(parent, "room_name", None) or getattr(parent, "name", None)
    if room_name:
        return str(room_name)
    # One more level up (object → receptacle → room)
    grandparent = getattr(parent, "parent", None)
    if grandparent:
        return str(getattr(grandparent, "room_name",
                           getattr(grandparent, "name", None)) or "unknown")
    return "unknown"


# ---------------------------------------------------------------------------
# Formatting for LLM prompts
# ---------------------------------------------------------------------------

def format_inventory_for_prompt(
    inventory: dict[str, int],
    room_inventory: dict[str, dict[str, int]] | None = None,
) -> str:
    """Produce a compact natural-language description of the scene inventory.

    The LLM uses this to propose which objects to move. Format is intentionally
    terse — the model needs category names and rough counts, not a full listing.
    """
    lines = ["Scene inventory (category: count):"]
    for cat, count in sorted(inventory.items(), key=lambda x: -x[1]):
        lines.append(f"  {cat}: {count}")
    if room_inventory:
        lines.append("\nBy room:")
        for room, cats in sorted(room_inventory.items()):
            top = sorted(cats.items(), key=lambda x: -x[1])[:5]
            lines.append(f"  {room}: " + ", ".join(f"{c}×{n}" for c, n in top))
    return "\n".join(lines)
