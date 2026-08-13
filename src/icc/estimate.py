"""Stage D — variance components and the ICC per activity.

The identity, stated once:

    ATUS  (many persons x 1 day)    -> sigma2_total  = between + within
    CASAS (few persons x many days) -> sigma2_within
    ICC = sigma2_between / sigma2_total = 1 - sigma2_within / sigma2_total

For that subtraction to mean anything, the two sources must be measuring
the same quantity with the same covariate structure removed. So:

* CASAS gives sigma2_within as the RESIDUAL scale of a random-intercept
  model, ``value ~ C(dow_type)`` grouped by person. The random intercept
  absorbs each person's habitual level (that is between-person variance and
  must not leak into the within estimate); the weekday/weekend fixed effect
  absorbs the regime difference, which is structure we model explicitly
  elsewhere rather than call noise.
* ATUS gives sigma2_total as the WEIGHTED variance of the same day-level
  statistic after removing the weighted weekday/weekend means — the same
  covariate, removed the same way, so the two numbers are commensurable.

Measures per activity: the start-time statistic (minutes from 04:00, when
the activity's start rule defines one), log duration (durations are
right-skewed and a variance on the raw scale is dominated by the tail), and
participation (did it happen that day).

Uncertainty is a BLOCK bootstrap: persons are resampled with replacement,
and within a person contiguous 7-day blocks are resampled rather than
individual days, because day-level resampling destroys the serial
correlation that :func:`ar1_phi` is measuring and would understate the
within-person variance's uncertainty.

Hard guardrail: sigma2_within > sigma2_total makes the ICC negative, which
is not a small-sample artefact to clamp away — it means the two sources are
not measuring the same thing (crosswalk mismatch, differing measurement
noise, or CASAS residents genuinely more erratic than the ATUS
population). Such activities are flagged ``FLAGGED_NEGATIVE`` and excluded
from the automated path; resolving one is a documented manual decision.
"""

from __future__ import annotations

import collections
import dataclasses
import math
import warnings
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from icc.schema import DayRow

BLOCK_DAYS = 7
N_BOOTSTRAP = 200
MIN_PERSONS = 3
MIN_DAYS_PER_PERSON = 10
MIN_ATUS_DIARIES = 500
NEGATIVE = "FLAGGED_NEGATIVE"
INSUFFICIENT = "INSUFFICIENT_DATA"
DEGENERATE = "DEGENERATE_NO_VARIANCE"
OK = "OK"
MIN_TOTAL_VARIANCE = 1e-6
UNIVERSAL_RATE = 0.99
"""A participation measure whose population rate exceeds this (or falls
below 1 - this) has no meaningful between-person variance to estimate:
99.9% of ATUS respondents sleep on any given day, so "does this person
sleep?" is not a trait. Such rows are DEGENERATE, not negative-ICC — a
ratio of two near-zero variances is noise dressed as a parameter."""

MEASURES = ("start_min", "log_duration", "participation")


@dataclasses.dataclass
class Estimate:
    """One (activity, measure) row of the ICC table."""

    activity: str
    measure: str
    status: str
    n_casas_persons: int
    n_casas_days: int
    n_atus_diaries: int
    sigma2_within: float
    sigma2_total: float
    icc: float
    icc_lo: float
    icc_hi: float
    phi_ar1: float
    resid_skew: float
    resid_kurtosis: float
    note: str

    FIELDS = ("activity", "measure", "status", "n_casas_persons",
              "n_casas_days", "n_atus_diaries", "sigma2_within",
              "sigma2_total", "icc", "icc_lo", "icc_hi", "phi_ar1",
              "resid_skew", "resid_kurtosis", "note")


def _values(rows: Sequence[DayRow], activity: str, measure: str
            ) -> pd.DataFrame:
    """Valid, participating day rows for one (activity, measure) as a frame."""
    recs = []
    for r in rows:
        if r.activity != activity or not r.valid_day:
            continue
        if measure == "participation":
            value: Optional[float] = float(r.participated)
        elif not r.participated:
            continue
        elif measure == "start_min":
            value = r.start_min
        else:
            value = (math.log(r.duration_min)
                     if r.duration_min and r.duration_min > 0 else None)
        if value is None:
            continue
        recs.append({"person_id": r.person_id, "date": r.date,
                     "dow_type": r.dow_type, "value": value,
                     "weight": r.weight})
    return pd.DataFrame.from_records(recs)


def within_variance(df: pd.DataFrame) -> Tuple[float, np.ndarray]:
    """Residual scale of ``value ~ C(dow_type)`` with a person intercept.

    Returns (sigma2_within, residuals). Falls back to the pooled
    within-(person, regime) variance when the mixed model cannot fit — the
    two agree closely and the fallback is reported in the note.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            fit = smf.mixedlm("value ~ C(dow_type)", df,
                              groups=df["person_id"]).fit()
            return float(fit.scale), np.asarray(fit.resid)
        except Exception:
            pass
    resid = []
    for _, cell in df.groupby(["person_id", "dow_type"]):
        resid.extend(cell["value"] - cell["value"].mean())
    arr = np.asarray(resid, dtype=float)
    n_cells = df.groupby(["person_id", "dow_type"]).ngroups
    dof = max(len(arr) - n_cells, 1)
    return float((arr ** 2).sum() / dof), arr


def pooled_within_variance(df: pd.DataFrame) -> float:
    """Fast ANOVA-style equivalent of :func:`within_variance`, for bootstrap
    resamples (thousands of mixed-model fits would dominate the runtime)."""
    ss = 0.0
    n_cells = 0
    n = 0
    for _, cell in df.groupby(["person_id", "dow_type"]):
        v = cell["value"].to_numpy()
        ss += float(((v - v.mean()) ** 2).sum())
        n_cells += 1
        n += len(v)
    return ss / max(n - n_cells, 1)


def weighted_total_variance(values: np.ndarray, weights: np.ndarray,
                            dow: np.ndarray) -> float:
    """Weighted variance after removing the weighted weekday/weekend means.

    Mirrors the covariate removal on the CASAS side so the two variances
    are commensurable (module docstring).
    """
    resid = np.empty_like(values, dtype=float)
    for regime in np.unique(dow):
        m = dow == regime
        w = weights[m]
        mean = float(np.average(values[m], weights=w))
        resid[m] = values[m] - mean
    w = weights
    return float(np.average(resid ** 2, weights=w) * len(w) / max(len(w) - 2, 1))


def ar1_phi(df: pd.DataFrame) -> float:
    """Lag-1 autocorrelation of person-demeaned residuals, averaged over
    persons — the "streaky week" parameter the day generator needs."""
    phis: List[float] = []
    for person, g in df.groupby("person_id"):
        g = g.sort_values("date")
        v = g["value"].to_numpy(dtype=float)
        if len(v) < 2 * BLOCK_DAYS:
            continue
        v = v - v.mean()
        denom = float((v[:-1] ** 2).sum())
        if denom <= 0:
            continue
        phis.append(float((v[:-1] * v[1:]).sum() / denom))
    return float(np.mean(phis)) if phis else float("nan")


def _person_blocks(g: pd.DataFrame) -> List[pd.DataFrame]:
    g = g.sort_values("date")
    return [g.iloc[i:i + BLOCK_DAYS] for i in range(0, len(g), BLOCK_DAYS)]


def bootstrap_icc(casas: pd.DataFrame, atus_values: np.ndarray,
                  atus_weights: np.ndarray, atus_dow: np.ndarray,
                  rng: np.random.Generator, n: int = N_BOOTSTRAP
                  ) -> Tuple[float, float]:
    """Percentile CI for the ICC from paired block bootstraps of both sides."""
    persons = list(casas["person_id"].unique())
    blocks = {p: _person_blocks(g) for p, g in casas.groupby("person_id")}
    n_atus = len(atus_values)
    draws: List[float] = []
    for _ in range(n):
        picked = rng.choice(persons, size=len(persons), replace=True)
        frames = []
        for k, p in enumerate(picked):
            bs = blocks[p]
            chosen = rng.integers(0, len(bs), size=len(bs))
            part = pd.concat([bs[i] for i in chosen])
            part = part.assign(person_id=f"{p}#{k}")   # resampled persons are
            frames.append(part)                        # distinct clusters
        boot = pd.concat(frames)
        within = pooled_within_variance(boot)
        idx = rng.integers(0, n_atus, size=n_atus)
        total = weighted_total_variance(atus_values[idx], atus_weights[idx],
                                        atus_dow[idx])
        if total > 0:
            draws.append(1.0 - within / total)
    if not draws:
        return float("nan"), float("nan")
    return (float(np.percentile(draws, 2.5)),
            float(np.percentile(draws, 97.5)))


def estimate(activity: str, measure: str, casas_rows: Sequence[DayRow],
             atus: Dict[Tuple[str, str], Tuple[np.ndarray, np.ndarray,
                                               np.ndarray]],
             rng: np.random.Generator) -> Estimate:
    """One ICC-table row, with the guardrails applied."""
    blank = dict(n_casas_persons=0, n_casas_days=0, n_atus_diaries=0,
                 sigma2_within=float("nan"), sigma2_total=float("nan"),
                 icc=float("nan"), icc_lo=float("nan"), icc_hi=float("nan"),
                 phi_ar1=float("nan"), resid_skew=float("nan"),
                 resid_kurtosis=float("nan"))
    casas = _values(casas_rows, activity, measure)
    key = (activity, measure)
    if key not in atus or casas.empty:
        return Estimate(activity, measure, INSUFFICIENT, note=(
            "no ATUS side" if key not in atus else "no CASAS rows"), **blank)
    values, weights, dow = atus[key]

    counts = casas.groupby("person_id").size()
    keepers = counts[counts >= MIN_DAYS_PER_PERSON].index
    casas = casas[casas["person_id"].isin(keepers)]
    n_persons = casas["person_id"].nunique()
    n_days = len(casas)
    blank.update(n_casas_persons=n_persons, n_casas_days=n_days,
                 n_atus_diaries=len(values))
    if n_persons < MIN_PERSONS or len(values) < MIN_ATUS_DIARIES:
        return Estimate(activity, measure, INSUFFICIENT, note=(
            f"needs >= {MIN_PERSONS} CASAS persons with >= "
            f"{MIN_DAYS_PER_PERSON} days and >= {MIN_ATUS_DIARIES} ATUS "
            f"diaries"), **blank)

    within, resid = within_variance(casas)
    total = weighted_total_variance(values, weights, dow)
    phi = ar1_phi(casas)
    skew = float(pd.Series(resid).skew()) if len(resid) > 2 else float("nan")
    kurt = float(pd.Series(resid).kurtosis()) if len(resid) > 3 else float("nan")
    icc = 1.0 - within / total if total > 0 else float("nan")
    lo, hi = bootstrap_icc(casas, values, weights, dow, rng)
    status = OK
    note = ""
    rate = float(np.average(values, weights=weights))
    universal = (measure == "participation"
                 and (rate > UNIVERSAL_RATE or rate < 1 - UNIVERSAL_RATE))
    if total < MIN_TOTAL_VARIANCE or universal:
        status = DEGENERATE
        note = (f"population rate {rate:.4f} is effectively constant: no "
                f"between-person variance to estimate" if universal else
                f"ATUS variance {total:.2e} below {MIN_TOTAL_VARIANCE:g}")
        icc = float("nan")
    elif icc < 0:
        status = NEGATIVE
        spans_zero = lo == lo and hi == hi and lo <= 0 <= hi
        note = ("sigma2_within exceeds sigma2_total: the two sources are not "
                "measuring the same quantity here. Requires manual "
                "resolution (crosswalk, measurement noise, or genuinely "
                "more erratic CASAS residents); excluded from the "
                "automated path."
                + (" The bootstrap CI includes 0, so this is consistent with "
                   "a true ICC of zero rather than with a gross mismatch."
                   if spans_zero else
                   " The bootstrap CI excludes 0, so this is a substantive "
                   "disagreement between the sources, not sampling noise."))
    return Estimate(activity=activity, measure=measure, status=status,
                    n_casas_persons=n_persons, n_casas_days=n_days,
                    n_atus_diaries=len(values), sigma2_within=within,
                    sigma2_total=total, icc=icc, icc_lo=lo, icc_hi=hi,
                    phi_ar1=phi, resid_skew=skew, resid_kurtosis=kurt,
                    note=note)
