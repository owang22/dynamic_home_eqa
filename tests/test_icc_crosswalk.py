"""The crosswalk is the pipeline's highest-risk artefact, so its invariants
are enforced by tests rather than by care."""

from __future__ import annotations

import pathlib

import pytest

from icc import crosswalk
from icc.schema import StartRule


def test_ships_and_validates() -> None:
    rows = crosswalk.load()
    assert len(rows) >= 10
    assert crosswalk.version() >= 1
    assert len(crosswalk.content_hash()) == 16


def test_every_mapping_states_a_rationale() -> None:
    # A mapping without a reason is exactly what a reviewer would attack.
    for m in crosswalk.load():
        assert len(m.rationale) > 40, m.activity


def test_included_activities_have_both_sides() -> None:
    for m in crosswalk.included():
        assert m.casas_labels, f"{m.activity}: no CASAS labels"
        # leave_home is derived from ATUS *location*, not an activity code;
        # it is the one documented exception.
        if m.activity != "leave_home":
            assert m.atus_codes, f"{m.activity}: no ATUS codes"


def test_start_rule_and_measure_are_consistent() -> None:
    for m in crosswalk.load():
        assert m.measure in ("episode", "event")
        if m.is_event:
            # An event carries an instant, so a start rule must exist for it.
            assert m.start_rule is not StartRule.NONE, m.activity


def test_duration_bearing_labels_are_not_shared(tmp_path: pathlib.Path) -> None:
    # Two episode-mappings reading one label would put the same minutes into
    # two variances; the loader must refuse rather than double count.
    bad = tmp_path / "cw.csv"
    header = ("version,activity,measure,casas_labels,atus_codes,"
              "atus_home_only,start_rule,merge_gap_min,status,confidence,"
              "rationale\n")
    row = ("1,{a},episode,Sleeping,0101,0,first,0,include,high,"
           "{a} rationale long enough to pass the rationale length check\n")
    bad.write_text(header + row.format(a="one") + row.format(a="two"))
    with pytest.raises(ValueError, match="two duration-bearing"):
        crosswalk.load(bad)


def test_event_mappings_may_share_episodes(tmp_path: pathlib.Path) -> None:
    # `wake` and `sleep` legitimately read the same sleep episodes: one takes
    # an instant from them, the other their minutes.
    ok = tmp_path / "cw.csv"
    header = ("version,activity,measure,casas_labels,atus_codes,"
              "atus_home_only,start_rule,merge_gap_min,status,confidence,"
              "rationale\n")
    ok.write_text(
        header
        + "1,wake,event,Sleeping,0101,0,first,60,include,high,"
          "reads the end of the episode already running at the window start\n"
        + "1,sleep,episode,Sleeping,0101,0,spans_end,60,include,high,"
          "reads the onset of the episode still running at the window end\n")
    assert len(crosswalk.load(ok)) == 2


def test_mixed_versions_are_rejected(tmp_path: pathlib.Path) -> None:
    bad = tmp_path / "cw.csv"
    header = ("version,activity,measure,casas_labels,atus_codes,"
              "atus_home_only,start_rule,merge_gap_min,status,confidence,"
              "rationale\n")
    bad.write_text(
        header
        + "1,a,episode,X,0101,0,first,0,include,high,rationale long enough here\n"
        + "2,b,episode,Y,0102,0,first,0,include,high,rationale long enough here\n")
    with pytest.raises(ValueError, match="mixed versions"):
        crosswalk.load(bad)
