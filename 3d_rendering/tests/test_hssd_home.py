"""Naming an HSSD home: numbering, the listing, ids built in code, coverage checks,
the kitchen check, and geometry carried through to the layout."""
import copy
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from lived_home import hssd_home as HH          # noqa: E402
from lived_home.layout import CLOSED, OPEN      # noqa: E402

HOME = {
    "scene": "s1",
    "rooms": [{"id": "kitchen", "area": 12.0}, {"id": "hallway", "area": 6.0}],
    "furniture": [
        {"id": "stove_1", "room": "kitchen", "category": "stove", "name": "Gas Range",
         "template": "t_stove", "instance_list": "articulated_object_instances", "instance_index": 3,
         "articulated": True, "position": [1, 0, 1], "rotation": [1, 0, 0, 0], "scale": 1.0},
        {"id": "cabinet_1", "room": "kitchen", "category": "cabinet", "name": "Sink Cabinet",
         "template": "t_cab", "instance_list": "articulated_object_instances", "instance_index": 4,
         "articulated": True, "position": [2, 0, 1], "rotation": [1, 0, 0, 0], "scale": 1.0},
        {"id": "cabinet_2", "room": "kitchen", "category": "cabinet", "name": "Sink Cabinet",
         "template": "t_cab", "instance_list": "articulated_object_instances", "instance_index": 5,
         "articulated": True, "position": [3, 0, 1], "rotation": [1, 0, 0, 0], "scale": 1.0},
        {"id": "table_1", "room": "hallway", "category": "table", "name": "Console",
         "template": "t_tab", "instance_list": "object_instances", "instance_index": 0,
         "articulated": False, "position": [0, 0, 5], "rotation": [1, 0, 0, 0], "scale": 1.0},
    ],
    "spots": [
        {"id": "kitchen_floor", "furniture": None, "room": "kitchen", "kind": "surface",
         "source": "floor", "height": 0.0, "area": 12.0, "center": [2, 0, 2], "index": 1, "of": 1},
        {"id": "stove_1_stove1", "furniture": "stove_1", "room": "kitchen", "kind": "surface",
         "source": "Stove0001_stove1_receptacle_mesh.0000 on link Stove0001", "height": 0.94,
         "area": 0.16, "center": [1, 0.94, 1], "index": 1, "of": 1},
        {"id": "cabinet_1_sink", "furniture": "cabinet_1", "room": "kitchen", "kind": "open",
         "source": "Cab_sink_receptacle_mesh.0000 on link Cab", "height": 0.75, "area": 0.2,
         "center": [2, 0.75, 1], "index": 1, "of": 2},
        {"id": "cabinet_1_drawer", "furniture": "cabinet_1", "room": "kitchen", "kind": "closed",
         "source": "Cab_drawer01_receptacle_mesh.0000 on link drawer01", "height": 0.6, "area": 0.1,
         "center": [2, 0.6, 1], "index": 2, "of": 2, "behind_door": None},
        {"id": "cabinet_2_top", "furniture": "cabinet_2", "room": "kitchen", "kind": "surface",
         "source": "Cab_top_receptacle_mesh.0000 on link Cab", "height": 0.9, "area": 0.3,
         "center": [3, 0.9, 1], "index": 1, "of": 1},
        {"id": "hallway_floor", "furniture": None, "room": "hallway", "kind": "surface",
         "source": "floor", "height": 0.0, "area": 6.0, "center": [0, 0, 5], "index": 1, "of": 1},
        {"id": "table_1_top", "furniture": "table_1", "room": "hallway", "kind": "surface",
         "source": "geometry", "height": 0.8, "area": 0.3, "center": [0, 0.8, 5], "index": 1, "of": 1},
    ],
}


def home():
    return copy.deepcopy(HOME)


def test_numbering_is_room_by_room_and_complete():
    h = home()
    furniture, spots = HH.number(h)
    assert [f["n"] for f in furniture] == [1, 2, 3, 4]
    assert [s["n"] for s in spots] == list(range(1, 8))
    rooms = [s["room"] for s in spots]
    assert rooms == sorted(rooms, key=["kitchen", "hallway"].index)


def test_listing_shows_every_spot_and_maker_label():
    h = home()
    furniture, spots = HH.number(h)
    text = HH.home_text(h, furniture, spots)
    for s in spots:
        assert f"S{s['n']}" in text
    assert "part: stove1" in text and "part: sink" in text and "part: drawer" in text
    assert "doors and drawers can be opened" in text


def test_cover_check_names_repeats_and_gaps():
    check = HH.check_cover("spots", [1, 2, 3])
    assert check({"spots": [{"n": 1}, {"n": 2}, {"n": 3}]}) == ""
    msg = check({"spots": [{"n": 1}, {"n": 1}, {"n": 3}]})
    assert "Repeated: [1]" in msg and "Missing: [2]" in msg


def _names(furniture, spots, fname=None):
    fn = {f["n"]: (fname or {}).get(f["n"], f"{f['category']}") for f in furniture}
    sn = {s["n"]: {"name": "top" if s["kind"] == "surface" else "basin" if s["kind"] == OPEN
                   else "drawer", "descriptions": ["a", "b"]} for s in spots}
    return fn, sn


def test_build_ids_unique_kinds_and_geometry_kept():
    h = home()
    furniture, spots = HH.number(h)
    fn, sn = _names(furniture, spots)
    fn = HH._distinct(fn, furniture)        # two kitchen "cabinet"s
    assert fn[2] != fn[3]
    entry = next(s["n"] for s in spots if s["id"] == "table_1_top")
    lay = HH.build(h, furniture, spots, fn, sn, entry)
    assert len(lay.places) == len(spots)
    assert lay.entry == "hallway_table_top"
    sink = next(p for p in lay.places.values() if p.geometry["hssd_spot"] == "cabinet_1_sink")
    assert sink.kind == OPEN and sink.id == "kitchen_cabinet_basin"
    drawer = next(p for p in lay.places.values() if p.geometry["hssd_spot"] == "cabinet_1_drawer")
    assert drawer.kind == CLOSED
    g = drawer.geometry
    assert g["scene"] == "s1" and g["template"] == "t_cab" and g["instance_index"] == 4
    assert g["center"] == [2, 0.6, 1] and g["position"] == [2, 0, 1]
    floor = lay.places["kitchen_floor"]
    assert floor.furniture == "floor" and "template" not in floor.geometry


def test_kitchen_check():
    h = home()
    furniture, spots = HH.number(h)
    fn, sn = _names(furniture, spots)
    lay = HH.build(h, furniture, spots, HH._distinct(fn, furniture), sn, 1)
    assert HH.check_kitchen(lay) == ""
    h2 = home()
    h2["spots"] = [s for s in h2["spots"] if s["kind"] != "open" and "stove" not in s["id"]]
    furniture, spots = HH.number(h2)
    fn, sn = _names(furniture, spots)
    lay = HH.build(h2, furniture, spots, HH._distinct(fn, furniture), sn, 1)
    msg = HH.check_kitchen(lay)
    assert "cooker" in msg and "sink basin" in msg


class _Caller:
    """Answers the two naming calls like the fake client, and records the stages."""
    def __init__(self):
        from lived_home.fake_client import FakeClient
        import json
        self.fake, self.json, self.stages = FakeClient(), json, []

    def call(self, stage, system, user, schema, check=None, max_tokens=0):
        self.stages.append(stage)
        ans = self.json.loads(self.fake.generate(system, user, schema))
        assert check is None or check(ans) == ""
        return ans


def test_create_layout_one_home_call_and_one_per_room():
    caller = _Caller()
    lay, rec = HH.create_layout(caller, home())
    assert caller.stages == ["create/hssd_home", "create/hssd_room/kitchen", "create/hssd_room/hallway"]
    assert len(lay.places) == 7 and rec["scene"] == "s1"
    assert all(len(p.descriptions) >= 2 for p in lay.places.values())


def test_a_resident_sleeps_on_the_mattress_not_the_headboard():
    from lived_home.household import mattress
    h = home()
    h["furniture"].append({"id": "bed_1", "room": "hallway", "category": "bed", "name": "Bed",
                           "template": "t_bed", "instance_list": "object_instances",
                           "instance_index": 9, "articulated": False, "position": [0, 0, 6],
                           "rotation": [1, 0, 0, 0], "scale": 1.0})
    h["spots"] += [
        {"id": "bed_1_top", "furniture": "bed_1", "room": "hallway", "kind": "surface",
         "source": "x", "height": 0.54, "area": 0.99, "center": [0, 0.5, 6], "index": 1, "of": 2},
        {"id": "bed_1_ledge", "furniture": "bed_1", "room": "hallway", "kind": "surface",
         "source": "x", "height": 0.70, "area": 0.06, "center": [0, 0.7, 6], "index": 2, "of": 2}]
    furniture, spots = HH.number(h)
    fn, sn = _names(furniture, spots)
    sn = {s["n"]: {"name": s["id"], "descriptions": ["a", "b"]} for s in spots}
    lay = HH.build(h, furniture, spots, HH._distinct(fn, furniture), sn, 1)
    ledge = next(p.id for p in lay.places.values() if p.geometry["hssd_spot"] == "bed_1_ledge")
    top = next(p.id for p in lay.places.values() if p.geometry["hssd_spot"] == "bed_1_top")
    assert mattress(lay, ledge) == top and mattress(lay, top) == top
