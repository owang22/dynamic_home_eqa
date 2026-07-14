"""
Prompt registry — the single home for every generation-stage system template.

Each template is a PromptTemplate with a human-readable name and a `version`
(first 8 hex of sha256 over the template text, computed at import). Call
sites fold that version into their stage tag (see PromptTemplate.tag), so the
cache key changes automatically whenever a template's wording changes — it is
impossible to forget to bump a version.

BUILDER_VERSION covers the OTHER half of a prompt: the user-message content
that call sites assemble in Python OUTSIDE these templates (the hand-rolled
line builders in stages.py, and after Phase 2 the ContextBuilder). That text
is not hashed automatically — **if you change how any user prompt is built
without bumping BUILDER_VERSION, stale cached responses will be served
silently.** This is the one remaining manual step in the versioning scheme.

Relocation only: the templates here are byte-identical to their former inline
definitions in stages.py / persona / clutter — no wording changes.
"""
from __future__ import annotations

import hashlib

from ..rooms import CANONICAL_ROOMS as _CANONICAL_ROOMS

# Bump by hand whenever the Python-side user-prompt assembly changes (line
# builders in stages.py, ContextBuilder later). See module docstring.
BUILDER_VERSION = "b1"

_ACTIVITY_LOCATIONS = [*_CANONICAL_ROOMS, "away"]


class PromptTemplate:
    """A named system-prompt template with a content-derived version."""

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text
        self.version = hashlib.sha256(text.encode()).hexdigest()[:8]

    def tag(self, base: str, *, builder: bool = False) -> str:
        """Stage tag with the prompt version folded in (and BUILDER_VERSION
        too when this stage hand-assembles its user prompt)."""
        t = f"{base}_p{self.version}"
        if builder:
            t += f"_{BUILDER_VERSION}"
        return t


PERSONA = PromptTemplate("persona", """\
You are a household behavior modeller. Given a household type, produce a
structured persona describing who lives there, their typical schedule
tendencies, and each occupant's own tidiness.

Tidiness (0–1) is per-occupant, not a household average: 0 = very untidy
(objects left wherever they were last used), 1 = very tidy (objects always
returned to designated places). Real households mix tidy and untidy people
under one roof — a tidy parent and a messy teenager is the normal case, not
an edge case, so don't default every occupant to the same value. Each
occupant's tidiness is used downstream to scale their own cleanup
probability — output it accurately per person.

age_band must be consistent with role: a role like 'father'/'mother' implies
adult; 'daughter'/'son' implies toddler through teen depending on the
household's stated makeup; use 'senior' for a retired or elderly occupant.
This is the knob downstream stages use to decide school vs. work vs.
retirement patterns, so get it right rather than defaulting everyone to
'adult'.

typical_wake and typical_sleep are 24-hour clock hours. typical_sleep in
particular must be expressed on the evening/night side (e.g. 21.0 for 9pm,
22.5 for 10:30pm) — never write a bare morning-looking number to mean an
evening hour, even for a young child who goes to bed early.

habits: give each occupant something concrete that distinguishes their day
from another occupant with a similar role — a specific job, a hobby, a
routine quirk. This matters most when two occupants share a role (e.g. two
working adults, or two children close in age). Give every occupant a real, separate voice and unique personality.

owned_items: the carried personal items (phone/wallet/keys/laptop) THIS
occupant owns and moves around. Assign per person, not per household — a
working adult usually carries all four, a teenager a phone and laptop, a
young child or toddler usually none. Only the owner ever moves their own
item, so never give a toddler a laptop or make the whole family share one
phone.

bedroom_index: which bedroom this occupant sleeps in, as a 1-based index. A
couple shares one index; each child gets their own. Two parents and two kids
means the parents are both index 1 and the kids are 2 and 3.

Respond only with valid JSON matching the provided schema. No commentary.
""")

DAY_PLAN = PromptTemplate("day_plan", """\
You are planning ONE day for a household. You are given the day type
(weekday / weekend / flex) and every member's profile. Think through what
this specific household's day looks like, then write a short scenario
(1-2 sentences) for EACH member.

Hard constraints:
- It is ONE coherent day: everyone lives the same calendar day. Household-
  scale events (a dinner party, a power outage, bad weather, a visitor) must
  appear in EVERY member's scenario if they appear in any.
- Respect age and role. Toddlers do not meditate, work, run errands alone,
  or supervise anything. School-age children and teens are at school on a
  weekday unless the day itself justifies staying home (illness, holiday) —
  and then say so. Working adults work on weekdays (at home or away, per
  their habits).
- Ground each scenario in the member's own profile (habits, role, age) —
  an artistic teen's Saturday differs from a gardening retiree's.
- Vary energy and texture across members; not everyone has an eventful day.
  "Ordinary day, follows their usual routine" is a fine scenario.

Respond with JSON only:
{"household_context": "<one sentence: the shared shape of this day>",
 "occupants": [{"name": "<name>", "scenario": "<1-2 sentences>"}, ...]}
Include every member exactly once. No commentary outside the JSON.
""")

ACTIVITY = PromptTemplate("activity", """\
You are a household activity scheduler. Given a persona and a day context,
produce a realistic day's activity trace for one occupant with continuous
(non-hour-snapped) times. Let the day context meaningfully shape the schedule —
different contexts should produce noticeably different traces. Use the
occupant's habits (given below) to make this specific day theirs, not a
generic template shared with other household members.

Activities must be contiguous and non-overlapping for the occupant, and
together must span the occupant's full day from typical_wake to typical_sleep
(wrapping past midnight if typical_sleep > 24).

Location must be exactly one of: {locations}.
'away' means genuinely outside the house. Whether it applies depends on the
occupant's age_band and the Day type given below:
  - "weekday": working adults are likely away at work. older_child and teen are away at school for a substantial
    block unless the day context itself overrides it (sick, holiday).
    young_child is often at school too (grade school); toddler may be home
    or at daycare — use judgement, it's not automatic either way. adult
    often still has a commute, errand, or offsite block even on a nominally
    "work from home" day. senior is often home (retired) unless habits say
    otherwise.
  - "weekend": no school for any age_band. Working adults may be in their office, or may be around the house. Occupants may or may not leave,
    per their habits and the day context. for example, people may go out for leisure or errands and be away.
A full day with every single activity indoors at home is the exception for a
school-age (older_child/teen) occupant on a weekday, not the default — if you
keep one home, the day context must justify it (illness, holiday), not just
default to it.

Repeated behavior should come from the day context, not habit alone: if the
day context implies frequent recurrence (e.g. "makes hot drinks frequently",
"mostly resting"), repeating that specific activity is correct. Otherwise,
don't reuse the same non-routine activity label more than twice — vary the
label even when the general behavior recurs (tidying, gardening,
arts_and_crafts, reorganizing are all different from "decorating" repeated
four times for no stated reason). Prefer plain, ordinary activity labels
(cooking, cleaning, breakfast) over dramatized ones (e.g.
"cooking_special_dish") unless the day context specifically motivates
something out of the ordinary.

Respond only with valid JSON matching the provided schema. No commentary.
""".format(locations=", ".join(_ACTIVITY_LOCATIONS)))

DISPLACEMENT = PromptTemplate("displacement", """\
You are a household object-placement modeller. Given an activity and a scene
inventory, propose CANDIDATE objects the occupant might move and where to.
You are a proposer, not a filter — a separate downstream stage grounds,
scores, and selects the final subset, so proposing more candidates than
would realistically all happen at once is fine, and preferred, over a short
"safe" list.

Rules:
- Only propose object categories that appear in the inventory.
- target_anchor entries name SPECIFIC real furniture instances in the format
  room.category_N (e.g. kitchen.counter_2 = the second counter in the
  kitchen, bedroom_1.bed_1 = the bed in the first bedroom). These are the
  ONLY real placement targets in the occupant's current room — there are no
  other surfaces, and nothing outside this list exists for this activity.
- Surface relations (on, on_top, inside, within) may only target anchors
  offered on the surface list — each has a real, physically usable surface.
  Proximity relations (near, next_to) may target any listed anchor: placing
  an object NEXT TO a fridge or tv is fine even though nothing can be placed
  ON them.
- Chairs and stools are FLOOR objects: they get pushed in, pulled out, or
  moved next to furniture — never lifted onto a table/counter/bed. For
  chair/stool, only use proximity relations (near, next_to); a chair/stool
  surface proposal will be discarded.
- If no listed anchor is an appropriate destination for an object, choose
  "none" (abstain) for that proposal rather than forcing a bad fit. An
  abstained proposal is dropped, not penalised — a wrong surface is worse
  than no proposal.
- If target_anchor "put_away" is offered, it means the occupant PUTS A CARRIED
  ITEM AWAY — a phone/keys/wallet/laptop that is currently out goes back into a
  bag, pocket, or drawer and disappears from view (we don't track where). Use
  it only for a carried item the current-state block shows is out, and only
  when the activity implies putting it away — leaving the house, bedtime,
  tidying up. Do not "put away" something that isn't out.
- The occupant is physically in one room for this whole activity (given
  below, when known). Every target_anchor offered to you already belongs to
  that room — you cannot place an object somewhere the occupant isn't. The
  object being moved does not have to already be in that room (it can be
  something they're carrying in from elsewhere); only the destination is
  room-constrained.
- Vary target_anchor across candidates when multiple objects could plausibly
  move — do not default every object to the same nearest surface. A
  breakfast candidate pool can spread across the table and both counters,
  not the same table three times over.
- A candidate must still be physically sensible for the activity (a cup can
  move to the table during breakfast; a sofa does not move during
  breakfast). Behavioral realism — how *likely* the move is, not just
  whether it's conceivable — is judged downstream; do not self-censor a
  plausible-but-less-common move here.
- For each proposal, write the `reason` FIRST: reason about what this
  activity, done by this person in this room, plausibly implies for object
  movement — given who they are, what they're doing, and where things
  currently are. Only then fill object_category/target_relationship/
  target_anchor to match that reasoning. The reasoning drives the choice,
  never rationalizes a choice already made.
- If your reason mentions where an object currently is, take it from the
  "Current object state" block — never guess. If the block doesn't list it,
  don't claim an origin at all.
- Chairs and stools slide on the floor: pull one out to sit somewhere
  (next_to), and tuck it back under the table/counter/desk when done
  (tucked_under) — tidying up, clearing space, or finishing a meal are
  natural moments to tuck chairs back in.

Respond only with valid JSON matching the provided schema. No commentary.
""")

REALISM_ASIS = PromptTemplate("realism_asis", """\
You are a behavioral-plausibility judge for household object placements.
Grounding has already confirmed each candidate below is physically
placeable; your job is a separate judgment — how behaviorally plausible is
it, given the activity, occupant, and household.

For EACH candidate, independently assign a realism score in [0, 1]: how
plausible is it that this specific object would end up at this location
because of this activity, for this occupant, in this household.

Score every candidate strictly on its own merits. Do not compare candidates
to each other or rank them, and do not let pool size influence a score — the
same candidate in a context should score the same whether the pool has 2
entries or 10.

Household tidiness scales plausible clutter, it does not gate realism: a
low-tidiness household plausibly leaves more objects out of place, so a
borderline "left behind" placement should score higher there than in a tidy
household — but a placement with no behavioral connection to the activity
should still score low regardless of tidiness.

A placement can be physically valid but behaviorally implausible — e.g. a
laptop on the dining table during dinner is placeable but out of place for
that activity, and should score low even though grounding accepted it.

Respond only with valid JSON matching the provided schema. No commentary.
""")

REALISM_STRICT = PromptTemplate("realism_strict", """\
You are a strict behavioral-plausibility judge for household object
placements. Grounding has already confirmed each candidate below is
physically placeable; your job is to decide how believably a real person
doing this activity would produce this exact placement. The proposal pool
is deliberately over-generated and varied — most candidates are NOT
supposed to pass. Be selective.

For EACH candidate, independently assign a realism score in [0, 1]:
  - 0.8–1.0: the placement is exactly what a typical person doing this
    activity would do; you would not notice it in a photo of a real home.
  - 0.5–0.7: plausible but noticeably less common; needs the household
    context (tidiness, occupant) to make sense.
  - 0.2–0.4: conceivable but contrived — you'd need a story to explain it.
  - 0.0–0.1: no believable behavioral connection to the activity, or
    physically-technically-possible-but-absurd (electronics in the fridge,
    a candle on a bed, food items in the bathroom).

Actively penalize: placements with no behavioral connection to THIS
activity; odd object-surface pairings a person wouldn't choose (books in a
bathtub, a vase on a toilet); the same object repeatedly shuffled to
arbitrary surfaces; safety-implausible placements. When in doubt, score
LOWER — a missed good candidate costs little in an over-generated pool, a
bad selection pollutes the dataset.

Be wary of justifications that don't make logical sense. Think about how the 
human would use the object, and if they would bring it with them on their activity.
Common reasons a placement wouldn't make sense:
- The object would be brought with the human and not left out. eg. a phone brought out on a jog
- There is a more convenient instance of the same or similar object at the destination. eg. a chair 
  for this human is already at the table, so a second chair from another room is not brought there.
- The justification text implies a different activity than the current one. eg. someone organizing 
  the house after dinner would not be organizing DURING dinner time
- The object is not needed for the activity despite the proposed justification. eg. a bowl is not 
  used for holding keys and small items
- The object is "for easy access" or "for convenience" in the justification. Be wary and think about whether the human would
  actually need easy access to the object during this activity.



Some candidates carry a `move history` note — how many times that object has
already moved today and its path. Repeated relocation of the SAME object needs
cumulative justification: each additional move of an object that does not
normally travel (furniture, plants, decor, dishware that lives in a cabinet)
is less believable than the last, so score a 4th/5th/7th such move
progressively lower. Objects a person naturally carries all day (phone, keys,
wallet, laptop, a cup in active use) are exempt — their repeated movement is
normal, not suspicious.

Score every candidate strictly on its own merits. Do not compare candidates
to each other or rank them, and do not let pool size influence a score.

Household tidiness scales plausible clutter, it does not gate realism: a
low-tidiness household plausibly leaves more objects out of place — but a
placement with no behavioral connection to the activity should still score
low regardless of tidiness.

Respond only with valid JSON matching the provided schema. No commentary.
""")

CONFLICT_VERIFY = PromptTemplate("conflict_verify", """\
You are reviewing activity traces for a multi-occupant household for
scheduling conflicts.

A conflict is:
  - Two occupants using the same scarce object simultaneously
    (e.g. both occupants eating at the single dining table at the same time is
     fine if there are 2+ seats; both using the single computer simultaneously
     is a conflict).
  - An occupant marked as 'away' also doing an indoor activity at the same time.
  - Any logically contradictory joint state.

For each conflict found, return the occupant name, the conflicting time range,
and a brief description. If no conflicts, return an empty list.

Respond only with valid JSON.
""")

def realism_strict_fewshot(exemplar_block: str) -> PromptTemplate:
    """The strict judge template augmented with a few-shot exemplar block
    (Phase 2.2). A new registry entry whose version hashes the strict text
    PLUS the exemplars, so different exemplar sets get different tags and the
    cache splits cleanly. Byte-identical strict wording; the examples are
    appended, not edited in."""
    return PromptTemplate(
        "realism_strict_fewshot",
        REALISM_STRICT.text + "\n" + exemplar_block + "\n",
    )


CLUTTER = PromptTemplate("clutter", """\
You are a household clutter modeller. Given a household type and its real
furniture layout (rooms + furniture categories actually present in this
scene), propose which small "static clutter" objects live in this home and
where each one lives — its persistent home, generated once before the day
starts, not a mid-day event.

These are NOT carried items (phone, keys, laptop, wallet) — do not propose
those. Static clutter is the small things that live somewhere and stay there
most of the time: a fruit bowl on the kitchen counter, books on a shelf, a candle on
the dining table, a vase in the living room. Only propose objects from the
given category list, and only onto anchors actually offered in the schema.

target_anchor entries name SPECIFIC real furniture instances in the format
room.category_N (e.g. kitchen.counter_2 = the second counter in the kitchen).
These are the only real surfaces in this home. Surface relations (on, on_top,
inside, within) may only use anchors from the surface list; proximity
relations (near, next_to) may use any listed anchor. If nothing listed fits
an object, choose "none" (abstain) for it rather than forcing a bad fit.

Propose realistic quantities for a home of this type — a handful of each
category, not one per room and not every category maxed out. Vary
target_anchor across proposals of the same category (e.g. three "book"
proposals on two different shelves) so the result
reads as a lived-in home, not a uniform stack.

Respond only with valid JSON matching the provided schema. No commentary.
""")
