"""Packs the rendered moments into what the page loads: one data file and sheets of pictures.

    python -m rendered_look.pack

A sheet holds 12 pictures (4 across, 3 down), so a few dozen files carry
several hundred pictures. Only pictures that a moment refers to are packed.
"""
from __future__ import annotations

import importlib
import json
import pathlib

from PIL import Image

from rendered_look import home, timeline
from rendered_look.world import BANKS, REPO

ACROSS, DOWN = 4, 3
DRAWN_ON_THE_MAP = {"bed", "couch", "table", "chair", "chest_of_drawers", "wardrobe", "cabinet",
                    "counter", "shelves", "fridge", "bathtub", "toilet", "shower", "stand", "bench",
                    "fireplace", "washer_dryer", "stool"}


def main(binding_name: str = "rendered_look.binding_hh_s151") -> None:
    binding = importlib.import_module(binding_name)
    source = REPO / "results/rendered_look" / binding.HOUSEHOLD.split("_t")[0]
    out = source / "page"
    (out / "sheets").mkdir(parents=True, exist_ok=True)
    moments = json.load((source / "moments.json").open())
    views = json.load((source / "views.json").open())
    bank = timeline.Bank(BANKS / f"{binding.HOUSEHOLD}.jsonl")

    files = sorted({v["file"] for m in moments for v in m["views"]})
    where = {}
    per_sheet = ACROSS * DOWN
    for start in range(0, len(files), per_sheet):
        group = files[start:start + per_sheet]
        first = Image.open(source / "frames" / group[0])
        width, height = first.size
        sheet = Image.new("RGB", (ACROSS * width, DOWN * height), "black")
        for i, name in enumerate(group):
            sheet.paste(Image.open(source / "frames" / name), ((i % ACROSS) * width, (i // ACROSS) * height))
            where[name] = [start // per_sheet, i]
        sheet.save(out / "sheets" / f"s{start // per_sheet:03d}.jpg", quality=80, optimize=True)

    room_of_region = {region: room for room, region in binding.ROOMS.items()}
    rooms = [{"region": r["name"], "room": room_of_region.get(r["name"]), "label": r["label"],
              "outline": [[round(p[0], 2), round(p[2], 2)] for p in r["poly_loop"]]}
             for r in home.regions_of(binding.HOME)]
    furniture = [{"name": f["name"], "category": f["category"],
                  "box": [f["low"][0], f["low"][2], f["high"][0], f["high"][2]]}
                 for f in json.load((source / "furniture.json").open())
                 if f["category"] in DRAWN_ON_THE_MAP and f["room"]]
    places = {place: {"room": bank.rooms.get(place), "kind": spec["kind"], "called": spec["called"],
                      "stand_in": spec.get("stand_in")}
              for place, spec in binding.PLACES.items()}
    # How much of a thing fills the outline of its box differs from thing to thing:
    # a coiled cable fills little of it even in full view. So each thing is compared
    # with its own best sightings, taken as the 90th percentile of those the edge
    # of the picture does not cut. Below half of that, only part of it shows.
    import numpy as np
    shares = {}
    for moment in moments:
        pose = {p["resident"]: p.get("pose") for p in moment["people"]}
        for view in moment["views"]:
            for p in view["in_picture"]:
                p["kind_for_share"] = f"{p['what']}/{pose.get(p['what'], '')}"
                # a person is tall and the camera looks down, so the edge cuts most
                # sightings of people; their best sightings are taken from all of them
                if p["seen"] and (p["is_person"] or not p.get("cut_by_the_edge")):
                    shares.setdefault(p["kind_for_share"], []).append(p["share_of_its_outline"])
    in_full = {k: float(np.percentile(v, 90)) for k, v in shares.items() if len(v) >= 5}
    for moment in moments:
        for view in moment["views"]:
            for p in view["in_picture"]:
                best = in_full.get(p.pop("kind_for_share"))
                p["share_of_itself"] = (round(min(1.0, p["share_of_its_outline"] / best), 2)
                                        if best else None)
                if p["is_person"]:   # a foot or a knee is not a person seen
                    p["only_part_shows"] = bool(p["pixels"] < 3000 or
                                                (best is not None and p["share_of_its_outline"] < 0.35 * best))
                else:
                    p["only_part_shows"] = bool(p.get("cut_by_the_edge") or
                                                (best is not None and p["share_of_its_outline"] < 0.5 * best))
    for moment in moments:
        for view in moment["views"]:
            view["at"] = where[view.pop("file")]
        for thing in moment["things"].values():
            for key in ("x", "y", "z"):
                if key in thing:
                    thing[key] = round(thing[key], 2)
    data = {
        "household": binding.HOUSEHOLD, "home": binding.HOME,
        "residents": bank.header["protocol"]["residents"],
        "people": binding.PEOPLE,
        "rooms": rooms, "furniture": furniture, "places": places,
        "views": [{k: v for k, v in view.items() if k in ("name", "room", "kind", "place", "eye", "target")}
                  for view in views],
        "sheet": {"across": ACROSS, "down": DOWN, "count": -(-len(files) // per_sheet)},
        "seen_at_least_pixels": 200, "lens_degrees": 75, "counted_at": [960, 720],
        "things_in_the_bank": len(bank.header["object_classes"]),
        "things_drawn": len(bank.asked),
        "moments": moments,
    }
    (out / "data.json").write_text(json.dumps(data, separators=(",", ":")))
    sizes = sum(f.stat().st_size for f in (out / "sheets").glob("s*.jpg"))
    print(f"{len(moments)} moments, {len(files)} pictures in {data['sheet']['count']} sheets, "
          f"{sizes / 1e6:.1f} MB of pictures, data {(out / 'data.json').stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
