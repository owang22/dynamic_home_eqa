"""The play task's 'how it got there' list, on a small made-up history."""
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
