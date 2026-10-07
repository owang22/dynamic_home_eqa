#!/usr/bin/env python3
"""Can a plain counting method be taught by this scenario, and then broken by it?

This is a gate, not a report. A scenario only deserves a night of GPU time if the
disruption is visible in the data with no language model anywhere near it. Two cheap
counting methods are run over the scenario's own question banks, and their accuracy
is followed through the four phases the calendar defines:

    learn        the settled window            accuracy climbs and reaches a decent level
    break        the first days of the upset    accuracy falls sharply
    re-learn     the rest of the upset          accuracy climbs back materially
    break again  the first days after the upset accuracy falls again

    python3 results/self_improve/check_classical_curve.py results/self_improve/runs/illness_v2

If a counting method shows no break, THE SCENARIO HAS FAILED, NOT THE METHOD. There
is then nothing in the data for a language model to notice, and any difference between
memory designs measured on it is noise or leakage. The output says this in as many
words, because a reader who skims the table will otherwise blame the method.

THE FOURTH LEG DOES NOT STAND ALONE. A drop at the return only means "a memory adopted
the upset and is now wrong again" in a scenario where something was adopted. Read on its
own it can be satisfied by the disrupted window merely having been an EASIER prediction
problem: the purpose-built night-shift control, which changes when things happen and not
where they end up, has no first break at all (+0.1 and +2.5 points, the wrong sign) and
yet its forgetting learner climbs straight through the disruption, 61.5 -> 69.2 -> 71.7
-> 75.7, and then loses 7.6 points on the first two days back, because a late shift's
weekday has no cooking and no dinner in it and fewer free slots to be wrong about. So:

  - the fourth leg is COUNTED ONLY IF THE BREAK LEG PASSED. Otherwise it is printed,
    labelled uninterpretable, and left out of the verdict either way.
  - the objects the upset never touched are printed beside it every time. On that
    night-shift control they drop 7.0 against the movers' 7.x - the control carries the
    whole leg, which is the signature of a difficulty change. On illness_v2 they move
    the OTHER way (+4.6 against the movers' -15.7), which is the signature of a memory
    losing a routine.

HOW DEEP IS A VERDICT? Every leg is recomputed with each object class left out in turn,
and the report says whether any single class decides the answer. This costs no extra
replay - the class sits in the leaf of the tally. It exists because a scenario's class
list can be tuned until it passes: a class that hardly moves buys about 5 points of
settled level and costs 6 to 9 points of break, so a dozen tries will find a mix that
clears every bar. The gate cannot tell that it was tuned, but it can refuse to let a
one-class-deep verdict be quoted without the caveat, and a scenario whose class list was
chosen against this gate is not independently tested by it. Floors (settled level, learn)
and discriminating legs (break, re-learn, break again) are named separately, because a
verdict whose FLOORS rest on one class is fragile while one whose BREAK does was, for
practical purposes, chosen.

ARE THE THRESHOLDS CARRYING THE VERDICT? Every bar here was set from what one scenario
and two older ones showed, so the last report moves all of them together - the four leg
bars and the settled-level floor - two points stricter and two points more lenient at
once, and says whether the verdict survives. Of the six scenarios that have been through
this gate, four are unchanged in both directions (illness_v1 passes throughout without a
single leg even changing state; illness_v2, the night-shift control and the
work-from-home scenario fail throughout). Two turn on the bars and must not be quoted
without saying so: the bathroom refit passes as set but fails two points stricter, on its
settled level alone, and the guest scenario fails as set but passes two points more
lenient, also on its settled level - it is 0.8 points of settled level short, which is a
near miss rather than a rejection.

THE TWO METHODS, and why these two.

  a timetable that never forgets - for each object, count every past sighting by the
  room it was in and the two-hour slot of the day it was seen in, weight every sighting
  equally however old it is, and answer with the most-counted room for the slot the
  question asks about. It is the yardstick for "is there a routine here at all": it
  cannot be misled by a passing fashion, and it cannot be broken by a return to the
  routine it never stopped believing in.

  a timetable with a three-day memory - the same counting, except a sighting's weight
  halves every three days, so anything older than about a week barely counts. It is the
  yardstick for "is the upset a new routine, learnable in ten days": it is the one that
  can be broken twice, once by the upset and once by the return.

Both are the repository's own TimetableLookup (src/baselines/beliefs/timetable.py) driven
through the same replay loop the paper's classical numbers come from
(baselines.patrol.run.run_belief), at the two-hour binning the earlier regime search
reported. Nothing is reimplemented here: a counting method that differed by a hair from
the one the paper reports would be worse than useless.

WHICH QUESTIONS THE CURVE IS MEASURED OVER. Three slices, printed side by side:

  all            every question. This is the paper's own metric and the one the
                 thresholds below are set on. It is unbiased, and it is dilute: the
                 objects the upset moves are a minority of the objects asked about, so
                 a 30-point swing on them shows up as a 10-point swing here.
  moved          questions about the objects whose usual place differs between the
                 settled and the disrupted window. Sharper, but SELECTION-BIASED, and
                 not gated on: the set is chosen by comparing the two windows, so
                 ordinary noise puts objects into it, and they then show a break by
                 construction. How large that bias is turns out to be a property of the
                 scenario rather than of the measure: the old night-shift scenario at
                 results/regime_search/nightshift shows a 16-point "break" on its moved
                 slice with almost nothing moving, while the purpose-built night-shift
                 control, which changes only when activities happen and not where they
                 end up, shows -0.2 there. So the slice is worth reading; it just cannot
                 be the thing a verdict rests on.
  stayed put     everything else. It is the control, and it is why the pooled fourth
                 leg can vanish: at the return the moved objects break while the ones
                 that stayed put recover, and the two cancel.

CLUSTERING. Every interval is clustered on household. Per-question intervals in this
project come out roughly four times too narrow, because twenty questions about one
object in one household are not twenty observations. The right summary of a leg is the
pooled size, the household-clustered standard error, and the number of households
that show the leg at all - a pooled curve can look perfect when two households carry
it and eight are flat.

HOUSEHOLD EXCLUSION. Same rule as check_scenario.py: a household where fewer than two
asked-about objects change their usual place is a household where the event did not
happen. Dropped by rule, named in the output, every other number computed without it.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from check_scenario import (MIN_MOVERS_TO_KEEP_HH, Bank, guess_stages,  # noqa: E402
                            modal_place)

# ---------------------------------------------------------------- the methods

METHODS = (
    ("a timetable that never forgets",
     {"name": "timetable", "bin_hours": 2}),
    ("a timetable with a three-day memory",
     {"name": "timetable", "bin_hours": 2, "half_life_h": 72.0}),
)
SHORT = {"a timetable that never forgets": "never forgets",
         "a timetable with a three-day memory": "three-day memory"}
"""Only for squeezing a method's name into a narrow column. The full name is what the
tables and the failure messages use."""

FORGETS = "a timetable with a three-day memory"
"""The method that can be broken twice. The never-forgetting one cannot be broken by
the return, by construction, so the fourth leg is not asked of it."""

LOOK = "off"
"""No free look. The methods see the nightly walkthrough and the answer feedback the
bank already records, and nothing else, so the curve is a property of the scenario
rather than of a search policy."""

# ---------------------------------------------------------------- phase windows

EARLY_DAYS = 2
"""The first scored days of the settled window: where the learner starts from."""

SETTLED_REFERENCE_DAYS = 3
"""The last days of the settled window: what the learner has learnt. Three days is
about 70 questions per household, enough that the reference is not itself noise."""

BREAK_DAYS = 2
"""How many days of a window count as "the first days" of it. One day is about 24
questions per household (household-clustered error about 10 points); two is about 48
(about 7 points); three already starts to include the re-learning, which shrinks the
measured break - on illness_v2 the never-forgetting method's break reads 11.8 points
over one day, 10.1 over two and 9.7 over three. Two is the compromise."""

RELEARN_REFERENCE_DAYS = 3
"""The last days of the disrupted window: how far the learner got by the end of it."""

# ---------------------------------------------------------------- thresholds
#
# Every number below is set on the "all questions" slice, from what the settled
# scenario actually shows, and checked against two scenarios with known answers:
# results/regime_search/sick10_partial, the earlier regime search's chosen scenario,
# which shows all four legs; and results/regime_search/nightshift, which barely
# disturbs the household and must not pass.

MIN_SETTLED_LEVEL = 0.70
# The last settled days must reach 70%. Not a discriminator, a floor: it only excludes
# a scenario whose ordinary routine cannot be learnt at all, and a scenario that fails
# it cannot lose anything at the upset either. Both methods clear it comfortably
# everywhere we have measured (illness_v2 81 and 77, nightshift 75 and 72,
# sick10_partial 78 and 73), which is what a floor should look like.

MIN_CLIMB = 10.0
# The settled level must beat the learner's own first two days by 10 points, or the
# routine is not being learnt and the "learn" leg is an artefact of where the learner
# started. Measured: 17 and 14 on illness_v2, 24 and 21 on sick10_partial. A counting
# method with no timetable at all (plain most-frequent) reads about -2 here, which is
# the shape this threshold is meant to catch.

MIN_BREAK = 8.0
# The first two disrupted days must cost 8 points against the settled level. This is
# the load-bearing threshold and the one that separates a real upset from a cosmetic
# one: illness_v2 reads 10.1 and 10.2, sick10_partial 24.5 and 22.4, and the
# night-shift control 6.0 and 4.1. The margin over the control is only about 4 points
# against a household-clustered error of 2 to 5, so this threshold is permissive and a
# scenario that only just clears it should be treated as thin, not as proven.

MIN_RELEARN = 5.0
# From the first two disrupted days to the last three, accuracy must climb back 5
# points, or the upset is a shock rather than a new routine and there is nothing in it
# for a memory to learn. Measured: 5.0 and 7.4 on illness_v2, 23.4 and 31.1 on
# sick10_partial, 5.3 and 4.7 on the night-shift control. Five points is about two
# household-clustered standard errors on this leg, this project's standing bar for
# claiming an effect at all, and no lower bar would mean anything.

MIN_SECOND_BREAK = 5.0
# The first two days after the return must cost the FORGETTING method 5 points against
# the end of the disrupted window. Asked of that method only: a learner that never
# forgets still believes the settled routine, so the return confirms it rather than
# breaking it, and demanding a break from it would be demanding a bug. Measured for the
# forgetting method: 22.8 on sick10_partial, 8.9 on illness_v1, 1.6 on illness_v2, 4.5
# on the night-shift control. Again about two clustered standard errors.

THRESHOLD_SHIFT_POINTS = 2.0
# Not a bar: the size of the perturbation the verdict is tested against. Every bar below
# is moved together by this much, stricter and then more lenient, and the report says
# whether the verdict survives. Two points because that is about one household-clustered
# standard error on the tightest leg, so it is the smallest move a reader could call
# arbitrary, and because the bars were set from three scenarios and could honestly have
# come out two points either way.

KNIFE_EDGE_POINTS = 2.0
# Not a bar either. A leg that passes with under two points to spare is being decided by
# noise rather than by the scenario, and saying so is honest where quoting it as a margin
# is not. illness_v2's re-learn passes by exactly 0.0 points, which is how this got here.

CONTROL_CARRIES_THE_DROP = 0.60
# Not a bar, a reading rule, and it moves no verdict. If the objects the upset never
# touched drop at the return by at least 60% of what the moved objects drop, then most
# of the fourth leg is the return being a harder prediction problem than the upset was,
# and saying so is the difference between a real finding and a difficulty artefact. The
# purpose-built night-shift control reads about 0.9 here; illness_v2's control moves the
# other way entirely, so it reads as a genuine mover effect.

MAX_SINGLE_ANSWER_SHARE = 0.60
# A method that answers the same place to more than 60% of the questions in a phase has
# collapsed, and its curve is measuring that collapse. Printed always, failed on,
# because two degenerate arms have each cost this project a night of compute.

MIN_QUESTIONS_PER_LEG = 20
# Per household, per leg window, on the "all" slice. Under this the household's own
# curve is not reported, because a leg computed on a handful of questions is noise
# wearing a number's clothes.

PER_HOUSEHOLD_LEG_MARGIN = 5.0
# A household "shows" a leg if it moves the right way by this much. Counted and
# printed, never failed on: on illness_v2 the pooled break is carried by half the
# households and on the night-shift control a smaller break is carried by seven of
# ten, so this count ranks scenarios differently from the pooled size and must not
# quietly override it.


# ---------------------------------------------------------------- running the methods

def phases(bank: Bank, settled: str, disrupted: str, after: str):
    """The four phase windows, in days, read from the scenario's own calendar.

    Day 0 is never scored (no questions), so the windows are taken over the days that
    actually carry questions. Nothing here knows that the upset starts on day 14."""
    lead = [d for d in bank.days_of(settled) if d >= 1]
    upset = [d for d in bank.days_of(disrupted) if d >= 1]
    back = [d for d in bank.days_of(after) if d >= 1]
    if not (lead and upset and back):
        raise SystemExit("one of the three windows has no scored days; "
                         "pass --settled/--disrupted/--after")
    if back[0] <= upset[-1]:
        raise SystemExit("the back-to-normal window is the same as the disrupted one, so "
                         "there is no return to measure; pass --after with the right stage name")
    if len(upset) < BREAK_DAYS + RELEARN_REFERENCE_DAYS:
        raise SystemExit(f"the disrupted window is only {len(upset)} scored days long, so its "
                         f"first {BREAK_DAYS} and last {RELEARN_REFERENCE_DAYS} would overlap and "
                         f"the break and the re-learning would be measured on the same days")
    if len(lead) < EARLY_DAYS + SETTLED_REFERENCE_DAYS:
        raise SystemExit(f"the settled window is only {len(lead)} scored days long, so its first "
                         f"{EARLY_DAYS} and last {SETTLED_REFERENCE_DAYS} would overlap")
    return {"early settled": lead[:EARLY_DAYS],
            "settled": lead[-SETTLED_REFERENCE_DAYS:],
            "broken": upset[:BREAK_DAYS],
            "re-learnt": upset[-RELEARN_REFERENCE_DAYS:],
            "returned": back[:BREAK_DAYS]}, (lead, upset, back)


def moved_objects(bank: Bank, settled: str, disrupted: str):
    """The asked-about objects whose usual place differs between the two windows.

    Same definition as check_scenario.py's movement(), so the two files agree on what
    the effective sample is."""
    out = set()
    for obj in bank.asked():
        a, b = modal_place(bank, obj, settled), modal_place(bank, obj, disrupted)
        if a is not None and b is not None and a != b:
            out.add(obj)
    return out


def replay(bank: Bank, spec: dict):
    """One method over one household, reusing the paper's own replay loop."""
    from baselines.bank import JsonlBank
    from baselines.patrol.run import run_belief
    header = json.loads(bank.path.read_text().splitlines()[0])
    episode = next(iter(JsonlBank(bank.path).episodes()))
    tag = {"household": header["household_id"],
           "_stages": header.get("stages") or {}}
    return run_belief(dict(spec), episode, LOOK, 0, tag)


def tally(banks, settled, disrupted, after):
    """method -> slice -> household -> day -> object class -> [right, asked].

    The object class is kept in the leaf so that dropping a class from the whole check
    is a matter of leaving it out of a sum, with no second replay: that is what makes
    the leave-one-class-out sensitivity report below cost nothing."""
    got = collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: collections.defaultdict(
                lambda: collections.defaultdict(
                    lambda: collections.defaultdict(lambda: [0, 0])))))
    answers = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    classes = collections.Counter()
    movers = {}
    for bank in banks:
        movers[bank.name] = moved_objects(bank, settled, disrupted)
        for label, spec in METHODS:
            for r in replay(bank, spec):
                cls = r.get("object_class") or "?"
                slices = ("all", "moved" if r["object_id"] in movers[bank.name] else "stayed put")
                for sl in slices:
                    cell = got[label][sl][bank.name][r["day_index"]][cls]
                    cell[0] += r["correct"]
                    cell[1] += 1
                stage = r.get("stage") or "?"
                answers[label][stage][r["answer"]] += 1
                if label == METHODS[0][0]:
                    classes[cls] += 1
    return got, answers, movers, classes


# ---------------------------------------------------------------- the arithmetic

def level(cells, households, days, drop_class=None):
    """Pooled accuracy over a set of households and days, and the question count.

    ``drop_class`` leaves one object class out of every sum, which is how the
    sensitivity report asks "would this verdict survive without that class?"."""
    right = asked = 0
    for h in households:
        for d in days:
            for cls, cell in cells[h][d].items():
                if cls == drop_class:
                    continue
                right += cell[0]
                asked += cell[1]
    return (100.0 * right / asked if asked else None), asked


def per_household(cells, households, days, drop_class=None):
    """household -> (accuracy, questions) over those days, households with none dropped."""
    out = {}
    for h in households:
        acc, asked = level(cells, [h], days, drop_class)
        if asked:
            out[h] = (acc, asked)
    return out


def leg(cells, households, frm, to, wanted_sign, drop_class=None):
    """One leg of the curve: pooled change, household-clustered error, who shows it.

    ``wanted_sign`` is +1 for a leg that should climb and -1 for one that should fall.
    ``shown`` counts households moving the wanted way by PER_HOUSEHOLD_LEG_MARGIN."""
    a, na = level(cells, households, frm, drop_class)
    b, nb = level(cells, households, to, drop_class)
    ha = per_household(cells, households, frm, drop_class)
    hb = per_household(cells, households, to, drop_class)
    each = {h: hb[h][0] - ha[h][0] for h in ha if h in hb}
    thin = [h for h in each
            if min(ha[h][1], hb[h][1]) < MIN_QUESTIONS_PER_LEG]
    vals = list(each.values())
    se = (statistics.stdev(vals) / len(vals) ** 0.5) if len(vals) > 1 else None
    return {"from": a, "to": b, "change": (b - a) if (a is not None and b is not None) else None,
            "questions_from": na, "questions_to": nb,
            "household_mean": statistics.mean(vals) if vals else None,
            "household_se": se, "per_household": each, "thin_households": thin,
            "shown": sum(1 for v in vals if v * wanted_sign >= PER_HOUSEHOLD_LEG_MARGIN),
            "households": len(vals), "wanted_sign": wanted_sign}


LEGS = (("learn", "early settled", "settled", +1, "accuracy climbs off its starting level"),
        ("break", "settled", "broken", -1, "accuracy falls when the upset starts"),
        ("re-learn", "broken", "re-learnt", +1, "accuracy climbs back during the upset"),
        ("break again", "re-learnt", "returned", -1, "accuracy falls when ordinary life returns"))


def fmt(x, unit=""):
    return "   --" if x is None else f"{x:5.1f}{unit}"


def signed(x):
    return "   --" if x is None else f"{x:+5.1f}"


# ---------------------------------------------------------------- the report

def check_curve(banks, settled, disrupted, after, quiet=False):
    """Returns (lines, failures, warnings, numbers), in check_scenario.py's shape."""
    lines, fails, warns = [], [], []
    numbers = {"settled": settled, "disrupted": disrupted, "after": after,
               "methods": [label for label, _ in METHODS],
               "look": LOOK, "thresholds": {
                   "min_settled_level": MIN_SETTLED_LEVEL, "min_climb": MIN_CLIMB,
                   "min_break": MIN_BREAK, "min_relearn": MIN_RELEARN,
                   "min_second_break": MIN_SECOND_BREAK}}

    # -- exclusion first, on check_scenario.py's rule, so nothing is computed on a
    #    household where the event did not happen
    movers_by_hh = {b.name: moved_objects(b, settled, disrupted) for b in banks}
    dropped = [b.name for b in banks if len(movers_by_hh[b.name]) < MIN_MOVERS_TO_KEEP_HH]
    kept_banks = [b for b in banks if b.name not in dropped]
    numbers["dropped_households"] = dropped
    numbers["kept_households"] = [b.name for b in kept_banks]
    if not kept_banks:
        fails.append("no household has a disruption in it at all")
        return lines, fails, warns, numbers

    window, (lead, upset, back) = phases(kept_banks[0], settled, disrupted, after)
    numbers["phase_days"] = {k: v for k, v in window.items()}
    got, answers, _, class_counts = tally(kept_banks, settled, disrupted, after)
    kept = [b.name for b in kept_banks]

    lines.append("CHECK 7  THE CLASSICAL CURVE - can a plain counting method be taught "
                 "by this scenario, then broken by it?")
    lines.append("  No language model is involved. If a counting method shows no break, "
                 "THE SCENARIO HAS FAILED, NOT THE METHOD:")
    lines.append("  there is then nothing in the data for a language model to notice, and "
                 "any difference between memory")
    lines.append("  designs measured on it is noise or leakage.")
    lines.append("")
    lines.append(f"  households: {len(kept)} kept"
                 + (f", dropped for having no disruption in them: {', '.join(dropped)}" if dropped else ""))
    lines.append(f"  phases read from the scenario's own calendar - settled '{settled}' days "
                 f"{lead[0]}-{lead[-1]}, upset '{disrupted}' days {upset[0]}-{upset[-1]}, "
                 f"back to normal '{after}' days {back[0]}-{back[-1]}")
    lines.append("  " + ",  ".join(f"{name}: days {w[0]}-{w[-1]}" for name, w in window.items()))
    lines.append("")

    # ------------------------------------------------ the counts, before any curve
    lines.append("  THE UNDERLYING COUNTS. A suspiciously clean curve is a bug until "
                 "these look right.")
    lines.append("  phase              questions  per household  households  objects asked  "
                 "of those, moved by the upset")
    counts = {}
    for name, days in window.items():
        total, per = 0, []
        objs, moved = set(), set()
        for b in kept_banks:
            n = level(got[METHODS[0][0]]["all"], [b.name], days)[1]
            total += n
            per.append(n)
            for q in b.questions:
                if q.get("day_index") in days:
                    objs.add((b.name, q["object_id"]))
                    if q["object_id"] in movers_by_hh[b.name]:
                        moved.add((b.name, q["object_id"]))
        counts[name] = {"questions": total, "per_household_min": min(per), "objects": len(objs),
                        "moved_objects": len(moved)}
        lines.append(f"  {name:18s} {total:9d}  {total / len(kept):13.0f}  {len(kept):10d}  "
                     f"{len(objs):13d}  {len(moved):12d}")
    numbers["counts"] = counts
    lines.append(f"  the effective sample size is objects, not questions: "
                 f"{sum(len(v) for v in movers_by_hh.values())} moved objects across "
                 f"{len(kept)} households. Every interval below is clustered on household.")
    lines.append("")

    # ------------------------------------------------ degeneracy guard
    lines.append("  WHAT THE METHODS ACTUALLY ANSWER. A method that says one place to "
                 "everything has collapsed.")
    lines.append("  method                               window        commonest answer            share  "
                 "distinct answers")
    degenerate = {}
    for label, _ in METHODS:
        for stage in (settled, disrupted, after):
            dist = answers[label][stage]
            if not dist:
                continue
            place, n = dist.most_common(1)[0]
            share = n / sum(dist.values())
            degenerate[f"{label}|{stage}"] = {"top": place, "share": share, "distinct": len(dist)}
            flag = ""
            if share > MAX_SINGLE_ANSWER_SHARE:
                flag = "   <-- COLLAPSED"
                fails.append(f"'{label}' answers '{place}' to {100 * share:.0f}% of the "
                             f"'{stage}' questions - the method has collapsed and its curve "
                             f"is measuring the collapse, not the scenario")
            lines.append(f"  {label:36s} {stage:12s}  {place:24s} {100 * share:5.1f}%  "
                         f"{len(dist):8d}{flag}")
    numbers["answer_distribution"] = degenerate
    lines.append("")

    # ------------------------------------------------ the curve
    lines.append("  THE CURVE. Accuracy at each phase, and the change along each leg. "
                 "Three slices of the questions:")
    lines.append("    all         every question - the paper's own metric, and the one the "
                 "thresholds are set on")
    lines.append("    moved       the objects whose usual place differs between the settled "
                 "and the upset window.")
    lines.append("                Sharper and SELECTION-BIASED - the set is chosen by "
                 "comparing those windows, so noise")
    lines.append("                puts objects in it and they break by construction. Read "
                 "it, do not gate on it.")
    lines.append("    stayed put  the control. At the return these recover while the moved "
                 "ones break, which is how")
    lines.append("                a pooled fourth leg can cancel to nothing.")
    lines.append("")
    curve = {}
    for label, _ in METHODS:
        lines.append(f"  {label}")
        for sl in ("all", "moved", "stayed put"):
            cells = got[label][sl]
            levels = {name: level(cells, kept, days) for name, days in window.items()}
            row = "  ".join(f"{name} {fmt(levels[name][0])}%" for name in window)
            lines.append(f"    {sl:11s} {row}")
            legs = {}
            for leg_name, frm, to, sign, _ in LEGS:
                r = leg(cells, kept, window[frm], window[to], sign)
                legs[leg_name] = r
                se = f"+-{r['household_se']:4.1f}" if r["household_se"] is not None else "     "
                two_se = (r["household_se"] is not None and r["household_mean"] is not None
                          and abs(r["household_mean"]) >= 2 * r["household_se"])
                lines.append(f"      {leg_name:12s} {signed(r['change'])} pts pooled   "
                             f"household mean {signed(r['household_mean'])} {se}   "
                             f"{'clears 2 standard errors' if two_se else 'inside 2 standard errors':25s}  "
                             f"shown by {r['shown']}/{r['households']} households")
            curve[f"{label}|{sl}"] = {
                "levels": {k: {"accuracy": v[0], "questions": v[1]} for k, v in levels.items()},
                "legs": {k: {kk: vv for kk, vv in v.items() if kk != "per_household"}
                         for k, v in legs.items()},
                "per_household": {k: v["per_household"] for k, v in legs.items()}}
        lines.append("")
    numbers["curve"] = curve

    # ------------------------------------------------ per household, the full shape
    lines.append("  PER HOUSEHOLD, on every question. A pooled curve can look perfect when "
                 "two households carry it")
    lines.append("  and eight are flat, so the summary that matters is how many households "
                 "show the whole shape.")
    shapes = {}
    for label, _ in METHODS:
        cells = got[label]["all"]
        legs = {n: leg(cells, kept, window[f], window[t], s) for n, f, t, s, _ in LEGS}
        lines.append(f"  {label}")
        lines.append(f"    household   learn   break  re-learn  break again   "
                     f"questions per leg   full shape")
        full = []
        for h in kept:
            vals = {n: legs[n]["per_household"].get(h) for n in legs}
            nq = min(level(cells, [h], window[w])[1] for w in window)
            ok = all(v is not None and v * s >= PER_HOUSEHOLD_LEG_MARGIN
                     for (n, _, _, s, _), v in ((L, vals[L[0]]) for L in LEGS))
            thin = nq < MIN_QUESTIONS_PER_LEG
            if ok and not thin:
                full.append(h)
            lines.append(f"    {h:11s} {signed(vals['learn'])}  {signed(vals['break'])}  "
                         f"{signed(vals['re-learn'])}     {signed(vals['break again'])}      "
                         f"{nq:10d}          {'yes' if ok else 'no':3s}"
                         + ("   (too few questions to say)" if thin else ""))
        shapes[label] = full
        lines.append(f"    households showing all four legs by at least "
                     f"{PER_HOUSEHOLD_LEG_MARGIN:.0f} points: {len(full)}/{len(kept)}"
                     + (f"  ({', '.join(full)})" if full else ""))
        if label != FORGETS:
            lines.append(f"    (the fourth leg is not expected of this method: a learner that "
                         f"never forgets still believes the settled")
            lines.append(f"     routine, so the return confirms it rather than breaking it.)")
        lines.append("")
    numbers["households_with_full_shape"] = shapes

    # ------------------------------------------------ the verdict, leg by leg
    lines.append("  THE GATE. Each threshold is applied to the pooled 'all questions' curve.")
    lines.append("  leg            method                                 measured   needed   verdict")
    verdicts = {}
    for label, _ in METHODS:
        cells = got[label]["all"]
        settled_level = level(cells, kept, window["settled"])[0]
        tests = [("settled level", settled_level, 100 * MIN_SETTLED_LEVEL, +1)]
        break_leg = leg(cells, kept, window["settled"], window["broken"], -1)
        break_happened = (break_leg["change"] is not None
                          and break_leg["change"] <= -MIN_BREAK)
        for leg_name, frm, to, sign, _ in LEGS:
            if leg_name == "break again" and label != FORGETS:
                continue
            r = leg(cells, kept, window[frm], window[to], sign)
            need = {"learn": MIN_CLIMB, "break": MIN_BREAK,
                    "re-learn": MIN_RELEARN, "break again": MIN_SECOND_BREAK}[leg_name]
            tests.append((leg_name, r["change"], need * sign, sign))
        for name, got_v, need_v, sign in tests:
            ok = got_v is not None and got_v * sign >= need_v * sign

            # ---- the fourth leg is only interpretable where something was adopted.
            # A return cost with no preceding break is not a memory losing a routine; it
            # is the disrupted window having been an easier prediction problem than
            # ordinary life, and the learner getting worse when ordinary life resumes.
            # The purpose-built night-shift control does exactly this: no break at all,
            # yet the forgetting learner drops 7.6 points at the return, because a late
            # shift's weekday has no cooking and no dinner in it and is simply easier to
            # predict. So when the break leg has failed, this leg is reported and does
            # NOT count either way.
            uninterpretable = (name == "break again" and not break_happened)
            if uninterpretable:
                verdicts[f"{label}|{name}"] = {"measured": got_v, "needed": need_v,
                                               "pass": None, "counted": False,
                                               "reason": "no break to return from"}
                lines.append(f"  {name:14s} {label:38s} {signed(got_v)}   {signed(need_v)}   "
                             f"not counted - uninterpretable")
                lines.append(f"    this leg is only meaningful where something was adopted in the "
                             f"first place, and the break leg")
                lines.append(f"    failed, so nothing was. A drop here without a break is the "
                             f"disrupted window having been an easier")
                lines.append(f"    prediction problem than ordinary life, not a memory losing a "
                             f"routine. Reported, not counted.")
                if got_v is not None and got_v < 0:
                    warns.append(f"'{label}' loses {-got_v:.1f} points at the return while having "
                                 f"no break at all, so the fourth leg was not counted: with nothing "
                                 f"adopted, a drop at the return measures the disrupted window "
                                 f"having been easier to predict, not a memory being lost")
            else:
                verdicts[f"{label}|{name}"] = {"measured": got_v, "needed": need_v, "pass": ok,
                                               "counted": True}
                lines.append(f"  {name:14s} {label:38s} {signed(got_v)}   {signed(need_v)}   "
                             f"{'pass' if ok else 'FAIL'}")

            # ---- and print the control beside it, always, counted or not. If the objects
            # the disruption never touched drop by about as much as the ones it moved, the
            # drop is a change in overall difficulty rather than a memory losing a routine.
            if name == "break again":
                mv = leg(got[label]["moved"], kept, window["re-learnt"], window["returned"], -1)
                sp = leg(got[label]["stayed put"], kept, window["re-learnt"], window["returned"], -1)
                lines.append(f"    the objects the upset moved: {signed(mv['change'])} pts;      "
                             f"the objects it never touched: {signed(sp['change'])} pts")
                verdicts[f"{label}|{name}"]["moved"] = mv["change"]
                verdicts[f"{label}|{name}"]["stayed_put"] = sp["change"]
                if (mv["change"] is not None and sp["change"] is not None
                        and sp["change"] < 0 and mv["change"] < 0
                        and sp["change"] <= CONTROL_CARRIES_THE_DROP * mv["change"]):
                    lines.append(f"    <-- the control drops nearly as far as the movers, so most "
                                 f"of this leg is overall difficulty,")
                    lines.append(f"        not a memory losing a routine")
                    warns.append(f"'{label}' drops {-sp['change']:.1f} points at the return on the "
                                 f"objects the upset never touched, against {-mv['change']:.1f} on "
                                 f"the ones it moved - most of the fourth leg is the return being a "
                                 f"harder prediction problem, not a memory losing a routine; do not "
                                 f"read it as the latter")
                elif mv["change"] is not None and sp["change"] is not None:
                    lines.append(f"    (the control moves the other way or barely moves, so this leg "
                                 f"is about the objects the upset moved)")

            if not ok and not uninterpretable:
                if name == "settled level":
                    fails.append(f"'{label}' only reaches {got_v:.0f}% by the end of the settled "
                                 f"window, under the {100 * MIN_SETTLED_LEVEL:.0f}% needed - the "
                                 f"ordinary routine is not learnable here, so nothing can be lost "
                                 f"at the upset either")
                elif name == "learn":
                    fails.append(f"'{label}' gains only {got_v:+.1f} points from its first two days "
                                 f"to the end of the settled window (need {need_v:+.0f}) - the "
                                 f"settled routine is not being learnt")
                elif name == "break":
                    moved = (f"loses only {-got_v:.1f} points" if got_v < 0
                             else f"does not lose anything at all - it GAINS {got_v:.1f} points")
                    fails.append(f"THE SCENARIO HAS NO BREAK IN IT: '{label}' {moved} on the first "
                                 f"{BREAK_DAYS} disrupted days (need {-need_v:.0f}). A counting "
                                 f"method that cannot be broken by the upset means there is nothing "
                                 f"in the data for a language model to notice. This is a failing "
                                 f"scenario, not a failing method")
                elif name == "re-learn":
                    fails.append(f"'{label}' recovers only {got_v:+.1f} points across the rest of "
                                 f"the upset (need {need_v:+.0f}) - the upset is a shock rather "
                                 f"than a new routine, so there is nothing in it for a memory to "
                                 f"learn")
                elif name == "break again":
                    lost = (f"loses only {-got_v:.1f}" if got_v < 0
                            else f"does not lose anything at all - it gains {got_v:.1f}")
                    fails.append(f"THE RETURN COSTS NOTHING: '{label}' {lost} "
                                 f"points on the first {BREAK_DAYS} days back to normal (need "
                                 f"{-need_v:.0f}). A forgetting learner that adopted the upset "
                                 f"should be wrong again when ordinary life resumes; if it is not, "
                                 f"the scenario's third phase is not a change and no arm can be "
                                 f"measured on it")
    numbers["gate"] = verdicts
    lines.append("")

    # ------------------------------------------------ is this verdict one class deep?
    # A scenario's list of asked-about object classes can be tuned until it passes: a
    # class that hardly moves buys settled level and costs break, so a dozen tries will
    # find a mix that clears every bar. The gate cannot tell that it was tuned, but it
    # can say how little would have to change to undo the answer. Recomputed with each
    # class left out in turn - no extra replay, the class is already in the leaf of the
    # tally. This is a report, and it moves no verdict: the point is to make a verdict
    # that rests on one class impossible to quote without the caveat.
    lines.append("  HOW DEEP IS THIS VERDICT? Every leg recomputed with one object class left "
                 "out at a time.")
    lines.append("  If a single class decides the answer, the class list is doing the work that "
                 "the scenario should be")
    lines.append("  doing, and the verdict is not an independent test of the scenario - "
                 "especially if the list was chosen")
    lines.append("  by trying mixes against this gate.")
    lines.append("")
    def all_legs(drop_class=None, offset=0.0):
        """Every gated leg, as name -> (measured, needed, slack). Slack is how many
        points to spare; negative means the leg fails. The fourth leg is skipped where
        the break leg failed, exactly as the gate skips it.

        ``offset`` moves every bar by that many points in the STRICTER direction at once
        (a higher settled level, a bigger climb, a deeper break, more re-learning, a
        bigger return cost), and a negative offset relaxes them all. The break bar that
        decides whether the fourth leg is interpretable moves with it, so the whole gate
        shifts consistently rather than in pieces."""
        out = {}
        for label, _ in METHODS:
            cells = got[label]["all"]
            brk = leg(cells, kept, window["settled"], window["broken"], -1, drop_class)
            adopted = brk["change"] is not None and brk["change"] <= -(MIN_BREAK + offset)
            checks = [("settled level", level(cells, kept, window["settled"], drop_class)[0],
                       100 * MIN_SETTLED_LEVEL + offset, +1)]
            for leg_name, frm, to, sign, _ in LEGS:
                if leg_name == "break again" and (label != FORGETS or not adopted):
                    continue
                r = leg(cells, kept, window[frm], window[to], sign, drop_class)
                need = {"learn": MIN_CLIMB, "break": MIN_BREAK,
                        "re-learn": MIN_RELEARN, "break again": MIN_SECOND_BREAK}[leg_name]
                checks.append((leg_name, r["change"], (need + offset) * sign, sign))
            for name, v, need, sign in checks:
                if v is not None:
                    out[f"{name} ({SHORT[label]})"] = (v, need, (v - need) * sign)
        return out

    full = all_legs()
    passes = all(s >= 0 for _, _, s in full.values())
    narrowest = sorted(full.items(), key=lambda kv: kv[1][2])
    lines.append("  in the full run, the legs with the least to spare:")
    for name, (v, need, slack) in narrowest[:3]:
        lines.append(f"    {name:36s} {v:+6.1f} against {need:+5.0f} needed - "
                     f"{slack:+.1f} points to spare")
    knife = [n for n, (_, _, s) in full.items() if 0 <= s <= KNIFE_EDGE_POINTS]
    if knife:
        warns.append(f"{', '.join(knife)} passes with under {KNIFE_EDGE_POINTS:.0f} points to "
                     f"spare, so that leg is decided by noise rather than by the scenario; do not "
                     f"quote it as a margin")
    lines.append("")
    lines.append("  class            questions   verdict without it   narrowest leg without it")
    flips, sens = [], {}
    for cls, n in class_counts.most_common():
        legs_without = all_legs(cls)
        without_passes = all(s >= 0 for _, _, s in legs_without.values())
        worst = min(legs_without.items(), key=lambda kv: kv[1][2], default=(None, (None, None, None)))
        newly_failing = [name for name, (_, _, s) in legs_without.items()
                         if s < 0 and full.get(name, (0, 0, -1))[2] >= 0]
        sens[cls] = {"questions": n, "verdict": "pass" if without_passes else "fail",
                     "flips": without_passes != passes, "newly_failing": newly_failing,
                     "narrowest_leg": worst[0], "narrowest_slack": worst[1][2]}
        if without_passes != passes:
            flips.append((cls, newly_failing))
        lines.append(f"  {cls:16s} {n:9d}   {'pass' if without_passes else 'fail':18s}"
                     f"   {worst[0]}: {worst[1][0]:+.1f} vs {worst[1][1]:+.0f} needed"
                     + ("    <-- FLIPS THE VERDICT" if without_passes != passes else ""))
    numbers["class_sensitivity"] = sens
    numbers["narrowest_legs"] = {k: {"measured": v[0], "needed": v[1], "slack": v[2]}
                                 for k, v in narrowest}
    lines.append("")
    if flips:
        # Which legs a class carries matters. The floors (settled level, learn) say the
        # routine is learnable at all; the discriminating legs (break, re-learn, break
        # again) are the ones that tell a real disruption from a cosmetic one. A verdict
        # whose floors are one class deep is fragile; one whose BREAK is one class deep
        # was, for practical purposes, chosen.
        FLOORS = ("settled level", "learn")
        carried = collections.defaultdict(list)
        for cls, legs_failing in flips:
            for name in legs_failing:
                carried[name].append(cls)
        floors = sorted({n for n in carried if n.split(" (")[0] in FLOORS})
        discriminating = sorted({n for n in carried if n.split(" (")[0] not in FLOORS})
        lines.append(f"  THE VERDICT IS ONE CLASS DEEP. Dropping "
                     f"{' or '.join(repr(c) for c, _ in flips)} on its own reverses it.")
        for name in sorted(carried):
            kind = "a floor" if name.split(" (")[0] in FLOORS else "a DISCRIMINATING leg"
            lines.append(f"    {name} ({kind}) fails without {', '.join(carried[name])}")
        lines.append(f"  This gate is only an independent test of this scenario if its class list "
                     f"was not chosen by trying")
        lines.append(f"  mixes against the gate.")
        detail = []
        if discriminating:
            detail.append(f"the discriminating leg(s) {', '.join(discriminating)} fail without them, "
                          f"which means the disruption itself rests on one class")
        if floors:
            detail.append(f"the floor(s) {', '.join(floors)} fail without them, which is fragility "
                          f"rather than a fitted disruption")
        warns.append(f"the verdict is one class deep: dropping "
                     f"{' or '.join(repr(c) for c, _ in flips)} on its own reverses it - "
                     + "; ".join(detail)
                     + ". If this scenario's class list was chosen by trying mixes against this "
                       "gate then the gate is not an independent test of it - say in the paper "
                       "which scenarios predate the gate and which were tuned against it")
    else:
        lines.append(f"  no single class decides the verdict: it survives dropping any one of the "
                     f"{len(class_counts)} classes on its own.")
    lines.append("")

    # ------------------------------------------------ are the thresholds carrying it?
    # Every bar here was set from what one scenario and two older ones showed, so the
    # fair question is whether the verdicts are the gate's or the bars'. All four leg
    # bars and the settled-level floor are moved together, by the same number of points,
    # in both directions. A verdict that survives that is the scenario's; a verdict that
    # flips inside it is the threshold's, and must not be quoted without saying so.
    lines.append(f"  ARE THE THRESHOLDS CARRYING THIS VERDICT? Every bar moved together, "
                 f"{THRESHOLD_SHIFT_POINTS:.0f} points stricter and")
    lines.append(f"  {THRESHOLD_SHIFT_POINTS:.0f} points more lenient at once - a higher settled "
                 f"level, a bigger climb, a deeper break, more")
    lines.append(f"  re-learning and a bigger return cost, then all of it the other way.")
    lines.append("")
    lines.append("  every bar moved by    verdict     legs that change")
    shifts, flipped_at = {}, []
    for offset in (THRESHOLD_SHIFT_POINTS, 0.0, -THRESHOLD_SHIFT_POINTS):
        legs_at = all_legs(offset=offset)
        ok_at = all(s >= 0 for _, _, s in legs_at.values())
        changed = []
        for name, (_, _, s) in legs_at.items():
            was = full.get(name)
            if was is None:
                changed.append(f"{name} now counted")
            elif (s >= 0) != (was[2] >= 0):
                changed.append(f"{name} {'now passes' if s >= 0 else 'now fails'}")
        for name in full:
            if name not in legs_at:
                changed.append(f"{name} no longer counted")
        word = {THRESHOLD_SHIFT_POINTS: f"+{THRESHOLD_SHIFT_POINTS:.0f} (stricter)", 0.0: " 0 (as set)"}.get(
            offset, f"-{THRESHOLD_SHIFT_POINTS:.0f} (more lenient)")
        shifts[f"{offset:+.0f}"] = {"verdict": "pass" if ok_at else "fail",
                                    "flips": ok_at != passes, "changed_legs": changed}
        if ok_at != passes:
            flipped_at.append(word.strip())
        lines.append(f"  {word:20s} {'pass' if ok_at else 'fail':10s}  "
                     f"{'; '.join(changed) if changed else 'none'}"
                     + ("    <-- FLIPS THE VERDICT" if ok_at != passes else ""))
    numbers["threshold_sensitivity"] = shifts
    lines.append("")
    if flipped_at:
        lines.append(f"  THE THRESHOLDS ARE CARRYING THIS VERDICT: it reverses at "
                     f"{' and at '.join(flipped_at)}. Whoever quotes this")
        lines.append(f"  scenario's verdict has to say that a {THRESHOLD_SHIFT_POINTS:.0f}-point "
                     f"move in the bars would have given the other answer.")
        warns.append(f"this verdict is not robust to the thresholds: moving every bar together by "
                     f"{THRESHOLD_SHIFT_POINTS:.0f} points reverses it at {' and at '.join(flipped_at)}. "
                     f"The bars were set from what one scenario and two older ones showed, so a "
                     f"verdict that turns on them is the gate's opinion rather than the scenario's "
                     f"- do not quote it without this caveat")
    else:
        lines.append(f"  the verdict is the scenario's, not the thresholds': it is unchanged by "
                     f"moving every bar together by")
        lines.append(f"  {THRESHOLD_SHIFT_POINTS:.0f} points in either direction.")
    lines.append("")

    # ------------------------------------------------ what a null excludes
    for label, _ in METHODS:
        cells = got[label]["all"]
        for leg_name, frm, to, sign, _ in LEGS:
            r = leg(cells, kept, window[frm], window[to], sign)
            if r["household_se"] is None or r["household_mean"] is None:
                continue
            if abs(r["household_mean"]) < 2 * r["household_se"]:
                bound = abs(r["household_mean"]) + 2 * r["household_se"]
                warns.append(f"'{label}' {leg_name} is {r['household_mean']:+.1f} points with a "
                             f"household-clustered error of {r['household_se']:.1f}, inside two "
                             f"standard errors of nothing; this null only excludes a change larger "
                             f"than about {bound:.0f} points, it does not show there is none")
    return lines, fails, warns, numbers


# ---------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Does a plain counting method show the four-phase curve on this scenario?")
    ap.add_argument("regime", nargs="?", help="a run directory containing banks/")
    ap.add_argument("--banks", help="glob for bank files, instead of a run directory")
    ap.add_argument("--settled"), ap.add_argument("--disrupted"), ap.add_argument("--after")
    ap.add_argument("--label", default="t03", help="the patrol label in the bank filenames")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--json", type=pathlib.Path)
    a = ap.parse_args(argv)

    if a.banks:
        paths = sorted(pathlib.Path(p) for p in glob.glob(a.banks))
        title = a.banks
    elif a.regime:
        root = pathlib.Path(a.regime)
        paths = sorted(root.glob(f"banks/hh_s*_{a.label}.jsonl")) or sorted(root.glob("hh_s*.jsonl"))
        title = str(root)
    else:
        ap.error("give a run directory or --banks")
    if not paths:
        raise SystemExit(f"no bank files found for {title}")

    banks = [Bank(p) for p in paths]
    guessed = guess_stages(banks[0])
    settled = a.settled or guessed[0]
    disrupted = a.disrupted or guessed[1]
    after = a.after or guessed[2]

    print("=" * 100)
    print(f"CLASSICAL-CURVE CHECK: {title}")
    print("=" * 100)
    print()
    lines, fails, warns, numbers = check_curve(banks, settled, disrupted, after, a.quiet)
    if not a.quiet:
        print("\n".join(lines))

    print("-" * 100)
    if fails:
        print(f"VERDICT: DO NOT RUN. {len(fails)} check(s) failed.")
        for i, f in enumerate(fails, 1):
            print(f"  {i}. {f}")
    else:
        print("VERDICT: THE CURVE IS THERE. A plain counting method learns this scenario, "
              "is broken by the upset,")
        print("         re-learns during it, and is broken again by the return.")
    if warns:
        print(f"\nWarnings ({len(warns)}) - not disqualifying, but say them in the paper:")
        for i, w in enumerate(warns, 1):
            print(f"  {i}. {w}")
    print("-" * 100)

    numbers["failures"] = fails
    numbers["warnings"] = warns
    numbers["verdict"] = "do not run" if fails else "the curve is there"
    if a.json:
        a.json.write_text(json.dumps(numbers, indent=2, default=str))
        print(f"numbers written to {a.json}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
