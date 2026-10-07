#!/usr/bin/env python3
"""Study 2, second count: baseline 2 (persistent new place per object) and a word match on
the nightly notes of the log-and-notes method.

Follows the Addendum at the end of SETUP.md beside this file. Reuses the loader and the
leave-one-out scaffolding of surprise_count.py (same folder). CPU only; stdlib only.

Baseline 2, definitions used here, stated once:
- Stream: every sighting from every look, in (day, time, file order), as in surprise_count.py.
  Each object's own stream is the sub-sequence of its sightings in that order.
- A sighting of object o in room r on day d is NEW when none of o's earlier sightings (earlier
  in the stream, so by day and time) with day >= d-7 is in room r. An object with no earlier
  sighting at all in that window (no sighting in any room on days d-7..d before this one) is
  SKIPPED, not new: there is no earlier place for it to have moved from. Without this, day 1
  would count every object as having moved.
- Object o HAS MOVED on day D when sighting i (new, in room r) is followed by sighting i+1
  (the next in o's own stream) also in room r; D is the day of sighting i+1. Variant "later
  day": additionally day(i+1) > day(i). Because the confirming sighting puts r inside the
  seven-day window, the same stay in r cannot fire again; the object fires again only after r
  has been unseen for a week and then regained (e.g. the return). So an object can have more
  than one move day over the run, and the return is counted like the change.
- Daily set M[d] = objects with a move day d. Window count W[d] = |M[d-2] U M[d-1] U M[d]|
  (distinct objects over the three days). Day d is an alarm day when W[d] >= k.
- k for a held-out household: the smallest integer such that every other household in the pool
  has zero alarm days on its days 1-13, i.e. k = 1 + max over the pool of W on days 1-13.
- Scores: delay = first alarm day in 14..23 minus 14 (0 = day 14, "none" if no alarm by day
  23); false alarms = alarm days on days 1-13, raw and times 30/13; return alarms = alarm days
  on days 24-31, reported separately. For the 50-day households also the second spell
  (32..41) and the second return (42..49).

Notes word match, definitions used here:
- The log-and-notes cells have no notes_by_night.jsonl; notes.json is a claim store in which
  every claim keeps first_written_day and a revision_history that stores the prior wording of
  every revision. The text WRITTEN on night n is reconstructed exactly: the statement and
  holds_under of each claim first written on night n (as first worded), plus, for every
  revision made on night n, its "why" text and the statement/holds_under as they stood after
  that revision. A second, looser view is also reported: the whole notes file as it read at
  the end of night n (every claim's statement and holds_under at that time).
- A night matches when the text contains any of the Addendum's words as whole words or stems
  (case-insensitive): ill/illness, sick/sickness, unwell, "not well", resting, changed,
  "no longer", "used to", "now stays", "now keeps", since.
- Delay = first matching night >= 13, minus 14 (night 13 would be -1; night 14 is 0); false
  mentions = matching nights among nights 1-13. The notes are written at the end of each day,
  so night 14 is the first that could have seen day 14.

Writes RESULTS_baseline2_and_notes.md and persistent_move.json beside this script.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from surprise_count import (REPO, TEN_DIR, FIFTY_DIR, TEN_NAMES, FIFTY_NAMES, CAL_DAYS,  # noqa: E402
                            PER_MONTH, WINDOW, SEVEN, load_cell, fmt_delay, mean_sd)

NOTES_DIR = REPO / "results/self_improve/overnight_wave/cells/the_log_and_notes_about_the_routine"
VARIANTS = ("any", "later_day")
VARIANT_LABEL = {"any": "V1: confirming sighting any time later",
                 "later_day": "V2: confirming sighting on a later day"}

WORDS = [("ill", r"\bill(?:ness)?\b"), ("sick", r"\bsick(?:ness)?\b"), ("unwell", r"\bunwell\b"),
         ("not well", r"\bnot\s+well\b"), ("resting", r"\bresting\b"), ("changed", r"\bchanged\b"),
         ("no longer", r"\bno\s+longer\b"), ("used to", r"\bused\s+to\b"),
         ("now stays", r"\bnow\s+stays\b"), ("now keeps", r"\bnow\s+keeps\b"), ("since", r"\bsince\b")]
WORD_RE = [(w, re.compile(p, re.IGNORECASE)) for w, p in WORDS]


# ----------------------------------------------------------------------------- baseline 2

def move_events(stream, variant):
    """Return (events, skipped) where events = [(move_day, object, from_room, to_room,
    first_day, first_time, confirm_time)] and skipped = sightings with no 7-day history."""
    per_obj = collections.defaultdict(list)
    for s in stream:
        per_obj[s["object_id"]].append(s)
    events = []
    skipped = 0
    for obj, sl in per_obj.items():
        for i, s in enumerate(sl):
            d, r = s["day"], s["room"]
            window = [t for t in sl[:i] if t["day"] >= d - SEVEN]
            if not window:
                skipped += 1
                continue
            if any(t["room"] == r for t in window):
                continue  # not new
            if i + 1 >= len(sl):
                continue  # never confirmed
            nxt = sl[i + 1]
            if nxt["room"] != r:
                continue
            if variant == "later_day" and nxt["day"] <= d:
                continue
            events.append((nxt["day"], obj, sl[i - 1]["room"], r, d, s["time"], nxt["time"]))
    events.sort()
    return events, skipped


def window_counts(events, last_day):
    by_day = collections.defaultdict(set)
    for ev in events:
        by_day[ev[0]].add(ev[1])
    W = {}
    for d in range(1, last_day + 1):
        objs = set()
        for e in range(max(1, d - WINDOW + 1), d + 1):
            objs |= by_day.get(e, set())
        W[d] = len(objs)
    return W, by_day


def alarm_days(W, k, days):
    return [d for d in days if W.get(d, 0) >= k]


def choose_k(pool_W, cal_days=CAL_DAYS):
    return 1 + max(W.get(d, 0) for W in pool_W for d in cal_days)


LATE_CAL_DAYS = list(range(8, 14))  # contrast only: after the seven-day window has filled


def first_alarm_delay(W, k, c0, c1):
    hits = alarm_days(W, k, range(c0, c1 + 1))
    return (hits[0] - c0) if hits else None


def run_set(names, root, spells, returns, last_day_expected):
    hh, missing = {}, []
    for name in names:
        d = root / name
        if not (d / "looks.jsonl").exists():
            missing.append(name)
            continue
        stream, looks_pd, rooms_pd, last_day, movers = load_cell(d)
        rec = {"stream_n": len(stream), "last_day": last_day or last_day_expected,
               "movers": movers, "events": {}, "W": {}, "by_day": {}, "skipped": {}}
        for v in VARIANTS:
            ev, sk = move_events(stream, v)
            rec["events"][v] = ev
            rec["skipped"][v] = sk
            rec["W"][v], rec["by_day"][v] = window_counts(ev, rec["last_day"])
        hh[name] = rec
    present = [n for n in names if n in hh]
    results = {v: {} for v in VARIANTS}
    late = {v: {} for v in VARIANTS}
    for v in VARIANTS:
        for name in present:
            pool = [hh[o]["W"][v] for o in present if o != name]
            W = hh[name]["W"][v]
            for cal, store in ((CAL_DAYS, results), (LATE_CAL_DAYS, late)):
                k = choose_k(pool, cal)
                fa = len(alarm_days(W, k, cal))
                store[v][name] = {
                    "k": k, "cal_days": [cal[0], cal[-1]],
                    "false_alarms_raw": fa, "false_alarms_per_month": fa * 30 / len(cal),
                    "false_alarm_days_1_13": alarm_days(W, k, CAL_DAYS),
                    "delays": [first_alarm_delay(W, k, c0, c1) for c0, c1 in spells],
                    "return_alarms": [len(alarm_days(W, k, range(r0, r1 + 1))) for r0, r1 in returns],
                    "alarm_days_all": alarm_days(W, k, range(1, hh[name]["last_day"] + 1)),
                    "own_max_W_cal": max(W.get(d, 0) for d in cal)}
    return hh, results, late, missing, present


# ----------------------------------------------------------------------------- notes

def nightly_text(notes):
    """night -> (text written that night, text of the whole file at the end of that night)."""
    claims = notes["claims"]
    last = notes.get("written_up_to_day") or max(c["last_revised_day"] for c in claims)
    written = collections.defaultdict(list)
    for c in claims:
        # wording of each version: versions[0] is the first wording; version j+1 is after revision j
        versions = [(h["was"]["statement"], h["was"]["holds_under"]) for h in c["revision_history"]]
        versions.append((c["statement"], c["holds_under"]))
        written[c["first_written_day"]].append(f"[{c['claim_id']} new] {versions[0][0]} "
                                               f"(when: {versions[0][1]})")
        for j, h in enumerate(c["revision_history"]):
            st, hu = versions[j + 1]
            changed_wording = (st != h["was"]["statement"]) or (hu != h["was"]["holds_under"])
            piece = f"[{c['claim_id']} revised] why: {h['why']}"
            if changed_wording:
                piece += f" | now: {st} (when: {hu})"
            written[h["day"]].append(piece)
    state = {}
    for n in range(0, last + 1):
        parts = []
        for c in claims:
            if c["first_written_day"] > n:
                continue
            versions = [(h["was"]["statement"], h["was"]["holds_under"]) for h in c["revision_history"]]
            versions.append((c["statement"], c["holds_under"]))
            # the wording after the last revision made on or before night n
            j = sum(1 for h in c["revision_history"] if h["day"] <= n)
            st, hu = versions[j]
            parts.append(f"[{c['claim_id']}] {st} (when: {hu})")
        state[n] = "\n".join(parts)
    return {n: "\n".join(written.get(n, [])) for n in range(0, last + 1)}, state, last


def match_words(text):
    hits = {}
    for w, rx in WORD_RE:
        m = rx.search(text)
        if m:
            hits[w] = m
    return hits


def line_around(text, m):
    line_start = text.rfind("\n", 0, m.start()) + 1
    line_end = text.find("\n", m.end())
    return text[line_start: (line_end if line_end != -1 else len(text))].strip()


def sentence_around(text, m):
    """The piece (one claim line) that holds the match, trimmed to the sentence."""
    line_start = text.rfind("\n", 0, m.start()) + 1
    line_end = text.find("\n", m.end())
    line = text[line_start: (line_end if line_end != -1 else len(text))]
    # split the line into sentences and return the one containing the match
    pos = m.start() - line_start
    sentences = re.split(r"(?<=[.!?])\s+", line)
    acc = 0
    for s in sentences:
        if acc <= pos < acc + len(s) + 1:
            return s.strip()
        acc += len(s) + 1
    return line.strip()


def notes_study(names):
    out = {}
    for name in names:
        f = NOTES_DIR / name / "notes.json"
        if not f.exists():
            out[name] = None
            continue
        notes = json.load(open(f))
        written, state, last = nightly_text(notes)
        rec = {"last_night": last, "n_claims": len(notes["claims"]), "views": {}}
        for view, texts in (("written", written), ("state", state)):
            per_night = {}
            for n in range(1, last + 1):
                hits = match_words(texts.get(n, ""))
                first_m = hits[min(hits, key=lambda w: hits[w].start())] if hits else None
                per_night[n] = {"words": sorted(hits),
                                "quote": sentence_around(texts[n], first_m) if hits else None,
                                "line": line_around(texts[n], first_m) if hits else None,
                                "n_chars": len(texts.get(n, ""))}
            first = next((n for n in range(13, last + 1) if per_night[n]["words"]), None)
            false_nights = [n for n in CAL_DAYS if per_night[n]["words"]]
            word_tally = collections.Counter(w for n in range(1, last + 1) for w in per_night[n]["words"])
            rec["views"][view] = {"per_night": per_night, "first_match_night": first,
                                  "delay": (first - 14) if first is not None else None,
                                  "false_nights": false_nights, "word_tally": word_tally,
                                  "matching_nights": [n for n in range(1, last + 1) if per_night[n]["words"]]}
        out[name] = rec
    return out


# ----------------------------------------------------------------------------- reporting

def score_table(results, present, spells, returns):
    lines = []
    for v in VARIANTS:
        lines.append(f"\n**{VARIANT_LABEL[v]}**\n")
        a, b = results[v][present[0]]["cal_days"]
        cal_label = f"{a}-{b}"
        head = ["household", "k (alarm when distinct movers in 3 days >= k)", f"own max W days {cal_label}"]
        for c0, _ in spells:
            head.append(f"delay from day {c0}")
        head += [f"false alarm days {cal_label} (raw)", f"false alarms per month (x30/{b - a + 1})"]
        if a != 1:
            head.append("alarm days 1-13 (all, incl. the warm-up week)")
        for r0, r1 in returns:
            head.append(f"alarm days {r0}-{r1} (return)")
        head.append("all alarm days")
        lines.append("| " + " | ".join(head) + " |")
        lines.append("|" + "---|" * len(head))
        for name in present:
            r = results[v][name]
            cells = [name, str(r["k"]), str(r["own_max_W_cal"])]
            cells += [fmt_delay(x) for x in r["delays"]]
            cells += [str(r["false_alarms_raw"]), f"{r['false_alarms_per_month']:.2f}"]
            if a != 1:
                cells.append(", ".join(map(str, r["false_alarm_days_1_13"])) or "-")
            cells += [str(x) for x in r["return_alarms"]]
            cells.append(", ".join(map(str, r["alarm_days_all"])) or "-")
            lines.append("| " + " | ".join(cells) + " |")
        for i, (c0, c1) in enumerate(spells):
            delays = [results[v][n]["delays"][i] for n in present]
            m, sd, n = mean_sd(delays)
            none_n = sum(1 for x in delays if x is None)
            lines.append(f"\nDelay from day {c0}: mean {m}, sd {sd} over n = {n} detected; "
                         f"{none_n} of {len(present)} with no alarm on days {c0}-{c1}.")
        fa = [results[v][n]["false_alarms_per_month"] for n in present]
        lines.append(f"False alarms per month: mean {statistics.mean(fa):.2f}; households with any false alarm day: "
                     f"{sum(1 for n in present if results[v][n]['false_alarms_raw'] > 0)} of {len(present)}.")
        ret = [sum(results[v][n]["return_alarms"]) for n in present]
        lines.append(f"Households with at least one return alarm: {sum(1 for x in ret if x > 0)} of {len(present)}.")
    return lines


def day_table(hh, present, days, title):
    lines = [f"\n{title}\n"]
    head = ["household", "row"] + [f"d{d}" for d in days]
    lines.append("| " + " | ".join(head) + " |")
    lines.append("|" + "---|" * len(head))
    for name in present:
        rec = hh[name]
        for v in VARIANTS:
            lines.append("| " + " | ".join([name, f"moved that day ({v})"] + [str(len(rec["by_day"][v].get(d, set()))) for d in days]) + " |")
            lines.append("| " + " | ".join([name, f"3-day distinct W ({v})"] + [str(rec["W"][v].get(d, 0)) for d in days]) + " |")
    return lines


def level_table(hh, present, windows):
    lines = []
    for v in VARIANTS:
        lines.append(f"\n{VARIANT_LABEL[v]}:\n")
        head = ["household", "move events (whole run)"] + [f"max W d{a}-{b} (on day)" for a, b in windows]
        lines.append("| " + " | ".join(head) + " |")
        lines.append("|" + "---|" * len(head))
        for n in present:
            W = hh[n]["W"][v]
            cells = [n, str(len(hh[n]["events"][v]))]
            for a, b in windows:
                best = max(range(a, b + 1), key=lambda d: (W.get(d, 0), -d))
                cells.append(f"{W.get(best, 0)} (d{best})")
            lines.append("| " + " | ".join(cells) + " |")
    return lines


def fmt_event(ev, movers):
    day, obj, frm, to, d0, t0, t1 = ev
    tag = " [true mover]" if obj in movers else ""
    same = "" if d0 == day else f", first seen there d{d0}"
    return f"{obj}{tag}: {frm} -> {to} (d{day}{same})"


def object_lists(hh, present, change_day, v):
    """Per household: objects that moved on days change..change+2 and in the windows of the three
    loudest settled days (by W)."""
    lines = []
    for name in present:
        rec = hh[name]
        W, by_day, evs = rec["W"][v], rec["by_day"][v], rec["events"][v]
        lines.append(f"\n**{name}** (movers by ground truth, for the reader only: {', '.join(rec['movers'])})\n")
        for d in (change_day, change_day + 1, change_day + 2):
            today = [fmt_event(e, rec["movers"]) for e in evs if e[0] == d]
            lines.append(f"- day {d} (W={W.get(d, 0)}): " + ("; ".join(today) if today else "no object moved"))
        loud = sorted(CAL_DAYS, key=lambda d: (-W.get(d, 0), d))[:3]
        for d in loud:
            win = [fmt_event(e, rec["movers"]) for e in evs if d - 2 <= e[0] <= d]
            lines.append(f"- settled day {d} (W={W.get(d, 0)}, window days {max(1, d - 2)}-{d}): "
                         + ("; ".join(win) if win else "no object moved"))
    return lines


def notes_table(ns, names, view):
    lines = ["| household | claims in file | first matching night >= 13 | delay from night 14 | matching nights 1-13 (false mentions) | all matching nights | words that fired (whole run) |",
             "|---|---|---|---|---|---|---|"]
    delays = []
    for name in names:
        r = ns.get(name)
        if r is None:
            lines.append(f"| {name} | missing | | | | | |")
            continue
        vw = r["views"][view]
        delays.append(vw["delay"])
        tally = ", ".join(f"{w} x{c}" for w, c in sorted(vw["word_tally"].items(), key=lambda t: -t[1]))
        lines.append(f"| {name} | {r['n_claims']} | {vw['first_match_night'] if vw['first_match_night'] is not None else 'none'} | "
                     f"{fmt_delay(vw['delay'])} | {len(vw['false_nights'])} ({', '.join(map(str, vw['false_nights'])) or '-'}) | "
                     f"{', '.join(map(str, vw['matching_nights'])) or '-'} | {tally or '-'} |")
    m, sd, n = mean_sd(delays)
    lines.append(f"\nDelay over households with a matching night >= 13: mean {m}, sd {sd}, n = {n}; "
                 f"{sum(1 for x in delays if x is None)} with none. Households with at least one false mention: "
                 f"{sum(1 for name in names if ns.get(name) and ns[name]['views'][view]['false_nights'])} of {len(names)}.")
    return lines


def main():
    out = []
    out.append("# Study 2, second count: baseline 2 (persistent new place) and a word match on the nightly notes\n")
    out.append("Computed by `persistent_move.py` beside this file. Baseline 2 reads the last-seen (no model) cells, "
               "the same sighting streams as RESULTS_baseline.md. The word match reads the log-and-notes cells. "
               "Definitions are in the script's docstring; the ones that needed a decision are repeated here.\n")
    out.append("- New sighting: object o in room r on day d, and none of o's earlier sightings with day >= d-7 is in r. "
               "An object with no earlier sighting at all in that window is skipped (not new).")
    out.append("- Moved: a new sighting followed, as the object's very next sighting, by another in the same room; the move "
               "day is the day of the confirming sighting. V2 also requires the confirming sighting on a later day.")
    out.append("- W[d] = distinct objects with a move day in d-2..d. Alarm day when W[d] >= k. k = 1 + the largest W on "
               "days 1-13 among the other households (zero alarm days on their days 1-13).")
    out.append("- Delay: first alarm day in 14..23 minus 14 (0 = day 14). False alarms: alarm days 1-13, raw and x30/13. "
               "Return alarms: alarm days 24-31, separate. The 50-day run also scores 32..41 and 42..49.\n")

    hh, res, late, missing, present = run_set(TEN_NAMES, TEN_DIR, [(14, 23)], [(24, 31)], 31)
    out.append("## Baseline 2, ten households, 31 days, 8 questions a day\n")
    out.append(f"Cells under `{TEN_DIR.relative_to(REPO)}`. Present: {len(present)} of {len(TEN_NAMES)}."
               + (f" Missing: {', '.join(missing)}." if missing else " None missing."))
    out.append("\n### Per-household scores, leave-one-out k\n")
    out += score_table(res, present, [(14, 23)], [(24, 31)])
    out.append("\n#### Contrast, not the Addendum's rule: k chosen on days 8-13 only\n")
    out.append("On days 1-7 the seven-day window is still filling, so an object's first visit to each of its ordinary "
               "rooms counts as a new place and its second sighting there as a move; most of the settled peaks above fall "
               "on days 1-6. This table chooses k on the pool's days 8-13 (zero alarm days there) and reports false alarms "
               "on days 8-13 (per month = x30/6), with the alarm days on 1-13 listed in full so the warm-up alarms are visible.")
    out += score_table(late, present, [(14, 23)], [(24, 31)])
    out.append("\n### Day by day, days 10-18\n")
    out.append("Objects whose move day is that day, and the 3-day distinct count W. The change is on day 14.")
    out += day_table(hh, present, list(range(10, 19)), "")
    out.append("\n### How high W runs in each window\n")
    out += level_table(hh, present, [(1, 7), (8, 13), (1, 13), (14, 23), (24, 31)])
    out.append("\n### What the rule reacts to: objects that moved on days 14-16 and in the three loudest settled windows\n")
    out.append("V1 (confirming sighting any time later). Each entry is object: room of the previous sighting -> new room "
               "(move day; the day it was first seen in the new room if earlier). '[true mover]' marks objects in the "
               "cell's ground-truth movers list; the tag is for the reader and is not used by the rule. The settled days "
               "listed are the three days 1-13 with the largest W, and the entries are all moves in that day's 3-day window.")
    out += object_lists(hh, present, 14, "any")

    hh5, res5, late5, missing5, present5 = run_set(FIFTY_NAMES, FIFTY_DIR, [(14, 23), (32, 41)], [(24, 31), (42, 49)], 49)
    out.append("\n## Baseline 2, three households, 50 days, 24 questions a day\n")
    out.append(f"Cells under `{FIFTY_DIR.relative_to(REPO)}`. Present: {len(present5)} of {len(FIFTY_NAMES)}."
               + (f" Missing: {', '.join(missing5)}." if missing5 else " None missing.")
               + " k is chosen on the other two households of this run, as in RESULTS_baseline.md.")
    out.append("\n### Per-household scores, leave-one-out k (pool = the other two)\n")
    out += score_table(res5, present5, [(14, 23), (32, 41)], [(24, 31), (42, 49)])
    out.append("\n#### Contrast, not the Addendum's rule: k chosen on days 8-13 only\n")
    out += score_table(late5, present5, [(14, 23), (32, 41)], [(24, 31), (42, 49)])
    out.append("\n### Day by day\n")
    out += day_table(hh5, present5, list(range(10, 19)), "Around the first change (day 14):")
    out += day_table(hh5, present5, list(range(28, 37)), "Around the second change (day 32):")
    out.append("\n### How high W runs in each window\n")
    out += level_table(hh5, present5, [(1, 7), (8, 13), (1, 13), (14, 23), (24, 31), (32, 41), (42, 49)])
    out.append("\n### What the rule reacts to (first change, V1)\n")
    out += object_lists(hh5, present5, 14, "any")

    # ---- notes
    ns = notes_study(TEN_NAMES)
    out.append("\n## Word match on the nightly notes of the log-and-notes method\n")
    out.append("**This is a word match, not a reading.** A night 'matches' when its text contains one of the listed words; "
               "a match does not mean the note describes the change, and the quoted sentences below are there so a reader "
               "can judge that.\n")
    out.append(f"Cells under `{NOTES_DIR.relative_to(REPO)}`. These cells have no notes_by_night.jsonl and no nightly "
               "summaries; the notes are a claim store (notes.json) in which each claim keeps the night it was first "
               "written and the prior wording of every revision, so the text written on each night is rebuilt exactly "
               "(new claims as first worded, plus each revision's reason and the wording after it). Two views are scored:")
    out.append("- *written that night*: only the text the model added or changed on night n (the primary view);")
    out.append("- *whole file at end of night*: every claim as it read at the end of night n (a claim written on night 3 "
               "containing 'since' matches every later night under this view).")
    out.append(f"\nWords: {', '.join(w for w, _ in WORDS)} (case-insensitive; ill/sick also match illness/sickness). "
               "Delay = first matching night >= 13, minus 14. False mentions = matching nights among 1-13.")
    out.append("\n### View 1: text written that night\n")
    out += notes_table(ns, TEN_NAMES, "written")
    out.append("\n### View 2: whole notes file as it read at the end of the night\n")
    out += notes_table(ns, TEN_NAMES, "state")

    out.append("\n### Quoted sentences, view 1, from the first matching night >= 13\n")
    out.append("Three households chosen as the first three in the study's household order that have a matching night; "
               "the sentence is the one that holds the first match in that night's text, with the claim id and whether the "
               "line is a new claim or a revision. Below those, one line per remaining household, so nothing is hidden.\n")
    quoted = 0
    for name in TEN_NAMES:
        r = ns.get(name)
        if r is None:
            continue
        vw = r["views"]["written"]
        n = vw["first_match_night"]
        if n is None:
            out.append(f"- **{name}**: no matching night 13-31.")
            continue
        pn = vw["per_night"][n]
        out.append(f"- **{name}**, night {n} (delay {fmt_delay(vw['delay'])}), words {', '.join(pn['words'])}: \"{pn['quote']}\"")
        if quoted < 3:
            out.append(f"  - the whole note line it sits in: `{pn['line']}`")
        quoted += 1
    out.append("\n### The false mentions, view 1: the sentence behind each matching night 1-13\n")
    for name in TEN_NAMES:
        r = ns.get(name)
        if r is None:
            continue
        vw = r["views"]["written"]
        for n in vw["false_nights"]:
            pn = vw["per_night"][n]
            out.append(f"- {name}, night {n}, words {', '.join(pn['words'])}: \"{pn['quote']}\"")
    if not any(ns.get(name) and ns[name]["views"]["written"]["false_nights"] for name in TEN_NAMES):
        out.append("- none")

    out.append("\n## Plain notes on anything odd\n")
    out.append(ODD_NOTES)

    (HERE / "RESULTS_baseline2_and_notes.md").write_text("\n".join(out) + "\n")

    dump = {}
    for tag, (h, r, l, p) in {"ten_31day": (hh, res, late, present), "three_50day": (hh5, res5, late5, present5)}.items():
        dump[tag] = {}
        for n in p:
            dump[tag][n] = {
                "scores": {v: r[v][n] for v in VARIANTS},
                "scores_k_from_days_8_13": {v: l[v][n] for v in VARIANTS},
                "W": {v: dict(sorted(h[n]["W"][v].items())) for v in VARIANTS},
                "events": {v: h[n]["events"][v] for v in VARIANTS},
                "skipped": h[n]["skipped"],
                "movers": h[n]["movers"]}
    dump["notes"] = {}
    for n, r in ns.items():
        if r is None:
            dump["notes"][n] = None
            continue
        dump["notes"][n] = {view: {"first_match_night": vw["first_match_night"], "delay": vw["delay"],
                                   "false_nights": vw["false_nights"], "matching_nights": vw["matching_nights"],
                                   "word_tally": dict(vw["word_tally"]),
                                   "per_night": {k: {"words": p["words"], "quote": p["quote"]} for k, p in vw["per_night"].items()}}
                            for view, vw in r["views"].items()}
    (HERE / "persistent_move.json").write_text(json.dumps(dump, indent=1, default=list))
    print("\n".join(out))


ODD_NOTES = """\
Written after reading the tables above. Figures quoted are from this file (ten-household run unless said).

1. Under the Addendum's rule (k from days 1-13, zero alarm days in the pool), baseline 2 V1 detects 1 of 10
   households (hh_s48, delay 1) at zero false alarm days and one return-alarm household; V2 detects 0 of 10 with
   one false alarm day (hh_s2, day 4). k is 9 for V1 in every household (7 for V2), set by hh_s48 and hh_s151,
   whose largest settled W (8) falls on days 4 and 6. The Addendum's prediction (0-2 days in at least seven of
   ten) is not met under this rule.

2. The settled peaks are a warm-up effect of the definition, not meal-time moves persisting. On days 1-7 the
   seven-day window is still filling: the first time an object is seen in each of its ordinary rooms (crockery
   seen in the dining room on day 1 and in the kitchen on day 2) the room has no earlier sighting, so the
   object counts as having moved there. The largest settled W is on days 1-6 in 9 of 10 households; on days
   8-13 W never exceeds 4 (hh_s48) and is 0 to 3 elsewhere, while the sick-window peaks are 3 to 9. The
   object lists for the loudest settled windows show it: plates, bowls and glasses kitchen <-> dining on days
   1-4, and a resident's charger, headphones, pen first seen in one room and then another. The Addendum says
   days 1-13, so that is the rule reported; the days-8-13 contrast is labelled as a contrast.

3. Under the contrast (k from days 8-13: k = 5 for V1, 4 or 3 for V2), V1 detects 4 of 10 (hh_s48 0,
   hh_s20 1, hh_s93 1, hh_s123 4; mean 1.5, sd 1.7), with one false alarm day on days 8-13 (hh_s48 day 13,
   W = 4 from a jacket, a hair dryer, a scarf and a towel moving between entry, bathroom and bedrooms on days 11-13) and warm-up alarms on days 2-6 in 4 households
   (hh_s2, hh_s48, hh_s109, hh_s151). Return alarms then appear in 6 of 10. V2 detects 3 of 10 (delays 1,
   1, 4). Six (V1) or seven (V2) households are still not detected within the sick window.

4. Why the change gives small counts. The rule needs two consecutive sightings of the same object in a room
   it had not been seen in for a week; one look into the bedroom gives the first sighting, and the confirming
   one needs a later look into the same room before the object is seen anywhere else. Of the 5-9 ground-truth
   movers per household, 3 to 6 get a move day inside days 14-23 (hh_s2 4 of 8, hh_s19 3 of 7, hh_s20 6 of 9,
   hh_s32 4 of 8, hh_s48 4 of 6, hh_s63 5 of 9, hh_s93 6 of 9, hh_s109 3 of 6, hh_s123 3 of 5, hh_s151 3 of
   8), and they do not all fall in one three-day window: the daily "moved" counts on days 14-16 are 0 to 6.
   Objects outside the movers list also move with the sick resident (vitamins, blanket_shared, headphones,
   skincare, toiletry bag, tablet) and count the same. hh_s123's first moves are on days 17-18 although it
   looked into the sick rooms on day 14 (RESULTS_baseline.md): its objects were each seen once there, not
   twice in a row, until day 17.

5. V2 (confirming sighting on a later day) halves the move events (e.g. hh_s2 23 -> 12, hh_s48 34 -> 18) and
   removes most of the day-14 and day-15 events, because two looks into the bedroom on the same sick day are
   what usually confirm a move. It lowers the warm-up peaks less than it lowers the sick-window peaks in most
   households.

6. 50-day run (24 questions a day). hh_s48 is louder than the other two in its own settled week (W = 12 on
   day 3 against k = 9 from hh_s2 and hh_s32), so it has 3 false alarm days (2, 3, 4; 6.9 a month) and detects
   the first spell at delay 0 but not the second (W peaks at 6 on days 32-41, under 9). hh_s2 and hh_s32 get
   k = 13 from hh_s48 and detect nothing in either spell (their spell peaks are 8 and 6, 7 and 11). Under the
   days-8-13 contrast V1 detects both spells in all three (delays 1, 4, 0 and 0, 0, 0), with 8 to 20 alarm
   days per household over the run and hh_s48 at k = 2 alarming on 40 of 49 days.

7. Notes word match. None of ill, sick, illness, sickness, unwell or "not well" appears in any night's text in
   any of the ten households, in either view. The words that fire are changed (19 nights), no longer (9),
   since (5), resting (7), almost all in a revision's "why" line about one object's place within a day
   ("Location changed from counter to sink between 15:10 and 20:59"). View 1 (text written that night): 7 of 10
   households have a matching night on or after night 13 (nights 13, 15, 16, 17, 19, 19, 20; delays -1 to 6,
   mean 3.0, sd 2.5); 5 of 10 have false mentions on nights 1-13 (1 to 5 nights). The first-match sentences
   on or after night 13 are about: a plate (hh_s2, night 20), Hana's office being empty on day 16 (hh_s20,
   night 16; Hana's things are the movers in that household), a razor on a sink "since Day 9" (hh_s48, night
   13), a medication's side table (hh_s93, night 19), a glasses' coffee table (hh_s109), a counter-to-sink
   move (hh_s123), Dana's towel shelf-to-rack (hh_s151, night 15; towel_dana is in that household's movers
   list). The reader decides which of these describe the change; the word match does not.

8. View 2 (the whole file as it read each night) matches less than view 1 because a revision's "why" text is
   not part of the file state, only the statement and holds_under are; 2 of 10 households match on or after
   night 13 under view 2. The Addendum's "first night whose note contains" is closer to view 1.

9. Night 13 is counted as "on or after night 13" as the brief says, so hh_s48's delay is -1; the match on that
   night (razor, "since Day 9") precedes the change.

10. Mechanics worth knowing. The log-and-notes cells hold no notes_by_night.jsonl; the per-night text was
    rebuilt from notes.json's claims (first_written_day and revision_history keep every earlier wording), so
    it is exact for what was written, including wording later overwritten. Sightings skipped for having no
    sighting of the object in the previous seven days: 79 of 2,537 in hh_s2 (first sightings and
    reappearances after a week unseen). The word list was applied to all text, not only to text "applied to a
    resident or an object" as the Addendum says; no such filter was attempted.
"""


if __name__ == "__main__":
    main()
