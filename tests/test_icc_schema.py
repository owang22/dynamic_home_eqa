"""Stage A: the shared day-level reductions.

These are the decisions both loaders depend on, so an error here biases
every ICC identically and invisibly — hence unit tests rather than trust.
"""

from __future__ import annotations

import pytest

from icc.schema import (DAY_END_MIN, DAY_START_MIN, DowType, DropReport,
                        StartRule, merge_episodes, reduce_episodes,
                        spanning_start_end)

H = 60


def ep(start_h: float, end_h: float):
    """An episode given in clock hours of the diary day (04:00 = hour 4)."""
    return (start_h * H, end_h * H)


def test_start_min_is_measured_from_the_0400_boundary() -> None:
    start, duration, n = reduce_episodes([ep(9, 9.5)], StartRule.FIRST)
    assert start == 5 * H          # 09:00 is 5 h after the 04:00 boundary
    assert duration == 30 and n == 1


def test_episodes_are_clipped_to_the_window() -> None:
    # An episode running past 04:00 next day contributes only its inside part.
    _, duration, _ = reduce_episodes([(DAY_END_MIN - 60, DAY_END_MIN + 600)],
                                     StartRule.FIRST)
    assert duration == 60


def test_duration_sums_and_first_start_wins() -> None:
    start, duration, n = reduce_episodes(
        [ep(20, 20.5), ep(8, 8.25), ep(12, 12.5)], StartRule.FIRST)
    assert start == 4 * H          # 08:00
    assert duration == 30 + 15 + 30
    assert n == 3


def test_last_rule_takes_the_final_onset() -> None:
    start, _, _ = reduce_episodes([ep(8, 9), ep(21, 22)], StartRule.LAST)
    assert start == 17 * H         # 21:00


def test_spans_end_rule_ignores_unlabelled_evenings() -> None:
    # A day holding only the morning tail of the previous night has NO
    # episode running at the window end, so bedtime is undefined rather
    # than being reported as 04:00 (the bug this rule exists to prevent).
    morning_only = [(DAY_START_MIN, DAY_START_MIN + 3 * H)]
    start, _, _ = reduce_episodes(morning_only, StartRule.SPANS_END)
    assert start is None
    # With an evening episode running past the boundary, that onset wins.
    with_evening = morning_only + [(23 * H, DAY_END_MIN + 3 * H)]
    start, _, _ = reduce_episodes(with_evening, StartRule.SPANS_END)
    assert start == 23 * H - DAY_START_MIN


def test_none_rule_yields_no_start() -> None:
    start, duration, n = reduce_episodes([ep(9, 9.1), ep(14, 14.1)],
                                         StartRule.NONE)
    assert start is None and n == 2 and duration == pytest.approx(12)


def test_wake_requires_an_episode_spanning_the_window_start() -> None:
    asleep_at_0400 = [(DAY_START_MIN - 300, DAY_START_MIN + 3 * H)]
    assert spanning_start_end(asleep_at_0400) == 3 * H
    # Awake at 04:00 (a night-shift day): waking is undefined, not the end
    # of whatever the first labelled episode happens to be.
    nap_only = [ep(14, 15)]
    assert spanning_start_end(nap_only) is None


def test_merge_joins_fragmented_episodes_within_tolerance() -> None:
    # A night split by a bathroom trip: one episode after merging.
    night = [(23 * H, 25 * H), (25 * H + 10, 31 * H)]
    assert len(merge_episodes(night, 60)) == 1
    assert merge_episodes(night, 60)[0] == (23 * H, 31 * H)
    # Far-apart episodes are never merged, whatever the tolerance.
    assert len(merge_episodes([ep(8, 9), ep(20, 21)], 60)) == 2
    # Zero tolerance leaves the series untouched (the default).
    assert len(merge_episodes(night, 0)) == 2


def test_merging_repairs_the_measures_it_was_added_for() -> None:
    # Unmerged, a 01:30 interruption makes "waking" look like 01:30 and the
    # re-settle look like the bedtime. Merged, both are correct.
    night = [(DAY_START_MIN - 300, 21.5 * H), (21.6 * H, DAY_END_MIN + 200)]
    assert spanning_start_end(night) == pytest.approx(17.5 * H)
    merged = merge_episodes(night, 60)
    assert spanning_start_end(merged) == pytest.approx(DAY_END_MIN
                                                       - DAY_START_MIN)


def test_dow_type_split() -> None:
    assert DowType.of(0) is DowType.WEEKDAY      # Monday
    assert DowType.of(4) is DowType.WEEKDAY      # Friday
    assert DowType.of(5) is DowType.WEEKEND      # Saturday
    assert DowType.of(6) is DowType.WEEKEND      # Sunday


def test_drops_are_counted_not_silent() -> None:
    r = DropReport(source="test")
    r.drop("sensor_outage", 3)
    r.drop("sensor_outage")
    assert r.counts["sensor_outage"] == 4
    assert "sensor_outage=4" in r.render()
