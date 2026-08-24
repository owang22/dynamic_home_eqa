"""Hosted-generation pilot, Task 2 guarantees, one test each:
to_hosted_schema() is idempotent; its output validates the same instances
the original accepted (round-trip of a committed routine_program.yaml and
a committed story.yaml through both forms); and the calendar stage's
local qwen path still builds a byte-identical request body. No live API
calls."""
from __future__ import annotations

import json
import pathlib
import sys

import jsonschema
import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
for p in (REPO / "src", REPO / "src" / "revamp_v2"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import schemas  # noqa: E402
import simulate as sim  # noqa: E402
import story_driven as sd  # noqa: E402

from dynamic_home_eqa.generation.hosted_schema import (  # noqa: E402
    drop_nulls, to_hosted_schema)

HH4 = REPO / "profiles" / "revamp_v2" / "rule_based" / "qwen3.8-27b" / "hh4"
HH4_STORY = (REPO / "profiles" / "revamp_v2" / "story_calendar"
             / "qwen3.8-27b" / "hh4")


def hostedize_instance(schema: dict, instance):
    """What a strict-mode model must emit for `instance`: every schema
    property present, absent optionals as null. Test-only helper."""
    if isinstance(schema.get("prefixItems"), list) and \
            isinstance(instance, list):
        return [hostedize_instance(s, v)
                for s, v in zip(schema["prefixItems"], instance)]
    if isinstance(schema.get("items"), dict) and isinstance(instance, list):
        return [hostedize_instance(schema["items"], v) for v in instance]
    props = schema.get("properties")
    if isinstance(props, dict) and isinstance(instance, dict):
        return {k: (hostedize_instance(props[k], instance[k])
                    if k in instance else None)
                for k in props}
    return instance


def _real_schemas():
    """The pilot household's actual contracts, sized from the committed
    qwen build (same construction the probe uses)."""
    control = yaml.safe_load((sim.PROFILES_DIR / "control.yaml").read_text())
    slot = next(h for h in control["households"]
                if h["household_id"] == "hh_004")
    persona = yaml.safe_load((HH4 / "persona.yaml").read_text())
    program = yaml.safe_load((HH4 / "routine_program.yaml").read_text())
    params = sim.load_params()
    residents = [r["id"] for r in persona["residents"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    object_ids = [o["id"] for o in persona["object_inventory"]]
    scheduled = sorted({b["activity"]
                        for b in (program.get("sleep_schedule") or [])
                        + program["weekly_blocks"]})
    days = int(program["days"])
    return {
        "persona": schemas.build_persona_schema(
            slot["household_id"], slot["household_type"],
            int(slot["residents"]), control["object_vocabulary"]),
        "calendar": schemas.build_calendar_schema(
            slot["household_id"], residents, receptacles, days, params),
        "objects": schemas.build_objects_schema(
            slot["household_id"], residents, object_ids, receptacles,
            days, params, scheduled),
        "special": schemas.build_special_schema(
            days, scheduled, residents, receptacles, object_ids, params),
        "story": sd.build_story_schema(residents, receptacles, 0, 0),
    }, persona, program


def test_transform_idempotent_on_every_real_schema():
    all_schemas, _, _ = _real_schemas()
    for name, schema in all_schemas.items():
        h1, _ = to_hosted_schema(schema)
        h2, rem2 = to_hosted_schema(h1)
        assert json.dumps(h1, sort_keys=True) == \
            json.dumps(h2, sort_keys=True), name
        assert rem2 == [], (name, rem2)


def test_roundtrip_committed_routine_program():
    """The committed hh4 program, split back into the raw responses the
    two L2 schemas accepted: each must validate under the ORIGINAL
    schema, its hostedized form (absent optionals as null) under the
    TRANSFORMED schema, and drop_nulls must invert the hostedization."""
    all_schemas, _, program = _real_schemas()
    cal_raw = {"reasoning": "x"}
    cal_raw.update({k: program[k] for k in
                    ("household", "source_persona", "days", "day0",
                     "residents", "sleep_schedule", "weekly_blocks",
                     "activities")})
    obj_raw = {"reasoning": "x", "object_rules": program["object_rules"]}
    for name, schema, raw in (("calendar", all_schemas["calendar"], cal_raw),
                              ("objects", all_schemas["objects"], obj_raw)):
        jsonschema.validate(raw, schema)          # original accepts it
        hosted_schema, _ = to_hosted_schema(schema)
        hosted_raw = hostedize_instance(schema, raw)
        jsonschema.validate(hosted_raw, hosted_schema)
        assert drop_nulls(hosted_raw) == raw, name


def test_roundtrip_committed_story():
    _, persona, program = _real_schemas()
    residents = [r["id"] for r in persona["residents"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    story = yaml.safe_load((HH4_STORY / "story.yaml").read_text())["days"]
    assert story, "committed story is empty"
    for day in story[:5]:
        schema = sd.build_story_schema(residents, receptacles,
                                       day["day"], day["day"])
        raw = {"days": [day]}
        jsonschema.validate(raw, schema)
        hosted_schema, _ = to_hosted_schema(schema)
        hosted_raw = hostedize_instance(schema, raw)
        jsonschema.validate(hosted_raw, hosted_schema)
        assert drop_nulls(hosted_raw) == raw


def test_story_local_thinking_body_byte_identical(monkeypatch):
    """Task 1.6's qwen-path guarantee: with a NON-hosted client,
    generate_story_json still routes through _thinking_call and builds
    exactly the body it always built (values AND key order)."""
    from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient
    client = OpenAIHTTPClient("http://127.0.0.1:8300", "qwen")
    day = {"day": 0, "summary": "s",
           "blocks": [{"resident": "r1", "activity": "wake_up",
                       "start": "07:00", "end": "07:10", "at": "bed"}]}
    captured = {}

    def fake_post_chat(body):
        captured["body"] = body
        return {"choices": [{
            "message": {"content": json.dumps({"days": [day]}),
                        "reasoning_content": "thought"},
            "finish_reason": "stop"}]}

    monkeypatch.setattr(client, "_post_chat", fake_post_chat)
    monkeypatch.setattr(sd, "_served_max_model_len", lambda c: None)
    out = sd.generate_story_json(
        client, "sys", "usr", seed=100, stage="t", max_tokens=5000,
        schema={"type": "object", "required": ["days"],
                "properties": {"days": {"type": "array"}}})
    assert out == {"days": [day]}
    golden = {
        "model": "qwen",
        "messages": [{"role": "system", "content": "sys"},
                     {"role": "user", "content": "usr"}],
        "temperature": 0.6, "top_p": 0.95, "max_tokens": 5000,
        "chat_template_kwargs": {"enable_thinking": True},
        "seed": 100,
    }
    assert captured["body"] == golden
    assert list(captured["body"].keys()) == list(golden.keys())


def test_widened_story_schema_keeps_the_narrow_array_length():
    """The hosted story path sends a day-widened schema so every call of
    a household presents one identical grammar (prompt-cache). Widening
    must relax the day INDEX only: rebuilding the schema over the full
    range instead moves minItems/maxItems to 21 and demands 21 days per
    call — every response then failed the narrow validator at ~10x the
    cost per call (measured on a real run, not hypothetically)."""
    narrow = sd.build_story_schema(["r1", "r2"], ["bed", "desk"], 15, 15)
    wide = sd.widen_day_bounds(narrow, 0, 20)
    n_days, w_days = narrow["properties"]["days"], wide["properties"]["days"]
    assert (w_days["minItems"], w_days["maxItems"]) == \
           (n_days["minItems"], n_days["maxItems"]) == (1, 1)
    assert w_days["items"]["properties"]["day"]["minimum"] == 0
    assert w_days["items"]["properties"]["day"]["maximum"] == 20
    # ...and a one-day response valid under narrow stays valid under wide
    day = {"day": 15, "summary": "s",
           "blocks": [{"resident": "r1", "activity": "wake_up",
                       "start": "07:00", "end": "07:10", "at": "bed"}]}
    jsonschema.validate({"days": [day]}, narrow)
    jsonschema.validate({"days": [day]}, wide)
    # the widened schema must NOT admit a different length
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"days": [day, dict(day, day=16)]}, wide)
