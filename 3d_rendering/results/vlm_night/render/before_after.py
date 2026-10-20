"""Before/after contact sheets: hssd_a (first placement) next to hssd_a_v2 (second placement)
for every picture whose spot has something resting on or in another thing, or something in an
open place (sink, bathtub, fireplace), or a repair of those kinds.

    ~/miniconda3/envs/dynamic_eqa/bin/python before_after.py 5 1000 [7 1200 ...]

Writes hssd_a_v2/checks/before_after_day_XX_HHMM_<n>.jpg (6 pairs per sheet: left before,
right after, with the spot name and the things concerned).
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw

OLD = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a")
NEW = pathlib.Path("/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_v2")
KINDS = {"beside_small_base", "stacked_in_container", "wider_than_container", "sticks_out_of_container",
         "folded_to_fit", "on_neighbours", "open_place_crowded"}


def spots(day, hhmm):
    t = json.load((NEW / f"day_{day:02d}" / hhmm / "truth.json").open())
    snap = json.load(open(t["snapshot"]))
    out = {}
    for oid, o in t["objects"].items():
        if not o["placed"]:
            continue
        on_thing = o["reference_kind"] == "object" and o["relation"] in ("on_top", "inside", "under")
        open_place = o["relation"] == "inside" and o["reference_kind"] == "place" and \
            snap["places"][o["place"]]["kind"] == "open"
        rep = any(r["kind"] in KINDS for r in o.get("repairs", []))
        if (on_thing or open_place or rep) and o["place"] in t["pictures"]:
            out.setdefault(o["place"], []).append(oid)
    return out


def main():
    a = sys.argv[1:]
    w, h, cols, per = 480, 360, 2, 6
    for day, hhmm in zip(map(int, a[0::2]), a[1::2]):
        sp = sorted(spots(day, hhmm).items())
        (NEW / "checks").mkdir(parents=True, exist_ok=True)
        for n0 in range(0, len(sp), per):
            chunk = sp[n0:n0 + per]
            rows = (len(chunk) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * (2 * w + 10), rows * (h + 30)), "white")
            d = ImageDraw.Draw(sheet)
            for k, (spot, oids) in enumerate(chunk):
                x, y = (k % cols) * (2 * w + 10), (k // cols) * (h + 30)
                for m, root in enumerate((OLD, NEW)):
                    f = root / f"day_{day:02d}" / hhmm / f"{spot}.jpg"
                    if f.exists():
                        sheet.paste(Image.open(f).convert("RGB").resize((w, h)), (x + m * w, y + 30))
                d.text((x + 2, y + 1), f"{spot[:70]}   (left: before, right: after)", fill="black")
                d.text((x + 2, y + 14), ", ".join(oids)[:150], fill="blue")
            out = NEW / "checks" / f"before_after_day_{day:02d}_{hhmm}_{n0 // per + 1}.jpg"
            sheet.save(out, quality=85)
            print(out)


if __name__ == "__main__":
    main()
