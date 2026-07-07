"""
End-to-end integration test: generate_for_scene -> build_manifest ->
trace_validate.validate(), using a fake LLM client (no GPU/vLLM required) so
this runs as a normal, fast pytest.

The fake client returns schema-conformant but randomized JSON for every
guided-decoding call, deliberately including edge cases that previously broke
trace integrity: multiple occupants sharing real-instance-backed categories,
the room-scoping fallback firing (forcing an anchor outside the occupant's
own room), and empty proposal lists. Runs across several real HSSD scenes,
household profiles, and seeds — the hard invariants must hold for every one.
"""
from __future__ import annotations

import json
import random

import pytest

from dynamic_home_eqa.generation import llm_client as llm_client_mod
from dynamic_home_eqa.generation.manifest import build_manifest
from dynamic_home_eqa.generation.pipeline import generate_for_scene
from dynamic_home_eqa.trace_validate import validate

SCENES   = ["102343992", "102344022", "102344049"]
PROFILES = ["family_with_kids", "single_retiree", "work_from_home_adult"]


def _fake_generate(self, system, user, schema, seed=None):
    rng = random.Random(seed)
    props = schema.get("properties", {})

    if "proposals" in props:
        item_schema = schema["properties"]["proposals"]["items"]
        branches = item_schema.get("oneOf", [item_schema])
        out_proposals = []
        for _ in range(rng.randint(0, 5)):
            branch = rng.choice(branches)
            bp = branch["properties"]
            item = {
                "object_category":     rng.choice(bp["object_category"]["enum"]),
                "target_relationship": rng.choice(bp["target_relationship"]["enum"]),
                "target_anchor":       rng.choice(bp["target_anchor"]["enum"]),
                "reason":              "fake reason",
            }
            if "assumed_from" in bp:
                item["assumed_from"] = rng.choice(
                    ["kitchen counter", "unknown", "the table", "living room shelf", ""]
                )
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
        names = ["Alex", "Sam", "Jordan", "Robin"]
        n = rng.randint(1, 4)
        occupants = [{
            "name": names[i], "age_band": rng.choice(age_band_enum), "role": "member",
            "tidiness": round(rng.random(), 2), "typical_wake": round(rng.uniform(5, 9), 1),
            "typical_sleep": round(rng.uniform(20, 25), 1), "habits": "fake habits",
        } for i in range(n)]
        return json.dumps({"occupants": occupants, "household_type": "fake"})

    if "activities" in props:
        locs = [l for l in props["activities"]["items"]["properties"]["location"]["enum"] if l != "away"]
        n_acts = rng.randint(3, 8)
        acts, t = [], round(rng.uniform(5, 8), 1)
        for _ in range(n_acts):
            end = round(t + rng.uniform(0.5, 4.0), 1)
            acts.append({
                "activity": rng.choice(["cooking", "resting", "working", "cleaning", "chores"]),
                "location": rng.choice(locs), "start": t, "end": end,
            })
            t = end
        acts.append({"activity": "sleep", "location": "bedroom", "start": t, "end": round((t - 17.5) % 24 or 6.0, 1)})
        return json.dumps({"occupant_name": "unused", "activities": acts})

    if "scores" in props:
        return json.dumps({
            "scores": [{"candidate_index": i, "score": round(rng.random(), 2), "reason": "fake"} for i in range(15)]
        })

    return json.dumps({"conflicts": []})


@pytest.fixture(autouse=True)
def _patch_llm_client(monkeypatch):
    monkeypatch.setattr(llm_client_mod._LLMClient, "generate", _fake_generate)


@pytest.mark.parametrize("scene_id", SCENES)
@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("variant", [0, 1, 2])
def test_generated_manifest_satisfies_hard_invariants(scene_id, profile, variant):
    result = generate_for_scene(
        scene_id=scene_id, household_type=profile, day=variant, variant=variant,
        cache_dir=None, force=True, use_semantic_grounding=True,
    )
    manifest = build_manifest(scene_id, profile, variant, result, seed=variant + 1)
    report = validate(manifest["changes"], result["traces"])

    assert report.ok, (
        f"{scene_id}/{profile}/v{variant}: {report.summary()}\n" +
        "\n".join(str(f) for f in report.findings)
    )
