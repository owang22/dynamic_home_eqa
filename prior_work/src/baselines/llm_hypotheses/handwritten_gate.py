"""The converter's real-bank gate: hand-written hypotheses on hh_001.

Before any LLM is involved, the converter must show that a hypothesis
matching the household's TRUE profile (written by hand from the bank's
truth stream and placements — privileged access, fine for a machinery
gate) outgains a plausible-but-wrong one within a reasonable number of
days of real sightings. If it does not, no prompt will fix it, and the
build stops here.

Usage:
  python -m baselines.llm_hypotheses.handwritten_gate            # hh_001
  python -m baselines.llm_hypotheses.handwritten_gate --days 14

Prints the mixture weights day by day and a PASS/FAIL verdict. PASS
needs all three of:

* the true hypothesis's CUMULATIVE event log likelihood (presence plus
  weighted absence, the quantity the weights integrate) beats the wrong
  one's over the episode;
* its weight is at least twice the wrong one's on 75% of days from day
  7 on — not every day, because a plausible-but-wrong hypothesis is
  right about some evenings and a tempered mixture honestly leans its
  way for a day when it is;
* it leads on the final day.
"""

from __future__ import annotations

import argparse
import json
import random
import tempfile
import pathlib

from baselines.bank import JsonlBank
from baselines.beliefs.llm_hypothesis_mixture import LLMHypothesisMixture
from baselines.household_analysis import bank_path
from baselines.types import DAY_SECONDS

TRUE_PREMISES = {"composition": "solo", "work_pattern": "works_away"}
"""The generating process behind hh_001 (persona: one working
professional at an office on weekdays) — the ground-truth premise labels
the assumption-recovery metric checks a graph against."""

TRUE_HYPOTHESIS = {
    "hypothesis_id": "h_true",
    "rationale": "single working professional: weekday office days take "
                 "the carry items out of the house; meals and coffee at "
                 "home mornings and evenings; weekend reading.",
    "rest": {
        "keys_mara": "entry_table_e1", "wallet_mara": "entry_table_e1",
        "backpack_mara": "entry_hook_e1", "jacket_mara": "entry_hook_e1",
        "laptop_mara": "kitchen_table_k1", "phone_mara": "nightstand_b1",
        "mug_mara": "cupboard_k1", "class:plate": "cupboard_k1",
        "class:bowl": "cupboard_k1", "class:pan": "cupboard_k1",
        "class:pot": "cupboard_k1", "book_mara": "bookshelf_l1",
        "glasses_mara": "kitchen_table_k1", "towel_mara": "towel_rack_ba1",
        "water_bottle_mara": "counter_k1", "umbrella_mara": "entry_floor_e1",
        "hairbrush_mara": "bathroom_shelf_ba1",
        "medication_bottle_mara": "bathroom_shelf_ba1",
    },
    "activities": [
        {"name": "office_day", "days": "weekday", "frequency_per_week": 5,
         "start_hour": 8.0, "duration_h": 8.5,
         "moves": [
             {"target": "keys_mara", "to": "OUT_OF_HOUSE",
              "chance": "almost_always"},
             {"target": "wallet_mara", "to": "OUT_OF_HOUSE",
              "chance": "almost_always"},
             {"target": "backpack_mara", "to": "OUT_OF_HOUSE",
              "chance": "almost_always"},
             {"target": "jacket_mara", "to": "OUT_OF_HOUSE",
              "chance": "usually"},
             {"target": "phone_mara", "to": "OUT_OF_HOUSE",
              "chance": "usually"},
         ]},
        {"name": "breakfast", "days": "both", "frequency_per_week": 7,
         "start_hour": 6.2, "duration_h": 0.8,
         "moves": [
             {"target": "class:bowl", "to": "kitchen_table_k1",
              "chance": "sometimes", "duration_h": 17.8},
             {"target": "class:pan", "to": "kitchen_table_k1",
              "chance": "sometimes", "duration_h": 17.8},
         ]},
        {"name": "coffee", "days": "both", "frequency_per_week": 5,
         "start_hour": 6.1, "duration_h": 0.5,
         "moves": [
             {"target": "mug_mara", "to": "counter_k1",
              "chance": "usually", "duration_h": 17.9},
         ]},
        {"name": "dinner", "days": "both", "frequency_per_week": 7,
         "start_hour": 17.5, "duration_h": 1.2,
         "moves": [
             {"target": "class:plate", "to": "kitchen_table_k1",
              "chance": "usually", "duration_h": 6.5},
             {"target": "class:pan", "to": "kitchen_table_k1",
              "chance": "sometimes", "duration_h": 6.5},
         ]},
        {"name": "weekend_reading", "days": "weekend",
         "frequency_per_week": 2, "start_hour": 14.0, "duration_h": 2.5,
         "moves": [
             {"target": "glasses_mara", "to": "couch_l1",
              "chance": "usually", "duration_h": 10.0},
             {"target": "book_mara", "to": "couch_l1",
              "chance": "usually"},
             {"target": "mug_mara", "to": "coffee_table_l1",
              "chance": "sometimes", "duration_h": 10.0},
         ]},
    ],
}

WRONG_HYPOTHESIS = {
    "hypothesis_id": "h_wrong",
    "rationale": "plausible for A working professional, wrong for this "
                 "one: works from home at a desk, no weekday absences, "
                 "dinner late, reading on weekday evenings.",
    "rest": {
        "keys_mara": "counter_k1", "wallet_mara": "nightstand_b1",
        "backpack_mara": "bedroom_floor_b1", "jacket_mara": "couch_l1",
        "laptop_mara": "desk_b1", "phone_mara": "kitchen_table_k1",
        "mug_mara": "dish_rack_k1", "class:plate": "dish_rack_k1",
        "class:bowl": "dish_rack_k1", "class:pan": "counter_k1",
        "class:pot": "counter_k1", "book_mara": "nightstand_b1",
        "glasses_mara": "nightstand_b1", "towel_mara": "bathroom_shelf_ba1",
    },
    "activities": [
        {"name": "home_office", "days": "both", "frequency_per_week": 7,
         "start_hour": 10.0, "duration_h": 7.0,
         "moves": [
             {"target": "laptop_mara", "to": "desk_b1",
              "chance": "almost_always", "duration_h": 14.0},
             {"target": "phone_mara", "to": "desk_b1",
              "chance": "usually", "duration_h": 14.0},
             {"target": "mug_mara", "to": "desk_b1",
              "chance": "usually", "duration_h": 14.0},
         ]},
        {"name": "late_dinner", "days": "both", "frequency_per_week": 7,
         "start_hour": 21.0, "duration_h": 1.0,
         "moves": [
             {"target": "class:plate", "to": "couch_l1",
              "chance": "usually", "duration_h": 3.0},
         ]},
        {"name": "evening_reading", "days": "weekday",
         "frequency_per_week": 5, "start_hour": 22.0, "duration_h": 1.0,
         "moves": [
             {"target": "book_mara", "to": "bed_b1",
              "chance": "usually", "duration_h": 2.0},
             {"target": "glasses_mara", "to": "bed_b1",
              "chance": "usually", "duration_h": 2.0},
         ]},
    ],
}


def run_gate(household: str = "hh_001", seed: int = 0,
             days: int | None = None, verbose: bool = True) -> bool:
    episode = next(JsonlBank(bank_path(household, seed)).episodes())
    with tempfile.TemporaryDirectory() as tmp:
        hyp_file = pathlib.Path(tmp) / f"{episode.household_id}.json"
        hyp_file.write_text(json.dumps(
            {"hypotheses": [TRUE_HYPOTHESIS, WRONG_HYPOTHESIS]}))
        model = LLMHypothesisMixture(random.Random(0), pathlib.Path(tmp))
        model.reset(episode.agent_view())
        for observation in episode.initial_observations:
            model.update(observation)
        horizon = (days if days is not None else episode.n_days) * DAY_SECONDS
        current_day, verdicts = 0, []
        for evidence in episode.evidence_stream():
            if evidence.t >= horizon:
                break
            if verbose and evidence.t // DAY_SECONDS > current_day:
                current_day = evidence.t // DAY_SECONDS
                _report(model, current_day, verdicts)
            model.update(evidence)
        _report(model, current_day + 1, verdicts)
        index = {p.name: i for i, p in enumerate(model.particles)}
        i_true = index["HypothesisProgram(h_true)"]
        i_wrong = index["HypothesisProgram(h_wrong)"]
        loglik = [p + a for p, a in zip(model.presence_totals,
                                        model.absence_totals)]
        cumulative_ok = loglik[i_true] > loglik[i_wrong]
        late = [v for day, v in verdicts if day >= 7]
        lead_ok = late and sum(late) / len(late) >= 0.75
        final_ok = verdicts[-1][1]
    passed = cumulative_ok and lead_ok and bool(final_ok)
    print(f"\ncumulative log-likelihood: true={loglik[i_true]:.1f} "
          f"wrong={loglik[i_wrong]:.1f} "
          f"(gap {loglik[i_true] - loglik[i_wrong]:+.1f} nats) -> "
          f"{'ok' if cumulative_ok else 'FAIL'}")
    print(f"2x weight lead on {sum(late)}/{len(late)} days from day 7 -> "
          f"{'ok' if lead_ok else 'FAIL'}; "
          f"final day {'ok' if final_ok else 'FAIL'}")
    print(f"\n{'PASS' if passed else 'FAIL'}")
    return passed


def _report(model: LLMHypothesisMixture, day: int, verdicts: list) -> None:
    weights = {p.name: w for p, w in zip(model.particles, model.weights)}
    true_w = weights["HypothesisProgram(h_true)"]
    wrong_w = weights["HypothesisProgram(h_wrong)"]
    verdicts.append((day, true_w > 2.0 * wrong_w))
    stat_w = 1.0 - true_w - wrong_w
    print(f"day {day:2d}  true={true_w:.3f}  wrong={wrong_w:.3f}  "
          f"stat={stat_w:.3f}  ess={model.effective_sample_size:.2f}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--household", default="hh_001")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--days", type=int, default=None)
    args = ap.parse_args()
    raise SystemExit(0 if run_gate(args.household, args.seed, args.days)
                     else 1)


if __name__ == "__main__":
    main()
