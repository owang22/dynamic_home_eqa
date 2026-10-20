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
BUILDER_VERSION = "b6"  # b3 -> b4: state block carries placement relations
                        # ("tucked under kitchen.counter_1"), concealment
                        # branch/vocabulary (inside closed storage = put-away),
                        # and grammar maxLength on reasons — assembly changes.
                        # b1 -> b2: seat-in-room vocabulary gate (chair/stool
                        # removed from a window's movable categories unless an
                        # instance is currently in the acting room) changes the
                        # assembled displacement prompt without touching any
                        # template text — bumped so pre-gate cached responses
                        # (which still propose cross-room chair fetches) can
                        # never replay against post-gate code.
                        # b2 -> b3: instance-explicit seats (seat ids replace
                        # the bare category in the schema enum + state block
                        # lists per-seat slots), candidate_line drops the
                        # move-history note and shows the instance id, and
                        # the judge schema gains a per-candidate reason —
                        # all Python-side assembly changes.

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
In addition, take into account the day of the week.

owned_items: the carried personal items THIS occupant owns and moves around
(phone/wallet/keys/laptop/backpack/sunglasses/headphones/medicine). Assign
per person and age-appropriately, not per household — a working adult
usually phone/wallet/keys/laptop (sunglasses if they drive or go out), a
teenager phone/laptop plus headphones and a school backpack, a school-age
child a backpack (maybe a phone), a senior phone/wallet/keys plus daily
medicine, a toddler none. Only the owner ever moves their own item, so
never give a toddler a laptop or make the whole family share one phone.

bedroom_index: which bedroom this occupant sleeps in, as a 1-based index. A
couple shares one index; each child gets their own. Two parents and two kids
means the parents are both index 1 and the kids are 2 and 3.

Respond only with valid JSON matching the provided schema. No commentary.
""")

# Postmortem note (stage1c): earlier versions of this prompt asked the model
# to invent each day from scratch and to self-police variety ("most days
# ordinary", "don't repeat recent themes"). That made both repetition AND
# variety properties of model temperament: it mode-collapsed onto one motif
# when primed, produced near-verbatim days when de-primed, and eventually
# resolved the repetition/variety tension by rewriting an occupant's
# occupation mid-episode. The planner is now a RENDERER: the routine profile
# (generated once per household, validated against the persona) says what
# repeats; the seeded event calendar says what varies; the model improvises
# neither.
DAY_PLAN = PromptTemplate("day_plan", """\
You are rendering ONE day for a household. You are given the day type, each
member's profile, each member's ROUTINE PROFILE (their stable weekly
pattern — authoritative ground truth), and today's scheduled event (usually
none). Write a short scenario (1-2 sentences) for EACH member.

Hard constraints:
- Follow each member's routine profile for this day type exactly. Do NOT
  invent new occupations, schedules, or lifestyles, and do not contradict
  the profile's wake/sleep pattern. Vary only the small, concrete details
  of how the routine plays out today (which room, which chore, which meal).
- If a scheduled event is given, weave it coherently into EVERY member's
  scenario. If none is given, this is an ordinary day: no parties, guests,
  outages, storms, illnesses, or trips.
- Respect age and role. Toddlers do not meditate, work, run errands alone,
  or supervise anything. School-age children and teens are at school on a
  weekday unless the scheduled event says otherwise.
- Ground each scenario in the member's signature habits where natural —
  those habits are what move household objects.

Respond with JSON only:
{"household_context": "<one sentence: the shared shape of this day>",
 "occupants": [{"name": "<name>", "scenario": "<1-2 sentences>"}, ...]}
Include every member exactly once. No commentary outside the JSON.
""")

ROUTINE_PROFILE = PromptTemplate("routine_profile", """\
You are defining the STABLE weekly routine of each household member — the
pattern that repeats week after week. This profile is generated ONCE per
household and then governs every generated day, so it must be strictly
faithful to each member's given profile: same occupation, same wake/sleep
tendencies, same habits. Never invent an occupation or lifestyle that the
profile does not state.

For each member output:
- occupation: their occupation/role exactly as the profile implies (a
  school-age child's occupation is "student"; a toddler's is "toddler").
- weekday_routine: 2-3 sentences describing their typical weekday, from
  wake to sleep, consistent with the profile's wake/sleep times.
- weekend_routine: 2-3 sentences for a typical weekend day.
- signature_habits: 2-4 short recurring habits involving household objects,
  drawn from the profile (e.g. "leaves the work laptop on the dining
  table overnight").

Respond with JSON only:
{"occupants": [{"name": "...", "occupation": "...", "weekday_routine": "...",
                "weekend_routine": "...", "signature_habits": ["...", ...]}]}
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

If the request includes "Coordination notes" — known clashes with other
household members' plans (both wanting the same space, object, or time slot)
— treat them as constraints: shift, shorten, or re-order this occupant's
activities so the clash doesn't happen, in a way that stays natural for who
they are. Do not simply drop the activity; people adapt (eat a little later,
use another room, wait their turn), they rarely abandon the plan outright.

Respond only with valid JSON matching the provided schema. No commentary.
""".format(locations=", ".join(_ACTIVITY_LOCATIONS)))

DISPLACEMENT = PromptTemplate("displacement", """\
You are a household object-placement modeller. Given an activity and a scene
inventory, propose CANDIDATE objects the occupant might move and where to.

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
- Seats and other floor-standing objects (chairs, stools, laundry baskets)
  are offered as SPECIFIC instances (stool_1, stool_2, ...), each listed in
  the current-state block with where it is right now. Propose the instance
  id as the object_category. Pick one that makes sense to move: a seat
  already pulled out and in use by another person at their spot stays put —
  take a different instance. Moving them BACK is ordinary life: tucking
  chairs back under the table after a meal, or returning a pulled-out
  stool, is exactly what a tidying/cleaning/after-meal activity does,
  including several seats in one activity.
- Small everyday items (books, bowls, cups, drinkware, bottles) are ABUNDANT:
  homes keep more of them in cabinets and shelves than are visible. Bringing
  a fresh one out for an activity is normal even when one of the same kind is
  already sitting out — people don't eat from the used bowl on the table.
  Prefer bringing a fresh one to re-moving one someone else set down. This
  does NOT apply to carried personal items (phone, keys, wallet, laptop —
  exactly one each, tied to their owner) or to furniture and seats (a home
  does not produce new chairs).
- If no listed anchor is an appropriate destination for an object, choose
  "none" (abstain) for that proposal rather than forcing a bad fit. An
  abstained proposal is dropped, not penalised — a wrong surface is worse
  than no proposal.
- Putting something INSIDE closed storage furniture (a cabinet, wardrobe,
  chest of drawers, fridge, dishwasher, washer/dryer) uses relation "inside"
  with that anchor, and means the object is STORED OUT OF SIGHT — it
  disappears from view like a put-away, it does not sit visibly on or
  beside the furniture. Use it for tidying items into cupboards, food into
  the fridge, dishes into the dishwasher.
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
  breakfast).
- For each proposal, write the `reason` FIRST: reason about what this
  activity, done by this person in this room, plausibly implies for object
  movement — given who they are, what they're doing, and where things
  currently are. Only then fill object_category/target_relationship/
  target_anchor to match that reasoning. The reasoning drives the choice,
  never rationalizes a choice already made. Keep the reason to AT MOST two
  sentences — one for why this object moves, one for where it ends up.
- If your reason mentions where an object currently is, take it from the
  "Current object state" block — never guess. If the block doesn't list it,
  don't claim an origin at all.
- Chairs and stools slide on the floor: pull one out to sit somewhere
  (next_to), and tuck it back under the table/counter/desk when done
  (tucked_under) — tidying up, clearing space, or finishing a meal are
  natural moments to tuck chairs back in.

Respond only with valid JSON matching the provided schema. No commentary.
""")

#NOT USED 
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
bathtub, a vase on a toilet); safety-implausible placements. When in doubt,
score LOWER — a missed good candidate costs little in an over-generated
pool, a bad selection pollutes the dataset.

For EACH candidate, write its `reason` BEFORE its score: weigh the evidence
for and against this exact placement — the activity, the person, the time,
the current object state — and state the deciding factor. AT MOST two
sentences. Then give a score consistent with that reasoning; the reasoning
decides the score, never justifies one already picked.

Before scoring, settle these consistency questions. A "yes" to ANY of them
is a hard failure: the reason IS INCOHERENT WITH THE MOVE, so the score
MUST be 0.1 or lower regardless of how sensible the placement would be on
its own — an incoherent justification is exactly the noise this pool
exists to filter, and a plausible-sounding placement with a contradictory
reason is worse than an implausible one, not better.
- FRESH vs. EXISTING mismatch — but FIRST apply the abundance rule above:
  for everyday abundant items (dishes, plates, bowls, cups, mugs, glasses,
  bottles, books, towels, toys), bringing out a FRESH one is CORRECT and
  normal even when another of the same kind is already sitting out — a home
  has many, and people take a clean one. DO NOT flag that as a
  contradiction; it is the expected behavior. This check fires only for
  UNIQUE or PERSONAL items that cannot have a fresh duplicate — a specific
  person's wallet/phone/keys/laptop/backpack, or one specific chair/stool
  named in the state: for those, a "bring a fresh one" justification is
  nonsense (there is only the one), and so is a reason that names moving a
  specific existing item the state shows is NOT out. Also flag any reason
  that internally contradicts itself (claims to bring a fresh item AND to
  relocate the specific used one in the same breath).
- PUT-AWAY mismatch: does the justification describe putting something
  AWAY, tidying it into a cupboard/drawer/cabinet, or clearing it out of
  sight, while the candidate is a VISIBLE placement (on_top / next_to a
  surface)? A real putting-away is an "inside <storage>" concealment or a
  put_away — not an object left sitting on a bench or table.
- OBJECT/DESTINATION mismatch: does the justification name a different
  object, or a different surface/room, than the candidate's actual
  object_category and target_anchor?
Only after all three are clear (no contradiction) do you score the
placement on its own behavioral merits using the bands above.

Be wary of justifications that don't make logical sense. Think about how the 
human would use the object, and if they would bring it with them on their activity.
Common reasons a placement wouldn't make sense:
- The justification references a different object or location than the actual motion being proposed
  eg. a cup is proposed to be moved to the table, but the justification references a phone on the table
- The object would be brought with the human and not left out. eg. a phone brought out on a jog
- A seat or furniture piece is fetched when a more convenient instance is already at the
  destination. eg. a chair for this human is already at the table, so a second chair from another
  room is not brought there. (This is about seats/furniture — for abundant small items like bowls
  and cups, a fresh one coming out alongside an existing one is normal; see below.)
- The justification text implies a different activity than the current one. eg. someone organizing 
  the house after dinner would not be organizing DURING dinner time
- The object is not needed for the activity despite the proposed justification. eg. a bowl is not 
  used for holding keys and small items
- The object is "for easy access" or "for convenience" in the justification. Be wary and think about whether the human would
  actually need easy access to the object during this activity.


Two placement patterns are ordinary life, not suspicious: (1) small everyday
items (books, bowls, cups, drinkware, bottles) are abundant — a home holds
more in cabinets than are visible, so a fresh one coming out is normal even
when one of the same kind is already sitting out; (2) seats moving back —
chairs tucked back under the table after a meal, a pulled-out stool returned
— are exactly what tidying and after-meal activities do, even several seats
within one activity. Judge each such move on whether THIS activity by THIS
person implies it, not on how much movement the day has already seen.

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
     fine if there are 2+ seats; both using the same phone simultaneously
     is a conflict).
  - An occupant marked as 'away' or otherwise outdoors also doing an indoor activity at the same time.
  - Any other logically contradictory joint state.

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


ASSET_BINDING = PromptTemplate("asset_binding", """\
You are assigning REAL 3D render assets to a household's personal carried
items. Each item below belongs to one specific person and lists candidate
assets as "uid: tags" — the tags are a human reviewer's appearance/style
descriptors (color, style, who it suits).

Pick the ONE candidate per item that best fits its owner's age, role, and
habits: a teen gets the gaming headset, not the classic office pair; a
retiree the sensible black sunglasses, not the hippie circles; a school
kid the cute frog backpack. Two people MAY receive the same style when
nothing distinguishes them, but prefer visibly different assets for
different people so items are tellable apart in a photo of the home.
A candidate tagged as odd/rare (e.g. "only rarely use") should be picked
only when it genuinely fits the owner better than everything else.

Respond only with valid JSON matching the provided schema — one binding
per item, using each item's own candidate uids. No commentary.
""")

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

A real home contains MOST of these categories somewhere — aim for broad,
lived-in coverage: typically 10–18 objects total spanning many different
categories, weighted by what this household type plausibly owns (a family
with kids has toys out; a retiree a teapot and newspaper; everyone has
plates and towels). Do not max out any single category, and skip a category
only when it genuinely doesn't fit the household. Vary target_anchor across
proposals of the same category (e.g. three "book" proposals on two
different shelves) so the result reads as a lived-in home, not a uniform
stack.

Keep each proposal's `reason` to AT MOST two sentences — why this object
lives in this home, and why on this anchor.

Respond only with valid JSON matching the provided schema. No commentary.
""")
