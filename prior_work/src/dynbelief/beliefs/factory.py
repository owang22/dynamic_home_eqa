"""Belief-tier factory: name -> configured instance.

f(t) sources for b3: "fremen" (spectral fit from the training days' change
times), "constant", or any SwitchingPrior-compatible callable (Stage 1's
offline schedule prior drops in here).
"""
from __future__ import annotations

from dynbelief.beliefs.base import object_class
from dynbelief.beliefs.beta_bayes import B25BetaBayes
from dynbelief.beliefs.fremen import (constant_prior, fremen_prior,
                                      fremen_prior_weekly)
from dynbelief.beliefs.perpetua import B3PerpetuaStar
from dynbelief.beliefs.zoo import B0LastSeen, B1LongMem, B2ClassDecay

BELIEF_TIERS = ["b0_lastseen", "b1_longmem", "b2_classdecay",
                "b25_betabayes", "b3_perpetua_star"]


def make_belief(name: str, world, f_source: str = "fremen",
                train_horizon_min: int | None = None,
                switching_prior=None):
    """`world` supplies the class map (and, for f_source="fremen", the
    training-day change times: every human-moved event with
    t < train_horizon_min)."""
    classes = {oid: object_class(lbl) for oid, lbl in world.obj_label.items()}
    if name == "b0_lastseen":
        return B0LastSeen()
    if name == "b1_longmem":
        return B1LongMem()
    if name == "b2_classdecay":
        return B2ClassDecay(classes)
    if name == "b25_betabayes":
        return B25BetaBayes(classes)
    if name == "b3_perpetua_star":
        if switching_prior is not None:
            f = switching_prior
        elif f_source == "constant":
            f = constant_prior()
        elif f_source == "fremen":
            times = [t for t in world.change_times()
                     if train_horizon_min is None or t < train_horizon_min]
            f = fremen_prior(times)
        elif f_source == "fremen_weekly":
            # Section C: valid only on calendar episodes (day 0 = Monday);
            # fremen_prior_weekly falls back to the daily fit when the
            # >=4-instances-per-day-of-week gate fails.
            assert train_horizon_min is not None, "fremen_weekly needs a train horizon"
            times = [t for t in world.change_times() if t < train_horizon_min]
            from dynbelief import MIN_PER_DAY
            train_days = list(range(train_horizon_min // MIN_PER_DAY))
            f = fremen_prior_weekly(times, train_days)
        else:
            raise ValueError(f"unknown f_source {f_source!r}")
        return B3PerpetuaStar(classes, f)
    raise ValueError(f"unknown belief tier {name!r}")
