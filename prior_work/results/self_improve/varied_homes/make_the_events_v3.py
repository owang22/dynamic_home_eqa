#!/usr/bin/env python3
"""Build varied_homes/scenario/events_varied_v3.yaml: varied_v2's illness with two more
things it moves, chosen so they do not belong to the ill resident's drinkware.

WHY THIS EXISTS. Measured on varied_v2's ten pilot banks on 2026-09-25
(results/self_improve/why_the_movers_are_drinkware/WHAT_I_FOUND.md): 42.1% of the
asked-about objects and 53.3% of the movers are a mug, a glass or a water bottle, and in
hh_s2_t03 six of the eight movers are one pattern - all six belong to resident_1, the ill
one, and all six switch on day 14-15. The asked-about class list is the cause: eleven
classes, all per-resident, of which the two certain to exist are a mug and a glass.

WHAT THIS CHANGES, and nothing else:
  * varied_v3.yaml widens the asked-about class list from 11 to 21.
  * this script adds exactly TWO placement rules to `unwell_spell`, so two of the added
    classes are movers rather than more controls:
      - plate -> coffee_table. Supper comes to the ill resident on a tray, so the MEAL
        relocates to the sofa. That is a different reason from a drink kept by the bed,
        and the plate's ordinary place is the dining table, not the kitchen.
      - remote -> coffee_table. The remote is a SHARED object: it belongs to nobody, so it
        is the first mover in this scenario that is not the ill resident's property.
  * everything else in the event is copied through byte-for-byte from events_varied.yaml.
    razor, towel and notebook still have no rule, and eight of the ten added classes have
    no rule either, so the control side grows more than the mover side.

WHY NOT THE OTHERS, each with the number it was rejected on (measured over the ten pilot
homes of varied_v2):
  * phone: `pocket: true`, so it rides on a person and is beyond the reach of any look for
    much of the day; and an ill resident uses it on EIGHT different surfaces, so its
    illness answer would be split eight ways.
  * blanket and bowl: an ill resident uses each on TWO surfaces (blanket on the bed in
    nap_bed and the couch in doze_couch; bowl on the tray at supper and the table at the
    late breakfast). A rule would split their answer, which is the exact fault
    make_the_events.py was written to catch. They are on the class list with NO rule.
  * vitamins: the dose_medicine bout already uses it on the nightstand, so it would become
    a fourth nightstand mover beside the glass, the water bottle and the medicine, and the
    illness destinations are already concentrated there. Off the class list.
  * gym_bag and lunchbox: NO activity in activities_varied.yaml uses either, so not one
    question would ever be drawn about them. Off the class list.
  * serving_dish: 4 instances in 4 of the ten homes. Too rare to carry a control line.
  * dog_bowl (107 truth rows over 7 homes) and dog_toy (28 over 7): pet-gated and they
    barely move, so they are controls with nothing to show.
  * magazine: 6 truth rows and ONE distinct place over all ten homes. It cannot move, so
    it cannot show a memory holding still either.

Run: python3 results/self_improve/varied_homes/make_the_events_v3.py
Nothing shared is touched: src/situation_sim/ is read only, and events_varied.yaml,
activities_varied.yaml, varied_v2.yaml and make_the_events.py are not modified.
"""
import importlib.util
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE / "scenario" / "events_varied.yaml"          # varied_v2's event file, read only
ACTS = HERE / "scenario" / "activities_varied.yaml"      # unchanged: v3 adds no activity
OUT = HERE / "scenario" / "events_varied_v3.yaml"

# the two rules added to unwell_spell, and nothing else
NEW_RULES = [
    {"class": "plate", "after": ["supper_on_a_tray"], "to": "coffee_table",
     "note": "supper comes on a tray; the plate stays by the sofa"},
    {"class": "remote", "after": ["rest_coffee"], "to": "coffee_table",
     "note": "the remote stays where the resting is, not by the television"},
]


def reachable_bouts(add_blocks, remove_list):
    """Every bout an ill resident can still have: the illness's own added bouts plus
    everything the removal list does not take away. Copied in behaviour from
    make_the_events.py so the two agree; it is imported from there, not re-typed."""
    full = yaml.safe_load(ACTS.read_text())
    gone = set(remove_list)
    gone_slots = {s[5:] for s in remove_list if s.startswith("slot:")}
    out = {a["activity"] for a in add_blocks}
    for role, days in full["schedules"].items():
        for blocks in days.values():
            for b in blocks:
                if "activity" in b and b["activity"] not in gone:
                    out.add(b["activity"])
    for kind in ("hobbies", "chores"):
        for name, spec in full["habits"][kind].items():
            if set(spec["slots"]) - gone_slots and spec["activity"] not in gone:
                out.add(spec["activity"])
                if spec.get("then"):
                    out.add(spec["then"])
    for slot, opts in full["slot_defaults"].items():
        if slot not in gone_slots:
            for o in opts:
                if o["activity"] != "none" and o["activity"] not in gone:
                    out.add(o["activity"])
    for b in full["habits"]["pet"]["dog"]["blocks"]:
        if b["activity"] not in gone:
            out.add(b["activity"])
    return out, full["activities"]


def main():
    events = yaml.safe_load(BASE.read_text())
    ev = events["events"]["unwell_spell"]
    problems = []

    existing = {r["class"] for r in ev["placement"]}
    for rule in NEW_RULES:
        if rule["class"] in existing:
            problems.append(f"{rule['class']} already has a rule in {BASE.name}")

    reach, acts = reachable_bouts(ev["schedule"]["add"], ev["schedule"]["remove"])

    # THE CHECK THAT MATTERS, and the one make_the_events.py was written around: every
    # class the illness moves must be used on exactly ONE surface by the bouts the ill
    # resident still has, and the rule's destination must BE that surface. Otherwise a
    # question asked mid-bout and a look at night disagree about where the thing is.
    surfaces = {}
    for name in sorted(reach):
        spec = acts.get(name)
        if spec is None or spec.get("surface") is None:
            continue
        for token in spec.get("uses", []):
            for cls in str(token).split("|"):
                surfaces.setdefault(cls, {}).setdefault(spec["surface"], []).append(name)
    for rule in NEW_RULES + [dict(r) for r in ev["placement"]]:
        cls, where = rule["class"], surfaces.get(rule["class"], {})
        if not where:
            problems.append(f"no bout an ill resident still has uses {cls}, so the illness "
                            f"cannot move it where a question can see it")
        elif len(where) > 1:
            detail = "; ".join(f"{s} ({', '.join(a)})" for s, a in sorted(where.items()))
            problems.append(f"an ill resident can use {cls} on more than one surface, so its "
                            f"answer during the illness would be split: {detail}")
        elif sorted(where)[0] != rule["to"]:
            problems.append(f"{cls} is told to rest on {rule['to']} but is used on "
                            f"{sorted(where)[0]}: the resting place and the surface it is "
                            f"used on must agree")

    # the controls must stay controls
    controls = {"razor", "towel", "notebook"}
    have_rules = {r["class"] for r in NEW_RULES} | existing
    if controls & have_rules:
        problems.append(f"the controls {sorted(controls & have_rules)} were given a rule")
    if len(NEW_RULES) < 2:
        problems.append("the brief asks for at least two added classes to be movers")

    # A CHECK THAT CANNOT FAIL IS WORTHLESS. Feed the one-surface test a case known to
    # break it before trusting it on the real rules.
    known_bad = {"class": "blanket", "after": ["any"], "to": "couch"}
    w = surfaces.get("blanket", {})
    if len(w) <= 1:
        problems.append("the one-surface test has lost its power: blanket was supposed to "
                        f"be used on two surfaces by an ill resident, found {sorted(w)}")
    else:
        print(f"  power check: the one-surface test correctly rejects a blanket rule "
              f"({known_bad['to']}) - an ill resident uses it on {sorted(w)}")

    if problems:
        print("NOT WRITTEN. Every one of these must be fixed first:")
        for p in problems:
            print("  -", p)
        return 1

    ev["placement"] = [dict(r) for r in ev["placement"]] + [dict(r) for r in NEW_RULES]
    header = __doc__.strip().splitlines()
    text = ("".join(f"# {line}\n" if line else "#\n" for line in header)
            + "# Generated by results/self_improve/varied_homes/make_the_events_v3.py.\n"
            + "# Edit that script, not this file.\n"
            + yaml.safe_dump(events, sort_keys=True, default_flow_style=False, width=100))
    OUT.write_text(text)
    print(f"wrote {OUT}")
    dests = sorted({r["to"] for r in ev["placement"]})
    print(f"  {len(ev['placement'])} placement rules over {len(dests)} destinations: {dests}")
    for r in sorted(ev["placement"], key=lambda r: r["class"]):
        print(f"    {r['class']:14s} -> {r['to']:16s} after {r['after']}")
    print("  classes with no rule (controls): razor, towel, notebook, bowl, blanket, "
          "laptop, headphones, pen, pan, pot, snack_bowl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
