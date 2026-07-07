"""
Tests for scripts/e2_voi_reconciliation.py's pure-logic pieces (bucket_
pairs, abstain_rate, accuracy_of_non_abstained, accuracy_of_all,
bootstrap_over_clusters, paired_bootstrap_delta) — the full main()/load_
rows() path needs real embodied_results/diagnostics/ data and is
exercised by actually running the script.
"""
from __future__ import annotations

import pytest

from dynamic_home_eqa.scripts.e2_voi_reconciliation import (
    accuracy_of_all,
    accuracy_of_non_abstained,
    abstain_rate,
    bootstrap_over_clusters,
    bucket_pairs,
    paired_bootstrap_delta,
)


def _row(policy, scene="s1", eval_folder="s1_day4", wait_hours=1.0, label="book_1",
         correct=True, abstained=False, invocations=1, distance=0.0):
    return {
        "policy": policy, "scene": scene, "eval_folder": eval_folder, "wait_hours": wait_hours,
        "label": label, "correct": correct, "abstained": abstained,
        "policy_invocations": invocations, "distance_traveled_m": distance,
    }


class TestBucketPairs:
    def test_identical_non_traveled_outcome_buckets_as_identical(self):
        rows = [
            _row("decay_voi", correct=True, invocations=1, distance=0.0),
            _row("answer_immediately", correct=True, invocations=1, distance=0.0),
        ]
        b = bucket_pairs(rows, "decay_voi", "answer_immediately")
        assert b.identical == 1
        assert b.traveled_diff == []
        assert b.voi_abstained_floor_answered == []
        assert b.mystery == []

    def test_traveled_and_differs_buckets_correctly(self):
        rows = [
            _row("decay_voi", correct=True, invocations=2, distance=5.0),
            _row("answer_immediately", correct=False, invocations=1, distance=0.0),
        ]
        b = bucket_pairs(rows, "decay_voi", "answer_immediately")
        assert len(b.traveled_diff) == 1
        assert b.identical == 0

    def test_voi_abstained_floor_answered_buckets_correctly(self):
        rows = [
            _row("decay_voi", correct=None, abstained=True, invocations=2, distance=3.0),
            _row("answer_immediately", correct=False, abstained=False, invocations=1, distance=0.0),
        ]
        b = bucket_pairs(rows, "decay_voi", "answer_immediately")
        assert len(b.voi_abstained_floor_answered) == 1
        assert b.traveled_diff == []

    def test_mystery_bucket_catches_untraveled_unexplained_difference(self):
        """A pair where decay_voi did NOT travel, did NOT abstain-diverge,
        yet the outcome differs anyway — the determinism-bug signal this
        script's own escalation path exists to catch."""
        rows = [
            _row("decay_voi", correct=True, invocations=1, distance=0.0),
            _row("answer_immediately", correct=False, invocations=1, distance=0.0),
        ]
        b = bucket_pairs(rows, "decay_voi", "answer_immediately")
        assert len(b.mystery) == 1

    def test_traveled_but_same_outcome_counts_as_identical(self):
        rows = [
            _row("decay_voi", correct=True, invocations=2, distance=5.0),
            _row("answer_immediately", correct=True, invocations=1, distance=0.0),
        ]
        b = bucket_pairs(rows, "decay_voi", "answer_immediately")
        assert b.identical == 1
        assert b.traveled_diff == []

    def test_buckets_partition_all_pairs_exactly_once(self):
        rows = []
        for i in range(5):
            rows.append(_row("decay_voi", label=f"obj_{i}", correct=(i % 2 == 0), invocations=1 + i % 2, distance=float(i)))
            rows.append(_row("answer_immediately", label=f"obj_{i}", correct=(i % 3 == 0)))
        b = bucket_pairs(rows, "decay_voi", "answer_immediately")
        total = b.identical + len(b.traveled_diff) + len(b.voi_abstained_floor_answered) + len(b.mystery)
        assert total == 5


class TestAbstainRateAndAccuracy:
    def test_abstain_rate(self):
        rows = [
            _row("decay_voi", abstained=True), _row("decay_voi", abstained=False, label="l2"),
            _row("decay_voi", abstained=False, label="l3"),
        ]
        assert abstain_rate(rows, "decay_voi") == pytest.approx(1 / 3)

    def test_accuracy_of_non_abstained_excludes_abstained_rows(self):
        rows = [
            _row("decay_voi", correct=True, abstained=False, label="l1"),
            _row("decay_voi", correct=False, abstained=False, label="l2"),
            _row("decay_voi", correct=None, abstained=True, label="l3"),
        ]
        assert accuracy_of_non_abstained(rows, "decay_voi") == pytest.approx(0.5)

    def test_accuracy_of_all_scores_abstain_at_r_abstain(self):
        rows = [
            _row("decay_voi", correct=True, abstained=False, label="l1"),
            _row("decay_voi", correct=False, abstained=False, label="l2"),
            _row("decay_voi", correct=None, abstained=True, label="l3"),
            _row("decay_voi", correct=None, abstained=True, label="l4"),
        ]
        # (1.0 + 0.0 + 0.5 + 0.5) / 4 = 0.5
        assert accuracy_of_all(rows, "decay_voi") == pytest.approx(0.5)


class TestPairedBootstrapDelta:
    def test_zero_delta_when_policies_identical(self):
        rows = []
        for i, scene in enumerate(["s1", "s2", "s3", "s4", "s5"]):
            rows.append(_row("decay_voi", scene=scene, eval_folder=f"{scene}_day4", label=f"obj_{i}", correct=True))
            rows.append(_row("answer_immediately", scene=scene, eval_folder=f"{scene}_day4", label=f"obj_{i}", correct=True))
        result = paired_bootstrap_delta(rows, "decay_voi", "answer_immediately", n_resamples=200, seed=0)
        assert result.point == pytest.approx(0.0)

    def test_positive_delta_when_a_strictly_better(self):
        rows = []
        for i, scene in enumerate(["s1", "s2", "s3", "s4", "s5"]):
            rows.append(_row("decay_voi", scene=scene, eval_folder=f"{scene}_day4", label=f"obj_{i}", correct=True))
            rows.append(_row("answer_immediately", scene=scene, eval_folder=f"{scene}_day4", label=f"obj_{i}", correct=False))
        result = paired_bootstrap_delta(rows, "decay_voi", "answer_immediately", n_resamples=200, seed=0)
        assert result.point == pytest.approx(1.0)
        assert not result.degenerate
        assert result.ci_lo > 0  # excludes zero

    def test_degenerate_with_one_shared_cluster(self):
        rows = [
            _row("decay_voi", scene="s1", eval_folder="s1_day4", correct=True),
            _row("answer_immediately", scene="s1", eval_folder="s1_day4", correct=False),
        ]
        result = paired_bootstrap_delta(rows, "decay_voi", "answer_immediately")
        assert result.degenerate
        assert result.n_clusters == 1


class TestBootstrapOverClusters:
    def test_deterministic_given_fixed_seed(self):
        r1 = bootstrap_over_clusters([0.1, 0.5, 0.9], seed=7)
        r2 = bootstrap_over_clusters([0.1, 0.5, 0.9], seed=7)
        assert r1.ci_lo == r2.ci_lo
        assert r1.ci_hi == r2.ci_hi

    def test_empty_is_degenerate_nan(self):
        result = bootstrap_over_clusters([])
        assert result.n_clusters == 0
        assert result.point != result.point  # NaN
