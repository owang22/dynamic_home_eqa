#!/usr/bin/env python3
"""Not pass/fail: which lever in THIS home is the wrong one, and what it is set to.

check_the_lazy_robot.py answers "can a robot that never learns already pass this
scenario?" and prints one number per household. It is right and it stays as it is.
What it does not say is what to change. This script reports, per household, the levers
that decide that number, with the current value of each:

  rooms                 how much house three looks cover. Six rooms means a look
                        covers half the home before anything is learned.
  top-3 share           the share of ALL answers that live in the three busiest
                        rooms. This is the concentration of the people's routines.
  movers                how many asked-about objects the illness moves to a DIFFERENT
                        ROOM: their commonest room in the ordinary fortnight is not
                        their commonest room during the illness. Room, not surface, on
                        purpose - a look opens a room, and every other lever here is
                        measured at room granularity. A towel moving from the towel rail
                        to the bathroom shelf is not a relocation this study can see:
                        the robot opens the bathroom either way. Counting those as
                        movers was rejecting 28 homes on towels and razors wobbling
                        between two surfaces of the same room, which is an artefact of
                        taking the commonest of a split set, not a fact about the world.
  movers landing OUT    of those, how many land in a room OUTSIDE the busiest three.
                        It is the difference between a home where memory can show
                        something and a home where the illness pushes things exactly
                        where the robot was already going to look.
  questions inside      the same thing counted over the QUESTIONS rather than the
                        objects. One moved object that lands back in a busy room can
                        carry more questions than the other five put together. This is
                        the number check_the_lazy_robot.py prints in its last column.
  THE STEP: leak and switch.
                        Whether the illness is a relocation or only a change of
                        frequency. Per moved object:
                          leak   - of the ordinary-fortnight questions about it, how
                                   often the answer is ALREADY its illness place.
                          switch - of the illness-window questions about it, how often
                                   the answer IS its illness place.
                        A slope rather than a step is what blunts every "did it notice
                        the change" measure in the project: if a thing is already on the
                        nightstand two days in five before the illness, there is no
                        break to notice. Required per object: leak under 10%, switch
                        over 70%, and every mover must clear both.

Every number here is a property of the WORLD - the floor plan, the residents'
routines, where the illness puts things, and when. Not one of them is any method's
score, so selecting on them cannot select for a method.

    python3 results/self_improve/varied_homes/which_lever_is_wrong.py results/self_improve/runs/illness_v1
    python3 ... <run_dir> --sim data/situation_sim/self_improve/illness_v1   # adds roles
    python3 ... <run_dir> --json out.json --curve      # the day-by-day step, days 10-19
"""
import argparse
import collections
import json
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
from self_improve.frozen_household import FrozenHousehold  # noqa: E402

ROOMS_A_LOOK_OPENS = 3

# The bars. Each is a property of the world; the justification is beside it.
MIN_ROOMS = 7           # every six-room home in illness_v1 failed the lazy robot: three
                        # looks cover half of a six-room house before anything is learned.
MAX_TOP3_SHARE = 0.88   # above this the routines are so concentrated that even a mover
                        # landing outside the top three is asked about too rarely to matter.
MIN_MOVERS = 3          # under three moved objects the illness barely happened here.
MIN_OUT_SHARE = 0.50    # at least half the moved objects must land outside the busiest
                        # three rooms. This is the lever the lazy robot's number tracks.
MIN_CONTROLS = 3        # asked-about objects the illness provably does not move.
MAX_QUESTIONS_INSIDE = 0.50  # of the disrupted-window questions about moved objects, at
                        # most half may be answered by one of the busiest three rooms.
                        # The same bar, on the same number, as
                        # check_the_lazy_robot.LAZY_ROBOT_ON_MOVERS_MUST_BE_UNDER, so
                        # this gate can never keep a home that one would reject.
MAX_LEAK = 0.10         # the illness place may be the answer in ordinary life at most
MIN_SWITCH = 0.70       # this often, and must be the answer during the illness at least
                        # this often. Set by the coordinator from what the illness_v1
                        # homes showed by eye: in hh_s1 the "moved" objects were already
                        # at their illness place 37-42% of the ordinary days and only
                        # 48% of the first illness day, a ten-point slope with no step
                        # in it at all.

SETTLED, DISRUPTED = range(1, 14), range(14, 24)
CURVE_DAYS = range(10, 20)      # the days either side of the change, for reading by eye


def room_of(household, place):
    rooms = household.place_room
    return rooms.get(place) if isinstance(rooms, dict) else rooms(place)


def modal_place_per_object(household, days):
    counts = collections.defaultdict(collections.Counter)
    for day in days:
        for question in household.questions_on_day(day):
            true_place = household.true_place_for_question(question)
            if true_place:
                counts[question["object_id"]][true_place] += 1
    return {o: c.most_common(1)[0][0] for o, c in counts.items() if c}


def answers_by_day(household):
    """day -> list of (object, true place). Computed once; three passes need it."""
    out = {}
    for day in range(1, household.n_days + 1):
        rows = []
        for question in household.questions_on_day(day):
            true_place = household.true_place_for_question(question)
            if true_place:
                rows.append((question["object_id"], true_place))
        out[day] = rows
    return out


def levers(household):
    """Every lever for one home, plus the day-by-day step."""
    by_day = answers_by_day(household)
    everything = collections.Counter()
    for rows in by_day.values():
        for _, place in rows:
            everything[room_of(household, place)] += 1
    total = sum(everything.values())
    busiest = [room for room, _ in everything.most_common(ROOMS_A_LOOK_OPENS)]
    top3_n = sum(everything[r] for r in busiest)

    settled = modal_place_per_object(household, SETTLED)
    disrupted = modal_place_per_object(household, DISRUPTED)
    # A MOVER IS AN OBJECT THE ILLNESS PUTS IN A DIFFERENT ROOM. See the header: room
    # rather than surface, so the definition matches the granularity of every other
    # lever, and an object that never leaves its room is a control rather than a mover.
    movers = sorted(o for o in settled if o in disrupted
                    and room_of(household, settled[o]) != room_of(household, disrupted[o]))
    controls = sorted(o for o in settled if o in disrupted
                      and room_of(household, settled[o]) == room_of(household, disrupted[o]))
    out = [o for o in movers if room_of(household, disrupted[o]) not in busiest]
    dest_rooms = collections.Counter(room_of(household, disrupted[o]) for o in movers)

    # the step, object by object
    step = {}
    for obj in movers:
        ill = disrupted[obj]
        leak_hits = leak_n = switch_hits = switch_n = 0
        for day in SETTLED:
            for o, place in by_day[day]:
                if o == obj:
                    leak_n += 1
                    leak_hits += place == ill
        for day in DISRUPTED:
            for o, place in by_day[day]:
                if o == obj:
                    switch_n += 1
                    switch_hits += place == ill
        step[obj] = {"illness_place": ill,
                     "settled_place": settled[obj],
                     "class": household.object_class.get(obj, "?"),
                     "leak": leak_hits / leak_n if leak_n else None,
                     "switch": switch_hits / switch_n if switch_n else None,
                     "settled_questions": leak_n, "illness_questions": switch_n}
    leaky = [(v["leak"], o) for o, v in step.items() if v["leak"] is not None]
    slow = [(v["switch"], o) for o, v in step.items() if v["switch"] is not None]

    # the curve a reader judges by eye: of the questions asked about moved objects on
    # this day, what share are answered by that object's illness place
    curve = {}
    for day in CURVE_DAYS:
        hits = n = 0
        for o, place in by_day.get(day, []):
            if o in step:
                n += 1
                hits += place == step[o]["illness_place"]
        curve[day] = (hits / n if n else None, n)

    mover_hits = mover_n = 0
    for day in DISRUPTED:
        for o, place in by_day[day]:
            if o in movers:
                mover_n += 1
                mover_hits += room_of(household, place) in busiest
    return {
        "household": household.name,
        "rooms": len(household.rooms),
        "room_names": list(household.rooms),
        "busiest": busiest,
        "top3_share": top3_n / total if total else None,
        "asked_objects": len(household.asked_objects),
        "n_movers": len(movers),
        "n_movers_out": len(out),
        "out_share": len(out) / len(movers) if movers else None,
        "movers_out": out,
        "movers_that_stay_inside": [o for o in movers if o not in out],
        "n_controls": len(controls),
        "destination_rooms": dict(dest_rooms.most_common()),
        "lazy_on_movers": mover_hits / mover_n if mover_n else None,
        "questions_on_movers_disrupted": mover_n,
        "step": step,
        "worst_leak": max(leaky) if leaky else None,
        "worst_switch": min(slow) if slow else None,
        "n_movers_that_step": sum(1 for v in step.values()
                                  if v["leak"] is not None and v["switch"] is not None
                                  and v["leak"] < MAX_LEAK and v["switch"] > MIN_SWITCH),
        "curve": curve,
    }


def verdict(row):
    """The sentence naming the lever that is wrong, worst lever first, or None."""
    if row["rooms"] < MIN_ROOMS:
        return ("rooms", f"only {row['rooms']} rooms, so three looks already cover "
                f"{ROOMS_A_LOOK_OPENS / row['rooms'] * 100:.0f}% of the house before "
                f"anything is learned. Needs at least {MIN_ROOMS}.")
    if row["n_movers"] < MIN_MOVERS:
        return ("movers", f"the illness moves only {row['n_movers']} asked-about "
                f"object(s) (needs {MIN_MOVERS}): there is almost no change to learn.")
    if row["out_share"] is not None and row["out_share"] < MIN_OUT_SHARE:
        inside = row["n_movers"] - row["n_movers_out"]
        return ("destinations", f"{inside} of {row['n_movers']} moved objects land back "
                f"inside the busiest three rooms ({', '.join(row['busiest'])}), so the "
                f"robot was going to open them anyway. Only "
                f"{row['out_share'] * 100:.0f}% land outside; needs "
                f"{MIN_OUT_SHARE * 100:.0f}%.")
    if (row["lazy_on_movers"] is not None
            and row["lazy_on_movers"] >= MAX_QUESTIONS_INSIDE):
        return ("questions_inside", f"{row['lazy_on_movers'] * 100:.0f}% of the "
                f"questions asked about moved objects during the illness are answered "
                f"by one of the busiest three rooms (bar: "
                f"{MAX_QUESTIONS_INSIDE * 100:.0f}%). "
                f"{row['n_movers_out']} of {row['n_movers']} moved objects land "
                f"outside, but the ones that land inside carry most of the questions, "
                f"so move THOSE objects' destinations out: "
                f"{', '.join(sorted(set(row['movers_that_stay_inside'])))}.")
    if row["worst_leak"] and row["worst_leak"][0] >= MAX_LEAK:
        leak, obj = row["worst_leak"]
        s = row["step"][obj]
        return ("leak", f"{obj} is already at its illness place ({s['illness_place']}) "
                f"in {leak * 100:.0f}% of the ordinary-fortnight questions about it "
                f"(bar: under {MAX_LEAK * 100:.0f}%). Its usual place is "
                f"{s['settled_place']}, so for this object the illness is a change of "
                f"frequency, not a relocation: either ordinary life must stop using "
                f"that surface, or this object has no one usual place to begin with.")
    if row["worst_switch"] and row["worst_switch"][0] <= MIN_SWITCH:
        switch, obj = row["worst_switch"]
        s = row["step"][obj]
        return ("switch", f"{obj} is at its illness place ({s['illness_place']}) in only "
                f"{switch * 100:.0f}% of the questions asked about it during the illness "
                f"(bar: over {MIN_SWITCH * 100:.0f}%). The other answers are elsewhere, "
                f"so the illness shares this object with a bout it still has: take that "
                f"bout away from the ill resident, or the change is a slope.")
    if row["top3_share"] is not None and row["top3_share"] > MAX_TOP3_SHARE:
        return ("concentration", f"the busiest three rooms hold "
                f"{row['top3_share'] * 100:.0f}% of every answer in the month "
                f"(bar: {MAX_TOP3_SHARE * 100:.0f}%): the residents' routines are "
                f"piled into the same rooms, so spread their hours and rooms apart.")
    if row["n_controls"] < MIN_CONTROLS:
        return ("controls", f"only {row['n_controls']} asked-about object(s) stay put "
                f"(needs {MIN_CONTROLS}), so 'did it get worse on the things that "
                f"moved specifically' has nothing to compare against.")
    return None


def roles_from_sim(sim_dir, name):
    """Residents' roles, for reading only: they are not part of any bar."""
    if not sim_dir:
        return None
    seed = name.split("_")[1] if "_" in name else name
    path = pathlib.Path(sim_dir) / f"hh_{seed}" / "hidden_state.json"
    if not path.exists():
        return None
    hh = json.loads(path.read_text())["household"]
    return {"household_type": hh["household_type"],
            "roles": [r["role"] for r in hh["residents"].values()],
            "bedrooms": [r["bedroom"] for r in hh["residents"].values()],
            "workspaces": [r["workspace"] for r in hh["residents"].values()]}


def print_curve(rows, title):
    """The table Oliver reads: near zero before day 14, a step up on it."""
    days = list(CURVE_DAYS)
    print(f"\n{title}")
    print("  of the questions asked about moved objects on that day, the share already "
          "answered by\n  that object's illness place. The illness begins on day 14.")
    print("  " + f"{'home':11s}" + "".join(f"{('d' + str(d)):>7}" for d in days)
          + "   step (d14-16 mean minus d10-13 mean)")
    print("  " + "-" * (11 + 7 * len(days) + 40))
    steps = []
    for row in rows:
        cells = []
        for d in days:
            share, n = row["curve"].get(d, (None, 0))
            cells.append("     -" if share is None else f"{share*100:>6.0f}%")
        before = [row["curve"][d][0] for d in (10, 11, 12, 13)
                  if row["curve"].get(d, (None,))[0] is not None]
        after = [row["curve"][d][0] for d in (14, 15, 16)
                 if row["curve"].get(d, (None,))[0] is not None]
        step = (statistics.mean(after) - statistics.mean(before)
                if before and after else None)
        if step is not None:
            steps.append(step)
        print("  " + f"{row['household'].replace('_t03',''):11s}"
              + "".join(f"{c:>7}" for c in cells)
              + (f"   {step*100:+5.0f} points" if step is not None else "   -"))
    if steps:
        print(f"\n  step over homes: median {statistics.median(steps)*100:+.0f} points, "
              f"range {min(steps)*100:+.0f} to {max(steps)*100:+.0f}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--sim", default=None, help="the sim_dir, to print residents' roles")
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--curve", action="store_true",
                    help="also print the day-by-day step for the homes that pass")
    ap.add_argument("--quiet", action="store_true", help="skip the home-by-home sentences")
    a = ap.parse_args(argv)

    banks = pathlib.Path(a.run_dir) / "banks"
    if not banks.is_dir():
        print(f"no banks directory under {a.run_dir}")
        return 2

    rows = []
    for bank in sorted(banks.glob("*.jsonl"), key=lambda p: int(p.stem.split("_")[1][1:])):
        household = FrozenHousehold(bank)
        row = levers(household)
        row["who"] = roles_from_sim(a.sim, row["household"])
        bad = verdict(row)
        row["failing_lever"] = bad[0] if bad else None
        row["why"] = bad[1] if bad else None
        rows.append(row)

    print("WHICH LEVER IS WRONG. Every column is a property of the world, never of a "
          "method's score.\n")
    print(f"the bars: rooms >= {MIN_ROOMS}; movers >= {MIN_MOVERS}; of the movers, "
          f">= {MIN_OUT_SHARE*100:.0f}% land outside the busiest three rooms;")
    print(f"          the busiest three hold <= {MAX_TOP3_SHARE*100:.0f}% of all "
          f"answers; >= {MIN_CONTROLS} control objects that do not move;")
    print(f"          of the questions about moved objects during the illness, "
          f"<= {MAX_QUESTIONS_INSIDE*100:.0f}% are answered by a busiest-three room;")
    print(f"          and EVERY mover has leak < {MAX_LEAK*100:.0f}% and switch > "
          f"{MIN_SWITCH*100:.0f}%.\n")
    head = (f"{'household':11s}{'rooms':>6}{'top-3':>7}{'asked':>7}{'movers':>8}"
            f"{'OUT':>7}{'ctrl':>6}{'q inside':>10}{'worst leak':>12}"
            f"{'worst switch':>14}{'step':>6}  lever")
    print(head)
    print("-" * len(head))
    for row in rows:
        lazy = ("-" if row["lazy_on_movers"] is None
                else f"{row['lazy_on_movers']*100:.0f}%")
        wl = ("-" if not row["worst_leak"] else f"{row['worst_leak'][0]*100:.0f}%")
        ws = ("-" if not row["worst_switch"] else f"{row['worst_switch'][0]*100:.0f}%")
        print(f"{row['household'].replace('_t03',''):11s}{row['rooms']:>6}"
              f"{row['top3_share']*100:>6.0f}%{row['asked_objects']:>7}"
              f"{row['n_movers']:>8}"
              f"{str(row['n_movers_out']) + '/' + str(row['n_movers']):>7}"
              f"{row['n_controls']:>6}{lazy:>10}{wl:>12}{ws:>14}"
              f"{row['n_movers_that_step']:>6}  {row['failing_lever'] or 'ok'}")

    if not a.quiet:
        print("\nwhat to change, home by home:")
        for row in rows:
            tag = row["household"].replace("_t03", "")
            who = row["who"]
            whom = ("" if not who else
                    f"  [{who['household_type']}: {', '.join(who['roles'])}"
                    f"{'; both in ' + who['bedrooms'][0] if len(set(who['bedrooms'])) == 1 else ''}]")
            if row["why"]:
                print(f"  {tag}: {row['why']}{whom}")
            else:
                print(f"  {tag}: every lever in range. busiest three "
                      f"{', '.join(row['busiest'])} hold {row['top3_share']*100:.0f}%; "
                      f"movers land in {', '.join(row['destination_rooms'])}; every "
                      f"mover steps.{whom}")

    passed = [r for r in rows if r["failing_lever"] is None]
    by_lever = collections.Counter(r["failing_lever"] for r in rows if r["failing_lever"])
    print(f"\n{len(passed)} of {len(rows)} homes have every lever in range.")
    if by_lever:
        print("failing lever, counted: " +
              ", ".join(f"{k} x{v}" for k, v in by_lever.most_common()))
    outs = [r["out_share"] for r in rows if r["out_share"] is not None]
    if outs:
        print(f"share of movers landing outside the busiest three: median "
              f"{statistics.median(outs)*100:.0f}%, "
              f"range {min(outs)*100:.0f}-{max(outs)*100:.0f}%")
    leaks = [v["leak"] for r in rows for v in r["step"].values() if v["leak"] is not None]
    sws = [v["switch"] for r in rows for v in r["step"].values() if v["switch"] is not None]
    if leaks:
        print(f"per-object leak:   median {statistics.median(leaks)*100:.0f}%, "
              f"{sum(x < MAX_LEAK for x in leaks)} of {len(leaks)} objects under "
              f"{MAX_LEAK*100:.0f}%")
        print(f"per-object switch: median {statistics.median(sws)*100:.0f}%, "
              f"{sum(x > MIN_SWITCH for x in sws)} of {len(sws)} objects over "
              f"{MIN_SWITCH*100:.0f}%")
    if a.curve:
        print_curve(passed or rows, "THE STEP, DAY BY DAY"
                    + (" (the homes that pass)" if passed else " (nothing passed)"))

    if a.json_out:
        pathlib.Path(a.json_out).write_text(json.dumps(
            {"run_dir": str(a.run_dir), "bars": {
                "min_rooms": MIN_ROOMS, "max_top3_share": MAX_TOP3_SHARE,
                "min_movers": MIN_MOVERS, "min_out_share": MIN_OUT_SHARE,
                "min_controls": MIN_CONTROLS,
                "max_questions_inside": MAX_QUESTIONS_INSIDE,
                "max_leak_per_mover": MAX_LEAK, "min_switch_per_mover": MIN_SWITCH},
             "n_homes": len(rows), "n_passed": len(passed), "homes": rows}, indent=2))
        print(f"wrote {a.json_out}")
    return 0 if len(passed) == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
