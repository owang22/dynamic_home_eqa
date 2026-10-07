#!/usr/bin/env python3
"""Score the arms on the rare-mover banks, every arm in one table, with the bars the memory
methods must beat.

MAIN SCORE (arm-independent unit): first guess right (found_at_step == 1) on the FIRST question
after each place change (`rare_move_rank == 1` in the bank), one row per move. Paired per
household against last-seen; SE over households.

Secondary, per question (each arm's own, since they depend on its looks, from looks.jsonl):
  unseen        rare-move questions asked before this arm had sighted the object at its new place
  after a miss  the unseen questions that are not the first after the move, i.e. an earlier
                search since the move already failed to find it
  seen          rare-move questions asked after such a sighting
  background    the random-time rare-mover questions when nothing moved in the last 24 h
  ordinary      the ordinary questions, with the same-id comparison against the ten-home
                last-seen cell at the same load
Pill box: forward (to the bedside) and return moves separately, counts of first-after-move right.

A cell is scored only if it carries its completion marker: cell.json with per_day rows for every
day up to last_day. Anything else is refused by name.

    python3 coordination/studies/study4_rare_things_that_matter/score_rare_movers.py --load 8 [--arms a b ...] [--json out]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
LOADS = {
    24: {"banks": REPO / "results/self_improve/varied_homes/rare_movers/banks",
         "wave": REPO / "results/self_improve/wave_rare_movers",
         "reference": REPO / "results/self_improve/overnight_wave_24_questions/cells/last_seen_no_model"},
    8: {"banks": REPO / "results/self_improve/varied_homes/rare_movers/banks_8_a_day",
        "wave": REPO / "results/self_improve/wave_rare_movers_8_a_day",
        "reference": REPO / "results/self_improve/overnight_wave/cells/last_seen_no_model"},
}
BASELINE = "last_seen_no_model"
SLICES = ("first_after_move", "unseen", "after_a_miss", "seen", "background", "ordinary")


def searches(cell: pathlib.Path):
    rows = {}
    with (cell / "searches.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("kind") == "search":
                rows[r["question_id"]] = r
    return rows


def sightings(cell: pathlib.Path):
    out = {}
    with (cell / "looks.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("kind") != "look":
                continue
            for s_ in r["sightings"]:
                out.setdefault((s_["object_id"], s_["place_id"]), []).append(s_["time"])
    return out


def complete(cell: pathlib.Path):
    """The completion marker: cell.json with a per_day row for every day to last_day."""
    f = cell / "cell.json"
    if not f.exists():
        return False, "no cell.json"
    c = json.loads(f.read_text())
    want = int(c.get("last_day", 31)) + 1
    if len(c.get("per_day", [])) != want:
        return False, f"per_day has {len(c.get('per_day', []))} rows, wanted {want}"
    if (cell / "CRASHED.txt").exists() or (cell / "RUNNING.lock").exists():
        return False, "CRASHED.txt or RUNNING.lock present"
    return True, ""


def fr(rows):
    return sum(1 for r in rows if r.get("found_at_step") == 1)


def pct(num, den):
    return 100 * num / den if den else float("nan")


def score_cell(cell, bank_q, ref_rows):
    rows = searches(cell)
    seen_at = sightings(cell)
    rare, bg, ordinary = [], [], []
    for qid, r in rows.items():
        q = bank_q[qid]
        if q.get("within_24h_of_rare_move"):
            t_move = q["rare_move_t"]
            times = seen_at.get((r["object_id"], r["true_place"]), [])
            r["asked_before_any_sighting_at_new_place"] = not any(t_move < t < r["time"] for t in times)
            r["rank"] = q.get("rare_move_rank")
            rare.append(r)
        elif q.get("rare_mover"):
            bg.append(r)
        else:
            ordinary.append(r)
    first = [r for r in rare if r["rank"] == 1]
    unseen = [r for r in rare if r["asked_before_any_sighting_at_new_place"]]
    miss = [r for r in unseen if r["rank"] != 1]
    seen = [r for r in rare if not r["asked_before_any_sighting_at_new_place"]]
    common = [qid for qid in ordinary_ids(rows, bank_q) if qid in ref_rows]
    # the bank's cause words: "... is unwell and starts the day in bed" (forward), "... is well again ..." (return)
    pb_fwd = [r for r in first if r["object_class"] == "pill_box" and "unwell" in bank_q[r["question_id"]]["rare_move_cause"]]
    pb_ret = [r for r in first if r["object_class"] == "pill_box" and "well again" in bank_q[r["question_id"]]["rare_move_cause"]]
    return {
        "n": {"first_after_move": len(first), "unseen": len(unseen), "after_a_miss": len(miss), "seen": len(seen),
              "background": len(bg), "ordinary": len(ordinary)},
        "right": {"first_after_move": fr(first), "unseen": fr(unseen), "after_a_miss": fr(miss), "seen": fr(seen),
                  "background": fr(bg), "ordinary": fr(ordinary)},
        "first_after_move_unseen": sum(1 for r in first if r["asked_before_any_sighting_at_new_place"]),
        "pill_box_forward": [fr(pb_fwd), len(pb_fwd)], "pill_box_return": [fr(pb_ret), len(pb_ret)],
        "car_keys_first": [fr([r for r in first if r["object_class"] == "car_keys"]),
                           sum(1 for r in first if r["object_class"] == "car_keys")],
        "common_n": len(common),
        "common_right_here": sum(1 for qid in common if rows[qid].get("found_at_step") == 1),
        "common_right_ten_home": sum(1 for qid in common if ref_rows[qid].get("found_at_step") == 1),
        "room_visits_a_day": sum(r["n_rooms_opened"] for r in rows.values()) / 32,
        "per_question": [{"question_id": r["question_id"], "object_id": r["object_id"], "day": r["day"], "time": r["time"],
                          "rare_move_rank": r["rank"], "asked_before_any_sighting_at_new_place": r["asked_before_any_sighting_at_new_place"],
                          "after_a_miss": r["asked_before_any_sighting_at_new_place"] and r["rank"] != 1,
                          "first_guess_right": r.get("found_at_step") == 1, "rooms_opened": r["rooms_opened"], "true_room": r["true_room"]}
                         for r in sorted(rare, key=lambda r: r["time"])],
    }


def ordinary_ids(rows, bank_q):
    return [qid for qid in rows if not bank_q[qid].get("rare_mover")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", type=int, choices=(24, 8), default=8)
    ap.add_argument("--arms", nargs="*", default=None, help="arm directories under cells/ (default: all present)")
    ap.add_argument("--json", type=pathlib.Path, default=None)
    a = ap.parse_args(argv)
    banks, wave, reference = (LOADS[a.load][k] for k in ("banks", "wave", "reference"))
    cells = wave / "cells"
    arms = a.arms or sorted(p.name for p in cells.iterdir() if p.is_dir())
    if BASELINE in arms:
        arms = [BASELINE] + [x for x in arms if x != BASELINE]
    homes = sorted((p.stem for p in banks.glob("hh_s*_t03.jsonl")), key=lambda n: int(n.split("_")[1][1:]))
    bank_qs = {}
    for home in homes:
        rows = [json.loads(l) for l in (banks / f"{home}.jsonl").open() if '"kind": "question"' in l]
        bank_qs[home] = {r["question_id"]: r for r in rows if r["kind"] == "question"}
    refs = {home: (searches(reference / home) if (reference / home / "searches.jsonl").exists() else {}) for home in homes}

    results = {}          # arm -> home -> record
    for arm in arms:
        results[arm] = {}
        for home in homes:
            cell = cells / arm / home
            ok, why = complete(cell) if cell.exists() else (False, "no such cell")
            if not ok:
                print(f"REFUSED {arm}/{home}: {why}")
                continue
            rec = score_cell(cell, bank_qs[home], refs[home])
            results[arm][home] = rec
            with (cell / "rare_move_questions_scored.jsonl").open("w") as fh:
                for r in rec["per_question"]:
                    fh.write(json.dumps(r) + "\n")
    print(f"\nload {a.load} ordinary a day; first guess right = found_at_step == 1; pooled over the homes each arm completed\n")
    head = f"{'arm':28s}" + "".join(f"{s:>17s}" for s in SLICES) + f"{'ten-home same ids':>18s}{'homes':>6s}"
    print(head)
    print("-" * len(head))
    pooled = {}
    for arm, by_home in results.items():
        if not by_home:
            continue
        pooled[arm] = {}
        line = f"{arm:28s}"
        for s in SLICES:
            n = sum(r["n"][s] for r in by_home.values()); k = sum(r["right"][s] for r in by_home.values())
            pooled[arm][s] = (k, n)
            line += f"{pct(k, n):8.1f} (n={n:4d})"
        cn = sum(r["common_n"] for r in by_home.values())
        line += f"{pct(sum(r['common_right_ten_home'] for r in by_home.values()), cn):9.1f}/{pct(sum(r['common_right_here'] for r in by_home.values()), cn):5.1f}  "
        line += f"{len(by_home):>5d}"
        print(line)
    print("\n(ten-home same ids = the ten-home last-seen cell at this load / this arm, on the ordinary ids both asked)")

    # the main unit, paired per household against last-seen
    if BASELINE in results and results[BASELINE]:
        print(f"\nMAIN SCORE: first question after each place change, paired per household against {BASELINE}")
        print(f"{'arm':28s}{'homes':>6s}{'mean diff':>10s}{'SE':>6s}{'2 SE':>6s}   per-home % (arm) ...")
        base = results[BASELINE]
        for arm, by_home in results.items():
            if arm == BASELINE or not by_home:
                continue
            d = [pct(by_home[h]["right"]["first_after_move"], by_home[h]["n"]["first_after_move"])
                 - pct(base[h]["right"]["first_after_move"], base[h]["n"]["first_after_move"])
                 for h in homes if h in by_home and h in base]
            if len(d) < 2:
                continue
            se = statistics.stdev(d) / len(d) ** 0.5
            print(f"{arm:28s}{len(d):>6d}{statistics.mean(d):+10.1f}{se:6.1f}{2 * se:6.1f}   "
                  + " ".join(f"{pct(by_home[h]['right']['first_after_move'], by_home[h]['n']['first_after_move']):4.0f}" for h in homes if h in by_home))
        print(f"{'(last-seen itself)':28s}{'':6s}{'':10s}{'':6s}{'':6s}   "
              + " ".join(f"{pct(base[h]['right']['first_after_move'], base[h]['n']['first_after_move']):4.0f}" for h in homes if h in base))
        fu = sum(r["first_after_move_unseen"] for r in base.values()); ft = sum(r["n"]["first_after_move"] for r in base.values())
        print(f"first-after-move questions that are unseen for last-seen: {fu} of {ft}")

    print("\nPILL BOX, first question after the move, right / moves:")
    for arm, by_home in results.items():
        if by_home:
            f_ = [sum(r["pill_box_forward"][i] for r in by_home.values()) for i in (0, 1)]
            r_ = [sum(r["pill_box_return"][i] for r in by_home.values()) for i in (0, 1)]
            k_ = [sum(r["car_keys_first"][i] for r in by_home.values()) for i in (0, 1)]
            print(f"  {arm:28s} forward (to the bedside) {f_[0]}/{f_[1]}   return {r_[0]}/{r_[1]}   (car keys {k_[0]}/{k_[1]})")

    print("\nTHE BARS: best rule on each slice, and best + 10 points")
    for s in SLICES:
        best = max(((arm, pct(*pooled[arm][s])) for arm in pooled), key=lambda x: x[1])
        print(f"  {s:17s} best {best[0]:28s} {best[1]:5.1f}   bar to clear {min(100.0, best[1] + 10):5.1f}")
    if a.json:
        slim = {arm: {h: {k: v for k, v in rec.items() if k != "per_question"} for h, rec in by_home.items()}
                for arm, by_home in results.items()}
        a.json.write_text(json.dumps(slim, indent=1))
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
