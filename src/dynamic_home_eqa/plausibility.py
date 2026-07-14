"""
plausibility.py — soft, scored plausibility warnings for generated day traces.

These are advisory: they never reject a proposal (trace_validate.py owns the
hard invariants that do). They score three patterns a manual review of real
generated output surfaced:
  - Occupant capability: would this occupant, given their age_band, plausibly
    do this? A toddler does not relocate a stool, carry a laptop between
    rooms, or own keys/wallet/phone.
  - Egress plausibility: a furniture-class object (stool, chair) heading
    outdoors is unusual and should score low, not zero — it does happen.
  - Ping-pong: the same object bouncing between slots more than a few times
    within an hour is a smell worth surfacing even when each individual move
    is individually plausible.

confidence (manifest.json's per-event field) is the output of
score_confidence() below — not a placeholder constant. day_report() is the
whole-day aggregate warning surface (the "plausibility report alongside the
hard-invariant report" the generation phase's trace-integrity work calls
for), computed independently from whatever confidence values got written, the
same way trace_validate.py re-derives attendance instead of trusting a
manifest's own claims.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Categories a toddler would not plausibly relocate/carry/own themselves.
# Two flavours: heavy/awkward movable furniture they can't physically relocate
# (chair/stool/potted_plant — cushion is intentionally NOT here, a toddler can
# carry a cushion; the other Tier-2a furniture like bench/couch/table are Tier-1
# fixtures that never move anyway), plus small items they wouldn't
# carry/own/handle (laptop/keys/wallet/phone/candle).
TODDLER_RESTRICTED_CATEGORIES: set[str] = {
    "chair", "stool", "potted_plant",
    "laptop", "keys", "wallet", "phone", "candle",
}

# Furniture-class categories that are unusual (not impossible) outdoors.
EGRESS_RESTRICTED_CATEGORIES: set[str] = {"stool", "chair", "bench", "couch"}

_CAPABILITY_PENALTY_FACTOR = 0.15   # score multiplier when capability is violated
_EGRESS_PENALTY_FACTOR     = 0.3    # score multiplier for unusual-outdoor moves
_PINGPONG_WINDOW_HOURS     = 1.0
_PINGPONG_MAX_MOVES        = 3       # moves within the window before penalizing
_PINGPONG_PENALTY_PER_EXCESS = 0.2   # multiplicative penalty per move over the max


def capability_factor(category: str, age_band: Optional[str]) -> float:
    """1.0 if this occupant's age_band plausibly interacts with `category`,
    else _CAPABILITY_PENALTY_FACTOR. Only toddler is restricted today — other
    age bands (young_child through senior) are not penalized here; if review
    surfaces a real problem for another band, extend the table, don't stretch
    this one band to cover it via a broader heuristic."""
    if age_band == "toddler" and category in TODDLER_RESTRICTED_CATEGORIES:
        return _CAPABILITY_PENALTY_FACTOR
    return 1.0


def egress_factor(category: str, to_room: Optional[str]) -> float:
    """1.0 unless a furniture-class object is heading outdoors."""
    if to_room == "outdoor" and category in EGRESS_RESTRICTED_CATEGORIES:
        return _EGRESS_PENALTY_FACTOR
    return 1.0


def pingpong_factor(prior_move_times: list[float], t: float,
                     window: float = _PINGPONG_WINDOW_HOURS,
                     max_moves: int = _PINGPONG_MAX_MOVES) -> float:
    """1.0 unless this label has moved too many times within `window` hours
    of t already. prior_move_times are the label's previous event
    timestamps (not including this one). Penalty compounds per move past
    the threshold, floored at 0.1 so a genuinely frantic label doesn't hit
    exactly zero (still a possible, if unlikely, real pattern)."""
    recent = sum(1 for pt in prior_move_times if abs(t - pt) <= window)
    excess = max(0, recent - (max_moves - 1))
    if excess == 0:
        return 1.0
    return max(0.1, 1.0 - _PINGPONG_PENALTY_PER_EXCESS * excess)


def score_confidence(
    category: str,
    age_band: Optional[str],
    to_room: Optional[str],
    prior_move_times: list[float],
    t: float,
) -> float:
    """Combined per-event confidence in [0, 1]. Multiplicative, not additive —
    an event that is both a capability violation and a ping-pong repeat
    should score lower than either penalty alone, not just take the min."""
    score = 1.0
    score *= capability_factor(category, age_band)
    score *= egress_factor(category, to_room)
    score *= pingpong_factor(prior_move_times, t)
    return round(score, 4)


# ---------------------------------------------------------------------------
# Whole-day advisory report
# ---------------------------------------------------------------------------

@dataclass
class PlausibilityWarning:
    kind:    str    # "capability" | "egress" | "pingpong"
    label:   str
    t:       float
    message: str


@dataclass
class PlausibilityReport:
    warnings: list[PlausibilityWarning] = field(default_factory=list)

    def count(self, kind: str) -> int:
        return sum(1 for w in self.warnings if w.kind == kind)

    def summary(self) -> str:
        kinds = sorted({w.kind for w in self.warnings})
        return "  ".join(f"{k}={self.count(k)}" for k in kinds) or "no warnings"


def day_report(
    changes: list[dict],
    occupant_age_band: dict[str, Optional[str]],
    slot_room_fn,
) -> PlausibilityReport:
    """Re-derive the same three soft-plausibility patterns over a finished
    day's changes, independent of whatever confidence values were written at
    generation time — the same "don't trust the writer's self-report"
    posture trace_validate.py takes for the hard invariants.

    slot_room_fn is rooms.slot_room, passed in rather than imported directly
    so this module has no hard dependency on any one room-resolution scheme.
    """
    report = PlausibilityReport()
    move_times: dict[str, list[float]] = {}

    events = sorted(changes, key=lambda c: (float(c.get("t", 0.0)), c.get("label", "")))
    for c in events:
        label = c.get("label", "")
        cat   = c.get("object_category", "")
        t     = float(c.get("t", 0.0))
        mover = c.get("mover")
        age_band = occupant_age_band.get(mover) if mover else None
        to_room  = slot_room_fn(c.get("to_semantic"))

        if capability_factor(cat, age_band) < 1.0:
            report.warnings.append(PlausibilityWarning(
                "capability", label, t,
                f"{label}@t={t:.2f}: age_band={age_band!r} occupant ({mover}) "
                f"moved {cat!r}, outside its plausible capability set",
            ))
        if egress_factor(cat, to_room) < 1.0:
            report.warnings.append(PlausibilityWarning(
                "egress", label, t,
                f"{label}@t={t:.2f}: furniture-class {cat!r} moved outdoors",
            ))
        prior = move_times.setdefault(label, [])
        if pingpong_factor(prior, t) < 1.0:
            report.warnings.append(PlausibilityWarning(
                "pingpong", label, t,
                f"{label}@t={t:.2f}: {len(prior)} prior moves within "
                f"{_PINGPONG_WINDOW_HOURS}h window",
            ))
        prior.append(t)

    return report
