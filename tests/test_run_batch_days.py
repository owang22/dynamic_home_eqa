"""
Tests for run_batch's day-seed plumbing (the --n-days knob): multiple
independent days for the same household must land in distinct folders, and
single-day runs (the default) must keep the exact pre-existing folder
naming (no day suffix) so this is additive, not a breaking change.
"""
from __future__ import annotations

import json
import random

import pytest

from dynamic_home_eqa.generation import llm_client as llm_client_mod
from dynamic_home_eqa.generation.pipeline import run_batch


def _fake_generate(self, system, user, schema, seed=None, temperature=None):
    rng = random.Random(seed)
    props = schema.get("properties", {})

    if "proposals" in props:
        item_schema = schema["properties"]["proposals"]["items"]
        branches = item_schema.get("oneOf", [item_schema])
        out_proposals = []
        for _ in range(rng.randint(0, 3)):
            branch = rng.choice(branches)
            bp = branch["properties"]
            item = {
                "object_category":     rng.choice(bp["object_category"]["enum"]),
                "target_relationship": rng.choice(bp["target_relationship"]["enum"]),
                "target_anchor":       rng.choice(bp["target_anchor"]["enum"]),
                "reason":              "fake reason",
            }
            if "assumed_from" in bp:
                item["assumed_from"] = "unknown"
            out_proposals.append(item)
        result = {"proposals": out_proposals}
        if "activity" in props:
            result["activity"] = "fake_activity"
        if "occupant" in props:
            result["occupant"] = "fake_occupant"
        return json.dumps(result)

    if "occupants" in props:
        occ_schema = props["occupants"]["items"]["properties"]
        age_band_enum = occ_schema["age_band"]["enum"]
        occupants = [{
            "name": "Alex", "age_band": rng.choice(age_band_enum), "role": "member",
            "tidiness": 0.5, "typical_wake": 7.0, "typical_sleep": 22.0, "habits": "fake",
        }]
        return json.dumps({"occupants": occupants, "household_type": "fake"})

    if "activities" in props:
        locs = [l for l in props["activities"]["items"]["properties"]["location"]["enum"] if l != "away"]
        # Vary both the location AND the transition time by seed so two
        # different day-seeds reliably produce different traces (the earlier
        # single rng.choice(loc) collided ~1/8 of the time, making the
        # day-variance assertion seed-fragile).
        mid = round(rng.uniform(17.0, 21.0), 1)
        acts = [
            {"activity": "resting", "location": rng.choice(locs), "start": 6.0, "end": mid},
            {"activity": "sleep", "location": "bedroom", "start": mid, "end": 6.0},
        ]
        return json.dumps({"occupant_name": "unused", "activities": acts})

    if "scores" in props:
        return json.dumps({
            "scores": [{"candidate_index": i, "score": 0.5, "reason": "fake"} for i in range(10)]
        })

    return json.dumps({"conflicts": []})


@pytest.fixture(autouse=True)
def _patch_llm_client(monkeypatch):
    monkeypatch.setattr(llm_client_mod._LLMClient, "generate", _fake_generate)


def test_single_day_default_keeps_old_folder_naming(tmp_path):
    run_batch(
        scene_ids=["102343992"], household_type="family_with_kids",
        out_dir=tmp_path, day=0, cache_dir=None, force=True,
    )
    assert (tmp_path / "102343992_family_with_kids").is_dir()
    assert not (tmp_path / "102343992_family_with_kids_day0").exists()


def test_multiple_days_get_distinct_suffixed_folders_including_day_zero(tmp_path):
    run_batch(
        scene_ids=["102343992"], household_type="family_with_kids",
        out_dir=tmp_path, day=0, n_days=3, cache_dir=None, force=True,
    )
    for d in (0, 1, 2):
        folder = tmp_path / f"102343992_family_with_kids_day{d}"
        assert folder.is_dir(), f"missing folder for day {d}"
        assert (folder / "manifest.json").exists()


def test_persona_is_day_invariant_across_generated_days(tmp_path):
    run_batch(
        scene_ids=["102343992"], household_type="family_with_kids",
        out_dir=tmp_path, day=5, n_days=2, cache_dir=None, force=True,
    )
    result_a = json.loads((tmp_path / "102343992_family_with_kids_day5" / "generation_result.json").read_text())
    result_b = json.loads((tmp_path / "102343992_family_with_kids_day6" / "generation_result.json").read_text())
    assert result_a["persona"] == result_b["persona"]
    assert result_a["traces"] != result_b["traces"]


def test_variant_and_day_suffixes_combine(tmp_path):
    run_batch(
        scene_ids=["102343992"], household_type="family_with_kids",
        out_dir=tmp_path, day=0, n_variants=2, n_days=2, cache_dir=None, force=True,
    )
    assert (tmp_path / "102343992_family_with_kids_day0").is_dir()
    assert (tmp_path / "102343992_family_with_kids_day1").is_dir()
    assert (tmp_path / "102343992_family_with_kids_v1_day0").is_dir()
    assert (tmp_path / "102343992_family_with_kids_v1_day1").is_dir()
