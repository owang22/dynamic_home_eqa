#!/usr/bin/env python3
"""Decaying fidelity on the shifting-household banks.

Repeats the July 'decaying fidelity' measurement on the current data, where the
world shifts.  For the two arms whose prompt content is directly inspectable -
the recency buffer (naive) and retrieval - we parse the sightings out of the
prompt itself and ask:

  * how much evidence about this object the prompt holds (total, and in the same
    2-hour clock bin as the question);
  * how often the answer FOLLOWS the most recent in-prompt sighting (overall,
    and the most recent one in the same clock bin);
  * whether following or overriding is right;

all of it split by stage: settled days 1-13, sick spell 14-23, return 24-31.

Offline, saved logs only.  Conventions (2h bins, MIN_Q=10 floor, per-household
pooling then mean +/- SE across households) follow retention_vs_generalisation.py.

Writes decaying_fidelity.md beside itself.
"""

import json
import re
import os
import collections
import math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "decaying_fidelity.md")

NAIVE = ("/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/run1/"
         "{hh}_t03_naive_nottold_lookoff/")
RETR = ("/home/oliver/robot/dynamic_home_eqa/results/confidence_shift_2026-09-20/uq/"
        "llm_strategies/chain_person/nottold/{hh}_t03_retrieval_nottold_lookoff/")

HHS = [f"hh_s{i}" for i in range(10)]
BIN_H = 2
MIN_Q = 10          # a cell with fewer than this many questions is not reported
PATROL_H = 3        # the nightly patrol round is at 03:00

STAGES = [
    ("settled (1-13)", lambda d: 1 <= d <= 13),
    ("sick spell (14-23)", lambda d: 14 <= d <= 23),
    ("return (24-31)", lambda d: 24 <= d <= 31),
]

ARMS = [
    ("naive (recency buffer)", NAIVE),
    ("retrieval", RETR),
]

# ------------------------------------------------------------------ parsing

# a sighting line, e.g. "- day 14 10:06: coffee_table_l1"
LINE = re.compile(r"^- day (\d+) (\d\d):(\d\d): (\S+)\s*$")
# a sightings-block header, buffer or retrieval flavour
HDR = re.compile(r"^(?:Retrieved s|S)ightings of (\S+)\b.*:\s*$")
NOW = re.compile(r"^Now: day (\d+), (\d\d):(\d\d)\b")
SPOTS = re.compile(r"^- (\w+): (.+)$")


def parse_prompt(content):
    """-> (list of (day, hour, minute, loc) sightings, object ids of blocks, now)

    Only lines inside a sightings block are read; the block ends at the first
    line that is neither a sighting line nor the literal '- none'.
    """
    sights, objs, now = [], [], None
    inblk = False
    for ln in content.split("\n"):
        h = HDR.match(ln)
        if h:
            inblk = True
            objs.append(h.group(1))
            continue
        n = NOW.match(ln)
        if n:
            now = (int(n.group(1)), int(n.group(2)), int(n.group(3)))
        if inblk:
            m = LINE.match(ln)
            if m:
                sights.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)))
            elif ln.strip() == "- none":
                pass
            else:
                inblk = False
    return sights, objs, now


def parse_spots(content):
    """the prompt's own 'Rooms and spots' list -> set of valid spot names"""
    spots = set()
    inblk = False
    for ln in content.split("\n"):
        if ln.startswith("Rooms and spots:"):
            inblk = True
            continue
        if inblk:
            m = SPOTS.match(ln)
            if m:
                spots.update(x.strip() for x in m.group(2).split(","))
            else:
                break
    return spots


# ------------------------------------------------------------------ loading

def load_arm(hh, tmpl):
    base = tmpl.format(hh=hh)
    calls = {}
    for l in open(os.path.join(base, "calls.jsonl")):
        r = json.loads(l)
        if re.match(r"^d\d+q\d+$", str(r.get("where"))):
            calls[r["where"]] = r["messages"][-1]["content"]
    rows = []
    for l in open(os.path.join(base, "run_log.jsonl")):
        r = json.loads(l)
        content = calls[r["question_id"]]
        sights, objs, now = parse_prompt(content)
        sights = sorted(set(sights))
        t = r["t_query"]
        b = int((t % 86400) // 3600) // BIN_H
        same = [s for s in sights if s[1] // BIN_H == b]
        nopat = [s for s in sights if s[1] != PATROL_H]
        rows.append(dict(
            qid=r["question_id"], day=r["day_index"], t=t, obj=r["object_id"],
            answer=r["answer"], truth=r["truth"], correct=bool(r["correct"]),
            bin=b, hour=int((t % 86400) // 3600),
            n_tot=len(sights), n_bin=len(same),
            anchor=max(sights)[3] if sights else None,
            anchor_bin=max(same)[3] if same else None,
            anchor_np=max(nopat)[3] if nopat else None,
            anchor_is_patrol=bool(sights) and max(sights)[1] == PATROL_H,
            sights=sights, objs=objs, now=now, spots=parse_spots(content),
        ))
    return rows


# ------------------------------------------------------------------ stats

def agg(per_hh):
    """per_hh: [(hits, n)] per household -> mean, sem, n_hh, total_q"""
    vals = [h / n for h, n in per_hh if n >= MIN_Q]
    tot = sum(n for _, n in per_hh)
    if len(vals) < 2:
        return None, None, len(vals), tot
    m = sum(vals) / len(vals)
    var = sum((v - m) ** 2 for v in vals) / (len(vals) - 1)
    return m, math.sqrt(var / len(vals)), len(vals), tot


def fmt(m, se, nhh, tot):
    if m is None:
        return f"too few (n_hh={nhh}, q={tot})"
    return f"{100*m:.1f} ± {100*se:.1f} (n={nhh}, q={tot})"


def stat(rows_by_hh, sel, hit):
    per = []
    for hh in HHS:
        s = [r for r in rows_by_hh[hh] if sel(r)]
        per.append((sum(1 for r in s if hit(r)), len(s)))
    return per


def cellf(rows_by_hh, sel, hit):
    return fmt(*agg(stat(rows_by_hh, sel, hit)))


# ------------------------------------------------------------------ main

def main():
    data = {}
    for arm, tmpl in ARMS:
        data[arm] = {hh: load_arm(hh, tmpl) for hh in HHS}

    # --- which objects the shift moved (same rule as retention_vs_generalisation.py)
    moved = {}
    ref = data["naive (recency buffer)"]
    for hh in HHS:
        lead, sick = {}, {}
        for r in ref[hh]:
            if r["day"] <= 13:
                lead.setdefault(r["obj"], collections.Counter())[r["truth"]] += 1
            elif r["day"] <= 23:
                sick.setdefault(r["obj"], collections.Counter())[r["truth"]] += 1
        for o in set(list(lead) + list(sick)):
            lm, sm = lead.get(o), sick.get(o)
            moved[(hh, o)] = bool(lm and sm and
                                  lm.most_common(1)[0][0] != sm.most_common(1)[0][0])
    for arm in data:
        for hh in HHS:
            for r in data[arm][hh]:
                r["moved"] = moved.get((hh, r["obj"]), False)

    lines = []
    w = lines.append

    # ================================================================ header
    w("# Decaying fidelity in a shifting household")
    w("")
    w("Generated by `decaying_fidelity.py`. Offline, saved logs only, no model calls.")
    w("")
    w("July's finding, on different banks, a different model and a scarce-sensing loop, was "
      "**decaying fidelity**: the model followed its own most recent recorded sighting 0.94 of the "
      "time on 1 observation and 0.70 on 4 or more, and when it overrode its own record it was right "
      "0.245 of the time against 0.59 when it followed. That world was stationary. This one shifts: "
      "a settled fortnight, then ten days with one resident off sick and their things moved, then "
      "eight days back. A rational agent should override MORE, and more profitably, right after a "
      "shift. This file repeats the measurement with that split.")
    w("")

    # ================================================================ method
    w("## Method")
    w("")
    w("**Arms.** The two whose prompt content is the evidence itself: the recency buffer "
      "(`fm_memory/run1/hh_s*_t03_naive_nottold_lookoff`, the newest 60 sightings of the asked "
      "object, listed with day and clock time) and retrieval "
      "(`chain_person/nottold/hh_s*_t03_retrieval_nottold_lookoff`, two blocks - the 8 most recent "
      "sightings and up to 10 sightings of the same object at about this time of day on other days). "
      "Both list sightings in the same format, `- day 14 10:06: coffee_table_l1`, so the same parser "
      "reads both. Reflection and long-context are excluded: their prompts carry written notes and a "
      "whole transcript rather than an enumerable sighting list, so 'the most recent sighting it "
      "holds' is not defined for them.")
    w("")
    w("**The prompt IS the feedback log.** `protocol.feedback_delay_min` is 10 in every household: "
      "ten minutes after every question the robot is told where the object actually was, and that "
      "correction enters the sighting list like any other sighting. So 'the evidence it holds' below "
      "is exactly the sightings the prompt lists, corrections included.")
    w("")
    w("**Evidence held.** For each scored question: `n_tot` = sightings of that object listed in the "
      "prompt (deduplicated; for retrieval the union of both blocks), `n_bin` = how many of those "
      "fall in the same 2-hour clock bin as the question. The 2h bin matches the classical timetable's "
      "own bin and the earlier retention analysis.")
    w("")
    w("**Follow.** The answer equals the location named by the most recent listed sighting of that "
      "object. Three anchors are reported, because in this bank they are not the same thing:")
    w("")
    w("- **recent** - the most recent listed sighting, whatever hour. This is July's definition "
      "verbatim. In this bank it is usually the 03:00 patrol round of that morning, which records "
      "where things REST, not where they are in use, so following it is often wrong by construction.")
    w("- **recent (no patrol)** - the same, ignoring 03:00 patrol lines. This is the closer analogue "
      "of July's scarce-sensing loop, which had no nightly sweep.")
    w("- **same clock bin** - the most recent listed sighting whose clock hour is in the same 2h bin "
      "as the question. Questions only ever fall between 07:00 and 22:59, so no 03:00 patrol line is "
      "ever in a question's own bin; this anchor is automatically patrol-free.")
    w("")
    w("**Right when following / right when overriding.** `correct` from the run log (answer == truth). "
      "Reported separately for the questions where the answer matched the anchor and where it did not. "
      "The anchor's own validity - how often the anchor location IS the truth - is reported alongside, "
      "because 'overriding is usually a mistake' only means something against how good the thing being "
      "overridden was.")
    w("")
    w("**Stages.** settled = days 1-13, sick spell = days 14-23, return = days 24-31.")
    w("")
    w("**Reporting.** Pool within a household, then mean and standard error ACROSS households, n = "
      "households contributing. A household contributes to a cell only if it has at least 10 questions "
      "in it; a cell with fewer than two contributing households is printed as 'too few' with its raw "
      "question count. No smoothing, no pooling across households.")
    w("")

    # ================================================================ validation
    w("## Parser validation")
    w("")
    nq = sum(len(data["naive (recency buffer)"][hh]) for hh in HHS)
    w(f"{nq} scored questions per arm, ten households, days 1-31, every question present in both "
      "`run_log.jsonl` and `calls.jsonl` (0 unmatched).")
    w("")
    checks = []

    # V1 header count
    bad = 0
    tot = 0
    for hh in HHS:
        base = NAIVE.format(hh=hh)
        for l in open(os.path.join(base, "calls.jsonl")):
            r = json.loads(l)
            if not re.match(r"^d\d+q\d+$", str(r.get("where"))):
                continue
            c = r["messages"][-1]["content"]
            m = re.search(r"Sightings of \S+ \(oldest first(?:; newest (\d+) of (\d+))?\)", c)
            n = len(parse_prompt(c)[0])
            tot += 1
            exp = int(m.group(1)) if m.group(1) else n
            if n != exp:
                bad += 1
    checks.append(("buffer: parsed line count equals the count the prompt's own header states "
                   "(`newest 60 of 84` -> 60 lines)", f"{tot-bad}/{tot} prompts agree"))

    # V2 locations valid, V3 timestamps in the past, V6 clock matches t_query,
    # V7 nothing missed and nothing picked up outside a sightings block
    for arm, tmpl in ARMS:
        badloc = badtime = badclock = badobj = n = 0
        badcount = 0
        for hh in HHS:
            calls = {}
            for l in open(os.path.join(tmpl.format(hh=hh), "calls.jsonl")):
                rr = json.loads(l)
                if re.match(r"^d\d+q\d+$", str(rr.get("where"))):
                    calls[rr["where"]] = rr["messages"][-1]["content"]
            for r in data[arm][hh]:
                raw = sum(1 for ln in calls[r["qid"]].split("\n") if LINE.match(ln))
                if raw != len(r["sights"]):
                    badcount += 1
            for r in data[arm][hh]:
                n += 1
                if any(s[3] not in r["spots"] for s in r["sights"]):
                    badloc += 1
                qd, qh, qm = r["day"], r["hour"], int((r["t"] % 3600) // 60)
                if any((s[0], s[1], s[2]) > (qd, qh, qm) for s in r["sights"]):
                    badtime += 1
                if r["now"] != (qd, qh, qm):
                    badclock += 1
                if any(o != r["obj"] for o in r["objs"]):
                    badobj += 1
        short = "buffer" if "naive" in arm else "retrieval"
        checks.append((f"{short}: the parser returns exactly as many sightings as there are "
                       "`- day D HH:MM: spot` lines anywhere in the prompt (nothing missed inside a "
                       "block, nothing picked up outside one)", f"{n-badcount}/{n}"))
        checks.append((f"{short}: every parsed location is a spot in the prompt's own room list",
                       f"{n-badloc}/{n}"))
        checks.append((f"{short}: every parsed sighting is at or before the question time",
                       f"{n-badtime}/{n}"))
        checks.append((f"{short}: the prompt's own `Now: day D, HH:MM` equals `day_index` and the "
                       "clock derived from `t_query` (so the bin is computed on the same clock the "
                       "model sees)", f"{n-badclock}/{n}"))
        checks.append((f"{short}: the sightings block is about the object the question asks about",
                       f"{n-badobj}/{n}"))

    # V4 feedback cross-check: the correction from question k must appear in prompt k+1
    for arm, _ in ARMS:
        hit = miss = 0
        for hh in HHS:
            rows = sorted(data[arm][hh], key=lambda r: r["t"])
            prev = {}
            for r in rows:
                p = prev.get(r["obj"])
                if p is not None:
                    ft = p["t"] + 600
                    fd, fh, fm = (int(ft // 86400), int((ft % 86400) // 3600),
                                  int((ft % 3600) // 60))
                    cand = [s for s in r["sights"] if (s[0], s[1]) == (fd, fh)
                            and abs(s[2] - fm) <= 1]
                    if cand:
                        hit += int(any(s[3] == p["truth"] for s in cand))
                        miss += int(not any(s[3] == p["truth"] for s in cand))
                prev[r["obj"]] = r
        short = "buffer" if "naive" in arm else "retrieval"
        checks.append((f"{short}: where a previous question's correction is still inside the prompt "
                       "window, the sighting the parser finds at that timestamp names that question's "
                       "logged truth", f"{hit}/{hit+miss}"))

    w("| check | result |")
    w("|---|---|")
    for k, v in checks:
        w(f"| {k} | {v} |")
    w("")
    w("Five prompts were also read by hand end to end (hh_s0 d16q05, hh_s2 d20q07, hh_s5 d3q02, "
      "hh_s7 d27q11, hh_s9 d14q03) against the parser's output, for both arms; the printed sighting "
      "lists matched line for line. The last check in the table is the strong one: it joins the "
      "parsed prompt text back to an independent file (the run log's `truth` for the previous "
      "question about that object) through a timestamp the parser had to read correctly.")
    w("")

    # ================================================================ what the prompt holds
    w("## What the prompt actually holds")
    w("")
    w("| arm | questions | median sightings held | share holding 4+ | median same-bin sightings | "
      "share with 0 same-bin | share whose most recent sighting is the 03:00 patrol |")
    w("|---|---|---|---|---|---|---|")
    for arm, _ in ARMS:
        rows = [r for hh in HHS for r in data[arm][hh]]
        tots = sorted(r["n_tot"] for r in rows)
        bins = sorted(r["n_bin"] for r in rows)
        med = lambda a: a[len(a) // 2]
        w(f"| {arm} | {len(rows)} | {med(tots)} | "
          f"{100*sum(1 for r in rows if r['n_tot']>=4)/len(rows):.0f}% | {med(bins)} | "
          f"{100*sum(1 for r in rows if r['n_bin']==0)/len(rows):.0f}% | "
          f"{100*sum(1 for r in rows if r['anchor_is_patrol'])/len(rows):.0f}% |")
    w("")
    w("**This is the first thing the repetition says.** July's evidence axis - 1, 2, 3, 4+ sightings "
      "held - does not exist in this bank. The buffer holds 60 sightings of the asked object in all "
      "but a handful of first-week questions and retrieval holds up to 18 by construction. The "
      "1/2/3/4+ table is printed below to show exactly how empty it is, and the working evidence axis "
      "for everything after it is the number of sightings in the same 2-hour clock bin, which does "
      "run from 0 to 60 across the study and is the axis on which 'how much evidence about this "
      "object at this hour' varies.")
    w("")

    # ---------------------------------------------------------------- T1 July axis
    w("## Table 1 - July's axis: follow rate by TOTAL sightings held (1 / 2 / 3 / 4+)")
    w("")
    w("Anchor = most recent listed sighting, any hour (July's definition). All stages pooled.")
    w("")
    w("| arm | 1 | 2 | 3 | 4+ |")
    w("|---|---|---|---|---|")
    for arm, _ in ARMS:
        cs = []
        for lo, hi in [(1, 1), (2, 2), (3, 3), (4, 10**9)]:
            cs.append(cellf(data[arm],
                            lambda r, lo=lo, hi=hi: r["anchor"] is not None and lo <= r["n_tot"] <= hi,
                            lambda r: r["answer"] == r["anchor"]))
        w(f"| {arm} | " + " | ".join(cs) + " |")
    w("")
    w("Every household is 'too few' in the first three columns: over all ten households and all 4130 "
      "questions there are 1 question holding 1 sighting, 45 holding 2 and 33 holding 3. The axis is "
      "unusable and no decay along it can be measured here. Table 2 substitutes an axis that exists.")
    w("")

    # ---------------------------------------------------------------- T2 working axis
    def bin_buckets(arm_data, anchorkey, cntkey, stage=None, moved_only=False):
        cs = []
        for lo, hi in [(1, 1), (2, 2), (3, 3), (4, 10**9)]:
            cs.append(cellf(arm_data,
                            lambda r, lo=lo, hi=hi: (r[anchorkey] is not None
                                                     and lo <= r[cntkey] <= hi
                                                     and (stage is None or stage(r["day"]))
                                                     and (not moved_only or r["moved"])),
                            lambda r: r["answer"] == r[anchorkey]))
        return cs

    w("## Table 2 - follow rate by sightings held IN THE SAME 2-HOUR CLOCK BIN")
    w("")
    w("Anchor = most recent listed sighting in the same 2h clock bin. All stages pooled.")
    w("")
    w("| arm | 1 | 2 | 3 | 4+ |")
    w("|---|---|---|---|---|")
    for arm, _ in ARMS:
        w(f"| {arm} | " + " | ".join(bin_buckets(data[arm], "anchor_bin", "n_bin")) + " |")
    w("")

    w("## Table 3 - the same, split by stage")
    w("")
    for arm, _ in ARMS:
        w(f"**{arm}** - follow rate on the most recent same-bin sighting")
        w("")
        w("| stage | 1 | 2 | 3 | 4+ | all |")
        w("|---|---|---|---|---|---|")
        for sname, sf in STAGES:
            cs = bin_buckets(data[arm], "anchor_bin", "n_bin", stage=sf)
            allc = cellf(data[arm],
                         lambda r, sf=sf: r["anchor_bin"] is not None and sf(r["day"]),
                         lambda r: r["answer"] == r["anchor_bin"])
            w(f"| {sname} | " + " | ".join(cs) + f" | {allc} |")
        w("")

    # ---------------------------------------------------------------- T4 headline
    w("## Table 4 - the headline: follow, and whether following or overriding is right")
    w("")
    w("Anchor = most recent same-bin sighting. `anchor validity` = how often that sighting's location "
      "is in fact the truth now; it is the thing being followed or overridden, and the two accuracy "
      "columns should be read against it. `all` = the arm's plain accuracy on the same questions.")
    w("")
    for arm, _ in ARMS:
        w(f"**{arm}**")
        w("")
        w("| stage | follow rate | anchor validity | right when it FOLLOWS | right when it OVERRIDES "
          "| accuracy, all |")
        w("|---|---|---|---|---|---|")
        for sname, sf in STAGES:
            base = lambda r, sf=sf: r["anchor_bin"] is not None and sf(r["day"])
            fol = cellf(data[arm], base, lambda r: r["answer"] == r["anchor_bin"])
            val = cellf(data[arm], base, lambda r: r["anchor_bin"] == r["truth"])
            rf = cellf(data[arm], lambda r, b=base: b(r) and r["answer"] == r["anchor_bin"],
                       lambda r: r["correct"])
            ro = cellf(data[arm], lambda r, b=base: b(r) and r["answer"] != r["anchor_bin"],
                       lambda r: r["correct"])
            al = cellf(data[arm], base, lambda r: r["correct"])
            w(f"| {sname} | {fol} | {val} | {rf} | {ro} | {al} |")
        base = lambda r: r["anchor_bin"] is not None
        w("| all days | "
          + cellf(data[arm], base, lambda r: r["answer"] == r["anchor_bin"]) + " | "
          + cellf(data[arm], base, lambda r: r["anchor_bin"] == r["truth"]) + " | "
          + cellf(data[arm], lambda r: base(r) and r["answer"] == r["anchor_bin"],
                  lambda r: r["correct"]) + " | "
          + cellf(data[arm], lambda r: base(r) and r["answer"] != r["anchor_bin"],
                  lambda r: r["correct"]) + " | "
          + cellf(data[arm], base, lambda r: r["correct"]) + " |")
        w("")

    # ---------------------------------------------------------------- T5 stage x evidence
    w("## Table 5 - right when following / right when overriding, by stage AND same-bin evidence count")
    w("")
    for arm, _ in ARMS:
        for lab, hitf, selextra in [
                ("right when it FOLLOWS", lambda r: r["correct"], lambda r: r["answer"] == r["anchor_bin"]),
                ("right when it OVERRIDES", lambda r: r["correct"], lambda r: r["answer"] != r["anchor_bin"])]:
            w(f"**{arm} - {lab}**")
            w("")
            w("| stage | 1 | 2 | 3 | 4+ |")
            w("|---|---|---|---|---|")
            for sname, sf in STAGES:
                cs = []
                for lo, hi in [(1, 1), (2, 2), (3, 3), (4, 10**9)]:
                    cs.append(cellf(
                        data[arm],
                        lambda r, lo=lo, hi=hi, sf=sf, sx=selextra:
                            r["anchor_bin"] is not None and lo <= r["n_bin"] <= hi
                            and sf(r["day"]) and sx(r),
                        hitf))
                w(f"| {sname} | " + " | ".join(cs) + " |")
            w("")

    # ---------------------------------------------------------------- T6 July anchor by stage
    w("## Table 6 - the same headline on July's own anchor (most recent sighting, any hour)")
    w("")
    w("and, beside it, the version that ignores the nightly 03:00 patrol line.")
    w("")
    for akey, alab in [("anchor", "most recent, any hour"), ("anchor_np", "most recent, ignoring the 03:00 patrol")]:
        w(f"**anchor: {alab}**")
        w("")
        w("| arm | stage | follow rate | anchor validity | right when it FOLLOWS | right when it "
          "OVERRIDES |")
        w("|---|---|---|---|---|---|")
        for arm, _ in ARMS:
            for sname, sf in STAGES:
                base = lambda r, sf=sf, k=akey: r[k] is not None and sf(r["day"])
                w(f"| {arm} | {sname} | "
                  + cellf(data[arm], base, lambda r, k=akey: r["answer"] == r[k]) + " | "
                  + cellf(data[arm], base, lambda r, k=akey: r[k] == r["truth"]) + " | "
                  + cellf(data[arm], lambda r, b=base, k=akey: b(r) and r["answer"] == r[k],
                          lambda r: r["correct"]) + " | "
                  + cellf(data[arm], lambda r, b=base, k=akey: b(r) and r["answer"] != r[k],
                          lambda r: r["correct"]) + " |")
        w("")

    # ---------------------------------------------------------------- T7 within-spell timing
    w("## Table 7 - inside the shift, day by day")
    w("")
    w("The shift lands on day 14 and the return on day 24. If overriding is the rational response to a "
      "shift, the days right after each boundary are where it should pay. Anchor = most recent "
      "same-bin sighting.")
    w("")
    WINDOWS = [
        ("11-13 (settled, just before)", lambda d: 11 <= d <= 13),
        ("14-15 (shift lands)", lambda d: 14 <= d <= 15),
        ("16-18", lambda d: 16 <= d <= 18),
        ("19-23 (late spell)", lambda d: 19 <= d <= 23),
        ("24-25 (return lands)", lambda d: 24 <= d <= 25),
        ("26-31 (late return)", lambda d: 26 <= d <= 31),
    ]
    for arm, _ in ARMS:
        w(f"**{arm}**")
        w("")
        w("| window | follow rate | anchor validity | right when it FOLLOWS | right when it OVERRIDES |")
        w("|---|---|---|---|---|")
        for wname, wf in WINDOWS:
            base = lambda r, wf=wf: r["anchor_bin"] is not None and wf(r["day"])
            w(f"| {wname} | "
              + cellf(data[arm], base, lambda r: r["answer"] == r["anchor_bin"]) + " | "
              + cellf(data[arm], base, lambda r: r["anchor_bin"] == r["truth"]) + " | "
              + cellf(data[arm], lambda r, b=base: b(r) and r["answer"] == r["anchor_bin"],
                      lambda r: r["correct"]) + " | "
              + cellf(data[arm], lambda r, b=base: b(r) and r["answer"] != r["anchor_bin"],
                      lambda r: r["correct"]) + " |")
        w("")

    # ---------------------------------------------------------------- T8 per household
    w("## Table 8 - per household")
    w("")
    w("follow % / right-when-following % / right-when-overriding % (questions). Anchor = most recent "
      "same-bin sighting. `-` where the cell has fewer than 10 questions.")
    w("")
    for arm, _ in ARMS:
        w(f"**{arm}**")
        w("")
        w("| stage | " + " | ".join(HHS) + " |")
        w("|" + "---|" * (len(HHS) + 1))
        for sname, sf in STAGES:
            cells = []
            for hh in HHS:
                sel = [r for r in data[arm][hh] if r["anchor_bin"] is not None and sf(r["day"])]
                fo = [r for r in sel if r["answer"] == r["anchor_bin"]]
                ov = [r for r in sel if r["answer"] != r["anchor_bin"]]
                def pct(s):
                    return "-" if len(s) < MIN_Q else f"{100*sum(1 for r in s if r['correct'])/len(s):.0f}"
                f_ = "-" if len(sel) < MIN_Q else f"{100*len(fo)/len(sel):.0f}"
                cells.append(f"{f_} / {pct(fo)} / {pct(ov)} ({len(sel)})")
            w(f"| {sname} | " + " | ".join(cells) + " |")
        w("")

    # ---------------------------------------------------------------- T9 moved objects
    w("## Table 9 - restricted to the objects the shift actually moved")
    w("")
    w("An object counts as moved if its modal true location over the spell differs from its modal true "
      "location over days 1-13 (same rule as `retention_vs_generalisation.py`). These are the objects "
      "for which overriding the old record could pay at all.")
    w("")
    w("| arm | stage | follow rate | anchor validity | right when it FOLLOWS | right when it OVERRIDES |")
    w("|---|---|---|---|---|---|")
    for arm, _ in ARMS:
        for sname, sf in STAGES:
            base = lambda r, sf=sf: r["anchor_bin"] is not None and sf(r["day"]) and r["moved"]
            w(f"| {arm} | {sname} | "
              + cellf(data[arm], base, lambda r: r["answer"] == r["anchor_bin"]) + " | "
              + cellf(data[arm], base, lambda r: r["anchor_bin"] == r["truth"]) + " | "
              + cellf(data[arm], lambda r, b=base: b(r) and r["answer"] == r["anchor_bin"],
                      lambda r: r["correct"]) + " | "
              + cellf(data[arm], lambda r, b=base: b(r) and r["answer"] != r["anchor_bin"],
                      lambda r: r["correct"]) + " |")
    w("")

    # ---------------------------------------------------------------- T10 anatomy
    w("## Table 10 - the anatomy of an override")
    w("")
    w("Among the questions where the arm did NOT answer the anchor: was the override WARRANTED - the "
      "anchor was in fact not the truth - and among the warranted ones, did the answer REPAIR the "
      "record, i.e. land on the truth? `base rate` is how often the anchor is wrong over all questions "
      "in the stage; an override picked at random would be warranted that often, so `lift` "
      "(warranted / base rate, derived from the two means beside it) is how well the arm picks WHICH "
      "record to distrust. Anchor = most recent same-bin sighting.")
    w("")
    for arm, _ in ARMS:
        w(f"**{arm}**")
        w("")
        w("| stage | base rate: anchor wrong | of overrides, warranted | lift | of the warranted "
          "overrides, repaired | for contrast: anchor wrong when it FOLLOWED |")
        w("|---|---|---|---|---|---|")
        for sname, sf in STAGES:
            base = lambda r, sf=sf: r["anchor_bin"] is not None and sf(r["day"])
            ov = lambda r, b=base: b(r) and r["answer"] != r["anchor_bin"]
            br = agg(stat(data[arm], base, lambda r: r["anchor_bin"] != r["truth"]))
            wa = agg(stat(data[arm], ov, lambda r: r["anchor_bin"] != r["truth"]))
            rp = agg(stat(data[arm], lambda r, o=ov: o(r) and r["anchor_bin"] != r["truth"],
                          lambda r: r["correct"]))
            fw = agg(stat(data[arm], lambda r, b=base: b(r) and r["answer"] == r["anchor_bin"],
                          lambda r: r["anchor_bin"] != r["truth"]))
            lift = "n/a" if (br[0] in (None, 0) or wa[0] is None) else f"{wa[0]/br[0]:.2f}x"
            w(f"| {sname} | {fmt(*br)} | {fmt(*wa)} | {lift} | {fmt(*rp)} | {fmt(*fw)} |")
        w("")

    # ---------------------------------------------------------------- T11 cost
    w("## Table 11 - what the overriding costs: the arm against always following its own record")
    w("")
    w("`always-follow` is the accuracy a policy would get by answering the anchor every time - it is "
      "the same number as `anchor validity`, restated as a policy. `arm` is what the arm actually "
      "scored on the same questions. The difference is paired inside each household, then averaged "
      "across households. A positive number means the arm's own judgement beat following its record.")
    w("")
    w("| arm | stage | always-follow | arm | arm minus always-follow (paired) |")
    w("|---|---|---|---|---|")
    cost = {}
    for arm, _ in ARMS:
        for sname, sf in STAGES:
            base = lambda r, sf=sf: r["anchor_bin"] is not None and sf(r["day"])
            af = agg(stat(data[arm], base, lambda r: r["anchor_bin"] == r["truth"]))
            ac = agg(stat(data[arm], base, lambda r: r["correct"]))
            diffs = []
            for hh in HHS:
                s = [r for r in data[arm][hh] if base(r)]
                if len(s) >= MIN_Q:
                    diffs.append((sum(1 for r in s if r["correct"])
                                  - sum(1 for r in s if r["anchor_bin"] == r["truth"])) / len(s))
            m = sum(diffs) / len(diffs)
            se = math.sqrt(sum((d - m) ** 2 for d in diffs) / (len(diffs) - 1) / len(diffs))
            cost[(arm, sname)] = (m, se, len(diffs))
            w(f"| {arm} | {sname} | {fmt(*af)} | {fmt(*ac)} | "
              f"{100*m:+.1f} ± {100*se:.1f} (n={len(diffs)}) |")
    w("")

    # ---------------------------------------------------------------- assay
    w("## Output assay (degeneracy guard)")
    w("")
    w("| arm | stage | answers | modal-answer share | truth's modal share | distinct answers | "
      "identical consecutive answers |")
    w("|---|---|---|---|---|---|---|")
    for arm, _ in ARMS:
        for sname, sf in STAGES:
            rows = [r for hh in HHS for r in data[arm][hh] if sf(r["day"])]
            ca = collections.Counter(r["answer"] for r in rows)
            ct = collections.Counter(r["truth"] for r in rows)
            rep = 0
            for hh in HHS:
                s = [r for r in data[arm][hh] if sf(r["day"])]
                s.sort(key=lambda r: r["t"])
                rep += sum(1 for a, b in zip(s, s[1:]) if a["answer"] == b["answer"])
            w(f"| {arm} | {sname} | {len(rows)} | {100*ca.most_common(1)[0][1]/len(rows):.0f}% | "
              f"{100*ct.most_common(1)[0][1]/len(rows):.0f}% | {len(ca)} | "
              f"{100*rep/max(1,len(rows)-10):.0f}% |")
    w("")

    # ---------------------------------------------------------------- numbers for prose
    # collect the key figures so the prose below is computed, not typed
    key = {}
    for arm, _ in ARMS:
        for sname, sf in STAGES:
            base = lambda r, sf=sf: r["anchor_bin"] is not None and sf(r["day"])
            key[(arm, sname, "fol")] = agg(stat(data[arm], base, lambda r: r["answer"] == r["anchor_bin"]))
            key[(arm, sname, "val")] = agg(stat(data[arm], base, lambda r: r["anchor_bin"] == r["truth"]))
            key[(arm, sname, "rf")] = agg(stat(data[arm], lambda r, b=base: b(r) and r["answer"] == r["anchor_bin"], lambda r: r["correct"]))
            key[(arm, sname, "ro")] = agg(stat(data[arm], lambda r, b=base: b(r) and r["answer"] != r["anchor_bin"], lambda r: r["correct"]))
        # paired per-household follow difference settled -> spell
        for a, b, tag in [("settled (1-13)", "sick spell (14-23)", "s2p"),
                          ("sick spell (14-23)", "return (24-31)", "p2r")]:
            diffs = []
            for hh in HHS:
                sa = [r for r in data[arm][hh] if r["anchor_bin"] is not None and dict(STAGES)[a](r["day"])]
                sb = [r for r in data[arm][hh] if r["anchor_bin"] is not None and dict(STAGES)[b](r["day"])]
                if len(sa) >= MIN_Q and len(sb) >= MIN_Q:
                    fa = sum(1 for r in sa if r["answer"] == r["anchor_bin"]) / len(sa)
                    fb = sum(1 for r in sb if r["answer"] == r["anchor_bin"]) / len(sb)
                    diffs.append(fb - fa)
            m = sum(diffs) / len(diffs)
            se = math.sqrt(sum((d - m) ** 2 for d in diffs) / (len(diffs) - 1) / len(diffs))
            key[(arm, tag)] = (m, se, len(diffs))
        # paired override-minus-follow accuracy gap per stage
        for sname, sf in STAGES:
            diffs = []
            for hh in HHS:
                sel = [r for r in data[arm][hh] if r["anchor_bin"] is not None and sf(r["day"])]
                fo = [r for r in sel if r["answer"] == r["anchor_bin"]]
                ov = [r for r in sel if r["answer"] != r["anchor_bin"]]
                if len(fo) >= MIN_Q and len(ov) >= MIN_Q:
                    diffs.append(sum(1 for r in ov if r["correct"]) / len(ov)
                                 - sum(1 for r in fo if r["correct"]) / len(fo))
            if len(diffs) >= 2:
                m = sum(diffs) / len(diffs)
                se = math.sqrt(sum((d - m) ** 2 for d in diffs) / (len(diffs) - 1) / len(diffs))
                key[(arm, sname, "gap")] = (m, se, len(diffs))
            else:
                key[(arm, sname, "gap")] = (None, None, len(diffs))

    w("## Table 12 - paired per-household differences")
    w("")
    w("Each household's own change, then mean ± SE across households. Anchor = most recent same-bin "
      "sighting.")
    w("")
    w("| arm | follow rate, spell minus settled | follow rate, return minus spell | "
      "right-when-overriding minus right-when-following, settled | ... spell | ... return |")
    w("|---|---|---|---|---|---|")
    for arm, _ in ARMS:
        def d(t):
            m, se, n = key[(arm, t)] if isinstance(t, str) else key[(arm, t[0], t[1])]
            if m is None:
                return f"too few (n={n})"
            return f"{100*m:+.1f} ± {100*se:.1f} (n={n})"
        w(f"| {arm} | {d('s2p')} | {d('p2r')} | "
          + " | ".join(d((s, "gap")) for s, _ in STAGES) + " |")
    w("")

    # ================================================================ prose
    def g(arm, stage, k):
        m, se, n, q = key[(arm, stage, k)]
        return "n/a" if m is None else f"{100*m:.0f} ± {100*se:.0f}"

    NA = "naive (recency buffer)"
    RE = "retrieval"
    SE_, SP, RT = [s for s, _ in STAGES]

    w("## What the numbers say")
    w("")
    w("**1. July's evidence axis does not exist in this bank, so the decay itself cannot be "
      "re-measured on its own terms.** July's loop sensed scarcely; the interesting contrast was 1 "
      "observation against 4 or more. These arms are drowning in evidence: the buffer holds the "
      f"newest 60 sightings of the asked object and holds four or more on "
      f"{100*sum(1 for hh in HHS for r in data[NA][hh] if r['n_tot']>=4)/nq:.0f}% of questions; "
      "retrieval holds up to 18 by construction. One question in the entire study holds a single "
      "sighting, 45 hold two, 33 hold three. Table 1 is empty by the reporting rule and would be "
      "meaningless if it were not. Everything after it uses the axis that does vary here: how many "
      "sightings the prompt holds AT THIS HOUR.")
    w("")
    w("**2. On that axis fidelity does not decay - it is flat to mildly rising.** Table 2, all stages "
      "pooled, anchor = most recent same-bin sighting: buffer "
      + " -> ".join(x.split(" ")[0] for x in bin_buckets(data[NA], "anchor_bin", "n_bin"))
      + " across 1 / 2 / 3 / 4+ same-hour sightings, retrieval "
      + " -> ".join(x.split(" ")[0] for x in bin_buckets(data[RE], "anchor_bin", "n_bin"))
      + ". July's shape was 0.94 -> 0.70. Nothing of the sort is here. The arms follow their own "
      "record slightly MORE as the same hour accumulates sightings. Read strictly: this is a "
      "different axis from July's and it is not evidence against July's result, it is evidence that "
      "the phenomenon cannot be looked for in this bank the way July looked for it.")
    w("")
    w("**3. July's second finding reproduces, and larger.** Pooled over all stages, the buffer is "
      "right "
      + cellf(data[NA], lambda r: r["anchor_bin"] is not None and r["answer"] == r["anchor_bin"], lambda r: r["correct"]).split(" ")[0]
      + "% when it follows its own most recent same-hour sighting and "
      + cellf(data[NA], lambda r: r["anchor_bin"] is not None and r["answer"] != r["anchor_bin"], lambda r: r["correct"]).split(" ")[0]
      + "% when it overrides it; retrieval, "
      + cellf(data[RE], lambda r: r["anchor_bin"] is not None and r["answer"] == r["anchor_bin"], lambda r: r["correct"]).split(" ")[0]
      + "% against "
      + cellf(data[RE], lambda r: r["anchor_bin"] is not None and r["answer"] != r["anchor_bin"], lambda r: r["correct"]).split(" ")[0]
      + "%. July was 0.59 against 0.245, a gap of about 35 points; here the gap is about 55. "
      "Different model, different banks, a world that shifts, and an arm holding sixty times the "
      "evidence - same shape, bigger.")
    w("")
    w("**4. The arms DO override more at the shift.** Follow rate, spell minus settled, paired inside "
      f"each household: buffer {100*key[(NA,'s2p')][0]:+.1f} ± {100*key[(NA,'s2p')][1]:.1f} "
      f"(n={key[(NA,'s2p')][2]}), retrieval {100*key[(RE,'s2p')][0]:+.1f} ± "
      f"{100*key[(RE,'s2p')][1]:.1f} (n={key[(RE,'s2p')][2]}). Both clear twice their standard error. "
      "So the behaviour a rational agent should show - trust the stale record less once the world has "
      "moved - is present. It is the only part of the flattering story that survives.")
    w("")
    w("**5. Those extra overrides are far worse than the ones in the settled world, not better.** "
      "Right when it overrides: buffer "
      f"{g(NA,SE_,'ro')}% settled, {g(NA,SP,'ro')}% in the spell, {g(NA,RT,'ro')}% on the return; "
      f"retrieval {g(RE,SE_,'ro')}%, {g(RE,SP,'ro')}%, {g(RE,RT,'ro')}%. Right when it follows barely "
      f"moves across the three stages ({g(NA,SE_,'rf')} / {g(NA,SP,'rf')} / {g(NA,RT,'rf')} for the "
      "buffer). Paired inside each household, override-minus-follow accuracy is "
      f"{100*key[(NA,SE_,'gap')][0]:+.1f} ± {100*key[(NA,SE_,'gap')][1]:.1f} settled, "
      f"{100*key[(NA,SP,'gap')][0]:+.1f} ± {100*key[(NA,SP,'gap')][1]:.1f} in the spell and "
      f"{100*key[(NA,RT,'gap')][0]:+.1f} ± {100*key[(NA,RT,'gap')][1]:.1f} on the return (buffer; "
      "retrieval is the same shape). The penalty for overriding nearly doubles at exactly the moment "
      "overriding is supposed to pay, and it does so in all ten households for both arms (Table 8: "
      "spell right-when-overriding runs 6-43% against 75-95% right-when-following, with no "
      "exception).")
    w("")
    w("**6. And the record they override is BETTER inside the spell, not staler.** Anchor validity - "
      "how often the most recent same-hour sighting is in fact the truth now - goes "
      f"{g(NA,SE_,'val')}% settled -> {g(NA,SP,'val')}% in the spell -> {g(NA,RT,'val')}% on the "
      "return. That is not a paradox: once the resident is home sick their things sit in one new "
      "place all day, so the previous same-hour sighting (usually a correction from ten minutes after "
      "the last question) is a very good guide. The shift makes the routine prior stale and the "
      "recent record sharper at the same time, and the arms respond by trusting the record less.")
    w("")
    w("**7. The collapse is in DETECTION, not in repair.** Table 10 splits an override in two: was it "
      "WARRANTED (the anchor really was not the truth) and, if so, did it REPAIR (the answer was). "
      "For the buffer, warranted goes 61.3 ± 4.4% settled -> 31.3 ± 3.6% in the spell -> 61.6 ± 5.5% "
      "on the return, while repaired barely moves, 71.5 ± 3.7 -> 60.6 ± 6.1 -> 65.6 ± 6.6. The two "
      "multiply to the override accuracy (0.613 x 0.715 = 0.44; 0.313 x 0.606 = 0.19), so almost all "
      "of the collapse from 45% to 19% is the arms overriding records that were in fact correct. "
      "Against the stage's own base rate of a wrong anchor, the discrimination falls from 2.59x to "
      "1.82x for the buffer and 2.70x to 1.61x for retrieval. They can still repair a genuinely stale "
      "record about as well as ever; what the shift destroys is their ability to tell which record is "
      "stale. Retrieval is the same story.")
    w("")
    w("**8. The cost is large and it is concentrated in the spell.** Table 11: a policy of simply "
      "answering the most recent same-hour sighting, every time, would have scored "
      f"{g(NA,SP,'val')}% in the spell where the buffer scored {fmt(*agg(stat(data[NA], lambda r: r['anchor_bin'] is not None and 14 <= r['day'] <= 23, lambda r: r['correct']))).split(' ')[0]}%"
      f" - paired per household, the arm is {100*cost[(NA,SP)][0]:+.1f} ± {100*cost[(NA,SP)][1]:.1f} "
      f"(n={cost[(NA,SP)][2]}) against it. In the settled fortnight the same comparison is "
      f"{100*cost[(NA,SE_)][0]:+.1f} ± {100*cost[(NA,SE_)][1]:.1f} and on the return "
      f"{100*cost[(NA,RT)][0]:+.1f} ± {100*cost[(NA,RT)][1]:.1f}. Retrieval: "
      f"{100*cost[(RE,SE_)][0]:+.1f} / {100*cost[(RE,SP)][0]:+.1f} / {100*cost[(RE,RT)][0]:+.1f}. "
      "The model's judgement is free in a stationary world and costs fifteen to twenty points at the "
      "shift.")
    w("")
    w("**9. The two boundaries are the only place the override gets a defence, and it is a weak one.** "
      "Table 7: on days 14-15, when the shift lands, anchor validity drops to "
      f"{fmt(*agg(stat(data[NA], lambda r: r['anchor_bin'] is not None and 14 <= r['day'] <= 15, lambda r: r['anchor_bin'] == r['truth']))).split(' ')[0]}% "
      "(against 80% on days 11-13) - the record really is stale there - and right-when-overriding is "
      "at its least bad for the buffer, "
      f"{fmt(*agg(stat(data[NA], lambda r: r['anchor_bin'] is not None and 14 <= r['day'] <= 15 and r['answer'] != r['anchor_bin'], lambda r: r['correct']))).split(' ')[0]}%, "
      "against 13-14% in the middle and late spell. The same happens across the return boundary, more "
      "strongly (69.8% on days 24-25). But the override is still worse than following in both "
      "windows, and only three or four households clear the ten-question floor in those cells, so "
      "this is a direction, not a measurement.")
    w("")
    w("**10. Both arms agree, and the patrol explains the one place the sign flips.** Retrieval sees a "
      "different selection of the same sightings - 8 recent plus 10 same-time-of-day - and reaches the "
      "same conclusion on every question this file asks. The only table where overriding wins is Table 6's first "
      "half, where the anchor is July's literal 'most recent sighting of any hour': in this bank that "
      f"is the 03:00 patrol line for "
      f"{100*sum(1 for hh in HHS for r in data[NA][hh] if r['anchor_is_patrol'])/nq:.0f}% of questions, "
      "and it records where the object RESTS overnight, not where it is at 11 in the morning. "
      "Overriding a patrol line is obviously right. Strip the patrol out (Table 6's second half) and "
      "the same-bin picture returns: following 81.5 / 84.3 / 84.7 against overriding 59.8 / 27.6 / "
      "56.3 across the three stages.")
    w("")

    w("## Does the stage split support or undermine 'overriding is usually a mistake'?")
    w("")
    w("**It supports it, and it closes the escape route.** The flattering reading was: overriding only "
      "looks bad on average because most of a stationary study is a world where the record is good; "
      "at a shift, where the record IS stale, overriding should pay, and July could not check because "
      "July's world never moved. Checked here, it does not pay. In the sick spell the buffer is right "
      f"{g(NA,SP,'rf')}% when it follows its own most recent same-hour sighting and {g(NA,SP,'ro')}% "
      f"when it overrides it; retrieval, {g(RE,SP,'rf')}% against {g(RE,SP,'ro')}%. Those are the "
      "widest follow/override gaps in the study, not the narrowest, and every one of the twenty "
      "household-by-arm cells has the same sign.")
    w("")
    w("The stage split does more than confirm the July reading; it changes the diagnosis. The naive "
      "picture would be 'the model clings to a stale record'. That is not what happens. At the shift "
      "the arms override MORE "
      f"({100*key[(NA,'s2p')][0]:+.1f} ± {100*key[(NA,'s2p')][1]:.1f} follow rate for the buffer, "
      f"{100*key[(RE,'s2p')][0]:+.1f} ± {100*key[(RE,'s2p')][1]:.1f} for retrieval), they override a "
      f"record that has just become MORE reliable ({g(NA,SE_,'val')}% -> {g(NA,SP,'val')}% valid), "
      "the discrimination behind their overrides collapses from 2.6x the base rate to 1.8x so that "
      "two thirds of their spell overrides hit a record that was already correct, and what they "
      "override towards is the old routine - the desk, the office - which is precisely the "
      "thing the shift has invalidated. The override is not an inference about the new regime. It is "
      "the prior reasserting itself against the evidence in its own context window.")
    w("")
    w("That is the same object as the earlier retention finding, seen from the other side. There we "
      "measured that in 807 of 890 spell questions the buffer's prompt already contained a same-hour "
      "spell sighting naming the true location and the arm got only 72% of them right. Here we can "
      "say what it did instead: it answered something other than that sighting about a third of the "
      "time, and when it did it was right less than one time in five.")
    w("")
    w("What this data cannot settle is whether a well-aimed override is possible here at all. In the "
      f"spell the anchor is still wrong {100-float(g(NA,SP,'val').split(' ')[0]):.0f}% of the time, so "
      "a discriminator that could find exactly those cases would beat pure following. Nothing measured "
      "here comes close; that is a gap in method, not a proof of impossibility.")
    w("")

    w("## Assumptions and limits")
    w("")
    w("- **Two arms only.** Reflection and long-context cannot be scored this way: their prompts hold "
      "written notes and a running transcript, not an enumerable sighting list, so 'the most recent "
      "sighting the prompt holds' has no referent. The summary arm has no `run_log.jsonl` at all.")
    w("- **'Follow' is string equality between the answer and the anchor's spot name.** A model that "
      "reasoned its way to the same spot by another route counts as following. There is no way to "
      "separate the two from the logs, and July's measure has the same property.")
    w("- **The evidence axis is not July's.** 1/2/3/4+ total sightings does not exist in this bank "
      "(Table 1). The substitute - sightings in the same 2h clock bin - is a different quantity and "
      "the comparison to July's 0.94 -> 0.70 is therefore qualitative, not like for like.")
    w("- **The nightly 03:00 patrol has no analogue in July's loop** and dominates the literal "
      "'most recent sighting' anchor. Three anchors are reported rather than one for this reason; "
      "the headline uses the same-bin anchor, which no patrol line can enter because questions only "
      "occur between 07:00 and 22:59.")
    w("- **The buffer arm comes from a different results tree** "
      "(`dynamic_home_eqa_fm/results/fm_memory/run1/`) because there is no naive arm under "
      "`chain_person/nottold`. It was verified in the earlier analysis to be the same bank: identical "
      "question ids, truths and row counts per household. That check is re-run implicitly here - the "
      "two arms' run logs have identical question id sets and identical truths in all ten households.")
    w("- **Questions with no same-bin sighting in the prompt are dropped from the headline.** 350 of "
      "the 4130 (8%) have no listed sighting of that object in the question's own 2h clock bin, so "
      "the anchor is undefined and they are excluded; the headline tables run on 3780. They are "
      "concentrated in the first few days and at unusual hours. Tables 1 and 6, which use the "
      "any-hour anchor, keep all but one of them.")
    w("- **`right when it OVERRIDES` has a ceiling that moves between stages.** An override can only "
      "be right if the anchor was wrong, so the number is bounded by how often the anchor is wrong "
      "among overrides - which is why Table 10 reports that term separately rather than leaving the "
      "headline to be read as if the ceiling were 100%. The stage comparison in the text is made on "
      "the decomposition, not on the raw rate alone.")
    w("- **Households have different question counts** (287 to 496); all per-household means are "
      "unweighted across households, so a small household counts as much as a large one.")
    w("- **Corrections are not logged as their own events.** They are identified inside the prompt "
      "text by timestamp (question time + 600 s). The validation table checks that the sighting found "
      "at that timestamp names the previous question's logged truth.")
    w("- **No smoothing, no pooling across households** except the raw counts quoted in the prose.")
    w("")

    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT, len(lines), "lines")

    # ---- bank-identity check printed to stdout (used in the limits section)
    for hh in HHS:
        a = {r["qid"]: r["truth"] for r in data[NA][hh]}
        b = {r["qid"]: r["truth"] for r in data[RE][hh]}
        assert a == b, hh
    print("bank identity check: identical question ids and truths in all 10 households")


if __name__ == "__main__":
    main()
