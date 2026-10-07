#!/usr/bin/env python3
"""Study 2 baseline: a surprise count over the robot's own sightings.

Follows coordination/studies/study2_noticing_a_routine_changed/SETUP.md.

Data: the last-seen (no model) cells, so the sighting stream does not depend on a model's
choices. Each cell's looks.jsonl holds one row per room opened; the row lists every object the
look revealed (object_id, room, place_id, day, time).

Definitions used here, stated once:
- The stream is every sighting from every look, ordered by (day, time, order in the file).
- Predicted room, definition A (last-seen): the room of the object's previous sighting.
- Predicted room, definition B (commonest over seven days): the commonest room among the
  object's earlier sightings whose day is >= today-7 (the past seven days plus earlier today);
  ties go to the room seen most recently.
- A sighting is surprising when its room differs from the predicted room. An object with no
  earlier sighting (A) or no sighting in the window (B) is skipped.
- Daily count c[d] = surprising sightings on day d. Window sum w[d] = c[d-2]+c[d-1]+c[d]
  (days before day 1 contribute nothing). Day d is an alarm day when w[d] > T.
- Threshold T for a held-out household: the smallest integer such that every other household
  in the pool has at most one alarm per month on days 1-13, with alarms counted per month as
  alarms * 30/13. One alarm in 13 days is 2.3 a month, so this rule means zero alarm days on
  days 1-13 for every household in the pool, i.e. T = the largest window sum any of them shows
  on days 1-13. A looser variant (at most one raw alarm day on days 1-13 per pool household,
  which is 2.3 a month) is also reported, labelled as such.
- Scores for the held-out household: delay = first alarm day in 14..23 minus 14 ("none" if no
  alarm by day 23); false alarms = alarm days on days 1-13, times 30/13; return alarms = alarm
  days on days 24-31, reported separately. For the 50-day households the second change is on
  day 32 (delay scored over days 32..41) and the second return on days 42-49.

Writes RESULTS_baseline.md and counts.json beside this script. CPU only; stdlib only.
"""
from __future__ import annotations

import collections
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
TEN_DIR = REPO / "results/self_improve/overnight_wave/cells/last_seen_no_model"
FIFTY_DIR = REPO / "results/self_improve/wave_the_second_illness/cells/last_seen_no_model"
TEN_NAMES = ["hh_s2_t03", "hh_s19_t03", "hh_s20_t03", "hh_s32_t03", "hh_s48_t03",
             "hh_s63_t03", "hh_s93_t03", "hh_s109_t03", "hh_s123_t03", "hh_s151_t03"]
FIFTY_NAMES = ["hh_s2_t03", "hh_s32_t03", "hh_s48_t03"]

WINDOW = 3
SEVEN = 7
CAL_DAYS = list(range(1, 14))
PER_MONTH = 30 / 13
RULES = ("last_seen", "commonest_7d")
RULE_LABEL = {"last_seen": "A: last-seen room", "commonest_7d": "B: commonest room, past 7 days"}


# ----------------------------------------------------------------------------- loading

def load_cell(cell_dir: pathlib.Path):
    """Return the sighting stream, looks per day, rooms opened per day, last day, movers."""
    looks = []
    with open(cell_dir / "looks.jsonl") as fh:
        for i, line in enumerate(fh):
            row = json.loads(line)
            if row.get("kind") != "look":
                continue
            looks.append((row["day"], row["time"], i, row))
    looks.sort(key=lambda t: (t[0], t[1], t[2]))
    stream = []
    looks_per_day = collections.Counter()
    rooms_opened = collections.defaultdict(list)
    for day, time, i, row in looks:
        looks_per_day[day] += 1
        for tgt in row.get("targets", []):
            rooms_opened[day].append(tgt["name"])
        for j, s in enumerate(row["sightings"]):
            stream.append({"day": s["day"], "time": s["time"], "order": (i, j),
                           "object_id": s["object_id"], "room": s["room"]})
    cell = json.load(open(cell_dir / "cell.json"))
    last_day = cell.get("last_day")
    movers = cell.get("movers", [])
    return stream, looks_per_day, rooms_opened, last_day, movers


def mover_rooms_when_sick(cell_dir: pathlib.Path, sick_days, settled_days):
    """Rooms where the movers truly were on sick days that are not where they were on settled
    days, taken from the searches' true_room field (ground truth, used only for the note)."""
    sick = collections.defaultdict(set)
    settled = collections.defaultdict(set)
    with open(cell_dir / "searches.jsonl") as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("kind") != "search" or not row.get("is_a_mover"):
                continue
            if row["day"] in sick_days:
                sick[row["object_id"]].add(row["true_room"])
            elif row["day"] in settled_days:
                settled[row["object_id"]].add(row["true_room"])
    rooms = set()
    for obj, rs in sick.items():
        rooms |= rs - settled.get(obj, set())
    return rooms


# ----------------------------------------------------------------------------- the count

def surprise_counts(stream, rule):
    counts = collections.Counter()
    skipped = 0
    history = collections.defaultdict(list)  # object -> [(day, room), ...] in stream order
    for s in stream:
        obj, day, room = s["object_id"], s["day"], s["room"]
        hist = history[obj]
        pred = None
        if rule == "last_seen":
            if hist:
                pred = hist[-1][1]
        elif rule == "commonest_7d":
            window = [(d, r) for d, r in hist if d >= day - SEVEN]
            if window:
                tally = collections.Counter(r for _, r in window)
                top = max(tally.values())
                tied = {r for r, n in tally.items() if n == top}
                for d, r in reversed(window):  # most recent among the tied rooms
                    if r in tied:
                        pred = r
                        break
        else:
            raise ValueError(rule)
        if pred is None:
            skipped += 1
        elif pred != room:
            counts[day] += 1
        hist.append((day, room))
    return counts, skipped


def window_sums(counts, last_day):
    return {d: sum(counts.get(e, 0) for e in range(max(1, d - WINDOW + 1), d + 1))
            for d in range(1, last_day + 1)}


def alarm_days(wsum, T, days):
    return [d for d in days if wsum.get(d, 0) > T]


def choose_T(pool_wsums, strict=True):
    """Smallest integer T so that every household in the pool passes the false-alarm rule on
    days 1-13. strict: alarms*30/13 <= 1 (so zero alarms). loose: at most one raw alarm day."""
    T = 0
    while True:
        ok = True
        for w in pool_wsums:
            n = len(alarm_days(w, T, CAL_DAYS))
            if strict and n * PER_MONTH > 1:
                ok = False
            if not strict and n > 1:
                ok = False
            if not ok:
                break
        if ok:
            return T
        T += 1


def first_alarm_delay(wsum, T, change_day, last_change_day):
    hits = alarm_days(wsum, T, range(change_day, last_change_day + 1))
    return (hits[0] - change_day) if hits else None


# ----------------------------------------------------------------------------- the study

def run_set(names, root, spells, returns, last_day_expected):
    """spells: list of (change_day, last_sick_day); returns: list of (first, last)."""
    hh = {}
    missing = []
    for name in names:
        d = root / name
        if not (d / "looks.jsonl").exists():
            missing.append(name)
            continue
        stream, looks_pd, rooms_pd, last_day, movers = load_cell(d)
        sick_days = set(range(spells[0][0], spells[0][1] + 1))
        rec = {"stream_n": len(stream), "looks_per_day": looks_pd, "rooms_opened": rooms_pd,
               "last_day": last_day or last_day_expected, "movers": movers,
               "sightings_per_day": collections.Counter(s["day"] for s in stream),
               "sick_rooms": mover_rooms_when_sick(d, sick_days, set(CAL_DAYS)),
               "counts": {}, "wsum": {}, "skipped": {}}
        for rule in RULES:
            c, sk = surprise_counts(stream, rule)
            rec["counts"][rule] = c
            rec["skipped"][rule] = sk
            rec["wsum"][rule] = window_sums(c, rec["last_day"])
        hh[name] = rec

    present = [n for n in names if n in hh]
    results = {rule: {"strict": {}, "loose": {}} for rule in RULES}
    for rule in RULES:
        for mode in ("strict", "loose"):
            for name in present:
                pool = [hh[o]["wsum"][rule] for o in present if o != name]
                T = choose_T(pool, strict=(mode == "strict"))
                w = hh[name]["wsum"][rule]
                fa = len(alarm_days(w, T, CAL_DAYS))
                row = {"T": T, "false_alarms_raw": fa, "false_alarms_per_month": fa * PER_MONTH,
                       "delays": [first_alarm_delay(w, T, c0, c1) for c0, c1 in spells],
                       "return_alarms": [len(alarm_days(w, T, range(r0, r1 + 1))) for r0, r1 in returns],
                       "alarm_days_all": alarm_days(w, T, range(1, hh[name]["last_day"] + 1))}
                results[rule][mode][name] = row
    return hh, results, missing, present


# ----------------------------------------------------------------------------- reporting

def fmt_delay(x):
    return "none" if x is None else str(x)


def mean_sd(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return "n/a", "n/a", 0
    m = statistics.mean(vals)
    sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
    return f"{m:.2f}", f"{sd:.2f}", len(vals)


def per_household_table(results, present, spells, returns, mode, label_days):
    lines = []
    for rule in RULES:
        lines.append(f"\n**Definition {RULE_LABEL[rule]}** (threshold rule: {mode})\n")
        head = ["household", "T (alarm when 3-day sum > T)"]
        for c0, _ in spells:
            head.append(f"delay from day {c0}")
        head += ["false alarm days 1-13 (raw)", "false alarms per month"]
        for r0, r1 in returns:
            head.append(f"alarm days {r0}-{r1} (return)")
        lines.append("| " + " | ".join(head) + " |")
        lines.append("|" + "---|" * len(head))
        for name in present:
            r = results[rule][mode][name]
            cells = [name, str(r["T"])]
            cells += [fmt_delay(x) for x in r["delays"]]
            cells += [str(r["false_alarms_raw"]), f"{r['false_alarms_per_month']:.2f}"]
            cells += [str(x) for x in r["return_alarms"]]
            lines.append("| " + " | ".join(cells) + " |")
        for k, (c0, c1) in enumerate(spells):
            delays = [results[rule][mode][n]["delays"][k] for n in present]
            m, sd, n = mean_sd(delays)
            none_n = sum(1 for x in delays if x is None)
            lines.append(f"\nDelay from day {c0} over households: mean {m}, sd {sd} "
                         f"(n = {n} detected; {none_n} with no alarm on days {c0}-{c1}; "
                         f"'none' excluded from the mean).")
        fa = [results[rule][mode][n]["false_alarms_per_month"] for n in present]
        lines.append(f"False alarms per month over households: mean {statistics.mean(fa):.2f}.")
        ret = [sum(results[rule][mode][n]["return_alarms"]) for n in present]
        lines.append(f"Households with at least one return alarm: {sum(1 for x in ret if x > 0)} of {len(present)}.")
    return lines


def day_table(hh, present, days, title):
    lines = [f"\n{title}\n"]
    head = ["household", "row"] + [f"d{d}" for d in days]
    lines.append("| " + " | ".join(head) + " |")
    lines.append("|" + "---|" * len(head))
    for name in present:
        rec = hh[name]
        rows = [("surprising (A last-seen)", rec["counts"]["last_seen"]),
                ("surprising (B 7-day)", rec["counts"]["commonest_7d"]),
                ("sightings", rec["sightings_per_day"]),
                ("looks (rooms opened)", rec["looks_per_day"])]
        for label, c in rows:
            lines.append("| " + " | ".join([name, label] + [str(c.get(d, 0)) for d in days]) + " |")
    return lines


def level_table(hh, present, windows):
    """Mean surprising sightings a day, and the largest 3-day sum, in each window, per rule."""
    lines = []
    for rule in RULES:
        lines.append(f"\nDefinition {RULE_LABEL[rule]}:\n")
        head = ["household"] + [f"mean/day d{a}-{b}" for a, b in windows] + \
               [f"max 3-day sum d{a}-{b} (on day)" for a, b in windows]
        lines.append("| " + " | ".join(head) + " |")
        lines.append("|" + "---|" * len(head))
        for n in present:
            c = hh[n]["counts"][rule]
            w = hh[n]["wsum"][rule]
            cells = [n]
            for a, b in windows:
                cells.append(f"{statistics.mean(c.get(d, 0) for d in range(a, b + 1)):.1f}")
            for a, b in windows:
                best = max(range(a, b + 1), key=lambda d: (w.get(d, 0), -d))
                cells.append(f"{w.get(best, 0)} (d{best})")
            lines.append("| " + " | ".join(cells) + " |")
    return lines


def sick_room_table(hh, present, change_day):
    lines = ["\n| household | movers | rooms the movers go to when sick (not their settled room) | "
             f"looks into those rooms on day {change_day} / +1 / +2 | first day >= {change_day} the robot opened one |"]
    lines.append("|---|---|---|---|---|")
    for name in present:
        rec = hh[name]
        rooms = sorted(rec["sick_rooms"])
        per = [sum(1 for r in rec["rooms_opened"].get(d, []) if r in rec["sick_rooms"])
               for d in (change_day, change_day + 1, change_day + 2)]
        first = next((d for d in range(change_day, rec["last_day"] + 1)
                      if any(r in rec["sick_rooms"] for r in rec["rooms_opened"].get(d, []))), None)
        lines.append(f"| {name} | {len(rec['movers'])} | {', '.join(rooms) or '-'} | "
                     f"{per[0]} / {per[1]} / {per[2]} | {first if first is not None else 'never'} |")
    return lines


NOTES = """\
Plain description of what in the data drives the numbers above. The figures quoted are from the tables in
this file (ten-household run unless said otherwise).

1. How much the robot sees. In the 8-questions-a-day run the robot opens about 8 to 19 rooms a day and records
   roughly 50 to 300 sightings a day (per-household means 71 to 153 on days 1-13). In the 24-questions-a-day run
   it is roughly 24 to 45 rooms and 180 to 530 sightings a day. A look writes down every object in the room, so
   the daily count moves with how many rooms were opened and which ones: one look into the dining room at
   a meal time adds up to nine surprising sightings at once (every plate, glass, mug and bottle that was
   last seen in the kitchen).

2. Settled days are not quiet. Under definition A the settled-window mean is 1.5 to 8.4 surprising
   sightings a day and the largest settled 3-day sums are 47 (hh_s2, days 3-5) and 42 (hh_s151, days
   4-6). Listing the surprising sightings on hh_s2 days 4-5 shows what they are: crockery and water bottles
   moving kitchen <-> dining at meals, and the residents' mugs, bottles and chargers moving between office,
   entry, bedroom and kitchen, each move seen at whatever time of day a question happened to fall. That is
   the ordinary routine, not noise in the sensor. The sick-window 3-day sums under A peak at 10 to 45, the
   same range as the settled peaks; in 6 of 10 households the settled maximum is at or above the sick
   maximum under A, and in 4 of 10 under B.

3. The threshold is set by the two loudest households. Leave-one-out with zero alarms allowed on days 1-13
   makes T the largest settled 3-day sum among the other nine, which is 47 for every household except the
   loud one itself (42). The loud households (hh_s2, hh_s151) are the ones that go over on their own days
   1-13 when held out. Settled peaks come early: under A the largest 3-day sum in days 1-7 exceeds the one
   in days 8-13 in 8 of 10 households (hh_s32 and hh_s123 are the exceptions; both are quiet throughout).
   SETUP says days 1-13, so no shorter window was used.

4. The change itself is small in sighting terms. The movers are 5 to 9 objects per household. Even if the
   robot saw every one of them in a new room on day 14, that adds at most 5 to 9 surprising sightings to a
   settled background of 1.5 to 8 a day. Day-14 counts under A are 0 to 24, against settled days that
   reach 22. The robot does look where the sick resident's things go: the first day on or after 14 on
   which it opens one of those rooms is day 14 in 9 of 10 households (day 15 in hh_s63), with 0 to 7 such
   looks on day 14.

5. The two definitions count a lasting move differently. A counts a move once (the next sighting in the
   new room is expected). B keeps counting the object as surprising until the new room is the commonest
   of the past seven days, so a lasting move gives a run of raised days (hh_s20 days 15-17: 26, 17, 12;
   hh_s93 days 15-17: 20, 21, 11). That is why B detects in 3 of 10 (all with delay 2, on the day-16
   window) and A in none, why B detects both spells in all three 50-day households (delays 0 to 2), and why
   B raises more return alarms.

6. The return is a change of the same size. Under both definitions the largest 3-day sum of the whole run
   is often on days 24-28: under A the return-window maximum exceeds the sick-window maximum in 9 of 10
   households (hh_s109 is the exception); under B the return raises alarms in 3 of 10 households (and in all three 50-day
   households, after both spells) while the sickness raises them in 3 of 10.

7. The 50-day run. Thresholds there come from two households each, and hh_s48's own settled days are
   louder than the other two, so it gets 3 alarm days on days 1-13 (6.9 a month) under B. Under A no spell
   is detected in any of the three; under B both spells are detected in all three.

8. The mean and standard deviation of the delay are over detected households only (0, 1 or 3 of 10), so
   they describe few households; the "none" count beside them is the larger part of the result.

9. The strict and loose threshold rules differ little: T drops from 47 to 40-46 and A gains one detection
   (hh_s109, delay 1, at T=42). With only 13 calibration days, "at most one false alarm per month" cannot
   be met by anything other than zero alarms, so the strict rule is the one SETUP's words describe.
"""


def main():
    out = []
    out.append("# Study 2 baseline: the surprise count, computed\n")
    out.append("Computed by `surprise_count.py` beside this file, from the last-seen (no model) cells. "
               "The definitions are in the script's docstring; the ones that needed a decision are repeated here.\n")
    out.append("- Stream: every sighting from every look, in (day, time, file order). A look records every "
               "object in the room it opened, so one look can add many sightings at once.")
    out.append("- A (last-seen): predicted room = room of the object's previous sighting.")
    out.append("- B (7-day commonest): predicted room = commonest room among the object's earlier sightings "
               "with day >= today-7 (past seven days plus earlier today); ties go to the most recent room.")
    out.append("- Alarm day: the sum of surprising sightings over days d-2..d exceeds T. Each day over T is one alarm day.")
    out.append("- Threshold, strict (SETUP's rule read literally): T is the smallest integer such that every other "
               "household in the pool has alarms*30/13 <= 1 on days 1-13. One alarm in 13 days is 2.3 a month, so "
               "this means zero alarm days on days 1-13 for every pool household; T equals the largest 3-day sum "
               "any pool household shows on days 1-13.")
    out.append("- Threshold, loose (reported for contrast only): at most one raw alarm day on days 1-13 per pool "
               "household, which is 2.3 a month and does not meet the SETUP bar.")
    out.append("- Delay: first alarm day in 14..23 minus 14 (0 = day 14); 'none' if no alarm by day 23. Return alarms "
               "on days 24-31 are counted separately and are not false alarms.\n")

    # ---- ten households, 31 days
    hh, res, missing, present = run_set(TEN_NAMES, TEN_DIR, [(14, 23)], [(24, 31)], 31)
    out.append("## Ten households, 31 days, 8 questions a day\n")
    out.append(f"Cells under `{TEN_DIR.relative_to(REPO)}`. Present: {len(present)} of {len(TEN_NAMES)}."
               + (f" Missing: {', '.join(missing)}." if missing else " None missing."))
    out.append("Per household: sightings in the stream, and sightings skipped for lack of an earlier sighting "
               "(A) or of one in the 7-day window (B).\n")
    out.append("| household | sightings | skipped A | skipped B | sightings/day, days 1-13 mean | days 14-23 mean |")
    out.append("|---|---|---|---|---|---|")
    for n in present:
        r = hh[n]
        m1 = statistics.mean(r["sightings_per_day"].get(d, 0) for d in range(1, 14))
        m2 = statistics.mean(r["sightings_per_day"].get(d, 0) for d in range(14, 24))
        out.append(f"| {n} | {r['stream_n']} | {r['skipped']['last_seen']} | {r['skipped']['commonest_7d']} | {m1:.0f} | {m2:.0f} |")

    out.append("\n### Per-household scores, leave-one-out threshold\n")
    out += per_household_table(res, present, [(14, 23)], [(24, 31)], "strict", None)
    out.append("\n#### The same with the loose threshold rule (not SETUP's bar; for contrast)")
    out += per_household_table(res, present, [(14, 23)], [(24, 31)], "loose", None)

    out.append("\n### Day-by-day counts, days 10-18\n")
    out.append("Raw surprising-sighting counts per day under both definitions, with the number of sightings "
               "and the number of rooms opened that day. The change is on day 14.")
    out += day_table(hh, present, list(range(10, 19)), "")

    out.append("\n### How high the count runs in each window\n")
    out.append("Mean surprising sightings a day in the settled, sick and return windows, and the largest 3-day "
               "sum inside each window (the day it falls on). The strict threshold for a household is the largest "
               "settled-window 3-day sum among the other nine, so a household is detected only if its sick-window "
               "maximum exceeds that.")
    out += level_table(hh, present, [(1, 13), (14, 23), (24, 31)])
    out.append("\n### Alarm days under the strict threshold, every day 1-31\n")
    for rule in RULES:
        out.append(f"\nDefinition {RULE_LABEL[rule]}:\n")
        out.append("| household | T | alarm days |")
        out.append("|---|---|---|")
        for n in present:
            r = res[rule]["strict"][n]
            out.append(f"| {n} | {r['T']} | {', '.join(map(str, r['alarm_days_all'])) or '-'} |")

    out.append("\n### Does the robot look into the rooms the sick resident's things go to?\n")
    out.append("Ground truth is used here only to describe the data, not in the baseline. 'Rooms the movers go "
               "to when sick' are the true rooms of mover objects on days 14-23 that are not the object's true "
               "room on days 1-13, from searches.jsonl.")
    out += sick_room_table(hh, present, 14)

    ten_summary = {"hh": hh, "res": res, "present": present}

    # ---- three households, 50 days
    hh5, res5, missing5, present5 = run_set(FIFTY_NAMES, FIFTY_DIR, [(14, 23), (32, 41)], [(24, 31), (42, 49)], 49)
    out.append("\n## Three households, 50 days, 24 questions a day\n")
    out.append(f"Cells under `{FIFTY_DIR.relative_to(REPO)}`. Present: {len(present5)} of {len(FIFTY_NAMES)}."
               + (f" Missing: {', '.join(missing5)}." if missing5 else " None missing.")
               + " The last question day is 49, so the second return is days 42-49. The threshold is chosen "
               "leave-one-out within these three (on the other two), because at 24 questions a day the sighting "
               "rate is about three times the 8-a-day run and a threshold tuned there would not transfer.")
    out.append("\n| household | sightings | skipped A | skipped B | sightings/day, days 1-13 mean | days 14-23 mean | days 32-41 mean |")
    out.append("|---|---|---|---|---|---|---|")
    for n in present5:
        r = hh5[n]
        m1 = statistics.mean(r["sightings_per_day"].get(d, 0) for d in range(1, 14))
        m2 = statistics.mean(r["sightings_per_day"].get(d, 0) for d in range(14, 24))
        m3 = statistics.mean(r["sightings_per_day"].get(d, 0) for d in range(32, 42))
        out.append(f"| {n} | {r['stream_n']} | {r['skipped']['last_seen']} | {r['skipped']['commonest_7d']} | {m1:.0f} | {m2:.0f} | {m3:.0f} |")
    out.append("\n### Per-household scores, leave-one-out threshold (pool = the other two)\n")
    out += per_household_table(res5, present5, [(14, 23), (32, 41)], [(24, 31), (42, 49)], "strict", None)
    out.append("\n#### The same with the loose threshold rule (for contrast)")
    out += per_household_table(res5, present5, [(14, 23), (32, 41)], [(24, 31), (42, 49)], "loose", None)
    out.append("\n### Day-by-day counts, days 10-18 and days 28-36\n")
    out += day_table(hh5, present5, list(range(10, 19)), "Around the first change (day 14):")
    out += day_table(hh5, present5, list(range(28, 37)), "Around the second change (day 32):")
    out.append("\n### How high the count runs in each window\n")
    out += level_table(hh5, present5, [(1, 13), (14, 23), (24, 31), (32, 41), (42, 49)])
    out.append("\n### Alarm days under the strict threshold, every day 1-49\n")
    for rule in RULES:
        out.append(f"\nDefinition {RULE_LABEL[rule]}:\n")
        out.append("| household | T | alarm days |")
        out.append("|---|---|---|")
        for n in present5:
            r = res5[rule]["strict"][n]
            out.append(f"| {n} | {r['T']} | {', '.join(map(str, r['alarm_days_all'])) or '-'} |")
    out.append("\n### Does the robot look into the rooms the sick resident's things go to? (first spell)\n")
    out += sick_room_table(hh5, present5, 14)

    out.append("\n## Notes on what makes the number easy or hard\n")
    out.append(NOTES)

    (HERE / "RESULTS_baseline.md").write_text("\n".join(out) + "\n")

    # machine-readable dump
    dump = {}
    for tag, (h, r, p) in {"ten_31day": (hh, res, present), "three_50day": (hh5, res5, present5)}.items():
        dump[tag] = {}
        for n in p:
            dump[tag][n] = {
                "sightings_per_day": dict(sorted(h[n]["sightings_per_day"].items())),
                "looks_per_day": dict(sorted(h[n]["looks_per_day"].items())),
                "surprise_counts": {rule: dict(sorted(h[n]["counts"][rule].items())) for rule in RULES},
                "scores": {rule: {mode: r[rule][mode][n] for mode in ("strict", "loose")} for rule in RULES},
                "sick_rooms": sorted(h[n]["sick_rooms"]),
            }
    (HERE / "counts.json").write_text(json.dumps(dump, indent=1))
    print("\n".join(out))


if __name__ == "__main__":
    main()
