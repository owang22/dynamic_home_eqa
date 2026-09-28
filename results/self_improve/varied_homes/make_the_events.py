#!/usr/bin/env python3
"""Build varied_homes/scenario/events_varied.yaml: the same illness, moved off the
rooms ordinary life already uses.

Only `unwell_spell` is touched; every other event is copied through untouched and all
of them are switched off by the config anyway, so the illness is the only thing that
changes in the month.

WHAT CHANGED FROM illness_v1's EVENT, and why each change is a fact about the world:

  * the morning dose moves from the bathroom shelf to the bedside. Over ten days the
    pill packet is kept by the bed, not walked to the cabinet - and the bathroom is
    the busiest room in almost every home the generator builds, so a bathroom answer
    was an answer the robot already had.
  * an evening dose on the coffee table, so the medicine is not a single-place fact.
  * breakfast is replaced by a late, small one: the ill resident is not up at 07:35.
  * the going-out and working habits are removed for the ill resident: no bag packed
    by the door, no phone docked in the hall, no desk to clear.
  * the resting places are unchanged from illness_v1 (bedside, bed, sofa, coffee
    table, side table or balcony) and razor, towel and notebook still have no rule at
    all, so they remain controls the illness provably does not touch.
"""
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parent / "scenario" / "events.yaml"
OUT = HERE / "scenario" / "events_varied.yaml"

REMOVE = ["commute_work", "classes", "shift", "work_session", "study", "video_call",
          "walk", "run", "gym", "cycle", "errands", "groceries", "lunch_out",
          "visit_friends", "photo_walk", "yoga",
          # the habits that only make sense if you are going out or working today
          "pack_the_bag", "dock_by_the_door", "desk_wind_down", "crossword_table",
          # THE ILLNESS CONFINES THE RESIDENT. For ten days they do not come to the
          # table, do not cook, do not wash up, do not sit down to the evening's
          # television or hobby and do not read in bed: supper is brought to them and
          # the evening is spent where the afternoon was. This is what makes the change
          # a step instead of a slope. While a mover class was still used by an
          # ordinary bout - a glass at dinner, a book in bed - only about half of the
          # questions asked about it during the illness had the illness place as their
          # answer, because the other half were asked while it was back at the table.
          "breakfast", "breakfast_reading", "lunch", "dinner", "cook_dinner",
          "wash_dishes", "snack", "break", "read", "evening_tv",
          "slot:morning", "slot:late_afternoon", "slot:weekend_morning",
          "slot:weekend_afternoon", "slot:evening"]

ADD = [
    {"activity": "dose_medicine", "room": "bedroom", "start": "08:15", "duration": 20,
     "who": "owner"},
    {"activity": "late_breakfast", "room": "dining_or_kitchen", "start": "08:45",
     "duration": 25, "who": "owner"},
    {"activity": "sip_by_bed", "room": "bedroom", "start": "09:30", "duration": 80,
     "who": "owner", "mean_bouts": 2},
    {"activity": "nap_bed", "room": "bedroom", "start": "11:10", "duration": 90,
     "who": "owner", "mean_bouts": 2},
    {"activity": "rest_coffee", "room": "living", "start": "13:00", "duration": 70,
     "who": "owner", "mean_bouts": 2},
    {"activity": "doze_couch", "room": "living", "start": "14:30", "duration": 100,
     "who": "owner", "mean_bouts": 2},
    {"activity": "sit_quietly", "room": "balcony_or_living", "start": "16:30",
     "duration": 70, "who": "owner"},
    {"activity": "supper_on_a_tray", "room": "living", "start": "19:20",
     "duration": 40, "who": "owner"},
    # the evening stays where the afternoon was, with a hot drink rather than the
    # television: the same room and the same surface as the afternoon's rest.
    {"activity": "rest_coffee", "room": "living", "start": "20:15", "duration": 90,
     "who": "owner", "mean_bouts": 2},
]

PLACEMENT = [
    {"class": "water_bottle", "after": ["any"], "to": "nightstand",
     "note": "drinking more; the bottle lives by the bed now"},
    {"class": "glass", "after": ["any"], "to": "nightstand",
     "note": "a glass of water kept by the bed"},
    {"class": "charger", "after": ["any"], "to": "bed",
     "note": "the phone charges in bed, not at the desk"},
    {"class": "medication", "after": ["any"], "to": "nightstand",
     "note": "the medicine box is kept within reach"},
    {"class": "book", "after": ["doze_couch", "sit_quietly"], "to": "couch",
     "note": "book dropped on the couch"},
    {"class": "glasses", "after": ["doze_couch"], "to": "couch",
     "note": "glasses left in the cushions"},
    {"class": "mug", "after": ["rest_coffee", "dose_evening"], "to": "coffee_table",
     "note": "the tea mug stays by the couch"},
    {"class": "tablet", "after": ["sit_quietly"], "to": "side_table",
     "note": "tablet left on the side table"},
    # razor, towel and notebook have NO rule on purpose: they are the controls.
]


def main():
    events = yaml.safe_load(BASE.read_text())
    problems = []
    if "unwell_spell" not in events["events"]:
        print("no unwell_spell in the base events file")
        return 1
    ev = events["events"]["unwell_spell"]
    acts = yaml.safe_load((HERE / "scenario" / "activities_varied.yaml").read_text())["activities"]

    for a in ADD:
        if a["activity"] not in acts:
            problems.append(f"added activity {a['activity']} is not in activities_varied.yaml")
    for name in REMOVE:
        if not name.startswith("slot:") and name not in acts:
            problems.append(f"removed activity {name} is not in activities_varied.yaml")
    dests = {r["to"] for r in PLACEMENT}
    if len(dests) < 2:
        problems.append("the illness needs at least two destinations")
    controls = {"razor", "towel", "notebook"} & {r["class"] for r in PLACEMENT}
    if controls:
        problems.append(f"the controls {sorted(controls)} have a placement rule")
    # every resting place must be reachable from a bout that actually happens
    bout_rooms = {acts[a["activity"]]["room"] for a in ADD}
    if "bathroom" in bout_rooms:
        problems.append("an illness bout is in the bathroom, the busiest room in most homes")

    # ONE SURFACE PER MOVED CLASS, checked here rather than discovered afterwards.
    # A question is asked in the middle of a bout and the answer is that bout's surface.
    # So if two bouts an ill resident still has use the same class on different surfaces,
    # the answer during the illness is split between them and there is no step change -
    # which is exactly what the first version of this scenario did (a glass at the dining
    # table at dinner and on the nightstand the rest of the day: 42 to 57% either way).
    # Below, every bout the ill resident can still have is enumerated and each moved
    # class must land on exactly one surface.
    full = yaml.safe_load((HERE / "scenario" / "activities_varied.yaml").read_text())
    gone = set(REMOVE)
    gone_slots = {s[5:] for s in REMOVE if s.startswith("slot:")}
    reachable = {a["activity"] for a in ADD}
    for role, days in full["schedules"].items():
        for blocks in days.values():
            for b in blocks:
                if "activity" in b and b["activity"] not in gone:
                    reachable.add(b["activity"])
    for kind in ("hobbies", "chores"):
        for name, spec in full["habits"][kind].items():
            if set(spec["slots"]) - gone_slots and spec["activity"] not in gone:
                reachable.add(spec["activity"])
                if spec.get("then"):
                    reachable.add(spec["then"])
    for slot, opts in full["slot_defaults"].items():
        if slot not in gone_slots:
            for o in opts:
                if o["activity"] != "none" and o["activity"] not in gone:
                    reachable.add(o["activity"])
    for b in full["habits"]["pet"]["dog"]["blocks"]:
        if b["activity"] not in gone:
            reachable.add(b["activity"])

    moved_classes = sorted({r["class"] for r in PLACEMENT})
    surfaces = {c: {} for c in moved_classes}
    for name in sorted(reachable):
        spec = acts.get(name)
        if spec is None or spec.get("surface") is None:
            continue
        for token in spec.get("uses", []):
            for cls in str(token).split("|"):
                if cls in surfaces:
                    surfaces[cls].setdefault(spec["surface"], []).append(name)
    for cls in moved_classes:
        where = surfaces[cls]
        if len(where) > 1:
            detail = "; ".join(f"{s} ({', '.join(a)})" for s, a in sorted(where.items()))
            problems.append(f"an ill resident can use {cls} on more than one surface, so "
                            f"its answer during the illness is split: {detail}")
        elif not where:
            problems.append(f"no bout an ill resident still has uses {cls}, so the "
                            f"illness cannot move it where a question can see it")
    one_surface = {c: (sorted(surfaces[c])[0] if surfaces[c] else None)
                   for c in moved_classes}
    for rule in PLACEMENT:
        if one_surface.get(rule["class"]) != rule["to"]:
            problems.append(f"{rule['class']} rests on {rule['to']} but is used on "
                            f"{one_surface.get(rule['class'])}: the resting place and the "
                            f"surface it is used on must agree, or a night look and a "
                            f"daytime question disagree about where it is")
    if problems:
        print("NOT WRITTEN. Every one of these must be fixed first:")
        for p in problems:
            print("  -", p)
        return 1

    ev["schedule"]["remove"] = list(REMOVE)
    ev["schedule"]["add"] = [dict(a) for a in ADD]
    ev["placement"] = [dict(r) for r in PLACEMENT]
    ev["trace_words"] = ("no work and no trips out; the day is spent between the bed, the "
                         "sofa and a chair by the window, and a different thing is left "
                         "behind in each")
    header = __doc__.strip().splitlines()
    text = ("".join(f"# {line}\n" if line else "#\n" for line in header)
            + "# Generated by results/self_improve/varied_homes/make_the_events.py.\n"
            + "# Edit that script, not this file.\n"
            + yaml.safe_dump(events, sort_keys=True, default_flow_style=False, width=100))
    OUT.write_text(text)
    print(f"wrote {OUT}")
    print(f"  illness bouts in rooms: {sorted(bout_rooms)}")
    print(f"  one surface per moved class: "
          + ", ".join(f"{c}->{s}" for c, s in sorted(one_surface.items())))
    print(f"  destinations: {sorted(dests)}")
    print(f"  classes with no rule (controls): razor, towel, notebook")
    return 0


if __name__ == "__main__":
    sys.exit(main())
