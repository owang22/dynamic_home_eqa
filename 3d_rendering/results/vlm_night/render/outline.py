"""Draw each object the truth file counts in a picture: outline plus a numbered label, and a
list of the numbers below the picture. For checking the ground truth by eye.

    ~/miniconda3/envs/dynamic_eqa/bin/python outline.py <day> <HHMM> <spot> [--min-px 1]
Writes PICS/checks/day_XX_HHMM_<spot>.jpg and prints the list.
"""
import argparse
import json

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

import lib

ap = argparse.ArgumentParser()
ap.add_argument("day", type=int)
ap.add_argument("hhmm")
ap.add_argument("spot")
ap.add_argument("--min-px", type=int, default=1)
a = ap.parse_args()
d = lib.PICS / f"day_{a.day:02d}" / a.hhmm
truth = json.load((d / "truth.json").open())
pic = truth["pictures"][a.spot]
colour = np.array(Image.open(d / pic["picture"]).convert("RGB"))
ids = np.array(Image.open(d / pic["ids_picture"]))
rows = [t for t in pic["objects"] if t["pixels"] >= a.min_px]
im = colour.copy()
for t in rows:
    m = ids == t["semantic_id"]
    if not m.any():
        continue
    edge = m & ~ndimage.binary_erosion(m)
    im[ndimage.binary_dilation(edge)] = (255, 230, 0) if t["visible"] else (255, 60, 200)
canvas = Image.new("RGB", (lib.W, lib.H + 14 * (len(rows) + 1)), "white")
canvas.paste(Image.fromarray(im), (0, 0))
dr = ImageDraw.Draw(canvas)
for n, t in enumerate(rows):
    m = ids == t["semantic_id"]
    if m.any():
        r, c = np.argwhere(m).mean(0)
        dr.rectangle([c - 1, r - 6, c + 12, r + 6], fill="black")
        dr.text((c, r - 6), str(n), fill="white")
    line = (f"{n}: {t['object']} [{t['type']}] {t['pixels']}px {'VISIBLE' if t['visible'] else 'below 30'}"
            f"{' on-spot' if t['on_this_spot'] else ''}{' HIDDEN' if t['hidden_in_snapshot'] else ''}"
            f"{' not-placed' if not t['placed'] else ''}")
    dr.text((4, lib.H + 2 + 14 * n), line[:110], fill="black")
    print(line)
out = lib.PICS / "checks"
out.mkdir(exist_ok=True)
path = out / f"day_{a.day:02d}_{a.hhmm}_{a.spot}.jpg"
canvas.save(path, quality=90)
print(path)
