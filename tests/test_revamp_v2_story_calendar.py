"""The story_calendar arm — story calendar bound to the
rule_based object_rules and realized by the unchanged rules engine."""
from __future__ import annotations

from revamp_v2_helpers import mini_program

import expand_calendar as xc
import simulate as sim
import story_calendar as sr


def _story():
    """Three story days: breakfast (bound by the program's rules),
    watch_tv (in the vocab, bound by nothing — informative, not an
    error), and night_sleep in two DIFFERENT beds across residents on
    day 2 (the per-location variant split)."""
    def day(d, blocks):
        return {"day": d, "summary": f"day {d}", "blocks": blocks}
    b = [
        {"resident": "resident_1", "activity": "night_sleep",
         "start": "22:00", "end": "07:30", "at": "bed_b1"},
        {"resident": "resident_1", "activity": "breakfast",
         "start": "08:00", "end": "08:30", "at": "table_a"},
        {"resident": "resident_1", "activity": "watch_tv",
         "start": "19:00", "end": "21:00", "at": "shelf_b"},
    ]
    return [day(0, b), day(1, b), day(2, b)]


def test_synthetic_program_replaces_only_the_schedule():
    program = mini_program()
    synth = sr.story_to_arc_program(program, _story(), 3)
    assert synth["weekly_blocks"] == [] and synth["sleep_schedule"] == []
    assert synth["object_rules"] == program["object_rules"]
    assert len(synth["arc_events"]) == 3
    assert all(a["patch"]["add"] for a in synth["arc_events"])
    # the source program is not mutated
    assert program["weekly_blocks"]


def test_jitter_and_skip_join_from_the_rule_based_program():
    program = mini_program()
    program["weekly_blocks"][0]["skip_p"] = 0.3          # breakfast
    synth = sr.story_to_arc_program(program, _story(), 3)
    adds = [b for a in synth["arc_events"] for b in a["patch"]["add"]]
    bkf = [b for b in adds if b["activity"] == "breakfast"]
    assert all(b["jitter"] == "routine" and b["skip_p"] == 0.3 for b in bkf)
    tv = [b for b in adds if b["activity"] == "watch_tv"]
    assert all(b["jitter"] == "routine" and b["skip_p"] == 0.0 for b in tv)
    slp = [b for b in adds if b["activity"] == "night_sleep"]
    assert all(b["skip_p"] == 0.0 for b in slp)          # sleep never skips


def test_expansion_binds_rules_and_counts_the_join():
    program = mini_program()
    synth = sr.story_to_arc_program(program, _story(), 3)
    acts, motions = xc.expand(synth)
    # breakfast binds the program's own mug rules
    assert motions["object_motions"]["breakfast"]["during"] == \
        {"mug_1": "table_a"}
    # watch_tv realizes with no bindings — present, empty, not an error
    assert motions["object_motions"]["watch_tv"]["during"] == {}
    # the program's relax rule never fires: the story has no relax
    assert "mug_1@relax" in acts["orphaned_rules"]


def test_location_variants_split_on_story_blocks():
    program = mini_program()
    program["residents"].append({"id": "resident_2", "jitter_scale": 1.0})
    story = _story()
    story[2]["blocks"].append(
        {"resident": "resident_2", "activity": "night_sleep",
         "start": "22:00", "end": "07:30", "at": "shelf_b"})
    story[2]["blocks"].append(
        {"resident": "resident_2", "activity": "errands",
         "start": "10:00", "end": "11:00", "at": "ELSEWHERE"})
    story[2]["blocks"].append(
        {"resident": "resident_1", "activity": "errands",
         "start": "10:00", "end": "11:00", "at": "ELSEWHERE"})
    synth = sr.story_to_arc_program(program, story, 3)
    _, motions = xc.expand(synth)
    names = set(motions["object_motions"])
    # one sleep per bed: base name + a __receptacle variant
    assert "night_sleep" in names
    assert any(n.startswith("night_sleep__") for n in names)
    # going OUT splits per resident (carried things must not mix)
    assert sum(1 for n in names if n.startswith("errands")) == 2


def test_realization_runs_the_rules_engine_end_to_end():
    program = mini_program()
    synth = sr.story_to_arc_program(program, _story(), 3)
    log, hourly, blocks, stats, acts, motions = sim.simulate_program(
        synth, 3, 0)
    assert stats["blocks"] > 0
    # rule events fire on story days (mug to the breakfast table)
    assert any(e["object"] == "mug_1" and e["by"] == "activity:breakfast"
               for e in log)
    # the unbound story activity produced no events
    assert not any(e["by"] == "activity:watch_tv" for e in log)


def test_prompt_hash_is_stable_and_short():
    h = sr.story_prompt_hash()
    assert len(h) == 8 and h == sr.story_prompt_hash()


class _StubGuidedClient:
    """Guided-JSON stub for the binding pass (generate() -> payload str)."""

    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def generate(self, system, user, schema, seed=None, temperature=0.7,
                 max_tokens=4096):
        self.calls.append({"user": user, "schema": schema})
        import json
        return json.dumps(self.payload)


def test_binding_pass_targets_only_unbound_at_home_activities():
    program = mini_program()
    story = _story()   # breakfast (bound), watch_tv (unbound, at shelf_b)
    story[0]["blocks"].append(
        {"resident": "resident_1", "activity": "errands",
         "start": "10:00", "end": "11:00", "at": "ELSEWHERE"})
    client = _StubGuidedClient(
        {"bindings": [
            {"object": "mug_1", "rules": []},
            {"object": "book_1", "rules": [
                {"cites": "evenings on the couch", "activity": "watch_tv",
                 "phase": "after",
                 "dist": [{"dest": "shelf_b", "p": 0.6},
                          {"dest": "NO_OP", "p": 0.4}]}]},
        ]})
    merged, stats = sr.bind_unbound(program, story, "persona", client,
                                    None, force=True)
    schema = client.calls[0]["schema"]
    acts = schema["properties"]["bindings"]["prefixItems"][0][
        "properties"]["rules"]["items"]["properties"]["activity"]["enum"]
    assert acts == ["watch_tv"]            # not breakfast (bound),
                                           # not errands (away),
                                           # not night_sleep (sleep)
    assert stats["n_rules_added"] == 1
    # merged copy carries the new rule; the source program is untouched
    book = next(e for e in merged["object_rules"]
                if e["object"] == "book_1")
    assert any(r["activity"] == "watch_tv" for r in book["rules"])
    src_book = next(e for e in program["object_rules"]
                    if e["object"] == "book_1")
    assert not any(r.get("activity") == "watch_tv"
                   for r in (src_book.get("rules") or []))


def test_bound_story_realizes_the_new_rule():
    import expand_calendar as xc2
    program = mini_program()
    story = _story()
    client = _StubGuidedClient(
        {"bindings": [
            {"object": "mug_1", "rules": []},
            {"object": "book_1", "rules": [
                {"cites": "evenings", "activity": "watch_tv",
                 "phase": "after",
                 "dist": [{"dest": "sink_k", "p": 0.7},
                          {"dest": "shelf_b", "p": 0.3}]}]},
        ]})
    merged, _ = sr.bind_unbound(program, story, "persona", client,
                                None, force=True)
    synth = sr.story_to_arc_program(merged, story, 3)
    log, _, _, _, acts, motions = sim.simulate_program(synth, 3, 0)
    # watch_tv is no longer an empty entry, and its after rule fires
    assert "book_1" in motions["object_motions"]["watch_tv"]["after"]
    assert any(e["by"] == "activity:watch_tv" for e in log)


def test_nothing_unbound_means_no_call():
    program = mini_program()
    story = [{"day": 0, "summary": "s", "blocks": [
        {"resident": "resident_1", "activity": "breakfast",
         "start": "08:00", "end": "08:30", "at": "table_a"}]}]
    client = _StubGuidedClient({"bindings": []})
    merged, stats = sr.bind_unbound(program, story, "persona", client,
                                    None, force=True)
    assert stats["n_rules_added"] == 0 and client.calls == []
    assert merged is program


def test_binding_pass_drops_rules_that_point_at_the_objects_own_home():
    """hh1's wallet_1 got three rules all naming its own home; the
    expander then marked it inert and stripped every rule, freezing it
    for 504 h. A no-op rule must never reach the merged program."""
    program = mini_program()
    home = next(e for e in program["object_rules"]
                if e["object"] == "book_1")["home"]
    client = _StubGuidedClient(
        {"bindings": [
            {"object": "mug_1", "rules": []},
            {"object": "book_1", "rules": [
                {"cites": "put back", "activity": "watch_tv",
                 "phase": "after",                          # all real mass
                 "dist": [{"dest": home, "p": 0.7},         # points home:
                          {"dest": "NO_OP", "p": 0.3}]},    # fake movement
                {"cites": "left out", "activity": "watch_tv",
                 "phase": "after",                          # real journey
                 "dist": [{"dest": "sink_k", "p": 0.5},
                          {"dest": home, "p": 0.5}]},       # home as ONE
            ]},                                             # outcome is ok
        ]})
    merged, stats = sr.bind_unbound(program, _story(), "persona", client,
                                    None, force=True)
    assert stats["n_rules_added"] == 1
    assert stats["n_dropped_noop_rules"] == 1
    book = next(e for e in merged["object_rules"] if e["object"] == "book_1")
    kept = [r for r in book["rules"] if r.get("activity") == "watch_tv"]
    assert len(kept) == 1                          # the all-home rule is gone
    assert any(d["dest"] != home for d in kept[0]["dist"])


def test_binding_prompt_lives_in_the_registry_after_only():
    """One source of truth: the binding prompt is prompts.BINDING (the
    registry), no inline copy in this module; and the schema makes
    `during` unwritable rather than advising against it."""
    import prompts as _prompts
    assert not hasattr(sr, "BIND_SYSTEM")
    assert "person:<resident_id>" in _prompts.BINDING.text
    assert "after" in _prompts.BINDING.text
    schema = sr.build_binding_schema(["mug_1"], ["watch_tv"],
                                     ["table_a"], ["resident_1"])
    phase = schema["properties"]["bindings"]["prefixItems"][0][
        "properties"]["rules"]["items"]["properties"]["phase"]
    assert phase == {"const": "after"}
