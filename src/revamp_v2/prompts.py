"""Prompt registry + guided-JSON schemas for the revamp_v2 pipeline.

Every LLM-facing string in revamp_v2 lives here, nothing inline — the
PromptTemplate pattern is ported from
src/dynamic_home_eqa/generation/prompt_registry.py: each template carries a
content-derived version (first 8 hex of sha256), folded into the cache stage
tag via .tag(), so cached responses can never silently survive a wording
change. BUILDER_VERSION covers the user-message assembly done by the
builder functions below — bump it by hand whenever that assembly changes.

Three templates (the pipeline's entire LLM surface):
  PERSONA          L1 — ported essentially verbatim from
                   profiles/revamp_v1/generation_prompt.md; only the output
                   transport changed (guided JSON instead of pasted YAML).
  ROUTINE_PROGRAM  L2 — the one new prompt: compiles a persona into a
                   weekly-pattern + arc-exceptions routine program.
                   Deliberately contains NO example content (objects, rooms,
                   story beats) that could prime uniform outputs across
                   households — the legacy DAY_PLAN storm-priming bug
                   (reports/stage1c/dataset_report.md) is the cautionary case.
  LEAK_AUDIT       validation check 4 — household-type classification from
                   object/receptacle ids alone; chance = 1/len(types).
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

# Object classes a person keeps ON them rather than in a place. Their home
# is the OWNER, not a receptacle: they ride along all day, out of the house
# included, and reach a receptacle only by being put down — which is how a
# phone actually behaves, and how revamp_v1's hh1 modelled Marisol's.
# Measured before this existed: not one object in ten households ever sat
# on a person, so the banks contained no ON_PERSON state at all, and a
# grad student's phone moved less than her mug and never left with her.
CARRIED_CLASSES = ["phone", "keys", "wallet", "headphones", "glasses"]

# The activities that take somebody OUT of the house. A carried item gets a
# pinned pick-up on one of these, because "on the person" has to include
# the moments they leave: with only a morning pick-up, the model put the
# phone down at the desk by mid-morning and the errand went without it.
LEAVING_ACTIVITIES = [
    "commute_out", "work_away", "school_run", "school", "errands",
    "groceries", "appointment", "night_out", "walk", "gym", "travel_away",
]

# A CLOSED activity vocabulary, drawn on by weekly_blocks, sleep_schedule,
# the per-activity extras AND every object rule. Activity names are the one
# cross-reference the schema could not otherwise constrain — they are free
# strings written in two distant sections — and the generator duly wrote
# rules for `snack` and `play` in a household whose blocks were `dinner`
# and `homework`, orphaning every rule and leaving 26 of 30 objects inert.
# Drawing both sections from one enum makes a dangling reference
# unwritable. Household character lives in the times, the jitter, the
# probabilities and the object rules — not in the activity's name — the
# same reasoning the closed 25-class object vocabulary already applies.
ACTIVITY_VOCAB = [
    # sleep and rest
    "night_sleep", "day_sleep", "nap", "lie_down", "bedtime_routine",
    "wake_up",
    # meals and kitchen
    "breakfast", "lunch", "dinner", "snack", "meal_prep", "batch_cooking",
    "coffee", "wash_dishes", "put_away_dishes",
    # out of the house
    "commute_out", "commute_home", "work_away", "school_run", "school",
    "errands", "groceries", "appointment", "night_out", "walk", "gym",
    "travel_away", "arrive_home",
    # work and study at home
    "work_home", "homework", "study", "video_call",
    # leisure at home
    "relax", "watch_tv", "gaming", "reading", "hobby", "music",
    "play_with_kids", "socialise_home", "phone_time",
    # chores and care
    "tidy_up", "deep_clean", "laundry", "take_out_bins", "pet_care",
    "medication", "shower", "bath", "get_ready",
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
                           # leave objects around the home. At least 2 must
                           # involve another resident. Examples:
                           # - "reads in bed, leaves the book on the
                           #    nightstand"
                           # - "borrows resident_2's charger from the desk
                           #    and rarely returns it"
                           # - "clears everyone's mugs to the kitchen when
                           #    tidying in the evening"
relationships: ...         # 2-3 sentences: who these people are to each
                           # other, and how they divide or share chores,
                           # spaces, and belongings. Include at least one
                           # point of friction or coordination (e.g. who
                           # does dishes, who loses the remote, whose stuff
                           # spreads into shared spaces).
home_layout_notes: ...     # 2-3 sentences: rooms and surfaces each person
                           # uses most, and which spaces are shared.
object_inventory:
  - id: mug_1              # indexed ids: mug_1, mug_2, laptop_sam. The id
                           # MUST begin with its class ("mug_1", not "cup_1")
    class: mug             # pick classes from the vocabulary below
    owner: resident_1      # or "shared"
    role: ...              # one short phrase: what this object is FOR in
                           # this household and how it tends to move. For
                           # shared objects, say who moves it and why.
daily_life_summary: ...    # 3-4 sentences describing a typical day in
                           # plain words, still without clock times.
                           # Mention how the residents' days overlap or
                           # miss each other (who is home when others are
                           # out, who crosses paths where).
quirks: ...                # 1-2 ways this household differs from the
                           # stereotype of its type

Object vocabulary (choose from these; do not invent new classes):
[mug, bowl, plate, laptop, phone, keys, book, water_bottle, remote,
charger, backpack, jacket, headphones, glasses, notebook, pen,
medication_bottle, toy, blanket, towel, gaming_controller, dog_leash,
lunchbox, umbrella, wallet]

Inventory rules:
- Not every household owns every class. Small households own few objects.
- Every object must have a MOMENT in this household's week — a point where
  someone picks it up, puts it down, or carries it somewhere. A later step
  has to say what moves each object and where; an object nobody in this
  particular home ever handles (a backpack in a household with no student
  or commuter, a dog leash with no dog) has no such moment, so leave it
  out. Fewer objects that all live are better than more that sit.
- Object counts should match household size (a family of five owns more
  bowls and backpacks than a person living alone). Per-person items like
  phones, keys, and wallets should exist per resident.
- Suggestive objects are allowed (medication_bottle, toy, dog_leash), but
  write the "role" field so the object's meaning comes from how it is
  used, not from the fact that it exists. The same object class could
  mean different things in different households.
- Shared objects are encouraged in multi-person homes; their "role" should
  name which residents move them.

Respond only with valid JSON matching the provided schema. No commentary.
""")

ROUTINE_PROGRAM = PromptTemplate("routine_program", """\
You are compiling a household ROUTINE PROGRAM: the complete machine-readable
weekly pattern of one household, derived strictly from its persona (in the
request). A deterministic simulator — not you — realizes the program into
weeks of object movements, so you author the judgment (times, bindings,
probabilities) once, and the simulator does all the bookkeeping.

Use ONLY the resident ids, object ids, receptacle ids and ACTIVITY NAMES
offered by the schema. Activity names come from one closed list shared by
every section: the block that schedules an activity and the object rule
that fires with it must name the SAME one, and a rule naming an activity
your household never schedules simply never happens. Pick the closest name
from the list rather than inventing one — a household's character comes
from its times, its probabilities and what its objects do, not from what
its activities are called. Every rule and block must encode something the persona states or
clearly implies. `cites` comes FIRST in every rule and block, and it is
written BEFORE you choose a destination, a time or a probability: name the
persona phrase that licenses what you are about to write, then write it.
It is a reason to decide from, not a note explaining a decision already
made — if you cannot state the licence first, the rule does not belong.
Keep it to ONE short clause, ten words or so, quoting the persona; the
field is hard-capped, and long early citations crowd out later objects
until the program runs out of room and truncates.
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
of the house. Blocks of the same activity must all share one `at` and one
`jitter`.
- `sleep: true` marks an OPTIONAL nap here (the real sleep is above). Set
  it only on a block where the person is genuinely asleep.
- Each activity name appears ONCE in `activities`, however many blocks
  use it.
- Decide what is INVARIANT for this household (skip_p: 0, tight jitter)
  versus variable (skip_p 0.1-0.4, looser jitter). Real people skip chores
  and optional meals, never contractual anchors, and never their actual
  sleep: a sleep block takes skip_p 0, whatever else slips that day. An
  optional NAP is different — that one is skippable, and often should be. Most
  households should end up with HALF or more of their non-anchor blocks
  (chores, optional meals, leisure, tidying) carrying a nonzero skip_p; a
  home where every planned thing happens every single day is a timetable,
  not a household.
- jitter classes, calibrated on real free-living homes — external: σ10 min
  (contractual: shifts, commutes, school runs, self-imposed strict
  rituals); routine: σ30 (body-clock: sleep onset, household meals);
  flexible: σ75 (self-paced); loose: σ110 (whim). Nothing real is tighter
  than external; per-resident `jitter_scale` (0.5 tidy-punctual to 2.0
  scattered) sets how punctual each person is overall.

object_rules — one entry per inventory object, in the same order, and this
section is the POINT of the program: the blocks say where people are, the
rules say what that does to their things. Take the objects ONE AT A TIME
and ask what this household actually does with this thing across a week.
Each entry carries everything about that object:
- `home` — where it belongs and where a tidy-up returns it, from its
  `role`. For a pocket item — a phone, keys, a wallet, headphones, glasses
  — THINK about whether this particular person keeps it ON them: if so,
  its home is `person:<owner>`, it automatically goes along whenever they
  leave the house, and your rules should say where it gets SET DOWN (the
  nightstand overnight, the desk while working, the counter on the way
  past) and picked back up. Decide per item and per person, not as a
  blanket: most people's phone rides with them, but a wallet may live in a
  bag by the door all day, reading glasses may never leave the desk, and a
  forgetful teenager's keys might be wherever they last landed. A home
  where every pocket item is glued to its owner all week is as wrong as
  one where phones sit on shelves — mix it, following each `role`.
- `p_misplace` (per day) + `misplace_set` — when the role describes
  absent-minded drift: the object gets set down at a random moment, on top
  of whatever its rules do. This is how a carried thing gets forgotten and
  left behind, so pocket items usually deserve one (0.1-0.4, at the spots
  this person actually abandons things). Omit both for objects that do not
  drift; never write a zero probability, and never give them to an object
  with no rules.
- An object that genuinely stays put is declared, not left blank: give
  it `motion: rarely_moved` with empty `rules` and cite the persona phrase
  that says so — a charger on its dock, a bowl by the door, a decorative
  thing nobody touches. This is a legitimate answer and you should use it
  whenever it is the truth: a home is allowed static objects. What is NOT
  legitimate is faking motion instead — writing two rules that both point
  at the object's own home says "it never moves" in a way that reads as
  movement and will be rejected. If it stays, say it stays.
  It is not available for things people carry (phones, keys, wallets,
  bags): a phone that sits on one charger for three weeks is a broken
  household, not a static object, whatever the persona implies.
- Otherwise its first two rules are the two legs of a journey, in order:
  a `during` rule naming the activity that picks the object UP and where
  it is taken — somewhere OTHER than its home, which is the whole point —
  then an `after` rule saying where it is left when that activity ends.
  Add further rules after those for whatever else happens to it. Each rule
  names the `activity` it fires with, a `phase` (`during` = when that
  activity starts, `after` = when it ends), and where the object ends up:
  `{dest}` (always there), `{dest, p, else}` (dest with probability p,
  otherwise the other named place — p and else come as a PAIR), or
  `{dist}` (2-5 places whose probabilities sum to 1). Probabilities are
  how reliably the persona's habit actually happens.
- Read every rule you write as a sentence: "because <cites>, when
  <activity> <starts/ends>, this goes from <only_from> to <dest>". If the
  from and the to are the same place, you have written "from the desk to
  the desk", which is not a journey — either give it somewhere real to go,
  or stop and declare it `motion: rarely_moved` instead. An object whose
  every destination is its own home has not moved, however many rules it
  has.
- NO TWO OBJECTS share one story. If phone_2 and wallet_2 get the same
  activities and the same destinations they will trace identical paths for
  three weeks, which real homes never produce. Give each object its own
  pattern — different set-down spots, different activities, different
  probabilities — drawn from ITS role, not its neighbour's.
- Things that are WORN or TAKEN ALONG move by definition: a jacket is worn
  out and hung up (or dumped on a chair), a backpack goes to work or
  school and comes back, an umbrella leaves on wet-weather trips, a laptop
  commutes between desk and couch or bag, a towel cycles through the wash.
  Declaring one of these `rules: []` says this household never wears the
  jacket — write that only when the persona actually says so.
- `only_from` names where the journey STARTS: the pick-up rule of every
  moving object states the places it might be resting when the activity
  begins. List every plausible origin, not just the home — if the object
  drifts (p_misplace) or its evening rule leaves it out, the pick-up must
  still fire from THOSE spots, or the object strands there for the rest
  of the run. It also stops a rule firing from its own result — a
  clear-to-the-sink rule should not fire on a day nothing was used.
- Every `activity` you name here must be one your sleep_schedule or
  weekly_blocks actually runs — check back against them.
activities — per-activity extras only (the object rules live above):
- `reset_all: {p, objects}` is a timed tidying walk: the resident walks
  the home putting strays back, one item at a time, for as long as the
  block lasts. It belongs ONLY on a block where someone is awake and
  actually tidying (a sweep, a reset, a wash-up), scoped by `objects` to
  what that sweep plausibly touches. Two consequences worth stating:
  - NEVER on a sleep or nap block — nobody walks the house while asleep.
    If you want the home to be tidier after a sleep, that is an `after`
    rule (or a reset_all) on the WAKING block that precedes or follows it:
    the clearing-up happens while someone is up, which is also when a real
    person does it.
  - Not on every activity either: a household that tidies constantly never
    accumulates the clutter the tidying is for. One or two tidying
    activities per household is normal.
- `fragment: {mean_bouts: k}` on activities that really happen as several
  short bouts spread over the block rather than one sitting. Give AT LEAST
  TWO activities a `fragment` with mean_bouts 2-5 — measured against real
  homes this is the single biggest gap in authored routines (a real
  kitchen sees ~4 separate sessions a day where a schedule writes one), so
  pick the household's own bursty behaviour: kitchen trips, checking a
  phone, puttering, going in and out. Never fragment sleep. EVERY `after`
  rule of a fragmented activity needs `only_from`, since those rules fire
  once per bout and would otherwise re-trigger all evening.

arc_events — the story layer: 4-8 dated exceptions across the episode,
each a patch (`drop` block realizations that day, and/or `add` one-off
blocks) with a `note` telling the beat. Check the calendar above before
writing a `drop`: it only bites if that activity's weekly block lists
that day's code, so dropping a weekday-only shift on a Saturday changes
nothing. An `add` block needs no `days` — its day is the arc event's own. Together they must span at least:
one skipped recurring chore, one schedule-violating appointment (an added
ELSEWHERE block at a time the routine says the resident is home or
asleep), and one multi-day fatigue or recovery stretch (several
consecutive days patched). Make the exceptions THIS household's — what
would actually go wrong in this life.

No example content is provided, deliberately: invent this household's
pattern from ITS persona, not from a template.

Respond only with valid JSON matching the provided schema. No commentary.
""")

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
    (arc events dropping activities that do not run on that day)."""
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
        f"This episode's calendar — an arc event's `day` is an index here, "
        f"and it may only drop an activity whose weekly block lists that "
        f"day's code:\n{calendar_table(days)}\n\n"
        f"Receptacles in this home (the only places objects can be):\n"
        f"{rec_lines}\n\n"
        f"PERSONA (the ground truth to encode):\n\n{persona_text}"
    )


def leak_user_prompt(object_ids: list[str], receptacle_ids: list[str],
                     household_types: list[str]) -> str:
    return (
        "Candidate household types:\n"
        + "\n".join(f"  - {t}" for t in household_types)
        + "\n\nObject ids:\n" + "\n".join(f"  - {o}" for o in object_ids)
        + "\n\nReceptacle ids:\n" + "\n".join(f"  - {r}" for r in receptacle_ids)
    )
