"""hssd_layout on one real HSSD home, read from disk (no GPU, no habitat-sim).

Skipped when the HSSD data folder is not on this machine."""
import json
from collections import defaultdict
import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from lived_home import hssd_layout as H  # noqa: E402

SCENE = "105515337_173104347"   # the recommended two-adult home
MARGIN = H.ROOM_MARGIN          # 0.25 m

pytestmark = pytest.mark.skipif(
    not (H.HSSD / "scenes-articulated" / f"{SCENE}.scene_instance.json").exists(),
    reason="HSSD data not found")


@pytest.fixture(scope="module")
def home():
    return H.extract(SCENE)


def _rooms(home):
    return {r["id"]: r for r in home["rooms"]}


def test_header_and_json(home):
    assert home["scene"] == SCENE
    assert home["dataset"] == "hssd-hab articulated"
    again = json.loads(json.dumps(home))
    assert again["spots"] == home["spots"]


def test_ids_unique(home):
    for key in ("rooms", "furniture", "spots"):
        ids = [x["id"] for x in home[key]]
        assert len(ids) == len(set(ids)), key
        assert all(i == i.lower() and " " not in i for i in ids), key


def test_every_room_of_spots_and_furniture_exists(home):
    rooms = _rooms(home)
    furniture = {f["id"] for f in home["furniture"]}
    assert all(f["room"] in rooms for f in home["furniture"])
    for s in home["spots"]:
        assert s["room"] in rooms, s["id"]
        assert s["furniture"] is None or s["furniture"] in furniture, s["id"]
        assert s["kind"] in ("surface", "open", "closed"), s["id"]
        assert 1 <= s["index"] <= s["of"], s["id"]


def test_spot_centres_inside_their_room_and_above_its_floor(home):
    rooms = _rooms(home)
    for s in home["spots"]:
        room = rooms[s["room"]]
        poly = np.array(room["polygon"])
        x, y, z = s["center"]
        assert H.distance_to_polygon(x, z, poly) <= MARGIN, (s["id"], s["room"])
        assert y >= room["floor_height"] - 0.05, s["id"]
        assert abs((y - room["floor_height"]) - s["height"]) < 0.01, s["id"]
        assert -0.05 <= s["height"] <= H.MAX_SPOT_HEIGHT, s["id"]
        assert s["area"] >= H.MIN_SPOT_AREA or s["furniture"] is None, s["id"]


def test_one_floor_spot_per_room(home):
    floors = [s for s in home["spots"] if s["furniture"] is None]
    assert sorted(s["id"] for s in floors) == sorted(f"{r}_floor" for r in _rooms(home))
    assert all(s["kind"] == "surface" and s["height"] == 0.0 for s in floors)


def test_multi_shelf_bookcase_gives_several_heights(home):
    shelves = [f for f in home["furniture"]
               if f["category"] in ("shelf", "bookshelf", "bookcase", "book rack")]
    best = max((sorted({round(s["height"], 2) for s in home["spots"] if s["furniture"] == f["id"]})
                for f in shelves), key=len, default=[])
    assert len(best) > 1, "no shelf unit with more than one level"
    assert len(best) == len(set(best))


def test_closed_spots_exist_and_drawers_are_closed(home):
    closed = [s for s in home["spots"] if s["kind"] == "closed"]
    assert closed
    drawers = [s for s in home["spots"] if "_drawer_" in s["id"]]
    assert drawers and all(s["kind"] == "closed" for s in drawers)
    # a closed spot sits on articulated furniture, or was read from a rigid mesh as a
    # compartment walled in on every side (a drawer or cupboard modelled in one piece)
    arts = {f["id"] for f in home["furniture"] if f["articulated"]}
    assert all(s["furniture"] in arts or s["source"] == "geometry" for s in closed)


def test_drawers_sit_below_the_top_of_their_dresser(home):
    for f in home["furniture"]:
        mine = [s for s in home["spots"] if s["furniture"] == f["id"]]
        tops = [s["height"] for s in mine if s["id"].endswith("_top")]
        drawers = [s["height"] for s in mine if "_drawer_" in s["id"]]
        if tops and drawers:
            assert max(drawers) < max(tops), f["id"]


def test_heights_are_plausible(home):
    """Kitchen worktops ~0.9 m, the desk ~0.75 m, beds 0.4-0.75 m above the floor."""
    cats = {f["id"]: f["category"] for f in home["furniture"]}
    worktops = [s["height"] for s in home["spots"] if s["room"] == "kitchen"
                and s["furniture"] and s["id"].endswith("top") and s["kind"] == "surface"
                and any(w in cats[s["furniture"]] for w in ("cabinet", "counter"))]
    assert len(worktops) >= 3 and all(0.85 <= h <= 0.95 for h in worktops), worktops
    desks = [s["height"] for s in home["spots"] if s["furniture"]
             and "desk" in cats[s["furniture"]] and s["id"].endswith("_top")]
    assert desks and all(0.7 <= h <= 0.8 for h in desks), desks
    beds = [s["height"] for s in home["spots"] if s["furniture"]
            and cats[s["furniture"]] == "bed" and s["index"] == 1]
    assert beds and all(0.4 <= h <= 0.75 for h in beds), beds


def test_receptacles_of_rigid_furniture_lie_on_the_furniture():
    """The glTF node transforms inside receptacle files matter (they flip x and z on
    many assets); with them applied, every receptacle point lies inside the bounding
    box of the object's own render mesh, as habitat-lab places them."""
    trimesh = pytest.importorskip("trimesh")
    scene = H._load_scene(SCENE)
    checked = 0
    for inst in scene["object_instances"]:
        template = inst["template_name"]
        cfg = H._object_config_path(template)
        if cfg is None or not H._receptacle_entries(cfg):
            continue
        render = cfg.parent / f"{template}.glb"
        lo, hi = trimesh.load(str(render), force="scene").bounds
        tol = 0.03 + 0.02 * float((hi - lo).max())
        for entry in H._receptacle_entries(cfg):
            for verts, _ in H._mesh_cached(entry["path"]):
                assert np.all((verts >= lo - tol) & (verts <= hi + tol)), (template, entry["name"])
                checked += 1
    assert checked > 5


def test_door_test_agrees_with_hssd_within_set(home):
    """HSSD's filter file lists receptacles PARTNR says need a link opened (within_set).
    Those on this home's furniture should come out closed (or open for sink basins)."""
    filt = json.loads((H.HSSD / "scene_filter_files/articulated_scene_filter_files"
                       / f"{SCENE}.rec_filter.json").read_text())
    within = {w.split("|")[1] for w in filt["within_set"]}
    kinds = [s["kind"] for s in home["spots"]
             if s["furniture"] and s["source"].split(" on link ")[0] in within]
    assert kinds
    assert sum(k != "surface" for k in kinds) / len(kinds) >= 0.9, kinds


def test_survey_row_fits_two_adults(home):
    row = H.summarise(home)
    assert row["kitchens"] >= 1 and row["living_rooms"] >= 1
    assert row["bedrooms"] >= 2 and row["bathrooms"] >= 1
    assert 100 <= row["spots"] <= 200
    assert row["spots"] == row["spots_surface"] + row["spots_open"] + row["spots_closed"]
    assert row["kitchen_sink"] and row["kitchen_stove"]
    assert H.fits_two_adults(row)


# ---------------------------------------------------------------- render-geometry spots
SECOND = "102344280"   # has washing machines and a sofa whose HSSD receptacles miss the seat


@pytest.fixture(scope="module")
def second():
    return H.extract(SECOND)


def _furniture(home, **match):
    return [f for f in home["furniture"] if all(f.get(k) == v for k, v in match.items())]


def _spots(home, fid):
    return [s for s in home["spots"] if s["furniture"] == fid]


def test_decomposed_furniture_is_read(home):
    """Dining sets and shelf units split into <id>_part_N live two folders down
    (objects/decomposed/<id>/); the living room's dining table must be there with its
    HSSD top at table height."""
    tables = [f for f in _furniture(home, room="living_room") if f["category"] == "table"]
    tops = [s for f in tables for s in _spots(home, f["id"])
            if 0.65 <= s["height"] <= 0.85 and s["area"] >= 1.0]
    assert tops, "no dining table top in the living room"


def test_point1_geometry_spots_for_furniture_without_receptacles(home):
    rooms = {r["id"]: r for r in home["rooms"]}
    geo = [s for s in home["spots"] if s["source"] == "geometry"]
    assert geo and all(s.get("geometry_from") for s in geo)
    cats = {f["id"]: f["category"].replace(" ", "_") for f in home["furniture"]}
    # never on decoration, never on a chair when the room has other seats
    assert not any(cats[s["furniture"]] in H.GEOMETRY_SKIP for s in geo)
    living_chairs = [f["id"] for f in _furniture(home, room="living_room") if f["category"] == "chair"]
    assert len(living_chairs) >= 2 and not any(_spots(home, c) for c in living_chairs)
    # every toilet (no HSSD receptacle) now has a surface: its closed lid or tank top
    toilets = [f for f in home["furniture"] if f["category"] == "toilet"]
    assert toilets and all(any(s["kind"] == "surface" and 0.3 <= s["height"] <= 0.9
                               for s in _spots(home, t["id"])) for t in toilets)
    # the second bathroom, empty before, has places to put things
    assert any(s["furniture"] for s in home["spots"] if s["room"] == "bathroom_2")
    # geometry spots sit on their furniture
    bbox = {f["id"]: f["bbox"] for f in home["furniture"]}
    for s in geo:
        lo, hi = np.array(bbox[s["furniture"]][0]) - 0.05, np.array(bbox[s["furniture"]][1]) + 0.05
        assert np.all(lo <= s["center"]) and np.all(np.array(s["center"]) <= hi), s["id"]
        assert rooms[s["room"]]


def test_point2_articulated_asset_without_receptacles_gets_drawers(home):
    """The two bedside tables in bedroom_1 (urdf 2af8f7c0..., Nightstand0026) ship an
    ao_config with no receptacle at all; each drawer link becomes a closed spot."""
    stands = [f for f in home["furniture"]
              if f["template"] == "2af8f7c0fc1c416b2c24affc510fb8eacef76e23"]
    assert len(stands) == 2
    for f in stands:
        mine = _spots(home, f["id"])
        drawers = [s for s in mine if "drawer" in s["id"]]
        assert len(drawers) == 2 and all(s["kind"] == "closed" for s in drawers), mine
        assert all(s["source"] == "geometry" for s in mine)
        assert len({s["height"] for s in drawers}) == 2
        top = [s for s in mine if s["kind"] == "surface"]
        assert top and max(s["height"] for s in drawers) < max(s["height"] for s in top)


def test_point3_basins_tubs_and_drums(home, second):
    rooms = {r["id"]: r for r in home["rooms"]}
    open_by_type = defaultdict(list)
    for s in home["spots"]:
        if s["kind"] == "open":
            open_by_type[rooms[s["room"]]["type"]].append(s["id"])
    assert any("sink" in i or "basin" in i for i in open_by_type["kitchen"]), open_by_type
    assert any("tub" in i for i in open_by_type["bathroom"]), open_by_type
    assert any("basin" in i for i in open_by_type["bathroom"]), open_by_type
    # the kitchen basin is HSSD's own receptacle "shelf_02", re-labelled, not a duplicate
    kb = [s for s in home["spots"] if s["id"] == "bathroom_cabinet_1_sink_basin"]
    assert kb and kb[0].get("reclassified") and kb[0]["source"] != "geometry"
    assert not [s for s in _spots(home, "bathroom_cabinet_1") if abs(s["height"] - kb[0]["height"]) < 0.05
                and s["id"] != kb[0]["id"]]
    # washing machines get a closed drum below their top
    washers = [f for f in second["furniture"] if f["category"] == "washing machine"]
    assert washers
    for f in washers:
        drum = [s for s in _spots(second, f["id"]) if s["id"].endswith("_drum")]
        top = [s for s in _spots(second, f["id"]) if s["kind"] == "surface"]
        assert drum and drum[0]["kind"] == "closed" and drum[0]["height"] < max(t["height"] for t in top)


def test_point4_sofa_seat_added_when_receptacles_miss_it(home, second):
    # here HSSD's couch receptacles are the seats (0.47 m) and nothing is added
    for f in home["furniture"]:
        if f["category"] == "couch":
            assert not any(s["id"].endswith("_seat") for s in _spots(home, f["id"]))
            assert any(0.4 <= s["height"] <= 0.55 for s in _spots(home, f["id"]))
    # there the Magnolia sofa's receptacles are its arms (0.72 m) and back (0.93 m)
    couch = [f for f in second["furniture"] if f["category"] == "couch"][0]
    seat = [s for s in _spots(second, couch["id"]) if s["id"].endswith("_seat")]
    assert seat and 0.4 <= seat[0]["height"] <= 0.6 and seat[0]["area"] > 0.5


def test_liveability_of_recommended_home(home):
    row = H.summarise(home)
    assert row["live_score"] == 7, row["live_checks"]
