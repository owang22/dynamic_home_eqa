#!/usr/bin/env python3
"""Does this scenario deserve a night of GPU time? Decide before spending it.

Run it on a regime directory (a config plus its generated household banks) and it
prints a table and a verdict. Nothing here is specific to the illness scenario; the
checks are the faults we found by hand on 2026-09-23/24, turned into thresholds.

    python3 results/self_improve/check_scenario.py results/regime_search/sick10_partial
    python3 results/self_improve/check_scenario.py --banks 'path/to/banks/hh_s*_t03.jsonl'

Options
    --settled NAME   the name of the ordinary window in the bank's stage map (default: guessed)
    --disrupted NAME the name of the disrupted window (default: guessed)
    --after NAME     the name of the back-to-normal window (default: guessed)
    --quiet          verdict and failures only
    --json PATH      also write every number as JSON

WHAT EACH CHECK IS FOR, and why the threshold is where it is.

HEADROOM. Two baselines that need no real memory: answer the single commonest place
in the window to every question ("one fact"), and answer each object's own commonest
place in the window ("per object"). The gap between them is the whole space a memory
can win in. On the scenario we nearly ran it was 5 points in the disrupted window,
and 0 points in the band holding 62% of the questions, so no memory design could
have distinguished itself from any other. Threshold: 15 points in the disrupted
window, and no band holding over a third of the questions may sit under 8.

HETEROGENEITY. A disruption where every moved object lands in the same place is one
fact, and one fact is represented equally well by a wholesale summary and by a store
of separate claims, so it cannot compare the two. We also need objects that do NOT
move, or nothing is being preserved. Threshold: at most 70% of movers to a single
receptacle per household, at least two destinations, at least three controls.

INDEPENDENCE. Ten households that all move the same objects to the same place are
one instance with ten cosmetic variations, and paired statistics across them
overstate what was shown. Threshold: under 60% of all movers, pooled across
households, landing on the single commonest destination.

VISIBILITY. A change that is only visible at hours when nothing is asked, or whose
most visible hours are the hours with no headroom, cannot be learned or cannot be
scored. Reported hour by hour, with the question load beside it.

REVERSION. If the world does not put things back, "did the memory revert" is
measuring the world. Reported as a contamination percentage, not failed on.

POWER. Questions per window is the flattering number; objects per window is the real
one, because twenty questions about one object are not twenty observations.

THE CLASSICAL CURVE (check 7, owned by check_classical_curve.py, which also runs on its
own). Two counting methods with no language model anywhere - a timetable that never
forgets and a timetable with a three-day memory - are replayed over the banks, and their
accuracy must climb through the settled window, fall at the upset, climb back during it,
and fall again at the return. If a counting method cannot be broken by the disruption
then there is nothing in the data for a language model to notice, and that is a failing
scenario, not a failing method. Thresholds and their justifications live in that file.

HOUSEHOLD EXCLUSION. A household where fewer than two asked-about objects change
their commonest place is a household where the event did not happen. Dropped by
rule, named in the output, and every other number computed without it.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import glob
import json
import pathlib
import statistics
import sys

# ---------------------------------------------------------------- thresholds

MIN_HEADROOM_DISRUPTED = 0.15
MIN_HEADROOM_BAND = 0.08
BAND_MATTERS_ABOVE = 1 / 3          # a band holding more than this share of questions counts
MAX_TOP_DESTINATION_SHARE_HH = 0.70  # per household
MAX_TOP_DESTINATION_SHARE_ALL = 0.60  # pooled over households
MIN_DESTINATIONS_HH = 2
MIN_CONTROLS_HH = 3
MIN_MOVERS_TO_KEEP_HH = 2            # the exclusion rule
MIN_AFFECTED_PER_WINDOW = 30         # per household, in the disrupted window
MIN_OBJECTS_PER_WINDOW = 8           # per household: the effective sample size

BANDS = [("morning 07-09", range(7, 10)),
         ("daytime 10-17", range(10, 18)),
         ("evening 18-23", range(18, 24)),
         ("night 00-06", list(range(0, 7)))]

BEYOND_REACH = ("OUT_OF_HOUSE", "ON_PERSON")


# ---------------------------------------------------------------- reading a bank

class Bank:
    """One household's frozen timeline, with the few lookups the checks need."""

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.header = None
        self.truth = collections.defaultdict(list)
        self.questions = []
        self.visits = []
        for line in path.open():
            row = json.loads(line)
            kind = row.get("kind")
            if kind == "episode_header":
                self.header = row
            elif kind == "truth":
                self.truth[row["object_id"]].append((row["t"], row["receptacle_id"]))
            elif kind == "question":
                self.questions.append(row)
            elif kind == "room_visit":
                self.visits.append(row)
        if self.header is None:
            raise SystemExit(f"{path}: no episode_header row")
        for obj in self.truth:
            self.truth[obj].sort()
        self._times = {o: [t for t, _ in v] for o, v in self.truth.items()}
        self.rooms_of = self.header.get("receptacle_rooms", {})
        self.stages = {int(k): v for k, v in (self.header.get("stages") or {}).items()}
        self.name = self.header.get("household_id", path.stem)
        self.n_days = self.header.get("n_days", 1 + max(self.stages or [0]))

    def place_at(self, obj: str, t: int):
        """Where the object truly is at time t, or None before its first record."""
        arr = self.truth.get(obj)
        if not arr:
            return None
        i = bisect.bisect_right(self._times[obj], t) - 1
        return arr[i][1] if i >= 0 else None

    def room_at(self, obj: str, t: int):
        place = self.place_at(obj, t)
        return self.rooms_of.get(place, place)

    def rooms(self):
        return sorted(set(self.rooms_of.values()) - {"person_check"})

    def places(self):
        return [r for r in self.header.get("receptacle_ids", []) if r in self.rooms_of]

    def days_of(self, stage: str):
        return sorted(d for d, s in self.stages.items() if s == stage and d >= 1)

    def asked(self):
        return sorted({q["object_id"] for q in self.questions})

    def answers(self, stage=None, days=None, band=None):
        """(object, true place) for every question in the given slice."""
        out = []
        for q in self.questions:
            if stage is not None and q.get("stage") != stage:
                continue
            if days is not None and q.get("day_index") not in days:
                continue
            if band is not None and (q["t_query"] % 86400) // 3600 not in band:
                continue
            out.append((q["object_id"], self.place_at(q["object_id"], q["t_query"])))
        return out


# ---------------------------------------------------------------- the measurements

def baselines(pairs):
    """one-fact accuracy, per-object accuracy, and the headroom between them."""
    if not pairs:
        return None
    counts = collections.Counter(place for _, place in pairs)
    one_fact = counts.most_common(1)[0][1] / len(pairs)
    per_object = collections.defaultdict(collections.Counter)
    for obj, place in pairs:
        per_object[obj][place] += 1
    best = sum(c.most_common(1)[0][1] for c in per_object.values()) / len(pairs)
    return one_fact, best, best - one_fact


def modal_place(bank: Bank, obj: str, stage: str):
    counts = collections.Counter(p for o, p in bank.answers(stage=stage) if o == obj)
    return counts.most_common(1)[0][0] if counts else None


def movement(bank: Bank, settled: str, disrupted: str, after: str):
    """Per asked object: its usual place in each window, and whether it moved."""
    rows = []
    for obj in bank.asked():
        a = modal_place(bank, obj, settled)
        b = modal_place(bank, obj, disrupted)
        c = modal_place(bank, obj, after)
        rows.append({"object": obj, "settled": a, "disrupted": b, "after": c,
                     "moved": a is not None and b is not None and a != b,
                     "comparable": a is not None and b is not None})
    return rows


def guess_stages(bank: Bank):
    """Name the three windows without being told, from the stage map's own order."""
    seen = []
    for d in sorted(bank.stages):
        s = bank.stages[d]
        if s not in seen:
            seen.append(s)
    if len(seen) >= 3:
        return seen[0], seen[1], seen[2]
    if len(seen) == 2:
        return seen[0], seen[1], seen[1]
    raise SystemExit("cannot tell the windows apart from the stage map; pass --settled/--disrupted/--after")


def visibility_by_hour(bank: Bank, settled: str, disrupted: str, only=None):
    """For each hour, the share of objects whose usual room at that hour differs between
    the settled and the disrupted window. That is what a look at that hour reveals.

    ``only`` restricts it to the objects that actually move, which is the number that
    matters: a control object that never moves cannot make a look more or less useful,
    and including it just dilutes the figure by however many controls the scenario has."""
    lead_days, sick_days = bank.days_of(settled), bank.days_of(disrupted)
    pool = list(only) if only is not None else bank.asked()
    out = {}
    for hour in range(24):
        changed = 0
        for obj in pool:
            a = collections.Counter(bank.room_at(obj, d * 86400 + hour * 3600) for d in lead_days)
            b = collections.Counter(bank.room_at(obj, d * 86400 + hour * 3600) for d in sick_days)
            if a and b and a.most_common(1)[0][0] != b.most_common(1)[0][0]:
                changed += 1
        out[hour] = changed / len(pool) if pool else 0.0
    return out


def affected(bank: Bank, stage: str, settled: str, days=None):
    """Questions whose true answer is NOT where a settled memory would look."""
    base = {o: modal_place(bank, o, settled) for o in bank.asked()}
    n = hit = 0
    for q in bank.questions:
        if stage is not None and q.get("stage") != stage:
            continue
        if days is not None and q.get("day_index") not in days:
            continue
        if base.get(q["object_id"]) is None:
            continue
        n += 1
        if base[q["object_id"]] != bank.place_at(q["object_id"], q["t_query"]):
            hit += 1
    return n, hit


# ---------------------------------------------------------------- the report

def pct(x):
    return "  --" if x is None else f"{100 * x:4.0f}"


def bar(x, width=24):
    return "#" * int(round(x * width)) + "." * (width - int(round(x * width)))


def check(banks, settled, disrupted, after, quiet=False):
    """Everything, in one pass, returning (lines, failures, numbers)."""
    lines, fails, warns = [], [], []
    numbers = {"settled": settled, "disrupted": disrupted, "after": after}

    # -- household exclusion first, so nothing downstream is computed on a dead household
    moves = {b.name: movement(b, settled, disrupted, after) for b in banks}
    dropped = [b.name for b in banks if sum(r["moved"] for r in moves[b.name]) < MIN_MOVERS_TO_KEEP_HH]
    kept = [b for b in banks if b.name not in dropped]
    numbers["dropped_households"] = dropped
    numbers["kept_households"] = [b.name for b in kept]

    lines.append("HOUSEHOLDS")
    lines.append(f"  found {len(banks)}: {', '.join(b.name for b in banks)}")
    if dropped:
        lines.append(f"  DROPPED by the exclusion rule (under {MIN_MOVERS_TO_KEEP_HH} asked objects change "
                     f"their usual place): {', '.join(dropped)}")
    else:
        lines.append("  dropped by the exclusion rule: none")
    lines.append(f"  kept {len(kept)}")
    if len(kept) < 5:
        fails.append(f"only {len(kept)} households survive the exclusion rule; need at least 5")
    lines.append("")
    if not kept:
        return lines, fails, warns, numbers

    r0 = kept[0]
    lines.append(f"  windows: settled='{settled}' days {r0.days_of(settled)[:1]}..{r0.days_of(settled)[-1:]}  "
                 f"disrupted='{disrupted}' days {r0.days_of(disrupted)[:1]}..{r0.days_of(disrupted)[-1:]}  "
                 f"back-to-normal='{after}' days {r0.days_of(after)[:1]}..{r0.days_of(after)[-1:]}")
    lines.append(f"  rooms per household: {[len(b.rooms()) for b in kept]}")
    lines.append(f"  places per household: {[len(b.places()) for b in kept]}")
    lines.append("")

    # ------------------------------------------------ 1. headroom, per window
    lines.append("CHECK 1  HEADROOM - is there anything for a memory to get right?")
    lines.append("  one fact = answer the commonest place to everything. per object = know each object perfectly.")
    lines.append("  the gap between them is all the room a memory design has to win in.")
    lines.append("")
    lines.append("  window          one fact  per object  headroom   per-household headroom")
    hr = {}
    for w in [settled, disrupted, after]:
        vals = [baselines(b.answers(stage=w)) for b in kept]
        vals = [v for v in vals if v]
        if not vals:
            continue
        gaps = [v[2] for v in vals]
        hr[w] = statistics.mean(gaps)
        lines.append(f"  {w:14s} {pct(statistics.mean(v[0] for v in vals))}%    {pct(statistics.mean(v[1] for v in vals))}%"
                     f"     {pct(statistics.mean(gaps))}pts   min {pct(min(gaps))} max {pct(max(gaps))}")
    numbers["headroom_by_window"] = hr
    if hr.get(disrupted, 0) < MIN_HEADROOM_DISRUPTED:
        fails.append(f"disrupted-window headroom is {100 * hr.get(disrupted, 0):.0f} points, "
                     f"under the {100 * MIN_HEADROOM_DISRUPTED:.0f} needed - a one-sentence memory scores "
                     f"almost as well as a perfect one, so no arm can separate")
    lines.append("")

    # ------------------------------------------------ 1b. headroom by time-of-day band
    lines.append("  the same, split by the hour the question was asked (the disrupted window):")
    lines.append("  band            share of Qs  one fact  per object  headroom")
    band_rows = {}
    total = sum(len(b.answers(stage=disrupted)) for b in kept)
    for name, hours in BANDS:
        vals, n = [], 0
        for b in kept:
            pairs = b.answers(stage=disrupted, band=hours)
            n += len(pairs)
            v = baselines(pairs)
            if v:
                vals.append(v)
        if not vals or not n:
            continue
        share = n / total if total else 0
        gap = statistics.mean(v[2] for v in vals)
        band_rows[name] = {"share": share, "headroom": gap,
                           "one_fact": statistics.mean(v[0] for v in vals),
                           "per_object": statistics.mean(v[1] for v in vals)}
        flag = ""
        if share > BAND_MATTERS_ABOVE and gap < MIN_HEADROOM_BAND:
            flag = "   <-- FAIL: a third of the questions sit here and there is nothing to win"
            fails.append(f"the '{name}' band holds {100 * share:.0f}% of the disrupted-window questions "
                         f"but has only {100 * gap:.0f} points of headroom")
        lines.append(f"  {name:14s} {pct(share)}%      {pct(vals and statistics.mean(v[0] for v in vals))}%"
                     f"    {pct(statistics.mean(v[1] for v in vals))}%     {pct(gap)}pts{flag}")
    numbers["headroom_by_band"] = band_rows
    lines.append("")

    # ------------------------------------------------ 2. heterogeneity
    lines.append("CHECK 2  HETEROGENEITY - do different things move to different places, and does anything stay?")
    lines.append("  household   asked  moved  stays put  destinations  biggest destination takes")
    het = {}
    for b in kept:
        rows = moves[b.name]
        movers = [r for r in rows if r["moved"]]
        controls = [r for r in rows if r["comparable"] and not r["moved"]]
        dest = collections.Counter(r["disrupted"] for r in movers)
        top = dest.most_common(1)[0][1] / len(movers) if movers else 0
        het[b.name] = {"asked": len(rows), "moved": len(movers), "controls": len(controls),
                       "destinations": len(dest), "top_share": top,
                       "dest": dest.most_common()}
        flags = []
        if top > MAX_TOP_DESTINATION_SHARE_HH:
            flags.append("one place takes nearly everything")
        if len(dest) < MIN_DESTINATIONS_HH:
            flags.append("only one destination")
        if len(controls) < MIN_CONTROLS_HH:
            flags.append("too few objects that stay put")
        lines.append(f"  {b.name:11s} {len(rows):5d}  {len(movers):5d}  {len(controls):9d}  {len(dest):12d}"
                     f"  {pct(top)}%   {'; '.join(flags)}")
    numbers["heterogeneity"] = het
    bad_top = [n for n, v in het.items() if v["top_share"] > MAX_TOP_DESTINATION_SHARE_HH]
    if len(bad_top) > len(kept) / 2:
        fails.append(f"in {len(bad_top)} of {len(kept)} households over "
                     f"{100 * MAX_TOP_DESTINATION_SHARE_HH:.0f}% of the moved objects land on one receptacle - "
                     f"the disruption is one fact, which a summary represents as well as separate claims")
    thin = [n for n, v in het.items() if v["controls"] < MIN_CONTROLS_HH]
    if len(thin) > len(kept) / 2:
        fails.append(f"{len(thin)} of {len(kept)} households have under {MIN_CONTROLS_HH} objects that stay put - "
                     f"nothing is being preserved, so keeping-versus-revising cannot be measured")
    lines.append("")

    # ------------------------------------------------ 3. independence
    lines.append("CHECK 3  INDEPENDENCE - are these separate instances, or one fact repeated?")
    pooled = collections.Counter()
    for b in kept:
        for r in moves[b.name]:
            if r["moved"]:
                pooled[r["disrupted"]] += 1
    tot = sum(pooled.values())
    share = pooled.most_common(1)[0][1] / tot if tot else 0
    numbers["pooled_destinations"] = pooled.most_common()
    numbers["pooled_top_share"] = share
    lines.append(f"  {tot} moved objects across {len(kept)} households, landing on {len(pooled)} distinct receptacles")
    for place, n in pooled.most_common(8):
        lines.append(f"    {place:24s} {n:3d}  {bar(n / tot)}")
    lines.append(f"  the single commonest destination takes {100 * share:.0f}% of all movers")
    if share > MAX_TOP_DESTINATION_SHARE_ALL:
        fails.append(f"{100 * share:.0f}% of every moved object in every household lands on the same receptacle - "
                     f"the households are one scenario measured {len(kept)} times, and paired statistics "
                     f"across them will overstate the result")
    lines.append("")

    # ------------------------------------------------ 4. visibility
    lines.append("CHECK 4  VISIBILITY - can a look see the change, at the hours questions are asked?")
    lines.append("  Among the objects that DO move (controls cannot make a look more useful):")
    lines.append("  hour   change visible   questions asked")
    vis = collections.defaultdict(list)
    vis_all = collections.defaultdict(list)
    for b in kept:
        movers = [r["object"] for r in moves[b.name] if r["moved"]]
        for h, v in visibility_by_hour(b, settled, disrupted, only=movers).items():
            vis[h].append(v)
        for h, v in visibility_by_hour(b, settled, disrupted).items():
            vis_all[h].append(v)
    qhour = collections.Counter()
    for b in kept:
        for q in b.questions:
            if q.get("stage") == disrupted:
                qhour[(q["t_query"] % 86400) // 3600] += 1
    qtot = sum(qhour.values()) or 1
    vmean = {h: statistics.mean(v) for h, v in vis.items()}
    for h in range(24):
        lines.append(f"  {h:02d}:00  {pct(vmean[h])}%  {bar(vmean[h], 20)}   {pct(qhour[h] / qtot)}%")
    numbers["visibility_by_hour_movers"] = vmean
    numbers["visibility_by_hour_all_asked"] = {h: statistics.mean(v) for h, v in vis_all.items()}
    numbers["question_share_by_hour"] = {h: qhour[h] / qtot for h in range(24)}
    best_h = max(vmean, key=lambda h: vmean[h])
    lines.append(f"  most visible hour: {best_h:02d}:00 at {100 * vmean[best_h]:.0f}%; "
                 f"quietest: {min(vmean, key=lambda h: vmean[h]):02d}:00 at {100 * min(vmean.values()):.0f}%")
    settled_floor = statistics.mean(vmean[h] for h in range(0, 7))
    lines.append(f"  overnight floor (00-06), which any change-detector must clear: {100 * settled_floor:.0f}%")
    numbers["overnight_floor"] = settled_floor
    lines.append(f"  (over ALL asked objects, including the controls, the peak is "
                 f"{100 * max(statistics.mean(v) for v in vis_all.values()):.0f}% - lower simply because "
                 f"controls never change)")
    if vmean[best_h] < 0.5:
        fails.append(f"even at its most visible hour the change shows on only "
                     f"{100 * vmean[best_h]:.0f}% of the objects that moved - a robot cannot learn "
                     f"what it cannot see")
    # the tension: are the visible hours the ones with headroom?
    for name, hours in BANDS:
        row = band_rows.get(name)
        if not row:
            continue
        v = statistics.mean(vmean[h] for h in hours)
        # a band that holds almost no questions cannot sink the study, however little
        # headroom it has, so the tension only counts where questions actually land
        if row["share"] > 0.15 and v > 0.5 and row["headroom"] < MIN_HEADROOM_BAND:
            fails.append(f"the '{name}' band is where the change is most visible ({100 * v:.0f}%) but it has "
                         f"only {100 * row['headroom']:.0f} points of headroom - visible and informative "
                         f"do not overlap")
        elif row["share"] > 0.15 and v > 0.5 and row["headroom"] < 0.15:
            warns.append(f"the '{name}' band is visible ({100 * v:.0f}%) but thin on headroom "
                         f"({100 * row['headroom']:.0f} points)")
    lines.append("")

    # ------------------------------------------------ 5. reversion
    lines.append("CHECK 5  REVERSION - does the world put things back, or is the return measuring drift?")
    back = stay = third = 0
    drift = ctrl = 0
    for b in kept:
        for r in moves[b.name]:
            if r["after"] is None:
                continue
            if r["moved"]:
                if r["after"] == r["settled"]:
                    back += 1
                elif r["after"] == r["disrupted"]:
                    stay += 1
                else:
                    third += 1
            elif r["comparable"]:
                ctrl += 1
                if r["after"] != r["settled"]:
                    drift += 1
    tot2 = back + stay + third
    contam = (stay + third) / tot2 if tot2 else 0
    lines.append(f"  of {tot2} moved objects with questions after the disruption: "
                 f"{back} go back, {stay} stay where the disruption put them, {third} end up somewhere third")
    lines.append(f"  of {ctrl} objects that never moved, {drift} have a different usual place afterwards anyway "
                 f"(ordinary drift, nothing to do with the event)")
    lines.append(f"  contamination of the reversion test: {100 * contam:.0f}% of movers plus "
                 f"{100 * drift / ctrl if ctrl else 0:.0f}% of controls")
    numbers["reversion"] = {"back": back, "stayed": stay, "third": third,
                            "controls": ctrl, "controls_drifting": drift, "contamination": contam}
    if contam > 0.4:
        warns.append(f"{100 * contam:.0f}% of moved objects do not return to where they were - "
                     f"the reversion measurement is mostly measuring the world, not the memory")
    lines.append("")

    # ------------------------------------------------ 6. power
    lines.append("CHECK 6  POWER - questions is the flattering number, objects is the real one")
    lines.append("  window          questions/hh  of those, a settled memory gets wrong   objects/hh  object-place facts/hh")
    pw = {}
    for w in [settled, disrupted, after]:
        ns, hits, objs, facts = [], [], [], []
        for b in kept:
            n, hit = affected(b, w, settled)
            pairs = b.answers(stage=w)
            ns.append(n); hits.append(hit)
            objs.append(len({o for o, _ in pairs}))
            facts.append(len(set(pairs)))
        pw[w] = {"questions": statistics.mean(ns), "affected": statistics.mean(hits),
                 "affected_min": min(hits), "objects": statistics.mean(objs), "facts": statistics.mean(facts)}
        lines.append(f"  {w:14s} {statistics.mean(ns):11.0f}   {statistics.mean(hits):9.0f}"
                     f" (worst household {min(hits)})        {statistics.mean(objs):6.1f}      {statistics.mean(facts):6.1f}")
    numbers["power"] = pw
    d = pw.get(disrupted, {})
    if d.get("affected", 0) < MIN_AFFECTED_PER_WINDOW:
        fails.append(f"only {d['affected']:.0f} questions per household in the disrupted window have an answer a "
                     f"settled memory would miss (worst household {d['affected_min']}); "
                     f"need about {MIN_AFFECTED_PER_WINDOW}")
    if d.get("objects", 0) < MIN_OBJECTS_PER_WINDOW:
        fails.append(f"only {d['objects']:.1f} distinct objects are asked about per household in the disrupted "
                     f"window; the effective sample size is objects, not questions, so this is the real n "
                     f"and it needs to be at least {MIN_OBJECTS_PER_WINDOW}")
    lines.append(f"  effective sample size for the disrupted window: about "
                 f"{sum(1 for b in kept for r in moves[b.name] if r['moved'])} moved objects "
                 f"across {len(kept)} households, NOT "
                 f"{sum(len(b.answers(stage=disrupted)) for b in kept)} questions. "
                 f"Cluster every interval on household and object.")
    lines.append("")

    # ------------------------------------------------ 7. the classical curve
    # Owned by check_classical_curve.py: two counting methods with no language model
    # anywhere, followed through the four phases of the calendar. Imported here rather
    # than at the top so this file still runs if that one is being edited.
    from check_classical_curve import check_curve
    cc_lines, cc_fails, cc_warns, cc_numbers = check_curve(banks, settled, disrupted, after, quiet)
    lines.extend(cc_lines)
    fails.extend(cc_fails)
    warns.extend(cc_warns)
    numbers["classical_curve"] = cc_numbers
    return lines, fails, warns, numbers


def main(argv=None):
    ap = argparse.ArgumentParser(description="Decide whether a scenario is worth running.")
    ap.add_argument("regime", nargs="?", help="a regime directory containing banks/ (and usually config.yaml)")
    ap.add_argument("--banks", help="glob for bank files, instead of a regime directory")
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
        ap.error("give a regime directory or --banks")
    if not paths:
        raise SystemExit(f"no bank files found for {title}")

    banks = [Bank(p) for p in paths]
    settled = a.settled or guess_stages(banks[0])[0]
    disrupted = a.disrupted or guess_stages(banks[0])[1]
    after = a.after or guess_stages(banks[0])[2]

    print("=" * 100)
    print(f"SCENARIO CHECK: {title}")
    print("=" * 100)
    print()
    lines, fails, warns, numbers = check(banks, settled, disrupted, after, a.quiet)
    if not a.quiet:
        print("\n".join(lines))

    print("-" * 100)
    if fails:
        print(f"VERDICT: DO NOT RUN. {len(fails)} check(s) failed.")
        for i, f in enumerate(fails, 1):
            print(f"  {i}. {f}")
    else:
        print("VERDICT: WORTH RUNNING. Every check passed.")
    if warns:
        print(f"\nWarnings ({len(warns)}) - not disqualifying, but say them in the paper:")
        for i, w in enumerate(warns, 1):
            print(f"  {i}. {w}")
    print("-" * 100)

    numbers["failures"] = fails
    numbers["warnings"] = warns
    numbers["verdict"] = "do not run" if fails else "worth running"
    if a.json:
        a.json.write_text(json.dumps(numbers, indent=2, default=str))
        print(f"numbers written to {a.json}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
