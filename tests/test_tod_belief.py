"""
Tests for embodied/posterior.py's tod_prior schedule-only baseline:
bucket_changes_by_time_of_day and TimeOfDayBeliefStore.

Named "tod_prior"/TimeOfDayBeliefStore, not "FreMEn" (Frequency Map
Enhancement) — no frequency-domain fit happens anywhere here, just
n_buckets independent discrete-time kernels (Suite Buildout phase B1
rename; see TimeOfDayBeliefStore's own docstring).

No habitat_sim needed — pure belief math and manifest bucketing, same as
test_transition_kernel.py.
"""
from __future__ import annotations

import pytest

from dynamic_home_eqa.embodied.posterior import (
    OUTSIDE,
    TimeOfDayBeliefStore,
    TransitionKernel,
    bucket_changes_by_time_of_day,
)
from dynamic_home_eqa.embodied.types import OracleDetection, Pose


def _kernel(bucket_id: int, states=("a", "b", OUTSIDE)) -> TransitionKernel:
    """A distinct dest_dist per bucket_id so tests can tell which bucket's
    kernel actually got selected."""
    dest_by_bucket = {
        0: (0.9, 0.05, 0.05),
        1: (0.05, 0.9, 0.05),
        2: (0.05, 0.05, 0.9),
        3: (0.4, 0.4, 0.2),
    }
    return TransitionKernel(category="test", states=states, lambda_per_hour=0.5, dest_dist=dest_by_bucket[bucket_id])


class TestBucketChangesByTimeOfDay:
    def test_splits_into_n_buckets(self):
        manifests = [{"changes": [
            {"t": 1.0}, {"t": 7.0}, {"t": 13.0}, {"t": 19.0},  # one per 6h bucket
        ]}]
        buckets = bucket_changes_by_time_of_day(manifests, n_buckets=4)
        assert len(buckets) == 4
        assert [len(b) for b in buckets] == [1, 1, 1, 1]

    def test_wraps_past_24_hours(self):
        # t=25.0 is hour 1 of the next day -> same bucket as t=1.0.
        manifests = [{"changes": [{"t": 1.0}, {"t": 25.0}]}]
        buckets = bucket_changes_by_time_of_day(manifests, n_buckets=4)
        assert len(buckets[0]) == 2

    def test_merges_across_manifests(self):
        manifests = [{"changes": [{"t": 1.0}]}, {"changes": [{"t": 2.0}]}]
        buckets = bucket_changes_by_time_of_day(manifests, n_buckets=4)
        assert len(buckets[0]) == 2


class TestTimeOfDayBeliefStore:
    def _store(self, n_buckets=4):
        bucketed = {"test": tuple(_kernel(i) for i in range(n_buckets))}
        return TimeOfDayBeliefStore(bucketed_kernels=bucketed, n_buckets=n_buckets)

    def _observe(self, store, label="obj_1", category="test", t=0.0):
        store.observe_detection(
            OracleDetection(label=label, category=category, world_pos=(0, 0, 0), anchor="a", t=t),
            Pose(0, 0, 0, 0),
        )

    def test_predicts_from_the_bucket_the_query_time_falls_in(self):
        store = self._store()
        self._observe(store)
        # Bucket 0 = hours [0,6): dest favors "a". Bucket 1 = [6,12): favors "b".
        assert store.believed_anchor("obj_1", t=2.0) == "a"
        assert store.believed_anchor("obj_1", t=8.0) == "b"

    def test_ignores_negative_observations_entirely(self):
        store = self._store()
        self._observe(store)
        before = store.believed_anchor("obj_1", t=2.0)
        store.observe_negative("obj_1", "a", t=2.0)
        after = store.believed_anchor("obj_1", t=2.0)
        assert before == after == "a"

    def test_unknown_label_returns_none(self):
        store = self._store()
        assert store.believed_anchor("never_seen", t=1.0) is None
        assert store.validity("never_seen", t=1.0) == 0.0

    def test_validity_is_the_predicted_states_own_mass(self):
        store = self._store()
        self._observe(store)
        assert store.validity("obj_1", t=2.0) == pytest.approx(0.9)

    def test_known_labels_tracks_observed_labels_only(self):
        store = self._store()
        assert store.known_labels() == []
        self._observe(store)
        assert store.known_labels() == ["obj_1"]

    def test_top_candidates_excludes_outside_and_unreachable(self):
        store = self._store()
        self._observe(store, t=13.0)  # bucket 2: dest = (0.05, 0.05, 0.9) -> a,b both near-zero
        # Use bucket 3 instead (0.4, 0.4, 0.2) so both a/b have real mass.
        top = store.top_candidates("obj_1", t=19.5, travel_time_to={"a": 1.0, "b": 100.0}.get)
        assert OUTSIDE not in top
        assert top[0] == "a"  # equal mass, much cheaper travel -> higher value density

    def test_has_no_nodes_attribute(self):
        # By design (see module docstring) — only ever paired with a
        # non-resensing policy; a search-capable policy touching
        # belief.nodes directly should fail loudly, not silently degrade.
        store = self._store()
        assert not hasattr(store, "nodes")
