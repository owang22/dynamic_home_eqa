"""
Tests for llm_prior/natural_dynamics.py — pure parsing/prompt logic, no
model calls.
"""
from __future__ import annotations

import pytest

from dynamic_home_eqa.llm_prior.natural_dynamics import (
    NaturalParseFailure,
    natural_dynamics_prompt,
    parse_natural_stay_probability,
)


class TestNaturalDynamicsPrompt:
    def test_returns_system_and_user(self):
        system, user = natural_dynamics_prompt("persona", "rooms", "candle", 1)
        assert "STAY_PROBABILITY" in system
        assert "candle" in user

    def test_asks_for_reasoning_not_a_forced_json_shape(self):
        system, user = natural_dynamics_prompt("persona", "rooms", "candle", 1)
        assert "JSON" not in system
        assert "JSON" not in user

    def test_state_axis_wording_differs_from_location(self):
        _, loc_user = natural_dynamics_prompt("p", "r", "fridge", 1, is_state=False)
        _, state_user = natural_dynamics_prompt("p", "r", "fridge", 1, is_state=True)
        assert loc_user != state_user


class TestParseNaturalStayProbability:
    def test_extracts_value_after_reasoning_prose(self):
        text = (
            "Emily usually cooks dinner around this time, so the fridge door "
            "opens often. Given the routine, I'd estimate:\n"
            "STAY_PROBABILITY: 0.35"
        )
        assert parse_natural_stay_probability(text) == pytest.approx(0.35)

    def test_case_insensitive_label(self):
        assert parse_natural_stay_probability("stay_probability: 0.8") == pytest.approx(0.8)

    def test_extracts_last_match_when_model_restates(self):
        text = "Initial guess STAY_PROBABILITY: 0.9\nOn reflection, STAY_PROBABILITY: 0.4"
        # re.search finds the FIRST match; documented behavior, not a bug —
        # if a model hedges by restating, the FIRST stated number is taken,
        # matching how a human skimming for the answer would read it.
        assert parse_natural_stay_probability(text) == pytest.approx(0.9)

    def test_raises_when_no_line_present(self):
        with pytest.raises(NaturalParseFailure, match="no STAY_PROBABILITY"):
            parse_natural_stay_probability("I think it depends on the household.")

    def test_raises_when_value_out_of_range(self):
        with pytest.raises(NaturalParseFailure, match="out of"):
            parse_natural_stay_probability("STAY_PROBABILITY: 1.5")
