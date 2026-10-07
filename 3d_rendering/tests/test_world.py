"""Engine rules on the hand-written layout, no model."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from lived_home.layout import pilot_layout          # noqa: E402
from lived_home.world import World, at_place        # noqa: E402


def obj(type_, place, rel="on", ref=None, carrier="none", pocketable=False, owner=None, inside=None):
    start = {"at": "inside", "carrier": inside} if inside else at_place(place, rel, ref)
    return {"type": type_, "owner": owner, "pocketable": pocketable, "carrier": carrier,
            "start": start}


def make():
    objects = {
        "mug_red": obj("mug", "kitchen_counter_by_sink"),
        "mug_white": obj("mug", "kitchen_upper_cabinet", "in"),
        "toaster_silver": obj("toaster", "kitchen_counter_by_stove"),
        "backpack_black": obj("backpack", "entry_table", carrier="closed", owner="ben"),
        "laptop_work": obj("laptop", None, inside="backpack_black", owner="ben"),
        "keys_ben": obj("keys", "entry_key_bowl", pocketable=True),
        "book_novel": obj("book", "living_coffee_table"),
        "book_atlas": obj("book", "living_coffee_table", "on_top_of", "book_novel"),
        "slipper_left": obj("slipper", "under_bed"),
        "phone_ana": obj("phone", "nightstand_left", pocketable=True, owner="ana"),
    }
    return World(pilot_layout(), objects, ["ana", "ben"], {"ana": "bed", "ben": "bed"})


def A(verb, **kw):
    return {"verb": verb, **kw}


def one_spot_each(w):
    for oid, pos in w.where.items():
        holders = [p.rid for p in w.people.values() if oid in p.hands or oid in p.pocket]
        assert len(holders) <= 1, oid
        if pos["at"] in ("hand", "pocket"):
            assert holders == [pos["person"]], oid
        else:
            assert holders == [], oid


def test_pick_up_walks_within_room_but_not_across_rooms():
    w = make()
    ok, msg, _ = w.apply("ana", A("pick_up", object="mug_red"), 0)
    assert not ok and "mug_red" in msg                  # bedroom, mug is in the kitchen
    assert "you last saw it" in msg                      # her memory, not a lookup
    w.apply("ana", A("go", place="kitchen_island"), 0)
    ok, _, _ = w.apply("ana", A("pick_up", object="mug_red"), 1)
    assert ok and w.people["ana"].at == "kitchen_counter_by_sink"
    assert any(e.get("implied") for e in w.log)
    one_spot_each(w)


def test_two_hands_only():
    w = make()
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    assert w.apply("ana", A("pick_up", object="mug_red"), 0)[0]
    assert w.apply("ana", A("pick_up", object="toaster_silver"), 0)[0]
    ok, msg, _ = w.apply("ana", A("pick_up", object="mug_white"), 0)
    assert not ok and "full" in msg


def test_relative_positions_and_hidden():
    w = make()
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ana", A("pick_up", object="mug_red"), 0)
    ok, msg, _ = w.apply("ana", A("put_down", object="mug_red", place="kitchen_counter_by_stove",
                                  relation="behind", ref="toaster_silver"), 1)
    assert ok, msg
    assert w.where["mug_red"] == at_place("kitchen_counter_by_stove", "behind", "toaster_silver")
    assert w.hidden("mug_red")
    # ben in the kitchen but at another spot does not see it; at the counter he does
    w.apply("ben", A("go", place="kitchen_island"), 2)
    assert not w.can_see("ben", "mug_red")
    w.apply("ben", A("go", place="kitchen_counter_by_stove"), 3)
    assert w.can_see("ben", "mug_red")
    # taking the toaster away leaves the mug simply on the counter
    w.apply("ben", A("pick_up", object="toaster_silver"), 4)
    assert w.where["mug_red"] == at_place("kitchen_counter_by_stove", "on", None)
    assert not w.hidden("mug_red")


def test_ref_must_be_at_the_spot():
    w = make()
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ana", A("pick_up", object="mug_red"), 0)
    ok, msg, _ = w.apply("ana", A("put_down", object="mug_red", relation="next_to",
                                  ref="toaster_silver"), 1)
    assert not ok and "not at" in msg


def test_stack_falls_back_when_bottom_taken():
    w = make()
    w.apply("ana", A("go", place="living_coffee_table"), 0)
    w.apply("ana", A("pick_up", object="book_novel"), 0)
    assert w.where["book_atlas"] == at_place("living_coffee_table", "on", None)


def test_bag_contents_travel_and_leave_home():
    w = make()
    w.apply("ben", A("go", place="entry_table"), 0)
    assert not w.can_see("ben", "laptop_work")          # closed bag on the table
    assert w.apply("ben", A("pick_up", object="backpack_black"), 0)[0]
    assert w.can_see("ben", "laptop_work")              # he holds the bag
    assert w.apply("ben", A("pocket", object="keys_ben"), 0)[0]
    ok, _, minutes = w.apply("ben", A("leave_home", minutes=480, text="work"), 1)
    assert ok and minutes == 480
    leave = w.log[-1]
    assert set(leave["carried"]) == {"backpack_black", "keys_ben", "laptop_work"}
    assert w.place_of("laptop_work") is None and w.holder_of("laptop_work") == "ben"
    w.come_home_if_due("ben", 481)
    assert w.people["ben"].at == "entry_table"
    one_spot_each(w)


def test_put_into_bag_and_take_out():
    w = make()
    w.apply("ana", A("go", place="nightstand_left"), 0)
    w.apply("ana", A("pick_up", object="phone_ana"), 0)
    w.apply("ana", A("go", place="entry_table"), 1)
    ok, msg, _ = w.apply("ana", A("put_down", object="phone_ana", relation="in",
                                  ref="backpack_black"), 2)
    assert ok, msg
    assert w.where["phone_ana"] == {"at": "inside", "carrier": "backpack_black"}
    assert set(w.contents("backpack_black")) == {"laptop_work", "phone_ana"}
    # anything can hold things, but not something already inside the thing itself
    w.apply("ana", A("pick_up", object="keys_ben"), 3)
    ok, msg, _ = w.apply("ana", A("put_down", object="keys_ben", relation="in", ref="phone_ana"), 3)
    assert ok, msg
    w.apply("ana", A("pick_up", object="backpack_black"), 3)
    ok, msg, _ = w.apply("ana", A("put_down", object="backpack_black", relation="in", ref="phone_ana"), 3)
    assert not ok and "cannot go inside" in msg
    ok, msg, _ = w.apply("ana", A("pick_up", object="laptop_work"), 4)
    assert ok, msg
    assert w.contents("backpack_black") == ["phone_ana"]


def test_a_bag_with_things_in_it_can_go_in_another_bag_and_both_move():
    w = make()
    objects_extra = {"tote_blue": obj("tote", "entry_table", carrier="closed")}
    w.objects.update(objects_extra)
    w.where["tote_blue"] = dict(objects_extra["tote_blue"]["start"])
    w.apply("ben", A("go", place="entry_table"), 0)
    w.apply("ben", A("pick_up", object="backpack_black"), 0)
    ok, msg, _ = w.apply("ben", A("put_down", object="backpack_black", relation="in", ref="tote_blue"), 0)
    assert ok, msg
    w.apply("ben", A("pick_up", object="tote_blue"), 1)
    w.apply("ben", A("leave_home", minutes=10), 1)
    assert {"tote_blue", "backpack_black", "laptop_work"} <= set(w.log[-1]["carried"])


def test_hidden_place_seen_only_when_there():
    w = make()
    w.apply("ana", A("go", place="nightstand_left"), 0)
    assert not w.can_see("ana", "slipper_left")
    w.apply("ana", A("go", place="under_bed"), 1)
    assert w.can_see("ana", "slipper_left")


def test_not_found_updates_belief_without_revealing():
    w = make()
    # ben moves the mug while ana is elsewhere
    w.apply("ben", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ben", A("pick_up", object="mug_red"), 0)
    w.apply("ben", A("go", place="living_coffee_table"), 1)
    w.apply("ben", A("put_down", object="mug_red"), 2)
    assert w.people["ana"].belief["mug_red"]["pos"]["place"] == "kitchen_counter_by_sink"
    w.apply("ana", A("go", place="kitchen_island"), 3)
    ok, msg, _ = w.apply("ana", A("pick_up", object="mug_red"), 4)
    assert not ok and "living" not in msg
    assert w.people["ana"].belief["mug_red"]["pos"]["at"] == "unknown"


def test_views_list_only_nonempty_and_filter_memory():
    w = make()
    w.apply("ana", A("go", place="kitchen_island"), 0)
    view = w.room_view("ana")
    assert "kitchen_counter_by_sink: mug_red" in view
    assert "kitchen_windowsill" not in view             # empty
    assert "mug_white" not in view                      # in a closed cabinet, not at it
    mem = w.memory_view("ana", {"laptop"})
    assert "laptop_work" in mem and "phone_ana" in mem  # needed type; owned
    assert "book_novel" not in mem


def test_give_needs_same_room():
    w = make()
    w.apply("ana", A("go", place="nightstand_left"), 0)
    w.apply("ana", A("pick_up", object="phone_ana"), 0)
    w.apply("ben", A("go", place="kitchen_island"), 0)
    ok, msg, _ = w.apply("ana", A("give", object="phone_ana", person="ben"), 1)
    assert not ok and "not in this room" in msg
    w.apply("ben", A("go", place="bed"), 1)
    ok, _, _ = w.apply("ana", A("give", object="phone_ana", person="ben"), 2)
    assert ok and w.where["phone_ana"] == {"at": "hand", "person": "ben"}
    one_spot_each(w)


def test_say_to_self_rejected():
    w = make()
    ok, msg, _ = w.apply("ana", A("say", person="ana", text="hi"), 0)
    assert not ok
    assert w.apply("ana", A("say", person="ben", text="hi"), 0)[0]
    assert w.apply("ana", A("say", person="", text="where are my keys"), 0)[0]


def test_wear_frees_hands_and_leaves_with_person():
    w = make()
    w.objects["shirt_blue"] = obj("shirt", "bed")
    w.where["shirt_blue"] = dict(w.objects["shirt_blue"]["start"])
    assert w.apply("ben", A("wear", object="shirt_blue"), 0)[0]
    assert w.people["ben"].hands == [] and w.where["shirt_blue"] == {"at": "worn", "person": "ben"}
    w.apply("ben", A("go", place="entry_table"), 1)
    assert w.apply("ben", A("wear", object="backpack_black"), 1)[0]
    w.apply("ben", A("leave_home", minutes=60), 2)
    assert {"shirt_blue", "backpack_black", "laptop_work"} <= set(w.log[-1]["carried"])
    w.come_home_if_due("ben", 70)
    ok, msg, _ = w.apply("ben", A("put_down", object="shirt_blue", place="entry_coat_hooks"), 70)
    assert ok, msg


def test_owner_labels_in_views():
    w = World(pilot_layout(), make().objects, ["ana", "ben"], {"ana": "bed", "ben": "bed"},
              names={"ana": "Ana", "ben": "Ben"})
    w.apply("ana", A("go", place="entry_table"), 0)
    assert "backpack_black (Ben's)" in w.room_view("ana")
    assert "phone_ana (yours)" in w.memory_view("ana", set())


def test_named_spot_in_another_room_walks_there():
    w = make()
    ok, msg, minutes = w.apply("ana", A("pick_up", object="mug_red", place="kitchen_counter_by_sink"), 0)
    assert ok and minutes == 1 and w.people["ana"].at == "kitchen_counter_by_sink"
    ok, msg, _ = w.apply("ana", A("pick_up", object="book_novel", place="dining_table"), 2)
    assert not ok and "you last saw it" in msg          # in another room, not where she said
    ok, msg, minutes = w.apply("ana", A("put_down", object="mug_red", place="living_coffee_table"), 3)
    assert ok and minutes == 1 and w.room_of_person("ana") == "living_room"


def test_not_found_reminds_own_memory_only():
    w = make()
    w.apply("ben", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ben", A("pick_up", object="mug_red"), 0)
    w.apply("ben", A("go", place="living_coffee_table"), 1)
    w.apply("ben", A("put_down", object="mug_red"), 2)
    w.apply("ana", A("go", place="bed"), 3)
    ok, msg, _ = w.apply("ana", A("pick_up", object="mug_red"), 4)
    assert not ok and "kitchen_counter_by_sink" in msg and "living" not in msg


def test_do_at_named_spot_walks_there():
    w = make()
    ok, _, minutes = w.apply("ana", A("do", place="kitchen_stovetop", minutes=10, text="cook"), 0)
    assert ok and minutes == 11 and w.people["ana"].at == "kitchen_stovetop"


def test_remembered_in_a_bag_that_is_here_marks_unknown_and_labels_contents():
    w = World(pilot_layout(), make().objects, ["ana", "ben"], {"ana": "bed", "ben": "bed"},
              names={"ana": "Ana", "ben": "Ben"})
    # ana takes ben's laptop out of his backpack while ben is elsewhere
    w.apply("ana", A("go", place="entry_table"), 0)
    assert "laptop_work" not in w.room_view("ana")            # closed bag: contents not seen
    w.apply("ana", A("pick_up", object="backpack_black"), 0)
    assert "laptop_work (Ben's)" in w.holding_view("ana")[0]  # holding it: contents seen, labelled
    w.apply("ana", A("pick_up", object="laptop_work"), 0)
    w.apply("ana", A("put_down", object="backpack_black"), 0)
    w.apply("ana", A("go", place="living_coffee_table"), 1)
    w.apply("ana", A("put_down", object="laptop_work"), 1)
    w.apply("ben", A("go", place="entry_key_bowl"), 2)
    ok, msg, _ = w.apply("ben", A("pick_up", object="laptop_work"), 2)
    assert not ok and "not inside backpack_black" in msg
    assert w.people["ben"].belief["laptop_work"]["pos"]["at"] == "unknown"


def test_pocket_goes_into_worn_clothes_and_stays_when_taken_off():
    w = make()
    for oid, o in {"jeans_blue": obj("jeans", "bed", carrier="pockets", owner="ben"),
                   "basket_laundry": obj("basket", "bedroom_chair", carrier="open")}.items():
        w.objects[oid] = o
        w.where[oid] = dict(o["start"])
    w.apply("ben", A("wear", object="jeans_blue"), 0)
    w.apply("ben", A("go", place="entry_key_bowl"), 1)
    assert w.apply("ben", A("pocket", object="keys_ben"), 1)[0]
    assert w.where["keys_ben"] == {"at": "inside", "carrier": "jeans_blue"}
    assert "keys_ben" in w.holding_view("ben")[1]
    w.apply("ben", A("leave_home", minutes=30), 2)
    assert "keys_ben" in w.log[-1]["carried"]
    w.come_home_if_due("ben", 40)
    w.apply("ben", A("go", place="bedroom_chair"), 41)
    # jeans with keys in the pocket go into the laundry basket; keys go with them
    ok, msg, _ = w.apply("ben", A("put_down", object="jeans_blue", relation="in", ref="basket_laundry"), 42)
    assert ok, msg
    assert w.place_of("keys_ben") == "bedroom_chair" and w.hidden("keys_ben")
    assert w.holding_view("ben")[1] == "nothing"
    # without pocketed clothes on, pocket is the person's own
    assert w.apply("ben", A("pick_up", object="keys_ben"), 43)[0]
    assert w.apply("ben", A("pocket", object="keys_ben"), 43)[0]
    assert w.where["keys_ben"] == {"at": "pocket", "person": "ben"}


def test_put_down_and_give_from_pocket_of_worn_clothes():
    w = make()
    w.objects["jeans_blue"] = obj("jeans", "bed", carrier="pockets", owner="ben")
    w.where["jeans_blue"] = dict(w.objects["jeans_blue"]["start"])
    w.apply("ben", A("wear", object="jeans_blue"), 0)
    w.apply("ben", A("go", place="entry_key_bowl"), 1)
    w.apply("ben", A("pocket", object="keys_ben"), 1)
    ok, msg, _ = w.apply("ben", A("put_down", object="keys_ben", place="entry_table"), 2)
    assert ok, msg
    w.apply("ben", A("pocket", object="keys_ben"), 3)
    w.apply("ana", A("go", place="entry_coat_hooks"), 3)
    ok, msg, _ = w.apply("ben", A("give", object="keys_ben", person="ana"), 4)
    assert ok, msg


def test_put_on_top_of_a_thing_still_in_hand_sets_it_down_first():
    w = make()
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ana", A("pick_up", object="mug_red"), 0)
    w.apply("ana", A("go", place="living_coffee_table"), 1)
    w.apply("ana", A("pick_up", object="book_atlas"), 1)
    ok, msg, _ = w.apply("ana", A("put_down", object="mug_red", place="living_coffee_table",
                                  relation="on_top_of", ref="book_atlas"), 2)
    assert ok, msg
    assert w.where["book_atlas"]["place"] == "living_coffee_table"
    assert w.where["mug_red"] == at_place("living_coffee_table", "on_top_of", "book_atlas")
    assert w.people["ana"].hands == []


def test_looking_in_a_closed_drawer_walks_there_and_reports_what_is_in_it():
    w = make()
    w.objects["pen_blue"] = obj("pen", "kitchen_drawer", "in")
    w.where["pen_blue"] = dict(w.objects["pen_blue"]["start"])
    w.objects["spoon_steel"] = obj("spoon", "kitchen_drawer", "in")
    w.where["spoon_steel"] = dict(w.objects["spoon_steel"]["start"])
    for person in w.people.values():
        for o in ("pen_blue", "spoon_steel"):
            person.belief[o] = {"pos": dict(w.where[o]), "day": -1, "minute": 0}
    w.where["pen_blue"] = at_place("office_desk")          # moved where ana did not see
    w.apply("ana", A("go", place="kitchen_island"), 0)
    ok, msg, _ = w.apply("ana", A("pick_up", object="pen_blue"), 1)
    assert not ok and "spoon_steel" in msg and "office" not in msg
    assert w.people["ana"].at == "kitchen_drawer"


def test_hidden_reference_is_not_named_to_someone_who_cannot_see_it():
    w = make()
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ana", A("pick_up", object="mug_red"), 0)
    w.apply("ana", A("put_down", object="mug_red", place="kitchen_counter_by_stove", relation="behind",
                     ref="toaster_silver"), 1)
    w.apply("ana", A("go", place="living_coffee_table"), 2)
    w.apply("ana", A("pick_up", object="book_novel"), 2)
    w.apply("ana", A("put_down", object="book_novel", place="kitchen_counter_by_stove", relation="on_top_of",
                     ref="mug_red"), 3)
    w.apply("ben", A("go", place="kitchen_island"), 4)
    assert "mug_red" not in w.room_view("ben")
    assert w.people["ben"].belief["book_novel"]["pos"]["ref"] is None


def test_others_in_the_room_see_a_move():
    w = make()
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ben", A("go", place="kitchen_island"), 0)
    w.apply("ana", A("pick_up", object="mug_red"), 1)
    assert w.people["ben"].belief["mug_red"]["pos"] == {"at": "hand", "person": "ana"}
