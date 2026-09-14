"""Offline tests for the elicitation plumbing: prompt construction,
scramble round-trip, JSON extraction, and validation splitting. No
server involved anywhere."""

from __future__ import annotations

import json

import pytest

from baselines.bank import JsonlBank
from baselines.household_analysis import bank_path
from baselines.llm_hypotheses.elicit import extract_json, validate_hypotheses
from baselines.llm_hypotheses.prompt import (build_anonymization_maps,
                                             crossref_table,
                                             deanonymize_hypothesis,
                                             elicitation_prompt,
                                             sighting_digest)


@pytest.fixture(scope="module")
def episode():
    return next(JsonlBank(bank_path("hh_001", 0)).episodes())


def test_named_prompt_contains_real_ids_and_rules(episode) -> None:
    user, maps = elicitation_prompt(episode, warmup_days=7)
    assert maps["omap"] == {}
    assert "laptop_mara" in user and "kitchen_table_k1" in user
    assert "almost_always" in user and "weekend" in user
    assert "d0 is a Monday" in user


def test_anonymized_prompt_leaks_no_real_names(episode) -> None:
    user, maps = elicitation_prompt(episode, warmup_days=7, anonymized=True)
    for real in list(episode.object_classes) + list(episode.receptacle_ids):
        assert real not in user
    for cls in set(episode.object_classes.values()):
        assert f"class: {cls}" not in user
    assert "object_1" in user and "receptacle_1" in user


def test_anonymization_round_trip_restores_real_ids(episode) -> None:
    omap, rmap, cmap = build_anonymization_maps(episode)
    some_class = next(iter(set(episode.object_classes.values())))
    anon_hyp = {
        "hypothesis_id": "h1", "rationale": "r",
        "rest": {omap["laptop_mara"]: rmap["kitchen_table_k1"],
                 "class:" + cmap[some_class]: rmap["cupboard_k1"]},
        "activities": [
            {"name": "a", "days": "weekday", "frequency_per_week": 5,
             "start_hour": 8.0, "duration_h": 8.0,
             "moves": [{"target": omap["keys_mara"],
                        "to": rmap["OUT_OF_HOUSE"],
                        "chance": "usually"}]}]}
    real = deanonymize_hypothesis(anon_hyp, omap, rmap, cmap)
    assert real["rest"]["laptop_mara"] == "kitchen_table_k1"
    assert real["rest"]["class:" + some_class] == "cupboard_k1"
    move = real["activities"][0]["moves"][0]
    assert move["target"] == "keys_mara" and move["to"] == "OUT_OF_HOUSE"
    valid, failed = validate_hypotheses(
        [real], episode.object_classes, episode.receptacle_ids)
    assert valid and not failed


def test_digest_is_compact_and_grouped(episode) -> None:
    digest = sighting_digest(episode, warmup_days=7)
    assert "laptop_mara:" in digest
    # Same-receptacle runs collapse: no receptacle repeated twice in a row
    # on one line.
    for line in digest.splitlines():
        parts = line.split("; ")
        tokens = [p.split(" ")[-1] for p in parts if " " in p]
        assert all(a != b for a, b in zip(tokens, tokens[1:])), line


def test_extract_json_from_prose_tail() -> None:
    payload = 'Some reasoning...\n{"hypotheses": [{"hypothesis_id": "h1"}]}'
    assert extract_json(payload)["hypotheses"][0]["hypothesis_id"] == "h1"
    with pytest.raises(json.JSONDecodeError):
        extract_json("no json here")


def test_validate_splits_and_names_bad_strings(episode) -> None:
    good = {"hypothesis_id": "ok", "rationale": "r",
            "rest": {"laptop_mara": "kitchen_table_k1"}, "activities": []}
    bad = {"hypothesis_id": "bad", "rationale": "r",
           "rest": {"marys_cup": "kitchen_table_k1"}, "activities": []}
    valid, failed = validate_hypotheses(
        [good, bad], episode.object_classes, episode.receptacle_ids)
    assert len(valid) == 1 and len(failed) == 1
    assert failed[0]["bad_strings"] == ["marys_cup"]


def test_crossref_table_covers_every_id(episode) -> None:
    """The cross-reference table is the key for reading anonymized
    artifacts later, so every object, receptacle, and class must appear
    next to its token."""
    omap, rmap, cmap = build_anonymization_maps(episode)
    table = crossref_table(episode, omap, rmap, cmap)
    for obj, token in omap.items():
        assert f"| {token} | {obj} |" in table
    for rec, token in rmap.items():
        assert f"| {token} | {rec} |" in table
    for cls, token in cmap.items():
        assert f"| {token} | {cls} |" in table


def test_anonymized_tokens_are_unpadded_and_unique(episode) -> None:
    omap, rmap, cmap = build_anonymization_maps(episode)
    assert omap[sorted(episode.object_classes)[0]] == "object_1"
    assert len(set(omap.values())) == len(omap)
    assert len(set(rmap.values())) == len(rmap)
