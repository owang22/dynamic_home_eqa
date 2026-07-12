"""Pure-logic tests for embodied/realized_world.py's schema + lookups —
no habitat_sim needed (the builder that PRODUCES a real artifact does)."""
from __future__ import annotations

import pathlib

from dynamic_home_eqa.embodied.realized_world import (
    PLACEMENT_ANCHOR_UNBACKED,
    PLACEMENT_OK,
    BIND,
    SPAWN,
    ObjectBinding,
    ObjectEventRecord,
    RealizedDayArtifact,
    RealizedDayHeader,
    RealizedEventMirror,
    RealizedObject,
    RealizedPose,
    anchor_at,
    divergent_object_time_rate,
    load_realized_day,
    pose_at,
    save_realized_day,
    unrealized_event_rate,
)


def _sample_artifact() -> RealizedDayArtifact:
    header = RealizedDayHeader(
        scene_id="102343992", day_seed="102343992_family_with_kids",
        builder_version="v1", code_hash="abc123", trace_hash="def456",
    )
    stool = RealizedObject(
        label="stool_1", category="stool",
        binding=ObjectBinding(kind=BIND, scene_instance_index=42, template_name="stool_hash", source="hssd"),
        events=[
            ObjectEventRecord(t=6.0, anchor="kitchen.counter_tucked",
                               realized_pose=RealizedPose.identity_at((1.0, 0.5, 2.0)),
                               placement_status=PLACEMENT_OK, placement_method="snap_down", realized=True,
                               effective_pose=RealizedPose.identity_at((1.0, 0.5, 2.0)), divergent=False),
            # Unrealized (item 2, Pre-Pool-Build Remediation round):
            # realized_pose is None (this event's OWN placement failed),
            # but effective_pose carries forward the prior event's real
            # pose — divergent=True since that carried pose's own anchor
            # ("kitchen.counter_tucked") differs from this event's
            # symbolic anchor ("bedroom.bed").
            ObjectEventRecord(t=11.7, anchor="bedroom.bed",
                               realized_pose=None, placement_status=PLACEMENT_ANCHOR_UNBACKED, realized=False,
                               effective_pose=RealizedPose.identity_at((1.0, 0.5, 2.0)), divergent=True),
        ],
    )
    events = [
        RealizedEventMirror(label="stool_1", change_type="move_existing", t=6.0,
                             from_semantic=None, to_semantic="kitchen.counter_tucked",
                             placement_status=PLACEMENT_OK, realized=True, divergent=False),
        RealizedEventMirror(label="stool_1", change_type="move_existing", t=11.7,
                             from_semantic="kitchen.counter_tucked", to_semantic="bedroom.bed",
                             realized=False, divergent=True,
                             placement_status=PLACEMENT_ANCHOR_UNBACKED, failure_detail="no bed instance within radius"),
    ]
    return RealizedDayArtifact(header=header, objects={"stool_1": stool}, events=events)


class TestRoundTrip:
    def test_save_and_load_preserves_content(self, tmp_path):
        artifact = _sample_artifact()
        path = tmp_path / "realized_day.json"
        save_realized_day(artifact, path)
        loaded = load_realized_day(path)
        assert loaded.header == artifact.header
        assert loaded.objects["stool_1"].category == "stool"
        assert loaded.objects["stool_1"].binding.scene_instance_index == 42
        assert len(loaded.objects["stool_1"].events) == 2
        assert loaded.events[1].placement_status == PLACEMENT_ANCHOR_UNBACKED

    def test_creates_parent_directory(self, tmp_path):
        path = tmp_path / "nested" / "dir" / "realized_day.json"
        save_realized_day(_sample_artifact(), path)
        assert path.exists()


class TestPoseAt:
    def test_returns_pose_of_last_event_at_or_before_t(self):
        artifact = _sample_artifact()
        pose = pose_at(artifact, "stool_1", t=8.0)
        assert pose.pos == (1.0, 0.5, 2.0)

    def test_returns_none_before_any_event(self):
        artifact = _sample_artifact()
        assert pose_at(artifact, "stool_1", t=5.0) is None

    def test_carries_forward_through_an_unrealized_event(self):
        # t=11.7's event has realized_pose=None (ANCHOR_UNBACKED) but a
        # real effective_pose (carried forward from t=6.0 at build time,
        # see _sample_artifact's item-2 comment) — pose_at must return
        # that carried pose, not None.
        artifact = _sample_artifact()
        pose = pose_at(artifact, "stool_1", t=20.0)
        assert pose.pos == (1.0, 0.5, 2.0)

    def test_unknown_label_returns_none(self):
        artifact = _sample_artifact()
        assert pose_at(artifact, "nope", t=10.0) is None


class TestAnchorAt:
    def test_returns_the_semantic_answer_even_if_placement_failed(self):
        # "two truths": the anchor is still the true semantic answer even
        # when its realized_pose is missing (PLACEMENT_ANCHOR_UNBACKED).
        artifact = _sample_artifact()
        assert anchor_at(artifact, "stool_1", t=15.0) == "bedroom.bed"

    def test_before_first_event_returns_none(self):
        artifact = _sample_artifact()
        assert anchor_at(artifact, "stool_1", t=1.0) is None


class TestBenchmarkCardStats:
    # _sample_artifact has 2 events: 1 realized/non-divergent, 1
    # unrealized/divergent — item 2's two benchmark-card statistics.
    def test_unrealized_event_rate(self):
        artifact = _sample_artifact()
        assert unrealized_event_rate(artifact) == 0.5

    def test_divergent_object_time_rate(self):
        artifact = _sample_artifact()
        assert divergent_object_time_rate(artifact) == 0.5

    def test_empty_artifact_returns_zero_not_a_divide_by_zero(self):
        artifact = RealizedDayArtifact(
            header=RealizedDayHeader(scene_id="x", day_seed="y", builder_version="v1",
                                       code_hash="a", trace_hash="b"),
            objects={}, events=[],
        )
        assert unrealized_event_rate(artifact) == 0.0
        assert divergent_object_time_rate(artifact) == 0.0
