"""
world_graph_adapter.py — Bidirectional bridge between PARTNR's WorldGraph
and our SceneState.

This module is the only place that imports from habitat_llm so that the rest
of dynamic-eqa works standalone without Habitat-sim installed.

Key mappings:
  WorldGraph Object node   → SceneState ObjectInstance
  WorldGraph Furniture node → semantic slot string (via FURNITURE_TYPE_TO_SLOT)
  SceneState slot string   → WorldGraph Furniture node (via SLOT_TO_FURNITURE_TYPE)
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .state import SceneState, ObjectInstance
from .deltas import FURNITURE_TYPE_TO_SLOT, SLOT_TO_FURNITURE_TYPE, Change

if TYPE_CHECKING:
    from habitat_llm.world_model.world_graph import WorldGraph


def _furniture_to_slot(furniture_node) -> str:
    """Map a PARTNR Furniture node to our nearest semantic slot."""
    ftype = furniture_node.properties.get("type", "")
    # Try exact match first, then prefix match
    if ftype in FURNITURE_TYPE_TO_SLOT:
        return FURNITURE_TYPE_TO_SLOT[ftype]
    for key, slot in FURNITURE_TYPE_TO_SLOT.items():
        if key in ftype or ftype in key:
            return slot
    # Fallback: build a generic slot from room + furniture type
    return ftype.replace(" ", "_")


def _slot_to_furniture(
    slot: str,
    world_graph: "WorldGraph",
    prefer_room: Optional[str] = None,
) -> Optional[object]:
    """Find the best matching Furniture node in world_graph for a slot string."""
    from habitat_llm.world_model import Furniture

    target_types = SLOT_TO_FURNITURE_TYPE.get(slot, [])
    candidates = world_graph.get_all_furnitures()
    for ftype in target_types:
        for furn in candidates:
            ft = furn.properties.get("type", "")
            if ftype in ft or ft in ftype:
                if prefer_room is None:
                    return furn
                # filter by room if specified
                try:
                    room = world_graph.get_room_for_entity(furn)
                    if prefer_room.lower() in room.name.lower():
                        return furn
                except Exception:
                    pass
    # Return first candidate of any matching type
    for ftype in target_types:
        for furn in candidates:
            ft = furn.properties.get("type", "")
            if ftype in ft or ft in ftype:
                return furn
    return None


# ---------------------------------------------------------------------------
# WorldGraph → SceneState
# ---------------------------------------------------------------------------

def world_graph_to_scene_state(world_graph: "WorldGraph") -> SceneState:
    """Convert a PARTNR WorldGraph snapshot to a SceneState.

    Object location = the slot string for its parent Furniture node.
    Objects held by an agent or with unknown furniture are omitted.
    """
    from habitat_llm.world_model import Object as WGObject

    state = SceneState()
    for obj in world_graph.get_all_objects():
        # Skip objects held by agents
        if world_graph.is_object_with_agent(obj):
            continue
        furniture = world_graph.find_furniture_for_object(obj)
        if furniture is None:
            continue
        slot = _furniture_to_slot(furniture)
        cat  = obj.properties.get("type", obj.properties.get("category", "object"))
        state.instances[obj.name] = ObjectInstance(
            instance_id=obj.name,
            category=cat,
            current_semantic=slot,
        )
    return state


# ---------------------------------------------------------------------------
# SceneState → WorldGraph patch (apply changes)
# ---------------------------------------------------------------------------

def apply_change_to_world_graph(
    change: Change,
    world_graph: "WorldGraph",
) -> bool:
    """Apply a single Change to a PARTNR WorldGraph in place.

    Returns True if the change was applied, False if the target furniture
    could not be resolved.

    Only move_existing and insert_new are handled; remove is a no-op.
    """
    from habitat_llm.world_model import Object as WGObject, Receptacle as WGReceptacle

    if change.change_type == "remove":
        return True  # removal not modelled in WorldGraph

    target_furn = _slot_to_furniture(change.to_semantic, world_graph)
    if target_furn is None:
        return False

    # Find existing object node or create a stub
    obj_node = world_graph.get_node_from_name(change.instance_id) if hasattr(
        world_graph, "get_node_from_name"
    ) else None

    if obj_node is None:
        # Insert new stub object
        obj_node = WGObject(
            change.instance_id,
            {
                "type": change.object_category,
                "category": change.object_category,
                "translation": target_furn.properties.get("translation", [0, 0, 0]),
            },
        )
        world_graph.add_node(obj_node)

    # Rewire object → new furniture (remove old parent edge, add new one)
    old_furn = world_graph.find_furniture_for_object(obj_node)
    if old_furn is not None and old_furn != target_furn:
        try:
            world_graph.remove_edge(obj_node, old_furn)
            world_graph.remove_edge(old_furn, obj_node)
        except Exception:
            pass

    world_graph.add_edge(obj_node, target_furn, "on", "under")
    return True


# ---------------------------------------------------------------------------
# Snapshot list utilities (for harness)
# ---------------------------------------------------------------------------

def world_state_at(
    snapshots: list[tuple[float, "WorldGraph"]],
    t: float,
) -> Optional["WorldGraph"]:
    """Return the WorldGraph snapshot taken at or before time t.

    snapshots is a list of (timestamp, WorldGraph) pairs sorted by time.
    """
    best = None
    for ts, wg in snapshots:
        if ts <= t:
            best = wg
        else:
            break
    return best
