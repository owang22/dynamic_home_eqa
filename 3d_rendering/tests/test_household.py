"""Household creation checks and id building, no model."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from lived_home.household import check_room_objects, compose_ids   # noqa: E402


def thing(n, type_, looks, ref=0, rel="on", carrier="none", place="a", **kw):
    o = {"n": n, "type": type_, "looks": looks, "color": "red", "material": "ceramic",
         "condition": "worn", "pattern": "plain", "place": place, "relation": rel,
         "ref": ref, "carrier": carrier}
    o.update(kw)
    return o


def test_ids_come_from_type_and_looks_without_names():
    objs = [thing(1, "Mug", "Red Ceramic"), thing(2, "t-shirt", "mara blue"),
            thing(3, "hand cream", "unscented tube")]
    compose_ids(objs, {}, ["mara", "daniel"])
    assert [o["id"] for o in objs] == ["mug_red_ceramic", "t_shirt_blue", "hand_cream_unscented_tube"]


def test_clash_takes_next_attribute_then_number():
    objs = [thing(1, "mug", "red"), thing(2, "mug", "red"), thing(3, "mug", "red")]
    compose_ids(objs, {"mug_red": None}, [])
    assert [o["id"] for o in objs] == ["mug_red_ceramic", "mug_red_ceramic_worn", "mug_red_ceramic_worn_plain"]


def test_refs_become_ids():
    objs = [thing(1, "tote bag", "canvas", carrier="closed"), thing(2, "wallet", "brown", ref=1, rel="in")]
    assert check_room_objects({"a"})({"objects": objs}) == ""
    compose_ids(objs, {}, [])
    assert objs[1]["ref"] == "tote_bag_canvas"


def test_semantic_problems_listed_together():
    objs = [thing(1, "book", "green", ref=2, rel="on_top_of"), thing(2, "book", "blue", ref=1, rel="on_top_of"),
            thing(3, "wallet", "brown", ref=4, rel="in"), thing(4, "mug", "red"),
            thing(5, "bag", "x", ref=6, rel="in", carrier="closed"), thing(6, "basket", "y", carrier="open"),
            thing(7, "pen", "z", ref=9)]
    msg = check_room_objects({"a"})({"objects": objs})
    assert "loop" in msg and "cannot hold things" in msg and "cannot start inside" in msg
    assert "not another thing" in msg


def test_owned_thing_described_again_is_dropped_but_shared_kept():
    objs = [thing(1, "reading glasses", "tortoiseshell frames", owner="mara"),
            thing(2, "mug", "red"), thing(3, "watch", "silver", ref=1, rel="next_to", owner="mara")]
    dropped = compose_ids(objs, {"reading_glasses_tortoiseshell_frames": "mara", "mug_red": None}, ["mara"])
    assert [o["id"] for o in dropped] == ["reading_glasses_tortoiseshell_frames"]
    assert [o["id"] for o in objs] == ["mug_red_ceramic", "watch_silver"]
    assert objs[1]["ref"] == ""
