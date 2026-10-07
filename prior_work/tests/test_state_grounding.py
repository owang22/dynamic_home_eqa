"""
Tests for generation/grounding.py's state-proposal grounding (M3) — a
membership/domain check, not PARTNR geometry (see that module's docstring
for why it lives there anyway).
"""
from __future__ import annotations

from dynamic_home_eqa.generation.grounding import ground_state_proposal, ground_state_proposal_batch

_STATEFUL_CATEGORIES = {"oven", "tv", "fridge", "wardrobe"}


def _proposal(category="oven", variable="power", target="powered"):
    return {"object_category": category, "state_variable": variable, "target_state": target}


def test_accepts_valid_proposal():
    result = ground_state_proposal(_proposal(), _STATEFUL_CATEGORIES)
    assert result.accepted


def test_rejects_category_absent_from_scene():
    result = ground_state_proposal(_proposal(category="dishwasher"), _STATEFUL_CATEGORIES)
    assert not result.accepted
    assert "not present in this scene" in result.reason


def test_rejects_unknown_state_variable():
    result = ground_state_proposal(_proposal(variable="temperature"), _STATEFUL_CATEGORIES)
    assert not result.accepted
    assert "unknown state_variable" in result.reason


def test_rejects_out_of_domain_target_value():
    result = ground_state_proposal(_proposal(target="on"), _STATEFUL_CATEGORIES)
    assert not result.accepted
    assert "not in" in result.reason


def test_batch_filters_only_accepted():
    proposals = [_proposal(), _proposal(category="dishwasher"), _proposal(target="on")]
    accepted, results = ground_state_proposal_batch(proposals, _STATEFUL_CATEGORIES)
    assert accepted == [proposals[0]]
    assert len(results) == 3
    assert sum(1 for r in results if r.accepted) == 1
