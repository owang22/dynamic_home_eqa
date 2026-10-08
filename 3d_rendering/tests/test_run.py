"""Day-loop rules that need no model."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from lived_home.run_pilot import Household     # noqa: E402


def act(room, start, end):
    return {"room": room, "start_min": start, "end_min": end}


def test_away_minutes_from_plan():
    # leaving during the commute, work follows: away until work ends
    a = {"verb": "leave_home", "minutes": 45}
    Household._away_minutes(a, act("out_of_house", 465, 510), [act("out_of_house", 510, 1020), act("dining", 1050, 1100)], 465)
    assert a["minutes"] == 1020 - 465 and a["minutes_as_written"] == 45
    # leaving at the end of a home activity, work starts next: filled from the plan
    a = {"verb": "leave_home", "minutes": 0}
    Household._away_minutes(a, act("entry", 390, 405), [act("out_of_house", 405, 990)], 400)
    assert a["minutes"] == 590
    # a quick walk with nothing out of house planned soon keeps its minutes
    a = {"verb": "leave_home", "minutes": 20}
    Household._away_minutes(a, act("living", 600, 660), [act("kitchen", 660, 700), act("out_of_house", 900, 960)], 610)
    assert a["minutes"] == 20 and "minutes_filled" not in a
    a = {"verb": "leave_home", "minutes": 0}
    Household._away_minutes(a, act("living", 600, 660), [act("out_of_house", 900, 960)], 610)
    assert a["minutes"] == 30 and a["minutes_filled"] == "default"


def test_away_minutes_skip_one_home_activity_before_work():
    # leaving at the end of dressing; "collect equipment" (home) then work out of house
    a = {"verb": "leave_home", "minutes": 0}
    Household._away_minutes(a, act("kitchen", 345, 390), [act("entry", 390, 405), act("out_of_house", 405, 990),
                                                           act("entry", 990, 1020)], 370)
    assert a["minutes"] == 990 - 370


def test_recap_shows_a_step_the_engine_did_first():
    from lived_home.run_pilot import _short_event
    e = {"verb": "put_down", "object": "notebook_red", "to": "on top desk", "implied": True}
    assert _short_event(e) == "put_down notebook_red (on top desk) [done for you first]"
    assert _short_event({"verb": "say", "person": "ben", "text": "hi"}) == 'say to ben "hi"'
