#!/usr/bin/env python3
"""Build varied_homes/scenario/activities_varied.yaml from the illness_v1 activities.

Written as a patch script rather than a hand-copied file so the change is auditable:
every edit below is applied to results/self_improve/scenario/activities.yaml, every
edit asserts that it actually changed something, and nothing is written unless all of
them applied. The asked-about class list in the config is NOT touched by this script.

THE PRINCIPLE, stated before anything was generated.

A question is asked in the middle of an activity and the answer is the surface that
activity uses, so "where do the answers live" is decided by which activity uses which
object in which room. In illness_v1 the same rooms hold the answers in ordinary life
and during the illness: the residents' evenings put mugs, glasses, books and chargers
on the sofa and the nightstand, and then the illness puts them on the sofa and the
nightstand. Six of ten homes were therefore uninformative.

So this household population is built the other way round:

  1. ORDINARY LIFE happens on the day-time surfaces - the bathroom shelf, the kitchen
     table, and the desk in the study. Mugs and glasses are not carried to the sofa,
     water glasses and chargers do not go to the bedside, screens do not go to bed.
     This is one coherent household habit (they eat and drink at the table), not a
     tuned list.
  2. THE ILLNESS happens on the bed, the nightstand, the sofa and the balcony - the
     surfaces ordinary life leaves empty. A ten-day illness genuinely does move a
     person to the bed and the sofa; what changed is that those are no longer where
     everything already was.
  3. THE RESIDENTS DIFFER BY ROLE, in rooms and in hours: the ones who leave the
     house pack a bag and dock a phone by the front door, the one who works at home
     lives at the desk in the study, the student reads over breakfast in the kitchen,
     the retired resident does the crossword at the table. Role composition differs
     from home to home, so the set of habits differs from home to home.
  4. SOME THINGS LIVE WHERE NOBODY WOULD GUESS: the pill box on the kitchen table,
     the water bottle and notebook on the hall table, the charger in the hall, the
     student's book in the kitchen. A common-sense prior gets these wrong; only a
     memory of this home gets them right.

None of these is a threshold and none of them mentions any method's score.
"""
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parent / "scenario" / "activities.yaml"
OUT = HERE / "scenario" / "activities_varied.yaml"

# 1. asked classes taken OFF the sofa, the armchair and the bedside.
DROP_USES = {
    "evening_tv":   ["mug", "glasses"],      # tea is drunk at the table, not the sofa
    "read":         ["glasses", "tablet"],   # no screens in bed; the glasses stay at the desk
    "read_living":  ["book", "glasses"],     # the armchair is for the magazine
    "listen_music": ["book"],
    "knit":         ["glasses"],
    "journal":      ["mug"],
    "gaming":       ["glass"],
    "movie":        ["glass"],
    "bedtime":      ["charger", "glass", "glasses"],   # the charger lives at the desk
    "morning_routine": ["glasses"],   # the glasses live at the desk, not the bathroom shelf
    "snack":        ["glass"],        # a snack is eaten standing up, with no glass
}
# 2. and the one unusual place every home has: the pill box on the kitchen table.
ADD_USES = {"breakfast": ["medication"]}
REPLACE_USES = {"call_family": ["phone", "headphones"]}   # was phone|tablet

# 3. meals happen at the table, not on the kitchen worktop and not in two places.
# This household eats at the table; the kitchen is where food is cooked. The point is
# that a glass or a mug then has ONE ordinary place instead of two it splits between -
# with breakfast on the kitchen table and dinner on the dining table, a well resident's
# glass sat 7 days in one and 7 in the other, and which one came out "usual" was a coin
# flip. An object with no usual place cannot be said to have moved.
MOVE_TO = {
    "breakfast":         ("dining_or_kitchen", "dining_or_kitchen_table"),
    "lunch":             ("dining_or_kitchen", "dining_or_kitchen_table"),
    "breakfast_reading": ("dining_or_kitchen", "dining_or_kitchen_table"),
}

# 3. new activities. Rooms and surfaces only; no new object class anywhere.
NEW_ACTIVITIES = {
    "pack_the_bag": dict(room="entry", surface="entry_table",
                         uses=["water_bottle", "notebook", "glasses", "phone"],
                         jitter="routine", words="packing the bag by the door"),
    "dock_by_the_door": dict(room="entry", surface="entry_table",
                             uses=["phone", "charger", "keys"],
                             jitter="routine", words="leaving the phone charging by the door"),
    "breakfast_reading": dict(room="kitchen", surface="kitchen_table",
                              uses=["book", "mug", "phone", "medication"],
                              jitter="routine", words="breakfast with a book"),
    "crossword_table": dict(room="dining_or_kitchen", surface="dining_or_kitchen_table",
                            uses=["notebook", "glasses", "mug", "medication"],
                            jitter="flexible", words="the crossword at the table"),
    "desk_wind_down": dict(room="workspace", surface="desk",
                           uses=["notebook", "charger", "glasses", "mug"],
                           jitter="routine", words="clearing the desk for the night"),
    # the illness's own bouts. dose_medicine moves OUT of the bathroom: over ten days
    # the pill packet is kept by the bed, not walked to the cabinet. That matters,
    # because the bathroom is the busiest room in almost every home the generator
    # builds, so a bathroom answer is an answer the robot already had.
    "dose_medicine": dict(room="bedroom", surface="nightstand",
                          uses=["medication", "vitamins", "glass", "phone"],
                          jitter="routine", words="taking medicine by the bed"),
    # supper is brought to where they are resting. It uses no asked-about class at all,
    # on purpose: a glass carried to the sofa would give the glass two illness places.
    "supper_on_a_tray": dict(room="living", surface="coffee_table",
                             uses=["plate", "bowl", "phone"], jitter="loose",
                             words="supper on a tray"),
    "sip_by_bed": dict(room="bedroom", surface="nightstand",
                       uses=["water_bottle", "glass", "phone"], jitter="loose",
                       words="sitting up in bed with a drink"),
    "nap_bed": dict(room="bedroom", surface="bed", uses=["charger", "phone", "blanket"],
                    jitter="loose", words="lying down in the bedroom"),
    "doze_couch": dict(room="living", surface="couch",
                       uses=["book", "glasses", "blanket", "phone"], jitter="loose",
                       words="dozing on the couch"),
    "rest_coffee": dict(room="living", surface="coffee_table", uses=["mug", "remote", "phone"],
                        jitter="loose", words="resting with a hot drink"),
    # the chair by the window, NOT "balcony or living": that token resolves to the
    # balcony table in one home and the living-room side table in another, while the
    # resting rule can only name one of the two. The tablet would then be used on the
    # balcony and rest in the living room, and its answer during the illness would be
    # split between two rooms. One surface, in every home.
    "sit_quietly": dict(room="living", surface="side_table",
                        uses=["tablet", "phone"], jitter="loose",
                        words="sitting quietly in the chair by the window"),
    # also no asked-about class: the mug belongs to the afternoon's rest_coffee and the
    # pills to the morning dose, and each must have exactly one place during the spell.
    "late_breakfast": dict(room="dining_or_kitchen", surface="dining_or_kitchen_table",
                           uses=["bowl", "phone"], jitter="loose",
                           words="a late, small breakfast"),
}

# 4. schedule additions, per role. (role, daytype) -> blocks to append.
SCHEDULE_ADD = {
    ("worker_out", "weekday"): [
        {"activity": "pack_the_bag", "start": "08:00", "duration": 10},
        {"activity": "dock_by_the_door", "start": "22:05", "duration": 10}],
    ("worker_out", "weekend"): [
        {"activity": "dock_by_the_door", "start": "22:30", "duration": 10}],
    ("shift_worker", "weekday"): [
        {"activity": "pack_the_bag", "start": "13:25", "duration": 10},
        {"activity": "dock_by_the_door", "start": "23:20", "duration": 10}],
    ("shift_worker", "weekend"): [
        {"activity": "dock_by_the_door", "start": "22:30", "duration": 10}],
    ("worker_home", "weekday"): [
        {"activity": "desk_wind_down", "start": "22:05", "duration": 10}],
    ("worker_home", "weekend"): [
        {"activity": "desk_wind_down", "start": "22:25", "duration": 10}],
    ("student", "weekday"): [
        {"activity": "pack_the_bag", "start": "08:30", "duration": 10}],
    ("retired", "weekday"): [
        {"activity": "crossword_table", "start": "08:30", "duration": 40}],
    ("retired", "weekend"): [
        {"activity": "crossword_table", "start": "09:00", "duration": 40}],
}
# the student eats with a book instead of eating: a swap, not an extra bout.
SCHEDULE_SWAP = {("student", "weekday"): [("breakfast", "breakfast_reading")],
                 ("student", "weekend"): [("breakfast", "breakfast_reading")]}


def main():
    acts = yaml.safe_load(BASE.read_text())
    A = acts["activities"]
    problems = []

    for name, drop in DROP_USES.items():
        if name not in A:
            problems.append(f"{name} is not an activity")
            continue
        before = list(A[name].get("uses", []))
        A[name]["uses"] = [u for u in before if u not in drop]
        if A[name]["uses"] == before:
            problems.append(f"{name}: none of {drop} was in its uses ({before})")
    for name, add in ADD_USES.items():
        if name not in A:
            problems.append(f"{name} is not an activity")
            continue
        before = list(A[name].get("uses", []))
        A[name]["uses"] = before + [u for u in add if u not in before]
        if A[name]["uses"] == before:
            problems.append(f"{name}: {add} already in its uses")
    for name, uses in REPLACE_USES.items():
        if name not in A:
            problems.append(f"{name} is not an activity")
            continue
        if A[name].get("uses") == uses:
            problems.append(f"{name}: uses already {uses}")
        A[name]["uses"] = list(uses)
    for name, spec in NEW_ACTIVITIES.items():
        A[name] = dict(spec)           # overwrites the illness bouts inherited from v1
    for name, (room, surface) in MOVE_TO.items():
        if name not in A:
            problems.append(f"{name} is not an activity")
            continue
        if (A[name].get("room"), A[name].get("surface")) == (room, surface):
            problems.append(f"{name} is already in {room}/{surface}")
        A[name]["room"], A[name]["surface"] = room, surface

    for (role, daytype), blocks in SCHEDULE_ADD.items():
        sched = acts["schedules"].get(role, {}).get(daytype)
        if sched is None:
            problems.append(f"no schedule for {role}/{daytype}")
            continue
        for b in blocks:
            if b["activity"] not in A:
                problems.append(f"{b['activity']} added to {role}/{daytype} is not an activity")
            if any(x.get("activity") == b["activity"] and x.get("start") == b["start"]
                   for x in sched):
                problems.append(f"{role}/{daytype} already has {b['activity']} at {b['start']}")
            sched.append(dict(b))
        sched.sort(key=lambda b: str(b.get("start", "00:00")))
    for (role, daytype), swaps in SCHEDULE_SWAP.items():
        sched = acts["schedules"].get(role, {}).get(daytype)
        if sched is None:
            problems.append(f"no schedule for {role}/{daytype}")
            continue
        for old, new in swaps:
            hit = [b for b in sched if b.get("activity") == old]
            if not hit:
                problems.append(f"{role}/{daytype} has no {old} block to swap")
            for b in hit:
                b["activity"] = new

    # every activity a schedule or a habit names must exist, or a household dies late
    named = {b["activity"] for role in acts["schedules"].values()
             for day in role.values() for b in day if "activity" in b}
    named |= {h["activity"] for h in acts["habits"]["hobbies"].values()}
    named |= {c["activity"] for c in acts["habits"]["chores"].values()}
    named |= {c["then"] for c in acts["habits"]["chores"].values() if c.get("then")}
    named |= {o["activity"] for opts in acts["slot_defaults"].values() for o in opts
              if o["activity"] != "none"}
    named |= {b["activity"] for b in acts["habits"]["pet"]["dog"]["blocks"]}
    missing = sorted(named - set(A))
    if missing:
        problems.append(f"activities named but not defined: {missing}")
    # and every surface must be resolvable: a compound room token needs a compound surface
    ok_pairs = {("dining_or_kitchen", "dining_or_kitchen_table"),
                ("balcony_or_living", "balcony_or_side_table")}
    for name, spec in sorted(A.items()):
        room, surf = spec.get("room"), spec.get("surface")
        if room and "_or_" in room and (room, surf) not in ok_pairs:
            problems.append(f"{name}: room {room} with surface {surf} cannot resolve in both")

    if problems:
        print("NOT WRITTEN. Every one of these must be fixed first:")
        for p in problems:
            print("  -", p)
        return 1

    header = __doc__.strip().splitlines()
    text = ("".join(f"# {line}\n" if line else "#\n" for line in header)
            + "# Generated by results/self_improve/varied_homes/make_the_activities.py.\n"
            + "# Edit that script, not this file.\n"
            + yaml.safe_dump(acts, sort_keys=True, default_flow_style=False, width=100))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT} ({len(text.splitlines())} lines, {len(A)} activities)")
    for name in sorted(NEW_ACTIVITIES):
        print(f"  new/replaced activity {name}: {A[name]['room']} / {A[name].get('surface')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
