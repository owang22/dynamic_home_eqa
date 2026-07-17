#!/usr/bin/env python3
"""
build_realized_day.py — offline builder for the realized-world artifact.

Materializes each (scene, day) trace ONCE into a realized_day.json
artifact (embodied/realized_world.py owns the schema); everything
downstream (render job, oracle sensor, future perception) reads the
artifact. There is no separate "commanded" pose to disagree with: the
build computes and snapshots the real 6-DoF pose of every trace object at
every event using real support raycasts and real collision resolution
against the scene and already-placed objects — never a blindly trusted
anchor-point coordinate. (Motivating failure class: a category-blind
nearest-rigid-object lookup once bound a "stool" event to a TV 0.019m
from its anchor — see results/reports/human_realism_study.md, round 3.)
Which real scene instance backs a label is decided once, by
category-filtered lookup against the label's own real starting position
(env/inventory.py's load_scene_state), not by proximity to a later
event's anchor.

DETERMINISTIC: no free physics settling. Every placement is a seeded,
deterministic search — REGION anchors via embodied/sensor.py's
deterministic_radial_offset pattern (_packing_candidates); INSTANCE
anchors via habitat-lab's Receptacle.sample_uniform_global + snap_down,
reseeded from sha256(label:t:attempt) before every sample (see
compliance_place_on_surface's docstring). Same (scene, day folder,
builder version) always produces a byte-identical artifact; the header
records builder_version/code_hash/trace_hash so a consumer can tell
whether an artifact is stale relative to the code or trace behind it.

Requires habitat-sim + habitat-lab (the dynamic_eqa env). The artifact
itself is plain JSON, habitat_sim-version-agnostic once written.

Scope: placement resolves POSITION with real collision avoidance
(raycast support height + circle-overlap packing against real bounding
boxes) but not ORIENTATION — every realized_pose ships an identity
quaternion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
from typing import Optional

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

from dynamic_home_eqa.embodied.realized_world import (
    PLACEMENT_ANCHOR_UNBACKED,
    PLACEMENT_INFEASIBLE,
    PLACEMENT_NO_ASSET,
    PLACEMENT_NO_RECEPTACLE_AUTHORED,
    PLACEMENT_NOT_APPLICABLE,
    PLACEMENT_OK,
    PLACEMENT_REMOVED,
    PLACEMENT_SUPPORT_MESH_GAP,
    PLACEMENT_SURFACE_FULL,
    BIND,
    SPAWN,
    ObjectBinding,
    ObjectEventRecord,
    RealizedDayArtifact,
    RealizedDayHeader,
    RealizedEventMirror,
    RealizedObject,
    RealizedPose,
    save_realized_day,
)

_BUILDER_VERSION = "realized_day_v6_clutter_starts"  # v5 -> v6: t=0 clutter placements enter the
                                                    # artifact as real spawned objects (object
                                                    # records only, no event mirrors) so renders
                                                    # show the true start state.
                                                    # v4 -> v5: per-label render assets — manifest
                                                    # LLM bindings for owner items + seeded
                                                    # without-replacement pool draws for shared
                                                    # clutter (AssetAllocator); recorded in each
                                                    # object's binding.template_name.
                                                    # v1 -> v2: INSTANCE-anchor placement replatformed onto
                                                 # habitat-lab Receptacle + snap_down (Receptacle
                                                 # Infrastructure Investigation round, GO'd). v2 -> v3:
                                                 # Pre-Pool-Build Remediation round — SURFACE_FULL split
                                                 # into 4 causes, unrealized-event carry-forward semantics
                                                 # (effective_pose/divergent), surface-height + synthetic
                                                 # fallbacks. v3 -> v4: Realizable-Anchor Vocabulary round
                                                 # (Part A) — census instance labels ("bedroom_2.bed_1")
                                                 # resolve DIRECTLY to their census instance's position/
                                                 # handle (env/anchor_census.py), no category->nearest-
                                                 # instance guessing; legacy anchors unchanged. Every
                                                 # realized_day.json artifact must rebuild under this
                                                 # fingerprint.
_OUT_DIR = _DYNAMIC_EQA / "data" / "realized_days"
_GEN_OUT = _DYNAMIC_EQA / "generation_out"

# Furniture-class categories bind to a real scene instance (never spawned);
# everything else is portable clutter and gets a new spawned mesh. This is
# not a new taxonomy — it's exactly env/inventory.py's existing tier split
# (TIER1_FURNITURE anchors-only + TIER2_HSSD_NATIVE move-eligible native
# clutter + STATEFUL_FURNITURE), reused rather than reinvented.
_ANCHOR_TOLERANCE_M = 0.35  # realized pose beyond this from the true anchor position -> PLACEMENT_INFEASIBLE

# One fixed real HSSD object-catalog asset per Tier-2b category, chosen
# deterministically (first id, sorted) from semantics/objects.csv's
# main_category column, confirmed to exist on disk. "keys" and "wallet"
# have no matching category OR reasonable synonym anywhere in this
# taxonomy at all (also checked key_chain/purse — and the Objaverse
# sourcing task's own finding, results/reports/asset_coverage.md: 0/5
# candidates cleared the real mask-area floor at any producible camera
# distance) — these get OBJECT_SPAWN_FAILED honestly, not a fake
# substitute. Moved here from scripts/realism_render_job.py at the
# Realized World Phase's render-job cutover (step 4) — the render job no
# longer spawns anything at all, this is build-time-only data now; "move,
# do not duplicate" per the phase's own cleanup rule.
#
# "cup" (Replatform round, item 4): re-pointed to
# 547c0a77b74f52c4e6c4a0a52f14f6c9c7a57b49 — a genuine HSSD-native mug
# asset (semantics/objects.csv: "Artisan Fair Trade mug", wnsynsetkey
# cup.n.01), found via the OVMM object-category cross-reference
# (receptacle_investigation.md's Section 3) and already present in our
# own local HSSD copy, no download needed. Confirmed directly, not
# assumed: measured through the real spectator-camera + mask-predicate
# pipeline at the same anchor, this asset's mask area (5.7% of frame)
# reads far more clearly than the prior drinkware substitution (0.94% —
# itself apparently no longer failing outright under the Spectator
# Camera round's closer framing, contrary to the older documented
# mask_too_small finding, but still much smaller/less legible). The old
# drinkware substitution is NOT deleted — "drinkware" itself is a real,
# separate category still mapped to it below; only "cup" moved off it.
SPAWNABLE_ASSET_BY_CATEGORY: dict[str, str] = {
    "bowl": "0391639c95af7b6f37ca6258afe8dd462605d847",
    "candle": "03569aed377a86f80ab87191174ae47b5332b77a",

    "vase": "00386b5179df69aec660a71fb9c65b344857d016",
    "bottle": "021a0ba1300490e2e288221a21f4387ce626d1de",
    "book": "0e00b8fa01cc07735378cc1df01619b667af2698",
    "laptop": "00b3040d6d75d68ba6d1bdf96e31c6b8432cbc1f",
    "drinkware": "036edf04844210dae3f5afc59165ad4955b3510b",
    "cup": "547c0a77b74f52c4e6c4a0a52f14f6c9c7a57b49",

    "wallet": "wallet_45e061790f36",
    "phone": "phone_223b376823b5",

    # Object-variety expansion (2026-07-15): reviewer-kept Objaverse assets
    # (data/objects/external_props/, tags in mapping.json). One asset per
    # category here for now — the per-label multi-asset binder (pools +
    # tag-driven owner assignment) replaces this dict's single-asset
    # limitation next.
    "plate": "plate_5d7ba0f7cebb",
    "mug": "mug_9646813e492b",
    "toy": "toy_16f83d9187ed",
    "towel": "towel_35b76b90614d",
    "newspaper": "newspaper_972f084ea5b9",
    "remote_control": "remote_control_35ac912c7dc1",
    "tray": "tray_4b8d86761f94",
    "cutting_board": "cutting_board_c1e6ac573c37",
    "scissors": "scissors_9399c720c9ed",
    "shears": "shears_0019c537f588",
    "teapot": "teapot_a90fd116b4b1",
    "alarm_clock": "alarm_clock_2d44fd75427e",
    "laundry_basket": "laundry_basket_1e88c90205f2",
    "medicine": "medicine_429536ff8dd8",
    # Objaverse "small key" (uid 9835dac44cd94286956357c21f17bfda, CC-BY,
    # Frybrix) — asset_coverage.md's Round 3 rejected this same candidate
    # (0.108% frame area) under the since-superseded ring-camera search;
    # re-verified under the current spectator-camera acceptance check
    # (asset_candidate_acceptance.py) and passed for real: scale 0.120m
    # (target 0.12m), area 5.473%, fail_reason=null, genuinely supported.
    "keys": "key_9835dac44cd9",
}
CATEGORY_SUBSTITUTED: set[str] = set()
NO_ASSET_CATEGORIES: set[str] = set()

# data/objects/external_props/ holds owner-sourced Objaverse assets (not
# HSSD) — short template names (keychain_1, wallet_<uid12>,
# phone_<uid12>) that don't follow HSSD's hash/first-char directory
# convention, so asset config resolution has to check here first.
_EXTERNAL_PROPS_DIR = _DYNAMIC_EQA / "data" / "objects" / "external_props"


def resolve_asset_config_path(asset_id: str) -> str:
    """Returns the object_config.json path for a SPAWNABLE_ASSET_BY_CATEGORY
    entry — external_props (owner-sourced Objaverse assets, keyed by short
    name) if one exists there, else the standard HSSD hash-directory path.
    Shared by spawn_new_object here and realism_render_job._materialize_object
    so both paths resolve external_props assets the same way."""
    from dynamic_home_eqa.topdown_map import HSSD_DIR

    external_path = _EXTERNAL_PROPS_DIR / "configs" / f"{asset_id}.object_config.json"
    if external_path.exists():
        return str(external_path)
    return f"{HSSD_DIR}/objects/{asset_id[0]}/{asset_id}.object_config.json"

# Coarse global sanity band for a spawned Tier-2b clutter item's post-spawn
# world AABB max extent — disclosed as coarse, not per-category-tuned:
# each category maps to exactly one fixed HSSD asset today, so a tight
# per-category band would mostly just re-measure that one asset's own
# known size — the real value of this check is catching a gross
# scale/unit bug (an asset landing 10x too big or too small).
_SPAWNABLE_SIZE_BAND_M = (0.02, 0.8)

# Overhang-suspect placements (footprint corner test failed on an accepted
# snap_down placement) — surfaced per build for collider-side QA, never a
# rejection (see compliance_place_on_surface).
_FOOTPRINT_SUSPECTS: list[str] = []


class UncoveredCategoryError(ValueError):
    """Raised by assert_category_has_asset_coverage — a category this pool
    references has no row anywhere in the asset mapping (not spawnable,
    not bind-eligible, not a documented no-asset exclusion). Distinct from
    a known, disclosed gap (NO_ASSET_CATEGORIES) — this is the "nobody has
    looked at this category yet" case, which should fail loudly at BUILD
    time rather than silently produce an artifact with unexplained gaps."""


def assert_category_has_asset_coverage(category: str) -> None:
    """Standing constraint (results/reports/asset_coverage.md's own
    instruction) — moved here from the render job at the Realized World
    Phase's cutover: coverage now needs to be true at BUILD time (the
    builder is what actually spawns/binds objects now), not render time.
    A category is covered if it's spawnable, bind-eligible (env/inventory.py's
    tier categories), or an explicitly evaluated no-asset exclusion."""
    from dynamic_home_eqa.generation.asset_binding import load_asset_pools
    covered = (
        category in SPAWNABLE_ASSET_BY_CATEGORY
        or category in load_asset_pools()      # reviewer-curated multi-asset pools
        or category in _bind_categories()
        or category in NO_ASSET_CATEGORIES
    )
    if not covered:
        raise UncoveredCategoryError(
            f"category {category!r} has no entry in the asset mapping (not spawnable, not "
            f"bind-eligible, not a documented no-asset exclusion) — evaluate it via "
            f"asset_candidate_acceptance.py (or add it to NO_ASSET_CATEGORIES if genuinely "
            f"unavailable) before it can appear in a realized-day build. "
            f"See results/reports/asset_coverage.md."
        )


def resolve_surface_height(sim, position: tuple[float, float, float], probe_up_m: float = 1.0,
                            max_distance_m: float = 2.0) -> Optional[float]:
    """Raycasts straight down from probe_up_m above `position` to find the
    real support surface's height. Returns None if nothing is hit within
    max_distance_m."""
    import habitat_sim
    import magnum as mn

    origin = mn.Vector3(position[0], position[1] + probe_up_m, position[2])
    ray = habitat_sim.geo.Ray(origin, mn.Vector3(0.0, -1.0, 0.0))
    result = sim.cast_ray(ray, max_distance=max_distance_m)
    if not result.has_hits():
        return None
    return origin[1] - result.hits[0].ray_distance


def _bind_categories() -> set[str]:
    from dynamic_home_eqa.env.inventory import STATEFUL_FURNITURE, TIER1_FURNITURE, TIER2_HSSD_NATIVE
    return TIER1_FURNITURE | TIER2_HSSD_NATIVE | set(STATEFUL_FURNITURE)


def normalize_stateful_anchor(anchor: str) -> str:
    """Aliases a room-qualified stateful-furniture anchor ("kitchen.fridge",
    "living_room.tv") to its real, resolvable bare-category form ("fridge",
    "tv") — the SAME alias realism_render_job.resolve_position_and_viewpoint
    applied before the Spectator Camera round deleted it (its only other
    job, pairing this alias with the now-deleted embodied viewpoint
    search, no longer applies — resolve_anchor_position below is the one
    remaining anchor-position resolver). Established since round 1 of the
    realism-render work (rooms.resolve_slot() no
    longer SYNTHESIZES this pattern going forward, but real already-
    generated traces still reference it, and STATEFUL_FURNITURE has only
    ever had one real bare-keyed position per category — never a
    room-qualified one — see topdown_map.anchor_world_positions).
    Missing this alias in the builder's own classification was a real,
    confirmed bug this round (kitchen.fridge/living_room.tv wrongly
    classified "unbacked" — 46 of 57 unbacked events on one review scene
    alone were this single bug, not a real generation-side gap)."""
    from dynamic_home_eqa.env.inventory import STATEFUL_FURNITURE

    if "." in anchor:
        bare = anchor.split(".", 1)[1]
        if bare in STATEFUL_FURNITURE:
            return bare
    return anchor


def classify_anchor(anchor: str) -> tuple[str, Optional[list[str]]]:
    """Returns (kind, cats): kind is "instance" (must bind to a real
    matching-category scene instance), "region" (floor placement, no
    single-instance requirement), or "unbacked" (no real backing anywhere
    — the build cannot place an object here, per the phase's admission
    rule). `cats` is the SLOT_ANCHORS category list when known (informational
    for region anchors, required for instance anchors).

    "region" for offset kinds "floor_near"/"current" (living_room.corner,
    living_room.open_floor, kitchen.counter_tucked) even though SLOT_ANCHORS
    hand-authors a "cats" hint for them — per the phase instruction's own
    example, living_room.corner IS a region anchor: those hints describe
    typical furniture nearby, not a strict single-instance requirement the
    way "on_surface" anchors (dining.table, bedroom.bed, ...) are.

    Pre-Pool-Build Remediation follow-up: a real, confirmed bug — 28 of 68
    anchor_unbacked events in this round's rebuild were `"{room}.{category}"`
    strings (e.g. "kitchen.range_hood", "bathroom.toilet",
    "bedroom.chest_of_drawers") for TIER1_FURNITURE categories that simply
    aren't among the 16 hand-authored SLOT_ANCHORS entries. These are NOT
    ungrounded: rooms.resolve_slot() already verifies a synthesized
    "{room}.{category}" string against the real per-room furniture census
    before generation ever emits it (see resolve_slot's own docstring —
    anything that fails that check is rejected at generation time, not
    written to the manifest), and topdown_map.anchor_world_positions
    already carries a real surveyed position for these anchors (confirmed
    directly — not assumed — by querying it for the exact failing anchors
    above; every one that has a real matching instance in that scene comes
    back with a real position). classify_anchor was simply never taught
    the same broader vocabulary — a build-time gap, not a generation-time
    grounding gap. Fixed by falling back to TIER1_FURNITURE membership for
    any dotted anchor not already covered by STATEFUL_FURNITURE or
    SLOT_ANCHORS, gated on slot_room() actually resolving a room for it
    (the same room-prefix/fuzzy-match machinery resolve_anchor_position
    and rooms.py use everywhere else, so "dining.x" vs "dining_room.x" and
    every other prefix convention already reconciled elsewhere stays
    consistent here too) — this does not touch position resolution at all,
    only which anchors are recognized as instance-backed in the first
    place."""
    from dynamic_home_eqa.env.deltas import SLOT_ANCHORS
    from dynamic_home_eqa.env.inventory import STATEFUL_FURNITURE, TIER1_FURNITURE
    from dynamic_home_eqa.rooms import CANONICAL_ROOMS, census_label_parts, slot_room

    anchor = normalize_stateful_anchor(anchor)

    # Realizable-Anchor Vocabulary round (Part A): a census instance label
    # names exactly one real furniture instance by construction — always
    # "instance", with the category parsed straight out of the label.
    # Whether the census actually backs it is resolve_anchor_position's
    # job (a miss there is a loud anchor_unbacked), not a string
    # classifier's.
    census_parts = census_label_parts(anchor)
    if census_parts is not None:
        return "instance", [census_parts[1]]

    if anchor in CANONICAL_ROOMS:
        return "region", None

    if anchor in STATEFUL_FURNITURE:
        return "instance", [anchor]

    spec = SLOT_ANCHORS.get(anchor)
    if spec is not None:
        if spec.get("offset") in ("floor_near", "current"):
            return "region", spec.get("cats")
        return "instance", spec.get("cats", [])

    if "." in anchor:
        category = anchor.split(".", 1)[1]
        if category in TIER1_FURNITURE and slot_room(anchor) is not None:
            return "instance", [category]

    return "unbacked", None


def resolve_anchor_position(world, anchor: str, anchor_census: Optional[dict] = None) -> Optional[tuple[float, float, float]]:
    """Real position for `anchor` — the furniture instance's own surveyed
    position for an instance anchor; for a region anchor, the room
    centroid (navmesh-snapped) of either the anchor itself (bare room
    name) or, for a SLOT_ANCHORS region entry like "living_room.open_floor"
    that isn't itself a room-centroid key, its ROOM's centroid (via
    rooms.slot_room() — the same room-extraction rooms.py already uses
    elsewhere; a literal `_room_centroids.get(anchor)` lookup for these
    always misses, since _room_centroids is keyed by bare CANONICAL_ROOMS
    names only, not slot strings: every
    "living_room.open_floor" event was wrongly ANCHOR_UNBACKED for want
    of this fallback). Reuses world._anchor_positions/_room_centroids —
    the SAME real-HSSD-derived tables the render job and sensor already
    trust, not an independent lookup.

    Part A: a census instance label resolves FIRST, by direct dictionary
    lookup against `anchor_census` (env/anchor_census.py's resolve_anchor)
    — the census carries the exact instance's position precisely so this
    is a lookup, not a category->nearest-instance guess. A census-shaped
    label with no census record (or no census loaded) deliberately falls
    through to the legacy tables and, failing those too, to None — the
    caller's loud anchor_unbacked path, exactly where a census bug should
    surface."""
    from dynamic_home_eqa.env.anchor_census import resolve_anchor
    from dynamic_home_eqa.rooms import slot_room

    anchor = normalize_stateful_anchor(anchor)

    census_record = resolve_anchor(anchor_census, anchor)
    if census_record is not None:
        return tuple(census_record["position"])

    pos = world._anchor_positions.get(anchor)
    if pos is not None:
        return pos

    centroid = world._room_centroids.get(anchor)
    if centroid is None:
        room = slot_room(anchor)
        if room is not None:
            centroid = world._room_centroids.get(room)
    if centroid is not None:
        cx, cz = centroid
        return world.snap_to_navmesh((cx, 0.0, cz))
    return None


def find_scene_instance_index(scene_id: str, position: tuple[float, float, float], tolerance_m: float = 0.02) -> Optional[int]:
    """Array index into scene_instance.json's object_instances for the
    entry at `position` (near-exact match — this is looking up the SAME
    file env/inventory.py's load_scene_state already read `position`
    from, not an independent guess). Recorded in the artifact for
    provenance/audit; not required for the live habitat_sim handle lookup
    (see find_live_object_at_xz), which matches the live sim directly."""
    from dynamic_home_eqa.env.inventory import HSSD_DIR

    scene_path = HSSD_DIR / "scenes-uncluttered" / f"{scene_id}.scene_instance.json"
    if not scene_path.exists():
        return None
    data = json.loads(scene_path.read_text())
    px, py, pz = position
    for i, obj in enumerate(data.get("object_instances", [])):
        t = obj.get("translation")
        if t and len(t) == 3 and math.dist((t[0], t[1], t[2]), (px, py, pz)) <= tolerance_m:
            return i
    return None


def find_live_object_at_xz(sim, position: tuple[float, float, float], max_xz_distance_m: float = 0.05):
    """The live habitat_sim rigid object at `position` — matched on X/Z
    ONLY, not full 3D distance. Shared by two callers: locating a BIND
    label's own live handle (position from env/inventory.py's
    load_scene_state) and locating the real furniture instance an
    "instance"-classified ANCHOR itself refers to (position from
    resolve_anchor_position/world._anchor_positions) — same underlying
    problem, same fix.

    Confirmed directly (not assumed), across three different real
    objects/categories, that habitat_sim's live loaded translation for a
    STATIC scene-instanced object systematically differs from the raw
    JSON translation in Y ONLY, by an amount that scales with the
    object's own height (stool: 0.24m, chair: 0.44m, potted_plant:
    0.65m — X/Z matched to within ~4mm in every case). This is not
    positional ambiguity to tolerate with a looser 3D radius (that would
    risk matching the wrong nearby object, the exact bug this phase
    exists to close) — it's a real, systematic Y-axis offset (leading
    hypothesis: COM-space application differs between scene-config-
    loaded STATIC instances and programmatically
    add_object_by_template_handle-created ones, which showed NO such gap
    when checked directly earlier this session) that has nothing to do
    with object identity. Matching X/Z tightly and ignoring Y entirely
    is the correct invariant, not a loosened check."""
    rom = sim.get_rigid_object_manager()
    best, best_dist = None, None
    for candidate in rom.get_objects_by_handle_substring().values():
        d = math.dist((candidate.translation.x, candidate.translation.z), (position[0], position[2]))
        if best_dist is None or d < best_dist:
            best, best_dist = candidate, d
    if best is None or best_dist > max_xz_distance_m:
        return None
    return best


def spawn_new_object(sim, category: str, asset_id: Optional[str] = None):
    """New clutter mesh for a SPAWN-category label. `asset_id` (the
    label's recorded binding, from the AssetAllocator) takes precedence;
    the category's legacy single-asset default is the fallback so old
    artifacts and category-only callers keep working."""
    import habitat_sim

    asset_id = asset_id or SPAWNABLE_ASSET_BY_CATEGORY.get(category)
    if asset_id is None:
        return None, None
    obj_attr_mgr = sim.get_object_template_manager()
    if not obj_attr_mgr.get_template_handles(asset_id):
        obj_attr_mgr.load_object_configs(resolve_asset_config_path(asset_id))
    templates = obj_attr_mgr.get_template_handles(asset_id)
    if not templates:
        return None, asset_id
    obj = sim.get_rigid_object_manager().add_object_by_template_handle(templates[0])
    if obj is not None:
        obj.motion_type = habitat_sim.physics.MotionType.KINEMATIC
    return obj, asset_id


class AssetAllocator:
    """Per-build label -> render-asset resolution (Strategy 2+).

    Resolution order for a SPAWN label:
      1. the manifest's `asset_bindings` (the generation-time LLM pick for
         owned Tier-3 items — obeyed verbatim, never re-rolled here);
      2. a seeded WITHOUT-REPLACEMENT draw from the category's reviewer-
         curated pool (external_props/mapping.json), so a home's three cups
         are visibly three DIFFERENT cups; the pool reshuffles and repeats
         once exhausted (a matching set is realistic, invisibility is not);
      3. the legacy single-asset default (SPAWNABLE_ASSET_BY_CATEGORY);
      4. None (PLACEMENT_NO_ASSET downstream, unchanged).

    Draws are memoized per label and seeded from (manifest seed, folder),
    so the same artifact rebuild binds the same assets — and the artifact
    records every choice in each object's binding.template_name anyway,
    which is what downstream readers should trust."""

    def __init__(self, manifest: Optional[dict], folder: str) -> None:
        import random
        from dynamic_home_eqa.generation.asset_binding import load_asset_pools
        self._manifest_bindings: dict = (manifest or {}).get("asset_bindings", {}) or {}
        self._pools = {cat: [e["uid"] for e in entries]
                       for cat, entries in load_asset_pools().items()}
        # Assets the reviewer flagged as rare ("only rarely use this one" in
        # the mapping note) sort to the END of every refill shuffle — drawn
        # only once the rest of the pool is in use, never first.
        self._rare = {e["uid"] for entries in load_asset_pools().values()
                      for e in entries if "rare" in (e.get("note") or "").lower()}
        self._rng = random.Random(f"{(manifest or {}).get('seed', 0)}|{folder}|assetalloc")
        self._remaining: dict[str, list[str]] = {}
        self._by_label: dict[str, str] = {}
        self.source_by_label: dict[str, str] = {}

    def pick(self, label: str, category: str) -> Optional[str]:
        if label in self._by_label:
            return self._by_label[label]
        uid = self._manifest_bindings.get(label)
        source = "external_props_llm_bound"
        if uid is None and self._pools.get(category):
            rem = self._remaining.get(category)
            if not rem:
                rem = list(self._pools[category])
                self._rng.shuffle(rem)
                # pop() draws from the END, so rare-flagged uids go FIRST
                # in the list (drawn last).
                rem.sort(key=lambda u: 0 if u in self._rare else 1)
                self._remaining[category] = rem
            uid = rem.pop()
            source = "external_props_pool"
        if uid is None:
            uid = SPAWNABLE_ASSET_BY_CATEGORY.get(category)
            source = "hssd_spawnable"
        if uid is not None:
            self._by_label[label] = uid
            self.source_by_label[label] = source
        return uid


def determine_binding(sim, scene_id: str, label: str, category: str, log: list[str],
                      allocator: Optional[AssetAllocator] = None) -> ObjectBinding:
    from dynamic_home_eqa.env.inventory import load_scene_state

    if category in _bind_categories():
        state = load_scene_state(scene_id)
        inst = state.instances.get(label)
        if inst is not None and inst.position is not None:
            idx = find_scene_instance_index(scene_id, inst.position)
            return ObjectBinding(kind=BIND, scene_instance_index=idx, template_name=None, source="hssd")
        log.append(f"ANOMALY: {label!r} (category={category!r}) is bind-eligible but has no real "
                    f"census position in scene {scene_id} — falling back to spawn (should not "
                    f"normally happen; generation is expected to only reference real census labels).")

    if allocator is not None:
        asset_id = allocator.pick(label, category)
        source = allocator.source_by_label.get(label, "none")
    else:
        asset_id = SPAWNABLE_ASSET_BY_CATEGORY.get(category)
        source = "hssd_spawnable"
    return ObjectBinding(kind=SPAWN, scene_instance_index=None, template_name=asset_id,
                          source=source if asset_id else "none")


def _footprint_radius(obj) -> float:
    bb = obj.root_scene_node.cumulative_bb
    return max(bb.size().x, bb.size().z) / 2.0


_N_RADIUS_TIERS = 6
_N_ANGLES_PER_TIER = 6  # 36 total candidates per placement search (1 center + 6 tiers x 6 angles)


def _packing_candidates(label: str, max_offset_m: float):
    """Ring-tiered candidate generator, the SAME pattern
    embodied/sensor.py's viewpoint search already uses (radius tiers,
    smallest first; a full angular ring sampled at each tier before
    growing the radius) — not the single-random-angle-per-attempt scheme
    an earlier version used, which could easily miss real free space at
    a given distance simply because it never sampled that angle. Tier 0
    is always the anchor position itself (radius 0), matching the
    caller's "try the exact anchor point first" contract. The per-tier
    angular offset is hash-seeded (by label+tier) so the ring's rotation
    isn't always axis-aligned/identical across objects, without making
    the search itself non-deterministic."""
    import hashlib as _hashlib

    yield (0.0, 0.0)
    for tier in range(1, _N_RADIUS_TIERS + 1):
        radius = max_offset_m * (tier / _N_RADIUS_TIERS)
        h = int(_hashlib.sha256(f"{label}:{tier}".encode()).hexdigest()[:16], 16)
        angle_offset = 2 * math.pi * ((h % 1_000_000) / 1_000_000.0)
        for i in range(_N_ANGLES_PER_TIER):
            angle = angle_offset + 2 * math.pi * i / _N_ANGLES_PER_TIER
            yield (radius * math.cos(angle), radius * math.sin(angle))


def compliance_place_region(sim, world, obj, label: str, seed_key: str,
                             target_pos: tuple[float, float, float],
                             beside_extent_m: float = 0.0,
                             beside_min_offset_m: float = 0.0) -> tuple[Optional[tuple[float, float, float]], str]:
    """REGION anchors only (item 3: "region anchors keep a radius (no
    instance to contain within)") — bare room names and the "floor_near"/
    "current" SLOT_ANCHORS offset kinds (living_room.corner,
    living_room.open_floor, kitchen.counter_tucked). No single furniture
    instance to bound placement to, so this stays a disk search around
    the anchor POINT — but the search itself is replatformed the same way
    compliance_place_on_surface's was (see its docstring): candidates are
    now navmesh-snapped (a real walkable floor point, not an arbitrary
    XZ offset that might land inside a wall) and validated via snap_down
    against LIVE collision state, replacing the retired circular-
    footprint occupancy list (_PACKING_MARGIN_M/`occupancy` — same
    booking-list bug class item 1 found and fixed for INSTANCE anchors).
    _ANCHOR_TOLERANCE_M's distance-to-point invariant is UNCHANGED — that
    is the semantic "stay near where the trace actually said" contract
    region placement is built on, not part of what's being retired here.

    Navmesh snapping goes through `world.snap_to_navmesh` (EmbodiedWorld's
    OWN sim, already properly `recompute_navmesh`'d with this project's
    real NavMeshConfig — see world.py) rather than `sim.pathfinder`
    directly: confirmed directly (a real segfault, not a hypothetical)
    that `sim` here — the BUILD sim, from _make_render_sim, which never
    calls recompute_navmesh — has an uninitialized pathfinder for this
    scene (102343992 ships no baked navmesh at all, see world.py's module
    docstring), and habitat_sim's C++ binding for snap_point on an empty
    navmesh crashes natively instead of raising a catchable Python
    exception or returning NaN. The two sims load the same scene/
    coordinate system, so a position `world` resolves is equally valid to
    hand to `sim`'s own object/collision state afterward.

    PLACEMENT_INFEASIBLE stays reserved for "every candidate this search
    tried was farther than _ANCHOR_TOLERANCE_M from the true anchor
    position" (the anchor itself has no nearby navigable floor at all);
    PLACEMENT_SURFACE_FULL covers "candidates exist near the anchor but
    none of them clear live collision" — same two-outcome split as
    before, just computed against real state instead of a booking list.

    For INSTANCE anchors (dining.table, bedroom.bed, fridge, the
    room.category census entries, ...) see compliance_place_on_surface
    instead — those bind to a real furniture instance and place within
    its own real receptacle surface, not a fixed-radius disk around a
    point."""
    import magnum as mn
    from habitat.sims.habitat_simulator.sim_utilities import snap_down

    # Floor-Bound Realization round: `beside_extent_m` widens both the
    # candidate ring and the distance tolerance by the anchor FURNITURE's
    # own half-extent, for floor-beside placements (chair next_to a
    # counter). With the bare 0.35m pivot tolerance, "beside a counter"
    # was structurally infeasible: the nearest floor point outside a
    # ~0.6m-deep counter's footprint is already farther from its PIVOT
    # than the whole tolerance (confirmed on scene 102344022 — 19
    # placement_infeasible events, every one a chair/stool beside a
    # counter/cabinet/couch). 0.0 (the default) is the original
    # open-floor region-anchor behavior, unchanged.
    obj_radius = _footprint_radius(obj)
    max_offset = obj_radius + 0.25 + beside_extent_m
    tolerance = _ANCHOR_TOLERANCE_M + beside_extent_m
    farthest_infeasible = None

    for attempt, (dx, dz) in enumerate(_packing_candidates(label, max_offset_m=max_offset)):
        cand_xz = (target_pos[0] + dx, target_pos[2] + dz)

        offset_from_anchor = math.dist(cand_xz, (target_pos[0], target_pos[2]))
        if offset_from_anchor > tolerance:
            if farthest_infeasible is None:
                farthest_infeasible = (cand_xz[0], target_pos[1], cand_xz[1])
            continue
        if offset_from_anchor < beside_min_offset_m:
            # Beside placements only: a candidate INSIDE the anchor
            # furniture's own footprint can pass snap_down without any
            # contact when the furniture's collider is a thin shell
            # (confirmed directly: a chair placed exactly at a kitchen
            # counter's pivot draws zero contact points — it visually
            # clips straight through the cabinetry). "Beside" starts at
            # the furniture's edge, not its pivot.
            continue

        snapped = world.snap_to_navmesh((cand_xz[0], target_pos[1], cand_xz[1]))
        if any(math.isnan(v) for v in snapped):
            continue  # no navigable floor anywhere near this candidate

        obj.translation = mn.Vector3(float(snapped[0]), float(snapped[1]) + 0.2, float(snapped[2]))
        if snap_down(sim, obj):  # default support_obj_ids=[stage_id] -- the real floor/stage mesh
            final_pos = (obj.translation.x, obj.translation.y, obj.translation.z)
            return final_pos, PLACEMENT_OK

    if farthest_infeasible is not None:
        return None, PLACEMENT_INFEASIBLE
    return None, PLACEMENT_SURFACE_FULL


def get_world_aabb(obj) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """World-space (min, max) AABB corners for a live rigid object — all 8
    local-bbox corners transformed through the object's own world
    transformation (position + rotation), not just cumulative_bb's local-
    frame min/max directly. Most HSSD scene furniture is axis-aligned or
    close to it, but this is correct regardless."""
    import magnum as mn

    bb = obj.root_scene_node.cumulative_bb
    corners = [
        mn.Vector3(x, y, z)
        for x in (bb.min.x, bb.max.x)
        for y in (bb.min.y, bb.max.y)
        for z in (bb.min.z, bb.max.z)
    ]
    world_corners = [obj.transformation.transform_point(c) for c in corners]
    xs = [c.x for c in world_corners]
    ys = [c.y for c in world_corners]
    zs = [c.z for c in world_corners]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


_SNAP_DOWN_MAX_ATTEMPTS = 40  # matches the Receptacle Infrastructure Investigation's spike (both
                               # real test events succeeded on attempt 2/40 — see
                               # receptacle_investigation.md's Section 4)


def resolve_furniture_receptacles(sim, scene_id: str, furniture_handle, active_names_cache: dict) -> tuple[list, bool]:
    """Returns the active (curated-in, .rec_filter.json "active") Receptacle
    objects (habitat-lab) belonging to `furniture_handle` (a live rigid
    object, e.g. the dining table itself — see find_live_object_at_xz),
    matched EXACTLY by receptacle.parent_object_handle ==
    furniture_handle.handle (not a proximity heuristic — the furniture
    handle is already the correct live object, so this is an exact,
    unambiguous join).

    Realizable-Anchor Vocabulary round: the old second return value
    (`raw_had_any`, distinguishing "no receptacle authored" from "authored
    but curator-filtered" so the latter could hard-block as
    PLACEMENT_RECEPTACLE_CURATED_OUT) is REMOVED along with that status —
    curation is enforced at LLM generation time now (the anchor census
    marks curated-out anchors proximity-only, so no surface proposal ever
    targets them), and the build-time hard block only ever punished
    legacy manifests (blanket-blocking every wardrobe placement).

    `active_names_cache` memoizes the per-scene find_receptacles() +
    .rec_filter.json read across the whole build (receptacles are a
    scene-level, not per-anchor, property) — keyed by scene_id, storing
    (all_raw_receptacles, active_names_or_None)."""
    import pathlib as _pathlib

    from habitat.datasets.rearrange.samplers.receptacle import find_receptacles

    from dynamic_home_eqa.topdown_map import HSSD_DIR

    if scene_id not in active_names_cache:
        filter_path = _pathlib.Path(HSSD_DIR) / "scene_filter_files" / f"{scene_id}.rec_filter.json"
        active_names = set(json.loads(filter_path.read_text())["active"]) if filter_path.exists() else None
        all_receptacles = find_receptacles(sim)
        active_names_cache[scene_id] = (all_receptacles, active_names)

    all_receptacles, active_names = active_names_cache[scene_id]
    handle = furniture_handle.handle
    raw = [r for r in all_receptacles if r.parent_object_handle == handle]
    return raw if active_names is None else [r for r in raw if r.unique_name in active_names]


_COLLISION_DEPTH_MARGIN_M = 0.01  # matches snap_down's own default max_collision_depth


def _seeded_sample(seed_key: str, salt: str):
    """Reseeds habitat-lab's global random/np.random state from a sha256
    hash of f"{seed_key}:{salt}" — see compliance_place_on_surface's
    DETERMINISM note. Shared by every candidate generator in this module
    that draws from Receptacle.sample_uniform_global's global RNG."""
    import random as _random

    import numpy as np

    seed = int(hashlib.sha256(f"{seed_key}:{salt}".encode()).hexdigest()[:16], 16) % (2**32)
    _random.seed(seed)
    np.random.seed(seed)


def _other_object_collides(sim, obj) -> bool:
    """True if `obj`, at its CURRENT translation, real-collides with any
    OTHER already-placed rigid object (not the stage, not itself) beyond
    _COLLISION_DEPTH_MARGIN_M penetration. Used by both fallback
    placement methods below in place of a raycast-based support check —
    by construction, both are only called when the support raycast
    itself cannot be trusted (see compliance_place_on_surface), but
    checking for real interpenetration with OTHER objects' own collision
    shapes remains valid: it's specifically the anchor furniture's own
    support geometry that's suspect, not everything else in the scene."""
    sim.perform_discrete_collision_detection()
    for cp in sim.get_physics_contact_points():
        if cp.object_id_a != obj.object_id and cp.object_id_b != obj.object_id:
            continue
        if cp.contact_distance < -_COLLISION_DEPTH_MARGIN_M:
            return True
    return False


def _footprint_supported(sim, obj, support_ids, inset_frac: float = 0.12,
                         max_drop_m: float = 0.12) -> bool:
    """All four (inset) corners of the object's world-AABB footprint must
    have the support surface directly beneath them — rejects candidates
    snap_down/collision accept with the object hanging off a counter edge
    or clipping through it (confirmed visually on scene 102344022's
    kitchen counter: plates/cups/laptops half off the side). A corner ray
    that first hits anything OTHER than the support (or nothing within
    max_drop_m) marks the candidate overhanging. support_ids empty (the
    synthetic/no-receptacle path has no authoritative support id set)
    accepts any first hit within range — the check then still rejects
    corners hanging over open air."""
    import habitat_sim
    import magnum as mn

    (min_x, min_y, min_z), (max_x, max_y, max_z) = get_world_aabb(obj)
    dx, dz = (max_x - min_x) * inset_frac, (max_z - min_z) * inset_frac
    own_id = obj.object_id
    # Rays start ABOVE the object's base (not below it): after snap_down the
    # base is in contact with the support, and an origin below it sits
    # INSIDE the support's collision solid, where the ray misses everything
    # and every legitimate placement got rejected (measured: 60%+ unrealized
    # rates). Own-collider hits are skipped on the way down.
    start_up = 0.04
    ok_corners = 0
    for x in (min_x + dx, max_x - dx):
        for z in (min_z + dz, max_z - dz):
            ray = habitat_sim.geo.Ray(mn.Vector3(x, min_y + start_up, z), mn.Vector3(0.0, -1.0, 0.0))
            res = sim.cast_ray(ray, max_distance=start_up + max_drop_m)
            for h in res.hits:
                if h.object_id == own_id:
                    continue
                if (h.object_id in support_ids) if support_ids else True:
                    ok_corners += 1
                break  # nearest non-self hit decides
    # 3-of-4, not 4-of-4: several HSSD colliders genuinely don't reach the
    # whole annotated surface (the documented support_mesh_gap — scene
    # 102344022's kitchen counter among them), so a strict all-corners
    # requirement rejected 30-55% of legitimate placements. Three corners
    # still rules out the visible half-off-the-edge overhangs this exists
    # to stop, while tolerating a collider gap under one corner.
    return ok_corners >= 3


def _place_at_candidates(sim, obj, bb, candidates, support_ids=()) -> Optional[tuple[float, float, float]]:
    """Shared placement loop for both fallback methods (item 3/4): each
    candidate is (x, y, z) where y is ALREADY the real resting/support
    height (the receptacle sample's own Y, or the furniture's own real
    top-surface Y for the synthetic case) — NOT a point to gravity-
    project from. Offsets by the object's own local bbox-bottom so its
    base lands exactly at that height, accepts the first candidate with
    no real collision against another already-placed object."""
    import magnum as mn

    for cx, cy, cz in candidates:
        obj.translation = mn.Vector3(cx, cy - bb.min.y, cz)
        # No _footprint_supported gate here (deliberately): these fallback
        # paths exist precisely because the furniture's collider CANNOT
        # confirm its own surface (support_mesh_gap / no receptacle) — a
        # collider-raycast gate would re-reject exactly the placements the
        # fallback was invented to rescue (measured: bed/backpack and the
        # scene-102344022 counter went 30-55% unrealized with it applied).
        if not _other_object_collides(sim, obj):
            return (obj.translation.x, obj.translation.y, obj.translation.z)
    return None


def _receptacle_surface_candidates(sim, receptacles: list, seed_key: str):
    """Item 3's candidate generator: deterministically-seeded samples
    directly on each receptacle's own annotated surface mesh (the same
    Receptacle.sample_uniform_global the normal snap_down path uses) —
    valid to trust for WHERE the surface is (that's what the receptacle
    mesh means) even when the furniture's separate collision mesh can't
    be trusted to confirm it via raycast (the support_mesh_gap case this
    exists for)."""
    for r_idx, receptacle in enumerate(receptacles):
        for attempt in range(_SNAP_DOWN_MAX_ATTEMPTS):
            _seeded_sample(seed_key, f"surfheight:{r_idx}:{attempt}")
            sample_pos = receptacle.sample_uniform_global(sim, 1.0)
            yield (float(sample_pos[0]), float(sample_pos[1]), float(sample_pos[2]))


_SYNTHETIC_EDGE_MARGIN_M = 0.05
_SYNTHETIC_GRID_N = 8


def _synthetic_top_candidates(furniture_handle, seed_key: str):
    """Item 4's candidate generator, for furniture with ZERO real
    receptacles anywhere (PLACEMENT_NO_RECEPTACLE_AUTHORED): a
    deterministic, label-seeded grid across the furniture's own real
    world AABB top face (inset by the edge margin) — programmatically
    constructing exactly the kind of "receptacle" a human curator would
    have annotated, when none exists at all. Same deterministic-grid
    shape the pre-replatform builder used for on-surface placement
    (retired in the Replatform round's item 1), reused here specifically
    for this narrower, disclosed fallback case, not as the default path."""
    fmin, fmax = get_world_aabb(furniture_handle)
    lo_x, hi_x = fmin[0] + _SYNTHETIC_EDGE_MARGIN_M, fmax[0] - _SYNTHETIC_EDGE_MARGIN_M
    lo_z, hi_z = fmin[2] + _SYNTHETIC_EDGE_MARGIN_M, fmax[2] - _SYNTHETIC_EDGE_MARGIN_M
    top_y = fmax[1]
    if lo_x > hi_x or lo_z > hi_z:
        return  # furniture footprint smaller than the edge margin allows -- no candidates
    n = _SYNTHETIC_GRID_N
    grid = [
        (lo_x + (hi_x - lo_x) * (i + 0.5) / n, top_y, lo_z + (hi_z - lo_z) * (j + 0.5) / n)
        for i in range(n) for j in range(n)
    ]
    h = int(hashlib.sha256(seed_key.encode()).hexdigest()[:16], 16)
    order = sorted(range(len(grid)), key=lambda k: (h * (k + 1)) % 999_983)
    for k in order:
        yield grid[k]


def compliance_place_on_surface(sim, obj, label: str, seed_key: str, anchor_position: tuple[float, float, float],
                                 furniture_handle, receptacles: list
                                 ) -> tuple[Optional[tuple[float, float, float]], str, Optional[str]]:
    """INSTANCE anchors: placement via habitat-lab's real receptacle
    geometry (Receptacle.sample_uniform_global + snap_down against LIVE
    collision state), replacing the retired circular-footprint occupancy
    list (see results/reports/receptacle_investigation.md's Section 4 —
    confirmed directly: two real trace events our own occupancy
    bookkeeping had rejected as SURFACE_FULL, because an earlier
    occupant's slot was never freed even after that occupant's OWN later
    event successfully moved it elsewhere, placed successfully via
    snap_down's live collision query in under 3 samples each). snap_down
    naturally handles the case the old bookkeeping could not: it only
    ever sees what is ACTUALLY in the live sim right now, not an
    accumulated whole-day booking list.

    Pre-Pool-Build Remediation round: the old single PLACEMENT_SURFACE_FULL
    bucket is split into distinguishable causes, each detected live,
    not assumed:
      - `receptacles` empty: PLACEMENT_NO_RECEPTACLE_AUTHORED — no usable
        receptacle for this furniture. Fallback: item 4's synthetic
        AABB-top grid. (The Realizable-Anchor Vocabulary round removed
        the old further split into "none authored" vs "curated out
        hard-block" — curation now acts at LLM generation time via the
        anchor census, which never offers a curated-out anchor as a
        surface target; the hard block here only ever hit legacy
        manifests, blanket-blocking e.g. every wardrobe placement.)
      - `receptacles` non-empty but snap_down never succeeds AND its own
        internal support raycast (bb_ray_prescreen) never once finds the
        furniture itself as the impacted surface, across every receptacle
        and attempt: PLACEMENT_SUPPORT_MESH_GAP — the receptacle's
        annotated surface and the furniture's separate collision mesh
        don't geometrically overlap (confirmed: bedroom.bed — the
        collider doesn't reach the mattress). Fallback: item 3's
        surface-height placement, trusting the receptacle mesh's own
        sample Y directly instead of a raycast that can't reach it.
      - `receptacles` non-empty, prescreen DOES succeed at least once, but
        every accepted-support candidate still fails snap_down's final
        collision check: PLACEMENT_SURFACE_FULL — a real, physically
        grounded "no free space" finding, the one genuinely unavoidable
        failure code left in this taxonomy.

    Both fallbacks return PLACEMENT_OK with a `placement_method` tag
    ("surface_height" / "synthetic") distinguishing them from the normal
    "snap_down" path in the build report and artifact — they are real,
    accepted placements, not degraded ones, but the provenance is kept
    visible (see build_realized_day's own audit stats).

    `furniture_handle` is the anchor's OWN live rigid object (the dining
    table itself, not the object being placed on it) — see
    find_live_object_at_xz. `receptacles` comes from
    resolve_furniture_receptacles.

    DETERMINISM: Receptacle.sample_uniform_global draws from the global
    `random`/`np.random` state, not a local seeded generator — confirmed
    by reading habitat-lab's own source. Left unseeded, this would break
    this module's own "same (scene, day folder, builder version) always
    produces a byte-identical artifact" guarantee (see module docstring).
    Reseeded via _seeded_sample from a sha256 hash of `seed_key` (the
    caller passes f"{label}:{t}" — label alone isn't enough, the same
    label can revisit the same anchor multiple times in one day) before
    every draw, in every candidate generator this function or its
    fallbacks use — the same hash-seeding convention viewpoint/packing
    search already use elsewhere in this codebase (
    deterministic_radial_offset, _packing_candidates), extended to cover
    habitat-lab's own RNG.

    Returns (pos_or_None, placement_status, placement_method_or_None)."""
    if not receptacles:
        bb = obj.root_scene_node.cumulative_bb
        pos = _place_at_candidates(sim, obj, bb, _synthetic_top_candidates(furniture_handle, seed_key))
        if pos is not None:
            return pos, PLACEMENT_OK, "synthetic"
        return None, PLACEMENT_NO_RECEPTACLE_AUTHORED, None

    import magnum as mn
    from habitat.sims.habitat_simulator.sim_utilities import bb_ray_prescreen, snap_down

    prescreen_ever_ok = False
    for r_idx, receptacle in enumerate(receptacles):
        support_ids = receptacle.get_support_object_ids(sim)
        for attempt in range(_SNAP_DOWN_MAX_ATTEMPTS):
            _seeded_sample(seed_key, f"{r_idx}:{attempt}")
            sample_pos = receptacle.sample_uniform_global(sim, 1.0)
            obj.translation = mn.Vector3(*sample_pos)
            prescreen = bb_ray_prescreen(sim, obj, support_obj_ids=support_ids)
            if prescreen["surface_snap_point"] is not None:
                prescreen_ever_ok = True
            if snap_down(sim, obj, support_obj_ids=support_ids):
                # Overhang DETECTOR (not a gate): the corner-ray test proved
                # unreliable as a rejector on scene-baked colliders (rays
                # vs. stage-baked furniture ids — rejecting on it pushed
                # legitimate placements to 30-55% unrealized while fixing
                # nothing), but it still flags candidates worth eyeballing.
                # The real overhang/clipping fix is collider-side (e.g.
                # scene 102344022's kitchen counter), tracked via this count
                # in the build report.
                if not _footprint_supported(sim, obj, support_ids):
                    _FOOTPRINT_SUSPECTS.append(f"{label} on {getattr(receptacle, 'name', '?')}")
                final_pos = (obj.translation.x, obj.translation.y, obj.translation.z)
                return final_pos, PLACEMENT_OK, "snap_down"

    if not prescreen_ever_ok:
        bb = obj.root_scene_node.cumulative_bb
        pos = _place_at_candidates(sim, obj, bb, _receptacle_surface_candidates(sim, receptacles, seed_key))
        if pos is not None:
            return pos, PLACEMENT_OK, "surface_height"
        return None, PLACEMENT_SUPPORT_MESH_GAP, None

    return None, PLACEMENT_SURFACE_FULL, None


def _code_hash() -> str:
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]


def _trace_hash(manifest: dict) -> str:
    return hashlib.sha256(json.dumps(manifest["changes"], sort_keys=True).encode()).hexdigest()[:16]


def build_realized_day(folder: str, scene_id: str, sim, world, manifest: Optional[dict] = None,
                       clutter: Optional[list] = None) -> tuple[RealizedDayArtifact, dict]:
    """`manifest`: pre-loaded manifest dict, for callers that already have
    one in memory (e.g. a test fixture not backed by a real
    generation_out/ folder). Defaults to reading generation_out/<folder>/
    manifest.json, the normal path."""
    import habitat_sim
    import magnum as mn

    from dynamic_home_eqa.env.replay import initial_state_and_changes_from_manifest

    if manifest is None:
        manifest = json.loads((_GEN_OUT / folder / "manifest.json").read_text())
    if clutter is None:
        _gr_path = _GEN_OUT / folder / "generation_result.json"
        clutter = (json.loads(_gr_path.read_text()).get("clutter", [])
                   if _gr_path.exists() else [])
    initial_state, changes = initial_state_and_changes_from_manifest(manifest)

    # Clutter-start realization: the t=0 clutter placements are REAL objects
    # the generation state reasons about ("plate_1 and plate_2 are already
    # on the counter"), but only labels with manifest CHANGES used to enter
    # this artifact — a never-moved plate was invisible in every render, and
    # even a moved one had no pose before its first move. Synthesized as
    # t=0.0 insert events through the normal placement path (physical
    # placement, collision, allocator asset), recorded ONLY on the object
    # records — not the event mirrors, which stay a 1:1 mirror of the
    # manifest's own change list. Label numbering mirrors build_manifest's
    # clutter_counters (same iteration order).
    from dynamic_home_eqa.env.deltas import Change as _Change
    from dynamic_home_eqa.rooms import resolve_slot
    from dynamic_home_eqa.topdown_map import instance_room_positions
    clutter_start_labels: set[str] = set()
    if clutter:
        _cc: dict[str, int] = {}
        _synthetic: list = []
        for _p in clutter:
            _cat = _p["object_category"]
            _cc[_cat] = _cc.get(_cat, 0) + 1
            _lbl = f"{_cat}_{_cc[_cat]}"
            clutter_start_labels.add(_lbl)
            try:
                _slot = resolve_slot(_p["target_anchor"], _p["target_relationship"],
                                     room_instance_categories={
                                         room: set(cats) for room, cats
                                         in instance_room_positions(scene_id).items()})
            except Exception:
                _slot = _p["target_anchor"]
            _synthetic.append(_Change(
                activity="clutter_start", phase="enter", instance_id=_lbl,
                change_type="insert_new", object_category=_cat,
                from_semantic=None, to_semantic=_slot,
                reason="start-of-day clutter placement", t=0.0))
        changes = _synthetic + list(changes)

    # Strategy 2+ per-label asset resolution: manifest LLM bindings first,
    # then seeded without-replacement pool draws (see AssetAllocator).
    asset_allocator = AssetAllocator(manifest, folder)

    # Part A: the realizable-anchor census — census instance labels in the
    # manifest resolve directly against this (see resolve_anchor_position).
    # None (no census for this scene) leaves every legacy anchor path
    # untouched; census-shaped labels would then land in anchor_unbacked,
    # loudly, which is correct (a manifest with census labels but no census
    # on disk is a real inconsistency worth seeing).
    from dynamic_home_eqa.env.anchor_census import load_anchor_census
    from dynamic_home_eqa.env.inventory import FLOOR_BOUND_CATEGORIES
    from dynamic_home_eqa.generation.schemas import PROXIMITY_RELATIONSHIPS
    anchor_census = load_anchor_census(scene_id)

    log: list[str] = []
    objects: dict[str, RealizedObject] = {}
    event_mirrors: list[RealizedEventMirror] = []
    live_handle: dict[str, object] = {}
    # Pre-Pool-Build Remediation round (item 2): last_effective_pose/
    # last_effective_anchor implement the "no object is ever poseless"
    # carry-forward rule — see _finalize_event below, the single place
    # every event-recording call site in this loop routes through so the
    # semantics are applied consistently regardless of which failure/
    # success branch produced the outcome.
    last_effective_pose: dict[str, RealizedPose] = {}
    last_effective_anchor: dict[str, str] = {}
    furniture_handle_cache: dict[str, object] = {}  # anchor string -> the anchor's OWN live furniture object (or None)
    receptacle_cache: dict[str, list] = {}  # anchor string -> active Receptacle list
    active_receptacle_names_cache: dict[str, tuple] = {}  # scene_id -> (raw receptacles, active names or None)
    audit = {
        "instance": 0, "region": 0, "unbacked": 0,
        "ok": 0, "surface_full": 0, "placement_infeasible": 0,
        "anchor_unbacked": 0, "no_asset": 0, "not_applicable": 0,
        "support_mesh_gap": 0, "no_receptacle_authored": 0,
        "placement_method": {"snap_down": 0, "surface_height": 0, "synthetic": 0},
        "unrealized_events": 0, "divergent_events": 0,
        # Phase 3 put-away removes — deliberate departures, counted apart
        # from unrealized_events (a remove is a success, not a failure).
        "removed_events": 0,
        # Part A: per-event trace of which anchor label was chosen upstream
        # vs which live furniture handle it actually resolved to — the
        # "chosen vs resolved" audit trail; and whether a census record
        # backed the resolution (census_backed=False on a census-shaped
        # label is a census bug surfacing).
        "anchor_resolutions": [],
        # Part A: census anchors with 0 active receptacles are proximity-
        # only targets (near/next_to — the schema cannot pair them with a
        # surface relation), realized as a floor placement BESIDE the
        # instance, never a synthetic-top (the fridge-top-bowl class).
        "proximity_floor_placements": 0,
    }

    def _finalize_event(label: str, anchor: str, change_type: str, t: float, from_semantic: Optional[str],
                         realized_pose: Optional[RealizedPose], placement_status: str,
                         placement_method: Optional[str] = None, failure_detail: Optional[str] = None) -> None:
        """Shared event-recording helper — every event-creation site in
        this loop (7 distinct branches: state_change, unbacked, target-
        unresolved, navmesh-pruned, no-asset, no-live-handle, and the main
        instance/region placement result) routes through here so item 2's
        carry-forward semantics (realized / effective_pose / divergent)
        are computed identically everywhere, not reimplemented ad hoc
        per branch."""
        is_realized = realized_pose is not None
        if is_realized:
            last_effective_pose[label] = realized_pose
            last_effective_anchor[label] = anchor
            effective_pose = realized_pose
            divergent = False
        else:
            audit["unrealized_events"] += 1
            effective_pose = last_effective_pose.get(label)
            divergent = effective_pose is not None and last_effective_anchor.get(label) != anchor
            if divergent:
                audit["divergent_events"] += 1

        objects[label].events.append(ObjectEventRecord(
            t=t, anchor=anchor, realized_pose=realized_pose, placement_status=placement_status,
            placement_method=placement_method, realized=is_realized,
            effective_pose=effective_pose, divergent=divergent,
        ))
        # Clutter-start events live only on object records — the mirror list
        # stays a strict 1:1 mirror of the manifest's own change list.
        if not (label in clutter_start_labels and t == 0.0):
            event_mirrors.append(RealizedEventMirror(
                label=label, change_type=change_type, t=t, from_semantic=from_semantic, to_semantic=anchor,
                placement_status=placement_status, failure_detail=failure_detail,
                realized=is_realized, divergent=divergent,
            ))

    for c in changes:
        label = c.instance_id
        category = c.object_category

        if label not in objects:
            binding = determine_binding(sim, scene_id, label, category, log,
                                        allocator=asset_allocator)
            objects[label] = RealizedObject(label=label, category=category, binding=binding, events=[])
            if binding.kind == BIND:
                # Seed the carry-forward state from this object's REAL
                # starting position/anchor (item 2: "or its initial pose
                # if the first event fails" — a BIND object has a real
                # physical starting state regardless of whether its
                # first manifest event succeeds; only a SPAWN object
                # genuinely has no prior physical existence to fall back
                # to, so this seeding is BIND-only, not universal).
                #
                # inst.position (env.inventory's census data) is NOT used
                # directly as the pose — confirmed a real gap by direct
                # gold-set comparison: it can differ from the live sim
                # object's own resting translation by enough to break a
                # STATEFUL_FURNITURE object's one narrow passing camera
                # angle (see the "state"/wardrobe gold item). Builder
                # Round 2's own fix for this same class of bug read the
                # LIVE object's translation instead of trusting the
                # census position blindly — replicated here, just
                # triggered upfront instead of deferred to the
                # state_change branch.
                from dynamic_home_eqa.env.inventory import load_scene_state
                inst = load_scene_state(scene_id).instances.get(label)
                if inst is not None and inst.position is not None:
                    seed_handle = find_live_object_at_xz(sim, inst.position)
                    if seed_handle is not None:
                        # Scene-baked HSSD instances load STATIC, and Bullet
                        # SILENTLY ignores `.translation` on a STATIC body —
                        # the compliance placement functions move `obj` per
                        # candidate, so a STATIC handle makes every
                        # candidate evaluate at the object's ORIGINAL
                        # position (confirmed on scene 102344022: every
                        # chair floor-beside placement failed INFEASIBLE
                        # because snap_down kept testing the chair at its
                        # tucked-under-a-table start spot, where it always
                        # contacts the table; the identical placement
                        # succeeds immediately once the handle is
                        # KINEMATIC). Must flip at ACQUISITION, not only
                        # after a successful placement (the old line, which
                        # never ran for a placement that couldn't succeed
                        # in the first place). Same class of bug as
                        # realism_render_job._materialize_object's
                        # documented BIND fix.
                        seed_handle.motion_type = habitat_sim.physics.MotionType.KINEMATIC
                        live_handle[label] = seed_handle
                        t = seed_handle.translation
                        last_effective_pose[label] = RealizedPose.identity_at((t.x, t.y, t.z))
                        last_effective_anchor[label] = inst.current_semantic
                    else:
                        log.append(f"ANOMALY: {label!r} bound but no live rigid object found near its census position (seed).")

        obj_record = objects[label]

        if c.change_type == "state_change":
            audit["not_applicable"] += 1
            # BIND-category (STATEFUL_FURNITURE is always BIND) carry-
            # forward pose is already seeded above at first sight of this
            # label — no special-case live lookup needed here anymore
            # (Builder Round 2's own fix for this is now subsumed by the
            # general item-2 seeding).
            pose = last_effective_pose.get(label)
            _finalize_event(label, c.to_semantic, c.change_type, c.t, c.from_semantic,
                             pose, PLACEMENT_NOT_APPLICABLE)
            continue

        if c.change_type == "remove":
            # Phase 3 put-away: the object leaves the world (to_semantic is
            # the symbolic "away", never a real anchor). Deliberately NOT
            # routed through _finalize_event — its carry-forward semantics
            # ("no object is ever poseless") are exactly wrong here: from
            # this event onward the object HAS no pose, and every pose-at-t
            # consumer must see None (realized_world.pose_at reads the
            # latest event's effective_pose directly; the render job's
            # event-time context parks a spawned context object out of view
            # on a None pose). The live handle is deleted so later
            # placements in this build don't collide against an object
            # that's gone.
            audit["removed_events"] += 1
            rm_handle = live_handle.pop(label, None)
            if rm_handle is not None:
                try:
                    sim.get_rigid_object_manager().remove_object_by_id(rm_handle.object_id)
                except Exception as exc:  # habitat-sim raises plain RuntimeError
                    log.append(f"remove: failed to delete live handle for {label!r}: {exc}")
            last_effective_pose.pop(label, None)
            last_effective_anchor.pop(label, None)
            objects[label].events.append(ObjectEventRecord(
                t=c.t, anchor=c.to_semantic, realized_pose=None,
                placement_status=PLACEMENT_REMOVED, placement_method=None,
                realized=False, effective_pose=None, divergent=False,
            ))
            event_mirrors.append(RealizedEventMirror(
                label=label, change_type=c.change_type, t=c.t,
                from_semantic=c.from_semantic, to_semantic=c.to_semantic,
                placement_status=PLACEMENT_REMOVED, failure_detail=None,
                realized=False, divergent=False,
            ))
            continue

        anchor = c.to_semantic
        # Tucked slots ("dining_room.table_1.tucked" — see rooms.resolve_slot)
        # name the same real furniture as their base census anchor; strip the
        # suffix for classification/position/census resolution, keep the full
        # string on the recorded event (it IS the slot, chain-consistent with
        # the manifest). is_tucked tightens the floor-beside ring below so the
        # chair hugs the furniture face instead of standing clear of it.
        is_tucked = anchor.endswith(".tucked")
        anchor_base = anchor[: -len(".tucked")] if is_tucked else anchor
        kind, cats = classify_anchor(anchor_base)
        audit[kind] += 1

        if kind == "unbacked":
            audit["anchor_unbacked"] += 1
            _finalize_event(label, anchor, c.change_type, c.t, c.from_semantic, None, PLACEMENT_ANCHOR_UNBACKED,
                             failure_detail=f"anchor {anchor!r} has no backing anywhere")
            continue

        from dynamic_home_eqa.rooms import census_label_parts
        is_census_anchor = census_label_parts(normalize_stateful_anchor(anchor_base)) is not None

        target_pos = resolve_anchor_position(world, anchor_base, anchor_census)
        if target_pos is None:
            audit["anchor_unbacked"] += 1
            _finalize_event(label, anchor, c.change_type, c.t, c.from_semantic, None, PLACEMENT_ANCHOR_UNBACKED,
                             failure_detail=f"anchor {anchor!r} classified {kind!r} but no real position resolved "
                                            f"({'census miss' if is_census_anchor else 'navmesh-pruned?'})")
            continue

        if kind == "instance" and not is_census_anchor and normalize_stateful_anchor(anchor_base) not in world._anchor_positions:
            # resolve_anchor_position fell back to a ROOM-CENTROID point
            # (world._ensure_sim() pruned this anchor's own real instance
            # position — it sits on a navmesh island below
            # min_component_area_m2, e.g. this scene's known-disconnected
            # living_room furniture cluster; confirmed directly, not
            # guessed — see tests/test_reachability.py). classify_anchor
            # is a pure string classifier and can't know this; the
            # fallback point is a generic room location, not the real
            # furniture, so there is nothing to bind a live handle to or
            # contain a surface within. Genuinely unbacked FOR PLACEMENT
            # purposes, even though the census confirms the category
            # exists in this scene somewhere.
            audit["anchor_unbacked"] += 1
            _finalize_event(label, anchor, c.change_type, c.t, c.from_semantic, None, PLACEMENT_ANCHOR_UNBACKED,
                             failure_detail=f"anchor {anchor!r}'s real instance position was pruned (disconnected navmesh island) — no usable furniture to place on")
            continue

        handle = live_handle.get(label)
        if handle is None:
            if obj_record.binding.kind == BIND:
                from dynamic_home_eqa.env.inventory import load_scene_state
                inst = load_scene_state(scene_id).instances.get(label)
                handle = find_live_object_at_xz(sim, inst.position) if inst and inst.position else None
                if handle is None:
                    log.append(f"ANOMALY: {label!r} bound but no live rigid object found near its census position.")
                else:
                    # Same STATIC->KINEMATIC-at-acquisition rule as the
                    # seed path above — see that comment.
                    handle.motion_type = habitat_sim.physics.MotionType.KINEMATIC
            else:
                if obj_record.binding.template_name is None:
                    audit["no_asset"] += 1
                    _finalize_event(label, anchor, c.change_type, c.t, c.from_semantic, None, PLACEMENT_NO_ASSET)
                    continue
                # Spawn the label's OWN bound asset (Strategy 2+), never a
                # category-wide lookup — this is what makes bowl_1 and
                # bowl_2 different bowls, and Ana's headphones always hers.
                handle, _asset_id = spawn_new_object(sim, category,
                                                     asset_id=obj_record.binding.template_name)
            live_handle[label] = handle

        if handle is None:
            audit["placement_infeasible"] += 1
            _finalize_event(label, anchor, c.change_type, c.t, c.from_semantic, None, PLACEMENT_INFEASIBLE,
                             failure_detail="no live object handle available")
            continue

        census_record = None
        if is_census_anchor:
            from dynamic_home_eqa.env.anchor_census import resolve_anchor
            census_record = resolve_anchor(anchor_census, normalize_stateful_anchor(anchor_base))

        # Floor-Bound Realization round: three ways an instance-anchor event
        # is realized as a floor placement BESIDE the instance rather than
        # on its surface —
        #   1. proximity-only census anchor (fridge/tv, 0 active
        #      receptacles — Part A; the schema guarantees only near/
        #      next_to can target these);
        #   2. the proposal's own relation is near/next_to (carried through
        #      the manifest as Change.target_relationship — "chair next_to
        #      kitchen.table_1" means beside the table on the floor, which
        #      the slot string alone could never distinguish from "on");
        #   3. the object's category is floor-bound (chair/stool — pushed
        #      in next to furniture, never lifted onto it), regardless of
        #      what a legacy manifest's relation says.
        # None of these ever takes the synthetic AABB-top fallback — that
        # fallback putting objects ON fridge tops/tables is exactly the
        # class this round kills. Legacy bare-category anchors with no
        # relation and a non-floor-bound category are unaffected.
        relation = getattr(c, "target_relationship", None)
        floor_beside = kind == "instance" and (
            (census_record is not None and census_record["active_receptacles"] == 0)
            or relation in PROXIMITY_RELATIONSHIPS
            or category in FLOOR_BOUND_CATEGORIES
        )
        if floor_beside:
            # The candidate ring/tolerance must clear the anchor
            # FURNITURE's own footprint — "beside the counter" means on
            # the floor just past its edge, which is farther from the
            # counter's pivot than the bare open-floor tolerance allows
            # (see compliance_place_region's beside_extent_m comment).
            beside_furniture = furniture_handle_cache.get(anchor_base, "MISS")
            if beside_furniture == "MISS":
                beside_furniture = find_live_object_at_xz(sim, target_pos)
                furniture_handle_cache[anchor_base] = beside_furniture
            beside_extent = 0.0
            beside_min_offset = 0.0
            if beside_furniture is not None:
                (fmin_x, _fy0, fmin_z), (fmax_x, _fy1, fmax_z) = get_world_aabb(beside_furniture)
                beside_extent = max(fmax_x - fmin_x, fmax_z - fmin_z) / 2.0
                # candidates must clear the furniture's SHORT-axis face —
                # the nearest real "beside" position (see
                # compliance_place_region's beside_min_offset_m comment).
                beside_min_offset = min(fmax_x - fmin_x, fmax_z - fmin_z) / 2.0
            if is_tucked:
                # Tucked: hug the furniture face instead of standing clear of
                # it — let candidates start at ~60% of the short-axis
                # half-extent (seat edging under the tabletop). snap_down's
                # collision check walks the ring outward until feasible, so
                # this realizes "as tucked as physically possible", degrading
                # to a beside placement rather than failing.
                beside_min_offset *= 0.6
            final_pos, status = compliance_place_region(
                sim, world, handle, label, f"{label}:{c.t}", target_pos,
                beside_extent_m=beside_extent, beside_min_offset_m=beside_min_offset,
            )
            method = "snap_down" if status == PLACEMENT_OK else None
            audit["proximity_floor_placements"] += 1
            audit["anchor_resolutions"].append({
                "t": c.t, "label": label, "anchor_chosen": anchor,
                "census_backed": census_record is not None,
                "resolved_handle": getattr(beside_furniture, "handle", None),
                "note": f"floor beside instance (relation={relation}, category={category}, "
                        f"beside_extent={beside_extent:.2f}m, tucked={is_tucked})",
            })
        elif kind == "instance":
            # Real receptacle-based placement (Receptacle Infrastructure
            # Investigation round, GO'd — see receptacle_investigation.md):
            # containment within the bound FURNITURE INSTANCE's own real
            # annotated receptacle surface, collision-checked against LIVE
            # sim state via snap_down — not a Python occupancy list.
            # Furniture handle and its receptacles are both cached per
            # anchor string — many events/labels can share the same
            # anchor (a busy dining table), and the furniture itself
            # never moves.
            furniture_handle = furniture_handle_cache.get(anchor_base, "MISS")
            if furniture_handle == "MISS":
                furniture_handle = find_live_object_at_xz(sim, target_pos)
                furniture_handle_cache[anchor_base] = furniture_handle
            audit["anchor_resolutions"].append({
                "t": c.t, "label": label, "anchor_chosen": anchor,
                "census_backed": is_census_anchor,
                "resolved_handle": getattr(furniture_handle, "handle", None),
            })
            if furniture_handle is None:
                # Classified "instance" (a real census/SLOT_ANCHORS match)
                # but the live sim has no rigid object there — should not
                # normally happen (see find_live_object_at_xz's tolerance,
                # already tuned against real data); logged loudly, not
                # silently downgraded to the region/disk path.
                log.append(f"ANOMALY: anchor {anchor!r} classified 'instance' but no live furniture "
                           f"object found at its resolved position — treating as PLACEMENT_INFEASIBLE.")
                final_pos, status, method = None, PLACEMENT_INFEASIBLE, None
            else:
                if anchor not in receptacle_cache:
                    receptacle_cache[anchor] = resolve_furniture_receptacles(
                        sim, scene_id, furniture_handle, active_receptacle_names_cache
                    )
                recs = receptacle_cache[anchor]
                final_pos, status, method = compliance_place_on_surface(
                    sim, handle, label, f"{label}:{c.t}", target_pos, furniture_handle, recs
                )
        else:
            final_pos, status = compliance_place_region(sim, world, handle, label, f"{label}:{c.t}", target_pos)
            method = "snap_down" if status == PLACEMENT_OK else None
        audit[status] += 1
        if method is not None:
            audit["placement_method"][method] += 1

        if status == PLACEMENT_OK:
            # Both branches (instance via compliance_place_on_surface,
            # region via compliance_place_region) are validated live
            # against the real sim by snap_down now — no Python-side
            # occupancy/footprint booking needed for either (see
            # compliance_place_on_surface's docstring for why the old
            # booking list was itself the bug this replaces).
            # A BIND-category `handle` (env.inventory.load_scene_state's
            # real, scene-baked instance) loads as motion_type STATIC —
            # Bullet silently ignores a `.translation` assignment on a
            # STATIC body (confirmed directly, see the Spectator Camera
            # round's identical fix in realism_render_job._materialize_object).
            # Harmless to THIS pass's own recorded data (final_pos, not
            # handle.translation, is what RealizedPose below actually
            # uses, and every collision/occupancy check above is pure
            # Python bookkeeping against `occupancy`, never a Bullet query
            # against `handle`'s live transform) — fixed anyway so this
            # line does what it visibly claims to do, not a silent no-op
            # landmine for a future reader/consumer of the build sim's
            # live state.
            handle.motion_type = habitat_sim.physics.MotionType.KINEMATIC
            handle.translation = mn.Vector3(*final_pos)
            pose = RealizedPose.identity_at(final_pos)
        else:
            pose = None

        _finalize_event(label, anchor, c.change_type, c.t, c.from_semantic, pose, status, method,
                         failure_detail=None if status == PLACEMENT_OK else f"{status} at {anchor!r}")

    for obj in live_handle.values():
        if obj is not None:
            try:
                sim.get_rigid_object_manager().remove_object_by_id(obj.object_id)
            except Exception:
                pass

    header = RealizedDayHeader(
        scene_id=scene_id, day_seed=folder, builder_version=_BUILDER_VERSION,
        code_hash=_code_hash(), trace_hash=_trace_hash(manifest),
    )
    artifact = RealizedDayArtifact(header=header, objects=objects, events=event_mirrors)
    audit["log"] = log
    audit["n_events"] = len(event_mirrors)
    audit["n_objects"] = len(objects)
    return artifact, audit


_DEFAULT_TEST_FOLDER = "102343992_family_with_kids"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # Default: the one scene/profile used as the fixture throughout this
    # project's own test suite and every round's own verification work —
    # a no-arg invocation is then a real, fast, single-folder smoke test
    # of the whole builder, not an error (see the top-level README's
    # pipeline instructions, which rely on this default matching
    # gen_dataset.py's own no-arg default folder).
    ap.add_argument("--folders", nargs="+", default=[_DEFAULT_TEST_FOLDER])
    ap.add_argument("--gen-dir", default=str(_GEN_OUT),
                    help="directory holding the generation folders (default: generation_out/)")
    ap.add_argument("--out-dir", default=str(_OUT_DIR),
                    help="where {folder}.realized_day.json artifacts land (default: "
                         "data/realized_days/). Artifacts are keyed by folder NAME "
                         "alone, so two runs that share a folder name (e.g. the same "
                         "scene+profile generated by two different models into two "
                         "--gen-dirs) MUST use distinct --out-dirs or the second "
                         "build silently overwrites the first run's artifact.")
    args = ap.parse_args()

    import pathlib as _pl
    gen_dir = _pl.Path(args.gen_dir)
    if not gen_dir.is_absolute():
        gen_dir = _DYNAMIC_EQA / gen_dir
    artifact_out_dir = _pl.Path(args.out_dir)
    if not artifact_out_dir.is_absolute():
        artifact_out_dir = _DYNAMIC_EQA / artifact_out_dir

    from dynamic_home_eqa.embodied.world import EmbodiedWorld
    from dynamic_home_eqa.scripts.realism_render_job import _make_render_sim

    total_audit = {}
    for folder in args.folders:
        gen_result = json.loads((gen_dir / folder / "generation_result.json").read_text())
        manifest = json.loads((gen_dir / folder / "manifest.json").read_text())
        scene_id = gen_result["scene_id"]

        for category in sorted({c["object_category"] for c in manifest["changes"]}):
            assert_category_has_asset_coverage(category)

        print(f"\n=== building {folder} (scene {scene_id}) ===")
        sim = _make_render_sim(scene_id)  # enable_physics + renderer off would be enough, but reuses a known-good factory
        world = EmbodiedWorld(scene_id, gen_result, manifest)
        try:
            # manifest passed explicitly: build_realized_day's None-default
            # re-reads from the hardcoded generation_out/ — silently building
            # from the WRONG pool whenever --gen-dir points elsewhere (bit
            # exactly that way on the labelset renders: artifact events came
            # from the frozen pool while the render job pooled the labelset
            # manifests, so every t-lookup missed).
            artifact, audit = build_realized_day(folder, scene_id, sim, world, manifest=manifest,
                                                 clutter=gen_result.get("clutter", []))
        finally:
            world.close()
            sim.close()

        out_path = artifact_out_dir / f"{folder}.realized_day.json"
        save_realized_day(artifact, out_path)
        # Part A: the upstream abstain counters (proposals the model
        # explicitly declined with the "none" anchor, dropped before
        # grounding — see generation/pipeline.py) surface in the build
        # audit too, so one log answers "how much did the vocabulary
        # change suppress" alongside "what did the builder do".
        audit["abstained_upstream"] = (
            gen_result.get("abstained_proposals", 0) + gen_result.get("abstained_clutter", 0)
        )
        total_audit[folder] = audit

        print(f"  objects: {audit['n_objects']}  events: {audit['n_events']}")
        print(f"  abstained upstream (generation, pre-grounding): {audit['abstained_upstream']}")
        print(f"  anchor classification: instance={audit['instance']} region={audit['region']} unbacked={audit['unbacked']}")
        print(f"  placement outcome: ok={audit['ok']} surface_full={audit['surface_full']} "
              f"support_mesh_gap={audit['support_mesh_gap']} no_receptacle_authored={audit['no_receptacle_authored']} "
              f"infeasible={audit['placement_infeasible']} anchor_unbacked={audit['anchor_unbacked']} "
              f"no_asset={audit['no_asset']} not_applicable={audit['not_applicable']}")
        pm = audit["placement_method"]
        print(f"  placement_method (of ok): snap_down={pm['snap_down']} surface_height={pm['surface_height']} synthetic={pm['synthetic']}")
        unrealized_rate = audit["unrealized_events"] / audit["n_events"] if audit["n_events"] else 0.0
        divergent_rate = audit["divergent_events"] / audit["n_events"] if audit["n_events"] else 0.0
        if _FOOTPRINT_SUSPECTS:
            print(f"  overhang-suspect placements (collider QA, not rejected): {len(_FOOTPRINT_SUSPECTS)}")
            for s in _FOOTPRINT_SUSPECTS[:8]:
                print(f"    {s}")
            _FOOTPRINT_SUSPECTS.clear()
        print(f"  unrealized-event rate: {unrealized_rate:.1%} ({audit['unrealized_events']}/{audit['n_events']})  "
              f"divergent-object-time rate: {divergent_rate:.1%} ({audit['divergent_events']}/{audit['n_events']})")
        for line in audit["log"]:
            print(f"  {line}")
        print(f"  wrote {out_path}")

    report_path = _DYNAMIC_EQA / "results" / "reports" / "realized_day_build_log.json"
    report_path.write_text(json.dumps(total_audit, indent=2, default=str))
    print(f"\nFull build log: {report_path}")


if __name__ == "__main__":
    main()
