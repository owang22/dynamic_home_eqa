"""Before/after contact sheets: hssd_a_v2 (left, 640x480 shown enlarged) next to hssd_a_v3 (right,
1280x960 shown reduced), both shown at 960x720.

    ~/miniconda3/envs/dynamic_eqa/bin/python before_after_v3.py 4 1000 [5 1000 ...]

Pictures chosen per snapshot: every spot named by the independent visual audit (ALWAYS); every spot with an object (visible in v3, >= 120 px, on that spot)
whose model changed in v3; every spot touched by a v3 spreading repair (beside_not_a_carrier,
respaced_on_its_place, moved_on_same_furniture, moved_to_other_furniture, stacked_no_free_surface,
lowered_onto_surface: the spot it was meant for and the spot it was drawn on); the spots before_after.py shows (things on or in things, open places).
Writes hssd_a_v3/checks/v2_v3_day_XX_HHMM_<n>.jpg, 6 pairs per sheet, each titled with the
spot and the objects concerned (blue: model changed, red: moved by the spreading rule).
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

import before_after

OLD = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_v2")
NEW = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_v3")
MOVE = {"beside_not_a_carrier", "respaced_on_its_place", "moved_on_same_furniture", "moved_to_other_furniture",
        "stacked_no_free_surface", "lowered_onto_surface"}
# spots the independent visual audit (2026-10-13) named; always shown when the snapshot has them
ALWAYS = ["bathroom_2_floor", "bedroom_1_bed_in_the_main_bedroom_mattress",
          "bedroom_1_nightstand_by_the_main_bed_top_of_the_nightstand", "kitchen_kitchen_sink_cabinet_kitchen_sink_basin",
          "kitchen_kitchen_sink_cabinet_countertop_beside_the_kitchen_sink", "living_room_living_room_coffee_table_top",
          "kitchen_kitchen_island_island_countertop", "dining_room_dining_table_tabletop",
          "bedroom_1_small_table_by_the_armchair_top_shelf_of_the_small_table",
          "bedroom_1_dresser_by_the_armchair_top_of_the_dresser", "dining_room_coffee_table_by_the_armchairs_tabletop",
          "office_office_desk_desk_top", "kitchen_range_right_cooktop"]


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def chosen(day, hhmm):
    t = json.load((NEW / f"day_{day:02d}" / hhmm / "truth.json").open())
    out = {}
    for spot, p in t["pictures"].items():
        for o in p["objects"]:
            if o["visible"] and o["on_this_spot"] and t["objects"][o["object"]].get("model_change"):
                out.setdefault(spot, {"model": set(), "moved": set()})["model"].add(o["object"])
    for r in t["repairs"]:
        if r["kind"] in MOVE:
            o = t["objects"][r["object"]]
            for spot in {o["place"], o.get("drawn_on")} - {None}:
                if spot in t["pictures"]:
                    out.setdefault(spot, {"model": set(), "moved": set()})["moved"].add(r["object"])
    for spot in ALWAYS:
        if spot in t["pictures"]:
            out.setdefault(spot, {"model": set(), "moved": set()})
    try:
        for spot, oids in before_after.spots(day, hhmm).items():
            out.setdefault(spot, {"model": set(), "moved": set()})
    except FileNotFoundError:
        pass
    return out


def main():
    a = sys.argv[1:]
    w, h, cols, per, top = 960, 720, 2, 6, 64
    f1, f2 = font(26), font(22)
    (NEW / "checks").mkdir(parents=True, exist_ok=True)
    for day, hhmm in zip(map(int, a[0::2]), a[1::2]):
        sp = sorted(chosen(day, hhmm).items())
        for n0 in range(0, len(sp), per):
            chunk = sp[n0:n0 + per]
            rows = (len(chunk) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * (2 * w + 20), rows * (h + top)), "white")
            d = ImageDraw.Draw(sheet)
            for k, (spot, what) in enumerate(chunk):
                x, y = (k % cols) * (2 * w + 20), (k // cols) * (h + top)
                for m, root in enumerate((OLD, NEW)):
                    f = root / f"day_{day:02d}" / hhmm / f"{spot}.jpg"
                    if f.exists():
                        sheet.paste(Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS), (x + m * w, y + top))
                d.text((x + 4, y + 2), f"{spot[:80]}   (left v2 640x480, right v3 1280x960)", fill="black", font=f1)
                d.text((x + 4, y + 32), ", ".join(sorted(what["model"]))[:110], fill="blue", font=f2)
                d.text((x + 4 + w, y + 32), ", ".join(sorted(what["moved"]))[:110], fill="red", font=f2)
            out = NEW / "checks" / f"v2_v3_day_{day:02d}_{hhmm}_{n0 // per + 1}.jpg"
            sheet.save(out, quality=88)
            print(out)


if __name__ == "__main__":
    main()
