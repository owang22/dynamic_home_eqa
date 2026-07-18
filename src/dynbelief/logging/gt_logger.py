"""Stage 0.1 — ground-truth logger.

The "object-state update loop" of this simulation is the manifest replay
(dynamic_home_eqa.env.replay): each generated sim-day is a manifest of
committed change events over a known initial state. This module hooks that
loop as a consumer — it converts one or more day folders (manifest.json +
generation_result.json) into the episode log format every downstream
dynbelief stage reads:

  logs/<episode>/events.jsonl        one record per change event
  logs/<episode>/snapshot_day<k>.json  full parent map + states at day start
  logs/<episode>/registry.json       label<->int id maps, receptacle rooms/
                                     positions, day count, scene id

Record schema (brief 0.1):
  {"t_min": int, "object_id": int, "parent_id": int,
   "states": {str: bool}, "moved_by": "human"|"robot"|"init"}

Conventions and adaptations (documented, not silent):
  - t_min = day*1440 + round(hour*60). Day k spans [k*1440, (k+1)*1440).
  - Receptacle ids come from the scene's anchor census (room-qualified
    instance labels, e.g. "kitchen.counter_1"). A resolved slot's ".tucked"
    suffix is stripped — tucked-under and beside are the same parent
    receptacle for belief purposes. Receptacle id 0 is ELSEWHERE: the
    manifest's "away" (put-away / concealed-in-storage removes) and any
    object not yet in the scene.
  - The generator produces INDEPENDENT days (each day restarts from the
    household's canonical start state; there is no overnight simulation).
    To keep the invariant "event replay == day-boundary snapshots" true —
    which downstream tests assert — the logger emits explicit `moved_by:
    "init"` reset events at each day boundary for every object whose
    day-(k) start parent differs from its day-(k-1) end parent. This models
    the overnight reset as observable events rather than hiding a
    discontinuity.
  - `states`: this pipeline's manifests carry location changes; furniture
    state_change events (open/closed etc.) exist in the schema but are not
    generated in the current datasets. state_change events update the
    states dict (value coerced: to_state equal to the variable's first
    listed value -> True) and re-assert the unchanged parent.
  - moved_by: every manifest change has a human mover -> "human". The robot
    never moves objects in replay. Day-start snapshot rows and boundary
    resets -> "init".
  - Exactly-one-parent invariant is asserted on every event and snapshot.
"""
from __future__ import annotations

import json
import pathlib
from typing import Optional

from dynbelief import ELSEWHERE_ID, ELSEWHERE_LABEL, MIN_PER_DAY

_AWAY_TOKENS = {"away", "", None}


def _slot_to_receptacle(slot: Optional[str]) -> str:
    """Resolved slot string -> parent receptacle label (census anchor), or
    ELSEWHERE_LABEL. Strips the ".tucked" sub-slot suffix."""
    if slot in _AWAY_TOKENS:
        return ELSEWHERE_LABEL
    if slot.endswith(".tucked"):
        return slot[: -len(".tucked")]
    return slot


def _clutter_start_parents(gen_result: dict, scene_id: str) -> dict[str, str]:
    """Label -> start receptacle for the day's Tier-2b clutter placements,
    mirroring build_manifest's clutter_counters numbering (same iteration
    order) and resolve_slot resolution — the same contract the realized-day
    builder (v6 clutter starts) and RunningState.seed_clutter follow."""
    from dynamic_home_eqa.rooms import resolve_slot
    from dynamic_home_eqa.topdown_map import instance_room_positions

    room_cats = {room: set(cats) for room, cats
                 in instance_room_positions(scene_id).items()}
    counters: dict[str, int] = {}
    out: dict[str, str] = {}
    for p in gen_result.get("clutter", []):
        cat = p["object_category"]
        counters[cat] = counters.get(cat, 0) + 1
        label = f"{cat}_{counters[cat]}"
        try:
            slot = resolve_slot(p["target_anchor"], p["target_relationship"],
                                room_instance_categories=room_cats)
        except Exception:
            slot = p["target_anchor"]
        out[label] = _slot_to_receptacle(slot)
    return out


def _day_start_parents(manifest: dict, gen_result: dict) -> dict[str, str]:
    """Full parent map at this day's t=0: replay initial state (movable
    instances with their corrected start slots) + clutter starts. Labels
    with an insert_new event start at ELSEWHERE (they do not exist yet) —
    except clutter-numbered labels, whose insert_new is the abundant-storage
    spawn of a NEW instance and whose lower-numbered siblings already sit at
    their clutter slots."""
    from dynamic_home_eqa.env.replay import initial_state_and_changes_from_manifest

    state, _ = initial_state_and_changes_from_manifest(manifest)
    parents: dict[str, str] = {}
    for label, inst in state.instances.items():
        parents[label] = _slot_to_receptacle(inst.current_semantic)
    parents.update(_clutter_start_parents(gen_result, manifest["scene_id"]))
    # Volatile / spawned labels present in changes but absent above start
    # at ELSEWHERE until their insert_new fires.
    for c in manifest.get("changes", []):
        parents.setdefault(c["label"], ELSEWHERE_LABEL)
    return parents


def _day_events(manifest: dict, day: int,
                parents: dict[str, str],
                states: dict[str, dict[str, bool]]) -> list[dict]:
    """Apply this day's manifest changes to `parents`/`states` in t order,
    emitting one event record per change. Mutates parents/states to the
    end-of-day state."""
    events: list[dict] = []
    for c in sorted(manifest.get("changes", []), key=lambda c: float(c["t"])):
        label = c["label"]
        # clamp past-midnight wraps (t in (24, 30)h is legal in the
        # manifests — late-night activity) into this day's final minute:
        # days are independent here, so letting a 26.4h event roll into
        # day+1 would inject it BEFORE that day's real morning events and
        # break the boundary-reset invariant (stage1c dataset_report flag)
        t_min = day * MIN_PER_DAY + min(int(round(float(c["t"]) * 60.0)),
                                        MIN_PER_DAY - 1)
        if c["change_type"] == "state_change":
            var = c.get("state_variable")
            if var is not None:
                from dynamic_home_eqa.env.deltas import STATE_VARIABLES
                first_val = STATE_VARIABLES.get(var, {}).get("values", [None])[0]
                states.setdefault(label, {})[var] = (c.get("to_state") == first_val)
            parent = parents.get(label, ELSEWHERE_LABEL)
        elif c["change_type"] == "remove":
            parent = ELSEWHERE_LABEL
        else:  # move_existing / insert_new
            parent = _slot_to_receptacle(c.get("to_semantic"))
        parents[label] = parent
        events.append({
            "t_min": t_min, "label": label, "parent_label": parent,
            "states": dict(states.get(label, {})), "moved_by": "human",
        })
    return events


def log_episode(gen_dir: pathlib.Path, folders: list[str],
                out_dir: pathlib.Path) -> pathlib.Path:
    """Convert an ordered list of day folders (one household, days 0..N-1)
    into logs/<episode>/. Returns the episode directory."""
    gen_dir = pathlib.Path(gen_dir)
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scene_id: Optional[str] = None
    all_events: list[dict] = []
    snapshots: list[dict] = []
    prev_end_parents: Optional[dict[str, str]] = None
    states: dict[str, dict[str, bool]] = {}
    object_labels: set[str] = set()
    receptacle_labels: set[str] = set()

    # True day index comes from the folder suffix (_day<k>), falling back to
    # list position: a day that failed trace validation leaves a GAP, and
    # position-indexing would silently shift every later day's calendar
    # (day-of-week!) — the exact corruption the stage1c weekly component
    # cannot tolerate.
    import re as _re
    indexed = []
    for pos, folder in enumerate(folders):
        m = _re.search(r"_day(\d+)$", folder)
        indexed.append((int(m.group(1)) if m else pos, folder))
    indexed.sort()
    logged_days = [d for d, _f in indexed]
    # Receptacle-LABEL prefix canonicalization (alias fix, part 2). Legacy
    # hand-authored slots spell rooms differently from census labels
    # ("dining.table_tucked" vs "dining_room.table_1"), so the model-facing
    # vocabulary showed one room under two names. Rewrite a label's prefix to
    # the census room iff the prefix is a ROOM word (not a furniture/appliance
    # category like fridge/tv — "fridge.inside" reads naturally and its room
    # is handled by the room-projection fix) that alias-matches exactly one
    # census room. Bijective per scene, applied at every label entry point.
    from dynamic_home_eqa.rooms import CATEGORY_ROOM_HINT as _CRH, rooms_match as _rm
    from dynamic_home_eqa.env.anchor_census import load_anchor_census
    _census_rooms_early = None
    _label_map: dict[str, str] = {}

    def _canon_label(lbl: str) -> str:
        nonlocal _census_rooms_early
        if lbl in _label_map:
            return _label_map[lbl]
        out = lbl
        if "." in lbl:
            prefix, _, rest = lbl.partition(".")
            if _census_rooms_early is None:
                _c = load_anchor_census(scene_id) or {"anchors": {}}
                _census_rooms_early = sorted({a.get("room") for a in
                                              _c["anchors"].values() if a.get("room")})
            if (prefix not in _census_rooms_early
                    and prefix not in _CRH):
                m = [r for r in _census_rooms_early if _rm(prefix, r)]
                if len(m) == 1:
                    out = f"{m[0]}.{rest}"
        _label_map[lbl] = out
        return out

    for day, folder in indexed:
        manifest = json.loads((gen_dir / folder / "manifest.json").read_text())
        gen_result = json.loads((gen_dir / folder / "generation_result.json").read_text())
        if scene_id is None:
            scene_id = manifest["scene_id"]
        assert manifest["scene_id"] == scene_id, "episode must be one scene"

        parents = _day_start_parents(manifest, gen_result)
        parents = {o: _canon_label(v) if v != ELSEWHERE_LABEL else v
                   for o, v in parents.items()}
        object_labels.update(parents)
        receptacle_labels.update(v for v in parents.values() if v != ELSEWHERE_LABEL)

        # Day-boundary reset events (independent-days adaptation, see module
        # docstring): every difference between day-(k-1) end and day-k start
        # becomes an explicit "init" event at exactly the boundary minute.
        if prev_end_parents is not None:
            t_boundary = day * MIN_PER_DAY
            for label in sorted(set(prev_end_parents) | set(parents)):
                before = prev_end_parents.get(label, ELSEWHERE_LABEL)
                after = parents.get(label, ELSEWHERE_LABEL)
                if before != after:
                    all_events.append({
                        "t_min": t_boundary, "label": label, "parent_label": after,
                        "states": dict(states.get(label, {})), "moved_by": "init",
                    })

        snapshots.append({
            "t_min": day * MIN_PER_DAY, "day": day,
            "parents": dict(sorted(parents.items())),
            "states": {k: dict(v) for k, v in states.items() if v},
        })

        day_events = _day_events(manifest, day, parents, states)
        for e in day_events:
            if e["parent_label"] != ELSEWHERE_LABEL:
                e["parent_label"] = _canon_label(e["parent_label"])
        receptacle_labels.update(e["parent_label"] for e in day_events
                                 if e["parent_label"] != ELSEWHERE_LABEL)
        object_labels.update(e["label"] for e in day_events)
        all_events.extend(day_events)
        # _day_events mutates `parents` to end-of-day state using RAW manifest
        # labels — re-canonicalize before it becomes the boundary reference,
        # else the midnight reset sees phantom alias diffs
        prev_end_parents = {o: (_canon_label(v) if v != ELSEWHERE_LABEL else v)
                            for o, v in parents.items()}

    # ---- registry: stable int ids ------------------------------------------
    census = load_anchor_census(scene_id) or {"anchors": {}}
    # Receptacle vocabulary = every census anchor (the full candidate set the
    # brief requires) plus anything observed as a parent that the census
    # lacks. ELSEWHERE is id 0.
    receptacle_labels.update(census["anchors"].keys())
    recep_ids = {ELSEWHERE_LABEL: ELSEWHERE_ID}
    for i, lbl in enumerate(sorted(receptacle_labels), start=1):
        recep_ids[lbl] = i
    obj_ids = {lbl: i for i, lbl in enumerate(sorted(object_labels))}

    # Canonical room projection (alias fix at source). Legacy hand-authored
    # slot labels ("dining.table_tucked", "tv.on", "fridge.inside") used to
    # fall back to their raw prefix as the "room", minting phantom rooms
    # ('dining' next to the census's 'dining_room', 'tv' next to
    # 'living_room') — measured downstream as phantom room-level moves (15/15
    # of the chair moved-bank cell). Receptacle labels stay distinct (a
    # tucked-slot and a table are different receptacles); only their ROOM
    # projection is unified: census rooms verbatim, legacy prefixes resolved
    # through CATEGORY_ROOM_HINT + rooms_match against this scene's census
    # rooms.
    from dynamic_home_eqa.rooms import CATEGORY_ROOM_HINT, rooms_match
    census_rooms = sorted({a.get("room") for a in census["anchors"].values()
                           if a.get("room")})

    def _canonical_room(lbl: str, census_room: Optional[str]) -> Optional[str]:
        if census_room:
            return census_room
        if "." not in lbl:
            return None
        prefix = lbl.split(".")[0]
        if prefix in census_rooms:
            return prefix
        cand = CATEGORY_ROOM_HINT.get(prefix, prefix)
        def _base(r):
            h, _, t = r.rpartition("_")
            return h if t.isdigit() else r
        matches = [r for r in census_rooms
                   if rooms_match(cand, r) or rooms_match(cand, _base(r))]
        if len(matches) == 1:
            return matches[0]
        return cand

    recep_meta = {}
    for lbl, rid in recep_ids.items():
        rec = census["anchors"].get(lbl, {})
        recep_meta[str(rid)] = {
            "label": lbl,
            "room": _canonical_room(lbl, rec.get("room")),
            "position": rec.get("position"),
            "category": rec.get("category"),
        }

    registry = {
        "scene_id": scene_id,
        # n_days spans the full calendar horizon (max true day + 1);
        # "days" lists which days actually exist — gaps are days that
        # failed generation and were skipped
        "n_days": (max(logged_days) + 1) if logged_days else 0,
        "days": logged_days, "folders": list(folders),
        "objects": obj_ids, "receptacles": recep_ids,
        "receptacle_meta": recep_meta,
        "elsewhere_id": ELSEWHERE_ID,
    }
    (out_dir / "registry.json").write_text(json.dumps(registry, indent=1))

    # ---- write events + snapshots with int ids ------------------------------
    with open(out_dir / "events.jsonl", "w") as f:
        for e in sorted(all_events, key=lambda e: (e["t_min"], e["label"])):
            rec = {"t_min": e["t_min"], "object_id": obj_ids[e["label"]],
                   "parent_id": recep_ids[e["parent_label"]],
                   "states": e["states"], "moved_by": e["moved_by"]}
            assert isinstance(rec["parent_id"], int)  # exactly one parent
            f.write(json.dumps(rec) + "\n")

    for snap in snapshots:
        parents_ids = {str(obj_ids[l]): recep_ids[p] for l, p in snap["parents"].items()}
        assert len(parents_ids) == len(snap["parents"])  # one parent per object
        (out_dir / f"snapshot_day{snap['day']}.json").write_text(json.dumps({
            "t_min": snap["t_min"], "day": snap["day"],
            "parents": parents_ids,
            "states": {str(obj_ids[l]): s for l, s in snap["states"].items()},
        }, indent=1))
    return out_dir
