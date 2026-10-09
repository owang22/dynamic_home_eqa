"""Engine rules on the hand-written layout, no model."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from lived_home.layout import pilot_layout          # noqa: E402
from lived_home.world import World, at_place        # noqa: E402


def obj(type_, place, rel="on_top", ref=None, carrier="none", pocketable=False, owner=None, inside=None):
    start = {"at": "inside", "carrier": inside} if inside else at_place(place, rel, ref)
    return {"type": type_, "owner": owner, "pocketable": pocketable, "carrier": carrier,
            "start": start}


def make():
    objects = {
        "mug_red": obj("mug", "kitchen_counter_by_sink"),
        "mug_white": obj("mug", "kitchen_upper_cabinet", "inside"),
        "toaster_silver": obj("toaster", "kitchen_counter_by_stove"),
        "backpack_black": obj("backpack", "entry_table", carrier="closed", owner="ben"),
        "laptop_work": obj("laptop", None, inside="backpack_black", owner="ben"),
        "keys_ben": obj("keys", "entry_key_bowl", pocketable=True),
        "book_novel": obj("book", "living_coffee_table"),
        "book_atlas": obj("book", "living_coffee_table", "on_top", "book_novel"),
        "slipper_left": obj("slipper", "bed", "under"),
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
                                  relation="under", ref="toaster_silver"), 1)
    assert ok, msg
    assert w.where["mug_red"] == at_place("kitchen_counter_by_stove", "under", "toaster_silver")
    assert w.hidden("mug_red")
    # ben in the kitchen but at another spot does not see it; at the counter he does
    w.apply("ben", A("go", place="kitchen_island"), 2)
    assert not w.can_see("ben", "mug_red")
    w.apply("ben", A("go", place="kitchen_counter_by_stove"), 3)
    assert w.can_see("ben", "mug_red")
    # taking the toaster away leaves the mug simply on the counter
    w.apply("ben", A("pick_up", object="toaster_silver"), 4)
    assert w.where["mug_red"] == at_place("kitchen_counter_by_stove", "on_top", None)
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
    assert w.where["book_atlas"] == at_place("living_coffee_table", "on_top", None)


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
    ok, msg, _ = w.apply("ana", A("put_down", object="phone_ana", relation="inside",
                                  ref="backpack_black"), 2)
    assert ok, msg
    assert w.where["phone_ana"] == {"at": "inside", "carrier": "backpack_black"}
    assert set(w.contents("backpack_black")) == {"laptop_work", "phone_ana"}
    # "inside" a phone, which holds nothing, means with it: here, in the bag it is in
    w.apply("ana", A("pick_up", object="keys_ben"), 3)
    ok, msg, _ = w.apply("ana", A("put_down", object="keys_ben", relation="inside", ref="phone_ana"), 3)
    assert ok, msg
    assert w.where["keys_ben"] == {"at": "inside", "carrier": "backpack_black"}
    assert w.log[-1]["ref_as_said"] == "phone_ana"
    w.apply("ana", A("pick_up", object="backpack_black"), 3)
    ok, msg, _ = w.apply("ana", A("put_down", object="backpack_black", relation="inside", ref="phone_ana"), 3)
    assert not ok and "cannot go inside" in msg
    ok, msg, _ = w.apply("ana", A("pick_up", object="laptop_work"), 4)
    assert ok, msg
    assert set(w.contents("backpack_black")) == {"phone_ana", "keys_ben"}


def test_a_bag_with_things_in_it_can_go_in_another_bag_and_both_move():
    w = make()
    objects_extra = {"tote_blue": obj("tote", "entry_table", carrier="closed")}
    w.objects.update(objects_extra)
    w.where["tote_blue"] = dict(objects_extra["tote_blue"]["start"])
    w.apply("ben", A("go", place="entry_table"), 0)
    w.apply("ben", A("pick_up", object="backpack_black"), 0)
    ok, msg, _ = w.apply("ben", A("put_down", object="backpack_black", relation="inside", ref="tote_blue"), 0)
    assert ok, msg
    w.apply("ben", A("pick_up", object="tote_blue"), 1)
    w.apply("ben", A("leave_home", minutes=10), 1)
    assert {"tote_blue", "backpack_black", "laptop_work"} <= set(w.log[-1]["carried"])


def test_under_a_spot_seen_only_when_there():
    w = make()
    assert w.hidden("slipper_left")                     # under the bed
    w.apply("ana", A("go", place="nightstand_left"), 0)
    assert not w.can_see("ana", "slipper_left")
    w.apply("ana", A("go", place="bed"), 1)
    assert w.can_see("ana", "slipper_left")


def test_open_container_contents_seen_closed_not():
    w = make()
    w.where["mug_red"] = at_place("kitchen_sink", "inside", None)
    assert not w.hidden("mug_red")                      # a sink is open
    assert w.hidden("mug_white")                        # in a closed cabinet
    w.apply("ana", A("go", place="kitchen_island"), 0)
    assert "kitchen_sink: mug_red" in w.room_view("ana") and "mug_white" not in w.room_view("ana")


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
    ok, msg, _ = w.apply("ben", A("put_down", object="jeans_blue", relation="inside", ref="basket_laundry"), 42)
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
                                  relation="on_top", ref="book_atlas"), 2)
    assert ok, msg
    assert w.where["book_atlas"]["place"] == "living_coffee_table"
    assert w.where["mug_red"] == at_place("living_coffee_table", "on_top", "book_atlas")
    assert w.people["ana"].hands == []


def test_looking_in_a_closed_drawer_walks_there_and_reports_what_is_in_it():
    w = make()
    w.objects["pen_blue"] = obj("pen", "kitchen_drawer", "inside")
    w.where["pen_blue"] = dict(w.objects["pen_blue"]["start"])
    w.objects["spoon_steel"] = obj("spoon", "kitchen_drawer", "inside")
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
    w.apply("ana", A("put_down", object="mug_red", place="kitchen_counter_by_stove", relation="under",
                     ref="toaster_silver"), 1)
    w.apply("ana", A("go", place="living_coffee_table"), 2)
    w.apply("ana", A("pick_up", object="book_novel"), 2)
    w.apply("ana", A("put_down", object="book_novel", place="kitchen_counter_by_stove", relation="next_to",
                     ref="toaster_silver"), 3)
    w.apply("ben", A("go", place="kitchen_island"), 4)
    view = w.room_view("ben")
    assert "mug_red" not in view and "book_novel (next to toaster_silver)" in view
    assert w.people["ben"].belief["book_novel"]["pos"]["ref"] == "toaster_silver"


def test_others_in_the_room_see_a_move():
    w = make()
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ben", A("go", place="kitchen_island"), 0)
    w.apply("ana", A("pick_up", object="mug_red"), 1)
    assert w.people["ben"].belief["mug_red"]["pos"] == {"at": "hand", "person": "ana"}


def test_memory_for_a_needed_kind_prefers_own_and_shared_things():
    w = make()
    w.objects["laptop_ana"] = obj("laptop", "office_desk", owner="ana")
    w.where["laptop_ana"] = dict(w.objects["laptop_ana"]["start"])
    for person in w.people.values():
        person.belief["laptop_ana"] = {"pos": dict(w.where["laptop_ana"]), "day": -1, "minute": 0}
    mem = w.memory_view("ana", {"laptop"})
    assert "laptop_ana" in mem and "laptop_work" not in mem      # ben's is left out
    mem = w.memory_view("ana", {"backpack"})
    assert "backpack_black" in mem                                # she has none: ben's shows


def test_four_relations_and_defaults():
    w = make()
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ana", A("pick_up", object="mug_red"), 0)
    # on_top of a closed place becomes inside it; inside a surface becomes on_top
    ok, _, _ = w.apply("ana", A("put_down", object="mug_red", place="kitchen_drawer", relation="on_top"), 1)
    assert ok and w.where["mug_red"] == at_place("kitchen_drawer", "inside", None)
    w.apply("ana", A("pick_up", object="mug_red"), 2)
    ok, _, _ = w.apply("ana", A("put_down", object="mug_red", place="kitchen_island", relation="inside"), 3)
    assert ok and w.where["mug_red"] == at_place("kitchen_island", "on_top", None)
    # an unknown relation falls back to the place's default
    w.apply("ana", A("pick_up", object="mug_red"), 4)
    ok, _, _ = w.apply("ana", A("put_down", object="mug_red", place="kitchen_island", relation="behind"), 5)
    assert ok and w.where["mug_red"]["rel"] == "on_top"


def test_not_holding_says_where_when_visible():
    w = make()
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    ok, msg, _ = w.apply("ana", A("put_down", object="mug_red"), 0)
    assert not ok and "on top kitchen_counter_by_sink" in msg


def test_laundry_dirty_after_a_day_clean_after_washing():
    w = make()
    w.objects["jeans_blue"] = obj("jeans", "bed", carrier="pockets", owner="ben")
    w.where["jeans_blue"] = dict(w.objects["jeans_blue"]["start"])
    w.objects["pajama_pants_gray"] = obj("pajama pants", "bed", owner="ben")
    w.where["pajama_pants_gray"] = dict(w.objects["pajama_pants_gray"]["start"])
    w.apply("ben", A("wear", object="jeans_blue"), 0)
    w.apply("ben", A("wear", object="pajama_pants_gray"), 0)
    w.end_of_day()
    assert "jeans_blue" in w.dirty and "pajama_pants_gray" not in w.dirty
    w.apply("ben", A("pick_up", object="jeans_blue"), 1)
    assert "(worn, needs washing)" in w.holding_view("ben")[0]
    w.apply("ben", A("put_down", object="jeans_blue", place="laundry_washer"), 2)
    w.apply("ben", A("do", minutes=40, text="run a wash"), 3)
    assert "jeans_blue" not in w.dirty


def test_positions_place_everything():
    w = make()
    w.apply("ben", A("go", place="entry_table"), 0)
    w.apply("ben", A("pick_up", object="backpack_black"), 0)
    pos = w.positions("scene_x")
    assert set(pos["objects"]) == set(w.objects)
    lap = pos["objects"]["laptop_work"]
    assert lap["relation"] == "inside" and lap["reference"] == "backpack_black" and lap["room"] == "entryway"
    bp = pos["objects"]["backpack_black"]
    assert bp["relation"] == "held_by" and bp["reference"] == "ben" and bp["place"] == "entry_table"
    sl = pos["objects"]["slipper_left"]
    assert sl["relation"] == "under" and sl["reference"] == "bed" and sl["hidden"]
    for o in pos["objects"].values():
        assert o["relation"] in ("inside", "on_top", "under", "next_to", "held_by", "worn_by", "in_pocket_of")
        assert o["place"] is None or o["place"] in pos["places"]


def test_memory_of_a_thing_in_a_carrier_says_where_the_carrier_is():
    w = make()
    w.objects["cup_white"] = obj("cup", "bathroom_sink_counter", carrier="open")
    w.where["cup_white"] = dict(w.objects["cup_white"]["start"])
    w.objects["toothbrush_blue"] = obj("toothbrush", "bathroom_sink_counter", owner="ana")
    w.where["toothbrush_blue"] = {"at": "inside", "carrier": "cup_white"}
    for r in w.people.values():
        r.belief["cup_white"] = {"pos": dict(w.where["cup_white"]), "day": -1, "minute": 0}
        r.belief["toothbrush_blue"] = {"pos": dict(w.where["toothbrush_blue"]), "day": -1, "minute": 0}
    text = w.describe(w.people["ana"].belief["toothbrush_blue"]["pos"], "ana")
    assert text == "inside cup_white, on top bathroom_sink_counter"
    # the cup moved while Ana was elsewhere: she still remembers the old spot
    w.where["cup_white"] = at_place("kitchen_island")
    assert "bathroom_sink_counter" in w.describe(w.people["ana"].belief["toothbrush_blue"]["pos"], "ana")
    assert "kitchen_island" in w.describe(w.where["toothbrush_blue"])


def test_pajamas_come_off_before_day_clothes_go_on():
    w = make()
    for oid, type_ in (("pajama_bottoms_blue", "pajama bottoms"), ("jeans_blue", "jeans"),
                       ("trousers_grey", "work trousers"), ("socks_red", "socks"), ("robe_white", "bathrobe")):
        w.objects[oid] = obj(type_, "bed", owner="ben")
        w.where[oid] = dict(w.objects[oid]["start"])
    assert w.apply("ben", A("wear", object="pajama_bottoms_blue"), 0)[0]
    assert w.apply("ben", A("wear", object="socks_red"), 0)[0]          # socks go with anything
    assert w.apply("ben", A("wear", object="robe_white"), 0)[0]         # a robe over pajamas
    ok, msg, _ = w.apply("ben", A("wear", object="jeans_blue"), 1)
    assert not ok and "pajama_bottoms_blue" in msg and "take it off" in msg
    assert w.apply("ben", A("put_down", object="pajama_bottoms_blue", place="bed"), 2)[0]
    assert w.apply("ben", A("wear", object="jeans_blue"), 3)[0]
    ok, msg, _ = w.apply("ben", A("wear", object="trousers_grey"), 4)
    assert not ok and "jeans_blue" in msg



def test_inside_a_thing_that_holds_nothing_is_next_to_it():
    w = make()
    w.objects["fork_steel"] = obj("fork", "kitchen_counter_by_sink")
    w.where["fork_steel"] = dict(w.objects["fork_steel"]["start"])
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ana", A("pick_up", object="mug_red"), 0)
    ok, msg, _ = w.apply("ana", A("put_down", object="mug_red", relation="inside", ref="fork_steel"), 1)
    assert ok, msg
    assert w.where["mug_red"] == at_place("kitchen_counter_by_sink", "next_to", "fork_steel")
    assert w.log[-1]["relation_as_said"] == "inside"


def test_a_full_spot_refuses_more_unless_stacked():
    w = make()
    w.layout.places["kitchen_counter_by_sink"].geometry = {"area": 0.06}   # room for 0.06 m2
    for i in range(2):
        w.objects[f"plate_{i}"] = dict(obj("plate", "kitchen_counter_by_sink"), size="medium")
        w.where[f"plate_{i}"] = dict(w.objects[f"plate_{i}"]["start"])
    w.objects["mug_red"]["size"] = "medium"
    w.apply("ana", A("go", place="kitchen_counter_by_sink"), 0)
    w.apply("ana", A("pick_up", object="mug_red"), 0)          # 2 plates left: 0.08 > 0.06 already
    ok, msg, _ = w.apply("ana", A("put_down", object="mug_red"), 1)
    assert not ok and "no room" in msg and "plate_0" in msg
    ok, msg, _ = w.apply("ana", A("put_down", object="mug_red", relation="on_top", ref="plate_0"), 2)
    assert ok, msg                                            # stacking takes no more room
    w.layout.places["kitchen_island"].geometry = {}             # no measured area: no limit
    w.apply("ana", A("pick_up", object="mug_red"), 3)
    ok, msg, _ = w.apply("ana", A("put_down", object="mug_red", place="kitchen_island"), 4)
    assert ok, msg
