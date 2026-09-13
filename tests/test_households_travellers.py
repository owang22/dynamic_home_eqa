"""Who leaves the house with what (src/households, v3 programs).

An object rides the trips its own rules name — and only those — while
pocket items (phone, keys, wallet) ride every trip of their owner, less a
standing per-trip-type omission and a per-departure forgetting draw.
Before this, "rides one trip, rides all" put hh1's suitcase on every
commute and its laundry basket on every walk, and NO_OP on a yoga mat's
gym rule left it in her hand on the sofa for 240 hours a month.
"""
from __future__ import annotations

import copy

import households.expand_calendar as xc
import households.simulate as sim

ALL_DAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
WEEKDAYS = ["Mo", "Tu", "We", "Th", "Fr"]


def _block(resident, activity, days, start, end, at, jitter="routine"):
    return {"resident": resident, "activity": activity, "days": days,
            "start": start, "end": end, "at": at, "jitter": jitter,
            "skip_p": 0.0, "sleep": False, "cites": "c"}


def _dist(*pairs):
    return [{"dest": d, "p": p} for d, p in pairs]


def program() -> dict:
    """One worker (resident_1) whose Tuesday work day ends at the gym,
    who does laundry at the laundromat on Sunday and at home on
    Wednesday, plus a homebody (resident_2)."""
    return copy.deepcopy({
        "household": "hh_test", "household_type": "test_type",
        "source_persona": "persona.yaml", "days": 14, "day0": "Monday",
        "object_semantics": xc.AFTER_ONLY_V3,
        "residents": [{"id": "resident_1", "jitter_scale": 1.0},
                      {"id": "resident_2", "jitter_scale": 1.0}],
        "receptacles": [{"id": "table_a", "room": "living"},
                        {"id": "shelf_b", "room": "living"},
                        {"id": "bed_b1", "room": "bedroom"},
                        {"id": "sink_k", "room": "kitchen"}],
        "object_owners": {"keys_1": "resident_1", "laptop_1": "resident_1",
                          "yoga_mat_1": "resident_1", "towel_1": "resident_1",
                          "plate_shared_1": "shared",
                          "umbrella_shared_1": "shared"},
        "sleep_schedule": [
            {"resident": r, "activity": "night_sleep", "days": ALL_DAYS,
             "start": "22:00", "end": "07:30+1", "at": "bed_b1",
             "jitter": "routine", "cites": "c"}
            for r in ("resident_1", "resident_2")],
        "weekly_blocks": [
            _block("resident_1", "work_away", WEEKDAYS, "09:00", "12:00",
                   "ELSEWHERE", "external"),
            _block("resident_1", "lunch", WEEKDAYS, "12:00", "12:30",
                   "ELSEWHERE", "external"),
            _block("resident_1", "work_away", WEEKDAYS, "12:30", "17:00",
                   "ELSEWHERE", "external"),
            _block("resident_1", "gym", ["Tu"], "17:00", "18:00",
                   "ELSEWHERE", "external"),
            _block("resident_1", "dinner", ALL_DAYS, "18:30", "19:00",
                   "table_a"),
            _block("resident_1", "walk", ["Sa"], "10:00", "11:00",
                   "ELSEWHERE", "loose"),
            _block("resident_1", "laundry", ["Su"], "10:00", "11:00",
                   "ELSEWHERE", "loose"),
            _block("resident_1", "laundry", ["We"], "19:30", "20:00",
                   "bed_b1"),
            _block("resident_1", "lunch", ["Sa", "Su"], "12:00", "12:30",
                   "table_a"),
            _block("resident_2", "tidy_up", ALL_DAYS, "10:00", "10:30",
                   "table_a", "flexible"),
        ],
        "object_rules": [
            {"object": "keys_1", "cites": "c", "home": "table_a",
             "rules": [{"cites": "c", "activity": "work_away",
                        "phase": "after",
                        "dist": _dist(("table_a", 0.7), ("NO_OP", 0.3))}]},
            {"object": "laptop_1", "cites": "c", "home": "table_a",
             "rules": [{"cites": "c", "activity": "work_away",
                        "phase": "after",
                        "dist": _dist(("table_a", 0.8), ("NO_OP", 0.2))}]},
            {"object": "yoga_mat_1", "cites": "c", "home": "shelf_b",
             "rules": [{"cites": "c", "activity": "gym", "phase": "after",
                        "dist": _dist(("shelf_b", 0.3), ("NO_OP", 0.7))}]},
            {"object": "towel_1", "cites": "c", "home": "bed_b1",
             "rules": [{"cites": "c", "activity": "laundry", "phase": "after",
                        "dist": _dist(("bed_b1", 0.9), ("shelf_b", 0.1))}]},
            {"object": "plate_shared_1", "cites": "c", "home": "sink_k",
             "rules": [{"cites": "c", "activity": "lunch", "phase": "after",
                        "dist": _dist(("sink_k", 0.7), ("table_a", 0.3))}]},
            {"object": "umbrella_shared_1", "cites": "c", "home": "shelf_b",
             "rules": [{"cites": "c", "activity": "walk", "phase": "after",
                        "dist": _dist(("shelf_b", 0.8), ("NO_OP", 0.2))}]},
        ],
        "activities": [{"name": "tidy_up", "cites": "c"}],
        "arc_events": [],
    })


def _expand(**kw):
    acts, motions = xc.expand(program(), **kw)
    sim.load_v1().validate(acts, motions)
    return acts, motions


def _carry_p(leg) -> float:
    return leg.get("p", 1.0) if isinstance(leg, dict) else 1.0


def _away_variants(motions):
    return {n: e for n, e in motions["object_motions"].items()
            if e.get("at") == xc.ELSEWHERE}


def test_an_object_rides_only_the_trip_its_rule_names():
    _, motions = _expand()
    away = _away_variants(motions)
    # Tuesday's work day absorbed the gym leg and is its own variant
    assert "work_away__resident_1+gym" in away
    plain, gym_day = away["work_away"], away["work_away__resident_1+gym"]
    assert "yoga_mat_1" not in plain["during"]
    assert gym_day["during"]["yoga_mat_1"]["dest"] == "person:resident_1"
    # the laptop rides every work day, never the walk or the laundromat
    for name in ("work_away", "work_away__resident_1+gym"):
        assert away[name]["during"]["laptop_1"]["dest"] == "person:resident_1"
    assert "laptop_1" not in away["walk"]["during"]
    assert "laptop_1" not in away["laundry"]["during"]
    # the towel goes to the laundromat only
    assert "towel_1" in away["laundry"]["during"]
    assert "towel_1" not in away["work_away"]["during"]


def test_noop_on_a_non_pocket_away_rule_is_the_chance_it_stays_home():
    _, motions = _expand()
    gym_day = _away_variants(motions)["work_away__resident_1+gym"]
    # NO_OP 0.7 after gym: the mat goes along 3 gym days in 10...
    assert abs(_carry_p(gym_day["during"]["yoga_mat_1"]) - 0.3) < 1e-9
    # ...and the mat that DID go always gets put down at homecoming
    rule = gym_day["after"]["yoga_mat_1"]
    assert "noop_p" not in rule
    assert rule["only_from"] == ["person:resident_1", xc.ELSEWHERE]
    laptop = _away_variants(motions)["work_away"]
    assert abs(_carry_p(laptop["during"]["laptop_1"]) - 0.8) < 1e-9
    assert "noop_p" not in laptop["after"]["laptop_1"]


def test_pocket_items_ride_every_trip_and_keep_noop_in_the_pocket():
    _, motions = _expand(forget_p=0.05, carry_p=1.0)
    away = _away_variants(motions)
    for name, entry in away.items():
        leg = entry["during"]["keys_1"]
        assert leg["dest"] == "person:resident_1", name
        assert abs(_carry_p(leg) - 0.95) < 1e-9, name
    # the authored homecoming keeps its NO_OP: "stays in her pocket"
    assert abs(away["work_away"]["after"]["keys_1"]["noop_p"] - 0.3) < 1e-9
    # a trip with no authored rule gets a putdown to home, off the person
    assert away["walk"]["after"]["keys_1"] == {
        "dest": "table_a", "only_from": ["person:resident_1"]}


def test_pocket_item_standing_omissions_are_per_trip_type():
    # carry_p 0 makes every unauthored (item, trip-type) pairing an
    # omission; authored trips are never subject to it
    acts, motions = _expand(carry_p=0.0)
    away = _away_variants(motions)
    assert "keys_1" in away["work_away"]["during"]
    assert "keys_1" not in away["walk"]["during"]
    assert "keys_1@walk" in acts["left_behind_by_trip"]
    # forget_p 0 and carry_p 1: a plain string leg, nothing to draw
    _, motions = _expand(carry_p=1.0, forget_p=0.0)
    assert _away_variants(motions)["walk"]["during"]["keys_1"] == \
        "person:resident_1"


def test_homebound_classes_never_ride():
    _, motions = _expand()
    for name, entry in _away_variants(motions).items():
        assert "plate_shared_1" not in entry["during"], name
    # ...but the authored lunch rule still fires at the work homecoming
    # as an in-house move (chain union), from receptacles
    rule = _away_variants(motions)["work_away"]["after"]["plate_shared_1"]
    assert "sink_k" in rule["only_from"]


def test_shared_object_rides_the_ruling_trip_without_a_handoff():
    _, motions = _expand()
    leg = _away_variants(motions)["walk"]["during"]["umbrella_shared_1"]
    assert leg["dest"] == "person:resident_1"
    assert not any(str(x).startswith(xc.PERSON) for x in leg["only_from"])
    assert "umbrella_shared_1" not in \
        _away_variants(motions)["work_away"]["during"]


def test_travellers_homecoming_reaches_only_what_came_home():
    _, motions = _expand()
    work = _away_variants(motions)["work_away"]
    for obj in ("keys_1", "laptop_1"):
        assert work["after"][obj]["only_from"] == \
            ["person:resident_1", xc.ELSEWHERE], obj


def test_person_invariant_holds_through_realization_including_misplace():
    p = program()
    p["object_rules"][0]["p_misplace"] = 0.9      # keys drift daily
    p["object_rules"][0]["misplace_set"] = ["shelf_b", "sink_k"]
    log, hourly, blocks, stats, acts, motions = sim.simulate_program(p, 14, 0)
    assert motions["person_invariant"] is True
    trips = [(b["t0"], b["t1"]) for b in blocks
             if b["resident"] == "resident_1" and b["at"] == xc.ELSEWHERE]
    bad = [e for e in log
           if e["from"] == "person:resident_1"
           and not str(e["to"]).startswith(xc.PERSON)
           and e["to"] != xc.ELSEWHERE
           and any(a < e["t"] < b for a, b in trips)]
    assert bad == [], bad[:3]
    assert stats["misplace_skipped_absent_holder"] > 0
    # the yoga mat only ever leaves on a gym day, and comes back
    mat = [e for e in log if e["object"] == "yoga_mat_1"
           and e["to"] == "person:resident_1"]
    assert all(e["by"] == "activity:work_away__resident_1+gym" for e in mat)
    assert stats["departures_without_item"] > 0


def test_unmarked_program_gets_none_of_this():
    p = program()
    del p["object_semantics"]
    acts, motions = xc.expand(p, forget_p=0.5)
    assert "person_invariant" not in motions
    for entry in motions["object_motions"].values():
        assert all(not isinstance(v, dict) for v in entry["during"].values())
