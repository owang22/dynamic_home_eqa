"""E2 unit tests: the elicited->pseudo-observation transform is faithful and
kappa-scaled, the injection is not initialization-only (persists through real
data), and the elicitation source-model guard holds (never Claude)."""
from __future__ import annotations

from collections import Counter

import pytest

from dynbelief.e2.elicit import ALLOWED_MODELS, elicit, mixture_average
from dynbelief.e2.inject import (KAPPA_DAYS, inject, pseudo_from_elicited)

RECEPS = ["nightstand_r1", "counter_k1", "sofa_l1", "sink_k1", "elsewhere"]
ELIC = {"phone": {"home": "nightstand_r1",
                  "secondary": {"sofa_l1": 0.4, "counter_k1": 0.2},
                  "active_windows": {"evening(18-22)": 1.0, "morning(6-10)": 1.0},
                  "weekday_weekend": "same", "move_rate": "high"}}
OBJ_CLASS = {"phone_1": "phone"}


def _occ(rows):
    c = Counter(r["parents"]["phone_1"] for r in rows)
    tot = sum(c.values())
    return {k: v / tot for k, v in c.items()}


def test_transform_faithful_home_dominant():
    """Elicited home receives the plurality of pseudo-occupancy mass."""
    rows = pseudo_from_elicited(ELIC, OBJ_CLASS, RECEPS, KAPPA_DAYS["strong"], seed=1)
    occ = _occ(rows)
    assert occ["nightstand_r1"] == max(occ.values())
    # secondary receptacles receive mass ordered by elicited weight
    assert occ.get("sofa_l1", 0) > occ.get("sink_k1", 0)   # sink not elicited


def test_transform_kappa_scales_sample_size():
    for tag, k in KAPPA_DAYS.items():
        rows = pseudo_from_elicited(ELIC, OBJ_CLASS, RECEPS, k, seed=2)
        assert len({r["day"] for r in rows}) == k           # kappa days present


def test_injection_not_initialization_only():
    """A strong prior must still move a from-scratch fit toward the elicited
    home (persistence): C1 fit on pseudo-obs alone puts the object at home."""
    from dynbelief.classical.rates import C1Constant
    rows = pseudo_from_elicited(ELIC, OBJ_CLASS, RECEPS, KAPPA_DAYS["strong"], seed=3)
    rm = C1Constant(RECEPS); rm.fit(rows)
    occ = [rm.occupancy("phone_1", r, 5 * 1440 + 3 * 60) for r in RECEPS]
    assert RECEPS[occ.index(max(occ))] == "nightstand_r1"


def test_injection_prepends_and_preserves_real():
    real = [{"day": 0, "t_min": 500, "parents": {"phone_1": "sink_k1"}}]
    pseudo = pseudo_from_elicited(ELIC, OBJ_CLASS, RECEPS, 1, seed=4)
    merged = inject(real, pseudo)
    assert merged[-1] is real[0]                            # real preserved, appended last
    assert len(merged) == len(pseudo) + 1


def test_elicit_refuses_claude():
    with pytest.raises(ValueError):
        elicit("claude-sonnet-5", "a home", ["phone"], RECEPS)
    assert "claude" not in " ".join(ALLOWED_MODELS).lower()


def test_mixture_average_combines_samples():
    s1 = {"classes": [{"object_class": "phone", "home": "nightstand_r1",
                       "secondary": [{"receptacle": "sofa_l1", "weight": 0.5}],
                       "active_windows": ["evening(18-22)"],
                       "weekday_weekend": "same", "move_rate": "high"}]}
    s2 = {"classes": [{"object_class": "phone", "home": "counter_k1",
                       "secondary": [{"receptacle": "sofa_l1", "weight": 0.3}],
                       "active_windows": ["morning(6-10)"],
                       "weekday_weekend": "same", "move_rate": "high"}]}
    avg = mixture_average([s1, s1, s2], ["phone"], RECEPS)
    assert avg["phone"]["home"] == "nightstand_r1"          # plurality vote
    assert 0 < avg["phone"]["secondary"]["sofa_l1"] < 0.5   # averaged over 3
