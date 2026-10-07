"""Stage D: does the estimator recover variance components it was given?

The ICC is a ratio of two variances estimated from two different datasets by
two different routes. A sampler or algebra bug is invisible in the output —
the number just comes out wrong — so the estimator is tested against
SYNTHETIC data whose true components are known by construction.
"""

from __future__ import annotations

import datetime
import math
from typing import List, Tuple

import numpy as np
import pytest

from icc.estimate import (DEGENERATE, NEGATIVE, OK, ar1_phi, estimate,
                          weighted_total_variance, within_variance)
from icc.schema import DayRow


def _casas_rows(persons: int, days: int, sigma_between: float,
                sigma_within: float, seed: int = 0,
                activity: str = "synthetic") -> List[DayRow]:
    """CASAS-shaped panel: few persons, many days, known components."""
    rng = np.random.default_rng(seed)
    rows: List[DayRow] = []
    start = datetime.date(2011, 1, 3)          # a Monday
    for p in range(persons):
        level = 600.0 + rng.normal(0, sigma_between)
        for d in range(days):
            day = start + datetime.timedelta(days=d)
            rows.append(DayRow(
                person_id=f"p{p}", source="casas", date=day.isoformat(),
                dow_type="weekend" if day.weekday() >= 5 else "weekday",
                activity=activity, participated=True,
                start_min=level + rng.normal(0, sigma_within),
                duration_min=60.0, n_occurrences=1, valid_day=True))
    return rows


def _atus_arrays(n: int, sigma_between: float, sigma_within: float,
                 seed: int = 1) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ATUS-shaped sample: one day per person, so the cross-sectional
    variance is between + within by construction."""
    rng = np.random.default_rng(seed)
    values = 600.0 + rng.normal(0, sigma_between, n) + \
        rng.normal(0, sigma_within, n)
    weights = np.ones(n)
    dow = np.where(rng.random(n) < 0.5, "weekend", "weekday")
    return values, weights, dow


def test_within_variance_recovers_the_residual_scale() -> None:
    rows = _casas_rows(persons=8, days=120, sigma_between=90, sigma_within=40)
    import pandas as pd
    df = pd.DataFrame.from_records(
        [{"person_id": r.person_id, "date": r.date, "dow_type": r.dow_type,
          "value": r.start_min, "weight": 1.0} for r in rows])
    sigma2, _ = within_variance(df)
    # Truth is 40^2 = 1600; the person intercepts must NOT leak in.
    assert sigma2 == pytest.approx(1600, rel=0.15)


def test_weighted_total_variance_recovers_between_plus_within() -> None:
    values, weights, dow = _atus_arrays(40000, sigma_between=90,
                                        sigma_within=40)
    total = weighted_total_variance(values, weights, dow)
    assert total == pytest.approx(90 ** 2 + 40 ** 2, rel=0.05)


def test_icc_is_recovered_end_to_end() -> None:
    # True ICC = 8100 / (8100 + 1600) = 0.835
    truth = 90 ** 2 / (90 ** 2 + 40 ** 2)
    casas = _casas_rows(persons=8, days=150, sigma_between=90,
                        sigma_within=40)
    atus = {("synthetic", "start_min"): _atus_arrays(40000, 90, 40)}
    est = estimate("synthetic", "start_min", casas, atus,
                   np.random.default_rng(0))
    assert est.status == OK
    assert est.icc == pytest.approx(truth, abs=0.06)
    assert est.icc_lo < truth < est.icc_hi


def test_zero_between_person_variance_gives_icc_near_zero() -> None:
    casas = _casas_rows(persons=8, days=150, sigma_between=0.001,
                        sigma_within=40)
    atus = {("synthetic", "start_min"): _atus_arrays(40000, 0.001, 40)}
    est = estimate("synthetic", "start_min", casas, atus,
                   np.random.default_rng(0))
    assert abs(est.icc) < 0.1


def test_negative_icc_is_flagged_never_clamped() -> None:
    # CASAS residents deliberately more erratic than the ATUS population:
    # the identity breaks and the pipeline must say so.
    casas = _casas_rows(persons=6, days=120, sigma_between=10,
                        sigma_within=200)
    atus = {("synthetic", "start_min"): _atus_arrays(20000, 10, 30)}
    est = estimate("synthetic", "start_min", casas, atus,
                   np.random.default_rng(0))
    assert est.status == NEGATIVE
    assert est.icc < 0                    # reported as-is, not clipped to 0
    assert "manual" in est.note


def test_universal_participation_is_degenerate_not_negative() -> None:
    rows = [DayRow(person_id=f"p{p}", source="casas",
                   date=(datetime.date(2011, 1, 3)
                         + datetime.timedelta(days=d)).isoformat(),
                   dow_type="weekday", activity="synthetic",
                   participated=True, start_min=600.0, duration_min=60.0,
                   n_occurrences=1, valid_day=True)
            for p in range(6) for d in range(100)]
    values = np.ones(20000)               # everyone, every day
    atus = {("synthetic", "participation"):
            (values, np.ones(20000), np.array(["weekday"] * 20000))}
    est = estimate("synthetic", "participation", rows, atus,
                   np.random.default_rng(0))
    assert est.status == DEGENERATE
    assert math.isnan(est.icc)


def test_insufficient_data_is_reported_not_estimated() -> None:
    casas = _casas_rows(persons=2, days=40, sigma_between=90,
                        sigma_within=40)          # 2 persons < MIN_PERSONS
    atus = {("synthetic", "start_min"): _atus_arrays(20000, 90, 40)}
    est = estimate("synthetic", "start_min", casas, atus,
                   np.random.default_rng(0))
    assert est.status == "INSUFFICIENT_DATA"
    assert math.isnan(est.icc)


def test_ar1_phi_recovers_a_known_autocorrelation() -> None:
    import pandas as pd
    rng = np.random.default_rng(3)
    phi_true = 0.6
    recs = []
    for p in range(6):
        z = 0.0
        for d in range(300):
            z = phi_true * z + rng.normal(0, 1)
            recs.append({"person_id": f"p{p}",
                         "date": (datetime.date(2011, 1, 1)
                                  + datetime.timedelta(days=d)).isoformat(),
                         "dow_type": "weekday", "value": z, "weight": 1.0})
    assert ar1_phi(pd.DataFrame(recs)) == pytest.approx(phi_true, abs=0.08)
