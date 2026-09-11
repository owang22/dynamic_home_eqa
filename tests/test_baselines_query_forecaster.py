"""Query forecaster: empirical rates by hour of day and day type.
Times are seconds since episode start; day 0 is a Monday."""

from __future__ import annotations

import pytest

from baselines.query_forecaster import QueryForecaster
from baselines.types import DAY_SECONDS, Question

H = 3600


def _q(n: int, obj: str, day: int, hour: int) -> Question:
    t = day * DAY_SECONDS + hour * H + 600
    return Question(question_id=f"q{n}", object_id=obj, t_query=t,
                    day_index=day, object_class="thing")


def test_empirical_rates_split_by_hour_and_day_type() -> None:
    # keys queried at 09:xx on every weekday day 0-4; never on the
    # weekend; mug queried once (day 1, 12:xx).
    questions = [_q(i, "keys", d, 9) for i, d in enumerate(range(5))]
    questions.append(_q(99, "mug", 1, 12))
    forecaster = QueryForecaster.fit_empirical(questions,
                                               training_days=range(7))
    # 5 weekday days in training, 5 keys queries in the 09:00 slot.
    assert forecaster.rate_at("keys", "weekday", 9) == pytest.approx(1.0)
    assert forecaster.rate_at("keys", "weekend", 9) == 0.0
    assert forecaster.rate_at("mug", "weekday", 12) == pytest.approx(1 / 5)
    # Full 09:00 weekday hour: one expected keys query; the weekend
    # (day 5 is Saturday) expects none.
    monday_9 = 7 * DAY_SECONDS + 9 * H
    assert forecaster.expected_queries(monday_9, 1.0)["keys"] == (
        pytest.approx(1.0))
    saturday_9 = 5 * DAY_SECONDS + 9 * H
    assert "keys" not in forecaster.expected_queries(saturday_9, 1.0)


def test_horizon_prorates_partial_hours() -> None:
    questions = [_q(i, "keys", d, 9) for i, d in enumerate(range(5))]
    forecaster = QueryForecaster.fit_empirical(questions,
                                               training_days=range(5))
    # Window 08:30-09:30 covers half of the 09:00 slot.
    t = 7 * DAY_SECONDS + 8 * H + 1800
    assert forecaster.expected_queries(t, 1.0)["keys"] == pytest.approx(0.5)
    # Window 08:00-10:00 covers the whole slot.
    t = 7 * DAY_SECONDS + 8 * H
    assert forecaster.expected_queries(t, 2.0)["keys"] == pytest.approx(1.0)
