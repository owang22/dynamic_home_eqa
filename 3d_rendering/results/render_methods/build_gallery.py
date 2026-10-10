"""Build the render-trials picture page: gallery/index.html plus gallery/img/ (JPEG copies).

Run again whenever a trial adds pictures, then republish gallery/index.html with the img/ files.
    ~/miniconda3/envs/dynamic_eqa/bin/python build_gallery.py
"""
from __future__ import annotations

import datetime
import html
import json
import re
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "gallery"
IMG = OUT / "img"
MAX_W = 960

METHODS = [
    ("habitat_hssd", "Habitat + HSSD", "done",
     "Finished. 219 of 251 objects placed in household A's own home. Drawers open with their "
     "contents. No shadows; 20 object types have no model."),
    ("behavior_omnigibson", "BEHAVIOR-1K / OmniGibson", "done",
     "Finished. Our HSSD home loads, but 101 of 208 objects move more than 2 cm in 2 s of physics "
     "(no wall collision, mirrored furniture unmirrored, solid shelves). Cloth does not load as cloth. "
     "In BEHAVIOR's own house, 151 of 220 objects placed and held."),
    ("envdreamer", "EnvDreamer (Unreal Engine 5)", "done",
     "Finished. Code not released, so no test views. These pictures are an Unreal Engine 5 check "
     "on our GPU (not the test) and figures copied from the paper."),
]

VIEWS = {1: "Kitchen counter by the range", 2: "Dining table", 3: "Coffee table",
         4: "Nightstand", 5: "Bathroom vanity", 6: "Entryway floor"}

# earlier settle runs superseded by settle_v2_coacd_locked (the one the report counts)
SKIP = {"settle_rigid", "settle_rigid_locked", "settle_rigid_coacd_locked", "settle_v3_coacd_locked", "load_check"}
SETTLE = "pictures/settle_v2_coacd_locked"

VIEW_RE = re.compile(r"^v?([1-6])_.*?(0\.37|1\.0)0?m")


def convert(src: Path, method: str) -> str:
    rel = src.relative_to(HERE / method)
    dst = IMG / method / rel.with_suffix(".jpg")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        im = Image.open(src).convert("RGB")
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=85)
    return dst.relative_to(OUT).as_posix()


def pretty(stem: str) -> str:
    s = stem.replace("_outlined", "")
    s = re.sub(r"_(0\.37|1\.00?)m", "", s)
    s = re.sub(r"^v?\d_", "", s).replace("_", " ")
    return s


def height(stem: str) -> str:
    m = re.search(r"(0\.37|1\.00?)m", stem)
    return {"0.37": "0.37 m", "1.0": "1.0 m", "1.00": "1.0 m"}.get(m.group(1), "") if m else ""


def last_log(method: str) -> str:
    log = HERE / method / "LOG.md"
    if not log.exists():
        return ""
    entries = re.split(r"\n(?=- \d\d:\d\d )", log.read_text())
    return entries[-1].strip().lstrip("- ") if len(entries) > 1 else ""


def collect():
    data = {}
    for key, *_ in METHODS:
        pics = []
        for src in sorted((HERE / key).rglob("*")):
            if src.suffix.lower() not in (".png", ".jpg", ".jpeg") or "gallery" in src.parts:
                continue
            if "outlined" in src.stem or SKIP & set(src.parts):
                continue
            rel = src.relative_to(HERE / key)
            group = rel.parent.as_posix()
            outlined = src.parent / "checks" / f"{src.stem}_outlined{src.suffix}"
            m = VIEW_RE.match(src.stem)
            pics.append({
                "src": convert(src, key),
                "alt": convert(outlined, key) if outlined.exists() else None,
                "name": pretty(src.stem), "height": height(src.stem), "group": group,
                "view": int(m.group(1)) if m else None,
                "file": f"{key}/{rel.as_posix()}",
            })
        data[key] = pics
    return data


def figure(p, label=None):
    alt = f' data-alt="{p["alt"]}"' if p["alt"] else ""
    cap = html.escape(label or f'{p["name"]}{" · " + p["height"] if p["height"] else ""}')
    return (f'<figure><button class="shot" type="button" data-full="{p["src"]}"{alt}>'
            f'<img loading="lazy" src="{p["src"]}" alt="{cap}"></button>'
            f'<figcaption>{cap}</figcaption></figure>')


def build():
    data = collect()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    title = {k: t for k, t, *_ in METHODS}

    status = []
    for key, name, state, note in METHODS:
        log = last_log(key) if state == "running" else ""
        logp = (f'<p class="log"><span>Latest log entry</span>{html.escape(log[:600])}</p>'
                if log else "")
        status.append(f'<div class="status"><div class="st-head"><h3>{name}</h3>'
                      f'<span class="pill {state}">{state}</span></div>'
                      f'<p>{html.escape(note)}</p><p class="count">{len(data[key])} pictures</p>{logp}</div>')

    # side by side: one row per test view, every set that has numbered views
    sets = []
    for key, *_ in METHODS:
        groups = sorted({p["group"] for p in data[key] if p["view"]})
        for g in groups:
            sets.append((key, g))
    rows = []
    for v, vname in VIEWS.items():
        cells = []
        for key, g in sets:
            ps = sorted([p for p in data[key] if p["view"] == v and p["group"] == g],
                        key=lambda p: p["height"])
            label = title[key] + (f" ({g.split('/')[-1].replace('_', ' ')})" if g != "pictures" else "")
            inner = "".join(figure(p, p["height"]) for p in ps) or '<p class="none">not rendered yet</p>'
            cells.append(f'<div class="cell"><h4>{html.escape(label)}</h4><div class="pair">{inner}</div></div>')
        rows.append(f'<section class="row"><h3><span class="vn">View {v}</span> {vname}</h3>'
                    f'<div class="cells">{"".join(cells)}</div></section>')

    settle = []
    for p in data["behavior_omnigibson"]:
        if p["group"] == SETTLE and p["file"].endswith("_placed.png"):
            after = next((q for q in data["behavior_omnigibson"]
                          if q["file"] == p["file"].replace("_placed.png", "_settled.png")), None)
            spot = p["name"].replace(" placed", "")
            pair = figure(p, "as placed") + (figure(after, "after 2 s") if after else "")
            settle.append(f'<div class="cell"><h4>{html.escape(spot)}</h4><div class="pair">{pair}</div></div>')

    per = []
    for key, name, *_ in METHODS:
        groups = {}
        for p in data[key]:
            if p["group"] == SETTLE:
                continue
            groups.setdefault(p["group"], []).append(p)
        blocks = "".join(
            f'<h4 class="grp">{html.escape(g)}</h4><div class="grid">{"".join(figure(p) for p in ps)}</div>'
            for g, ps in groups.items())
        per.append(f'<section class="method" id="{key}"><h2>{name}</h2>{blocks or "<p class=none>No pictures yet.</p>"}</section>')

    page = (HERE / "gallery_template.html").read_text()
    page = (page.replace("{{UPDATED}}", now).replace("{{STATUS}}", "".join(status))
                .replace("{{ROWS}}", "".join(rows)).replace("{{SETTLE}}", "".join(settle)).replace("{{PER_METHOD}}", "".join(per)))
    (OUT / "index.html").write_text(page)
    files = sorted(p.relative_to(OUT).as_posix() for p in IMG.rglob("*.jpg"))
    (OUT / "files.json").write_text(json.dumps(files, indent=1))
    print(f"{len(files)} pictures, page {len(page)//1024} KB")


if __name__ == "__main__":
    build()
