"""
Tests for llm_prior/scoring.py's parsers and brier_score — pure logic, no
model calls, no network.
"""
from __future__ import annotations

import pytest

from dynamic_home_eqa.llm_prior.scoring import (
    ParseFailure,
    brier_score,
    parse_mcq_logprob_distribution,
    parse_sample_count_distribution,
    parse_verbalized_location,
    parse_verbalized_stay_probability,
)


class TestParseMcqLogprobDistribution:
    def test_confident_answer_dominates(self):
        top_logprobs = {"▁A": -0.001, "▁B": -8.0, "▁The": -10.0}
        dist = parse_mcq_logprob_distribution(top_logprobs, ("A", "B"))
        assert dist["A"] > 0.99
        assert dist["A"] + dist["B"] == pytest.approx(1.0)

    def test_bare_token_without_sentencepiece_marker_still_matches(self):
        top_logprobs = {"A": -0.5, "B": -1.0}
        dist = parse_mcq_logprob_distribution(top_logprobs, ("A", "B"))
        assert set(dist) == {"A", "B"}

    def test_missing_option_gets_floor_not_zero(self):
        top_logprobs = {"A": -0.1, "C": -5.0}  # "B" never appears in top-N
        dist = parse_mcq_logprob_distribution(top_logprobs, ("A", "B"))
        assert dist["B"] > 0.0

    def test_variants_of_same_letter_combine(self):
        top_logprobs = {"▁A": -2.0, "A": -3.0, "▁B": -1.0}
        dist = parse_mcq_logprob_distribution(top_logprobs, ("A", "B"))
        assert dist["A"] + dist["B"] == pytest.approx(1.0)

    def test_raises_on_empty_logprobs(self):
        with pytest.raises(ParseFailure):
            parse_mcq_logprob_distribution({}, ("A", "B"))


class TestParseVerbalizedLocation:
    def test_parses_valid_json(self):
        raw = '{"shelf": 0.7, "table": 0.3}'
        dist = parse_verbalized_location(raw, ("shelf", "table"))
        assert dist["shelf"] == pytest.approx(0.7)

    def test_normalizes_unnormalized_probabilities(self):
        raw = '{"shelf": 7, "table": 3}'
        dist = parse_verbalized_location(raw, ("shelf", "table"))
        assert dist["shelf"] == pytest.approx(0.7)
        assert sum(dist.values()) == pytest.approx(1.0)

    def test_extracts_json_embedded_in_prose(self):
        raw = 'Sure, here you go:\n{"shelf": 0.5, "table": 0.5}\nHope that helps!'
        dist = parse_verbalized_location(raw, ("shelf", "table"))
        assert dist["shelf"] == pytest.approx(0.5)

    def test_raises_on_missing_support_state(self):
        raw = '{"shelf": 1.0}'
        with pytest.raises(ParseFailure, match="missing support"):
            parse_verbalized_location(raw, ("shelf", "table"))

    def test_raises_on_malformed_json(self):
        with pytest.raises(ParseFailure):
            parse_verbalized_location("not json at all", ("shelf", "table"))

    def test_raises_on_non_numeric_value(self):
        raw = '{"shelf": "high", "table": 0.5}'
        with pytest.raises(ParseFailure):
            parse_verbalized_location(raw, ("shelf", "table"))


class TestParseVerbalizedStayProbability:
    def test_parses_valid_value(self):
        assert parse_verbalized_stay_probability('{"stay_probability": 0.42}') == pytest.approx(0.42)

    def test_raises_on_out_of_range(self):
        with pytest.raises(ParseFailure):
            parse_verbalized_stay_probability('{"stay_probability": 1.5}')

    def test_raises_on_missing_key(self):
        with pytest.raises(ParseFailure):
            parse_verbalized_stay_probability('{"probability": 0.5}')


class TestParseSampleCountDistribution:
    def test_normalizes_over_recognized_options(self):
        counts = {"A": 15, "B": 5, "_other": 0}
        result = parse_sample_count_distribution(counts, ("A", "B"))
        assert result.distribution["A"] == pytest.approx(0.75)
        assert result.unparsed_fraction == pytest.approx(0.0)
        assert result.n == 20

    def test_reports_unparsed_fraction(self):
        counts = {"A": 10, "B": 8, "_other": 2}
        result = parse_sample_count_distribution(counts, ("A", "B"))
        assert result.unparsed_fraction == pytest.approx(0.1)
        assert result.distribution["A"] == pytest.approx(10 / 18)

    def test_raises_when_nothing_recognized(self):
        counts = {"A": 0, "B": 0, "_other": 20}
        with pytest.raises(ParseFailure):
            parse_sample_count_distribution(counts, ("A", "B"))

    def test_raises_on_zero_total(self):
        with pytest.raises(ParseFailure):
            parse_sample_count_distribution({"A": 0, "B": 0}, ("A", "B"))


class TestBrierScore:
    def test_perfect_prediction_scores_zero(self):
        assert brier_score({"a": 1.0, "b": 0.0}, "a") == pytest.approx(0.0)

    def test_worst_prediction_scores_two(self):
        assert brier_score({"a": 0.0, "b": 1.0}, "a") == pytest.approx(2.0)

    def test_uniform_over_two_scores_half(self):
        assert brier_score({"a": 0.5, "b": 0.5}, "a") == pytest.approx(0.5)

    def test_raises_if_true_state_not_in_distribution(self):
        with pytest.raises(ValueError):
            brier_score({"a": 1.0}, "b")
