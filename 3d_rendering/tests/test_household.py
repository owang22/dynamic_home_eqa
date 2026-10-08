"""Household creation checks and id building, no model."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from lived_home.household import check_room_objects, compose_ids   # noqa: E402


def thing(n, type_, looks, ref=0, rel="on_top", carrier="none", place="a", **kw):
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
    compose_ids(objs, {"mug_red": {"owner": None, "place": "elsewhere", "type": "mug", "looks": {"red"}}}, [])
    assert [o["id"] for o in objs] == ["mug_red_ceramic", "mug_red_ceramic_worn", "mug_red_ceramic_worn_plain"]


def test_refs_become_ids():
    objs = [thing(1, "tote bag", "canvas", carrier="closed"), thing(2, "wallet", "brown", ref=1, rel="inside")]
    assert check_room_objects({"a"})({"objects": objs}) == ""
    compose_ids(objs, {}, [])
    assert objs[1]["ref"] == "tote_bag_canvas"


def test_semantic_problems_listed_together():
    objs = [thing(1, "book", "green", ref=2, rel="on_top"), thing(2, "book", "blue", ref=1, rel="on_top"),
            thing(3, "wallet", "brown", ref=4, rel="inside"), thing(4, "mug", "red"),
            thing(5, "bag", "x", ref=6, rel="inside", carrier="closed"), thing(6, "basket", "y", carrier="open"),
            thing(7, "pen", "z", ref=9)]
    msg = check_room_objects({"a"})({"objects": objs})
    assert "loop" in msg and "not another thing" in msg
    assert "cannot hold" not in msg                     # anything may hold anything


def test_owned_thing_described_again_is_dropped_but_shared_kept():
    objs = [thing(1, "reading glasses", "tortoiseshell frames", owner="mara"),
            thing(2, "mug", "red"), thing(3, "watch", "silver", ref=1, rel="next_to", owner="mara")]
    dropped = compose_ids(objs, {"reading_glasses_tortoiseshell_frames": {"owner": "mara", "place": "x", "type": "reading glasses", "looks": {"tortoiseshell", "frames"}},
                                 "mug_red": {"owner": None, "place": "elsewhere", "type": "mug", "looks": {"red"}}}, ["mara"])
    assert [o["id"] for o in dropped] == ["reading_glasses_tortoiseshell_frames"]
    assert [o["id"] for o in objs] == ["mug_red_ceramic", "watch_silver"]
    assert objs[1]["ref"] == ""


def test_thing_in_a_bag_takes_the_bags_spot():
    objs = [thing(1, "tote bag", "canvas", carrier="open", place="hook"),
            thing(2, "gloves", "gray", ref=1, rel="inside", place="floor")]
    assert check_room_objects({"hook", "floor"})({"objects": objs}) == ""
    compose_ids(objs, {}, [])
    assert objs[1]["place"] == "hook" and objs[1]["place_as_written"] == "floor"


def test_same_type_same_spot_shared_look_is_dropped():
    taken = {"fruit_bowl_blue_stoneware": {"owner": None, "place": "a", "type": "fruit bowl", "looks": {"blue", "stoneware"}}}
    objs = [thing(1, "fruit bowl", "blue glazed", carrier="open"), thing(2, "apple", "red", ref=1, rel="inside")]
    dropped = compose_ids(objs, taken, [])
    assert [o["n"] for o in dropped] == [1] and objs[0]["ref"] == ""


def test_owned_clash_with_other_owner_is_the_same_thing():
    taken = {"phone_blue_rubber_case": {"owner": "daniel", "place": "x", "type": "phone", "looks": {"blue", "rubber", "case"}}}
    objs = [thing(1, "phone", "blue rubber case", owner="mara", place="dining")]
    assert len(compose_ids(objs, taken, ["mara", "daniel"])) == 1


def test_missing_essentials_by_type_words():
    from lived_home.household import missing_essentials
    objs = [{"type": "phone", "owner": "mara"}, {"type": "house keys", "owner": "mara"},
            {"type": "phone charger", "owner": "ben"}, {"type": "purse", "owner": "ben"}]
    assert missing_essentials(objs, "mara") == ["wallet or purse"]
    assert missing_essentials(objs, "ben") == ["phone", "keys"]


def test_personal_call_keeps_a_lookalike_owned_by_someone_else():
    taken = {"wallet_brown_leather": {"owner": "mara", "place": "drawer", "type": "wallet", "looks": {"brown", "leather"}}}
    objs = [thing(1, "wallet", "brown bifold", owner="daniel", place="drawer"),
            thing(2, "keys", "truck", owner="daniel", place="drawer")]
    assert compose_ids(objs, taken, ["mara", "daniel"], owner="daniel") == []
    objs = [thing(1, "wallet", "brown leather", owner="daniel", place="drawer")]
    assert compose_ids(objs, taken, ["mara", "daniel"], owner="daniel") == []
    assert objs[0]["id"] != "wallet_brown_leather"


def test_shared_supplies_keep_a_lookalike_someone_owns():
    from lived_home.household import NOBODY
    taken = {"pain_reliever_white_bottle": {"owner": "daniel", "place": "shelf", "type": "pain reliever",
                                            "looks": {"white", "bottle"}}}
    objs = [thing(1, "pain reliever", "white caplet bottle", owner="none", place="shelf")]
    assert compose_ids(objs, taken, ["daniel"], owner=NOBODY) == []


def test_more_forks_asked_for_are_kept_beside_a_look_alike():
    taken = {"fork_four_tine_steel": {"owner": None, "place": "a", "type": "fork", "looks": {"four", "tine", "steel"}}}
    objs = [thing(1, "fork", "four tine brushed"), thing(2, "fork", "three tine steel")]
    assert len(compose_ids([dict(o) for o in objs], dict(taken), [])) == 2     # repeats, without the request
    kept = [dict(o) for o in objs]
    assert compose_ids(kept, dict(taken), [], more_of={"fork"}) == []
    assert [o["id"] for o in kept] == ["fork_four_tine_brushed", "fork_three_tine_steel"]
