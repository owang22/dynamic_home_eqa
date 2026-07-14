"""
trace_validate.py — pure hard-invariant validator for one generated day trace.

No I/O, no pipeline imports beyond rooms.py (the shared room vocabulary).
`validate(changes, traces)` checks a manifest's Change-log against the four
hard invariants every exported day trace must satisfy:

  1. Chain consistency — an event's from_semantic must equal the same
     label's previous event's to_semantic (or be that label's first event,
     which has nothing to check against).
  2. Insert-once — insert_new fires at most once per label per day; every
     later event for that label must be move_existing.
  3. No no-ops — from_semantic must differ from to_semantic.
  4. Attendance — the event's source or destination room must contain an
     occupant (per `traces`) at event time. For a change_type=="remove"
     (Phase 3 despawn/put-away of a carried Tier-3 item), the item travels
     with its owner rather than sitting in a room, so this instead requires
     the mover to be home (a real, non-"away" activity location) at event time.

For change_type == "state_change" (M3: state-change dynamics), invariants
1 and 3 are checked on (from_state, to_state) keyed by (label,
state_variable) instead of (from_semantic, to_semantic) keyed by label —
a stateful instance's location never changes (from_semantic == to_semantic
== the instance's fixed bare-category slot, by construction — see
env/inventory.py's STATEFUL_FURNITURE seeding), so the ordinary no-op
check would misfire on every state event if applied to the location
fields. Insert-once doesn't apply (state variables have no insert
semantics — the instance exists from scene-init). Attendance is
unchanged: state_change events still carry from_semantic/to_semantic (the
furniture's own fixed room), so the same room-derivation logic applies.

Findings are independent of whatever the manifest itself claims (e.g. its
`mover` field) — attendance is re-derived straight from `traces`, so this
validator still catches a manifest that mis-attributes its own events.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .rooms import location_at, occupants_in_room, slot_room


class FindingKind(str, Enum):
    CHAIN_BREAK = "chain_break"
    RE_INSERT   = "re_insert"
    NO_OP       = "no_op"
    UNATTENDED  = "unattended"


class Severity(str, Enum):
    HARD = "hard"
    SOFT = "soft"


@dataclass(frozen=True)
class Finding:
    kind:     FindingKind
    severity: Severity
    index:    int           # position in the time-sorted event list
    label:    str
    message:  str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    n_events: int = 0

    def count(self, kind: FindingKind) -> int:
        return sum(1 for f in self.findings if f.kind == kind)

    @property
    def chain_breaks(self) -> int:
        return self.count(FindingKind.CHAIN_BREAK)

    @property
    def re_inserts(self) -> int:
        return self.count(FindingKind.RE_INSERT)

    @property
    def no_ops(self) -> int:
        return self.count(FindingKind.NO_OP)

    @property
    def unattended(self) -> int:
        return self.count(FindingKind.UNATTENDED)

    @property
    def ok(self) -> bool:
        """True iff no hard-invariant violations were found."""
        return not any(f.severity == Severity.HARD for f in self.findings)

    def summary(self) -> str:
        return (
            f"{self.n_events} events — chain_breaks={self.chain_breaks} "
            f"re_inserts={self.re_inserts} no_ops={self.no_ops} "
            f"unattended={self.unattended}"
        )

    def validation_hash(self) -> str:
        """Deterministic hash of this report's hard-invariant outcome
        (ok + the four violation counts) — the contamination-audit
        primitive (navmesh-connectivity phase's stale-day0 finding):
        any artifact that consumes a scene-day's manifest should record
        this hash for every folder it reads, so a later re-validation
        (e.g. after regenerating a previously-corrupted day) is
        mechanically detectable — the hash changes, and any pool-level
        fingerprint incorporating it changes too, rather than requiring
        someone to remember which days were ever suspect."""
        import hashlib
        payload = repr((self.ok, self.chain_breaks, self.re_inserts, self.no_ops, self.unattended))
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


def validate(changes: list[dict], traces: list[dict]) -> Report:
    """Check the hard trace-integrity invariants against a manifest's changes.

    Args:
        changes: manifest.json's "changes" list — dicts with at least
                 t, label, change_type, object_category, from_semantic,
                 to_semantic.
        traces:  generation_result.json's "traces" list — one dict per
                 occupant, each {occupant_name, activities: [{activity,
                 location, start, end}, ...]}.
    """
    report = Report(n_events=len(changes))
    events = sorted(changes, key=lambda c: (float(c.get("t", 0.0)), c.get("label", "")))

    last_to:       dict[str, Optional[str]] = {}
    last_to_state: dict[tuple[str, str], Optional[str]] = {}  # (label, state_variable) -> to_state
    inserted:      set[str] = set()

    for idx, c in enumerate(events):
        label    = c.get("label", "")
        ctype    = c.get("change_type", "")
        from_sem = c.get("from_semantic")
        to_sem   = c.get("to_semantic")
        t        = float(c.get("t", 0.0))
        is_state = ctype == "state_change"

        if is_state:
            variable   = c.get("state_variable")
            from_state = c.get("from_state")
            to_state   = c.get("to_state")
            state_key  = (label, variable)

            # 1. Chain consistency, keyed by (label, state_variable) — a
            # label's location and its state track independent chains.
            if state_key in last_to_state and from_state != last_to_state[state_key]:
                report.findings.append(Finding(
                    FindingKind.CHAIN_BREAK, Severity.HARD, idx, label,
                    f"{label}@t={t:.2f}: from_state={from_state!r} (variable={variable!r}) "
                    f"but the previous event for this label/variable left it at "
                    f"{last_to_state[state_key]!r}",
                ))

            # 3. No no-ops, on (from_state, to_state) — from_semantic ==
            # to_semantic is EXPECTED for a state_change event (the
            # furniture never moves; see module docstring), so the
            # location no-op check below must not run for these.
            if from_state is not None and from_state == to_state:
                report.findings.append(Finding(
                    FindingKind.NO_OP, Severity.HARD, idx, label,
                    f"{label}@t={t:.2f}: from_state == to_state == {to_state!r} (variable={variable!r})",
                ))

            last_to_state[state_key] = to_state
        else:
            # 1. Chain consistency: skip the label's first-ever event —
            # there is no prior state within `changes` to check it against.
            if label in last_to and from_sem != last_to[label]:
                report.findings.append(Finding(
                    FindingKind.CHAIN_BREAK, Severity.HARD, idx, label,
                    f"{label}@t={t:.2f}: from_semantic={from_sem!r} but the previous "
                    f"event for this label left it at {last_to[label]!r}",
                ))

            # 3. No no-ops (a first-event insert_new with from_semantic=None
            # is exempt by construction — None != to_semantic trivially).
            if from_sem is not None and from_sem == to_sem:
                report.findings.append(Finding(
                    FindingKind.NO_OP, Severity.HARD, idx, label,
                    f"{label}@t={t:.2f}: from_semantic == to_semantic == {to_sem!r}",
                ))

        # 2. Insert-once (state_change events are never insert_new, so this
        # never fires for them — state variables have no insert semantics,
        # the instance exists from scene-init).
        if ctype == "insert_new":
            if label in inserted:
                report.findings.append(Finding(
                    FindingKind.RE_INSERT, Severity.HARD, idx, label,
                    f"{label}@t={t:.2f}: insert_new fired again; an earlier "
                    f"event already inserted this label",
                ))
            inserted.add(label)

        # 4. Attendance.
        if ctype == "remove":
            # A removal (Phase 3 despawn/put-away) is an occupant pocketing
            # their OWN carried Tier-3 item — it travels with them, so it need
            # not sit in any fixed room and to_semantic is the symbolic "away".
            # The room-presence check below would misfire (destination room is
            # None). The meaningful invariant instead: the mover is actually
            # home (a real, non-"away" activity location) at event time. Still
            # re-derived from `traces`, so a put-away claimed while its mover is
            # out of the house is caught.
            mover = c.get("mover")
            mover_room = next(
                (location_at(tr.get("activities", []), t)
                 for tr in traces if tr.get("occupant_name") == mover),
                None,
            )
            if mover_room is None or mover_room == "away":
                report.findings.append(Finding(
                    FindingKind.UNATTENDED, Severity.HARD, idx, label,
                    f"{label}@t={t:.2f}: remove/put-away but mover {mover!r} is "
                    f"not home (location={mover_room!r}) at event time",
                ))
        else:
            # (state_change events still carry from_semantic/to_semantic, the
            # furniture's own fixed room, so the room derivation applies.)
            dest_room = slot_room(to_sem)
            src_room  = slot_room(from_sem)
            present = set(occupants_in_room(traces, dest_room, t)) \
                | set(occupants_in_room(traces, src_room, t))
            if not present:
                report.findings.append(Finding(
                    FindingKind.UNATTENDED, Severity.HARD, idx, label,
                    f"{label}@t={t:.2f}: no occupant in source ({src_room!r}) or "
                    f"destination ({dest_room!r}) room (manifest claimed mover: "
                    f"{c.get('mover')!r})",
                ))

        last_to[label] = to_sem

    return report
