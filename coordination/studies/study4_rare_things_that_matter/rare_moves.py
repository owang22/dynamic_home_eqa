#!/usr/bin/env python3
"""Study 4, rare things that matter: count moves of asked-about objects in the
banks and score the existing method cells on the questions asked within 24
hours after a move.  CPU only; reads banks and searches.jsonl; writes
RESULTS_count.md beside this file.

Definitions (coordination/studies/study4_rare_things_that_matter/SETUP.md):
  * place of an object at time t = receptacle_id of the latest truth row with
    row.t <= t (same rule as frozen_household.FrozenHousehold.place_of_object);
  * a move = a truth row whose receptacle_id differs from the previous row's
    (a row repeating the current place is not a move);
  * room of a place = header.receptacle_rooms[place]; ON_PERSON and
    OUT_OF_HOUSE map to "beyond reach"; a room-level move is a move whose
    from-room and to-room differ;
  * rare mover = asked-about object with at most RARE_MAX moves in the bank;
  * a question is "within 24 h after a move" of object o if it asks about o
    and some move of o happened at t_m with t_m < t_q <= t_m + 86400;
  * first guess right = search row with kind == "search" and
    found_at_step == 1.
Everything is computed at both the place (receptacle) level and the room
level, because the score is room-level while SETUP speaks of place changes.
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import statistics
import sys

REPO = pathlib.Path("/home/oliver/robot/dynamic_home_eqa")
HERE = REPO / "coordination/studies/study4_rare_things_that_matter"
DAY = 86_400
RARE_MAX = 3
BEYOND = "beyond reach"
NOT_A_REAL_ROOM = "person_check"
LAST_SEEN = "last_seen_no_model"
MOST_FREQUENT = "most_frequent_offline"

WAVES = {
    "overnight_wave (ten homes, 31 days, 8 questions a day)": dict(
        cells=REPO / "results/self_improve/overnight_wave/cells",
        banks=REPO / "results/self_improve/varied_homes/ten_homes/banks",
    ),
    "wave_the_second_illness (three homes, 50 days, 24 questions a day)": dict(
        cells=REPO / "results/self_improve/wave_the_second_illness/cells",
        banks=REPO / "results/self_improve/varied_homes/all_generated_v2_twice/banks",
    ),
}


# ----------------------------------------------------------------- banks --
class Bank:
    def __init__(self, path: pathlib.Path):
        self.name = path.stem
        hist = collections.defaultdict(list)
        self.questions = []
        header = None
        for line in path.open():
            row = json.loads(line)
            k = row["kind"]
            if k == "episode_header":
                header = row
            elif k == "truth":
                hist[row["object_id"]].append((row["t"], row["receptacle_id"]))
            elif k == "question":
                self.questions.append(row)
        assert header is not None, path
        self.header = header
        self.n_days = int(header["n_days"])
        self.place_room = dict(header["receptacle_rooms"])
        for h in hist.values():
            h.sort()
        self.hist = hist
        self.asked = sorted({q["object_id"] for q in self.questions})

    def room_of(self, place):
        if place in ("ON_PERSON", "OUT_OF_HOUSE"):
            return BEYOND
        r = self.place_room.get(place)
        if r is None or r == NOT_A_REAL_ROOM:
            return BEYOND
        return r

    def place_at(self, obj, t):
        h = self.hist.get(obj)
        if not h:
            return None
        import bisect
        i = bisect.bisect_right(h, (t, "￿")) - 1
        return h[i][1] if i >= 0 else None

    def moves(self, obj, level):
        """List of (t, from, to) at the given level ('place' or 'room')."""
        out = []
        prev = None
        for t, p in self.hist.get(obj, []):
            v = p if level == "place" else self.room_of(p)
            if prev is not None and v != prev:
                out.append((t, prev, v))
            prev = v
        return out


def same_day_change_back_pairs(moves):
    """Consecutive moves A->B then B->A on the same calendar day."""
    n = 0
    for (t1, a1, b1), (t2, a2, b2) in zip(moves, moves[1:]):
        if a1 == b2 and b1 == a2 and t1 // DAY == t2 // DAY:
            n += 1
    return n


def within_day_after(moves, t_q):
    return any(tm < t_q <= tm + DAY for tm, _, _ in moves)


# ----------------------------------------------------------------- cells --
def load_searches(path):
    rows = []
    for line in path.open():
        r = json.loads(line)
        if r.get("kind") == "search":
            rows.append(r)
    return rows


def first_guess_right(row):
    return row.get("found_at_step") == 1


def most_frequent_guess(bank, asked_rows_for_obj, t_q):
    """Offline estimate: the room the object was most often in at the times of
    the earlier asked questions about it (strictly before t_q); ties broken by
    the room seen most recently.  None if no earlier question."""
    counts = collections.Counter()
    latest = {}
    for r in asked_rows_for_obj:
        if r["time"] < t_q:
            room = bank.room_of(bank.place_at(r["object_id"], r["time"]))
            counts[room] += 1
            latest[room] = max(latest.get(room, -1), r["time"])
    if not counts:
        return None
    return max(counts, key=lambda rm: (counts[rm], latest[rm]))


# ------------------------------------------------------------------ stats --
def mean_se(xs):
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = statistics.fmean(xs)
    if n < 2:
        return m, float("nan")
    return m, statistics.stdev(xs) / math.sqrt(n)


def pct(k, n):
    return f"{100.0 * k / n:.1f}" if n else "–"


def fmt(x):
    return "–" if (x is None or (isinstance(x, float) and math.isnan(x))) else f"{x:+.1f}"


# ------------------------------------------------------------------- main --
def run_wave(title, cells_dir, banks_dir, out, summary):
    out.append(f"\n# {title}\n")
    out.append(f"cells: `{cells_dir.relative_to(REPO)}`; banks: `{banks_dir.relative_to(REPO)}`\n")
    methods = sorted(p.name for p in cells_dir.iterdir() if p.is_dir())
    assert LAST_SEEN in methods, methods
    households = sorted(p.name for p in (cells_dir / LAST_SEEN).iterdir() if p.is_dir())
    banks = {h: Bank(banks_dir / f"{h}.jsonl") for h in households}

    # the question set per household, from last_seen's searches.jsonl
    asked = {h: load_searches(cells_dir / LAST_SEEN / h / "searches.jsonl") for h in households}
    # check every other cell asks the same question ids
    mismatches = []
    scores = collections.defaultdict(dict)  # scores[method][h] = {qid: bool}
    for m in methods:
        for h in households:
            p = cells_dir / m / h / "searches.jsonl"
            if not p.exists():
                continue
            rows = load_searches(p)
            ids = {r["question_id"] for r in rows}
            ref = {r["question_id"] for r in asked[h]}
            if ids != ref:
                mismatches.append((m, h, len(ids - ref), len(ref - ids)))
            scores[m][h] = {r["question_id"]: first_guess_right(r) for r in rows}
    # most-frequent offline
    for h in households:
        b = banks[h]
        by_obj = collections.defaultdict(list)
        for r in asked[h]:
            by_obj[r["object_id"]].append(r)
        sc = {}
        for r in asked[h]:
            g = most_frequent_guess(b, by_obj[r["object_id"]], r["time"])
            sc[r["question_id"]] = (g is not None and g == r["true_room"])
        scores[MOST_FREQUENT][h] = sc
    methods_all = methods + [MOST_FREQUENT]

    notes = []
    if mismatches:
        notes.append("question-id sets differ from last_seen in: " + ", ".join(
            f"{m}/{h} (+{a}/-{b})" for m, h, a, b in mismatches))
    # sanity: cell's true_room agrees with the bank
    disagree = 0
    for h in households:
        for r in asked[h]:
            if banks[h].room_of(banks[h].place_at(r["object_id"], r["time"])) != r["true_room"]:
                disagree += 1
    notes.append(f"true_room in last_seen's searches.jsonl agrees with the bank on all but {disagree} rows.")

    # ------------------------------------------------ 1. moves per object --
    for level in ("place", "room"):
        out.append(f"\n## 1 ({level} level). Moves per asked-about object\n")
        out.append(f"A move is a change of {level}; rare mover = at most {RARE_MAX} moves. "
                   "`nq` = questions the cells asked about the object. "
                   "`pairs` = change-and-change-back within one calendar day (counted as two moves).\n")
        hist_all = collections.Counter()
        odd = collections.defaultdict(list)
        rare_detail = []
        for h in households:
            b = banks[h]
            out.append(f"\n### {h}  (n_days {b.n_days}, {len(asked[h])} questions asked, "
                       f"{len(b.questions)} in the bank)\n")
            out.append("| object | moves | pairs | to/from beyond reach | days with a move | nq asked | nq in bank | rare? |")
            out.append("|---|---:|---:|---:|---:|---:|---:|---|")
            nq = collections.Counter(r["object_id"] for r in asked[h])
            nq_bank = collections.Counter(q["object_id"] for q in b.questions)
            rare = []
            counts = []
            for o in b.asked:
                mv = b.moves(o, level)
                beyond = sum(1 for _, a, c in mv if BEYOND in (b.room_of(a) if level == "place" else a,
                                                              b.room_of(c) if level == "place" else c))
                days_moving = len({t // DAY for t, _, _ in mv})
                is_rare = len(mv) <= RARE_MAX
                if is_rare:
                    rare.append(o)
                    if mv:
                        q_asked = [r for r in asked[h] if r["object_id"] == o and within_day_after(mv, r["time"])]
                        q_bank = [q for q in b.questions if q["object_id"] == o and within_day_after(mv, q["t_query"])]
                        rare_detail.append((h, o, [(t // DAY, f"{a}->{c}") for t, a, c in mv],
                                            len(q_asked), len(q_bank)))
                counts.append(len(mv))
                if len(mv) == 0:
                    odd["never move"].append(f"{h}/{o} ({nq[o]} asked)")
                if days_moving >= b.n_days - 1:
                    odd["move on every day or all but one"].append(f"{h}/{o} ({len(mv)} moves)")
                if nq[o] == 0:
                    odd["in the bank's questions but never asked by the cells"].append(f"{h}/{o} ({nq_bank[o]} in bank)")
                out.append(f"| {o} | {len(mv)} | {same_day_change_back_pairs(mv)} | {beyond} | {days_moving} | {nq[o]} | {nq_bank[o]} | {'yes' if is_rare else ''} |")
            hist = collections.Counter(bin_moves(c) for c in counts)
            hist_all.update(hist)
            out.append("\nhistogram of moves per object: " + ", ".join(
                f"{k}: {hist[k]}" for k in BINS if hist[k]))
            out.append(f"\nrare movers ({len(rare)} of {len(b.asked)}): {', '.join(rare) if rare else 'none'}")
        out.append(f"\n### rare movers that move at all ({level} level): when, and the questions that follow\n")
        if rare_detail:
            out.append("| household | object | moves (day: from->to) | asked questions within 24 h | bank questions within 24 h |")
            out.append("|---|---|---|---:|---:|")
            for h, o, mv, qa, qb in rare_detail:
                out.append(f"| {h} | {o} | {'; '.join(f'd{d}: {s}' for d, s in mv)} | {qa} | {qb} |")
        else:
            out.append("none: every rare mover has zero moves.")
        out.append(f"\n### odd things ({level} level)\n")
        for k, v in odd.items():
            out.append(f"- {k} ({len(v)}): {', '.join(v)}")
        out.append(f"\n### all households, histogram of moves per object ({level} level)\n")
        out.append("| moves | objects |")
        out.append("|---|---:|")
        for k in BINS:
            out.append(f"| {k} | {hist_all[k]} |")

        # ------------------------------------------- 2. questions in slices --
        slices = {}  # slices[h][qid] = 'rare' | 'move' | 'other'
        out.append(f"\n## 2 ({level} level). Questions within 24 h after a move\n")
        out.append("| household | questions | rare-move questions | rare movers asked about | rare-move questions in the full bank | all-move questions | other (no move of the object in the prior 24 h) | about never-moving objects |")
        out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        tot = collections.Counter()
        by_threshold = collections.Counter()
        for h in households:
            b = banks[h]
            mv = {o: b.moves(o, level) for o in b.asked}
            rare_set = {o for o in b.asked if len(mv[o]) <= RARE_MAX}
            never = {o for o in b.asked if len(mv[o]) == 0}
            n_rare_bank = sum(1 for q in b.questions
                              if q["object_id"] in rare_set and within_day_after(mv[q["object_id"]], q["t_query"]))
            for thr in THRESHOLDS:
                by_threshold[thr] += sum(1 for r in asked[h]
                                         if len(mv.get(r["object_id"], [])) <= thr
                                         and within_day_after(mv.get(r["object_id"], []), r["time"]))
            sl = {}
            n_rare = n_move = n_other = n_never = 0
            rare_objs_asked = set()
            for r in asked[h]:
                o = r["object_id"]
                if o not in mv:
                    sl[r["question_id"]] = "no truth"
                    continue
                if within_day_after(mv[o], r["time"]):
                    if o in rare_set:
                        sl[r["question_id"]] = "rare"
                        n_rare += 1
                        rare_objs_asked.add(o)
                    else:
                        sl[r["question_id"]] = "move"
                    n_move += 1
                else:
                    sl[r["question_id"]] = "other"
                    n_other += 1
                if o in never:
                    n_never += 1
            slices[h] = sl
            tot.update(dict(q=len(asked[h]), rare=n_rare, move=n_move, other=n_other, never=n_never,
                            rare_bank=n_rare_bank))
            out.append(f"| {h} | {len(asked[h])} | {n_rare} | {len(rare_objs_asked)} | {n_rare_bank} | {n_move} | {n_other} | {n_never} |")
        out.append(f"| **total** | {tot['q']} | {tot['rare']} | | {tot['rare_bank']} | {tot['move']} | {tot['other']} | {tot['never']} |")
        n_obj = sum(len(banks[h].asked) for h in households)
        summary.append(f"| {title.split(' (')[0]} | {level} | {len(households)} | {n_obj} | {hist_all['0']} | "
                       f"{sum(hist_all[k] for k in ('1', '2', '3'))} | {tot['q']} | {tot['rare']} | {tot['rare_bank']} | "
                       f"{tot['move']} | {tot['other']} |")
        out.append("\nThe rare-move questions are a subset of the all-move questions. "
                   "A question is in exactly one of: all-move, other. 'In the full bank' counts all the bank's "
                   "questions (24 a day), not only those the cells asked.")
        out.append(f"\nHow the asked-question count in the rare slice depends on the rare threshold ({level} level, all households):\n")
        out.append("| at most this many moves | asked questions within 24 h after a move of such an object |")
        out.append("|---:|---:|")
        for thr in THRESHOLDS:
            out.append(f"| {thr} | {by_threshold[thr]} |")

        # ---------------------------------------------- 3. first guess right --
        slice_defs = [("rare", "(a) rare-move questions", lambda s: s == "rare"),
                      ("move", "(b) all-move questions", lambda s: s in ("rare", "move")),
                      ("other", "(c) all other questions", lambda s: s == "other")]
        out.append(f"\n## 3 ({level} level). First guess right (found_at_step == 1), per cent\n")
        out.append(f"`{MOST_FREQUENT}` is an offline estimate computed here from the bank: for each question, "
                   "the room the object was truly in most often at the times of the earlier asked questions "
                   "about it (ties by most recent); no guess before the first question about an object. "
                   "It uses true rooms, which no robot had; the cells used what they saw.\n")
        per_slice_acc = {}  # per_slice_acc[slice][method][h] = (k, n)
        for key, label, pred in slice_defs:
            out.append(f"\n### {label}\n")
            out.append("| method | " + " | ".join(households) + " | pooled | pooled n |")
            out.append("|---|" + "---:|" * (len(households) + 2))
            acc = {}
            for m in methods_all:
                row = []
                K = N = 0
                acc[m] = {}
                for h in households:
                    sc = scores[m].get(h)
                    if sc is None:
                        row.append("–")
                        continue
                    ids = [q for q, s in slices[h].items() if pred(s)]
                    k = sum(1 for q in ids if sc.get(q))
                    n = len(ids)
                    acc[m][h] = (k, n)
                    K += k
                    N += n
                    row.append(pct(k, n))
                out.append(f"| {m} | " + " | ".join(row) + f" | {pct(K, N)} | {N} |")
            per_slice_acc[key] = acc
            # paired differences against last seen
            out.append(f"\nPaired per-household difference against `{LAST_SEEN}` (points; households with "
                       "the method present and a non-empty slice):\n")
            out.append("| method | n households | mean | SE | 2 SE | per household |")
            out.append("|---|---:|---:|---:|---:|---|")
            for m in methods_all:
                if m == LAST_SEEN:
                    continue
                diffs = []
                per = []
                for h in households:
                    if h not in acc[m] or h not in acc[LAST_SEEN]:
                        continue
                    k, n = acc[m][h]
                    k0, n0 = acc[LAST_SEEN][h]
                    if n == 0 or n0 == 0:
                        continue
                    d = 100.0 * (k / n - k0 / n0)
                    diffs.append(d)
                    per.append(f"{h.split('_')[1]}:{d:+.0f}")
                mu, se = mean_se(diffs)
                out.append(f"| {m} | {len(diffs)} | {fmt(mu)} | {fmt(se).lstrip('+')} | {fmt(2 * se).lstrip('+') if not math.isnan(se) else '–'} | {' '.join(per)} |")
        # ------------------------------------------------- 4. detectable gap --
        out.append(f"\n## 4 ({level} level). Rare-move questions per household and the detectable gap\n")
        out.append("| household | rare-move questions |")
        out.append("|---|---:|")
        for h in households:
            out.append(f"| {h} | {per_slice_acc['rare'][LAST_SEEN].get(h, (0, 0))[1]} |")
        # best method(s) on the rare slice by pooled accuracy, excluding last seen; ties all listed
        pooled = {}
        for m in methods_all:
            if m == LAST_SEEN:
                continue
            K = sum(k for k, n in per_slice_acc["rare"][m].values())
            N = sum(n for k, n in per_slice_acc["rare"][m].values())
            if N:
                pooled[m] = K / N
        if pooled:
            top = max(pooled.values())
            for m in [m for m, v in pooled.items() if v == top]:
                diffs = []
                for h in households:
                    if h in per_slice_acc["rare"][m] and h in per_slice_acc["rare"][LAST_SEEN]:
                        k, n = per_slice_acc["rare"][m][h]
                        k0, n0 = per_slice_acc["rare"][LAST_SEEN][h]
                        if n and n0:
                            diffs.append(100.0 * (k / n - k0 / n0))
                mu, se = mean_se(diffs)
                out.append(f"\nBest method on the rare-move slice by pooled first guess right (ties all listed): `{m}` "
                           f"({100 * top:.1f}%). Paired against `{LAST_SEEN}` over {len(diffs)} households with a "
                           f"non-empty slice: mean {fmt(mu)}, SE {fmt(se).lstrip('+')}, "
                           f"2 SE {fmt(2 * se).lstrip('+') if not math.isnan(se) else '–'}. "
                           "(The paired table under 3(a) has every method.)")
        else:
            out.append("\nNo rare-move questions in any household; no gap is detectable on this slice.")
    out.append("\n## Notes on this wave\n")
    for n in notes:
        out.append(f"- {n}")


BINS = ["0", "1", "2", "3", "4-10", "11-30", "31-100", "101-300", ">300"]
THRESHOLDS = [3, 5, 10, 20, 30]


def bin_moves(c):
    if c <= 3:
        return str(c)
    if c <= 10:
        return "4-10"
    if c <= 30:
        return "11-30"
    if c <= 100:
        return "31-100"
    if c <= 300:
        return "101-300"
    return ">300"


def main():
    out = ["# Study 4, rare things that matter: the count",
           "",
           "Produced by `rare_moves.py` in this directory. Definitions are in the script's docstring "
           "and in SETUP.md. Two levels are reported throughout: **place** (receptacle id, as SETUP says "
           "'place changes') and **room** (what first-guess-right is scored at; a move between two spots in "
           "the same room is not a room-level move). Moves to or from ON_PERSON / OUT_OF_HOUSE count as "
           "moves at both levels (room = 'beyond reach')."]
    summary = []
    body = []
    for title, cfg in WAVES.items():
        run_wave(title, cfg["cells"], cfg["banks"], body, summary)
    out += ["", "## Summary", "",
            "| wave | level | households | asked-about objects | objects with 0 moves | objects with 1-3 moves | "
            "questions asked | rare-move questions | rare-move questions in the full bank | all-move questions | other questions |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"] + summary
    out += ["",
            "The rare-move slice (questions asked within 24 h after a move of an object with at most 3 moves) holds "
            "1 question at place level and 6 at room level in the ten-home run, and 0 / 1 in the 50-day run, so no "
            "difference between methods is measurable on it: the paired 2 SE against last-seen is undefined where "
            "only one household has a question in the slice, and 40 to 63 points where five do (ten-home run, room "
            "level; section 3(a) of each wave). The full bank (24 questions a day) holds 18 such questions at most. "
            "Nearly every rare mover never moves at all (towels at place level; towels, razors, books and some "
            "glasses, mugs and notebooks at room level). Of the eight room-level rare movers in the ten-home run "
            "that do move, six move exactly twice, out on day 12-14 and back on day 24-31 (the bank's sick block is "
            "days 14-23); the other two, and both in the 50-day run, change room and change back within one day. "
            "Every question falls in exactly one of the all-move / other slices; none is unclassified. "
            "The 'pairs' column counts consecutive move pairs A->B, B->A on one calendar day, so a run "
            "A->B->A->B on one day counts two pairs."]
    out += body
    text = "\n".join(out) + "\n"
    (HERE / "RESULTS_count.md").write_text(text)
    sys.stdout.write(text)


if __name__ == "__main__":
    main()
