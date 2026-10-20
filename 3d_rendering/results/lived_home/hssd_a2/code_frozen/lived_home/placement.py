"""Which things may hold which, and what may go on a floor or into a basin.

Two rules, both checked where the world carries out a put_down (world.World._put_down)
and on the household's start positions (household.fix_start_placement), and both
counted on a finished run by lived_home.check_placement.

1. Holding. A thing may sit on top of another thing, or inside it, only when the
   lower thing is a base or container for that kind of thing:
   - on top: a tray, board, plate or coaster takes what fits on it; a book, notebook
     or folder takes paper, pens, glasses, a phone; clothes and towels take clothes
     and towels (a pile); a box, tin or kit takes small things; a bowl takes food,
     cutlery and smaller dishes (an apple on the fruit bowl); a laundry basket takes
     clothes. Nothing else is a base: no sketchbook on a mug, butter on a saucepan,
     folder on a laptop, earplugs on a wallet, metronome on a notebook.
   - inside: only things whose `carrier` is open, closed or pockets hold anything,
     and of those the explicit table below says what: a bag takes what fits; a
     folder takes paper; a pencil case takes pens; a first-aid kit takes medicine; a
     mug or glass takes pens, cutlery, a toothbrush; a laundry basket or laundry bag
     takes clothes; pockets take pocketable things. A thing that is itself a full
     package (yogurt, eggs, a tea tin, tissues, painkillers, a water bottle) holds
     nothing, whatever its `carrier` says.
   Size: what goes on or in a thing is not bigger than it (small < medium < large).

2. Places. A basin (sink, bathtub) takes dishes, cutlery, cups, toiletries and
   cleaning things (a kitchen sink also food being rinsed), not books or clothes.
   A floor (or under a piece of furniture) takes shoes, bags, baskets and boxes,
   floor things (a bath mat, an umbrella, a vacuum), clothes and towels (counted
   separately as lying about), and large things that are not food, dishes or
   electronics; a shower or bath floor also takes toiletries. Not food, not
   electronics, not dishes, not books.

A put_down that breaks rule 1 is carried out next to the lower thing, at the
place where it sits; one that breaks rule 2 goes to a surface of the same
furniture, or else the nearest table, counter or shelf in the room.
"""
from __future__ import annotations

import re
from typing import Optional

SIZE_RANK = {"small": 0, "medium": 1, "large": 2}

# ------------------------------------------------------------------ what a thing is
# Each list is matched as whole words (a trailing s or es allowed) against the type.
CATEGORIES = {
    "food": ("apple", "banana", "butter", "tomato", "tomatoes", "carrot", "coffee beans", "egg",
             "eggs", "flour", "honey", "lemon", "herbs", "milk", "olive oil", "oil", "pasta", "rice",
             "sugar", "tea", "yogurt", "garlic", "onion", "juice", "soda", "sparkling water",
             "hot sauce", "sauce", "bread", "cheese", "cereal", "fruit", "vegetable", "salt cellar",
             "pepper mill", "pepper grinder", "salt grinder", "spice", "jam", "snack", "chocolate",
             "biscuit", "cookie", "potato", "orange", "avocado", "leftover"),
    "dish": ("bowl", "mug", "cup", "plate", "glass", "platter", "saucer", "saucepan", "pan",
             "stockpot", "pot", "skillet", "colander", "baking sheet", "measuring cup", "lunch container",
             "leftover container", "thermos", "water bottle", "jug", "pitcher", "teapot", "kettle",
             "tupperware", "dish", "dishes"),
    "utensil": ("fork", "forks", "knife", "knives", "spoon", "spoons", "ladle", "whisk", "tongs",
                "spatula", "rolling pin", "bottle opener", "corkscrew", "peeler", "can opener",
                "cutting board", "chopping board", "chopsticks", "grater", "measuring spoons",
                "measuring spoon", "kitchen tongs", "straw"),
    "toiletry": ("toothbrush", "toothpaste", "floss", "dental floss", "soap", "hand soap", "shampoo",
                 "conditioner", "hand cream", "lotion", "face wash", "body wash", "moisturizer", "razor",
                 "shaving cream", "deodorant", "cotton swabs", "hairbrush", "comb", "hair clip",
                 "hair tie", "hair ties", "nail clippers", "perfume", "loofah", "toothbrush holder"),
    "cleaning": ("sponge", "dish soap", "cleaning spray", "cloth", "cloths", "microfiber",
                 "rubber gloves", "scrubber", "brush", "toilet brush", "stain remover", "laundry soap",
                 "detergent", "paper towels", "dish towel", "kitchen towel", "tea towel", "tea towels"),
    "electronic": ("phone", "charger", "laptop", "tablet", "headphones", "remote", "remote control",
                   "earbuds", "charging brick", "cable", "ssd", "usb", "mouse", "computer", "metronome",
                   "flashlight", "batteries", "battery", "watch", "kettle", "electric kettle",
                   "food scale", "coffee grinder", "light", "speaker", "camera", "adapter",
                   "music stand light", "laptop stand"),
    "paper": ("book", "paperback", "notebook", "sketchbook", "magazine", "newspaper", "mail", "receipt",
              "receipts", "folder", "pad", "cookbook", "sketches", "notepad", "envelope", "card",
              "recipe card", "map", "sticky notes", "music", "sheet music", "piano music", "binder",
              "journal", "diary", "planner", "papers", "documents", "letter", "fabric samples",
              "photo", "photo frame", "bookmark"),
    "writing": ("pen", "pens", "pencil", "mechanical pencil", "marker", "highlighter", "eraser",
                "ruler", "binder clips", "sticky notes", "bookmark", "scissors", "adhesive tape",
                "tape", "paperweight"),
    "eyewear": ("glasses", "reading glasses", "sunglasses"),
    "medicine": ("painkillers", "painkiller", "medicine", "cold medicine", "plasters", "thermometer",
                 "bandage", "bandages", "pills", "vitamins"),
    "shoe": ("shoe", "shoes", "boot", "boots", "sneaker", "trainer", "slipper", "slippers", "sandal",
             "flats", "heels", "loafers", "loafer", "clog", "clogs", "rain boots"),
    "bag": ("bag", "bags", "backpack", "tote", "purse", "handbag", "pouch", "satchel", "rucksack",
            "briefcase", "suitcase", "luggage", "knife roll"),
    "basket": ("basket", "hamper", "box", "crate", "bin", "parcel", "laundry basket"),
    "textile": ("towel", "towels", "sheet", "sheet set", "pillowcase", "blanket", "throw", "duvet",
                "pillow", "cushion", "napkin", "napkins", "cocktail napkin", "bath mat", "mat", "rug",
                "quilt", "comforter", "apron", "oven mitt", "gardening gloves"),
    "floor_thing": ("umbrella", "spare umbrella", "shoehorn", "toilet brush", "vacuum", "vacuum cleaner",
                    "bath mat", "mat", "rug", "dumbbell", "kettlebell", "laundry basket", "hamper",
                    "trash bag", "bin", "laundry detergent", "parcel", "garment bag"),
    "jewelry": ("earrings", "ring", "necklace", "bracelet", "jewelry"),
}
# word matches that are wrong: category -> types that look like it but are not
NOT_REALLY = {
    "food": ("tea towel", "tea towels"),
    "bag": ("tea bag", "tea bags", "food storage bags", "food storage bag"),
    "textile": ("dryer sheet", "dryer sheets", "sheet music", "sheet music folder", "baking sheet",
                "parchment paper"),
    "clothing": ("hair tie", "hair ties", "tie clip"),
    "paper": ("toilet paper", "parchment paper", "paper towels"),
}
# a full package of its own contents: whatever its `carrier` says, nothing else goes in it
PACKAGES = ("yogurt", "egg", "eggs", "milk", "pasta", "rice", "flour", "honey jar", "honey",
            "coffee beans", "tea tin", "sugar jar", "olive oil", "tissues", "tissue box", "painkillers",
            "painkiller", "medicine", "cold medicine", "plasters", "batteries", "matchbox",
            "water bottle", "thermos", "laundry detergent", "dryer sheets", "dryer sheet",
            "clothespins", "market herbs", "salt cellar", "milk carton", "orange juice", "cotton swabs",
            "hand cream", "parcel", "spare umbrella", "umbrella", "food storage bags", "toilet paper",
            "paper towels", "canvas backpack contents", "sparkling water", "soda can", "hot sauce",
            "yogurt cup", "tea bag", "tea bags", "dryer sheet")


def _words(type_: str) -> str:
    return " " + re.sub(r"[^a-z0-9 ]+", " ", type_.lower()) + " "


def _has(words: str, w: str) -> bool:
    return re.search(rf"(?<![a-z]){re.escape(w)}(?:s|es)?(?![a-z])", words) is not None


def is_clothing(type_: str) -> bool:
    from lived_home.world import _clothing
    t = type_.lower()
    return _clothing(t) or any(_has(_words(t), w) for w in (
        "belt", "cap", "hat", "jacket", "tie", "socks", "sock", "scarf", "underwear", "robe",
        "bathrobe", "sleepwear", "pajama", "leggings", "blazer", "t shirt", "shirt", "sleep mask"))


def tags(type_: str) -> set:
    """The categories a type belongs to (a 'dish towel' is cleaning and textile)."""
    w = _words(type_)
    out = {c for c, words in CATEGORIES.items() if any(_has(w, x) for x in words)}
    if is_clothing(type_):
        out.add("clothing")
    for c, wrong in NOT_REALLY.items():
        if any(x and _has(w, x) for x in wrong):
            out.discard(c)
    if "toiletry" in out and "bag" in out:          # a toiletry bag is a bag
        out.discard("toiletry")
    if "kettle" in w and "electric" not in w:
        out.discard("electronic")
    if _has(w, "glasses") and not (_has(w, "water glass") or _has(w, "wine glass")
                                   or _has(w, "drinking glass")):
        out.discard("dish")                           # reading glasses are not a glass
    if _has(w, "dish towel") or _has(w, "dish soap"):
        out.discard("dish")
    if _has(w, "board") and not (_has(w, "cutting board") or _has(w, "chopping board")):
        out.discard("utensil")
    if "food" in out and ("dish" in out or "utensil" in out) and not _is_package(type_):
        # "salad bowl", "butter knife": the dish, not the food
        if not any(_has(w, x) for x in ("yogurt", "milk", "juice")):
            out.discard("food")
    return out


def _is_package(type_: str) -> bool:
    w = _words(type_)
    return any(_has(w, x) for x in PACKAGES)


def _rank(o: dict) -> int:
    return SIZE_RANK.get(o.get("size"), 1)


def _fits(item: dict, base: dict, strictly: bool = False) -> bool:
    return _rank(item) < _rank(base) if strictly else _rank(item) <= _rank(base)


# ------------------------------------------------------------------ the explicit table
# base role -> what it takes ON TOP ("on") and INSIDE ("in"); a role is chosen from the
# base's type, in this order. Each rule is a set of categories (or "any" for anything
# that fits by size, or "small" for anything small). None: it is not a base that way.
BASE_ROLES = [
    # role,          words in the base's type,                                    on,                              in
    ("pockets",      (),                                                           {"clothing", "textile"},         {"pocketable"}),
    ("laundry",      ("laundry basket", "hamper", "laundry bag", "mesh laundry bag", "delicates bag",
                      "garment bag"),
                     {"clothing", "textile"},                                      {"clothing", "textile"}),
    ("tray",         ("tray", "cutting board", "chopping board", "plate", "platter", "saucer",
                      "placemat", "baking sheet", "dish rack", "serving board"),  {"any"},                         {"any"}),
    ("coaster",      ("coaster",),                                                 {"dish"},                        None),
    ("folder",       ("folder", "binder", "clipboard"),                            {"paper", "writing", "eyewear"}, {"paper", "writing"}),
    ("paper",        ("book", "paperback", "notebook", "sketchbook", "magazine", "newspaper", "pad",
                      "cookbook", "journal", "diary", "planner", "notepad", "music", "sketches"),
                     {"paper", "writing", "eyewear", "phone"},                     None),
    ("first_aid",    ("first-aid kit", "first aid kit", "medicine box", "pill box"),
                     {"small"},                                                    {"medicine", "toiletry"}),
    ("pencil_case",  ("pencil case", "pencil cup", "pen holder"),                  {"writing"},                     {"writing"}),
    ("toothbrush",   ("toothbrush holder",),                                       {"toothbrush"},                  {"toothbrush"}),
    ("stand",        ("laptop stand", "tablet stand", "phone stand", "music stand"),
                     {"stand_things"},                                             None),
    ("wallet",       ("wallet", "card holder"),                           None,                            {"wallet_things"}),
    ("small_case",   ("earbud case", "earplug case", "glasses case", "audio adapter case",
                      "cable organizer", "jewelry box", "button tin", "sewing kit", "case"),
                     {"small"},                                                    {"small"}),
    ("knife_roll",   ("knife roll",),                                              None,                            {"utensil"}),
    ("food_box",     ("lunch container", "leftover container", "food storage", "container"),
                     {"small"},                                                    {"food", "utensil"}),
    ("cup",          ("mug", "cup", "glass", "measuring cup"),                     None,                            {"cup_things"}),
    ("bowl",         ("bowl", "colander", "basket"),                               {"food", "utensil", "bowl_dish", "small"},
                                                                                   {"food", "utensil", "bowl_dish", "small"}),
    ("pot",          ("saucepan", "stockpot", "pot", "skillet", "pan", "wok"),     None,                            {"food", "utensil"}),
    ("bag",          ("bag", "backpack", "tote", "handbag", "pouch", "satchel", "rucksack",
                      "briefcase", "suitcase", "luggage"),                         {"bag"},                         {"any"}),
    ("box",          ("box", "tin", "crate", "chest", "kit", "bin"),               {"small"},                       {"any"}),
    ("textile",      (),                                                           {"clothing", "textile"},         None),
]
CUP_THINGS = ("pen", "pencil", "marker", "highlighter", "toothbrush", "toothpaste", "spoon", "fork",
              "knife", "straw", "tea bag", "infuser", "scissors", "brush", "chopsticks", "whisk",
              "spatula", "ladle", "wooden spoon")
WALLET_THINGS = ("card", "cards", "cash", "receipt", "receipts", "restaurant receipt", "ticket", "coin",
                 "badge", "work badge", "transit map", "key", "keys", "photo", "note")


NOT_BASE = ("binder clips", "music stand light", "paper towels", "toilet paper", "tea bag")


def role(obj: dict) -> Optional[str]:
    """The base role of a thing, or None when nothing may go on or in it. obj has
    the world's fields (type, size, carrier, pocketable); a positions file's `holds`
    is read as `carrier`."""
    t = obj.get("type", "")
    w = _words(t)
    if obj.get("carrier", obj.get("holds")) == "pockets":
        return "pockets"
    if any(_has(w, x) for x in NOT_BASE):
        return None
    for name, words, _on, _in in BASE_ROLES:
        if words and any(_has(w, x) for x in words):
            if name in ("bowl", "cup", "box", "bag", "food_box", "small_case") and _is_package(t):
                return None                      # yogurt cup, tissue box, water bottle: a package
            if name == "cup" and ("eyewear" in tags(t)):
                continue                          # reading glasses
            return name
    if _is_package(t):
        return None
    if {"clothing", "textile"} & tags(t):
        return "textile"
    return None


def _takes(rule: set, item: dict, base: dict, rel: str) -> bool:
    t = item.get("type", "")
    tg = tags(t)
    w = _words(t)
    if "any" in rule:
        return _fits(item, base)
    if "small" in rule and _rank(item) == 0 and _fits(item, base, strictly=_rank(base) > 0) \
            and not {"clothing", "textile"} & tg:
        return True
    if "stand_things" in rule:
        return any(_has(w, x) for x in ("laptop", "tablet", "phone", "sheet music", "music", "book"))
    if rule & {"clothing"} and any(_has(w, x) for x in ("laundry bag", "delicates bag", "mesh laundry bag")):
        return True                               # a laundry bag in the laundry basket
    if "pocketable" in rule:
        return bool(item.get("pocketable"))
    if "cup_things" in rule:
        return _rank(item) == 0 and any(_has(w, x) for x in CUP_THINGS)
    if "wallet_things" in rule:
        return _rank(item) == 0 and any(_has(w, x) for x in WALLET_THINGS)
    if "toothbrush" in rule:
        return _has(w, "toothbrush") or _has(w, "toothpaste")
    if "phone" in rule and (_has(w, "phone") and not _has(w, "charger") or _has(w, "tablet")):
        return True
    if "bowl_dish" in rule and (_has(w, "bowl") or _has(w, "plate")) and _fits(item, base):
        return not any(_has(w, x) for x in ("tray", "platter", "board"))
    hit = rule & (tg - {"bowl_dish"})
    if not hit:
        return False
    if rule & {"clothing", "textile"} and tg & {"clothing", "textile"}:
        return True                               # a pile of clothes or towels: size does not matter
    if rule & {"paper"} and "paper" in tg:
        return True                               # a stack of books
    return _fits(item, base)


def holding_problem(item: dict, base: dict, rel: str) -> str:
    """Why `item` may not go `rel` (on_top or inside) `base`; "" when it may.
    item and base are object records (type, size, carrier, pocketable)."""
    if rel not in ("on_top", "inside"):
        return ""
    r = role(base)
    name = base.get("type", "thing")
    if r is None:
        return f"a {name} is not something to put things {'on' if rel == 'on_top' else 'in'}"
    entry = next((e for e in BASE_ROLES if e[0] == r), None)
    on, inn = entry[2], entry[3]
    if rel == "inside" and base.get("carrier", base.get("holds", "none")) == "none":
        return f"a {name} does not hold things"
    rule = on if rel == "on_top" else inn
    if rule is None:
        return f"a {name} is not something to put things {'on' if rel == 'on_top' else 'in'}"
    if _takes(rule, item, base, rel):
        return ""
    return f"a {item.get('type', 'thing')} does not go {'on' if rel == 'on_top' else 'in'} a {name}"


# ------------------------------------------------------------------ floors and basins
FLOOR_OK = {"shoe", "bag", "basket", "clothing", "textile", "floor_thing"}
FLOOR_NEVER = {"food", "electronic", "dish", "utensil", "paper", "medicine", "eyewear", "jewelry",
               "writing"}
BASIN_OK = {"dish", "utensil", "toiletry", "cleaning"}
KITCHEN_BASIN_OK = BASIN_OK | {"food"}
SHOWER_FLOOR_EXTRA = {"toiletry", "cleaning"}


def place_kind(place, rel: str = "", ref=None) -> str:
    """'floor' or 'basin' when the rule for that kind applies, else ''. Under a thing
    (a coaster under a mug) is where that thing is, not the floor."""
    from lived_home.world import _drop_kind
    kind = _drop_kind(place, "" if ref else rel)
    if kind == "floor":
        return "floor"
    if kind == "wet":
        return "basin"
    return ""


def place_problem(item: dict, place, rel: str = "", ref=None) -> str:
    """Why `item` may not go on (or in, or under) `place`; "" when it may. place is a
    layout.Place; ref the thing it is put relative to, if any."""
    from lived_home.world import _spot_words, _has as w_has
    kind = place_kind(place, rel, ref)
    if not kind:
        return ""
    t = item.get("type", "")
    tg = tags(t)
    if kind == "basin":
        kitchen = "kitchen" in (place.room + " " + place.furniture).lower()
        ok = KITCHEN_BASIN_OK if kitchen else BASIN_OK
        if tg & ok and not (tg & {"clothing", "paper", "electronic"} - ok):
            return ""
        return f"a {t} does not go in a {'kitchen ' if kitchen else ''}basin"
    words = _spot_words(place)
    allowed = set(FLOOR_OK)
    if w_has(words, "shower") or w_has(words, "bath") or w_has(words, "bathtub"):
        allowed |= SHOWER_FLOOR_EXTRA
    never = (FLOOR_NEVER - allowed) & tg
    if never and not tg & {"shoe", "bag", "basket", "floor_thing"}:
        return f"a {t} ({', '.join(sorted(never))}) does not go on the floor"
    if tg & allowed or _rank(item) == 2:
        return ""
    return f"a {t} does not go on the floor"


def nearest_surface(layout, place_id: str, item: dict, near: Optional[str] = None,
                    full=None) -> Optional[str]:
    """Where a thing that may not go at place_id goes instead: a surface of the same
    furniture (the counter by the sink), else the surface nearest to `near` (or to the
    place itself) in the same room that is not a floor, seat, basin, stove or laundry
    drum, else (a hall or entryway with nothing but a floor) the nearest such surface
    in any room, when the home has positions. full(pid) -> True skips a spot with no
    room left."""
    from lived_home.layout import SURFACE
    from lived_home.world import _drop_kind
    p = layout.places[place_id]

    def fine(q):
        return q.id != place_id and q.kind == SURFACE and _drop_kind(q) == "" \
            and not place_problem(item, q) and not (full and full(q.id))
    room = [layout.places[q] for q in layout.places_in(p.room)]
    same = [q for q in room if q.furniture == p.furniture and fine(q)]
    if same:
        return same[0].id
    ref = layout.places.get(near or place_id) or p
    c = (ref.geometry or {}).get("center")

    def dist(q):
        qc = (q.geometry or {}).get("center")
        return sum((a - b) ** 2 for a, b in zip(c, qc)) if qc else 1e9
    others = [q for q in room if fine(q)]
    if others:
        return min(others, key=dist).id if c else others[0].id
    if not c:
        return None
    anywhere = [q for q in layout.places.values() if (q.geometry or {}).get("center") and fine(q)]
    return min(anywhere, key=dist).id if anywhere else None
