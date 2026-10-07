"""Step-3 tests: referential + reachability checks and the leak audit
(with a stub client — no LLM needed)."""
from __future__ import annotations

import json

from revamp_v2_helpers import PERSONA, mini_program

import validate as v2v


def _referential(program):
    return v2v.check_referential(program, PERSONA)


def test_valid_program_has_no_problems():
    program = mini_program()
    assert _referential(program) == []
    assert v2v.check_reachability(program) == []


def test_placements_must_match_inventory_exactly():
    program = mini_program()
    program["object_rules"].pop()          # book_1 missing
    assert any("placements != persona inventory" in p
               for p in _referential(program))
    program = mini_program()
    program["object_rules"].append(dict(program["object_rules"][0]))
    assert any("more than once" in p for p in _referential(program))


def test_p_without_else_is_dropped_not_a_no_op_branch():
    # A `p` with no `else` resolves to `dest` either way; the expander
    # drops the branch rather than the gate rejecting the program.
    import expand_calendar as xc
    program = mini_program()
    del program["object_rules"][0]["rules"][1]["else"]
    assert _referential(program) == []
    _, motions = xc.expand(program)
    rule = motions["object_motions"]["breakfast"]["after"]["mug_1"]
    assert rule == {"dest": "sink_k", "only_from": ["table_a"]}


def test_dist_must_sum_to_one():
    program = mini_program()
    program["object_rules"][0]["rules"][1] = {
        "activity": "breakfast", "phase": "after",
        "dist": [{"dest": "sink_k", "p": 0.5}, {"dest": "shelf_b", "p": 0.3}]}
    assert any("sums to" in p for p in _referential(program))


def test_rule_on_an_activity_no_block_runs_is_dropped_and_counted():
    # The household was written with a meal the weekly pattern never
    # schedules: the rule can never fire, so it is normalized away —
    # and the object must still reach a second place on its own.
    import expand_calendar as xc
    program = mini_program()
    program["object_rules"][0]["rules"][0]["activity"] = "gym"
    assert _referential(program) == []
    acts, motions = xc.expand(program)
    assert acts["orphaned_rules"] == ["mug_1@gym"]
    assert "gym" not in motions["object_motions"]


def test_object_stranded_by_orphaned_rules_is_reported_as_inert():
    """Its rules named an activity nothing schedules, so after they are
    dropped it can no longer move — and mobility must be judged on what
    SURVIVES, or the object is left declared mobile and frozen."""
    import expand_calendar as xc
    program = mini_program()
    for r in program["object_rules"][0]["rules"]:
        r["activity"] = "gym"
    acts, motions = xc.expand(program)
    assert acts["inert_objects"] == ["mug_1"]
    assert motions["placements"]["mug_1"]["static"] is True


def test_never_moving_object_with_p_misplace_flagged():
    program = mini_program()
    program["object_rules"][1]["p_misplace"] = 0.2
    program["object_rules"][1]["misplace_set"] = ["shelf_b"]
    assert any("planned as never moving" in p for p in _referential(program))


def test_rules_must_cover_every_inventory_object():
    program = mini_program()
    program["object_rules"].pop()
    assert any("placements != persona inventory" in p or
               "object_rules covers" in p for p in _referential(program))


def test_resident_needs_a_sleep_block():
    # Structural now: the schema requires one sleep_schedule entry per
    # resident. The check remains as defence for a hand-written program.
    program = mini_program()
    program["sleep_schedule"] = []
    assert any("no sleep/nap block" in p for p in _referential(program))


def test_sleep_is_renamed_for_the_downstream_convention():
    # "lie_down" is what a model actually writes; being in
    # sleep_schedule is what makes it sleep, and the expander gives it the
    # name export_bank and the v1 simulator detect by substring.
    program = mini_program()
    program["sleep_schedule"][0]["activity"] = "lie_down"
    assert not any("no sleep/nap block" in p for p in _referential(program))
    import expand_calendar as xc
    _, motions = xc.expand(program)
    assert "sleep_lie_down" in motions["object_motions"]


def test_reserved_linger_prefix_rejected():
    program = mini_program()
    program["weekly_blocks"][1]["activity"] = "linger_table_a"
    assert any("reserved" in p for p in _referential(program))


def test_object_whose_rules_all_name_home_becomes_a_declared_static():
    """A journey that goes nowhere is immobility, and immobility must be
    declared rather than happen silently — so it is derived and REPORTED
    (`inert_objects`), not left looking alive."""
    import expand_calendar as xc
    program = mini_program()
    program["object_rules"][0]["home"] = "table_a"
    for r in program["object_rules"][0]["rules"]:
        r["dest"] = "table_a"
        r.pop("p", None); r.pop("else", None); r.pop("only_from", None)
    acts, motions = xc.expand(program)
    assert acts["inert_objects"] == ["mug_1"]
    assert motions["placements"]["mug_1"]["static"] is True
    # and its dead rules are gone, so the v1 lint's "a static appears in
    # no rule" invariant still holds
    assert "mug_1" not in motions["object_motions"]["breakfast"]["during"]


def test_a_household_of_statics_is_reported_not_rejected():
    """Static objects are welcome (a charger on its dock, grandma's
    clock); the count is surfaced by the panel and meta.json, never
    gated — an all-static home passes and the reader judges it."""
    import expand_calendar as xc
    program = mini_program()
    program["object_rules"] += [
        {"object": f"mug_{i}", "home": "shelf_b", "rules": []}
        for i in range(2, 8)]
    assert v2v.check_reachability(program) == []
    _, motions = xc.expand(program)
    statics = [o for o, pl in motions["placements"].items()
               if pl.get("static")]
    assert len(statics) >= 7          # ...but the fact is still recorded


def test_fragmented_after_rule_gets_a_derived_only_from():
    """The gate's purpose — never re-fire from your own result — is
    derivable, so an author who omits it does not lose the program."""
    import expand_calendar as xc
    program = mini_program()
    program["activities"][0]["fragment"] = {"mean_bouts": 3}
    del program["object_rules"][0]["rules"][1]["only_from"]
    assert v2v.check_reachability(program) == []
    acts, motions = xc.expand(program)
    gate = motions["object_motions"]["breakfast"]["after"]["mug_1"]["only_from"]
    # the rule can fire from anywhere EXCEPT its own two destinations
    assert "sink_k" not in gate and "table_a" not in gate
    assert "shelf_b" in gate and "bed_b1" in gate
    assert acts["derived_only_from"] == ["breakfast.mug_1"]


def test_fragment_on_sleep_is_dropped_and_counted():
    import expand_calendar as xc
    program = mini_program()
    program["activities"].append(
        {"name": "night_sleep", "fragment": {"mean_bouts": 4}})
    acts, motions = xc.expand(program)
    assert "fragment" not in motions["object_motions"]["night_sleep"]
    assert acts["dropped_sleep_fragments"] == ["night_sleep"]


class _StubClient:
    """Duck-types llm_client generate() for the leak audit."""

    def __init__(self, predicted):
        self.predicted = predicted
        self.calls = 0

    def generate(self, system, user, schema, seed=None, temperature=0.7):
        self.calls += 1
        assert "cites" not in user          # cites are never shown
        return json.dumps({"predicted_type": self.predicted,
                           "confidence": 0.5, "reason": "stub"})


TYPES = [f"type_{i}" for i in range(9)] + ["test_type"]


def test_leak_audit_rejects_correct_guess():
    program = mini_program()
    problems, record = v2v.check_leak(program, TYPES,
                                      _StubClient("test_type"), None, 1,
                                      "leak_test")
    assert problems and record["correct"] is True


def test_leak_audit_passes_wrong_guess_but_logs():
    program = mini_program()
    problems, record = v2v.check_leak(program, TYPES,
                                      _StubClient("type_3"), None, 1,
                                      "leak_test")
    assert problems == []
    assert record == {"predicted_type": "type_3", "confidence": 0.5,
                      "reason": "stub", "actual_type": "test_type",
                      "correct": False}


def test_duplicate_weekdays_flagged():
    program = mini_program()
    program["weekly_blocks"][0]["days"] = ["Mo", "Mo", "Tu"]
    assert any("repeats weekdays" in p for p in _referential(program))


def test_sleep_block_cannot_be_skipped():
    # sleep_schedule entries carry no skip_p at all; a nap in weekly_blocks
    # long enough to be the primary sleep is what this catches.
    program = mini_program()
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "day_sleep",
         "days": ["Mo"], "start": "08:00", "end": "20:00", "at": "bed_b1",
         "jitter": "routine", "skip_p": 0.3, "sleep": True,
         "cites": "night shift"})   # 12 h: this is the primary sleep
    assert any("does not skip sleeping" in p for p in _referential(program))


def test_tidy_walk_on_a_sleep_activity_is_dropped_and_counted():
    # A reset_all is a walk through the house; a sleeping resident cannot
    # take it. Normalized away (and reported), not rejected.
    import expand_calendar as xc
    program = mini_program()
    program["activities"].append(
        {"name": "night_sleep", "reset_all": {"p": 0.5}})
    assert _referential(program) == []
    acts, motions = xc.expand(program)
    assert "reset_all" not in motions["object_motions"]["night_sleep"]
    assert acts["dropped_sleep_resets"] == ["night_sleep"]


def test_drift_with_no_destination_is_normalized_away():
    # p_misplace without misplace_set describes nothing; the expander drops
    # it rather than the gate rejecting an otherwise-good program.
    import expand_calendar as xc
    program = mini_program()
    program["object_rules"][0]["p_misplace"] = 0.3      # no misplace_set
    assert _referential(program) == []
    _, motions = xc.expand(program)
    assert motions["placements"]["mug_1"] == {"home": "shelf_b"}


def test_p_misplace_alone_does_not_make_an_object_mobile():
    """The brief's reachability is "through some RULE": a program whose
    activities carry no bindings is inert, however much random drift it
    declares."""
    program = mini_program()
    # every object declares rules: [] (never moves) yet drifts constantly
    for e in program["object_rules"]:
        e["rules"] = []
    for pl in program["object_rules"]:
        pl["p_misplace"] = 0.5
        pl["misplace_set"] = ["table_a", "sink_k"]
    problems = _referential(program)
    assert any("planned as never moving" in p for p in problems)


def test_rule_moved_object_passes_reachability():
    assert v2v.check_reachability(mini_program()) == []


def test_a_nap_may_be_skipped():
    # Skippability is what makes a nap a nap; only real sleep is fixed.
    program = mini_program()
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "nap",
         "days": ["Sa"], "start": "14:00", "end": "15:00", "at": "bed_b1",
         "jitter": "loose", "skip_p": 0.4, "sleep": True, "cites": "rests"})
    assert not any("does not skip sleeping" in p for p in _referential(program))


def test_only_the_primary_sleep_is_unskippable():
    """A bedtime wind-down or a second doze is skippable; the resident's
    longest sleep is not."""
    program = mini_program()
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "bedtime_routine",
         "days": ["Mo"], "start": "20:00", "end": "20:30", "at": "bed_b1",
         "jitter": "routine", "skip_p": 0.3, "sleep": True,
         "cites": "winds down"})
    assert not any("does not skip sleeping" in p for p in _referential(program))
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "lie_down", "days": ["Tu"],
         "start": "08:00", "end": "20:00", "at": "bed_b1",
         "jitter": "routine", "skip_p": 0.2, "sleep": True, "cites": "x"})
    assert any("does not skip sleeping" in p for p in _referential(program))


def test_a_short_doze_is_never_treated_as_the_primary_sleep():
    # If the author flags only the nap, the longest sleep-flagged block is
    # an hour long — that is not the sleep the rule is protecting.
    program = mini_program()
    program["weekly_blocks"] = [b for b in program["weekly_blocks"]
                                if b["activity"] != "night_sleep"]
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "nap",
         "days": ["Mo"], "start": "14:00", "end": "15:00", "at": "bed_b1",
         "jitter": "loose", "skip_p": 0.3, "sleep": True, "cites": "dozes"})
    assert not any("does not skip sleeping" in p for p in _referential(program))


def test_declared_statics_are_welcome_however_many():
    """`rules: []` is the model saying "this stays put" — a charger on its
    dock, grandma's clock. Never gated, however many there are."""
    program = mini_program()
    program["object_rules"] += [
        {"object": f"mug_{i}", "home": "shelf_b", "rules": []}
        for i in range(2, 12)]
    assert v2v.check_reachability(program) == []


def test_rampant_fake_movement_is_rejected():
    """Rules whose every destination is the object's own home are movement
    that moves nothing. A couple are slip-ups; a houseful means the
    program is frozen by accident, and only resampling fixes it."""
    program = mini_program()
    for i in range(2, 12):                       # ten objects, all no-ops
        program["object_rules"].append(
            {"object": f"mug_{i}", "home": "shelf_b", "rules": [
                {"activity": "breakfast", "phase": "during", "dest": "shelf_b"},
                {"activity": "breakfast", "phase": "after", "dest": "shelf_b"}]})
    problems = v2v.check_reachability(program)
    assert any("only ever name their own home" in p for p in problems)


def test_a_couple_of_slip_ups_still_pass():
    program = mini_program()
    program["object_rules"] += [
        {"object": f"mug_{i}", "home": "shelf_b", "rules": [
            {"activity": "breakfast", "phase": "during", "dest": "shelf_b"},
            {"activity": "breakfast", "phase": "after", "dest": "shelf_b"}]}
        for i in range(2, 4)]                    # two, under the floor
    assert v2v.check_reachability(program) == []
