"""What may hold what, what goes on floors and into basins, measured spot areas."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from lived_home.layout import SURFACE, Place, pilot_layout   # noqa: E402
from lived_home.placement import holding_problem, place_problem   # noqa: E402
from lived_home.world import World, at_place                 # noqa: E402


def thing(type_, size="medium", carrier="none", pocketable=False):
    return {"type": type_, "size": size, "carrier": carrier, "pocketable": pocketable}


# ------------------------------------------------------------------ the rule itself
NOT_BASES = [  # (item, rel, base) seen in household A or B, all implausible
    (thing("sketchbook"), "on_top", thing("mug", carrier="open")),
    (thing("canned tomatoes"), "on_top", thing("carrots")),
    (thing("butter", "small"), "on_top", thing("saucepan")),
    (thing("project folder", carrier="closed"), "on_top", thing("laptop")),
    (thing("earplugs", "small"), "on_top", thing("wallet", "small", "closed")),
    (thing("metronome", "small"), "on_top", thing("music notebook")),
    (thing("wooden tray", "large", "open"), "on_top", thing("mixing bowl", "large", "open")),
    (thing("egg", "small"), "inside", thing("milk carton", "large", "closed")),
    (thing("cocktail napkin", "small"), "on_top", thing("hot sauce", "small")),
    (thing("laptop"), "inside", thing("mug", carrier="open")),
    (thing("towel", "large"), "inside", thing("work trousers", carrier="pockets")),
]
BASES = [      # plausible ones from the same runs
    (thing("painkillers", "small", "closed"), "inside", thing("first-aid kit", carrier="closed")),
    (thing("mail", "small"), "inside", thing("ceramic tray", carrier="open")),
    (thing("paring knife", "small"), "on_top", thing("cutting board", "large")),
    (thing("dish towel", "small"), "on_top", thing("wooden tray", "large", "open")),
    (thing("pen", "small"), "on_top", thing("music notebook")),
    (thing("laptop"), "inside", thing("tote bag", "large", "closed")),
    (thing("work blouse"), "inside", thing("laundry basket", "large", "open")),
    (thing("phone", "small", pocketable=True), "inside", thing("work trousers", carrier="pockets")),
    (thing("towel"), "on_top", thing("towel")),
    (thing("apple", "small"), "on_top", thing("bowl", carrier="open")),
    (thing("tea bag", "small"), "inside", thing("mug", carrier="open")),
    (thing("work laptop"), "on_top", thing("laptop stand")),
]


def test_things_that_are_no_base_are_refused():
    for item, rel, base in NOT_BASES:
        assert holding_problem(item, base, rel), (item["type"], rel, base["type"])


def test_plausible_bases_and_containers_are_allowed():
    for item, rel, base in BASES:
        assert holding_problem(item, base, rel) == "", (item["type"], rel, base["type"])


def test_size_matters_for_trays_and_bags():
    assert holding_problem(thing("stockpot", "large"), thing("plate", "small"), "on_top")
    assert holding_problem(thing("backpack", "large", "closed"), thing("pencil case", "small", "closed"), "inside")


def floor(room="entryway"):
    return Place(f"{room}_floor", room, "floor", "floor", SURFACE, geometry={"height": 0.0})


def test_floors_take_shoes_bags_and_baskets_not_food_or_electronics():
    f = floor()
    for ok in ("running shoes", "backpack", "laundry basket", "umbrella", "jeans", "bath mat"):
        assert place_problem(thing(ok), f) == "", ok
    for bad in ("phone", "laptop", "apple", "mug", "paperback book", "keys"):
        assert place_problem(thing(bad, "small"), f), bad
    # under a thing on a table is not the floor; under the bed is
    table = Place("t", "living_room", "coffee table", "top", SURFACE)
    assert place_problem(thing("coaster", "small"), table, "under", "mug_red") == ""
    assert place_problem(thing("apple", "small"), table, "under") != ""   # under the table: floor


def test_basins_take_dishes_and_toiletries_not_books_or_clothes():
    sink = pilot_layout().places["kitchen_sink"]
    tub = Place("tub", "bathroom", "bathtub", "bathtub", "open")
    assert place_problem(thing("mug"), sink) == ""
    assert place_problem(thing("carrots"), sink) == ""                   # rinsed in a kitchen sink
    assert place_problem(thing("shampoo"), tub) == ""
    assert place_problem(thing("paperback book"), sink)
    assert place_problem(thing("hoodie"), tub)
    assert place_problem(thing("carrots"), tub)
    # a shelf beneath the sink is storage, not the basin
    shelf = Place("s", "kitchen", "kitchen sink cabinet", "shelf beneath the kitchen sink", "open")
    assert place_problem(thing("paperback book"), shelf) == ""


# ------------------------------------------------------------------ in the world
def obj(type_, place, rel="on_top", ref=None, carrier="none", size="medium", inside=None, pocketable=False):
    start = {"at": "inside", "carrier": inside} if inside else at_place(place, rel, ref)
    return {"type": type_, "owner": None, "pocketable": pocketable, "carrier": carrier, "size": size,
            "start": start}


def make(rules=True):
    lay = pilot_layout()
    lay.places["entry_floor"] = floor()
    lay.rooms["entryway"].append("entry_floor")
    objects = {
        "mug_red": obj("mug", "kitchen_counter_by_sink", carrier="open"),
        "sketchbook_green": obj("sketchbook", "living_coffee_table"),
        "tray_wood": obj("wooden tray", "kitchen_island", carrier="open", size="large"),
        "keys_ben": obj("keys", "living_coffee_table", size="small", pocketable=True),
        "shoes_ben": obj("running shoes", "living_coffee_table"),
        "book_novel": obj("paperback book", "kitchen_island"),
        "milk_carton": obj("milk carton", "kitchen_fridge", "inside", carrier="closed", size="large"),
        "egg_brown": obj("egg", None, size="small", inside="milk_carton"),
    }
    w = World(lay, objects, ["ana"], {"ana": "living_coffee_table"})
    w.rules = {"holding": rules, "places": rules}
    return w


def A(verb, **kw):
    return {"verb": verb, **kw}


def test_put_on_something_that_is_no_base_goes_next_to_it():
    w = make()
    w.apply("ana", A("pick_up", object="sketchbook_green"), 0)
    ok, msg, _ = w.apply("ana", A("put_down", object="sketchbook_green", place="kitchen_counter_by_sink",
                                  relation="on_top", ref="mug_red"), 1)
    assert ok, msg
    assert w.where["sketchbook_green"] == at_place("kitchen_counter_by_sink", "next_to", "mug_red")
    e = w.log[-1]
    assert e["redirected"] and e["relation_as_said"] == "on_top" and e["ref_as_said"] == "mug_red"


def test_a_tray_still_takes_things_and_rules_off_restore_the_old_behaviour():
    w = make()
    w.apply("ana", A("pick_up", object="sketchbook_green"), 0)
    ok, msg, _ = w.apply("ana", A("put_down", object="sketchbook_green", place="kitchen_island",
                                  relation="on_top", ref="tray_wood"), 1)
    assert ok and w.where["sketchbook_green"] == at_place("kitchen_island", "on_top", "tray_wood")
    w = make(rules=False)
    w.apply("ana", A("pick_up", object="sketchbook_green"), 0)
    ok, msg, _ = w.apply("ana", A("put_down", object="sketchbook_green", place="kitchen_counter_by_sink",
                                  relation="on_top", ref="mug_red"), 1)
    assert ok and w.where["sketchbook_green"] == at_place("kitchen_counter_by_sink", "on_top", "mug_red")


def test_inside_something_that_holds_nothing_of_the_kind_goes_next_to_it():
    w = make()
    w.apply("ana", A("pick_up", object="keys_ben"), 0)
    ok, msg, _ = w.apply("ana", A("put_down", object="keys_ben", place="kitchen_counter_by_sink",
                                  relation="inside", ref="mug_red"), 1)
    assert ok, msg
    assert w.where["keys_ben"] == at_place("kitchen_counter_by_sink", "next_to", "mug_red")


def test_floor_and_basin_redirects():
    w = make()
    w.apply("ana", A("pick_up", object="keys_ben"), 0)
    w.apply("ana", A("pick_up", object="shoes_ben"), 0)
    w.apply("ana", A("go", place="entry_table"), 1)
    ok, msg, _ = w.apply("ana", A("put_down", object="shoes_ben", place="entry_floor"), 2)
    assert ok and w.where["shoes_ben"]["place"] == "entry_floor"
    ok, msg, _ = w.apply("ana", A("put_down", object="keys_ben", place="entry_floor"), 2)
    assert ok, msg
    got = w.where["keys_ben"]["place"]
    assert got != "entry_floor" and w.layout.room_of(got) == "entryway"
    assert w.log[-1]["place_as_said"] == "entry_floor"
    # a book dropped into the kitchen sink lands on a kitchen surface instead
    w.apply("ana", A("go", place="kitchen_island"), 3)
    w.apply("ana", A("pick_up", object="book_novel"), 3)
    ok, msg, _ = w.apply("ana", A("put_down", object="book_novel", place="kitchen_sink"), 4)
    assert ok and w.where["book_novel"]["place"] != "kitchen_sink"
    assert w.layout.places[w.where["book_novel"]["place"]].kind == SURFACE


def test_start_positions_follow_the_rules():
    from lived_home.household import fix_start_placement
    w = make()
    objs = [dict(o, id=k) for k, o in w.objects.items()]
    objs.append(dict(obj("phone", "entry_floor", size="small"), id="phone_ana"))
    changed = dict(fix_start_placement(objs, w.layout))
    by = {o["id"]: o for o in objs}
    assert by["egg_brown"]["start"] == at_place("kitchen_fridge", "next_to", "milk_carton")
    assert by["phone_ana"]["start"]["place"] != "entry_floor"
    assert set(changed) == {"egg_brown", "phone_ana"}


# ------------------------------------------------------------------ areas and the checker
def test_measured_area_used_unless_the_scan_is_doubtful():
    from lived_home.measured_areas import apply, capacity_area
    assert capacity_area({"area": 2.545}, {"scanned": 1.344, "assumed": 2.545}) == (1.344, "scanned")
    assert capacity_area({"area": 0.109}, {"scanned": 0.002, "assumed": 0.109})[1] == "assumed (scan doubtful)"
    assert capacity_area({"area": 0.5}, None) == (0.5, "assumed")
    lay = pilot_layout()
    lay.places["dining_table"].geometry = {"area": 2.545}
    import lived_home.measured_areas as m
    real = m.load
    m.load = lambda scene: {"dining_table": {"scanned": 1.344, "assumed": 2.545}}
    try:
        apply(lay, "x")
        apply(lay, "x")                       # twice: still from the assumed value
    finally:
        m.load = real
    g = lay.places["dining_table"].geometry
    assert g["area"] == 1.344 and g["area_assumed"] == 2.545 and g["area_from"] == "scanned"


def test_checker_counts_what_the_rule_forbids_and_overfull_spots():
    from lived_home.check_placement import holding_violations, overfull
    objects = {"a": dict(thing("sketchbook"), id="a"), "b": dict(thing("mug", carrier="open"), id="b"),
               "c": dict(thing("pen", "small"), id="c"), "d": dict(thing("notebook"), id="d")}
    state = {"objects": {
        "a": {"relation": "on_top", "reference": "b", "reference_kind": "object", "place": "t", "size": "medium"},
        "b": {"relation": "on_top", "reference": "t", "reference_kind": "place", "place": "t", "size": "medium"},
        "c": {"relation": "on_top", "reference": "d", "reference_kind": "object", "place": "t", "size": "small"},
        "d": {"relation": "on_top", "reference": "t", "reference_kind": "place", "place": "t", "size": "medium"}}}
    assert [v[:3] for v in holding_violations(state, objects)] == [("a", "on_top", "b")]
    assert overfull(state, {"t": (0.1, SURFACE)}) == []           # 0.04 + 0.04 resting
    assert overfull(state, {"t": (0.05, SURFACE)}) == [("t", 0.08, 0.05)]
