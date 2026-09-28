#!/usr/bin/env python3
"""Build guest_v4: guest_v3 with cause A spread over three places, and the disruption
measured from the day it actually starts.

WHY THERE IS A v4, measured not guessed. guest_v3 generated cleanly, cause A fired in all
ten homes (4.2 movers per home against v2's 0.6), and the two causes measured as genuinely
independent: agreement 0.319 across them against 0.533 inside one, a drop of 0.215, where
the same contrast on the ILLNESS gives 0.014 and on a random split of guest_v3's own movers
gives -0.02. But check_scenario said DO NOT RUN, on one bar: the three-day counting method
loses only 3.1 points on the first two disrupted days against a bar of 8.

Two faults behind it, both diagnosed from the gate's own output rather than guessed:

  1. THE DISRUPTION WAS MEASURED IN THE WRONG PLACE. Cause B switches on day 9 - that is
     the whole point of it - but the calendar called days 9-13 `prepare`, so the gate
     treated them as ordinary life and measured the break at day 14, by which time the
     three-day memory had already had five days to learn cause B. Only cause A was new at
     the boundary the gate looked at. Fixed by giving BOTH disruption stages the same
     name, `guest`: the guest episode is one fifteen-day disruption with two phases, and
     `stage_for` still resolves force_events by day range while the bank header records one
     window of days 9-23.

  2. CAUSE A COLLAPSED TO ONE PLACE. With `after: [any]` all four of its classes rested on
     the coffee table, so 44 of 93 movers landed on one receptacle - 47% against the gate's
     60% bar - and per-object accuracy inside the window rose to 96% against 86% in
     ordinary life. A window where everything is in one place is EASIER than ordinary life,
     which is the fault that killed sick10_owner. Fixed the way the illness fixes it: three
     bouts in the living room on three different surfaces, so the plate rests on the coffee
     table, the glass on the side table and the snack bowl on the armchair.

guest_v2 and guest_v3 are kept beside this, unchanged, as the record of the two earlier tries.

guest_v3 was: guest_v2 with cause A made to last.

WHY THERE IS A v3, measured not guessed. guest_v2 generated and measured cleanly and cause
B worked exactly as designed - it switches on day 9 in 16 of 18 cases, and agreement ACROSS
the two causes is 0.192 against 0.684 inside one cause. But cause A produced only 0.6 movers
per household and NONE AT ALL in seven of the ten homes. The reason is mechanical: its rules
fired only `after` the two guest meals, so a plate went to the coffee table for an hour and
then went back to the sink (`after_use: sink`) and the cupboard. Over the fifteen daytime
hours the commonest place never changed, so the plate was not a mover.

The fix is the one the illness already uses for the glass by the bed: `after: [any]`, so the
plate RESTS on the coffee table for the whole stay, plus `wash_dishes` and `snack` removed.
That is also the true fact about a guest - the washing up does not get done - and it is a
change to the world, not to a threshold. guest_v2 is kept beside this, unchanged, as the
record of the first try.

Build guest_v2 was: a scenario whose disruption has TWO causes on two different sets of
objects, in two different rooms, starting on two different days.

WHY, AND THE DESIGN GOAL STATED BEFORE ANYTHING WAS GENERATED.

Measured on 2026-09-25 (results/self_improve/why_the_movers_are_drinkware/): the illness
produces effectively 2.4 to 3.4 independent movers out of 6 to 14, and widening the
asked-about class list from 11 kinds to 21 did not change the mean pairwise agreement at
all (0.286 before, 0.286 after). The reason is structural, not about kinds of object: ONE
event starts on ONE day for ONE person, and that person's belongings follow that person.
Measured on varied_v3's 547 mover pairs, agreement falls with the gap between the two
switch days - 0.408 on the same day, 0.356 one day apart, 0.248 at two to three days,
0.243 at four to seven. So the only lever that touches the correlation is TIME, and a
second cause has to start on a different day, not merely move different things.

guest_v1 fails one gate bar by two points and its change is most visible at MIDNIGHT. That
is the other thing fixed here: measured over varied_v3's 7,440 questions, no question is
ever asked between 23:00 and 06:59, 21.7% are asked 07:00-09:59, 41.3% 10:00-17:59 and
37.0% 18:00-22:59, with peaks at 08-09 (16.8%) and 19-20 (18.1%). guest_v1's added bouts
run 18:15 to 22:05, and its two strongest (clear_the_couch 21:25, blanket_away 21:50) land
in the 12.6% tail and then persist through the eight hours when nothing is asked. Every
bout added below starts at 09:00, 12:40, 13:30 or 19:20 - inside the peaks.

THE TWO CAUSES.

  A  THE TABLE MOVES TO THE LIVING ROOM, days 14-23, household scope.
     The guest is fed and entertained in the living room for the whole stay, so lunch and
     supper happen at the coffee table instead of the dining table. The objects are
     plates, glasses and the serving dish: every resident's, and the serving dish is
     nobody's at all. Not one of them belongs to a single person, which is exactly what
     the illness could never give us.

  B  THE OFFICE BECOMES THE GUEST'S BEDROOM, days 9-23, household scope.
     The spare room is turned into a bedroom five days BEFORE the guest arrives - beds are
     made up and rooms are aired in advance - and stays that way until they leave. So the
     desk work moves to the bedroom desk from day 9, five days before cause A starts. The
     objects are the work kit. Different room, different objects, and a five-day head
     start, which is the band where measured agreement is 0.243 rather than 0.408.

  A one-day tidy pulse was considered and dropped: one day out of thirty-two cannot move a
  day-level agreement measure, and pretending otherwise would be decoration.

WHAT COULD NOT BE BUILT, and it is a fact about the generator rather than a choice.
  * "the guest's own things appear at the entry and are gone afterwards" is not buildable.
    Every object in `src/situation_sim/objects.yaml` is created by `sample_household` at
    day 0 and exists for the whole month; there is no mechanism for an object that appears
    mid-episode. A guest towel cannot appear either.
  * "the cushions move to the couch" is not buildable. `cushion` is `static: true` in the
    catalogue, and `question_rows` and `sensable_question_rows` both drop static objects,
    so a cushion never moves and is never asked about.
  Both would need an edit to src/situation_sim/, which this work may not make.

THE CAP THAT REFUSES A RULE, and why the mover list below is shorter than the wish list.
A question is asked in the middle of a bout and the answer is that bout's surface, so a
class used on two surfaces during the disruption has its answer split and shows no step.
`make_the_events.py` turned that into a refusal and this script uses the same test. It is
the cap that binds on this design: `notebook` is used at the dining table by
`crossword_table` and at the entry table by `pack_the_bag`, `mug` and `water_bottle` are
used all over the house, and each is therefore left as a CONTROL rather than forced into a
rule that would not hold. The refusals are printed, not hidden.

Run: python3 results/self_improve/varied_homes/make_the_guest.py
Reads src/situation_sim/ and scenario/*.yaml; writes only new files beside them.
"""
import copy
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
ACTS_IN = HERE / "scenario" / "activities_varied.yaml"
EVENTS_IN = HERE / "scenario" / "events_varied.yaml"
ACTS_OUT = HERE / "scenario" / "activities_guest_v4.yaml"
EVENTS_OUT = HERE / "scenario" / "events_guest_v4.yaml"

# New bouts. Rooms, surfaces and hours only; no new object CLASS is invented anywhere, and
# nothing under `habits` is touched, so `sample_household` samples the same households as
# varied_v2 and varied_v3 and the three scenarios sit on the same ten homes.
NEW_ACTIVITIES = {
    # cause A: the guest is fed in the living room. 12:40 and 19:20 are both inside the
    # hours where questions are actually drawn.
    "lunch_with_the_guest": dict(
        room="living", surface="coffee_table", uses=["plate", "phone"],
        jitter="flexible", words="lunch in the living room with the guest"),
    "supper_with_the_guest": dict(
        room="living", surface="coffee_table",
        uses=["plate", "serving_dish", "phone"],
        jitter="routine", words="supper in the living room with the guest"),
    # three surfaces, not one: the plate on the coffee table, the glass on the side table,
    # the snack bowl on the armchair. A disruption that puts everything in one place is an
    # EASIER prediction problem than ordinary life, which is what guest_v3 measured at 96%
    # per-object accuracy and a single receptacle taking 47% of all movers.
    "drinks_with_the_guest": dict(
        room="living", surface="side_table", uses=["glass", "phone"],
        jitter="loose", words="drinks with the guest by the side table"),
    "snacks_with_the_guest": dict(
        room="living", surface="armchair", uses=["snack_bowl", "phone"],
        jitter="loose", words="something to nibble with the guest"),
    # cause B: the desk work moves to the bedroom desk. Same hours as the work_session
    # bouts it replaces, which is what keeps it inside the question hours.
    "work_from_the_bedroom": dict(
        room="bedroom", surface="desk",
        uses=["laptop", "charger", "pen", "headphones", "phone"],  # charger and headphones are used here AND elsewhere, so they stay controls
        jitter="routine", words="working at the bedroom desk"),
}

# cause B, days 9-23: the spare room is made up as a bedroom and the desk work moves out.
PREPARE_REMOVE = ["work_session", "study", "video_call", "desk_wind_down"]
PREPARE_ADD = [
    {"activity": "work_from_the_bedroom", "room": "bedroom", "start": "09:00",
     "duration": 190, "mean_bouts": 2, "who": "all_home"},
    {"activity": "work_from_the_bedroom", "room": "bedroom", "start": "13:30",
     "duration": 150, "mean_bouts": 2, "who": "all_home"},
]
# charger and headphones were in this list and the one-surface test REFUSED both, for a
# reason worth keeping in the world rather than removing: the charger is still docked by
# the front door every night (`dock_by_the_door`, entry_table) and the headphones are still
# used for calls in bed (`call_family`, bed). Forcing a rule on either would split its
# answer between two surfaces and it would show no step. Both are CONTROLS instead - and
# good ones, because they belong to the same person as the laptop and do not move, so an
# arm that generalises "this person's things moved" is wrong about them.
PREPARE_PLACEMENT = [
    {"class": "laptop", "after": ["work_from_the_bedroom"], "to": "desk",
     "note": "the laptop lives on the bedroom desk while the office is a guest room"},
    {"class": "pen", "after": ["work_from_the_bedroom"], "to": "desk",
     "note": "the pen moved to the bedroom desk"},
]

# cause A, days 14-23: everything cause B does, PLUS the meals in the living room.
# `board_game_night` is removed too, and not to make a number work: it puts a glass on the
# dining table, and while a guest has the living room and the evenings the household's own
# board-game night does not happen. Without this removal the glass is used on two surfaces
# and shows no step; with it the glass is the second class of cause A.
# `wash_dishes` and `snack` are removed as well: with them in, a plate goes to the sink and
# the snack bowl to the kitchen counter, and neither is a mover.
GUEST_REMOVE = PREPARE_REMOVE + ["lunch", "dinner", "evening_tv", "movie",
                                 "board_game_night", "wash_dishes", "snack", "gaming"]
# `gaming` goes for the same stated reason as `board_game_night`: it puts the snack bowl on
# the living-room couch, and the living room and its evenings belong to the guest. Without
# this removal the snack bowl has two surfaces and shows no step.
GUEST_ADD = PREPARE_ADD + [
    {"activity": "lunch_with_the_guest", "room": "living", "start": "12:40",
     "duration": 45, "who": "all_home"},
    {"activity": "supper_with_the_guest", "room": "living", "start": "19:20",
     "duration": 60, "who": "all_home"},
    {"activity": "drinks_with_the_guest", "room": "living", "start": "20:30",
     "duration": 50, "who": "all_home"},
    {"activity": "snacks_with_the_guest", "room": "living", "start": "15:30",
     "duration": 40, "who": "all_home"},
]
GUEST_PLACEMENT = PREPARE_PLACEMENT + [
    # `after: [any]` rather than after the two meals, for the reason in the docstring: a
    # rule that fires only after a meal loses to `after_use: sink` for the other fourteen
    # hours of the day and the object is never a mover. With `any` the washing up simply
    # does not get done while the guest is there, which is the true fact anyway.
    {"class": "plate", "after": ["any"], "to": "coffee_table",
     "note": "the plates stay by the sofa; the washing up waits while the guest is here"},
    {"class": "glass", "after": ["any"], "to": "side_table",
     "note": "the glasses stay on the side table by the armchair"},
    {"class": "serving_dish", "after": ["any"], "to": "coffee_table",
     "note": "supper is served from the coffee table and stays there"},
    {"class": "snack_bowl", "after": ["any"], "to": "armchair",
     "note": "the snack bowl lives on the armchair while the guest is here"},
]

CONTROLS = ["towel", "razor", "notebook", "mug", "water_bottle", "bowl", "book",
            "tablet", "medication", "glasses", "remote", "blanket", "snack_bowl",
            "pot", "pan", "charger", "headphones"]
CONTROLS = [c for c in CONTROLS if c != "snack_bowl"]   # snack_bowl is a cause-A mover in v3


def reachable(acts_full, add_blocks, remove_list):
    """Every bout a resident can still have during the stage, and the activities table."""
    gone = set(remove_list)
    gone_slots = {s[5:] for s in remove_list if s.startswith("slot:")}
    out = {a["activity"] for a in add_blocks}
    for role, days in acts_full["schedules"].items():
        for blocks in days.values():
            for b in blocks:
                if "activity" in b and b["activity"] not in gone:
                    out.add(b["activity"])
    for kind in ("hobbies", "chores"):
        for name, spec in acts_full["habits"][kind].items():
            if set(spec["slots"]) - gone_slots and spec["activity"] not in gone:
                out.add(spec["activity"])
                if spec.get("then"):
                    out.add(spec["then"])
    for slot, opts in acts_full["slot_defaults"].items():
        if slot not in gone_slots:
            for o in opts:
                if o["activity"] != "none" and o["activity"] not in gone:
                    out.add(o["activity"])
    for b in acts_full["habits"]["pet"]["dog"]["blocks"]:
        if b["activity"] not in gone:
            out.add(b["activity"])
    return out


def surfaces_for(acts_full, bouts):
    acts = acts_full["activities"]
    out = {}
    for name in sorted(bouts):
        spec = acts.get(name)
        if spec is None or spec.get("surface") is None:
            continue
        for token in spec.get("uses", []):
            for cls in str(token).split("|"):
                out.setdefault(cls, {}).setdefault(spec["surface"], []).append(name)
    return out


def check_stage(label, acts_full, add_blocks, remove_list, placement, problems):
    bouts = reachable(acts_full, add_blocks, remove_list)
    surf = surfaces_for(acts_full, bouts)
    print(f"  stage '{label}': {len(bouts)} bouts a resident can still have")
    for rule in placement:
        cls, where = rule["class"], surf.get(rule["class"], {})
        if not where:
            problems.append(f"{label}/{cls}: no bout in this stage uses it, so the event "
                            f"cannot move it where a question can see it")
        elif len(where) > 1:
            detail = "; ".join(f"{s} ({', '.join(a)})" for s, a in sorted(where.items()))
            problems.append(f"{label}/{cls}: used on more than one surface, so its answer "
                            f"during the stage would be split: {detail}")
        elif sorted(where)[0] != rule["to"]:
            problems.append(f"{label}/{cls}: told to rest on {rule['to']} but used on "
                            f"{sorted(where)[0]}")
        else:
            print(f"    {cls:14s} -> {rule['to']:14s} one surface, agrees")
    # the controls must have no rule
    have = {r["class"] for r in placement}
    clash = sorted(set(CONTROLS) & have)
    if clash:
        problems.append(f"{label}: the controls {clash} were given a rule")
    return surf


def main():
    acts_full = yaml.safe_load(ACTS_IN.read_text())
    if set(NEW_ACTIVITIES) & set(acts_full["activities"]):
        print("a new activity name already exists in activities_varied.yaml")
        return 1
    acts_full["activities"].update({k: dict(v) for k, v in NEW_ACTIVITIES.items()})

    problems = []
    print("ONE SURFACE PER MOVED CLASS, checked per stage:")
    surf_p = check_stage("prepare (days 9-13)", acts_full, PREPARE_ADD, PREPARE_REMOVE,
                         PREPARE_PLACEMENT, problems)
    surf_g = check_stage("guest (days 14-23)", acts_full, GUEST_ADD, GUEST_REMOVE,
                         GUEST_PLACEMENT, problems)

    # A CHECK THAT CANNOT FAIL IS WORTHLESS. Feed the one-surface test classes known to be
    # used in several places and confirm it would refuse them.
    print()
    print("  power check - classes the test MUST refuse in the guest stage:")
    # notebook (dining table + entry table) and water_bottle (entry table + living-room
    # floor) are both verified multi-surface in this stage. `mug` was in this list and is
    # not: removing lunch, dinner and the television left it with only the dining table, so
    # it could in fact take a rule. It is kept as a control, and the power check no longer
    # claims it as a known-bad case - a check has to be fed a case that really is bad.
    for cls in ("notebook", "water_bottle"):
        w = surf_g.get(cls, {})
        if len(w) > 1:
            print(f"    {cls:14s} refused, {len(w)} surfaces: {sorted(w)}")
        else:
            problems.append(f"the one-surface test has lost its power: {cls} was expected "
                            f"to have several surfaces in the guest stage, found {sorted(w)}")

    # the two causes must touch DISJOINT sets of objects, or they are one pattern
    a = {r["class"] for r in GUEST_PLACEMENT} - {r["class"] for r in PREPARE_PLACEMENT}
    b = {r["class"] for r in PREPARE_PLACEMENT}
    if a & b:
        problems.append(f"the two causes share classes {sorted(a & b)}, so they are one pattern")
    print()
    print(f"  cause A (days 14-23, the living room): {sorted(a)}")
    print(f"  cause B (days 9-23, the bedroom desk): {sorted(b)}")
    print(f"  the two sets are disjoint: {not (a & b)}")

    # nothing under habits may change, or the households change with it
    original = yaml.safe_load(ACTS_IN.read_text())
    for key in ("habits", "schedules", "slot_defaults"):
        if acts_full[key] != original[key]:
            problems.append(f"'{key}' was modified; that would change which households the "
                            f"generator samples and the three scenarios would stop being "
                            f"comparable")

    if problems:
        print()
        print("NOT WRITTEN. Every one of these must be fixed first:")
        for p in problems:
            print("  -", p)
        return 1

    ACTS_OUT.write_text(
        "# guest_v2's activities: activities_varied.yaml plus three new bouts and nothing\n"
        "# else. `habits`, `schedules` and `slot_defaults` are byte-identical, so\n"
        "# sample_household samples the SAME ten households as varied_v2 and varied_v3.\n"
        "# Generated by results/self_improve/varied_homes/make_the_guest.py.\n"
        "# Edit that script, not this file.\n"
        + yaml.safe_dump(acts_full, sort_keys=True, default_flow_style=False, width=100))

    events = yaml.safe_load(EVENTS_IN.read_text())
    base = copy.deepcopy(events["events"]["guest_visit"])
    for name, add, rem, place, words in (
            ("making_up_the_spare_room", PREPARE_ADD, PREPARE_REMOVE, PREPARE_PLACEMENT,
             "the office is turned into a bedroom for the guest who is coming, so the desk "
             "work moves to the bedroom desk"),
            ("guest_in_the_house", GUEST_ADD, GUEST_REMOVE, GUEST_PLACEMENT,
             "a guest has the spare room, the desk work is still in the bedroom, and lunch "
             "and supper are eaten in the living room instead of at the table")):
        ev = copy.deepcopy(base)
        ev["description"] = words.capitalize() + "."
        ev["scope"] = "household"
        ev["p_day"] = {"weekday": 0.0, "weekend": 0.0}
        ev["placement"] = [dict(r) for r in place]
        ev["schedule"] = {"add": [dict(x) for x in add], "remove": list(rem)}
        ev["trace_words"] = words
        ev.pop("block", None)
        ev.pop("internal", None)
        events["events"][name] = ev
    EVENTS_OUT.write_text(
        "# guest_v2's events: events_varied.yaml plus making_up_the_spare_room and\n"
        "# guest_in_the_house. unwell_spell is copied through untouched and is switched off\n"
        "# by the config, so the guest is the only thing that changes in the month.\n"
        "# Generated by results/self_improve/varied_homes/make_the_guest.py.\n"
        "# Edit that script, not this file.\n"
        + yaml.safe_dump(events, sort_keys=True, default_flow_style=False, width=100))
    print()
    print(f"wrote {ACTS_OUT}")
    print(f"wrote {EVENTS_OUT}")
    print(f"  controls with no rule in either stage: {', '.join(CONTROLS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
