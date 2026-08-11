"""SequentialSearch correctness: the unlimited-budget invariant and the
decisive negative-evidence fixture.

The invariant is the primary reason SequentialSearch exists: on any bank
whose queried objects are each inside some receptacle at query time,
unlimited-budget search must score task accuracy 1.0 with EVERY belief
model. A failure here is a bug in the harness, the belief update, or the
bank — never an acceptable score.
"""

from __future__ import annotations

import dataclasses
import pathlib
from typing import Callable, List

import pytest

from baselines.bank import (JsonlBank, write_gate_fail_static_bank,
                            write_gate_pass_bank,
                            write_negative_evidence_bank,
                            write_synthetic_bank)
from baselines.cli import build_agent
from baselines.harness import QuestionRecord, run_episode

UNLIMITED = 10_000

FIXTURE_BUILDERS: dict[str, Callable[[pathlib.Path], JsonlBank]] = {
    "synthetic": write_synthetic_bank,
    "negative_evidence": write_negative_evidence_bank,
    "gate_pass": write_gate_pass_bank,
    "gate_fail_static": write_gate_fail_static_bank,
}
BELIEFS = ("last_observation", "most_frequent", "timetable")


def _run_search(bank: JsonlBank, belief: str,
                budget: int | None = None) -> List[QuestionRecord]:
    records: List[QuestionRecord] = []
    for episode in bank.episodes():
        if budget is not None:
            episode = dataclasses.replace(episode, budget_per_day=budget)
        agent = build_agent({"name": belief}, {"name": "sequential_search"},
                            seed=0, episode_id=episode.episode_id)
        records += list(run_episode(agent, episode))
    return records


@pytest.mark.parametrize("fixture", sorted(FIXTURE_BUILDERS))
@pytest.mark.parametrize("belief", BELIEFS)
def test_unlimited_budget_search_is_exact(
        fixture: str, belief: str, tmp_path: pathlib.Path) -> None:
    bank = FIXTURE_BUILDERS[fixture](tmp_path / f"{fixture}.jsonl")
    records = _run_search(bank, belief, budget=UNLIMITED)
    accuracy = sum(r.correct for r in records) / len(records)
    assert accuracy == 1.0, (
        f"unlimited-budget SequentialSearch with {belief} scored "
        f"{accuracy:.3f} on {fixture}; wrong answers: "
        f"{[r.question_id for r in records if not r.correct]}")


@pytest.mark.parametrize("belief", BELIEFS)
def test_negative_evidence_is_decisive(
        belief: str, tmp_path: pathlib.Path) -> None:
    # Every belief favors shelf_a for the wallet (its three sightings),
    # but the wallet moved to shelf_c unseen. Without exclusions a search
    # senses shelf_a, sees the wallet is absent, and still answers
    # shelf_a — wrong at unlimited budget. With exclusions the miss rules
    # shelf_a out and the sweep must find shelf_c within the remaining
    # three receptacles: <= 4 senses total, >= 2 (the first must miss).
    bank = write_negative_evidence_bank(tmp_path / "neg.jsonl")
    records = {r.question_id: r for r in _run_search(bank, belief)}

    wallet = records["q_wallet"]
    assert wallet.answer_receptacle == "shelf_c"
    assert wallet.correct
    assert 2 <= wallet.budget_spent <= 4
    first_sense = wallet.actions[0]
    assert first_sense["type"] == "sense"
    assert first_sense["receptacle_id"] == "shelf_a", (
        "the belief-favored receptacle must be tried (and miss) first")

    # The decoy is where every belief expects it: found in one sense.
    decoy = records["q_coin"]
    assert decoy.correct and decoy.budget_spent == 1
