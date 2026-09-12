"""Unit tests for the belief disagreement measurement: the divergence
arithmetic, the volatility split, and one pass over a synthetic bank."""

from __future__ import annotations

import pathlib

import pytest

from baselines.bank import JsonlBank, write_synthetic_bank
from baselines.disagreement import (FAMILY_PANEL, PARAMETER_PANEL,
                                    jensen_shannon, mean_pairwise_divergence,
                                    moves_per_day, pair_agreement,
                                    panel_labels, passive_rows,
                                    volatility_terciles)


def _episode(tmp_path: pathlib.Path):
    bank = write_synthetic_bank(tmp_path / "bank.jsonl")
    return next(JsonlBank(bank.path if hasattr(bank, "path")
                          else tmp_path / "bank.jsonl").episodes())


def test_divergence_spans_zero_to_one_and_is_symmetric() -> None:
    p = {"a": 0.5, "b": 0.5}
    q = {"c": 0.5, "d": 0.5}
    assert jensen_shannon(p, p) == pytest.approx(0.0)
    assert jensen_shannon(p, q) == pytest.approx(1.0)
    assert jensen_shannon(p, q) == pytest.approx(jensen_shannon(q, p))
    half = jensen_shannon({"a": 1.0}, {"a": 0.5, "b": 0.5})
    assert 0.0 < half < 1.0


def test_mean_pairwise_divergence_of_one_distribution_is_zero() -> None:
    assert mean_pairwise_divergence([{"a": 1.0}]) == 0.0


def test_volatility_terciles_rank_by_moves_per_day() -> None:
    moves = {f"o{i}": float(i) for i in range(9)}
    terciles = volatility_terciles(moves)
    assert terciles["o0"] == 0 and terciles["o4"] == 1 and terciles["o8"] == 2
    assert sorted(terciles.values()) == [0, 0, 0, 1, 1, 1, 2, 2, 2]
    assert volatility_terciles({}) == {}


def test_panel_labels_disambiguate_only_repeated_names() -> None:
    assert panel_labels(FAMILY_PANEL) == tuple(
        str(s["name"]) for s in FAMILY_PANEL)
    labels = panel_labels(PARAMETER_PANEL)
    assert len(set(labels)) == len(PARAMETER_PANEL)
    assert labels[0] == "smoothed_recency(smoothing_half_life_h=1)"


def test_single_belief_panel_always_agrees_with_itself(tmp_path) -> None:
    episode = _episode(tmp_path)
    rows = passive_rows(episode, [{"name": "most_frequent"}])
    assert rows
    assert all(row.unanimous for row in rows)
    assert all(row.mean_jsd == 0.0 for row in rows)


def test_two_beliefs_on_a_synthetic_bank_disagree_somewhere(
        tmp_path) -> None:
    episode = _episode(tmp_path)
    panel = [{"name": "last_observation"}, {"name": "timetable"}]
    rows = passive_rows(episode, panel)
    assert len(rows) == sum(len(day) for day in episode.questions_by_day)
    assert any(not row.unanimous for row in rows)
    assert all(0.0 <= row.mean_jsd <= 1.0 for row in rows)
    assert all(0 <= row.hour < 24 for row in rows)


def test_pair_agreement_is_symmetric_with_a_unit_diagonal(tmp_path) -> None:
    episode = _episode(tmp_path)
    panel = [{"name": "last_observation"}, {"name": "most_frequent"},
             {"name": "timetable"}]
    matrix = pair_agreement(passive_rows(episode, panel), len(panel))
    assert all(matrix[i][i] == 1.0 for i in range(len(panel)))
    assert all(matrix[i][j] == matrix[j][i]
               for i in range(len(panel)) for j in range(len(panel)))


def test_moves_per_day_counts_changes_not_the_starting_row(
        tmp_path) -> None:
    episode = _episode(tmp_path)
    moves = moves_per_day(episode)
    assert set(moves) == set(episode.trajectories)
    assert all(value >= 0.0 for value in moves.values())
