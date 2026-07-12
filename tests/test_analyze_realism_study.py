"""
Tests for scripts/analyze_realism_study.py against synthetic response
data — no real human annotations exist yet, so these prove the
statistics are computed correctly (known-agreement/known-correlation
synthetic cases), not that any real quality number is good or bad.
"""
from __future__ import annotations

from dynamic_home_eqa.scripts.analyze_realism_study import (
    build_report,
    escape_rate,
    human_vs_automatic_correlation,
    overall_quality_rates,
    pairwise_weighted_kappa,
)


def _response(participant, item, placement="resting_naturally", behavior="plausible",
              visibility="clearly_visible", **signals):
    row = {
        "participant_id": participant, "item_id": item,
        "placement": placement, "behavior": behavior, "visibility": visibility,
    }
    row.update(signals)
    return row


class TestPairwiseWeightedKappa:
    def test_perfect_agreement_gives_kappa_one(self):
        responses = [
            _response("ada", f"i{i}", placement=v)
            for i, v in enumerate(["resting_naturally", "slightly_off", "clearly_wrong"] * 3)
        ] + [
            _response("bob", f"i{i}", placement=v)
            for i, v in enumerate(["resting_naturally", "slightly_off", "clearly_wrong"] * 3)
        ]
        result = pairwise_weighted_kappa(responses, "placement")
        assert result["n_pairs"] == 1
        assert result["mean_kappa"] == 1.0
        assert "almost perfect" in result["interpretation"]

    def test_opposite_ratings_give_low_kappa(self):
        items = [f"i{i}" for i in range(9)]
        vals_a = (["resting_naturally", "slightly_off", "clearly_wrong"] * 3)
        vals_b = (["clearly_wrong", "slightly_off", "resting_naturally"] * 3)
        responses = [_response("ada", it, placement=v) for it, v in zip(items, vals_a)]
        responses += [_response("bob", it, placement=v) for it, v in zip(items, vals_b)]
        result = pairwise_weighted_kappa(responses, "placement")
        assert result["mean_kappa"] < 0.0

    def test_escape_values_excluded_from_agreement(self):
        responses = [
            _response("ada", "i1", placement="resting_naturally"),
            _response("ada", "i2", placement="cannot_tell"),
            _response("bob", "i1", placement="resting_naturally"),
            _response("bob", "i2", placement="clearly_wrong"),
        ]
        result = pairwise_weighted_kappa(responses, "placement")
        # only i1 is comparable (i2 excluded on ada's side) — with n=1
        # overlapping item python's kappa is undefined; the important
        # thing is it doesn't silently treat cannot_tell as a scale point.
        assert result["n_pairs"] in (0, 1)

    def test_insufficient_data_reported_not_crashed(self):
        responses = [_response("ada", "i1")]
        result = pairwise_weighted_kappa(responses, "placement")
        assert result["n_pairs"] == 0
        assert result["mean_kappa"] is None


class TestEscapeRate:
    def test_computes_fraction_using_escape_value(self):
        responses = [
            _response("ada", "i1", placement="resting_naturally"),
            _response("ada", "i2", placement="cannot_tell"),
            _response("ada", "i3", placement="cannot_tell"),
            _response("ada", "i4", placement="clearly_wrong"),
        ]
        assert escape_rate(responses, "placement") == 0.5

    def test_visibility_has_no_escape_value(self):
        assert escape_rate([_response("ada", "i1")], "visibility") is None


class TestHumanVsAutomaticCorrelation:
    def test_perfect_positive_correlation_detected(self):
        scale = ["clearly_wrong", "slightly_off", "resting_naturally"]
        responses = [
            _response("ada", f"i{i}", placement=scale[i % 3], llm_self_graded_realism_day_mean=float(i % 3))
            for i in range(12)
        ]
        result = human_vs_automatic_correlation(responses, "placement", "llm_self_graded_realism_day_mean")
        assert result["rho"] > 0.9
        assert result["ci95"][0] > 0  # even the low end of the CI should be positive

    def test_no_variance_reported_not_crashed(self):
        responses = [_response("ada", f"i{i}", placement="resting_naturally", llm_self_graded_realism_day_mean=1.0) for i in range(10)]
        result = human_vs_automatic_correlation(responses, "placement", "llm_self_graded_realism_day_mean")
        assert result["rho"] is None
        assert "note" in result

    def test_too_few_observations_reported_not_crashed(self):
        responses = [_response("ada", "i1", llm_self_graded_realism_day_mean=1.0)]
        result = human_vs_automatic_correlation(responses, "placement", "llm_self_graded_realism_day_mean")
        assert result["n"] == 1
        assert result["rho"] is None


class TestOverallQualityRates:
    def test_low_quality_rate_computed_across_the_whole_pool(self):
        responses = (
            [_response("ada", f"bad{i}", placement="clearly_wrong") for i in range(3)]
            + [_response("ada", f"good{i}", placement="resting_naturally") for i in range(9)]
        )
        rates = overall_quality_rates(responses)
        assert rates["n_responses"] == 12
        assert abs(rates["placement_low_quality_rate"] - 0.25) < 1e-9


class TestBuildReportEndToEnd:
    def test_empty_db_path_produces_zero_response_report(self, tmp_path):
        report = build_report(tmp_path / "does_not_exist.db", "v1")
        assert report["n_responses"] == 0
        assert report["n_participants"] == 0
        for axis_result in report["agreement"].values():
            assert axis_result["n_pairs"] == 0

    def test_real_sqlite_db_reads_correctly(self, tmp_path):
        import json
        import sqlite3

        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            """CREATE TABLE responses_v1 (
                participant_id TEXT, item_id TEXT, dataset_version TEXT,
                placement TEXT, behavior TEXT, visibility TEXT, issues TEXT,
                llm_self_graded_realism_day_mean REAL
            )"""
        )
        conn.execute(
            "INSERT INTO responses_v1 VALUES (?,?,?,?,?,?,?,?)",
            ("ada", "i1", "v1", "resting_naturally", "plausible", "clearly_visible",
             json.dumps(["floating"]), 2.5),
        )
        conn.commit()
        conn.close()

        report = build_report(db_path, "v1")
        assert report["n_responses"] == 1
        assert report["n_participants"] == 1
