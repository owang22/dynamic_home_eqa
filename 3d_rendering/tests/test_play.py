"""The play task's 'how it got there' list, on a small made-up history."""
import collections
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from lived_home.play import how_it_got_there, spot_words      # noqa: E402

PLACES = {"desk_top": {"room": "office", "furniture": "desk", "name": "desk top"},
          "hall_floor": {"room": "hall", "furniture": "floor", "name": "floor"}}
NAMES = {"wallet_tan": "tan wallet", "bag_olive": "olive bag", "pen_red": "red pen"}


def ev(day, minute, verb, obj, to_pos=None, frm="", to=""):
    return {"day": day, "minute": minute, "time": f"{minute // 60:02d}:{minute % 60:02d}", "resident": "ana",
            "verb": verb, "object": obj, "to_pos": to_pos, "from": frm, "to": to, "why": "because"}


def test_bag_moves_count_only_after_the_thing_went_in_and_nothing_after_the_question():
    state = {"objects": {
        "wallet_tan": {"relation": "inside", "reference": "bag_olive", "reference_kind": "object"},
        "bag_olive": {"relation": "on_top", "reference": "desk_top", "reference_kind": "place", "place": "desk_top"},
        "pen_red": {"relation": "on_top", "reference": "desk_top", "reference_kind": "place", "place": "desk_top"}}}
    events = [
        ev(2, 480, "pick_up", "bag_olive", {"at": "hand", "person": "ana"}, frm="on top hall_floor"),
        ev(2, 481, "put_down", "wallet_tan", {"at": "inside", "carrier": "bag_olive"}, to="inside bag_olive"),
        ev(2, 490, "put_down", "bag_olive", {"at": "place", "place": "desk_top"}, to="on top desk_top"),
        ev(2, 600, "pick_up", "bag_olive", {"at": "hand", "person": "ana"}, frm="on top desk_top"),   # at the question
        ev(2, 500, "put_down", "pen_red", {"at": "place", "place": "desk_top"}, to="on top desk_top")]
    out = how_it_got_there(["wallet_tan"], state, (2, "1000"), events, {}, NAMES, {"ana": "Ana"}, PLACES)
    texts = [m["text"] for m in out]
    assert len(out) == 2                                       # not the 08:00 pick-up, not 10:00
    assert texts[0].startswith("put down the tan wallet inside the olive bag")
    assert texts[1] == "put down the olive bag (with the tan wallet inside) on top of the desk top (office)"
    assert all("red pen" not in t for t in texts)


def test_spot_words():
    assert spot_words("glass desk", "desk top") == "glass desk top"
    assert spot_words("floor", "floor") == "floor"
    assert spot_words("king bed", "mattress") == "king bed mattress"


# ------------------------------------------------------------------ simple methods (play_baselines)
def _data(patrol_where="", truth_kind="put away", truth_who=None):
    """One question about a mug: patrols saw it on the kitchen counter (or in Ana's
    hands); now it is not visible anywhere."""
    fur = [{"key": "kitchen|counter", "room": "kitchen", "name": "counter", "x": 0.0, "z": 0.0,
            "spots": [{"id": "counter_top", "kind": "surface"}]},
           {"key": "kitchen|cabinet", "room": "kitchen", "name": "cabinet", "x": 1.0, "z": 0.0,
            "spots": [{"id": "cabinet_in", "kind": "closed"}]},
           {"key": "hall|table", "room": "hall", "name": "table", "x": 5.0, "z": 0.0,
            "spots": [{"id": "hall_table", "kind": "surface"}]}]
    answer = ({"kind": truth_kind, "spot": "cabinet_in", "furniture": "kitchen|cabinet", "room": "kitchen"}
              if truth_kind == "put away" else {"kind": truth_kind, "who": truth_who})
    return {"session": "t", "residents": [{"id": "ana", "name": "Ana Lima"}],
            "layout": {"entry": "hall_table", "furniture": fur},
            "patrols": [{"day": 1, "time": "08:00", "rooms": ["kitchen"], "people": {},
                         "seen": [{"furniture": "kitchen|counter", "oids": ["mug_red"],
                                   "things": [{"spot": "counter_top", "thing": "red mug",
                                               "where": patrol_where}]}]}],
            "questions": [{"n": 1, "day": 1, "time": "10:00", "kind": "put away", "accept": ["mug_red"],
                           "answer": {"mug_red": answer}, "looks": {}, "people": {}}],
            "rules": {"max_looks": 2}}


def test_memory_answers_put_away_and_someone_has_it():
    from lived_home.play_baselines import play
    # last seen on a counter with no drawers: put away in the nearest cabinet of that room
    r = play(_data(), "last seen")[0]
    assert r["answer"] == "putaway" and r["verdict"] == "good"
    assert play(_data(), "last seen", memory_answers=False)[0]["verdict"] == "part"   # can't tell
    assert play(_data(), "nearest")[0]["answer"] == "cant"                            # no memory
    # last seen in Ana's hands: someone has it
    d = _data("in Ana's hands", "someone has it", "ana")
    r = play(d, "most often")[0]
    assert r["answer"] == "someone" and r["verdict"] == "good"


def test_judge_matches_the_play_page():
    from lived_home.play_baselines import judge
    F = {"kitchen|cabinet": {"room": "kitchen"}, "kitchen|counter": {"room": "kitchen"}}
    q = {"answer": {"m": {"kind": "put away", "furniture": "kitchen|cabinet", "room": "kitchen"}}}
    assert judge(q, {"type": "putaway", "fkey": "kitchen|cabinet"}, F) == "good"
    assert judge(q, {"type": "putaway", "fkey": "kitchen|counter"}, F) == "part"
    assert judge(q, {"type": "someone", "who": "ana"}, F) == "bad"
    assert judge(q, {"type": "cant"}, F) == "part"


def test_every_question_covers_each_askable_thing_at_each_question_time():
    import pytest
    run = pathlib.Path(__file__).resolve().parents[1] / "results" / "lived_home" / "hssd_b"
    if not (run / "day_14").exists():
        pytest.skip("run hssd_b not here")
    from lived_home.play import QUESTION_TIMES, build_all
    data = build_all(run, 2)
    qs = data["questions"]
    slots = {(q["day"], q["time"]) for q in qs}
    assert len(slots) == 11 * len(QUESTION_TIMES)               # days 4-14
    per_slot = collections.Counter((q["day"], q["time"]) for q in qs)
    assert len(qs) > 4000 and max(per_slot.values()) - min(per_slot.values()) < 40
    # the same patrols as the 30-question session with that seed
    sess = json.loads((run / "play" / "play_data.json").read_text())
    assert [p["rooms"] for p in sess["patrols"]] == [p["rooms"] for p in data["patrols"]]
