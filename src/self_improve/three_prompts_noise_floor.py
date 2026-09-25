"""The rerun noise floor, measured inside the experiment rather than bought separately.

WHAT THIS IS. `control` and `told_unwell` are given **byte-identical prompts on every
night from day 0 to day 13**: the told-it arm's only difference is one sentence added on
the night of day 14 and one on the night of day 24. Their room-choice prompts and answer
prompts are functions of the notes and the look history, which both start empty and are
built by identical calls. So over days 0 to 13 the two arms are **the same experiment run
twice**, and every difference between them in that window is rerun noise and nothing else.

That makes the floor free, and better than a deliberate rerun would be: it is measured on
the same server, in the same session, under the same concurrency, inside the actual
experiment, on the actual measures.

WHY THERE IS ANY NOISE AT ALL, since the prompts are identical and the cache is keyed on
the prompt. Two cells running in parallel miss the cache at the same moment, each calls the
server, and the server returns different completions at temperature 0. Demonstrated on
2026-09-24 on `hh_s2_t03`: the two arms agreed on every one of the first 24 searches and
then diverged at day 4, question `d4q01`, where the rebuilt answer prompts are
byte-identical, the cache key is the same, and the recorded answers are
`bedroom_floor_b1` and `dining_table_d1`. Same prompt, same key, two answers.

WHAT IT MEANS FOR EVERY OTHER NUMBER HERE. An arm difference smaller than this floor is
not evidence of anything, however clean its standard error looks - the standard error
measures spread across homes, not this. The floor is per measure and per window, never a
single project constant: it is reported for each of the four headline measures separately,
and only over days 0 to 13, because that is the only window in which the two arms were
asked the same thing.

A CONSEQUENCE WORTH STATING PLAINLY. The day-13 freeze point was described as an exact
null "by construction" for the told-it arm. That is wrong, and this module is why: it is
exact in the PROMPTS and not in the trajectories. The day-13 comparison is a noise
measurement, not an identity.

    python -m self_improve.three_prompts_noise_floor
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

from self_improve.three_prompts import PILOT_TEN, cell_dir

SETTLED = tuple(range(0, 14))
PAIR = ("control", "told_unwell")


def measures_over(searches: Sequence[Dict[str, Any]], days: Sequence[int]
                  ) -> Optional[Dict[str, Any]]:
    """The four headline measures over a set of days. Same code as the outcomes report
    uses, so the floor and the effect are in the same units."""
    here = [r for r in searches if r["day"] in days]
    if not here:
        return None
    opened = [r for r in here if r["rooms_opened"]]
    scored = [r for r in here if r["correct_place"] is not None]
    return {
        "n_questions": len(here),
        "share_first_room_was_right": (
            sum(1 for r in opened if r["rooms_opened"][0] == r["true_room"]) / len(opened))
            if opened else None,
        "mean_rooms_opened": statistics.mean(r["n_rooms_opened"] for r in here),
        "share_found_within_budget": sum(1 for r in here if r["found_it"]) / len(here),
        "share_correct_shelf": (sum(1 for r in scored if r["correct_place"]) / len(scored))
            if scored else None,
        "share_correct_room": (sum(1 for r in scored if r["correct_room"]) / len(scored))
            if scored else None,
    }


def first_divergence(a: Sequence[Dict[str, Any]], b: Sequence[Dict[str, Any]]
                     ) -> Optional[Dict[str, Any]]:
    """The first question on which the two runs of the same experiment differ.

    Reported because it says whether the noise starts early or late: a pair that agrees for
    two hundred questions and then diverges is a different problem from one that diverges on
    day 4, and only the second makes the whole settled fortnight a noise measurement.
    """
    by_id_b = {r["question_id"]: r for r in b}
    for row in a:
        other = by_id_b.get(row["question_id"])
        if other is None:
            continue
        if (tuple(row["rooms_opened"]) != tuple(other["rooms_opened"])
                or row["answer_place"] != other["answer_place"]):
            return {"question_id": row["question_id"], "day": row["day"],
                    "object_id": row["object_id"],
                    "rooms_a": row["rooms_opened"], "rooms_b": other["rooms_opened"],
                    "answer_a": row["answer_place"], "answer_b": other["answer_place"],
                    "the_rooms_differ": tuple(row["rooms_opened"]) != tuple(other["rooms_opened"])}
    return None


def load_searches(root: pathlib.Path, arm: str, household: str
                  ) -> Optional[List[Dict[str, Any]]]:
    cell = cell_dir(root, arm, household)
    if (cell / "cell.json").exists():
        return json.loads((cell / "cell.json").read_text())["searches"]
    stream = cell / "searches.jsonl"
    if not stream.exists():
        return None
    out = []
    for line in stream.open():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("kind") == "search":
            out.append(row)
    return out or None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/three_prompts"))
    parser.add_argument("--out", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    rows: List[Dict[str, Any]] = []
    for household in PILOT_TEN:
        a = load_searches(args.root, PAIR[0], household)
        b = load_searches(args.root, PAIR[1], household)
        if not a or not b:
            continue
        # only the days BOTH have reached, so the pair is never compared over
        # different amounts of the month
        days = sorted(set(r["day"] for r in a) & set(r["day"] for r in b)
                      & set(SETTLED))
        if not days:
            continue
        ma, mb = measures_over(a, days), measures_over(b, days)
        if not ma or not mb:
            continue
        shared = {r["question_id"] for r in a} & {r["question_id"] for r in b}
        agreed = sum(1 for r in a if r["question_id"] in shared
                     and r["answer_place"] == next(
                         x["answer_place"] for x in b if x["question_id"] == r["question_id"])
                     and r["day"] in days)
        n_shared = sum(1 for r in a if r["question_id"] in shared and r["day"] in days)
        rows.append({
            "household": household,
            "days_both_reached": [min(days), max(days)],
            "n_questions": ma["n_questions"],
            "share_of_questions_with_the_same_answer": agreed / n_shared if n_shared else None,
            "first_divergence": first_divergence(
                [r for r in a if r["day"] in days], [r for r in b if r["day"] in days]),
            PAIR[0]: ma, PAIR[1]: mb,
        })

    if not rows:
        print("neither arm of the identical pair has enough of the settled fortnight yet")
        return 0

    print(f"\n{'='*94}")
    print("THE RERUN NOISE FLOOR, measured inside the experiment.")
    print(f"`{PAIR[0]}` and `{PAIR[1]}` are given BYTE-IDENTICAL prompts on days 0-13, so")
    print("every difference between them in that window is rerun noise and nothing else.")
    print(f"{'='*94}\n")
    print(f"{'home':12s} {'days':>7s} {'n q':>5s} {'same answer':>12s}  first divergence")
    for row in rows:
        d = row["first_divergence"]
        where = ("none: the two runs agreed on every question" if d is None else
                 f"day {d['day']} {d['object_id']} "
                 f"({'different rooms, ' if d['the_rooms_differ'] else 'same rooms, '}"
                 f"{d['answer_a']} vs {d['answer_b']})")
        print(f"{row['household']:12s} {row['days_both_reached'][0]}-"
              f"{row['days_both_reached'][1]:<4d} {row['n_questions']:5d} "
              f"{row['share_of_questions_with_the_same_answer']:11.1%}  {where}")

    print(f"\n{'measure':34s} {'mean |difference|':>18s} {'largest':>9s} {'n homes':>8s}")
    floor: Dict[str, Any] = {}
    for label, field, pct in (
            ("first room was the right one", "share_first_room_was_right", True),
            ("rooms opened per question", "mean_rooms_opened", False),
            ("found it within the budget", "share_found_within_budget", True),
            ("final answer right, shelf", "share_correct_shelf", True),
            ("final answer right, room", "share_correct_room", True)):
        gaps = [abs(r[PAIR[0]][field] - r[PAIR[1]][field]) for r in rows
                if r[PAIR[0]][field] is not None and r[PAIR[1]][field] is not None]
        if not gaps:
            continue
        mean, worst = statistics.mean(gaps), max(gaps)
        floor[field] = {"mean_absolute_difference": mean, "largest": worst,
                        "n_homes": len(gaps)}
        fmt = (lambda x: f"{100*x:.1f} pts") if pct else (lambda x: f"{x:.3f}")
        print(f"{label:34s} {fmt(mean):>18s} {fmt(worst):>9s} {len(gaps):8d}")

    print("\nHOW TO USE THIS. An arm difference smaller than the floor for the SAME measure")
    print("is not evidence, however tight its standard error: the standard error measures")
    print("spread across homes, not this. The floor is per measure and per window and is")
    print("never a single project constant.")
    print("\nAnd note what it costs the design: the two arms were meant to be the same run")
    print("until day 14, so the day-13 comparison is a NOISE MEASUREMENT and not the exact")
    print("null 'by construction' it was described as. It is exact in the prompts only.")

    out = args.out or (args.root / "the_rerun_noise_floor.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "what_it_is": ("control and told_unwell have byte-identical prompts on days 0-13, "
                       "so their difference over that window is rerun noise"),
        "why_any_noise_exists": ("two cells miss the prompt cache at the same moment, each "
                                 "calls the server, and vLLM returns different completions "
                                 "at temperature 0"),
        "window": [min(SETTLED), max(SETTLED)],
        "floor_per_measure": floor, "per_home": rows}, indent=1))
    print(f"\nwritten to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
