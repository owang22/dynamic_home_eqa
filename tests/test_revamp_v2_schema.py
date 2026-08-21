"""Step-1 unit tests: the L2 guided-JSON schema accepts a valid program
and rejects structurally invalid ones (jsonschema is the same validator
class the build-time schema check uses)."""
from __future__ import annotations

import pytest

from revamp_v2_helpers import (PERSONA, RECEPTACLES, mini_program,
                               mini_program_v3)

import prompts
import schemas
import simulate as sim
import validate as v2v


def _schema():
    params = sim.load_params()
    return schemas.build_program_schema(
        "hh_test",
        [r["id"] for r in PERSONA["residents"]],
        [o["id"] for o in PERSONA["object_inventory"]],
        [r["id"] for r in RECEPTACLES],
        21, params)


def _raw(program=None):
    return v2v.strip_injected(program or mini_program_v3())


def test_valid_program_passes():
    assert v2v.check_schema(_raw(), _schema()) == []


def test_injected_keys_are_not_schema_keys():
    # The injected form (receptacles/household_type) must NOT pass: those
    # fields are pipeline data the model never authors.
    assert v2v.check_schema(mini_program(), _schema())


@pytest.mark.parametrize("mutate", [
    lambda p: p["object_rules"][0].__setitem__("home", "no_such_receptacle"),
    lambda p: p["weekly_blocks"][0]["days"].append("Xx"),
    lambda p: p["weekly_blocks"][0].__setitem__("start", "25:00"),
    lambda p: p["weekly_blocks"][0].__setitem__("jitter", "wobbly"),
    lambda p: p["residents"][0].__setitem__("jitter_scale", 3.0),
    lambda p: p["object_rules"][0]["rules"][0]["dist"][0]
        .__setitem__("p", 1.5),
    lambda p: p["object_rules"][0]["rules"][0].__setitem__(
        "phase", "during"),                 # during is UNWRITABLE now
    lambda p: p["object_rules"][0]["rules"][0].__setitem__(
        "dest", "sink_k"),                  # bare dest is unwritable too
    lambda p: p["weekly_blocks"][0].pop("skip_p"),
    lambda p: p["object_rules"][0].__setitem__(
        "object", "someone_elses_thing"),
    lambda p: p.__setitem__("household", "hh_other"),
])
def test_invalid_programs_fail(mutate):
    program = mini_program_v3()
    mutate(program)
    assert v2v.check_schema(_raw(program), _schema())


def test_skip_p_bounded_by_params():
    params = sim.load_params()
    program = mini_program_v3()
    program["weekly_blocks"][0]["skip_p"] = \
        params["skip"]["max_skip_p"] + 0.05
    assert v2v.check_schema(_raw(program), _schema())


def test_fragment_bounds():
    program = mini_program_v3()
    program["activities"][0]["fragment"] = {"mean_bouts": 99}
    assert v2v.check_schema(_raw(program), _schema())
    program["activities"][0]["fragment"] = {"mean_bouts": 3}
    assert not any("fragment" in e
                   for e in v2v.check_schema(_raw(program), _schema()))


def test_prompt_versions_are_content_hashes():
    p1 = prompts.PromptTemplate("x", "hello")
    p2 = prompts.PromptTemplate("x", "hello!")
    assert p1.version != p2.version
    assert prompts.PERSONA.tag("persona", builder=True).endswith(
        prompts.BUILDER_VERSION)


def test_rules_are_keyed_by_object_so_none_can_be_forgotten():
    # The array carries exactly one entry per inventory object: "every
    # object's fate is decided" is structural, not policed. One shape per
    # object now — the static/mobile oneOf died with `motion`: staying
    # put is NO_OP mass, a probability statement, not a special case.
    schema = _schema()
    rules = schema["properties"]["object_rules"]
    n = len(PERSONA["object_inventory"])
    assert rules["minItems"] == rules["maxItems"] == n
    assert [slot["properties"]["object"]["const"]
            for slot in rules["prefixItems"]] == \
        [o["id"] for o in PERSONA["object_inventory"]]
    assert rules["items"] is False
    entry = rules["prefixItems"][0]
    assert "oneOf" not in entry and "motion" not in entry["properties"]
    assert entry["properties"]["rules"]["maxItems"] == 8


def test_rules_are_after_only_dists_with_noop():
    """The v3 grammar: `during` and bare `dest` are unwritable (the
    object is with the resident while the activity runs — the expander
    synthesizes that leg), every outcome is a dist, and NO_OP is a
    first-class member of it."""
    schema = _schema()
    rule = schema["properties"]["object_rules"]["prefixItems"][0][
        "properties"]["rules"]["items"]
    assert rule["properties"]["phase"] == {"const": "after"}
    assert "dest" not in rule["properties"]
    assert "p" not in rule["properties"] and "else" not in rule["properties"]
    assert "dist" in rule["required"]
    dest_enum = rule["properties"]["dist"]["items"]["properties"]["dest"][
        "enum"]
    assert "NO_OP" in dest_enum
    assert "misplace_set" not in schema["properties"]["object_rules"][
        "prefixItems"][0]["properties"]      # drift spot is derived now


def test_calendar_table_maps_days_to_weekdays():
    table = prompts.calendar_table(21)
    assert "day  0 = Mon (Mo)" in table
    assert "day  6 = Sun (Su)" in table
    assert "day 20 = Sun (Su)" in table
    assert "day 21" not in table


def test_program_prompt_carries_the_calendar():
    text = prompts.program_user_prompt("persona", RECEPTACLES, 21, "Monday")
    assert "day  5 = Sat (Sa)" in text
    assert all(r["id"] in text for r in RECEPTACLES)


def test_tag_changes_when_the_schema_changes():
    # A tightened schema must not replay responses sampled under the old
    # one: seeds derive from the tag, so the schema hash belongs in it.
    base = _schema()
    tightened = dict(base, required=base["required"] + ["extra_field"])
    t1 = prompts.CALENDAR.tag("calendar", builder=True, schema=base)
    t2 = prompts.CALENDAR.tag("calendar", builder=True, schema=tightened)
    assert t1 != t2
    assert prompts.CALENDAR.tag("calendar") != t1
    # the pinned objects schema differs per calendar, so its tag does too
    import simulate as _sim
    o1 = schemas.build_objects_schema("hh_test", ["resident_1"], ["mug_1"],
                                      ["table_a"], 21, _sim.load_params(),
                                      ["breakfast"])
    o2 = schemas.build_objects_schema("hh_test", ["resident_1"], ["mug_1"],
                                      ["table_a"], 21, _sim.load_params(),
                                      ["breakfast", "relax"])
    assert prompts.OBJECT_RULES.tag("object_rules", schema=o1) != \
        prompts.OBJECT_RULES.tag("object_rules", schema=o2)


def test_object_rules_must_cover_every_object():
    program = mini_program_v3()
    program["object_rules"].pop()
    assert v2v.check_schema(_raw(program), _schema())


def test_pocket_items_may_choose_their_owner_as_home():
    """Carrying is a CHOICE, not a pin: person:<owner> is offered among
    the homes (and among every dist's destinations), never forced."""
    schema = schemas.build_program_schema(
        "hh_test", ["resident_1"], ["phone_1", "mug_1"], ["table_a", "shelf_b"],
        21, sim.load_params())
    for slot in schema["properties"]["object_rules"]["prefixItems"]:
        assert "person:resident_1" in slot["properties"]["home"]["enum"]
        assert "const" not in slot["properties"]["home"]
        dests = slot["properties"]["rules"]["items"]["properties"]["dist"][
            "items"]["properties"]["dest"]["enum"]
        assert "person:resident_1" in dests
        assert "p_misplace" not in slot["required"]


def test_residents_and_their_sleep_are_pinned_per_slot():
    """A five-person household came back as [r1, r1, r1, r2, r2] — the
    right length with three people missing — and its sleep schedule the
    same way. Pinning slot i to resident i makes that unwritable, exactly
    as object_rules pins slot i to object i."""
    ids = ["resident_1", "resident_2", "resident_3", "resident_4"]
    schema = schemas.build_program_schema(
        "hh_test", ids, ["mug_1"], ["table_a"], 21, sim.load_params())
    residents = schema["properties"]["residents"]
    sleep = schema["properties"]["sleep_schedule"]
    assert [s["properties"]["id"]["const"] for s in residents["prefixItems"]] == ids
    assert [s["properties"]["resident"]["const"]
            for s in sleep["prefixItems"]] == ids
    for arr in (residents, sleep):
        assert arr["items"] is False          # no extra, no substitutions
        assert arr["minItems"] == arr["maxItems"] == len(ids)


def test_pure_noop_dist_is_flagged_by_referential():
    """`motion: rarely_moved` retired: staying put is heavy NO_OP mass.
    A dist that is ENTIRELY NO_OP is a rule that never does anything —
    the schema cannot forbid it (cross-entry arithmetic), so referential
    names it instead of letting the expander thin it silently."""
    program = mini_program_v3()
    program["object_rules"][0]["rules"][1]["dist"] = [
        {"dest": "NO_OP", "p": 0.5}, {"dest": "NO_OP", "p": 0.5}]
    problems = v2v.check_referential(program, PERSONA)
    assert any("pure NO_OP" in p for p in problems)


def test_cites_is_required_and_declared_before_the_decision():
    """Property order IS generation order under guided decoding, so a
    justification declared last is written after the choice it explains."""
    schema = schemas.build_program_schema(
        "hh_test", ["resident_1"], ["mug_1"], ["table_a", "shelf_b"],
        21, sim.load_params())
    entry = schema["properties"]["object_rules"]["prefixItems"][0]
    assert list(entry["properties"])[:3] == ["object", "cites", "home"]
    rule = entry["properties"]["rules"]["items"]
    keys = list(rule["properties"])
    # background -> reasoning -> decision: the licence first, then the
    # activity it licenses, then the outcome distribution it informs.
    assert keys.index("cites") < keys.index("activity") < keys.index("dist")
    assert "cites" in rule["required"]
    block = schema["properties"]["weekly_blocks"]["items"]
    assert list(block["properties"])[0] == "cites"
    assert list(block["properties"]).index("sleep") < \
        list(block["properties"]).index("skip_p")


def test_special_schema_pins_drop_to_the_scheduled_calendar():
    """Special events are a second call, conditioned on the accepted
    program: `drop` is grammar-pinned to activities that actually run —
    the single largest historical source of rejected programs (unknown /
    vacuous drops) becomes unwritable — while `add` keeps the full vocab
    (an exception the routine never runs is the point)."""
    schema = schemas.build_special_schema(
        21, ["breakfast", "relax"], ["resident_1"], ["table_a"],
        ["mug_1"], {})
    ev = schema["properties"]["special_events"]["items"]
    patch = ev["properties"]["patch"]["properties"]
    assert patch["drop"]["items"]["enum"] == ["breakfast", "relax"]
    assert patch["add"]["items"]["properties"]["activity"]["enum"] == \
        prompts.ACTIVITY_VOCAB
    assert ev["properties"]["day"]["maximum"] == 20
    dests = patch["after_override"]["items"]["properties"]["rule"][
        "properties"]["dist"]["items"]["properties"]["dest"]["enum"]
    assert "NO_OP" in dests
