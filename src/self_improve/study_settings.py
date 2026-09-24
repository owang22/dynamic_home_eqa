"""The study's settings in one place, with the measurement behind each one.

Everything here is a parameter. Nothing about the sensing granularity, the
budget or the visit times is written into the other modules.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Settings:
    # ---- which scenario. Locked 2026-09-24.
    banks: str = "results/regime_search/sick10_partial/banks"
    """One resident off sick, questions asked about EVERYONE's things. Read-only:
    this directory belongs to another paper's finished numbers.

    Why not the owner-only regime: there every asked object belongs to the sick
    resident and nearly all of them land on the same coffee table, so one
    sentence covers the whole disruption and a per-claim memory cannot beat a
    wholesale rewrite by construction. Worse, the sick window there is EASIER
    than ordinary life: answering "coffee table" to everything scores 78% and
    knowing every object's own commonest place perfectly scores 83%, five points
    of headroom against a one-to-two-point rerun floor. In this regime the same
    two baselines are 58% and 80%: twenty-two points of headroom.

    Here each household has 8 to 18 asked objects, 3 to 8 of which move, to 1 to
    5 different destinations, and the rest never move at all - so the memory has
    both revision and preservation to do."""

    exclusion_rule_measured: str = "over daytime hours"
    """Households are dropped when fewer than two asked objects change their
    usual place. WHICH households that drops depends on this choice and the two
    answers differ: measured over daytime hours it drops none, measured at
    question times it drops s4. See which_objects_moved.py."""

    # ---- sensing. Locked 2026-09-24 on measured evidence; see EXPECTATIONS.md.
    granularity: str = "room"
    """Rooms, not places. A rotation over a household's 32 to 47 places takes 11
    to 15 days for one pass, longer than the ten-day disruption, so which
    households ever notice it would come down to where the rotation started."""

    budget_per_look: int = 1
    """One room per look. At three rooms a look a plain rotation sweeps the whole
    house every two to three days, leaving a robot that chooses nothing to find.
    At one room a look a rotation takes six to nine days, so the schedule
    typically sees the disruption late or not at all while a robot reasoning from
    its own failures can be there in a day or two."""

    visit_times: List[str] = field(default_factory=lambda: ["13:00"])
    """Daytime, in the middle of the 10:00-17:00 plateau where 71 to 75% of the
    disruption is visible. No 3am sweep: at 3am only 9 of the 53 asked-about
    objects across the ten households have a different resting place in the
    disrupted period than in the settled one, and in three households none do,
    so a night look cannot see the disruption at all. It would also hand every
    arm the same free evidence and shrink the differences we are measuring."""

    fixed_schedule_kind: str = "fair over every target"
    """The honest control. The alternative - rotate only the rooms that usually
    held things during the ordinary fortnight - never visits the room the
    disruption moves into in 9 of the 10 frozen households, because that room is
    in the settled-period top three in only one of them. A control that cannot
    possibly detect the change is rigged, not fair."""

    shared_warm_start: bool = False
    """One walkthrough of the whole house on day 0 at 18:00, the same for every
    arm. Off by default. Measured reason it may be needed: one room a day gives
    only 4.0 sightings per asked-about object across the whole month, and only
    17.6 days in 32 on which any asked-about object is seen at all (8 in the worst
    household), so claims about the ordinary routine rest on about two sightings
    each. Being identical across arms, it cannot favour one."""

    rotation_seed: int = 0
    """The order the fixed rota is walked in, per household. When one full pass
    takes longer than the thing being detected, this order carries the result, so
    it is chosen and recorded rather than left to how the room names sort."""

    # ---- the two budgets. They are separate and must not be merged.
    curation_looks_per_asked_object: int = 3
    """Looks spent on keeping the notes, across the whole study: about 36 looks
    in this regime, so roughly one a day, which is what the one-room-a-day
    design already gives."""

    search_looks_when_answering: int = 3
    """Places the robot may check while answering one question. This count is the
    headline search-cost metric and is reported separately from accuracy."""

    # ---- answering. Identical across every arm.
    retrieval_budget: int = 4
    """How many claims the model may read at answer time. The same for every arm,
    so no arm wins by reading more. Four, not twelve: a household has only 8 to 18
    asked-about objects, so a budget of twelve never forces the retrieval to
    choose anything and we could not claim that reading had been tested at all."""

    # ---- the model. Local vLLM only; no hosted API, no spend.
    endpoint: str = "http://localhost:8300"
    temperature: float = 0.0

    # ---- households.
    households: Optional[List[str]] = None
    """None means all ten frozen households. Results are always reported per
    household and then combined; nothing is ever pooled across household sets."""

    # ---- how much of a difference is real.
    noise_floor: float = 0.05
    """Generation on this server is not deterministic: the same notes rerun on
    the same data change about 3 to 5% of their answers. Treat any difference
    smaller than this as noise."""


LOCKED = Settings()
