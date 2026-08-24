"""The v3 object semantics end to end: after-only dists with NO_OP,
synthesized during legs (the object is WITH the resident while the
activity runs), derived misplace spots — all gated on the
`object_semantics: after_only_v3` marker so every unmarked program (and
the v1 regression fixture) realizes exactly as before."""
from __future__ import annotations

import collections

from revamp_v2_helpers import PERSONA, mini_program, mini_program_v3

import expand_calendar as xc
import simulate as sim
import validate as v2v


def _v3():
    return mini_program_v3(object_semantics=xc.AFTER_ONLY_V3)


def test_v3_program_passes_the_static_checks():
    program = _v3()
    assert v2v.check_referential(program, PERSONA) == []
    assert v2v.check_reachability(program) == []


def test_noop_mass_is_lifted_out_and_dist_renormalized():
    r = xc._rule_to_v1({"dist": [{"dest": "NO_OP", "p": 0.6},
                                 {"dest": "sink_k", "p": 0.3},
                                 {"dest": "table_a", "p": 0.1}]})
    assert abs(r["noop_p"] - 0.6) < 1e-6
    assert abs(sum(r["dist"].values()) - 1.0) < 1e-6
    assert xc._rule_to_v1({"dist": [{"dest": "NO_OP", "p": 1.0},
                                    {"dest": "NO_OP", "p": 0.0}]}) is None


def test_during_leg_is_synthesized_only_under_the_marker():
    # unmarked: after-only rules get NO during leg (old behaviour)
    _, plain = xc.expand(mini_program_v3())
    assert plain["object_motions"]["breakfast"]["during"] == {}
    # marked: the mug is WITH the resident at the breakfast table
    _, v3 = xc.expand(_v3())
    assert v3["object_motions"]["breakfast"]["during"] == {"mug_1": "table_a"}
    # ...but NOT for the NO_OP-heavy relax rule (usually untouched)
    assert v3["object_motions"]["relax"]["during"] == {}
    assert "mug_1@breakfast" in \
        xc.expand(_v3())[0]["synthesized_during"]


def test_misplace_spots_are_derived_from_occupied_rooms():
    _, plain = xc.expand(mini_program_v3())
    # unmarked: p_misplace with no authored set is dropped (old rule)
    assert "p_misplace" not in plain["placements"]["mug_1"]
    _, v3 = xc.expand(_v3())
    pl = v3["placements"]["mug_1"]
    assert pl["p_misplace"] == 0.1
    # candidate spots: receptacles in rooms the household occupies
    # (table_a/bed_b1 via blocks -> living+bedroom), minus the home
    assert set(pl["misplace_set"]) == {"table_a", "bed_b1"}


def test_v3_realizes_and_noop_suppresses_moves():
    program = _v3()
    log, hourly, blocks, stats, acts, motions = sim.simulate_program(
        program, 21, 0)
    by_act = collections.Counter(e["by"] for e in log)
    # the synthesized during leg fires (mug to the table at breakfast)
    assert any(e["object"] == "mug_1" and e["to"] == "table_a"
               and e["by"] == "activity:breakfast" for e in log)
    # relax fires far fewer moves than its 21 scheduled days: 0.8 of its
    # mass is NO_OP (drops on days 3/8/9 also thin it slightly)
    assert by_act.get("activity:relax", 0) < 10
    sim.tag_event_kinds(log)
    assert all("kind" in e for e in log)
    # any misplace drift lands only on the DERIVED spots
    assert all(e["to"] in ("table_a", "bed_b1")
               for e in log if e["kind"] == "misplace")


def test_regression_fixture_is_untouched_by_v3_machinery():
    """The whole point of the marker: identical byte behaviour for
    unmarked programs is asserted (again) by the byte-for-byte regression
    suite; here we pin that the marker itself is what gates the change."""
    p_old = mini_program()
    acts, motions = xc.expand(p_old)
    assert "synthesized_during" in acts and acts["synthesized_during"] == []


def test_three_way_dist_survives_v1_tolerance():
    """round(1/3, 6) * 3 = 0.999999 fails v1 validate's `< 1e-6` check
    exactly at the boundary — hh2's toy_1 lost a 2-hour build to it. No
    per-entry rounding: the renormalized dist must sum to 1 in float."""
    r = xc._rule_to_v1({"dist": [{"dest": "a", "p": 1}, {"dest": "b", "p": 1},
                                 {"dest": "c", "p": 1}]})
    assert abs(sum(r["dist"].values()) - 1.0) < 1e-9
    r = xc._rule_to_v1({"dist": [{"dest": "NO_OP", "p": 0.25},
                                 {"dest": "a", "p": 0.25},
                                 {"dest": "b", "p": 0.25},
                                 {"dest": "c", "p": 0.25}]})
    assert abs(sum(r["dist"].values()) - 1.0) < 1e-9


def test_away_chain_merges_so_things_come_home_once():
    """hh1's keys jumped off their owner at 20:18 (commute_out's end) and
    sat on the entry hook through a night shift, because work_away
    followed. Consecutive away blocks merge into one, so the after-rule
    fires at the real homecoming."""
    program = _v3()
    program["weekly_blocks"] = [
        {"resident": "resident_1", "activity": "commute_out",
         "days": ["Mo"], "start": "08:00", "end": "08:30", "at": "ELSEWHERE",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"},
        {"resident": "resident_1", "activity": "work_away",
         "days": ["Mo"], "start": "08:30", "end": "17:00", "at": "ELSEWHERE",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"},
        {"resident": "resident_1", "activity": "relax",
         "days": ["Mo"], "start": "17:00", "end": "21:00", "at": "table_a",
         "jitter": "flexible", "skip_p": 0.0, "sleep": False, "cites": "c"},
    ]
    program["object_rules"][0]["rules"] = [
        {"cites": "c", "activity": "commute_out", "phase": "after",
         "dist": [{"dest": "shelf_b", "p": 0.5}, {"dest": "sink_k", "p": 0.5}]}]
    acts, motions = xc.expand(program)
    merged = acts["merged_away_blocks"]
    assert merged                        # the chain merged into one trip
    # Only ONE away block survives per trip, per day — named for the
    # DOMINANT member (the trip's reason: eight hours of work_away, not
    # the half-hour commute that begins it), starting at the commute's
    # own start (the true departure).
    mon = [e for e in acts["calendar"] if e["weekday"] == "Mon"]
    away = [i for d in mon for i in d["activities"]
            if i["a"].startswith(("commute_out", "work_away"))]
    assert away and all(i["a"].startswith("work_away") for i in away)
    assert away[0]["t"] == "08:00"
    # ...and the commute's OWN after-rule still fires at the homecoming:
    # the chain union attaches every member's rules to the survivor.
    entry = motions["object_motions"]["work_away"]
    assert "mug_1" in entry["after"]
    assert set(entry["after"]["mug_1"]["dist"]) == {"shelf_b", "sink_k"}
    assert any("mug_1@work_away<-commute_out" == c
               for c in acts["chain_inherited_after"])


def test_unmarked_program_keeps_both_away_blocks():
    program = mini_program_v3()          # no v3 marker
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "commute_out",
         "days": ["Mo"], "start": "09:00", "end": "09:30", "at": "ELSEWHERE",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"})
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "work_away",
         "days": ["Mo"], "start": "09:30", "end": "17:00", "at": "ELSEWHERE",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"})
    acts, motions = xc.expand(program)
    assert acts["merged_away_blocks"] == []
    assert "work_away" in motions["object_motions"]


# ------------------------------------------------ the person invariant --

def _two_res_program():
    program = _v3()
    program["residents"] = [{"id": "resident_1", "jitter_scale": 1.0},
                            {"id": "resident_2", "jitter_scale": 1.0}]
    program["object_owners"] = {"mug_1": "resident_1",
                                "keys_1": "resident_2"}
    program["sleep_schedule"].append(
        {"resident": "resident_2", "activity": "night_sleep",
         "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
         "start": "22:00", "end": "07:30+1", "at": "bed_b1",
         "jitter": "routine", "cites": "c"})
    # resident_2 goes to work; resident_1 tidies at home meanwhile
    program["weekly_blocks"] = [
        {"resident": "resident_2", "activity": "work_away",
         "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
         "start": "09:00", "end": "17:00", "at": "ELSEWHERE",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"},
        # a home block between work and the walk, or the away-chain
        # merge (correctly) reads them as one continuous outing
        {"resident": "resident_2", "activity": "dinner",
         "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
         "start": "17:15", "end": "17:45", "at": "table_a",
         "jitter": "routine", "skip_p": 0.0, "sleep": False, "cites": "c"},
        {"resident": "resident_2", "activity": "walk",
         "days": ["Mo"], "start": "18:00", "end": "18:30",
         "at": "ELSEWHERE", "jitter": "loose", "skip_p": 0.0,
         "sleep": False, "cites": "c"},
        {"resident": "resident_1", "activity": "tidy_up",
         "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
         "start": "10:00", "end": "10:30", "at": "table_a",
         "jitter": "flexible", "skip_p": 0.0, "sleep": False, "cites": "c"},
    ]
    program["object_rules"] = [
        {"object": "mug_1", "cites": "c", "home": "shelf_b",
         "rules": [{"cites": "c", "activity": "tidy_up", "phase": "after",
                    "dist": [{"dest": "shelf_b", "p": 0.6},
                             {"dest": "sink_k", "p": 0.4}]}]},
        # keys: away-bound via work_away, and a shared home-activity rule
        # that USED to be able to yank them off their absent owner
        {"object": "keys_1", "cites": "c", "home": "table_a",
         "rules": [
             {"cites": "c", "activity": "work_away", "phase": "after",
              "dist": [{"dest": "table_a", "p": 0.7},
                       {"dest": "shelf_b", "p": 0.3}]},
             {"cites": "c", "activity": "tidy_up", "phase": "after",
              "dist": [{"dest": "table_a", "p": 0.9},
                       {"dest": "NO_OP", "p": 0.1}]}]},
    ]
    program["activities"] = [{"name": "tidy_up", "cites": "c"}]
    program["arc_events"] = []
    return program


def test_home_after_rules_cannot_reach_a_person_or_elsewhere():
    _, motions = xc.expand(_two_res_program())
    tidy = motions["object_motions"]["tidy_up"]
    for obj, rule in tidy["after"].items():
        assert rule["only_from"], (obj, rule)
        assert all(not str(x).startswith("person:") and x != "ELSEWHERE"
                   for x in rule["only_from"]), (obj, rule)


def test_travellers_are_not_paraded_to_home_sites():
    _, motions = xc.expand(_two_res_program())
    tidy = motions["object_motions"]["tidy_up"]
    assert "keys_1" not in tidy["during"]      # away-bound: never paraded
    assert tidy["during"].get("mug_1") == "table_a"   # homebody: paraded


def test_pocket_items_ride_every_trip_of_their_owner_only():
    _, motions = xc.expand(_two_res_program())
    # keys ride the owner's work trip AND the walk (no authored walk rule)
    for act in ("work_away", "walk"):
        assert motions["object_motions"][act]["during"].get("keys_1") == \
            "person:resident_2", act
    # the walk got a synthesized homecoming putdown to the keys' home
    walk_after = motions["object_motions"]["walk"]["after"]["keys_1"]
    assert walk_after["dest"] == "table_a"
    assert walk_after["only_from"] == ["person:resident_2"]
    # and nothing puts resident_1's mug on resident_2
    assert "mug_1" not in motions["object_motions"]["work_away"]["during"]


def test_no_owner_data_means_no_person_legs():
    program = _two_res_program()
    del program["object_owners"]
    _, motions = xc.expand(program)
    assert motions["object_motions"]["work_away"]["during"] == {}


def test_person_invariant_holds_through_realization():
    """End to end: with resident_2 at work 09:00-17:00 daily, no event may
    take keys_1 off person:resident_2 during the trip's interior."""
    program = _two_res_program()
    log, hourly, blocks, stats, acts, motions = sim.simulate_program(
        program, 21, 0)
    trips = [(b["t0"], b["t1"]) for b in blocks
             if b["resident"] == "resident_2" and b["at"] == "ELSEWHERE"]
    bad = [e for e in log
           if e["from"] == "person:resident_2"
           and not str(e["to"]).startswith("person:")
           and e["to"] != "ELSEWHERE"
           and e["by"] != "misplace"
           and any(a < e["t"] < b for a, b in trips)]
    assert bad == [], bad[:3]


def test_home_pointing_away_rule_is_a_homecoming_not_fake_movement():
    """jacket case: an after rule on an AWAY activity whose dest is the
    object's own home is 'worn out, hung up on return' — under v3 the
    object rides its owner (reaching person:<owner>), so it is mobile and
    the rule survives. The old inert logic classed it static, the
    synthesis then carried it, and the v1 lint rejected the household."""
    program = _two_res_program()
    program["object_owners"]["jacket_1"] = "resident_2"
    program["object_rules"].append(
        {"object": "jacket_1", "cites": "c", "home": "shelf_b",
         "rules": [{"cites": "worn out, hung up on return",
                    "activity": "work_away", "phase": "after",
                    "dist": [{"dest": "shelf_b", "p": 0.9},
                             {"dest": "NO_OP", "p": 0.1}]}]})
    acts, motions = xc.expand(program)
    assert "jacket_1" not in acts["inert_objects"]
    assert not motions["placements"]["jacket_1"].get("static")
    assert motions["object_motions"]["work_away"]["during"]["jacket_1"] == \
        "person:resident_2"
    # the whole program still passes the v1 lint
    sim.load_v1().validate(acts, motions)


def test_another_residents_homecoming_cannot_reach_my_pocket():
    """Away variants inherit the base activity's after rules, so roommate
    B's homecoming used to fire rules over roommate A's held keys (hh9:
    four residents sharing work_away, 516 mid-trip teleports). A variant's
    after may reach receptacles, ELSEWHERE, and its OWN resident's person
    — never someone else's."""
    program = _two_res_program()
    # resident_1 ALSO works away, so both variants exist
    program["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "work_away",
         "days": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
         "start": "09:30", "end": "16:30", "at": "ELSEWHERE",
         "jitter": "external", "skip_p": 0.0, "sleep": False, "cites": "c"})
    _, motions = xc.expand(program)
    variants = [n for n in motions["object_motions"]
                if n.startswith("work_away")]
    assert len(variants) == 2
    persons_per_variant = {}
    for name in variants:
        act = motions["object_motions"][name]
        persons = set()
        for obj, rule in act.get("after", {}).items():
            persons |= {x for x in rule.get("only_from", [])
                        if str(x).startswith("person:")}
        # a variant's rules may reach at most ONE person — its own
        assert len(persons) <= 1, (name, persons)
        persons_per_variant[name] = persons
    # and the two variants reach DIFFERENT persons (each its own)
    reached = [p for s in persons_per_variant.values() for p in s]
    assert len(reached) == len(set(reached)) == 2, persons_per_variant
