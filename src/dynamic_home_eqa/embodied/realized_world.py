"""
realized_world.py — the realized_day.json schema + read-side lookups.

This module owns the OUTPUT of the offline builder
(scripts/build_realized_day.py) — one realized_day.json per (scene, day)
folder, produced ONCE, deterministically, and read by everything
downstream (render job, oracle sensor, future perception). No
habitat_sim dependency here — pure data schema plus the lookup helpers
that only need the artifact itself, keeping the repo's split between
pure-logic and habitat_sim-dependent modules.

Two truths (see the builder's own docstring for the full rationale): the
semantic anchor is the ANSWER (questions/belief/kernels unchanged); the
realized_pose is the APPEARANCE (cameras/occlusion/perception). Both are
recorded per object per event, plus a placement_status explaining any
gap between them.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import asdict, dataclass, field
from typing import Optional

PLACEMENT_OK = "ok"
PLACEMENT_SURFACE_FULL = "surface_full"                # receptacle exists, collider sound, genuinely no collision-free sample
PLACEMENT_INFEASIBLE = "placement_infeasible"           # compliance resolution pushed the object out of anchor tolerance
PLACEMENT_ANCHOR_UNBACKED = "anchor_unbacked"            # instance-style anchor with no real backing scene instance
PLACEMENT_NO_ASSET = "no_asset_for_category"             # spawn category with no registered asset (keys/wallet)
PLACEMENT_NOT_APPLICABLE = "not_applicable"              # state_change event — no position to realize
PLACEMENT_REMOVED = "removed"                            # remove event (Phase 3 put-away) — the object left the
                                                         # world; deliberate, NOT a failure. Its effective_pose is
                                                         # None from this event onward, which every pose-at-t
                                                         # consumer (pose_at below, the render job's event-time
                                                         # context) reads as "not present".
# Pre-Pool-Build Remediation round: PLACEMENT_SURFACE_FULL split into
# distinguishable causes (was previously one bucket conflating all of
# these) — see build_realized_day.py's compliance_place_on_surface for
# the live detection logic and receptacle_investigation.md /
# replatform_flip_report.md for the concrete bedroom.bed (support-mesh
# gap) / fridge (no annotation) findings that motivated the split.
# (A fourth status, receptacle_curated_out — a hard block whenever every
# receptacle was curator-filtered — was REMOVED in the Realizable-Anchor
# Vocabulary round: curation is now enforced at LLM generation time via
# the anchor census (a curated-out anchor is proximity-only, never a
# surface target), so the build-time hard block only ever hit legacy
# manifests, where it blanket-blocked e.g. every wardrobe placement; an
# empty active-receptacle set now takes the synthetic-top fallback
# instead. Old artifacts on disk may still carry the retired string.)
PLACEMENT_SUPPORT_MESH_GAP = "support_mesh_gap"          # receptacle exists but snap_down's collider raycast never reaches it
PLACEMENT_NO_RECEPTACLE_AUTHORED = "no_receptacle_authored"  # zero usable receptacles for this furniture

_ALL_PLACEMENT_STATUSES = {
    PLACEMENT_OK, PLACEMENT_SURFACE_FULL, PLACEMENT_INFEASIBLE,
    PLACEMENT_ANCHOR_UNBACKED, PLACEMENT_NO_ASSET, PLACEMENT_NOT_APPLICABLE,
    PLACEMENT_SUPPORT_MESH_GAP, PLACEMENT_NO_RECEPTACLE_AUTHORED,
}

BIND = "scene_instance"   # bound to a real, pre-existing HSSD scene instance
SPAWN = "spawned"          # a new object mesh instantiated by the builder


@dataclass(frozen=True)
class RealizedPose:
    pos: tuple[float, float, float]
    quat: tuple[float, float, float, float]  # (w, x, y, z)

    def to_json(self) -> dict:
        return {"pos": list(self.pos), "quat": list(self.quat)}

    @staticmethod
    def from_json(d: dict) -> "RealizedPose":
        return RealizedPose(pos=tuple(d["pos"]), quat=tuple(d["quat"]))

    @staticmethod
    def identity_at(pos: tuple[float, float, float]) -> "RealizedPose":
        return RealizedPose(pos=pos, quat=(1.0, 0.0, 0.0, 0.0))


@dataclass(frozen=True)
class ObjectEventRecord:
    t: float
    anchor: str
    realized_pose: Optional[RealizedPose]
    placement_status: str
    # Pre-Pool-Build Remediation round additions (additive, no field removed):
    placement_method: Optional[str] = None  # None (unrealized) / "snap_down" / "surface_height" / "synthetic"
    # realized: whether THIS event's OWN placement attempt succeeded
    # (equivalent to realized_pose is not None, stored explicitly per the
    # round's schema spec rather than left implicit).
    realized: bool = False
    # effective_pose: what the physical world actually shows RIGHT NOW,
    # regardless of whether THIS event realized — carries forward the
    # last successfully-realized pose when this event did not (see
    # build_realized_day.py's main loop). Never None for a BIND-category
    # object (seeded from its real scene starting position before any
    # event runs); can be None for a SPAWN-category object that has never
    # yet been successfully placed at all (it has no physical existence
    # to carry forward from — an honest "not yet in the world" state, not
    # a bug).
    effective_pose: Optional[RealizedPose] = None
    # divergent: True when effective_pose's own anchor (wherever the
    # object's carried-forward pose actually came from) differs from this
    # event's symbolic anchor -- i.e. the physical world and the trace's
    # claimed answer have split. Oracle-v2/perception should read this
    # before trusting effective_pose as "the object is where the trace
    # says": the trace (symbolic tier) is still authoritative for
    # question answers regardless of this flag.
    divergent: bool = False

    def to_json(self) -> dict:
        return {
            "t": self.t, "anchor": self.anchor,
            "realized_pose": self.realized_pose.to_json() if self.realized_pose is not None else None,
            "placement_status": self.placement_status,
            "placement_method": self.placement_method,
            "realized": self.realized,
            "effective_pose": self.effective_pose.to_json() if self.effective_pose is not None else None,
            "divergent": self.divergent,
        }

    @staticmethod
    def from_json(d: dict) -> "ObjectEventRecord":
        pose = RealizedPose.from_json(d["realized_pose"]) if d.get("realized_pose") is not None else None
        # Legacy artifacts (built before the Pre-Pool-Build Remediation
        # round's schema additions) have no "realized" key at all —
        # naively defaulting
        # realized=False/effective_pose=None for every event in an old
        # artifact makes every one of its OK placements look like a
        # failure to any reader keying off the new fields (render job,
        # future Oracle-v2 consumers) — silently breaking every
        # not-yet-rebuilt scene rather than just those genuinely
        # rebuilt under the new taxonomy. realized_pose has been
        # reliably populated since before this round and is always the
        # correct ground truth for "did this specific event's own
        # placement succeed" — used here to backfill the new fields
        # exactly as build_realized_day.py's _finalize_event would have
        # computed them for an artifact with no unrealized events at all
        # (which is what every pre-this-round artifact's schema
        # implicitly assumed).
        if "realized" in d:
            effective = RealizedPose.from_json(d["effective_pose"]) if d.get("effective_pose") is not None else None
            realized = d.get("realized", False)
            divergent = d.get("divergent", False)
        else:
            effective = pose
            realized = pose is not None
            divergent = False
        return ObjectEventRecord(
            t=d["t"], anchor=d["anchor"], realized_pose=pose, placement_status=d["placement_status"],
            placement_method=d.get("placement_method"), realized=realized,
            effective_pose=effective, divergent=divergent,
        )


@dataclass(frozen=True)
class ObjectBinding:
    kind: str  # BIND or SPAWN
    scene_instance_index: Optional[int] = None   # array index into scene_instance.json's object_instances, BIND only
    template_name: Optional[str] = None           # HSSD asset handle actually used, either kind
    source: str = "hssd"                           # "hssd" | "hssd_spawnable" | "external_props" (future Objaverse), etc.

    def to_json(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_json(d: dict) -> "ObjectBinding":
        return ObjectBinding(**d)


@dataclass
class RealizedObject:
    label: str
    category: str
    binding: ObjectBinding
    events: list[ObjectEventRecord] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "label": self.label, "category": self.category,
            "binding": self.binding.to_json(),
            "events": [e.to_json() for e in self.events],
        }

    @staticmethod
    def from_json(d: dict) -> "RealizedObject":
        return RealizedObject(
            label=d["label"], category=d["category"],
            binding=ObjectBinding.from_json(d["binding"]),
            events=[ObjectEventRecord.from_json(e) for e in d["events"]],
        )


@dataclass
class RealizedEventMirror:
    """One entry per original trace event (manifest["changes"] order),
    annotated with its realized outcome — lets a consumer iterate events
    in original trace order without re-deriving per-label event indices."""
    label: str
    change_type: str
    t: float
    from_semantic: Optional[str]
    to_semantic: Optional[str]
    placement_status: str
    failure_detail: Optional[str] = None  # free-text, e.g. which anchor/category mismatch
    # Pre-Pool-Build Remediation round: mirrors ObjectEventRecord's own
    # realized/divergent flags here too, so a consumer iterating in flat
    # trace order (this class's own purpose) can compute the
    # unrealized-event rate / divergent-object-time rate benchmark-card
    # statistics without cross-referencing back into `objects`.
    realized: bool = False
    divergent: bool = False

    def to_json(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_json(d: dict) -> "RealizedEventMirror":
        # Same legacy-artifact concern as ObjectEventRecord.from_json:
        # backfill "realized" for a pre-remediation-round artifact rather
        # than silently defaulting to False for every event. This mirror
        # has no realized_pose to check directly (unlike
        # ObjectEventRecord), so the best available proxy is
        # placement_status == PLACEMENT_OK — an approximation for the
        # rare NOT_APPLICABLE/state-change case (whose old BIND-lookup
        # fallback could populate a real pose at the object-record level
        # without this mirror ever recording it), acceptable because
        # this field only feeds the benchmark-card rate statistics, not
        # placement/rendering behavior.
        if "realized" not in d:
            d = {**d, "realized": d.get("placement_status") == PLACEMENT_OK, "divergent": False}
        return RealizedEventMirror(**d)


@dataclass
class RealizedDayHeader:
    scene_id: str
    day_seed: str          # the folder name — the actual unit of determinism for this artifact
    builder_version: str
    code_hash: str
    trace_hash: str

    def to_json(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_json(d: dict) -> "RealizedDayHeader":
        return RealizedDayHeader(**d)


@dataclass
class RealizedDayArtifact:
    header: RealizedDayHeader
    objects: dict[str, RealizedObject]
    events: list[RealizedEventMirror]

    def to_json(self) -> dict:
        return {
            "header": self.header.to_json(),
            "objects": {label: obj.to_json() for label, obj in self.objects.items()},
            "events": [e.to_json() for e in self.events],
        }

    @staticmethod
    def from_json(d: dict) -> "RealizedDayArtifact":
        return RealizedDayArtifact(
            header=RealizedDayHeader.from_json(d["header"]),
            objects={label: RealizedObject.from_json(o) for label, o in d["objects"].items()},
            events=[RealizedEventMirror.from_json(e) for e in d["events"]],
        )


def save_realized_day(artifact: RealizedDayArtifact, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact.to_json(), indent=2))


def load_realized_day(path: pathlib.Path) -> RealizedDayArtifact:
    return RealizedDayArtifact.from_json(json.loads(path.read_text()))


def pose_at(artifact: RealizedDayArtifact, label: str, t: float) -> Optional[RealizedPose]:
    """The pose the physical world actually shows for `label` at time
    `t` — the Oracle-v2 / render-job read path (Pre-Pool-Build
    Remediation round, item 2). Returns the last event's own
    `effective_pose` (event.t <= t), or None if the label isn't tracked
    or has no event at or before t. Carry-forward across an unrealized
    event (the "no object is ever poseless" rule) is computed ONCE at
    build time (build_realized_day.py's _finalize_event) and baked into
    every event's own `effective_pose` — this function no longer
    re-derives it by scanning past events for a real `realized_pose`,
    it just reads whatever effective_pose the selected event already
    carries. Events are stored in the order the builder applied them,
    which is trace (t-ascending) order — a linear scan is fine at this
    scale (order 10s of events per object per day)."""
    obj = artifact.objects.get(label)
    if obj is None:
        return None
    best: Optional[ObjectEventRecord] = None
    for e in obj.events:
        if e.t <= t:
            if best is None or e.t >= best.t:
                best = e
    return best.effective_pose if best is not None else None


def anchor_at(artifact: RealizedDayArtifact, label: str, t: float) -> Optional[str]:
    """The semantic anchor (the ANSWER) for `label` at time `t` — same
    lookup rule as pose_at, but returns the anchor string regardless of
    whether that event's placement actually succeeded (a failed
    placement's anchor is still the true semantic answer; only its
    APPEARANCE is missing — see the module docstring's "two truths")."""
    obj = artifact.objects.get(label)
    if obj is None:
        return None
    best: Optional[ObjectEventRecord] = None
    for e in obj.events:
        if e.t <= t:
            if best is None or e.t >= best.t:
                best = e
    return best.anchor if best is not None else None


def unrealized_event_rate(artifact: RealizedDayArtifact) -> float:
    """Item 2's first benchmark-card statistic: fraction of this
    artifact's events whose own placement failed (`realized=False`),
    regardless of whether a carried-forward effective_pose was
    available. Read-side, operates on the saved artifact directly (the
    same numbers build_realized_day.py's own audit dict tallies during
    the build, exposed here for a future benchmark-card/report step that
    reads realized_day.json files without re-running the builder).
    Returns 0.0 for an artifact with no events."""
    if not artifact.events:
        return 0.0
    return sum(1 for e in artifact.events if not e.realized) / len(artifact.events)


def divergent_object_time_rate(artifact: RealizedDayArtifact) -> float:
    """Item 2's second benchmark-card statistic: fraction of this
    artifact's events where the carried-forward effective_pose's own
    anchor differs from the event's symbolic anchor (`divergent=True`)
    — how often the physical world a camera would see disagrees with
    the trace's claimed answer. A subset of the unrealized events (only
    ones with a real carried-forward pose to diverge FROM can be
    divergent at all — see ObjectEventRecord.divergent's docstring).
    Returns 0.0 for an artifact with no events."""
    if not artifact.events:
        return 0.0
    return sum(1 for e in artifact.events if e.divergent) / len(artifact.events)
