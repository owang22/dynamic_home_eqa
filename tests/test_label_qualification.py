"""
Pure-logic tests for embodied/sampling.py's LabelQualification dataclass —
specifically the D1 (kernel generalization) unmapped_slots property, which
joined exists_at_patrol_start/unreachable_slots as a third qualification
gate. No habitat_sim needed (unlike qualify_labels itself, which builds a
real EmbodiedWorld — see test_sampling.py for that end-to-end path).
"""
from __future__ import annotations

from dynamic_home_eqa.embodied.sampling import LabelQualification


def test_qualifies_when_all_three_properties_hold():
    lq = LabelQualification(
        label="book_1", exists_at_patrol_start=True,
        historical_slots=("kitchen.counter",), unreachable_slots=(), unmapped_slots=(),
    )
    assert lq.qualifies


def test_does_not_qualify_when_a_slot_is_unmapped():
    lq = LabelQualification(
        label="book_1", exists_at_patrol_start=True,
        historical_slots=("kitchen.counter", "xyzzy_bad"), unreachable_slots=(),
        unmapped_slots=("xyzzy_bad",),
    )
    assert not lq.qualifies


def test_unmapped_slots_defaults_to_empty():
    lq = LabelQualification(
        label="book_1", exists_at_patrol_start=True,
        historical_slots=("kitchen.counter",), unreachable_slots=(),
    )
    assert lq.unmapped_slots == ()
    assert lq.qualifies


def test_reason_reports_unmapped_slots():
    lq = LabelQualification(
        label="book_1", exists_at_patrol_start=True,
        historical_slots=("xyzzy_bad",), unreachable_slots=(), unmapped_slots=("xyzzy_bad",),
    )
    assert "unmapped historical slot" in lq.reason()
    assert "xyzzy_bad" in lq.reason()


def test_reason_reports_all_three_failures_together():
    lq = LabelQualification(
        label="book_1", exists_at_patrol_start=False,
        historical_slots=("attic.shelf", "xyzzy_bad"),
        unreachable_slots=("attic.shelf",), unmapped_slots=("xyzzy_bad",),
    )
    reason = lq.reason()
    assert "does not exist at patrol_start" in reason
    assert "unreachable historical slot" in reason
    assert "unmapped historical slot" in reason


def test_reason_is_qualifies_when_nothing_wrong():
    lq = LabelQualification(
        label="book_1", exists_at_patrol_start=True,
        historical_slots=("kitchen.counter",), unreachable_slots=(), unmapped_slots=(),
    )
    assert lq.reason() == "qualifies"
