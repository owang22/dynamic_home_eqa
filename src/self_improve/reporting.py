"""Paired differences with honest uncertainty.

Two rules, both of which this project has paid for:

**Never pool across households.** Compute each household's number, then combine
the household numbers. A household with 744 questions and one with 644 are not
interchangeable and a pooled share silently weights by bank size.

**Never put a confidence interval on the questions.** A household's sick window
has about twelve distinct asked objects and thirty distinct object-and-place
facts. Two hundred and forty questions about twelve objects are not two hundred
and forty independent observations: the same object asked again at 14:10 and
14:50 is nearly the same observation. A per-question binomial interval is about
four times too narrow. So intervals cluster on the household, and where we can,
on the object within the household.

There is also a floor no interval can go below: generation on this server is not
deterministic, and the same notes rerun on the same data change about 3 to 5% of
their answers. A difference smaller than that is noise whatever its standard
error says.
"""
from __future__ import annotations

import math
import statistics
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

NOISE_FLOOR = 0.05


def _mean(xs: Sequence[float]) -> Optional[float]:
    return statistics.fmean(xs) if xs else None


def share_correct_per_object(answers: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    """One number per asked object: the share of its questions answered right.
    The object is the unit that repeats, so this is the level we average at."""
    per: Dict[str, List[float]] = {}
    for a in answers:
        if a.get("correct") is None:
            continue
        per.setdefault(a["object_id"], []).append(1.0 if a["correct"] else 0.0)
    return {object_id: statistics.fmean(v) for object_id, v in per.items()}


def household_score(answers: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """One household's score, computed two ways so the difference is visible.

    over questions: the plain share of questions answered right.
    over objects:   the average across objects of each object's share. This is
                    the one to report, because it does not let a household's
                    most-asked object dominate.
    """
    scored = [a for a in answers if a.get("correct") is not None]
    per_object = share_correct_per_object(answers)
    return {
        "n_questions_scored": len(scored),
        "n_objects": len(per_object),
        "share_correct_over_questions": _mean([1.0 if a["correct"] else 0.0 for a in scored]),
        "share_correct_over_objects": _mean(list(per_object.values())),
        "per_object": per_object,
    }


def paired_difference(first_by_household: Dict[str, float],
                      second_by_household: Dict[str, float],
                      first_name: str, second_name: str) -> Dict[str, Any]:
    """The difference between two arms, paired within household, with the
    standard error taken across households. The household is the unit."""
    shared = sorted(set(first_by_household) & set(second_by_household))
    differences = [first_by_household[h] - second_by_household[h] for h in shared]
    n = len(differences)
    mean = _mean(differences)
    if n >= 2:
        spread = statistics.stdev(differences)
        standard_error = spread / math.sqrt(n)
    else:
        spread = standard_error = None
    verdict = "not measurable"
    if mean is not None and standard_error is not None:
        if abs(mean) < NOISE_FLOOR:
            verdict = (f"smaller than the {NOISE_FLOOR:.0%} the server's own "
                       f"non-determinism costs us, so noise")
        elif abs(mean) > 2 * standard_error:
            verdict = "larger than twice its standard error"
        else:
            verdict = "within twice its standard error of zero"
    return {
        "first_arm": first_name,
        "second_arm": second_name,
        "clustered_on": "household",
        "n_households": n,
        "households": shared,
        "per_household_difference": dict(zip(shared, differences)),
        "mean_difference": mean,
        "standard_error": standard_error,
        "standard_deviation_across_households": spread,
        "how_many_households_favour_the_first_arm":
            sum(1 for d in differences if d > 0),
        "verdict": verdict,
    }


def paired_difference_over_objects(first_per_object: Dict[str, Dict[str, float]],
                                  second_per_object: Dict[str, Dict[str, float]],
                                  first_name: str, second_name: str) -> Dict[str, Any]:
    """The same difference, but the unit is the object within the household -
    the finer clustering, useful when a household has few movers. Households are
    still kept apart: we average objects within a household first, then across
    households, so a household with eighteen objects does not outvote one with
    eight.
    """
    shared_households = sorted(set(first_per_object) & set(second_per_object))
    by_household: Dict[str, float] = {}
    n_objects = 0
    for household in shared_households:
        first, second = first_per_object[household], second_per_object[household]
        objects = sorted(set(first) & set(second))
        n_objects += len(objects)
        if objects:
            by_household[household] = _mean([first[o] - second[o] for o in objects])
    out = paired_difference(by_household, {h: 0.0 for h in by_household},
                            first_name, second_name)
    out["clustered_on"] = "object within household, then household"
    out["n_objects_total"] = n_objects
    return out


def difference_on_the_questions_a_settled_memory_gets_wrong(
        answers: Sequence[Dict[str, Any]],
        questions_a_settled_memory_gets_wrong: Iterable[str]) -> Dict[str, Any]:
    """The only questions that can separate the arms.

    A memory that simply learned the ordinary fortnight and never updated
    already answers most questions correctly, because most objects never move.
    Those questions carry no signal about the intervention and they dilute
    everything. So we report the restricted score alongside the full one.
    """
    wanted = set(questions_a_settled_memory_gets_wrong)
    restricted = [a for a in answers if a["question_id"] in wanted]
    return {"n_questions_in_the_restricted_set": len(restricted),
            "share_of_all_questions": (len(restricted) / len(answers)) if answers else None,
            **household_score(restricted)}


def effective_sample_note(per_household_objects: Dict[str, int]) -> str:
    total = sum(per_household_objects.values())
    return (f"{total} asked objects across {len(per_household_objects)} households is "
            f"the honest sample size; the question count is several times larger and "
            f"several times too optimistic.")
