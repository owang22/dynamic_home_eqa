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
