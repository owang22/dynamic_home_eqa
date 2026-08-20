"""Step-1 unit tests: the L2 guided-JSON schema accepts a valid program
and rejects structurally invalid ones (jsonschema is the same validator
class the build-time schema check uses)."""
from __future__ import annotations

import pytest

from revamp_v2_helpers import PERSONA, RECEPTACLES, mini_program

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
    return v2v.strip_injected(program or mini_program())


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
    lambda p: p["object_rules"][0]["rules"][1].__setitem__("p", 1.5),
    lambda p: p["arc_events"][0].__setitem__("day", 40),
    lambda p: p["weekly_blocks"][0].pop("skip_p"),
    lambda p: p["object_rules"][0].__setitem__(
        "object", "someone_elses_thing"),
    lambda p: p.__setitem__("household", "hh_other"),
])
def test_invalid_programs_fail(mutate):
    program = mini_program()
    mutate(program)
    assert v2v.check_schema(_raw(program), _schema())


def test_skip_p_bounded_by_params():
    params = sim.load_params()
    program = mini_program()
    program["weekly_blocks"][0]["skip_p"] = \
        params["skip"]["max_skip_p"] + 0.05
    assert v2v.check_schema(_raw(program), _schema())


def test_fragment_bounds():
    program = mini_program()
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
    # object that moves has a rule" is structural, not policed.
    schema = _schema()
    rules = schema["properties"]["object_rules"]
    n = len(PERSONA["object_inventory"])
    assert rules["minItems"] == rules["maxItems"] == n
    # slot i is pinned to object i: neither a duplicate nor an omission
    # is expressible, however long the inventory is
    assert [slot["oneOf"][0]["properties"]["object"]["const"]
            for slot in rules["prefixItems"]] == \
        [o["id"] for o in PERSONA["object_inventory"]]
    assert rules["items"] is False
    # ...and each entry is either "never moves" or "at least two rules":
    # a lone homing rule is not a journey.
    shapes = rules["prefixItems"][0]["oneOf"]
    assert sorted((s["properties"]["rules"].get("minItems", 0),
                   s["properties"]["rules"]["maxItems"]) for s in shapes) == \
        [(0, 0), (2, 8)]


def test_a_single_rule_for_an_object_is_unwritable():
    program = mini_program()
    program["object_rules"][0]["rules"] = program["object_rules"][0]["rules"][:1]
    assert v2v.check_schema(_raw(program), _schema())


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
    tightened = dict(base, required=base["required"] + ["arc_events"])
    t1 = prompts.ROUTINE_PROGRAM.tag("routine_program", builder=True,
                                     schema=base)
    t2 = prompts.ROUTINE_PROGRAM.tag("routine_program", builder=True,
                                     schema=tightened)
    assert t1 != t2
    assert prompts.ROUTINE_PROGRAM.tag("routine_program") != t1


def test_object_rules_must_cover_every_object():
    program = mini_program()
    program["object_rules"].pop()
    assert v2v.check_schema(_raw(program), _schema())


def test_pocket_items_may_choose_their_owner_as_home():
    """Carrying is a CHOICE, not a pin: person:<owner> is offered among the
    homes, never forced. The pinned design overshot — wallets rode their
    owners for 21 days without one put-down."""
    schema = schemas.build_program_schema(
        "hh_test", ["resident_1"], ["phone_1", "mug_1"], ["table_a", "shelf_b"],
        21, sim.load_params(),
        object_owners={"phone_1": "resident_1", "mug_1": "resident_1"},
        object_classes={"phone_1": "phone", "mug_1": "mug"})
    for slot in schema["properties"]["object_rules"]["prefixItems"]:
        # A carried class is offered ONLY the moving shape — a phone that
        # sits on one charger for three weeks is a broken household, not a
        # static object — so its slot has no `oneOf` to choose from.
        entry = slot["oneOf"][1] if "oneOf" in slot else slot
        assert "person:resident_1" in entry["properties"]["home"]["enum"]
        assert "const" not in entry["properties"]["home"]
        # journey legs stay generic: one during, one after, rest free
        phases = [x["properties"]["phase"]["const"]
                  for x in entry["properties"]["rules"]["prefixItems"]]
        assert phases == ["during", "after"]
        assert "p_misplace" not in entry["required"]


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


def test_static_shape_is_named_and_withheld_from_carried_classes():
    """`rules: []` was chosen 0 times in 180 object entries: an absence is
    not an option a generator picks, so staying put is declared positively
    as `motion: rarely_moved`. A phone is never offered that choice."""
    schema = schemas.build_program_schema(
        "hh_test", ["resident_1"], ["phone_1", "mug_1"], ["table_a", "shelf_b"],
        21, sim.load_params(),
        object_owners={"phone_1": "resident_1", "mug_1": "resident_1"},
        object_classes={"phone_1": "phone", "mug_1": "mug"})
    phone, mug = schema["properties"]["object_rules"]["prefixItems"]
    assert "oneOf" not in phone                     # no static shape at all
    static = mug["oneOf"][0]
    assert static["properties"]["motion"] == {"const": "rarely_moved"}
    assert "motion" in static["required"]
    assert "motion" not in mug["oneOf"][1]["properties"]


def test_cites_is_required_and_declared_before_the_decision():
    """Property order IS generation order under guided decoding, so a
    justification declared last is written after the choice it explains."""
    schema = schemas.build_program_schema(
        "hh_test", ["resident_1"], ["mug_1"], ["table_a", "shelf_b"],
        21, sim.load_params(),
        object_owners={"mug_1": "resident_1"}, object_classes={"mug_1": "mug"})
    entry = schema["properties"]["object_rules"]["prefixItems"][0]["oneOf"][1]
    assert list(entry["properties"])[:3] == ["object", "cites", "home"]
    rule = entry["properties"]["rules"]["prefixItems"][0]
    keys = list(rule["properties"])
    # background -> reasoning -> decision: the licence sits after the
    # activity it licenses and before every field it should inform.
    assert keys.index("activity") < keys.index("cites") < keys.index("dest")
    assert "cites" in rule["required"]
    assert keys.index("only_from") < keys.index("dest")   # from before to
    assert "only_from" in rule["required"]        # the during leg has a FROM
    after = entry["properties"]["rules"]["prefixItems"][1]
    assert "only_from" not in after["required"]   # origin implicit there
    block = schema["properties"]["weekly_blocks"]["items"]
    assert list(block["properties"])[0] == "cites"
    assert list(block["properties"]).index("sleep") < \
        list(block["properties"]).index("skip_p")
