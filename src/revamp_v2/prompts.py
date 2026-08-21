"""Prompt registry + guided-JSON schemas for the revamp_v2 pipeline.

Every LLM-facing string in revamp_v2 lives here, nothing inline — the
PromptTemplate pattern is ported from
src/dynamic_home_eqa/generation/prompt_registry.py: each template carries a
content-derived version (first 8 hex of sha256), folded into the cache stage
tag via .tag(), so cached responses can never silently survive a wording
change. BUILDER_VERSION covers the user-message assembly done by the
builder functions below — bump it by hand whenever that assembly changes.

The pipeline's LLM surface, one template per sequential call — each call
conditioned on the accepted output of the previous, each with the
tightest grammar that output allows:
  PERSONA        L1 — ported essentially verbatim from
                 profiles/revamp_v1/generation_prompt.md; only the output
                 transport changed (guided JSON instead of pasted YAML).
  CALENDAR       L2a — persona -> the weekly schedule (sleep_schedule,
                 weekly_blocks, activity extras). No object content.
  OBJECT_RULES   L2b — schedule -> after-only object dists. The rule
                 activity enum is PINNED to what the calendar actually
                 scheduled, so an orphaned rule is unwritable.
  SPECIAL_EVENTS L2c — schedule -> 4-8 dated exceptions; `drop` pinned
                 the same way, retiring vacuous/unknown drops.
  BINDING        story arms — adds rules for a story's unbound at-home
                 activities, same rule grammar as L2b.
  LEAK_AUDIT     validation check 4 — household-type classification from
                 object/receptacle ids alone; chance = 1/len(types).
The L2 prompts deliberately contain NO example content (objects, rooms,
story beats) that could prime uniform outputs across households — the
legacy DAY_PLAN storm-priming bug is the cautionary case.
"""
from __future__ import annotations

import hashlib
import json

BUILDER_VERSION = "rv2-b5"   # b3 -> b4: `cites` is required and
                             # declared FIRST everywhere (property
                             # order is generation order, so a
                             # justification written last is
                             # post-hoc), and a static object is
                             # declared `motion: rarely_moved`
                             # rather than left as an empty list.
                             # b1 -> b2: the program user prompt now
                             # carries the day-index -> weekday table.
                             # b2 -> b3: control.yaml's household types
                             # were rebalanced towards ordinary homes, and
                             # the persona prompt lists the OTHER types in
                             # the set for contrast — so the assembled
                             # prompt changed for every slot, including the
                             # ones whose own type did not. Without this
                             # bump the seed is unchanged and every cached
                             # persona replays under the old set.

JITTER_CLASS_NAMES = ["external", "routine", "flexible", "loose"]

# A CLOSED activity vocabulary, drawn on by weekly_blocks, sleep_schedule,
# the per-activity extras AND every object rule. Activity names are the one
# cross-reference the schema could not otherwise constrain — they are free
# strings written in two distant sections — and the generator duly wrote
# rules for `snack` and `play` in a household whose blocks were `dinner`
# and `homework`, orphaning every rule and leaving 26 of 30 objects inert.
# Drawing both sections from one enum makes a dangling reference
# unwritable. Household character lives in the times, the jitter, the
# probabilities and the object rules — not in the activity's name — the
# same reasoning the closed object vocabulary already applies.
ACTIVITY_VOCAB = [
    # sleep and rest
    "night_sleep", "day_sleep", "nap", "lie_down", "bedtime_routine",
    "wake_up",
    # meals and kitchen
    "breakfast", "lunch", "dinner", "snack", "meal_prep", "batch_cooking",
    "coffee", "wash_dishes", "put_away_dishes",
    # out of the house
    "work_away", "school",
    "errands", "groceries", "appointment", "night_out", "walk", "gym",
    "traveling",
    # work and study at home
    "work_home", "homework", "study", "video_call",
    # leisure at home
    "relax", "watch_tv", "gaming", "reading", "hobby", "music",
    "play_with_kids", "socialise_home", "phone_time",
    # chores and care
    "tidy_up", "deep_clean", "laundry", "take_out_bins", "pet_care",
    "take_medication", "shower", "bath", "get_ready",
]
DAY_ABBREV = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]  # day 0 = Monday
TIME_PATTERN = r"^([01]?\d|2[0-3]):[0-5]\d(\+1)?$"
NAME_PATTERN = r"^[a-z][a-z0-9_]{2,39}$"


class PromptTemplate:
    """A named system-prompt template with a content-derived version."""

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text
        self.version = hashlib.sha256(text.encode()).hexdigest()[:8]

    def tag(self, base: str, *, builder: bool = False,
            schema: dict | None = None) -> str:
        """Cache stage tag with every input that shapes the response folded
        in: the template text (self.version), the Python-side user-prompt
        assembly (BUILDER_VERSION), and the guided-JSON schema itself.

        The schema hash is the piece the legacy registry lacked: seeds
        derive from this tag, so without it a tightened schema would keep
        replaying responses sampled under the older, looser contract."""
        t = f"{base}_p{self.version}"
        if builder:
            t += f"_{BUILDER_VERSION}"
        if schema is not None:
            digest = hashlib.sha256(
                json.dumps(schema, sort_keys=True).encode()).hexdigest()[:8]
            t += f"_s{digest}"
        return t


PERSONA = PromptTemplate("persona_v2", """\
You are writing profiles of fictional households for a research simulation.
The simulation will later animate each household: objects will move around
the home over days and weeks, driven by what the residents do. Right now we
are only writing WHO lives in each home and WHAT objects they own. Daily
schedules with clock times come in a later step — do not write any times of
day or hour-by-hour routines.

Each household must be clearly different from every other household in the
set (the other households' types are listed in the request) — different
personalities, ages, living situations, and habits, not just different
names.

For each household you are told its TYPE and the number of residents.
Keep the type and headcount you are given; do not change them. Invent a
specific, believable household of that type.

Fields to produce (returned as JSON matching the provided schema; the
meaning of each field is unchanged from the YAML original):

household_id: as given
household_type: as given, copy exactly
residents:
  - id: resident_1
    name: ...
    age: ...
    occupation: ...        # or "student", "retired", "stay-at-home parent"
    personality: ...       # 2-3 traits that affect how they treat objects
                           # (e.g. tidy, forgetful, always in a hurry)
    habits:                # 5-8 concrete habits about how they use and
                           # leave objects around the home. If appropriate,
                           # these habits can
                           # involve another resident. Examples:
                           # - "reads in bed, leaves the book on the
                           #    nightstand"
                           # - "borrows resident_2's charger from the desk
                           #    and rarely returns it"
                           # - "clears everyone's plates and does the dishes after dinner"
relationships: ...         # 2-3 sentences: who these people are to each
                           # other, and how they divide or share chores,
                           # spaces, and belongings. Include at least one
                           # point of friction or coordination (e.g. which people
                           # do which dishes, who loses the remote, whose stuff
                           # spreads into shared spaces).
home_layout_notes: ...     # 2-3 sentences: rooms and surfaces each person
                           # uses most, and which spaces are shared, eg. reason about
                           # people who are likely to share a bedroom.
object_inventory:
  - id: mug_marie          # indexed ids: bowl_1, bowl_2, laptop_sam, laptop_mia. 
                           # Note shared (interchangeable) objects have number index, but personal
                           # objects carry the id of their owner. The id
                           # MUST begin with its class ("mug_marie", not "marie's_mug")
    class: mug             # pick classes from the vocabulary below
    owner: resident_1      # or "shared: [resident_1, resident_2]", like a list of residents who often use it
    role: ...              # one short phrase: what activities this object is often used for, 
                           # and where it tends to be left when not in use.
                           # this household. For
                           # shared objects, say who moves it and why.
daily_life_summary: ...    # 3-4 sentences describing a typical day in
                           # plain words, still without clock times.
                           # Mention how the residents' days overlap or
                           # miss each other (who is home when others are
                           # out, who crosses paths where).
quirks: ...                # 0-2 ways this household differs from the
                           # stereotype of its type

Object vocabulary (choose from these; do not invent new classes):
[mug, bowl, plate, laptop, phone, tablet, keys, wallet, book,
water_bottle, remote, charger, backpack, jacket, headphones, glasses,
notebook, pen, medication_bottle, toy, blanket, towel, gaming_controller,
dog_leash, lunchbox, umbrella, laundry_basket, vacuum_cleaner, pot, pan,
suitcase, hairbrush, makeup_kit, watering_can, yoga_mat]

Inventory rules:
- Not every household owns every class of object, the residents own what makes sense for their lifestyle.
  Aim for 15-20 objects for a solo resident matching with their persona and add roughly 4-6 per
  additional resident that would make sense as personal belongings aligning with their personas.
- Objects have events where someone picks it up for use in an activity, puts it down afterwards, or carries it somewhere. A later step
  has to say what moves each object and where. Think about what each object is for, and how it is used in the household's daily life.
- Object counts should match household size (a family of three owns more
  bowls and backpacks than a person living alone). Per-person items like
  phones, keys, and wallets should exist per resident, and for each one
  the `role` must say HOW IT TRAVELS: an item the person takes out of the
  house moves WITH them. Be conscious that people must have a good reason to
  move another resident's per-person object (eg. its plausible to ocassionally bring
  someone's phone to them, but unlikely to take someone else's glasses out on a walk).
  People who leave the house usually take their phone and
  keys with them unless the persona says otherwise (eg. they are extremely forgetful).
  Other objects tend to stay in particular spots in the home, or have a few locations that make sense
  to inhabit based off of activities (eg. a plate is stored in a dishwasher, drying rack, or cupboard,
  but some people might leave plates in the sink overnight). The `role` field should describe how the object is used and where it tends to be left.
- A household that eats at home OWNS THE DISHES IT EATS FROM: bowls,
  plates, a pot or a pan, whatever this kitchen actually uses. These are
  the best objects in the whole inventory — their cycle is daily and
  multi-stop (cupboard -> table -> sink -> drying rack -> cupboard) and
  it differs per person: one household washes up immediately, another
  leaves plates in the sink overnight, a third eats off the same bowl
  every morning. Do not skip them because they are ordinary; ordinary is
  what moves.
- Suggestive objects are allowed (medication_bottle, toy, dog_leash), but
  write the "role" field so the object's meaning comes from how it is
  used, not from the fact that it exists. The same object class could
  mean different things in different households.
- Shared objects are encouraged in multi-person homes; their "role" should
  name which residents move them.

Respond only with valid JSON matching the provided schema. No commentary.
""")

CALENDAR = PromptTemplate("calendar_program", """\
You are compiling the CALENDAR half of a household routine program: the
complete machine-readable weekly schedule of one household, derived
strictly from its persona (in the request). A deterministic simulator —
not you — realizes it; a SECOND step will author what the schedule does
to the household's objects, and a THIRD adds the special events — do not
write either here.

Use ONLY the resident ids, receptacle ids and ACTIVITY NAMES offered by
the schema. Pick the closest name from the closed list rather than
inventing one — a household's character comes from its times, its
probabilities and its objects, not from what its activities are called.
Every block must encode something the persona states or clearly implies.
`cites` comes FIRST in every block, written BEFORE you choose a time or a
probability: name the persona phrase that licenses what you are about to
write, then write it. Keep it to ONE short clause, ten words or so.
Do not invent occupations, rooms, or habits the persona does not support.

sleep_schedule — one entry per resident, before anything else: where and
when that person sleeps, every night (or every day, for a night worker).
Everyone in the household gets exactly one, including children. These are
weekly blocks like any other — days, start, end, at, jitter — they simply
live in their own section because everybody sleeps. Nobody skips it, so
there is no skip_p here; an optional afternoon nap belongs in
weekly_blocks below with `sleep: true`.

weekly_blocks — the rest of each resident's stable week, no gaps in
intent: when a block ends and the next has not started, the resident
lingers where they were. `start`/`end` are "HH:MM" clock times; append
"+1" when the moment falls past midnight of the block's day (a night
worker's return home belongs to the evening's sequence). `end` must be
LATER than `start` on that same "+1"-extended timeline: a block starting
"22:00" and ending half past seven the next morning ends "07:30+1", and
one that already starts "07:45+1" cannot end "12:00" — it ends
"12:00+1". `at` is the
receptacle where the resident is during the block, or ELSEWHERE when out
of the house. 
- `sleep: true` marks an OPTIONAL nap here (the real sleep is above). Set
  it only on a block where the person is genuinely asleep.
- Each activity name appears ONCE in `activities`, however many blocks
  use it.
- Decide how variable different Recurring activities are (skip_p: 0, tight jitter)
  or (skip_p 0.1-0.4, looser jitter). Real people skip chores
  and optional meals, and may put off other activities like laundry or gaming. 
  Unless otherwise mentioned, a person won't skip work or sleep. 
- In contrast to Recurring activities, there are some Occasional activities that happen
  only when appropriate and are not scheduled for fixed times each week. 
  These activities have high skip rates (0.5-0.9) and should be enumerated as possible activities
  based on the persona/hobbies/interests of the person. For example, someone who likes to 
  game may find time on some nights of the week, maybe more on weekends, but not at regular times.
- Different people may consider the same activity (like tidying) to be Recurring or Occasional, depending on their persona.
- Most households should have a realistic mix of Recurring and Occasional activities, and the program should reflect that.
- jitter classes, calibrated on real free-living homes — external: 10 min
  (contractual: shifts, commutes, school runs, self-imposed strict
  rituals); routine: 30 (body-clock: sleep onset, household meals);
  flexible: 75 (self-paced); loose: 110 (whim).
  A per-resident `jitter_scale` (0.5 tidy-punctual to 2.0
  scattered) derived from persona info determines how punctual each person is overall.

special_events are authored in a SEPARATE later step, after this
calendar exists — do not include any here.

Reason about the household's pattern from its own persona.

Respond only with valid JSON matching the provided schema. No commentary.
""")


OBJECT_RULES = PromptTemplate("object_rules", """\
You are compiling the OBJECT half of a household routine program. The
calendar half already exists — the request shows the full weekly schedule
— and your job is what that schedule DOES to the household's things: the
blocks say where people are, the rules say what happens to their objects.

The activity names offered by the schema are EXACTLY the ones this
household's calendar schedules — nothing else exists to bind to, so a
rule can never name an activity that never happens. Every rule must
encode something the persona states or clearly implies. `cites` comes
FIRST in every rule, written BEFORE you choose a destination or a
probability. Keep it to ONE short clause, ten words or so; the field is
hard-capped, and long early citations crowd out later objects until the
response runs out of room.

object_rules — one entry per inventory object, in the same order: 
the blocks say where people are, the
rules say what that does to their things. Take the objects ONE AT A TIME
and ask what the resident actually does with this thing based on their activities.
Each entry contains everything about that object:
- `home` — where it can often be found, eg. where a tidy-up returns it, from its
  `role`. For a CARRIED item (a phone, keys, a wallet, sometimes headphones, glasses),
  even though it is usually carried with the person, they may still have homes like
  "desk" or "bedside table" where it is set down when not in use.
- `p_misplace` (per day) — when the role describes absent-minded drift:
  the object gets set down at a random moment, on top of whatever its
  rules do. You author only the RATE — the simulator picks the spot from
  wherever the household actually spends its time, so a forgotten thing
  turns up on the counters and tables its owner really passes. CARRIED
  items usually deserve one (0.1-0.4); larger objects are less likely to
  be forgotten. Omit it for objects that do not drift; never write a
  zero probability.
- An object that rarely moves needs no special flag: give the few
  activities that could plausibly touch it a dist with heavy NO_OP mass
  (0.8-0.95) — a vacuum that comes out for deep_clean one time in five,
  a charger that almost never leaves the wall. `rules: []` remains the
  honest answer for an object truly nothing in this life touches.
- Rules are AFTER-only. While an activity is underway, an object it uses
  is simply WITH the resident — at their spot in the home, or out of the
  house with them — and the simulator handles that leg automatically. You
  author only where the object LANDS when the activity ends: each rule
  names the `activity` it fires with, `phase: after`, and a `dist` of 2-5
  outcomes whose probabilities sum to 1. For example, a plate is with
  whoever is eating, wherever they eat; when dinner ends it is possibly
  left in the sink, on the table, or put straight into the drying rack.
  One outcome may be NO_OP: this firing left the object where it already
  was (the activity happened without moving this object). NO_OP mass is
  how "sometimes" and "rarely" are written — a book that usually stays
  put during relax is `NO_OP: 0.8`, not a missing rule. Keep the persona
  in mind: some people put things in many different places, and their
  dists should say so.
- NO TWO OBJECTS share identical rules. Give each object its own
  pattern — different set-down spots, different activities, different
  probabilities — drawn from its role and the persona/activities.
- More items that can be CARRIED include backpacks, jackets, laptops etc. 
  Recognize that these are sometimes carried (eg. AWAY to work), and sometimes 
  may be left in a few reasonable locations when not in use/returning to home. To decide, think about the persona and their activities.
- Every `activity` you name here must be one your sleep_schedule or
  weekly_blocks actually runs — check back against them.
- The reverse also holds: every AT-HOME activity in your weekly_blocks
  must appear in at least one object rule phase.

- Tidying is an ordinary activity: an object that
  someone tidies simply declares tidy_up (or deep_clean) like any other
  activity, with an `after` dist over the places this household actually
  returns it to — a plate may equally end in the cupboard or the drying
  rack, and the dist says so. `home` is where the object starts on day 0
  and its single most natural resting place; the tidy dist is allowed to
  disagree with it. Depending on the persona, tidying can be Recurring or
  Occasional like anything else. Meanwhile, use your judgement, as a child likely won't tidy.

Respond only with valid JSON matching the provided schema. No commentary.
""")

SPECIAL_EVENTS = PromptTemplate("special_events", """\
You are adding the story layer to a simulated household whose routine
program already exists — the full weekly calendar is in the request.
Author 4-8 dated special events: the exceptions that make three weeks a
lived stretch of life instead of a repeating template.

Make the exceptions THIS household's, from its personas: a student stays
out late and is wrecked the next morning; a worker's business trip empties
the home for two days; a sick child keeps a parent home from work; a
friend's dinner invitation simply wipes out cooking that evening. Small
is good; connected-across-days is better.

Each event names its `note` (the beat, in one line), its `day`, and a
`patch` over that day's calendar:
- `drop` removes that day's runs of an activity — the list offers ONLY
  activities this program actually schedules, and a drop only bites on a
  day the activity actually runs (the calendar in the request shows which
  weekdays each block lists).
- `add` inserts one-off blocks (an appointment, the trip out, the sick
  day at home). An added block needs no weekday list — its day is the
  event's own.
- `after_override` (optional, rare) changes where an object lands after
  an activity on that day only.

Together the events should include at least one dropped routine, one
schedule-violating ELSEWHERE addition, and one stretch of several
consecutive patched days (an illness, a visit, a heavy week).

Respond only with valid JSON matching the provided schema. No
commentary.
""")


BINDING = PromptTemplate("story_binding", """\
You are extending a simulated household's object-rule program. The
household's three weeks were authored as a story; the activities listed
in the request appear in that story.

For each object, add `after` rules describing where it ends up when one
of these activities ENDS. While an activity is underway, assume the
object is simply WITH the resident using it; what you author is where it
gets LEFT afterwards — the plate to the sink or the drying rack, the
controller back on the shelf or abandoned on the couch. Each rule names
`cites` FIRST (one short clause grounded in the persona), the `activity`,
`phase: after`, and a `dist` of 2-5 outcomes whose probabilities sum
to 1. One outcome may be NO_OP — this firing left the object where it
was — which is how "sometimes" and "rarely" are written.
`person:<resident_id>` is a valid destination for something the resident
keeps on them after the activity (for instance, after commuting to work, jacket and keys may
stay on the person). A dist whose every real outcome is the object's own home
is not a journey and will be discarded.

Most objects are untouched by most activities: an empty `rules` list for
an object is the normal, correct answer. NO TWO OBJECTS share identical
rules — each object's set-down spots and probabilities come from ITS
role and the persona, not its neighbour's.

Respond only with valid JSON matching the provided schema. No
commentary.
""")

BINDING_USER = """\
The household (persona, verbatim):

{persona}

Story activities with NO object rule (bind these and no others; the
place after each name is where the story puts the resident during it):
{activities}

The objects, their homes, and the rules they ALREADY have (do not repeat
these; your additions compose with them):
{objects}

Places in this home:
{places}

For each object in order, give `rules` (possibly empty) for the unbound
activities above.
"""


LEAK_AUDIT = PromptTemplate("leak_audit", """\
You are auditing a simulated household for vocabulary leaks. You get the
household's object id list and receptacle id list, with all narrative
context removed, plus the closed list of candidate household types. Guess
which type this household is, from the ids alone, and give your confidence.

Answer with your genuine best guess — this is a leak audit: if the ids
alone give the household away, the generation pipeline needs to know.

Respond only with valid JSON matching the provided schema. No commentary.
""")


# --------------------------------------------------------------------------
# user-message builders (covered by BUILDER_VERSION)
# --------------------------------------------------------------------------

def persona_user_prompt(slot: dict, other_types: list[str]) -> str:
    lines = [
        f"household_id: {slot['household_id']}",
        f"TYPE: {slot['household_type']}",
        f"residents: {slot['residents']} ({slot.get('residents_spec', '')})",
        f"constraints: {slot.get('constraints') or 'none'}",
        "",
        "Other household types in this set (for contrast only — make this "
        "household clearly unlike what those types suggest):",
        ", ".join(other_types),
    ]
    return "\n".join(lines)


DAY_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]


def calendar_table(days: int) -> str:
    """day index -> weekday, spelled out. Arc events name a day NUMBER
    while weekly blocks name weekday CODES; making the model derive that
    mapping itself was the single largest source of rejected programs
    (special events dropping activities that do not run on that day)."""
    return "\n".join(
        "  " + "   ".join(
            f"day {d:>2} = {DAY_FULL[d % 7][:3]} ({DAY_ABBREV[d % 7]})"
            for d in range(row, min(row + 3, days)))
        for row in range(0, days, 3))


def program_user_prompt(persona_text: str, receptacles: list[dict],
                        days: int, day0: str) -> str:
    rec_lines = "\n".join(f"  - {r['id']} (room: {r['room']})"
                          for r in receptacles)
    return (
        f"Author the routine program for the household below: {days} days, "
        f"day 0 = {day0}.\n\n"
        f"This episode's calendar — a special event's `day` is an index here, "
        f"and it may only drop an activity whose weekly block lists that "
        f"day's code:\n{calendar_table(days)}\n\n"
        f"Receptacles in this home (the only places objects can be):\n"
        f"{rec_lines}\n\n"
        f"PERSONA (the ground truth to encode):\n\n{persona_text}"
    )


def render_calendar(program: dict) -> str:
    """The accepted calendar rendered compactly (resident, weekdays, time,
    activity, place) — the shared context for the objects call and the
    special-events call."""
    lines = []
    for b in (program.get("sleep_schedule") or []):
        lines.append(f"  {b['resident']}  {','.join(b['days'])}  "
                     f"{b['start']}-{b.get('end', '?')}  {b['activity']} "
                     f"@ {b['at']}  [sleep]")
    for b in program.get("weekly_blocks") or []:
        lines.append(f"  {b['resident']}  {','.join(b['days'])}  "
                     f"{b['start']}-{b.get('end', '?')}  {b['activity']} "
                     f"@ {b['at']}  skip_p={b.get('skip_p', 0)}")
    return "\n".join(lines)


def objects_user_prompt(persona_text: str, receptacles: list[dict],
                        program: dict) -> str:
    rec_lines = "\n".join(f"  - {r['id']} (room: {r['room']})"
                          for r in receptacles)
    return (
        f"Author the object rules for the household below.\n\n"
        f"The weekly calendar these rules fire with (resident, weekdays, "
        f"time, activity, place):\n{render_calendar(program)}\n\n"
        f"Receptacles in this home (the only places objects can be):\n"
        f"{rec_lines}\n\n"
        f"PERSONA (the ground truth to encode):\n\n{persona_text}"
    )


def special_user_prompt(program: dict, days: int) -> str:
    """The accepted program rendered compactly: the calendar the events
    patch, with weekday lists visible so a drop can be aimed at a day the
    activity actually runs."""
    return (
        f"The household's routine program ({days} days, day 0 = Monday).\n\n"
        f"This episode's calendar — an event's `day` is an index here:\n"
        f"{calendar_table(days)}\n\n"
        f"The weekly calendar (resident, weekdays, time, activity, place):\n"
        + render_calendar(program))


def leak_user_prompt(object_ids: list[str], receptacle_ids: list[str],
                     household_types: list[str]) -> str:
    return (
        "Candidate household types:\n"
        + "\n".join(f"  - {t}" for t in household_types)
        + "\n\nObject ids:\n" + "\n".join(f"  - {o}" for o in object_ids)
        + "\n\nReceptacle ids:\n" + "\n".join(f"  - {r}" for r in receptacle_ids)
    )
