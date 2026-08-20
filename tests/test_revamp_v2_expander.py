"""Step-2 property tests for expand_calendar.expand: deterministic, weekly
coverage, arc drop/add semantics, linger synthesis, day_overrides."""
from __future__ import annotations

import pytest

from revamp_v2_helpers import mini_program

import expand_calendar as xc


def test_expansion_is_deterministic():
    a1 = xc.expand(mini_program())
    a2 = xc.expand(mini_program())
    assert a1 == a2


def _items(acts, name):
    return [(e["day"], it) for e in acts["calendar"]
            for it in e["activities"] if it["a"] == name]


def test_weekly_block_covers_every_matching_day():
    acts, motions = xc.expand(mini_program())
    assert len(_items(acts, "breakfast")) == 21          # Mo-Su, 21 days
    # relax dropped on days 3, 8, 9 by arc events
    days = [d for d, _ in _items(acts, "relax")]
    assert len(days) == 18 and not {3, 8, 9} & set(days)


def test_restricted_days_expand_only_those_weekdays():
    p = mini_program()
    p["weekly_blocks"][0]["days"] = ["Mo", "Th"]
    acts, _ = xc.expand(p)
    days = [d for d, _ in _items(acts, "breakfast")]
    assert days == [0, 3, 7, 10, 14, 17]


def test_arc_add_lands_on_its_day():
    acts, motions = xc.expand(mini_program())
    assert [(d, it["t"]) for d, it in _items(acts, "errands")] == [(5, "10:00")]
    assert motions["object_motions"]["errands"]["at"] == "ELSEWHERE"


def test_drop_of_unknown_activity_is_an_error():
    p = mini_program()
    p["arc_events"][0]["patch"]["drop"] = ["deep_clean"]
    with pytest.raises(ValueError, match="names no activity"):
        xc.expand(p)


def test_drop_on_a_day_the_activity_does_not_run_is_a_counted_noop():
    # Vacuous, not fatal — but never silent: it is counted for the report.
    p = mini_program()
    p["weekly_blocks"][1]["days"] = ["Sa", "Su"]     # relax weekends only
    p["arc_events"][0]["day"] = 2                    # a Wednesday
    acts, _ = xc.expand(p)
    # days 2, 8 and 9 are all weekdays now, so all three drops are vacuous
    assert acts["vacuous_drops"] == [{"day": d, "activity": "relax"}
                                     for d in (2, 8, 9)]
    # and every weekend realization survives untouched
    assert [d for d, _ in _items(acts, "relax")] == [5, 6, 12, 13, 19, 20]


def test_linger_marks_authored_end():
    acts, motions = xc.expand(mini_program())
    lingers = _items(acts, "linger_table_a")
    # breakfast (daily, 08:30) + relax (18 surviving days, 21:45)
    assert len(lingers) == 21 + 18
    assert motions["object_motions"]["linger_table_a"] == {
        "at": "table_a", "jitter": xc.LINGER_JITTER,
        "during": {}, "after": {}}
    # each linger is tied to its source block for skip propagation
    assert all(it.get("_follows") for _, it in lingers)


def test_no_linger_when_next_block_truncates():
    p = mini_program()
    # errand at 21:20 truncates relax (end 21:45) on day 5
    p["arc_events"][1]["patch"]["add"][0]["start"] = "21:20"
    acts, _ = xc.expand(p)
    day5 = [it for d, it in _items(acts, "linger_table_a") if d == 5]
    assert len(day5) == 1        # only breakfast's linger remains on day 5


def test_sleep_end_past_midnight_lingers_next_morning():
    acts, _ = xc.expand(mini_program())
    lingers = _items(acts, "linger_bed_b1")
    # 21 sleeps; last (day 20) ends past the horizon -> 20 lingers,
    # each landing on the morning AFTER its block's day
    assert len(lingers) == 20
    assert all(it["t"] == "07:30" for _, it in lingers)
    assert [d for d, _ in lingers] == list(range(1, 21))


def test_end_equal_to_start_wraps_a_full_day():
    # An `end` equal to its own `start` is the next occurrence of that
    # clock time, i.e. 24 h later — bounded, never negative.
    p = mini_program()
    p["weekly_blocks"][0]["end"] = "08:00"
    acts, _ = xc.expand(p)
    # the day-long breakfast is truncated by the next block every day, so
    # it synthesizes no linger at all
    assert not [it for e in acts["calendar"] for it in e["activities"]
                if it["a"] == "linger_table_a" and it["t"] == "08:00"]


def test_same_activity_in_two_places_becomes_per_location_variants():
    """Four residents each sleeping in their own bed is ONE activity, not
    four differently-named ones — the v1 simulator's one-at-per-activity
    table is satisfied by splitting into variants that share bindings."""
    p = mini_program()
    p["weekly_blocks"].append(
        {"resident": "resident_1", "activity": "breakfast",
         "days": ["Sa", "Su"], "start": "09:00", "end": "09:30",
         "at": "sink_k", "jitter": "routine", "skip_p": 0.0,
         "cites": "weekend coffee elsewhere"})
    acts, motions = xc.expand(p)
    names = {it["a"] for e in acts["calendar"] for it in e["activities"]}
    assert "breakfast" in names and "breakfast__sink_k" in names
    assert motions["object_motions"]["breakfast"]["at"] == "table_a"
    assert motions["object_motions"]["breakfast__sink_k"]["at"] == "sink_k"
    # both variants carry the SAME bindings
    assert (motions["object_motions"]["breakfast"]["during"]
            == motions["object_motions"]["breakfast__sink_k"]["during"])


def test_single_location_activity_keeps_its_name():
    _, motions = xc.expand(mini_program())
    assert not [n for n in motions["object_motions"] if "__" in n]


def test_after_override_becomes_day_override():
    p = mini_program()
    p["arc_events"][1]["patch"]["after_override"] = [
        {"activity": "breakfast",
         "rule": {"object": "mug_1", "dest": "shelf_b"}}]
    _, motions = xc.expand(p)
    assert motions["day_overrides"] == [
        {"days": [5], "activity": "breakfast", "reason": "an appointment",
         "after": {"mug_1": {"dest": "shelf_b"}}}]


def test_activity_entry_without_blocks_is_dropped_and_counted():
    # Extras (a tidy walk, a fragment) attached to an activity nothing
    # schedules describe something that never happens.
    p = mini_program()
    p["activities"].append({"name": "gym", "reset_all": {"p": 0.5}})
    acts, motions = xc.expand(p)
    assert "gym" not in motions["object_motions"]
    assert acts["unscheduled_activities"] == ["gym"]


def test_dist_rules_convert_in_order():
    p = mini_program()
    p["object_rules"][0]["rules"] = [
        {"activity": "breakfast", "phase": "after",
         "dist": [{"dest": "sink_k", "p": 0.6}, {"dest": "shelf_b", "p": 0.4}],
         "only_from": ["table_a"]}]
    _, motions = xc.expand(p)
    rule = motions["object_motions"]["breakfast"]["after"]["mug_1"]
    assert rule == {"dist": {"sink_k": 0.6, "shelf_b": 0.4},
                    "only_from": ["table_a"]}
    assert list(rule["dist"]) == ["sink_k", "shelf_b"]


def test_zero_p_misplace_is_dropped_not_kept():
    # A 0.0 probability is the ABSENCE of drift: v1's lint tests presence,
    # so keeping it would make a static object read as mobile.
    p = mini_program()
    p["object_rules"][1]["p_misplace"] = 0.0
    p["object_rules"][1]["misplace_set"] = ["shelf_b"]
    _, motions = xc.expand(p)
    assert motions["placements"]["book_1"] == {"home": "table_a",
                                               "static": True}
    p = mini_program()
    p["object_rules"][0]["p_misplace"] = 0.3
    p["object_rules"][0]["misplace_set"] = ["table_a", "sink_k"]
    _, motions = xc.expand(p)
    assert motions["placements"]["mug_1"] == {
        "home": "shelf_b", "p_misplace": 0.3,
        "misplace_set": ["table_a", "sink_k"]}


def test_end_is_next_occurrence_of_that_clock_time():
    # "+1" carried inconsistently must not be an error: a block starting
    # 12:00+1 and ending "16:30" ends 4.5 h later, not the day before.
    p = mini_program()
    p["arc_events"][1]["patch"]["add"] = [
        {"resident": "resident_1", "activity": "night_out", "start": "12:00+1",
         "end": "16:30", "at": "ELSEWHERE", "jitter": "external"}]
    acts, _ = xc.expand(p)
    linger = [(e["day"], it["t"]) for e in acts["calendar"]
              for it in e["activities"] if it["a"] == "linger_out"]
    assert linger == [(6, "16:30")]      # day 5 + 1, 4.5 h after the start


def test_duplicate_activity_entries_are_merged():
    # They carry only extras, so the union is what the author meant.
    p = mini_program()
    p["activities"] = [{"name": "breakfast", "reset_all": {"p": 0.5}},
                       {"name": "breakfast", "fragment": {"mean_bouts": 3}}]
    _, motions = xc.expand(p)
    act = motions["object_motions"]["breakfast"]
    assert act["reset_all"] == {"p": 0.5} and act["fragment"]["mean_bouts"] == 3


def test_rules_survive_the_sleep_rename():
    """A block the author flags `sleep: true` gets renamed for the
    downstream convention; rules naming it must follow, or the object
    silently loses them — which cost a phone its only pick-up rule."""
    p = mini_program()
    for b in p["weekly_blocks"]:
        if b["activity"] == "breakfast":
            b["sleep"] = True          # author's call, however odd
    acts, motions = xc.expand(p)
    assert acts["orphaned_rules"] == []
    assert "sleep_breakfast" in motions["object_motions"]
    assert motions["object_motions"]["sleep_breakfast"]["during"] == {
        "mug_1": "table_a"}


def test_leaving_the_house_takes_your_things_with_you():
    """A person-homed item is picked up by whoever is going out — and only
    by them: two people running errands must not pocket each other's."""
    p = mini_program()
    p["object_rules"][0]["home"] = "person:resident_1"     # mug_1 stands in
    p["arc_events"][1]["patch"]["add"] = [
        {"resident": "resident_1", "activity": "errands", "start": "10:00",
         "at": "ELSEWHERE", "jitter": "external"}]
    acts, motions = xc.expand(p)
    assert motions["object_motions"]["errands"]["during"]["mug_1"] == \
        "person:resident_1"
    assert acts["carried_on_departure"] == ["mug_1@errands"]


def test_departure_pickup_is_per_resident():
    p = mini_program()
    p["residents"].append({"id": "resident_2", "jitter_scale": 1.0})
    p["object_rules"][0]["home"] = "person:resident_2"     # belongs to R2
    p["sleep_schedule"].append(
        dict(p["sleep_schedule"][0], resident="resident_2"))
    p["arc_events"][1]["patch"]["add"] = [
        {"resident": "resident_1", "activity": "errands", "start": "10:00",
         "at": "ELSEWHERE", "jitter": "external"}]
    acts, motions = xc.expand(p)
    # resident_1 leaving must not pick up resident_2's things
    assert "mug_1" not in motions["object_motions"]["errands"]["during"]
    assert acts["carried_on_departure"] == []


def test_carry_on_departure_can_be_turned_off():
    p = mini_program()
    p["object_rules"][0]["home"] = "person:resident_1"
    p["arc_events"][1]["patch"]["add"] = [
        {"resident": "resident_1", "activity": "errands", "start": "10:00",
         "at": "ELSEWHERE", "jitter": "external"}]
    _, motions = xc.expand(p, carry_on_departure=False)
    assert "mug_1" not in motions["object_motions"]["errands"]["during"]


def test_carried_putdown_fires_at_activity_start_not_end():
    """The v1 loop fires a boundary minute's `during` before its `after`,
    so an end-of-block put-down overrode the next block's departure pickup
    — the phone was grabbed and instantly back on the nightstand."""
    p = mini_program()
    p["object_rules"][0]["home"] = "person:resident_1"
    p["object_rules"][0]["rules"] = [
        {"activity": "breakfast", "phase": "during",
         "dest": "person:resident_1"},
        {"activity": "relax", "phase": "after", "dest": "table_a", "p": 0.7,
         "else": "shelf_b"},
    ]
    acts, motions = xc.expand(p)
    relax = motions["object_motions"]["relax"]
    assert "mug_1" not in relax["after"]
    assert relax["during"]["mug_1"] == "table_a"     # modal destination
    assert acts["carried_putdowns_at_start"] == ["mug_1@relax"]
    # off = untouched (the regression fixture depends on this)
    _, m2 = xc.expand(p, carry_on_departure=False)
    assert "mug_1" in m2["object_motions"]["relax"]["after"]


def test_take_along_varies_by_item_and_trip_but_is_stable():
    picks = [(o, a) for o in ("phone_1", "wallet_1", "keys_1", "glasses_1")
             for a in ("errands", "walk", "gym", "groceries")
             if xc.takes_along("hh_x", o, a, 0.85)]
    assert 0 < len(picks) < 16          # some taken, some standing omissions
    assert picks == [(o, a) for o in ("phone_1", "wallet_1", "keys_1",
                                      "glasses_1")
                     for a in ("errands", "walk", "gym", "groceries")
                     if xc.takes_along("hh_x", o, a, 0.85)]   # deterministic
    assert xc.takes_along("hh_x", "phone_1", "errands", 1.0)  # 1.0 = always


def test_left_behind_pairs_are_reported():
    p = mini_program()
    p["object_rules"][0]["home"] = "person:resident_1"
    p["arc_events"][1]["patch"]["add"] = [
        {"resident": "resident_1", "activity": "errands", "start": "10:00",
         "at": "ELSEWHERE", "jitter": "external"}]
    acts, motions = xc.expand(p, carry_p=0.0)      # never taken
    assert "mug_1" not in motions["object_motions"]["errands"]["during"]
    assert acts["left_behind_by_trip"] == ["mug_1@errands"]
