"""One or more contact sheets per query: python3 mksheets.py [cols] -> sheets/q{n}_{part}.jpg and sheets/index.json"""
import sys, json, os
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/oliver/robot/dynamic_home_eqa/go2/lab_agent")
import memory as M
by = {r["id"]: r for r in M.load()}
pools = json.load(open("pools.json"))
SMALL = {"blue roll of tape", "red screwdriver", "phone", "cup", "water bottle", "power strip", "shoes", "red bottle", "plant", "speaker"}
os.makedirs("sheets", exist_ok=True)
index = {}
for n, (q, items) in enumerate(pools.items()):
    items = sorted(items, key=lambda z: by[z[0]]["t"])
    C, W, per = (2, 600, 8) if q in SMALL else (3, 400, 15)
    H = W * 9 // 16
    for part in range(0, len(items), per):
        chunk = items[part:part + per]
        rows = (len(chunk) + C - 1) // C
        sh = Image.new("RGB", (W * C, (H + 16) * rows), "white"); d = ImageDraw.Draw(sh)
        for k, (i, a) in enumerate(chunk):
            x0, y0 = (k % C) * W, (k // C) * (H + 16)
            sh.paste(Image.open(by[i]["path"]).convert("RGB").resize((W - 4, H)), (x0 + 2, y0 + 16))
            d.text((x0 + 4, y0 + 2), f"#{part + k} {i} {by[i]['time'][4:]}", fill="black")
            if a is not None:
                xa = x0 + 2 + a * (W - 4); d.line([(xa, y0 + 16), (xa, y0 + 30)], fill="red", width=3)
        f = f"sheets/q{n:02d}_{part // per}.jpg"; sh.save(f, quality=85)
    index[q] = [i for i, _ in items]
json.dump(index, open("sheets/index.json", "w"), indent=0)
print(sum(len(v) for v in index.values()), len(os.listdir("sheets")))
