"""Every object's chosen model photographed alone, to check it draws and is the right thing.

Each model is set at the same spot far below the house (black background, same six lights),
photographed at 256x256 from a distance of 2.2 times its longest side, and the share of the
picture it fills is measured from the ids picture. Writes checks/model_sheet_*.jpg and
checks/model_check.json.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import scene  # noqa: E402

S = 256
home = scene.Home(extra_cameras=[dict(uuid="solo", kind="colour", width=S, height=S, hfov=40),
                                 dict(uuid="solo_ids", kind="ids", width=S, height=S, hfov=40)])
home.add_objects()
spot = np.array([0.0, -30.0, 0.0])
tiles, out = [], {}
for oid in sorted(home.snap["objects"]):
    rec = home.records[oid]
    if oid not in home.things:
        out[oid] = {"type": rec["type"], "model": rec["model"], "share": 0.0, "drawn": False}
        continue
    yaw = 0.6
    low, high = home.turn(oid, yaw)
    size = float(np.max(high - low))
    home.set_at(oid, spot[0], spot[1], spot[2])
    mid = spot + np.array([0, (high[1] - low[1]) / 2, 0])
    d = 2.2 * size / (2 * math.tan(math.radians(20)))
    eye = mid + np.array([0, 0.5 * d, 0.87 * d])
    common.look_from(home.sim, eye, mid)
    shot = home.shoot("solo", "solo_ids")
    share = float((shot["solo_ids"] == home.facts[oid]["sid"]).mean())
    out[oid] = {"type": rec["type"], "model": rec["model"], "share": round(share, 4), "drawn": share > 0.002}
    img = Image.fromarray(shot["solo"][:, :, :3]).resize((200, 200))
    draw = ImageDraw.Draw(img)
    m = rec["model"]
    draw.rectangle([0, 0, 200, 30], fill=(0, 0, 0))
    draw.text((3, 2), f"{rec['type'][:22]}", fill=(255, 255, 0))
    draw.text((3, 15), f"{m['source'][:5]} {m.get('looks_like', '')[:24]}", fill=(200, 200, 200))
    tiles.append(img)
    home.park(oid)
per = 48
for k in range(0, len(tiles), per):
    sheet = Image.new("RGB", (8 * 200, 6 * 200))
    for n, t in enumerate(tiles[k:k + per]):
        sheet.paste(t, ((n % 8) * 200, (n // 8) * 200))
    sheet.save(common.OUT / "checks" / f"model_sheet_{k // per + 1}.jpg", quality=85)
(common.OUT / "checks/model_check.json").write_text(json.dumps(out, indent=1))
print("drawn", sum(v["drawn"] for v in out.values()), "of", len(out), "no model", sum(1 for v in out.values() if v["model"].get("source") == "none"))
for oid, v in out.items():
    if not v["drawn"]:
        print("NOT DRAWN", oid, v["model"].get("source"), v["model"].get("id"), v["share"])
