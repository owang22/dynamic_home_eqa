"""The dataset pipeline, end to end with a scripted client and no API:
persona -> story -> movement -> realized timeline, plus the trip-merge
helper and the story schema's structural guarantees."""
from __future__ import annotations

import json
import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
for p in (REPO / "src", REPO / "src" / "revamp_v2"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from revamp_v2_helpers import PERSONA  # noqa: E402

import generate_dataset as sf  # noqa: E402

# The real persona schema demands >= 8 inventory objects; pad the shared
# 2-object fixture with declared statics (rules: [] downstream).
FILLER = [{"id": f"book_{i}", "class": "book", "owner": "resident_1",
           "role": "shelf filler"} for i in range(2, 8)]
PERSONA8 = dict(PERSONA,
                object_inventory=PERSONA["object_inventory"] + FILLER)

SLOT = {"household_id": "hh_test", "household_type": "test_type",
        "residents": 1, "residents_spec": "1", "constraints": None,
        "bedrooms": 1}
CONTROL = {"days": 3, "object_vocabulary": ["mug", "book"],
           "households": [SLOT]}
DAYS = 3

# One resident's day: 8 blocks (the schema floor), with a commute-errand
# chain so the trip merge and carried-object mechanics are exercised.
def _day(i):
    return {"day": i, "summary": f"day {i}",
            "blocks": [
                {"resident": "resident_1", "activity": "night_sleep",
                 "start": "22:30", "end": "06:30", "at": "bed_b1"},
                {"resident": "resident_1", "activity": "wake_up",
                 "start": "06:30", "end": "06:45", "at": "bed_b1"},
                {"resident": "resident_1", "activity": "breakfast",
                 "start": "06:45", "end": "07:15", "at": "kitchen_table_k1"},
                {"resident": "resident_1", "activity": "traveling",
                 "start": "07:15", "end": "07:45", "at": "ELSEWHERE"},
                {"resident": "resident_1", "activity": "errands",
                 "start": "07:45", "end": "12:00", "at": "ELSEWHERE"},
                {"resident": "resident_1", "activity": "traveling",
                 "start": "12:00", "end": "12:30", "at": "ELSEWHERE"},
                {"resident": "resident_1", "activity": "dinner",
                 "start": "18:00", "end": "19:00", "at": "kitchen_table_k1"},
                {"resident": "resident_1", "activity": "relax",
                 "start": "19:00", "end": "22:00", "at": "couch_l1"},
            ]}


MOVEMENT_RESPONSE = {"reasoning": "walk the day", "object_rules": [
    {"object": "mug_1", "cites": "coffee at breakfast",
     "home": "counter_k1", "p_misplace": 0.1, "rules": [
         {"cites": "breakfast mug", "activity": "breakfast",
          "phase": "after",
          "dist": [{"dest": "sink_k1", "p": 0.6},
                   {"dest": "NO_OP", "p": 0.4}]},
         {"cites": "travel mug rides along", "activity": "errands",
          "phase": "after",
          "dist": [{"dest": "counter_k1", "p": 0.8},
                   {"dest": "sink_k1", "p": 0.2}]},
         {"cites": "evening tea", "activity": "dinner", "phase": "after",
          "dist": [{"dest": "sink_k1", "p": 0.5},
                   {"dest": "NO_OP", "p": 0.5}]}]},
    {"object": "book_1", "cites": "evening reading",
     "home": "bookshelf_l1", "rules": [
         {"cites": "set down after reading", "activity": "relax",
          "phase": "after",
          "dist": [{"dest": "coffee_table_l1", "p": 0.5},
                   {"dest": "bookshelf_l1", "p": 0.3},
                   {"dest": "NO_OP", "p": 0.2}]},
         {"cites": "morning page", "activity": "wake_up", "phase": "after",
          "dist": [{"dest": "nightstand_b1", "p": 0.5},
                   {"dest": "NO_OP", "p": 0.5}]}]},
] + [{"object": f"book_{i}", "cites": "stays on the shelf",
      "home": "bookshelf_l1", "rules": []} for i in range(2, 8)]}


class ScriptedHostedClient:
    """Duck-types HostedOpenAIClient for offline builds: routes by
    schema shape, satisfies every schema it is shown."""
    hosted = True
    snapshot = "scripted"

    class _Guard:
        def summary(self):
            return "offline"

    def __init__(self):
        self.guard = self._Guard()
        self.last_meta = {"finish_reason": "stop",
                          "usage": {"prompt_tokens": 1,
                                    "completion_tokens": 1},
                          "model_snapshot": "scripted", "cost_usd": 0.0}
        self.calls = []

    def generate(self, system, user, schema, seed=None, temperature=0.7,
                 max_tokens=4096):
        props = schema.get("properties", {})
        if "object_inventory" in props:
            out = dict(PERSONA8, reasoning="a household")
            # schema minLength 2 on names; the shared fixture says "T"
            out["residents"] = [dict(r, name="Tess")
                                for r in out["residents"]]
            kind = "persona"
        elif "object_rules" in props:
            kind, out = "movement", MOVEMENT_RESPONSE
        else:
            kind, out = "story", {"days": [_day(i) for i in range(DAYS)]}
        self.calls.append(kind)
        return json.dumps(out)


def test_trip_merge_names_the_dominant_leg():
    story = [_day(0)]
    at_home, trips = sf.effective_activities(story)
    # traveling(30m) -> errands(4h15) -> traveling(30m): one trip, named
    # for the dominant member, commute never survives
    assert trips == {"errands"}
    assert "traveling" not in at_home | trips
    assert {"wake_up", "breakfast", "dinner", "relax"} <= at_home
    assert "night_sleep" not in at_home


def test_month_schema_pins_every_day_and_the_block_floor():
    schema = sf.build_story_schema("resident_1", ["bed_b1"], 5)
    days = schema["properties"]["days"]
    assert (days["minItems"], days["maxItems"]) == (5, 5)
    assert [s["properties"]["day"]["const"]
            for s in days["prefixItems"]] == [0, 1, 2, 3, 4]
    blocks = days["prefixItems"][0]["properties"]["blocks"]
    assert (blocks["minItems"], blocks["maxItems"]) == (8, 18)
    # ...and the hosted transform accepts it (idempotent, prefixItems kept)
    from dynamic_home_eqa.generation.hosted_schema import to_hosted_schema
    h1, _ = to_hosted_schema(schema)
    h2, rem2 = to_hosted_schema(h1)
    assert rem2 == [] and "prefixItems" in json.dumps(h1)


def test_end_to_end_offline_build(tmp_path, monkeypatch):
    """persona -> story -> movement -> realized timeline, no API: the
    carried mug rides the errand trip and lands back home, events flow
    from at-home rules and drift, provenance is logged."""
    client = ScriptedHostedClient()
    ok = sf.build_household(SLOT, CONTROL, tmp_path, "scripted-model",
                            DAYS, 0, client, cache=None, force=True)
    assert ok
    hh = tmp_path / "hh0"    # hh_test -> int('test'.strip digits) ...
    # household_id hh_test has no digits; directory name derived from it
    dirs = list(tmp_path.iterdir())
    hh = [d for d in dirs if d.is_dir()][0]
    for name in ("persona.yaml", "story.yaml", "object_movement.yaml",
                 "program.yaml", "build_log.json"):
        assert (hh / name).exists(), name
    events = [json.loads(l) for l in
              (hh / "timeline_seed0" / "events.jsonl").read_text()
              .splitlines()]
    assert events, "realization produced no events"
    mug = [e for e in events if e["object"] == "mug_1"]
    assert mug, "the carried mug never moved"
    # the trip rule fired: some mug event is caused by the errands trip
    assert any("errands" in e.get("by", "") for e in mug), \
        [e.get("by") for e in mug][:6]
    meta = json.loads((hh / "timeline_seed0" / "meta.json").read_text())
    assert meta["engine"] == "storyfirst"
    assert meta["effective_trips"] == ["errands"]
    assert meta["uncovered_at_home"] == []
    log = json.loads((hh / "build_log.json").read_text())
    assert [c for c in client.calls] == ["persona", "story", "movement"]
    assert log["movement_attempts"][-1]["failures"] == []
