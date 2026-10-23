"""Contact sheets for labelling by eye: python3 sheet.py out.jpg id1 id2 ... (2 columns, 640 px each, id + time on top)."""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

PICS = Path(__file__).resolve().parents[3] / "data" / "lab_agent" / "pictures"


def times():
    import glob
    idx = sorted(glob.glob(str(Path(__file__).parent / "data" / "index_snapshot_*.jsonl")))[0]
    return {json.loads(l)["id"]: json.loads(l)["time"][-11:] for l in open(idx)}


def sheet(out, ids, w=640, cols=2):
    T = times()
    ims = []
    for i in ids:
        im = Image.open(PICS / f"{i}.jpg").convert("RGB")
        im = im.resize((w, round(im.height * w / im.width)))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w, 22], fill=(0, 0, 0))
        d.text((4, 4), f"{i}  {T.get(i, '')}", fill=(255, 255, 0))
        ims.append(im)
    h = max(im.height for im in ims)
    rows = (len(ims) + cols - 1) // cols
    S = Image.new("RGB", (w * cols, h * rows), (40, 40, 40))
    for k, im in enumerate(ims):
        S.paste(im, ((k % cols) * w, (k // cols) * h))
    S.save(out, quality=88)


if __name__ == "__main__":
    sheet(sys.argv[1], sys.argv[2:])
