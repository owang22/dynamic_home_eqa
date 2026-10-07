#!/usr/bin/env python3
"""Headroom between the best simple rule and what the robot's own record could reach, for the
four study setups. CPU only, no model.

    cd /home/oliver/robot/dynamic_home_eqa
    /home/oliver/miniconda3/bin/python coordination/headroom/headroom.py

Writes, beside this script: study{1,2,3,4}.png, study{1,2,3,4}.json, HEADROOM.md.

The record-reachable ceilings, per "where is X" question (room level, as first guess right is):
  loose    = 1 if the true room at question time is a room in which the robot had itself sighted X
             at an earlier time (strictly before the question's time), else 0.
  routine  = 1 if the true room is the room of X's most recent earlier sighting, OR X was sighted in
             the true room on an earlier day within one hour of the same time of day; else 0.
Both are computed from the LAST-SEEN cell's looks.jsonl, so they do not depend on a model's choices.
A question's own search looks happen at the question's time and are not "earlier".
First guess right = found_at_step == 1 on a kind == "search" row, as the existing scorers do.
"""
from __future__ import annotations

import bisect
import collections
import importlib.util
import json
import pathlib
import re
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
RES = REPO / "results/self_improve"
DAY = 86400

# one colour per method, the same on every chart
C = {
    "last_seen": "#7f7f7f",          # grey
    "most_frequent": "#1f4e9c",      # dark blue
    "same_time_of_day": "#3f8fd2",   # mid blue
    "alternate_room": "#9dc6ea",     # light blue
    "best_rule": "#1f4e9c",          # a rule: dark blue
    "notes": "#e07b1a",              # record plus notes: orange
    "ceiling": "#000000",            # loose ceiling: dashed black
    "routine": "#1b7f5a",            # routine ceiling: dashed dark green
    "knowledge": "#d9d9d9",          # the room only knowledge could take
}
DASH_LOOSE = (0, (7, 3))
DASH_ROUTINE = (0, (3, 2))
LOOSE_LABEL = "loose ceiling, from the last-seen robot's own record"
ROUTINE_LABEL = "routine ceiling, from the last-seen robot's own record"
FIGSIZE = (16, 9)
DPI = 100


def pct(k, n):
    return 100.0 * k / n if n else float("nan")


# ----------------------------------------------------------------------------- loading

def read_searches(cell):
    rows = []
    with (cell / "searches.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("kind") == "search":
                rows.append(r)
    return rows


def read_looks(cell):
    looks = []
    with (cell / "looks.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("kind") == "look":
                looks.append(r)
    return looks


def sightings_by_object(looks):
    """object_id -> sorted list of (time, day, room, place_id)."""
    out = collections.defaultdict(list)
    for lk in looks:
        for s in lk["sightings"]:
            out[s["object_id"]].append((s["time"], s["day"], s["room"], s["place_id"]))
    for v in out.values():
        v.sort()
    return out


def resident_sightings(looks):
    """name -> sorted list of (time, day, room)."""
    out = collections.defaultdict(list)
    for lk in looks:
        if not lk.get("residents_seen"):
            continue
        rooms = [t["name"] for t in lk.get("targets", []) if t.get("kind") == "room"]
        room = rooms[0] if len(rooms) == 1 else None
        for name in lk["residents_seen"]:
            out[name].append((lk["time"], lk["day"], room))
    for v in out.values():
        v.sort()
    return out


# ----------------------------------------------------------------------------- the ceilings

def tod_close(t1, t2, tol=3600):
    a, b = t1 % DAY, t2 % DAY
    d = abs(a - b)
    return min(d, DAY - d) <= tol


def ceilings(q, sb):
    """(loose, routine) for one search row q given sightings_by_object sb."""
    hist = sb.get(q["object_id"], [])
    k = bisect.bisect_left(hist, (q["time"], -1, "", ""))
    earlier = hist[:k]
    if not earlier:
        return 0, 0
    true_room = q["true_room"]
    loose = int(any(s[2] == true_room for s in earlier))
    if not loose:
        return 0, 0
    routine = int(earlier[-1][2] == true_room or any(
        s[2] == true_room and s[1] < q["day"] and tod_close(s[0], q["time"]) for s in earlier))
    return loose, routine


def score_rows(rows, sb=None):
    """right, loose, routine, n for a list of search rows (ceilings only if sb given)."""
    right = sum(1 for r in rows if r.get("found_at_step") == 1)
    if sb is None:
        return {"right": right, "n": len(rows)}
    lo = ro = 0
    for r in rows:
        a, b = ceilings(r, sb)
        lo += a
        ro += b
    return {"right": right, "loose": lo, "routine": ro, "n": len(rows)}


def legend_below(fig, ax, handles, labels, ncol, bottom=0.18):
    fig.subplots_adjust(bottom=bottom)
    fig.legend(handles, labels, loc="lower center", ncol=ncol, frameon=False, fontsize=12,
               bbox_to_anchor=(0.5, 0.01))


# ============================================================================= study 1

def study1():
    cells = RES / "wave_the_second_illness/cells"
    homes = ["hh_s2_t03", "hh_s32_t03", "hh_s48_t03"]
    ill = [(14, 23), (32, 41)]
    windows = {"days 24-28": range(24, 29), "days 42-46": range(42, 47)}
    per_home = {}
    for h in homes:
        ls = read_searches(cells / "last_seen_no_model" / h)
        notes = read_searches(cells / "the_log_and_notes_about_the_routine" / h)
        assert [(r["day"], r["question_id"], r["object_id"], r["true_room"]) for r in ls] == \
               [(r["day"], r["question_id"], r["object_id"], r["true_room"]) for r in notes], h
        sb = sightings_by_object(read_looks(cells / "last_seen_no_model" / h))
        sb_notes = sightings_by_object(read_looks(cells / "the_log_and_notes_about_the_routine" / h))
        notes_right = {r["question_id"]: r.get("found_at_step") == 1 for r in notes}
        per_q = []
        for r in ls:
            lo, ro = ceilings(r, sb)
            lo_n, ro_n = ceilings(r, sb_notes)   # the same ceilings from the notes arm's own looks
            per_q.append({"day": r["day"], "question_id": r["question_id"], "object_id": r["object_id"],
                          "is_a_mover": bool(r.get("is_a_mover")), "last_seen": r.get("found_at_step") == 1,
                          "notes": notes_right[r["question_id"]], "loose": lo, "routine": ro,
                          "loose_from_notes_looks": lo_n, "routine_from_notes_looks": ro_n})
        per_home[h] = per_q

    days = list(range(1, 50))
    keys = ["last_seen", "notes", "loose", "routine", "loose_from_notes_looks", "routine_from_notes_looks"]
    by_day = {h: {k: [] for k in keys} for h in homes}
    for h in homes:
        for d in days:
            rows = [q for q in per_home[h] if q["day"] == d]
            for k in keys:
                by_day[h][k].append(pct(sum(int(q[k]) for q in rows), len(rows)))
    mean = {k: [statistics.fmean(by_day[h][k][i] for h in homes) for i in range(len(days))] for k in keys}

    def table(filter_fn):
        out = {}
        for h in homes:
            rows = [q for q in per_home[h] if filter_fn(q)]
            out[h] = {k: sum(int(q[k]) for q in rows) for k in keys} | {"n": len(rows)}
        pooled = {k: sum(out[h][k] for h in homes) for k in keys + ["n"]}
        out["pooled"] = pooled | {k + "_pct": pct(pooled[k], pooled["n"]) for k in keys}
        return out

    tables = {}
    for wname, w in windows.items():
        tables[wname] = table(lambda q, w=w: q["day"] in w)
        tables[wname + ", movers"] = table(lambda q, w=w: q["day"] in w and q["is_a_mover"])
    both = set(windows["days 24-28"]) | set(windows["days 42-46"])
    tables["days 24-28 and 42-46"] = table(lambda q: q["day"] in both)
    tables["days 24-28 and 42-46, movers"] = table(lambda q: q["day"] in both and q["is_a_mover"])
    tables["all days 1-49"] = table(lambda q: True)
    tables["all days, movers"] = table(lambda q: q["is_a_mover"])
    tables["ill days 14-23 and 32-41"] = table(lambda q: any(a <= q["day"] <= b for a, b in ill))
    tables["ill days, movers"] = table(lambda q: q["is_a_mover"] and any(a <= q["day"] <= b for a, b in ill))

    # ---- chart
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor("white")
    for a, b in ill:
        ax.axvspan(a - 0.5, b + 0.5, color="#ececec", zorder=0)
        ax.text((a + b) / 2, 2, "ill", ha="center", va="bottom", fontsize=13, color="#555555")
    for a, b in ((24, 28), (42, 46)):
        ax.axvspan(a - 0.5, b + 0.5, color="#fbf1e6", zorder=0)
        ax.text((a + b) / 2, 2, "return", ha="center", va="bottom", fontsize=13, color="#8a5a2a")
    ax.plot(days, mean["loose"], color=C["ceiling"], linestyle=DASH_LOOSE, lw=1.8, marker="^", ms=5, label=LOOSE_LABEL + " (true room ever sighted for this object)")
    ax.plot(days, mean["routine"], color=C["routine"], linestyle=DASH_ROUTINE, lw=1.8, marker="v", ms=5, label=ROUTINE_LABEL + " (most recent sighting, or same hour on an earlier day)")
    ax.plot(days, mean["loose_from_notes_looks"], color=C["notes"], linestyle=DASH_LOOSE, lw=1.1, label="loose ceiling, from the record-plus-notes robot's own record")
    ax.plot(days, mean["notes"], color=C["notes"], lw=2.2, marker="s", ms=5, label="record plus notes (the method)")
    ax.plot(days, mean["last_seen"], color=C["last_seen"], lw=2.2, marker="o", ms=5, label="last-seen rule")
    ax.set_xlim(0.5, 49.5)
    ax.set_ylim(0, 102)
    ax.set_xticks(range(1, 50, 2))
    ax.set_xlabel("Day of the run", fontsize=13)
    ax.set_ylabel("First guess right, percent of the day's questions", fontsize=13)
    ax.set_title("Study 1, memory through a shift and back: first guess right by day, mean of three households\n(24 questions a day; resident 1 ill on days 14-23 and 32-41; the scored return windows are days 24-28 and 42-46)", fontsize=13)
    ax.grid(axis="y", color="#e5e5e5")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    h_, l_ = ax.get_legend_handles_labels()
    legend_below(fig, ax, h_, l_, ncol=2, bottom=0.22)
    fig.savefig(HERE / "study1.png", facecolor="white")
    plt.close(fig)

    json.dump({"what": "Study 1: first guess right by day (percent) per household and mean over households; ceilings from the last-seen cell's looks",
               "households": homes, "days": days, "per_household_by_day": by_day, "mean_by_day": mean,
               "tables": tables, "ill_days": ill},
              (HERE / "study1.json").open("w"), indent=1)
    return tables, mean


# ============================================================================= study 2

def load_bank_header_and_truth(bank_path):
    header = None
    truth = collections.defaultdict(list)
    with open(bank_path) as fh:
        for line in fh:
            if '"kind": "truth"' not in line and '"kind": "episode_header"' not in line:
                continue
            r = json.loads(line)
            if r["kind"] == "episode_header":
                header = r
            elif r["kind"] == "truth":
                truth[r["object_id"]].append((r["t"], r["receptacle_id"]))
    for v in truth.values():
        v.sort()
    return header, truth


def places_in_window(timeline, a, b):
    """receptacle ids an object occupies at any moment in [a, b)."""
    out = set()
    cur = None
    for t, rec in timeline:
        if t < a:
            cur = rec
        elif t < b:
            if cur is not None:
                out.add(cur)
            cur = rec
            out.add(rec)
        else:
            break
    if cur is not None:
        out.add(cur)
    return out


def study2():
    cells = RES / "overnight_wave/cells/last_seen_no_model"
    homes = ["hh_s2_t03", "hh_s19_t03", "hh_s20_t03", "hh_s32_t03", "hh_s48_t03",
             "hh_s63_t03", "hh_s93_t03", "hh_s109_t03", "hh_s123_t03", "hh_s151_t03"]
    days = list(range(14, 32))
    per_home = {}
    for h in homes:
        cell = cells / h
        cfg = json.load((cell / "cell.json").open())
        bank = pathlib.Path(cfg["overnight_wave"]["bank"])
        header, truth = load_bank_header_and_truth(bank)
        rec_room = header["receptacle_rooms"]
        if isinstance(rec_room, str):
            rec_room = json.loads(rec_room)
        unsensable = set(header.get("unsensable_receptacles", [])) | {r for r, room in rec_room.items() if room == "person_check"}
        residents = header["protocol"]["residents"]
        ill_name = next(r["name"] for r in residents if r["resident_id"] == "resident_1")
        searches = read_searches(cell)
        movers = sorted({r["object_id"] for r in searches if r.get("is_a_mover")})
        looks = read_looks(cell)
        sb = sightings_by_object(looks)
        rs = resident_sightings(looks)

        mover_info = {}
        for m in movers:
            tl = truth[m]
            settled_p = places_in_window(tl, 1 * DAY, 14 * DAY) - unsensable
            sick_p = places_in_window(tl, 14 * DAY, 24 * DAY) - unsensable
            settled_r = {rec_room[p] for p in settled_p}
            sick_r = {rec_room[p] for p in sick_p}
            new_rooms = sick_r - settled_r
            new_places = sick_p - settled_p
            sights = [s for s in sb.get(m, []) if s[0] >= 14 * DAY]
            first_room_day = min((s[1] for s in sights if s[2] in new_rooms), default=None)
            first_place_day = min((s[1] for s in sights if s[3] in new_places), default=None)
            mover_info[m] = {"new_rooms": sorted(new_rooms), "new_places": sorted(new_places),
                             "first_day_sighted_in_a_new_room": first_room_day,
                             "first_day_sighted_at_a_new_place": first_place_day}
        with_room = [m for m in movers if mover_info[m]["new_rooms"]]
        with_place = [m for m in movers if mover_info[m]["new_places"]]
        room_share = [pct(sum(1 for m in with_room if (mover_info[m]["first_day_sighted_in_a_new_room"] or 99) <= d), len(with_room)) for d in days]
        place_share = [pct(sum(1 for m in with_place if (mover_info[m]["first_day_sighted_at_a_new_place"] or 99) <= d), len(with_place)) for d in days]

        # the ill resident: sightings per day; out-of-routine = no sighting of them on days 1-13
        # in the same room within one hour of the same time of day; bedroom by day 09:00-17:00
        r_s = rs.get(ill_name, [])
        settled_rs = [s for s in r_s if 1 <= s[1] <= 13]
        def out_of_routine(s):
            return not any(t[2] == s[2] and tod_close(t[0], s[0]) and t is not s for t in settled_rs)
        # the same measure on the settled days themselves, each sighting judged against the others
        settled_loo = pct(sum(1 for s in settled_rs if out_of_routine(s)), len(settled_rs))
        bedroom = residents[0]["bedroom"]
        res_rows = {}
        for d in days:
            since = [s for s in r_s if 14 <= s[1] <= d]
            res_rows[d] = {"sightings_that_day": sum(1 for s in r_s if s[1] == d),
                           "sightings_since_day_14": len(since),
                           "share_out_of_routine_since_day_14": pct(sum(1 for s in since if out_of_routine(s)), len(since)),
                           "seen_in_bedroom_by_day_since_day_14": any(s[2] == bedroom and 9 * 3600 <= s[0] % DAY < 17 * 3600 for s in since)}
        per_home[h] = {"ill_resident": ill_name, "movers": movers, "mover_info": mover_info,
                       "n_movers": len(movers), "n_movers_with_a_new_room": len(with_room),
                       "n_movers_with_a_new_place": len(with_place),
                       "share_movers_seen_in_new_room_by_day": room_share,
                       "share_movers_seen_at_new_place_by_day": place_share,
                       "ill_resident_by_day": res_rows,
                       "ill_resident_sightings_days_1_13": len(settled_rs),
                       "ill_resident_share_out_of_routine_days_1_13_leave_one_out": settled_loo}

    mean_room = [statistics.fmean(per_home[h]["share_movers_seen_in_new_room_by_day"][i] for h in homes) for i in range(len(days))]
    mean_place = [statistics.fmean(per_home[h]["share_movers_seen_at_new_place_by_day"][i] for h in homes) for i in range(len(days))]

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor("white")
    ax.axvspan(13.5, 23.5, color="#f2f2f2", zorder=0)
    ax.text(18.5, 3, "ill", ha="center", va="bottom", fontsize=13, color="#555555")
    for h in homes:
        ax.plot(days, per_home[h]["share_movers_seen_in_new_room_by_day"], color="#bbbbbb", lw=1.4, marker="o", ms=4)
    ax.plot(days, mean_room, color="black", lw=2.6, marker="o", ms=6)
    ax.set_xlim(13.5, 31.5)
    ax.set_ylim(0, 102)
    ax.set_xticks(days)
    ax.set_xlabel("Day of the run (the routine changes on day 14)", fontsize=13)
    ax.set_ylabel("Percent of the illness movers sighted in their new room since day 14", fontsize=13)
    n_mov = sum(r["n_movers"] for r in per_home.values())
    n_room = sum(r["n_movers_with_a_new_room"] for r in per_home.values())
    lo_m = min(r["n_movers_with_a_new_room"] for r in per_home.values())
    hi_m = max(r["n_movers_with_a_new_room"] for r in per_home.values())
    ax.set_title("Study 2, noticing a routine changed: by each day, the share of the movers the robot has itself seen in their new room (ten households, 8 questions a day)\n"
                 f"A mover's new room is one it truly uses on days 14-23 and never on days 1-13; {n_mov - n_room} of {n_mov} flagged movers have no room-level new room\n"
                 f"and are excluded, leaving {lo_m} to {hi_m} movers per household", fontsize=12)
    ax.grid(axis="y", color="#e5e5e5")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    handles = [Line2D([], [], color="#bbbbbb", lw=1.4, marker="o"), Line2D([], [], color="black", lw=2.6, marker="o")]
    legend_below(fig, ax, handles, ["one household", "mean of the ten households"], ncol=2, bottom=0.14)
    fig.savefig(HERE / "study2.png", facecolor="white")
    plt.close(fig)

    json.dump({"what": "Study 2: visibility of the illness movers and of the ill resident in the last-seen cell's own looks",
               "definitions": {"new room": "a room (receptacle room) the mover truly occupies at some moment on days 14-23 and never on days 1-13, from the bank's truth rows; ON_PERSON and out-of-house excluded",
                               "seen in new room by day d": "at least one sighting of the mover in one of its new rooms at a time from the start of day 14 to the end of day d",
                               "out of routine (resident)": "a sighting of the ill resident on days 14..d with no sighting of them on days 1-13 in the same room within one hour of the same time of day"},
               "households": homes, "days": days, "per_household": per_home,
               "mean_share_movers_seen_in_new_room_by_day": mean_room,
               "mean_share_movers_seen_at_new_place_by_day": mean_place},
              (HERE / "study2.json").open("w"), indent=1)
    return per_home, mean_room, mean_place, days


# ============================================================================= study 3

def parse_within_budget(path):
    """budget -> {policy: [found of findable, of towels, of other things]} from the
    'within the budget of B' tables of a study-3 results file."""
    text = pathlib.Path(path).read_text().splitlines()
    out = {}
    budget = None
    in_table = False
    for line in text:
        m = re.match(r"within the budget of (\d+)", line)
        if m:
            budget = int(m.group(1))
            out[budget] = {}
            in_table = False
            continue
        if budget is None:
            continue
        if line.startswith("policy "):
            in_table = True
            continue
        if in_table:
            if not line.strip():
                in_table = False
                budget = None
                continue
            if line.startswith("  start"):
                continue
            name = line[:42].strip()
            nums = line[42:].split()
            out[budget][name] = [float(x) for x in nums[:3]]
    return out


def study3():
    d = REPO / "coordination/studies/study3_costly_looks"
    gate = parse_within_budget(d / "gate_oracle_within_memory.txt")
    dry = parse_within_budget(d / "dry_run_fake_nearest.txt")
    budgets = [30, 60, 120]
    not_rules = {"random", "distance order", "oracle within memory", "oracle within memory, then last seen", "oracle", "model"}
    rows = {}
    for b in budgets:
        g = gate[b]
        for name, v in g.items():
            if name in dry[b]:
                assert dry[b][name] == v, (b, name, v, dry[b][name])
        rules = {k: v for k, v in g.items() if k not in not_rules}
        best = max(rules, key=lambda k: rules[k][2])
        best_all = max(rules, key=lambda k: rules[k][0])
        rows[b] = {"best_rule": best, "best_rule_other_things": 100 * rules[best][2],
                   "best_rule_on_all_findable": best_all, "best_rule_all_findable": 100 * rules[best_all][0],
                   "last_seen_nearest_other_things": 100 * g["last seen (nearest)"][2],
                   "ceiling_other_things": 100 * g["oracle within memory, then last seen"][2],
                   "ceiling_all_findable": 100 * g["oracle within memory, then last seen"][0],
                   "floor_oracle_within_memory_only_other_things": 100 * g["oracle within memory"][2],
                   "plain_oracle_other_things": 100 * g["oracle"][2],
                   "model_fake_nearest_other_things": 100 * dry[b]["model"][2] if "model" in dry[b] else None}
    n_other = 67
    n_findable = 155

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor("white")
    ax.plot(budgets, [rows[b]["plain_oracle_other_things"] for b in budgets], color="#555555", linestyle=":", lw=1.8, marker="D", ms=6, label="plain oracle (knows where everything is): 100")
    ax.plot(budgets, [rows[b]["ceiling_other_things"] for b in budgets], color=C["ceiling"], linestyle=DASH_LOOSE, lw=2, marker="^", ms=7, label="record-reachable ceiling: oracle among remembered places, then last-seen's exploration")
    ax.plot(budgets, [rows[b]["best_rule_other_things"] for b in budgets], color=C["best_rule"], lw=2.4, marker="s", ms=7, label="best simple rule at that budget (named at each point)")
    ax.plot(budgets, [rows[b]["last_seen_nearest_other_things"] for b in budgets], color=C["last_seen"], lw=2, marker="o", ms=6, label="last seen (nearest)")
    for b in budgets:
        # annotations in a block below the lowest line at each budget (to the right of the last budget), each naming its line
        texts = [(f'ceiling {rows[b]["ceiling_other_things"]:.1f}', "black"),
                 (f'best rule {rows[b]["best_rule_other_things"]:.1f}: {rows[b]["best_rule"]}', C["best_rule"]),
                 (f'last seen (nearest) {rows[b]["last_seen_nearest_other_things"]:.1f}', C["last_seen"])]
        if b == budgets[-1]:
            ys = [rows[b]["ceiling_other_things"], rows[b]["best_rule_other_things"] - 1.5, rows[b]["last_seen_nearest_other_things"] - 5]
            for (t, col), yy in zip(texts, ys):
                ax.annotate(t, (b, yy), textcoords="offset points", xytext=(12, 0), ha="left", va="center", fontsize=11, color=col)
        else:
            y0 = rows[b]["last_seen_nearest_other_things"] - 6
            for i, (t, col) in enumerate(texts):
                ax.annotate(t, (b, y0 - 4.5 * i), textcoords="offset points", xytext=(0, 0), ha="left", va="center", fontsize=11, color=col)
    ax.set_xscale("log")
    ax.set_xticks(budgets)
    ax.set_xticklabels([str(b) for b in budgets])
    ax.minorticks_off()
    ax.set_xlim(25, 200)
    ax.set_ylim(0, 105)
    ax.set_xlabel("Budget per question (5 units per look, 10 per look into an occupied room)", fontsize=13)
    ax.set_ylabel(f"Found within budget, percent of findable non-towel things (n = {n_other} questions)", fontsize=13)
    ax.set_title("Study 3, costly looks: found within budget on findable non-towel things, one household, numbers read from the study's result files", fontsize=13)
    ax.grid(axis="y", color="#e5e5e5")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    h_, l_ = ax.get_legend_handles_labels()
    legend_below(fig, ax, h_, l_, ncol=2, bottom=0.18)
    fig.savefig(HERE / "study3.png", facecolor="white")
    plt.close(fig)

    json.dump({"what": "Study 3: found within budget, percent, read from gate_oracle_within_memory.txt (checked equal to dry_run_fake_nearest.txt on shared rows); n = 1 household",
               "n_questions_other_things": n_other, "n_questions_findable": n_findable, "budgets": budgets,
               "by_budget": rows, "all_policies_within_budget": {str(b): gate[b] for b in budgets}},
              (HERE / "study3.json").open("w"), indent=1)
    return rows, n_other, n_findable


# ============================================================================= study 4

def study4():
    spec = importlib.util.spec_from_file_location(
        "score_rare_movers", REPO / "coordination/studies/study4_rare_things_that_matter/score_rare_movers.py")
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)
    banks, wave, reference = (S.LOADS[8][k] for k in ("banks", "wave", "reference"))
    arms = ["last_seen_no_model", "most_frequent_no_model", "same_time_of_day_no_model", "alternate_room_no_model"]
    homes = sorted((p.stem for p in banks.glob("hh_s*_t03.jsonl")), key=lambda n: int(n.split("_")[1][1:]))
    bank_qs = {}
    for home in homes:
        rows = [json.loads(l) for l in (banks / f"{home}.jsonl").open() if '"kind": "question"' in l]
        bank_qs[home] = {r["question_id"]: r for r in rows if r["kind"] == "question"}
    refs = {home: (S.searches(reference / home) if (reference / home / "searches.jsonl").exists() else {}) for home in homes}

    slices = ["first_after_move", "unseen", "after_a_miss", "seen", "background", "ordinary"]
    subsets = ["pill_box_forward", "pill_box_return", "car_keys_first"]
    arm_counts = {a: {s: [0, 0] for s in slices + subsets} for a in arms}
    per_home_arm = {a: {h: {} for h in homes} for a in arms}   # arm -> home -> slice -> [right, n]
    refused = []
    for arm in arms:
        for home in homes:
            cell = wave / "cells" / arm / home
            ok, why = S.complete(cell) if cell.exists() else (False, "no such cell")
            if not ok:
                refused.append(f"{arm}/{home}: {why}")
                continue
            rec = S.score_cell(cell, bank_qs[home], refs[home])
            for s in slices:
                arm_counts[arm][s][0] += rec["right"][s]
                arm_counts[arm][s][1] += rec["n"][s]
                per_home_arm[arm][home][s] = [rec["right"][s], rec["n"][s]]
            for s in subsets:
                arm_counts[arm][s][0] += rec[s][0]
                arm_counts[arm][s][1] += rec[s][1]
                per_home_arm[arm][home][s] = list(rec[s])

    # ceilings on the last-seen cell's own slices (its looks decide unseen/seen)
    ceil = {s: {"loose": 0, "routine": 0, "n": 0} for s in slices + subsets}
    per_home_ceil = {h: {s: {"loose": 0, "routine": 0, "n": 0} for s in slices + subsets} for h in homes}
    per_move = []
    for home in homes:
        cell = wave / "cells/last_seen_no_model" / home
        rows = S.searches(cell)
        sb = sightings_by_object(read_looks(cell))
        bank_q = bank_qs[home]
        seen_at = S.sightings(cell)
        for qid, r in rows.items():
            q = bank_q[qid]
            lo, ro = ceilings(r, sb)
            member = []
            if q.get("within_24h_of_rare_move"):
                times = seen_at.get((r["object_id"], r["true_place"]), [])
                unseen = not any(q["rare_move_t"] < t < r["time"] for t in times)
                rank = q.get("rare_move_rank")
                if rank == 1:
                    member.append("first_after_move")
                    if r["object_class"] == "pill_box" and "unwell" in q["rare_move_cause"]:
                        member.append("pill_box_forward")
                    if r["object_class"] == "pill_box" and "well again" in q["rare_move_cause"]:
                        member.append("pill_box_return")
                    if r["object_class"] == "car_keys":
                        member.append("car_keys_first")
                    per_move.append({"home": home, "question_id": qid, "object_id": r["object_id"], "day": r["day"],
                                     "true_room": r["true_room"], "unseen_for_last_seen": unseen,
                                     "last_seen_right": r.get("found_at_step") == 1, "loose": lo, "routine": ro,
                                     "cause": q["rare_move_cause"]})
                member.append("unseen" if unseen else "seen")
                if unseen and rank != 1:
                    member.append("after_a_miss")
            elif q.get("rare_mover"):
                member.append("background")
            else:
                member.append("ordinary")
            for s in member:
                for tgt in (ceil[s], per_home_ceil[home][s]):
                    tgt["loose"] += lo
                    tgt["routine"] += ro
                    tgt["n"] += 1

    table = {}
    for s in slices + subsets:
        table[s] = {a: {"right": arm_counts[a][s][0], "n": arm_counts[a][s][1], "pct": pct(*arm_counts[a][s])} for a in arms}
        table[s]["loose_ceiling"] = {"right": ceil[s]["loose"], "n": ceil[s]["n"], "pct": pct(ceil[s]["loose"], ceil[s]["n"])}
        table[s]["routine_ceiling"] = {"right": ceil[s]["routine"], "n": ceil[s]["n"], "pct": pct(ceil[s]["routine"], ceil[s]["n"])}
        best = max(arms, key=lambda a: table[s][a]["pct"])
        table[s]["best_rule"] = best

    # ---- chart: two panels, slices and the pill box / keys subsets
    bars = [("last_seen_no_model", "last-seen", C["last_seen"], None),
            ("most_frequent_no_model", "most frequent", C["most_frequent"], None),
            ("same_time_of_day_no_model", "same time of day", C["same_time_of_day"], None),
            ("alternate_room_no_model", "alternate room", C["alternate_room"], None),
            ("routine_ceiling", ROUTINE_LABEL, C["routine"], DASH_ROUTINE),
            ("loose_ceiling", LOOSE_LABEL, C["ceiling"], DASH_LOOSE)]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIGSIZE, dpi=DPI, gridspec_kw={"width_ratios": [6, 3]})
    fig.patch.set_facecolor("white")
    g1 = [("first_after_move", "first question\nafter each move"), ("unseen", "unseen: asked\nbefore a sighting\nat the new place"),
          ("after_a_miss", "after a miss:\nunseen, not the\nfirst after it"),
          ("seen", "seen: asked\nafter one"), ("background", "background:\nrare mover, no\nmove in 24 h"), ("ordinary", "ordinary\nquestions")]
    g2 = [("pill_box_forward", "pill box, forward\nmove (to the\nbedside)"), ("pill_box_return", "pill box,\nreturn move"), ("car_keys_first", "car keys")]
    w = 0.13
    for ax, groups in ((ax1, g1), (ax2, g2)):
        for gi, (s, label) in enumerate(groups):
            for bi, (key, name, col, dash) in enumerate(bars):
                x = gi + (bi - 2.5) * w
                v = table[s][key]["pct"]
                if dash is None:
                    ax.bar(x, v, w * 0.92, color=col, edgecolor="white", linewidth=0.5)
                    ax.text(x, v + 1, f"{v:.0f}", ha="center", va="bottom", fontsize=8, color="#333333")
                else:
                    ax.bar(x, v, w * 0.92, color="white", edgecolor=col, linewidth=1.6, linestyle=dash)
                    # the two ceiling labels sit side by side; lift the second when they would touch
                    lift = 5 if key == "loose_ceiling" and abs(v - table[s]["routine_ceiling"]["pct"]) < 6 else 1
                    ax.text(x, v + lift, f"{v:.0f}", ha="center", va="bottom", fontsize=8, color=col)
        ax.set_xticks(range(len(groups)))
        ax.set_xticklabels([f"{l}\nn = {table[s]['last_seen_no_model']['n']}" for s, l in groups], fontsize=9.5)
        ax.set_ylim(0, 108)
        ax.grid(axis="y", color="#e5e5e5")
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    ax1.set_ylabel("First guess right, percent (pooled over ten households)", fontsize=12)
    ax1.set_title("By question slice", fontsize=12)
    ax2.set_title("First question after the move, by object", fontsize=12)
    fig.suptitle("Study 4, rare things that matter: first guess right of four simple rules and the two record-reachable ceilings (ten households, 8 ordinary questions a day)\n"
                 "Loose ceiling: the true room is one the robot had itself sighted the object in before.\n"
                 "Routine ceiling: the true room is the room of its most recent sighting, or it was sighted there at the same hour on an earlier day.",
                 fontsize=11.5)
    fig.text(0.5, 0.12, "Each rule's unseen / after-a-miss / seen slices are decided by that arm's own looks; the ceilings and their slices come from the last-seen arm's looks,\n"
                        "so on a slice where the arms differ a ceiling can sit a point below a rule (after a miss: ceiling 0, each rule 1 right of about 105).",
             ha="center", va="center", fontsize=10, color="#444444")
    handles = [Patch(facecolor=col, edgecolor="white") if dash is None else Patch(facecolor="white", edgecolor=col, linestyle=dash, linewidth=1.6) for _, _, col, dash in bars]
    legend_below(fig, ax1, handles, [n for _, n, _, _ in bars], ncol=3, bottom=0.25)
    fig.subplots_adjust(top=0.85, wspace=0.16)
    fig.savefig(HERE / "study4.png", facecolor="white")
    plt.close(fig)

    json.dump({"what": "Study 4: first guess right per rule and record-reachable ceilings per slice, pooled over the ten households",
               "notes": ["unseen/seen for each rule are that arm's own slices (its looks decide them), as in score_rare_movers.py; the ceilings' unseen/seen are the last-seen cell's",
                         "ceilings are from the last-seen cell's looks"],
               "arms": arms, "households": homes, "refused_cells": refused, "table": table,
               "per_household_rules": per_home_arm, "per_household_ceilings": per_home_ceil, "per_move_last_seen": per_move},
              (HERE / "study4.json").open("w"), indent=1)
    return table, refused, per_home_arm, per_home_ceil, homes


# ============================================================================= summary

def boot_homes(per_home, reps=10000, seed=1):
    """per_home: list of (rule_right, ceiling_right, n). Resample households with replacement,
    gap = pooled ceiling percent minus pooled rule percent; 2.5th and 97.5th percentile."""
    import random
    rng = random.Random(seed)
    k = len(per_home)
    gaps = []
    for _ in range(reps):
        pick = [per_home[rng.randrange(k)] for _ in range(k)]
        n = sum(p[2] for p in pick)
        if n == 0:
            continue
        gaps.append(100 * (sum(p[1] for p in pick) - sum(p[0] for p in pick)) / n)
    gaps.sort()
    return gaps[int(0.025 * len(gaps))], gaps[min(len(gaps) - 1, int(0.975 * len(gaps)))]


def boot_questions(both, ceiling_only, rule_only, neither, reps=10000, seed=1):
    """Paired bootstrap over questions given the four pairing counts."""
    import random
    rng = random.Random(seed)
    cells = [(1, 1)] * both + [(0, 1)] * ceiling_only + [(1, 0)] * rule_only + [(0, 0)] * neither
    n = len(cells)
    gaps = []
    for _ in range(reps):
        pick = [cells[rng.randrange(n)] for _ in range(n)]
        gaps.append(100 * (sum(c[1] for c in pick) - sum(c[0] for c in pick)) / n)
    gaps.sort()
    return gaps[int(0.025 * len(gaps))], gaps[min(len(gaps) - 1, int(0.975 * len(gaps)))]


def summary(t1, r3, t4, per_home_arm, per_home_ceil, homes4):
    homes1 = ["hh_s2_t03", "hh_s32_t03", "hh_s48_t03"]
    short = {"last_seen_no_model": "last-seen", "most_frequent_no_model": "most frequent",
             "same_time_of_day_no_model": "same time of day", "alternate_room_no_model": "alternate room"}
    rows = []

    def s1_row(label, key):
        ph = [(t1[key][h]["last_seen"], t1[key][h]["loose"], t1[key][h]["n"]) for h in homes1]
        n = sum(p[2] for p in ph)
        rows.append({"label": label, "rule_name": "last-seen", "rule": 100 * sum(p[0] for p in ph) / n,
                     "ceiling": 100 * sum(p[1] for p in ph) / n, "n": n, "households": 3,
                     "interval": boot_homes(ph), "interval_over": "households"})
    s1_row("Study 1, return windows (days 24-28 and 42-46)", "days 24-28 and 42-46")
    s1_row("Study 1, ill days, mover questions", "ill days, movers")

    # study 3, budget 60, non-towel: pairing reconstructed from the printed counts (see HEADROOM.md)
    r = r3[60]
    n3 = 67
    rule_k = round(r["best_rule_other_things"] * n3 / 100)
    ceil_k = round(r["ceiling_other_things"] * n3 / 100)
    assert (rule_k, ceil_k) == (30, 36), (rule_k, ceil_k)
    rows.append({"label": "Study 3, non-towel things, found within budget 60",
                 "rule_name": r["best_rule"], "rule": r["best_rule_other_things"], "ceiling": r["ceiling_other_things"],
                 "n": n3, "households": 1, "interval": boot_questions(30, 6, 0, 31), "interval_over": "questions"})

    def s4_row(label, s):
        best = t4[s]["best_rule"]
        ph = [(per_home_arm[best][h][s][0], per_home_ceil[h][s]["loose"], per_home_ceil[h][s]["n"]) for h in homes4]
        for h in homes4:
            assert per_home_arm[best][h][s][1] == per_home_ceil[h][s]["n"], (s, h)
        n = sum(p[2] for p in ph)
        name = short[best] if t4[s][best]["pct"] > 0 else "all four rules 0"
        rows.append({"label": label, "rule_name": name, "rule": 100 * sum(p[0] for p in ph) / n,
                     "ceiling": 100 * sum(p[1] for p in ph) / n, "n": n, "households": len(homes4),
                     "interval": boot_homes(ph), "interval_over": "households"})
    s4_row("Study 4, first question after each move", "first_after_move")
    s4_row("Study 4, car keys, first question after the move", "car_keys_first")
    s4_row("Study 4, pill box forward move, first question after it", "pill_box_forward")
    s4_row("Study 4, ordinary questions", "ordinary")

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor("white")
    ys = list(range(len(rows)))[::-1]
    for y, rw in zip(ys, rows):
        lo, hi = rw["interval"]
        ax.plot([rw["ceiling"], 100], [y, y], color=C["knowledge"], lw=5, solid_capstyle="butt", zorder=1)
        ax.plot([rw["rule"], rw["ceiling"]], [y, y], color="#555555", lw=1.6, zorder=2)
        ax.plot([rw["rule"] + lo, rw["rule"] + hi], [y - 0.22, y - 0.22], color="#555555", lw=1.0, zorder=2)
        for xx in (rw["rule"] + lo, rw["rule"] + hi):
            ax.plot([xx, xx], [y - 0.3, y - 0.14], color="#555555", lw=1.0, zorder=2)
        ax.plot(rw["rule"], y, marker="o", ms=11, color=C["last_seen"], zorder=3, linestyle="none")
        ax.plot(rw["ceiling"], y, marker="D", ms=9, color="black", zorder=3, linestyle="none")
        if rw["ceiling"] - rw["rule"] < 0.5:
            ax.text(rw["ceiling"] + 1.2, y + 0.2, f'rule {rw["rule"]:.1f} ({rw["rule_name"]}), ceiling {rw["ceiling"]:.1f}', ha="left", va="bottom", fontsize=9.5, color="#555555")
        elif rw["ceiling"] - rw["rule"] < 12:
            ax.text(rw["rule"] - 1.2, y + 0.2, f'{rw["rule"]:.1f} {rw["rule_name"]}', ha="right", va="bottom", fontsize=9.5, color="#555555")
            ax.text(rw["ceiling"] + 1.2, y + 0.2, f'{rw["ceiling"]:.1f}', ha="left", va="bottom", fontsize=9.5, color="black")
        else:
            ax.text(rw["rule"], y + 0.2, f'{rw["rule"]:.1f} {rw["rule_name"]}', ha="center", va="bottom", fontsize=9.5, color="#555555")
            ax.text(rw["ceiling"], y + 0.2, f'{rw["ceiling"]:.1f}', ha="center", va="bottom", fontsize=9.5, color="black")
        gap = rw["ceiling"] - rw["rule"]
        ax.text(102, y, f'gap {gap:+.1f}  [{lo:+.1f}, {hi:+.1f}]\n{rw["interval_over"]}, n = {rw["n"]}, {rw["households"]} household{"s" if rw["households"] > 1 else ""}',
                ha="left", va="center", fontsize=9.5, color="#222222")
    ax.set_yticks(ys)
    ax.set_yticklabels([rw["label"] for rw in rows], fontsize=10.5)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlabel("Percent of questions (first guess right; study 3: found within a budget of 60)", fontsize=12)
    ax.set_title("Headroom in the four setups: the best simple rule, the loose record ceiling, and what is left to knowledge", fontsize=13)
    ax.grid(axis="x", color="#e5e5e5")
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    handles = [Line2D([], [], marker="o", ms=11, color=C["last_seen"], linestyle="none"),
               Line2D([], [], marker="D", ms=9, color="black", linestyle="none"),
               Line2D([], [], color="#555555", lw=1.6),
               Line2D([], [], color="#555555", lw=1.0, marker="|", ms=8),
               Line2D([], [], color=C["knowledge"], lw=5)]
    labels = ["best simple rule (named)", "loose ceiling, from the last-seen robot's own record",
              "the room a better rule could take (rule to ceiling)",
              "2.5th to 97.5th percentile of that gap, bootstrap over households (study 3: over questions)",
              "the room only knowledge could take (ceiling to 100)"]
    fig.subplots_adjust(left=0.34, right=0.80, bottom=0.2)
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=10.5, bbox_to_anchor=(0.5, 0.01))
    fig.savefig(HERE / "summary.png", facecolor="white")
    plt.close(fig)
    json.dump({"what": "summary rows: best simple rule, loose record ceiling, gap and bootstrap interval",
               "study3_pairing_note": "budget 60, 67 non-towel findable questions: rule finds 30, ceiling 36; the printed paired section (12 discordant over all 155 findable, net 0; towels 88 vs 82 in the rule's favour) fixes the non-towel pairing as 30 both, 6 ceiling only, 0 rule only, 31 neither",
               "rows": rows}, (HERE / "summary.json").open("w"), indent=1)
    return rows


# ============================================================================= write-up

def f1(x):
    return "-" if x != x else f"{x:.1f}"


def main():
    t1, mean1 = study1()
    p2, mean_room, mean_place, days2 = study2()
    r3, n_other, n_findable = study3()
    t4, refused4, per_home_arm4, per_home_ceil4, homes4 = study4()
    srows = summary(t1, r3, t4, per_home_arm4, per_home_ceil4, homes4)

    # the reading check asked for: record plus notes on days 24-28
    notes_2428 = [mean1["notes"][d - 1] for d in range(24, 29)]
    check_2428 = {"per_day_mean_over_households": notes_2428, "mean_of_days": statistics.fmean(notes_2428),
                  "pooled_table_value": t1["days 24-28"]["pooled"]["notes_pct"]}

    L = []
    p = L.append
    p("# Headroom: best simple rule against what the robot's own record could reach\n")
    p("Computed by `headroom.py` beside this file; charts `summary.png` and `study1.png` to `study4.png`, numbers `summary.json` and `study1.json` to `study4.json`. CPU only, no model run.\n")
    p("## Summary: gap from the best simple rule to the loose record ceiling\n")
    p("One row per setup and slice, as in `summary.png`. Gap = loose ceiling minus best rule, in points of first guess right (study 3: found within a budget of 60). "
      "Interval = 2.5th to 97.5th percentile of the gap under a bootstrap over households (10000 draws); for study 3's one household it is a paired bootstrap over its 67 questions, "
      "with the pairing reconstructed from the printed counts (rule 30 found, ceiling 36; the paired section's 12 discordant over all 155 findable with net 0 and towels 88 against 82 leave the 6 non-towel discordant questions all in the ceiling's favour).\n")
    p("| setup and slice | best rule | best rule, percent | loose ceiling | gap | interval | interval over | n questions | n households |")
    p("|---|---|---|---|---|---|---|---|---|")
    for rw in srows:
        lo, hi = rw["interval"]
        p(f"| {rw['label']} | {rw['rule_name']} | {rw['rule']:.1f} | {rw['ceiling']:.1f} | {rw['ceiling'] - rw['rule']:+.1f} | [{lo:+.1f}, {hi:+.1f}] | {rw['interval_over']} | {rw['n']} | {rw['households']} |")
    p("")
    p(f"Reading check, record plus notes on days 24-28 (mean over the three households per day): " + ", ".join(f"day {d}: {v:.1f}" for d, v in zip(range(24, 29), notes_2428)) +
      f"; mean of the five days {check_2428['mean_of_days']:.1f}, pooled over the 360 questions {check_2428['pooled_table_value']:.1f} (equal n per day, so the two agree). Days 26-28 are {notes_2428[2]:.1f}, {notes_2428[3]:.1f} and {notes_2428[4]:.1f}; days 24 and 25 are {notes_2428[0]:.1f} and {notes_2428[1]:.1f}, which pull the window mean down.\n")
    p("Definitions, stated once. First guess right = `found_at_step == 1` on a search row (room level). "
      "Loose ceiling = the true room at question time is a room in which the robot had itself sighted that object at an earlier time. "
      "Routine ceiling = the true room is the room of the object's most recent earlier sighting, or the object was sighted in the true room on an earlier day within one hour of the same time of day. "
      "Both ceilings use the last-seen cell's own looks, and only sightings strictly before the question's time (a few questions share a time stamp with another question; sightings from that other search are not counted, which costs the ceilings at most one question in 3528 in study 1). "
      "Check made: in study 1, of the 3079 questions last-seen gets right, 3078 have loose ceiling 1 and one is a guess with no record. Headroom = ceiling minus the best simple rule on the same questions. "
      "Study 3 uses its own, already computed, ceiling (oracle among remembered places, then last-seen's exploration) and score (found within budget).\n")

    # ---- study 1
    p("## Study 1, memory through a shift and back (three households, 49 days, 24 questions a day)\n")
    p("Last-seen is the only simple rule in this run, so it is the best rule. The ceilings are from the last-seen cell's looks; the last two columns give the same ceilings from the notes arm's own looks, because that arm's searches open different rooms and so its record differs.\n")
    p("| questions | last-seen (best rule) | record plus notes | loose ceiling | routine ceiling | headroom, loose | headroom, routine | n questions | n households | loose ceiling from the notes arm's looks | routine, same |")
    p("|---|---|---|---|---|---|---|---|---|---|---|")
    for name in ["days 24-28", "days 42-46", "days 24-28 and 42-46", "days 24-28, movers", "days 42-46, movers",
                 "days 24-28 and 42-46, movers", "ill days 14-23 and 32-41", "ill days, movers", "all days 1-49", "all days, movers"]:
        t = t1[name]["pooled"]
        p(f"| {name} | {f1(t['last_seen_pct'])} | {f1(t['notes_pct'])} | {f1(t['loose_pct'])} | {f1(t['routine_pct'])} | "
          f"{f1(t['loose_pct'] - t['last_seen_pct'])} | {f1(t['routine_pct'] - t['last_seen_pct'])} | {t['n']} | 3 | "
          f"{f1(t['loose_from_notes_looks_pct'])} | {f1(t['routine_from_notes_looks_pct'])} |")
    p("")
    p("Per household, days 24-28 and 42-46 pooled (right / n): " + "; ".join(
        f"{h}: last-seen {t1['days 24-28 and 42-46'][h]['last_seen']}, notes {t1['days 24-28 and 42-46'][h]['notes']}, loose {t1['days 24-28 and 42-46'][h]['loose']}, routine {t1['days 24-28 and 42-46'][h]['routine']} of {t1['days 24-28 and 42-46'][h]['n']}"
        for h in ["hh_s2_t03", "hh_s32_t03", "hh_s48_t03"]) + ".\n")
    # where by day
    days = list(range(1, 50))
    gaps = {d: mean1["loose"][i] - mean1["last_seen"][i] for i, d in enumerate(days)}
    gaps_r = {d: mean1["routine"][i] - mean1["last_seen"][i] for i, d in enumerate(days)}
    def mean_over(ds, g):
        return statistics.fmean(g[d] for d in ds)
    p(f"Mean daily gap to the loose ceiling, by stretch of days: settled 1-13 {mean_over(range(1, 14), gaps):.1f}, ill 14-23 {mean_over(range(14, 24), gaps):.1f}, "
      f"return 24-31 {mean_over(range(24, 32), gaps):.1f}, ill 32-41 {mean_over(range(32, 42), gaps):.1f}, return 42-49 {mean_over(range(42, 50), gaps):.1f} points. "
      f"To the routine ceiling: {mean_over(range(1, 14), gaps_r):.1f}, {mean_over(range(14, 24), gaps_r):.1f}, {mean_over(range(24, 32), gaps_r):.1f}, {mean_over(range(32, 42), gaps_r):.1f}, {mean_over(range(42, 50), gaps_r):.1f}. "
      f"Largest single-day gaps to the loose ceiling: " + ", ".join(f"day {d} ({gaps[d]:.0f})" for d in sorted(days, key=lambda d: -gaps[d])[:5]) + ".\n")
    tw = t1["days 24-28 and 42-46"]["pooled"]; tm = t1["days 24-28 and 42-46, movers"]["pooled"]
    ti = t1["ill days 14-23 and 32-41"]["pooled"]
    n_exceed = sum(1 for i, d in enumerate(days) if mean1["notes"][i] > mean1["loose"][i] + 1e-9)
    exceed_days = [d for i, d in enumerate(days) if mean1["notes"][i] > mean1["loose"][i] + 1e-9]
    p(f"Note. The headroom sits in the two return windows and on the mover questions there: in days 24-28 and 42-46 pooled both ceilings are {tw['loose_pct']:.1f} (every asked object had been sighted in its settled room before the illness) while last-seen is {tw['last_seen_pct']:.1f} on all questions and {tm['last_seen_pct']:.1f} on the {tm['n']} mover questions, so the gap is {tw['loose_pct'] - tw['last_seen_pct']:.1f} and {tm['loose_pct'] - tm['last_seen_pct']:.1f} points; "
      f"during the ill days the ceilings themselves fall (loose {ti['loose_pct']:.1f}, routine {ti['routine_pct']:.1f} against last-seen {ti['last_seen_pct']:.1f}), so the gap there is {ti['loose_pct'] - ti['last_seen_pct']:.1f} points. "
      f"The record-plus-notes method is above the last-seen-record loose ceiling on {n_exceed} of 49 days (days {', '.join(map(str, exceed_days))}), which is possible because that arm opens different rooms and so holds a different record, and on day 1 because a guess with no record can still be right; by its own looks its loose ceiling on the ill days is {ti['loose_from_notes_looks_pct']:.1f}.\n")

    # ---- study 2
    p("## Study 2, noticing a routine changed (ten households, 31 days, change on day 14)\n")
    p("This setup scores detection, not first guess right, so the headroom here is visibility: whether the robot's own record contains the change at all. "
      "Movers are the objects flagged `is_a_mover` on the search rows; a mover's new room is a room it truly occupies on days 14-23 and never on days 1-13 (bank truth rows; on-person and out-of-house excluded). "
      "Residents do appear in `looks.jsonl` (`residents_seen`, a list of names on each look, the room being the look's target), so the ill resident (resident 1 in every bank) is reported too.\n")
    homes2 = list(p2)
    p("| household | movers | with a new room | seen in a new room by day 14 | by day 16 | by day 18 | by day 23 | by day 31 | with a new place | seen at a new place by day 23 | ill resident sightings days 1-13 | days 14-23 | share out of routine by day 23 | same measure on days 1-13 (leave one out) | seen in bedroom 09-17 by day 16 |")
    p("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    idx = {d: i for i, d in enumerate(days2)}
    for h in homes2:
        r = p2[h]
        rs = r["ill_resident_by_day"]
        p(f"| {h} | {r['n_movers']} | {r['n_movers_with_a_new_room']} | {f1(r['share_movers_seen_in_new_room_by_day'][idx[14]])} | {f1(r['share_movers_seen_in_new_room_by_day'][idx[16]])} | "
          f"{f1(r['share_movers_seen_in_new_room_by_day'][idx[18]])} | {f1(r['share_movers_seen_in_new_room_by_day'][idx[23]])} | {f1(r['share_movers_seen_in_new_room_by_day'][idx[31]])} | "
          f"{r['n_movers_with_a_new_place']} | {f1(r['share_movers_seen_at_new_place_by_day'][idx[23]])} | {r['ill_resident_sightings_days_1_13']} | {rs[23]['sightings_since_day_14']} | "
          f"{f1(rs[23]['share_out_of_routine_since_day_14'])} | {f1(r['ill_resident_share_out_of_routine_days_1_13_leave_one_out'])} | {'yes' if rs[16]['seen_in_bedroom_by_day_since_day_14'] else 'no'} |")
    mean_oor = statistics.fmean(p2[h]["ill_resident_by_day"][23]["share_out_of_routine_since_day_14"] for h in homes2)
    mean_loo = statistics.fmean(p2[h]["ill_resident_share_out_of_routine_days_1_13_leave_one_out"] for h in homes2)
    n_bed16 = sum(1 for h in homes2 if p2[h]["ill_resident_by_day"][16]["seen_in_bedroom_by_day_since_day_14"])
    p(f"| mean | | | {f1(mean_room[idx[14]])} | {f1(mean_room[idx[16]])} | {f1(mean_room[idx[18]])} | {f1(mean_room[idx[23]])} | {f1(mean_room[idx[31]])} | | {f1(mean_place[idx[23]])} | | | {f1(mean_oor)} | {f1(mean_loo)} | {n_bed16} of 10 |")
    p("")
    p("| day | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 27 | 31 |")
    p("|---|" + "---|" * 12)
    p("| mean share of movers seen in a new room, percent | " + " | ".join(f1(mean_room[idx[d]]) for d in [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 27, 31]) + " |")
    p("| mean share of movers seen at a new place, percent | " + " | ".join(f1(mean_place[idx[d]]) for d in [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 27, 31]) + " |")
    p("")
    n_no_room = sum(r["n_movers"] - r["n_movers_with_a_new_room"] for r in p2.values())
    n_mov = sum(r["n_movers"] for r in p2.values())
    p(f"Note. Of {n_mov} flagged movers over the ten households, {n_no_room} have no room-level new room (they move within a room or to a place they also used on settled days); the room-level shares are over the rest. "
      f"By the end of day 14 the robot has seen on average {mean_room[idx[14]]:.0f} percent of the movers in a new room, by day 16 {mean_room[idx[16]]:.0f} percent and by day 23 {mean_room[idx[23]]:.0f} percent, so the days on which the record does not yet hold the change are 14 to about 17. "
      f"For the ill resident, {mean_oor:.0f} percent of sightings on days 14-23 are out of routine against {mean_loo:.0f} percent for the settled days judged the same way, and {n_bed16} of 10 households have a daytime bedroom sighting of them by day 16.\n")

    # ---- study 3
    p("## Study 3, costly looks (one household, 248 searches; found within budget, of findable non-towel things)\n")
    p("Numbers are read from `coordination/studies/study3_costly_looks/gate_oracle_within_memory.txt` (the 'within the budget' tables, column 3) and checked against `dry_run_fake_nearest.txt` on every shared row. Here the ceiling is the study's own: an oracle choosing among remembered places, then last-seen's exploration when memory has nothing; the plain oracle is 100.\n")
    p("| budget | best rule | best rule, percent | ceiling (oracle within memory, then last seen) | headroom | plain oracle | last seen (nearest) | floor: oracle within memory only | n questions | n households |")
    p("|---|---|---|---|---|---|---|---|---|---|")
    for b in [30, 60, 120]:
        r = r3[b]
        p(f"| {b} | {r['best_rule']} | {f1(r['best_rule_other_things'])} | {f1(r['ceiling_other_things'])} | {f1(r['ceiling_other_things'] - r['best_rule_other_things'])} | 100 | {f1(r['last_seen_nearest_other_things'])} | {f1(r['floor_oracle_within_memory_only_other_things'])} | {n_other} | 1 |")
    p("")
    p(f"Note. The gap between the best rule and the record-reachable ceiling is {r3[30]['ceiling_other_things'] - r3[30]['best_rule_other_things']:.1f}, {r3[60]['ceiling_other_things'] - r3[60]['best_rule_other_things']:.1f} and {r3[120]['ceiling_other_things'] - r3[120]['best_rule_other_things']:.1f} points at budgets 30, 60 and 120, "
      f"while the gap to the plain oracle is {100 - r3[30]['best_rule_other_things']:.0f}, {100 - r3[60]['best_rule_other_things']:.0f} and {100 - r3[120]['best_rule_other_things']:.0f} points. On all findable things (towels included, n = {n_findable}) the ceiling is {r3[30]['ceiling_all_findable']:.1f}, {r3[60]['ceiling_all_findable']:.1f}, {r3[120]['ceiling_all_findable']:.1f} against the rule that is best on that count, {r3[30]['best_rule_all_findable']:.1f} ({r3[30]['best_rule_on_all_findable']}), {r3[60]['best_rule_all_findable']:.1f} ({r3[60]['best_rule_on_all_findable']}), {r3[120]['best_rule_all_findable']:.1f} ({r3[120]['best_rule_on_all_findable']}).\n")

    # ---- study 4
    p("## Study 4, rare things that matter (ten households, 32 days, 8 ordinary questions a day plus the rare-mover questions)\n")
    if refused4:
        p("Refused cells: " + "; ".join(refused4) + "\n")
    p("Slices as in `score_rare_movers.py`. For the rules, unseen and seen are each arm's own slices (its looks decide them); the ceilings' unseen and seen are the last-seen cell's, so the n shown is the last-seen cell's.\n")
    arms = ["last_seen_no_model", "most_frequent_no_model", "same_time_of_day_no_model", "alternate_room_no_model"]
    short = {"last_seen_no_model": "last-seen", "most_frequent_no_model": "most frequent", "same_time_of_day_no_model": "same time of day", "alternate_room_no_model": "alternate room"}
    p("| slice | last-seen | most frequent | same time of day | alternate room | best rule | loose ceiling | routine ceiling | headroom, loose | headroom, routine | n questions (last-seen cell) | n households |")
    p("|---|---|---|---|---|---|---|---|---|---|---|---|")
    names = [("first_after_move", "first question after each move"), ("unseen", "unseen"), ("after_a_miss", "after a miss"), ("seen", "seen"),
             ("background", "background"), ("ordinary", "ordinary"), ("pill_box_forward", "pill box, forward (first question)"),
             ("pill_box_return", "pill box, return (first question)"), ("car_keys_first", "car keys (first question)")]
    for s, label in names:
        t = t4[s]
        best = t["best_rule"]
        bp = t[best]["pct"]
        p(f"| {label} | " + " | ".join(f"{f1(t[a]['pct'])} ({t[a]['right']}/{t[a]['n']})" for a in arms) +
          f" | {short[best]} | {f1(t['loose_ceiling']['pct'])} | {f1(t['routine_ceiling']['pct'])} | {f1(t['loose_ceiling']['pct'] - bp)} | {f1(t['routine_ceiling']['pct'] - bp)} | {t['loose_ceiling']['n']} | 10 |")
    p("")
    tf, tu, ts = t4["first_after_move"], t4["unseen"], t4["seen"]
    p(f"Note. On the first question after each of the {tf['loose_ceiling']['n']} moves the best rule ({short[tf['best_rule']]}) is {tf[tf['best_rule']]['pct']:.1f} and the loose ceiling {tf['loose_ceiling']['pct']:.1f}, the routine ceiling {tf['routine_ceiling']['pct']:.1f}; "
      f"on the unseen slice the loose ceiling is {tu['loose_ceiling']['pct']:.1f} against the best rule {tu[tu['best_rule']]['pct']:.1f}, and on the seen slice {ts['loose_ceiling']['pct']:.1f} against {ts[ts['best_rule']]['pct']:.1f}. "
      f"The pill box forward move has a loose ceiling of {t4['pill_box_forward']['loose_ceiling']['pct']:.0f} (the bedside had never been sighted holding it) and the return move {t4['pill_box_return']['loose_ceiling']['pct']:.0f}; the car keys {t4['car_keys_first']['loose_ceiling']['pct']:.0f}. "
      f"The small negative headrooms on 'after a miss' and 'background' come from each rule being scored on its own slice while the ceiling uses the last-seen cell's; they are within one question.\n")

    p("## Files\n")
    for f in ["headroom.py", "HEADROOM.md", "summary.png", "summary.json", "study1.png", "study1.json", "study2.png", "study2.json", "study3.png", "study3.json", "study4.png", "study4.json"]:
        p(f"- coordination/headroom/{f}")
    (HERE / "HEADROOM.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
