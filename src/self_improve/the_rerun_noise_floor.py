"""The noise floor for the exact quantity the paper quotes.

The paper's primary number is the day-23-minus-day-13 difference, not raw accuracy, so
the floor has to be measured on *that* quantity: rerun both freeze points unchanged and
recompute the difference. A floor for accuracy alone would understate the floor for a
difference, which inherits the noise twice over.

**The rerun must use a fresh cache directory.** `LLMClient.complete` keys its file cache
on a hash of the messages, schema, max tokens, temperature and seed, so a genuinely
unchanged rerun issues byte-identical prompts, hits the cache on every call, replays the
original answers and reports a floor of exactly zero - in a fraction of the time, looking
like a clean demonstration that the server is perfectly reproducible. It is not: it
changes 3 to 5% of answers on identical prompts at temperature zero. So this module
refuses to report a floor unless the run it is given actually called the model, and it
prints the cache-hit count so the reader can check.

    python -m self_improve.the_rerun_noise_floor
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Tuple

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.score_at_both_levels import PLACE_LEVEL, ROOM_LEVEL, rescore

BEFORE = "before anything changed"
AFTER = "did it learn the new routine"


def differences_in(results_dir: pathlib.Path, banks: pathlib.Path
                   ) -> Dict[Tuple[str, str, str], float]:
    """(household, arm, level) -> the day-23-minus-day-13 difference, in points."""
    households: Dict[str, FrozenHousehold] = {}
    scores: Dict[Tuple[str, str], Dict[str, Dict[str, Any]]] = collections.defaultdict(dict)
    for answers_file in sorted(results_dir.rglob("held_out_answers.json")):
        payload = json.loads(answers_file.read_text())
        if payload["freeze_point"] not in (BEFORE, AFTER):
            continue
        name = payload["household"]
        if name not in households:
            households[name] = FrozenHousehold(banks / f"{name}.jsonl")
        arm = answers_file.parent.parent.name
        scores[(name, arm)][payload["freeze_point"]] = rescore(
            households[name], payload["answers"])

    out: Dict[Tuple[str, str, str], float] = {}
    for (name, arm), pair in scores.items():
        if BEFORE not in pair or AFTER not in pair:
            continue
        for level in (ROOM_LEVEL, PLACE_LEVEL):
            before, after = pair[BEFORE][level], pair[AFTER][level]
            if before is not None and after is not None:
                out[(name, arm, level)] = 100 * (after - before)
    return out


def how_answers_changed(first: pathlib.Path, second: pathlib.Path) -> Dict[str, Any]:
    """How many individual answers differ between a run and its rerun, broken down.

    Reported with its n, because a zero from 90 observations and a zero from 900 are
    different claims. Broken down by arm, because the two arms' prompts differ in length
    and structure: if one is materially noisier, they do not share a floor and cannot be
    quoted against one. And by freeze point, because the day-23 notes hold more claims, so
    that prompt is longer, and longer prompts are where this server's non-determinism
    appears - which makes the day-23 side of every difference the noisier side, widening
    the variance without biasing the estimate.
    """
    per_cell = []
    by_arm: Dict[str, List[int]] = collections.defaultdict(list)
    by_freeze: Dict[str, List[int]] = collections.defaultdict(list)
    changed = total = 0
    for answers_file in sorted(first.rglob("held_out_answers.json")):
        twin = second / answers_file.relative_to(first)
        if not twin.exists():
            continue
        payload = json.loads(answers_file.read_text())
        a = {x["question_id"]: x.get("answer_place") for x in payload["answers"]}
        b = {x["question_id"]: x.get("answer_place")
             for x in json.loads(twin.read_text())["answers"]}
        shared = [q for q in a if q in b]
        moved = sum(1 for q in shared if a[q] != b[q])
        changed += moved
        total += len(shared)
        arm = ("claim store" if "incremental" in answers_file.parent.parent.name
               else "wholesale rewrite")
        by_arm[arm] += [moved, len(shared)]
        by_freeze[payload["freeze_point"]] += [moved, len(shared)]
        per_cell.append({"household": payload["household"], "arm": arm,
                         "freeze_point": payload["freeze_point"],
                         "n_questions": len(shared), "n_answers_that_changed": moved})

    def rate(pairs: List[int]) -> Dict[str, Any]:
        moved = sum(pairs[0::2])
        n = sum(pairs[1::2])
        return {"n_changed": moved, "n_questions": n,
                "rate": (moved / n) if n else None}

    return {"n_changed": changed, "n_questions": total,
            "rate": (changed / total) if total else None,
            "by_arm": {k: rate(v) for k, v in by_arm.items()},
            "by_freeze_point": {k: rate(v) for k, v in by_freeze.items()},
            "per_cell": per_cell}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/frozen_memory_test_v1"))
    parser.add_argument("--rerun", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/RERUN_for_the_noise_floor"))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/rerun_noise_floor.json"))
    args = parser.parse_args(argv)

    first = differences_in(args.original, args.banks)
    second = differences_in(args.rerun, args.banks)
    shared = sorted(set(first) & set(second))
    if not shared:
        print(f"no household-arm-level cells finished in both {args.original} and {args.rerun} yet")
        return 0

    how = how_answers_changed(args.original, args.rerun)
    changed = how["rate"]
    print(f"individual answers that changed place between run and rerun: "
          f"{how['n_changed']} of {how['n_questions']} = "
          f"{'unknown' if changed is None else format(changed, '.2%')}")
    for label, group in (("by arm", how["by_arm"]), ("by freeze point", how["by_freeze_point"])):
        print(f"   {label}:")
        for key, r in sorted(group.items()):
            print(f"      {key:34s} {r['n_changed']:3d} of {r['n_questions']:4d} = "
                  f"{'n/a' if r['rate'] is None else format(r['rate'], '.2%')}")
    arms = how["by_arm"]
    if len(arms) == 2:
        rates = [r["rate"] for r in arms.values() if r["rate"] is not None]
        if len(rates) == 2 and max(rates) > 2 * max(min(rates), 0.001):
            print("   THE TWO ARMS DO NOT SHARE A FLOOR: one is more than twice as noisy as "
                  "the other, so a single floor must not be quoted for both.")
    if changed is not None and changed == 0:
        print("  THAT IS ZERO, so the rerun was replayed from cache and the floor below "
              "is meaningless. Use a cache directory nothing has written to.")
    print()

    rows = []
    for level in (ROOM_LEVEL, PLACE_LEVEL):
        here = [k for k in shared if k[2] == level]
        if not here:
            continue
        gaps = [second[k] - first[k] for k in here]
        absolute = [abs(g) for g in gaps]
        print(f"=== {level}: the day-23-minus-day-13 difference, original vs rerun")
        for k in here:
            print(f"   {k[0].replace('_t03','')} {k[1].split('_[')[0]:20s} "
                  f"original {first[k]:+6.1f}   rerun {second[k]:+6.1f}   "
                  f"moved {second[k]-first[k]:+6.1f}")
        floor = statistics.fmean(absolute)
        spread = statistics.stdev(gaps) if len(gaps) > 1 else None
        print(f"   FLOOR for this quantity: mean absolute move {floor:.1f} points, "
              f"largest {max(absolute):.1f}, "
              f"spread of the move {'n/a' if spread is None else format(spread, '.1f')}, "
              f"n={len(gaps)} cells")
        rows.append({"level": level, "n_cells": len(gaps),
                     "mean_absolute_move": floor, "largest_move": max(absolute),
                     "spread_of_the_move": spread,
                     "per_cell": {f"{k[0]} / {k[1]}": {"original": first[k], "rerun": second[k]}
                                  for k in here}})
        print()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(
        {"how_answers_changed": how, "by_level": rows}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
