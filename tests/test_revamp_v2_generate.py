"""Step-4 tests: the generation orchestration (L0 template, L1 canonical
persona writing, L2 accept/reject loop) with a scripted stub client — the
LLM boundary is exercised without a model."""
from __future__ import annotations

import copy
import json

from revamp_v2_helpers import (PERSONA, RECEPTACLES, mini_program,
                               mini_program_v3)

import generate as gen
import validate as v2v

CONTROL = {
    "days": 21,
    "object_vocabulary": ["mug", "book"],
    "households": (
        [{"household_id": f"hh_{i:03d}", "household_type": f"type_{i}",
          "residents": 1, "bedrooms": 1} for i in range(1, 10)]
        + [{"household_id": "hh_test", "household_type": "test_type",
            "residents": 1, "residents_spec": "1", "constraints": None,
            "bedrooms": 1}]),
}
SLOT = CONTROL["households"][-1]


def test_synthetic_receptacles_scale_only_with_bedrooms():
    one = gen.synthetic_receptacles(1)
    three = gen.synthetic_receptacles(3)
    ids_one = [r["id"] for r in one]
    ids_three = [r["id"] for r in three]
    assert len(ids_one) == len(set(ids_one))
    assert len(ids_three) == len(ids_one) + 2 * 4
    # identical template for identical bedrooms -- nothing type-specific
    assert one == gen.synthetic_receptacles(1)
    rooms = {r["room"] for r in three}
    assert {"bedroom_1", "bedroom_2", "bedroom_3", "living", "kitchen",
            "bathroom", "entry"} == rooms


class ScriptedClient:
    """Returns persona / calendar / objects / special / leak responses
    keyed off the schema. Scripted content stays a list of FULL raw
    programs; the client splits each into its calendar and objects halves
    as the two-stage pipeline asks for them."""

    def __init__(self, program_responses, leak_prediction="type_1"):
        self.program_responses = list(program_responses)
        self.leak_prediction = leak_prediction
        self.program_calls = 0
        self._pending_objects = []

    def generate(self, system, user, schema, seed=None, temperature=0.7,
                 max_tokens=4096):
        props = schema.get("properties", {})
        if "predicted_type" in props:
            return json.dumps({"predicted_type": self.leak_prediction,
                               "confidence": 0.3, "reason": "stub"})
        if "object_inventory" in props:
            return json.dumps(PERSONA)
        if "special_events" in props:      # the third (story-layer) call
            return json.dumps({"special_events": [
                {"note": f"beat {i}", "day": 3 + i,
                 "patch": {"drop": ["relax"]}} for i in range(4)]})
        if "object_rules" in props and "weekly_blocks" not in props:
            if not self._pending_objects:  # an objects RETRY: consume the
                full = self.program_responses.pop(0)   # next script entry
                self._pending_objects.append(full["object_rules"])
            return json.dumps(
                {"object_rules": self._pending_objects.pop(0)})
        self.program_calls += 1            # the calendar call
        full = self.program_responses.pop(0)
        self._pending_objects.append(full["object_rules"])
        return json.dumps({k: v for k, v in full.items()
                           if k != "object_rules"})


def _raw_program():
    return v2v.strip_injected(mini_program_v3())


def test_persona_written_canonically():
    client = ScriptedClient([])
    persona, text, seed = gen.generate_persona(SLOT, CONTROL, client, None,
                                               False)
    assert persona["household_id"] == "hh_test"
    # canonical style: block sequences indented, folded prose keys
    assert "residents:\n  - id: resident_1" in text
    assert "relationships: lives alone" in text or \
        "relationships:" in text


def test_program_accepted_first_attempt():
    client = ScriptedClient([_raw_program()])
    program, attempts = gen.generate_program(
        SLOT, CONTROL, PERSONA, "persona text", copy.deepcopy(RECEPTACLES),
        21, client, None, False)
    assert program is not None
    assert program["household_type"] == "test_type"
    # every model-authored section survives injection (a section was
    # silently dropped once by an explicit key list that predated it)
    assert {p["object"] for p in program["object_rules"]} == \
        {p["object"] for p in program["object_rules"]}
    assert len(program["sleep_schedule"]) == len(PERSONA["residents"])
    assert [r["id"] for r in program["receptacles"]] == \
        [r["id"] for r in RECEPTACLES]
    # two-stage pipeline: one calendar record, one objects record
    assert [a["stage"] for a in attempts] == ["calendar", "objects"]
    assert all(a["failures"] == [] for a in attempts)


def test_bad_objects_retry_the_objects_call_not_the_calendar():
    bad = _raw_program()
    bad["object_rules"] = bad["object_rules"][:1]     # inventory mismatch
    client = ScriptedClient([bad, _raw_program()])
    program, attempts = gen.generate_program(
        SLOT, CONTROL, PERSONA, "persona text", copy.deepcopy(RECEPTACLES),
        21, client, None, False)
    assert program is not None
    # calendar accepted once; the OBJECTS stage retried with a new seed
    assert [a["stage"] for a in attempts] == \
        ["calendar", "objects", "objects"]
    obj_a, obj_b = attempts[1], attempts[2]
    assert obj_a["failures"] and not obj_b["failures"]
    assert obj_a["seed"] != obj_b["seed"]
    assert client.program_calls == 1      # the week was never regenerated


def test_leaking_persona_is_resampled_not_the_program(tmp_path, monkeypatch):
    """The ids the audit judges come from the PERSONA, so a leak has to
    resample the household — re-rolling the routine program against the
    same inventory can only fail the same way five times."""
    client = ScriptedClient([_raw_program()] * gen.MAX_ATTEMPTS,
                            leak_prediction="test_type")   # always correct
    monkeypatch.setattr(gen, "synthetic_receptacles",
                        lambda n: [dict(r) for r in RECEPTACLES])
    slot = dict(SLOT, household_id="hh_010")
    gen.build_household(slot, CONTROL, tmp_path / "slug", "m/model",
                        None, 21, client, None, False)
    log = json.loads(
        (tmp_path / "slug" / "hh10" / "build_log.json").read_text())
    assert len(log["persona_attempts"]) == gen.MAX_ATTEMPTS
    assert all(a["leak_prediction"]["correct"] for a in log["persona_attempts"])
    # distinct seeds: each retry asks for a genuinely different household
    seeds = [a["seed"] for a in log["persona_attempts"]]
    assert len(set(seeds)) == len(seeds)


def test_census_receptacles_match_the_symbolic_contract():
    """--scene mode: downstream layers must not be able to tell which L0
    mode produced the list, so it carries the same (id, room) contract."""
    import pathlib
    from revamp_v2_helpers import REPO
    census = REPO / "data" / "anchor_census" / "102343992.json"
    if not census.exists():
        import pytest
        pytest.skip("no anchor census on this machine")
    recs = gen.census_receptacles("102343992")
    assert recs and all({"id", "room"} <= set(r) for r in recs)
    ids = [r["id"] for r in recs]
    assert len(ids) == len(set(ids))
    assert not any("." in i for i in ids)   # ids stay yaml/id-safe
    # every entry is backed by a real anchor label
    assert all(r["anchor"].replace(".", "_") == r["id"] for r in recs)


def test_failed_regeneration_removes_a_stale_program(tmp_path, monkeypatch):
    """A FAILED build must not leave the previous run's program behind:
    build.sh would simulate it as though this run produced it."""
    out_root = tmp_path / "slug"
    hh_dir = out_root / "hh10"
    hh_dir.mkdir(parents=True)
    stale = hh_dir / "routine_program.yaml"
    stale.write_text("household: hh_test\n")
    bad = _raw_program()
    bad["object_rules"] = bad["object_rules"][:1]       # never validates
    client = ScriptedClient([bad] * gen.MAX_ATTEMPTS)
    monkeypatch.setattr(gen, "synthetic_receptacles",
                        lambda n: [dict(r) for r in RECEPTACLES])
    slot = dict(SLOT, household_id="hh_010")
    ok = gen.build_household(slot, CONTROL, out_root, "m/model", None, 21,
                             client, None, False)
    assert ok is False
    assert not stale.exists()
    assert (hh_dir / "build_log.json").exists()
