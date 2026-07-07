"""
Tests for scripts/e2_headline_comparison.py's pure-logic pieces: pool
fingerprint, clustered aggregation, and bootstrap-over-clusters. The full
main()/plotting path is exercised by actually running the script against
real milestone result files (see the phase's own verification notes), not
re-derived here with synthetic fixtures for every I/O branch.
"""
from __future__ import annotations

import pytest

from dynamic_home_eqa.scripts.e2_headline_comparison import (
    BootstrapResult,
    PoolManifest,
    SceneDescriptor,
    _cluster_means,
    bootstrap_over_clusters,
    check_pool_fingerprint,
    cluster_key,
)


def _descriptor(scene_id="102343992", location_labels=("book_1",), state_labels=(), navmesh="nm", island=1):
    return SceneDescriptor(
        scene_id=scene_id, location_labels=location_labels, state_labels=state_labels,
        navmesh_repr=navmesh, start_island=island,
    )


class TestPoolManifest:
    def test_fingerprint_is_deterministic(self):
        m1 = PoolManifest(scenes=(_descriptor(),), pipeline_version="v1")
        m2 = PoolManifest(scenes=(_descriptor(),), pipeline_version="v1")
        assert m1.fingerprint() == m2.fingerprint()

    def test_fingerprint_changes_with_scene_labels(self):
        m1 = PoolManifest(scenes=(_descriptor(location_labels=("book_1",)),), pipeline_version="v1")
        m2 = PoolManifest(scenes=(_descriptor(location_labels=("book_1", "vase_1")),), pipeline_version="v1")
        assert m1.fingerprint() != m2.fingerprint()

    def test_fingerprint_changes_with_navmesh(self):
        m1 = PoolManifest(scenes=(_descriptor(navmesh="a"),), pipeline_version="v1")
        m2 = PoolManifest(scenes=(_descriptor(navmesh="b"),), pipeline_version="v1")
        assert m1.fingerprint() != m2.fingerprint()

    def test_fingerprint_changes_with_start_island(self):
        m1 = PoolManifest(scenes=(_descriptor(island=1),), pipeline_version="v1")
        m2 = PoolManifest(scenes=(_descriptor(island=2),), pipeline_version="v1")
        assert m1.fingerprint() != m2.fingerprint()

    def test_fingerprint_changes_with_pipeline_version(self):
        m1 = PoolManifest(scenes=(_descriptor(),), pipeline_version="v1")
        m2 = PoolManifest(scenes=(_descriptor(),), pipeline_version="v2")
        assert m1.fingerprint() != m2.fingerprint()

    def test_fingerprint_changes_with_more_scenes(self):
        m1 = PoolManifest(scenes=(_descriptor(scene_id="a"),), pipeline_version="v1")
        m2 = PoolManifest(scenes=(_descriptor(scene_id="a"), _descriptor(scene_id="b")), pipeline_version="v1")
        assert m1.fingerprint() != m2.fingerprint()


class TestCheckPoolFingerprint:
    def test_passes_with_matching_fingerprints(self):
        results = [{"fingerprint": "abc"}, {"fingerprint": "abc"}]
        check_pool_fingerprint(results, PoolManifest(scenes=(), pipeline_version="v1"))  # must not raise

    def test_raises_on_mismatched_fingerprints(self):
        results = [{"fingerprint": "abc"}, {"fingerprint": "def"}]
        with pytest.raises(ValueError, match="Mismatched fingerprints"):
            check_pool_fingerprint(results, PoolManifest(scenes=(), pipeline_version="v1"))


class TestClusterKey:
    def test_uses_scene_and_eval_folder_fields(self):
        row = {"scene": "102343992", "eval_folder": "day4"}
        assert cluster_key(row) == ("102343992", "day4")

    def test_falls_back_to_frozen_for_legacy_rows(self):
        from dynamic_home_eqa.embodied.experiment_config import FROZEN
        row = {}  # a row written before "scene"/"eval_folder" were recorded
        assert cluster_key(row) == (FROZEN.scene, FROZEN.eval_folder)


class TestClusterMeans:
    def test_one_mean_per_cluster(self):
        rows = [
            {"scene": "a", "eval_folder": "d1", "v": 1.0},
            {"scene": "a", "eval_folder": "d1", "v": 3.0},
            {"scene": "b", "eval_folder": "d1", "v": 10.0},
        ]
        means = sorted(_cluster_means(rows, lambda r: r["v"]))
        assert means == [2.0, 10.0]

    def test_filter_fn_excludes_rows(self):
        rows = [
            {"scene": "a", "eval_folder": "d1", "v": 1.0, "keep": True},
            {"scene": "a", "eval_folder": "d1", "v": 100.0, "keep": False},
        ]
        means = _cluster_means(rows, lambda r: r["v"], filter_fn=lambda r: r["keep"])
        assert means == [1.0]

    def test_none_values_are_dropped(self):
        rows = [{"scene": "a", "eval_folder": "d1", "v": None}, {"scene": "a", "eval_folder": "d1", "v": 5.0}]
        means = _cluster_means(rows, lambda r: r["v"])
        assert means == [5.0]


class TestBootstrapOverClusters:
    def test_degenerate_with_zero_clusters(self):
        result = bootstrap_over_clusters([])
        assert result.n_clusters == 0
        assert result.degenerate
        assert result.ci_lo is None and result.ci_hi is None

    def test_degenerate_with_one_cluster(self):
        result = bootstrap_over_clusters([0.75])
        assert result.n_clusters == 1
        assert result.degenerate
        assert result.point == pytest.approx(0.75)
        assert result.ci_lo is None and result.ci_hi is None

    def test_point_estimate_is_the_mean(self):
        result = bootstrap_over_clusters([0.5, 0.7, 0.9])
        assert result.point == pytest.approx(0.7)

    def test_ci_brackets_the_point_estimate_with_enough_clusters(self):
        result = bootstrap_over_clusters([0.1, 0.5, 0.9, 0.3, 0.7, 0.6, 0.4, 0.8], n_resamples=1000, seed=0)
        assert not result.degenerate
        assert result.ci_lo <= result.point <= result.ci_hi

    def test_deterministic_given_fixed_seed(self):
        values = [0.2, 0.4, 0.6, 0.8, 1.0]
        r1 = bootstrap_over_clusters(values, seed=42)
        r2 = bootstrap_over_clusters(values, seed=42)
        assert r1.ci_lo == r2.ci_lo
        assert r1.ci_hi == r2.ci_hi

    def test_nan_values_are_dropped_before_aggregation(self):
        result = bootstrap_over_clusters([1.0, float("nan"), 3.0])
        assert result.n_clusters == 2
        assert result.point == pytest.approx(2.0)
