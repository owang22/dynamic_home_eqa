"""Every 3D model household A uses, photographed alone and judged by eye and by the local Qwen.

    ~/miniconda3/envs/dynamic_eqa/bin/python model_check_v3.py v2|v3 [--ask]
    ~/miniconda3/envs/dynamic_eqa/bin/python model_check_v3.py candidates <file.json> [--ask]

v2 / v3: the models chosen by SnapshotHomeV2 / SnapshotHomeV3 (models_v3.json applied) for the
household's objects; one picture per distinct (type, model). candidates: models listed in a
JSON file [{"label", "type", "looks", "mesh", "longest_m"}], to choose replacements.

Each model is set below the house (nothing else in view), scaled as the renderer scales it,
and photographed at 384x384 from two angles (30 deg and 65 deg down, a third of a turn
apart), at 2.2x its longest side, on a plain grey background (from the id picture), with the
renderer's six lights. With --ask, the local Qwen3.8-27B (vLLM :8300, thinking off, answer
forced by a JSON schema, at most 4 requests at a time) is asked whether the picture looks like
a normal, intact <type>, with a verdict from a fixed list and a short reason.

Writes run_v3/model_check/<set>/<n>.jpg (one per model), sheet_<k>.jpg (24 per sheet, with
labels) and check.json (type, model, size, verdict, reason).
"""
from __future__ import annotations

import base64
import json
import math
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image, ImageDraw

import lib_v3
import lib

S = 384
GREY = (150, 150, 150)
VERDICTS = ["looks_right", "right_thing_odd_colour_or_detail", "wrong_kind_of_thing", "broken_or_missing_texture",
            "broken_or_shredded_mesh", "too_coarse", "cannot_tell"]
SCHEMA = {"type": "object", "properties": {"verdict": {"type": "string", "enum": VERDICTS},
                                           "reason": {"type": "string", "maxLength": 200}},
          "required": ["verdict", "reason"]}
PROMPT = """The picture shows one 3D model, seen from two angles (left and right halves), on a plain grey background. In a simulated home it stands for: a {typ} ({looks}).

Judge the model itself. Does it look like a normal, intact {typ} that a person would recognise? Pick one verdict:
- looks_right: a normal, intact {typ}
- right_thing_odd_colour_or_detail: it is a {typ}, but its colour or a detail is odd
- wrong_kind_of_thing: it looks like a different kind of object
- broken_or_missing_texture: texture missing, stretched, smeared, flat single colour where detail is expected, or magenta/checkerboard
- broken_or_shredded_mesh: holes, see-through or inside-out faces, spikes, shredded or exploded geometry
- too_coarse: so blocky or low-detail that it is hard to recognise
- cannot_tell: too small or unclear to judge
Give the verdict and a short reason (one sentence)."""


def ask(img_path, typ, looks):
    data = base64.b64encode(open(img_path, "rb").read()).decode()
    body = {"model": "Qwen/Qwen3.8-27B", "temperature": 0.0, "max_tokens": 200,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{data}"}},
                {"type": "text", "text": PROMPT.format(typ=typ, looks=looks)}]}],
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_schema", "json_schema": {"name": "verdict", "schema": SCHEMA}}}
    req = urllib.request.Request("http://127.0.0.1:8300/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            out = json.loads(urllib.request.urlopen(req, timeout=600).read())
            return json.loads(out["choices"][0]["message"]["content"])
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                return {"verdict": "error", "reason": str(e)[:200]}
            time.sleep(5)


def photograph(home, oid, sid):
    """Two 384x384 views of a placed-alone thing, grey background; returns an RGB image 768x384."""
    spot = np.array([0.0, -30.0, 0.0])
    halves = []
    for yaw, down in ((0.6, 30.0), (0.6 + 2.1, 65.0)):
        low, high = home.turn(oid, 0.0)
        size = float(np.max(high - low))
        home.set_at(oid, *spot)
        mid = spot + np.array([0, (high[1] - low[1]) / 2, 0])
        d = 2.2 * size / (2 * math.tan(math.radians(20)))
        e = math.radians(down)
        eye = mid + d * np.array([math.cos(e) * math.sin(yaw), math.sin(e), math.cos(e) * math.cos(yaw)])
        common = lib.common
        common.look_from(home.sim, eye, mid)
        shot = home.shoot("solo", "solo_ids")
        rgb = shot["solo"][:, :, :3].copy()
        rgb[shot["solo_ids"] != sid] = GREY
        halves.append(Image.fromarray(rgb))
    home.park(oid)
    out = Image.new("RGB", (2 * S, S))
    out.paste(halves[0], (0, 0))
    out.paste(halves[1], (S, 0))
    return out


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    do_ask = "--ask" in sys.argv
    which = a[0]
    cams = [dict(uuid="solo", kind="colour", width=S, height=S, hfov=40),
            dict(uuid="solo_ids", kind="ids", width=S, height=S, hfov=40)]
    snap_file = lib.snapshot_path(4, "1000")
    if which == "v2":
        home = lib.open_home(snap_file, cams, home_class=lib.SnapshotHomeV2)
    else:
        home = lib.open_home(snap_file, cams, home_class=lib_v3.SnapshotHomeV3)
    home.add_objects()
    objs = home.snap["objects"]
    items = []                      # (label, type, looks, model info, oid)
    if which in ("v2", "v3"):
        seen = {}
        for oid in sorted(objs):
            if oid not in home.things:
                continue
            m = home.records[oid]["model"]
            key = (objs[oid]["type"], m.get("id"))
            if key in seen:
                seen[key]["objects"].append(oid)
                continue
            seen[key] = {"type": key[0], "looks": objs[oid].get("looks") or "", "model": m, "oid": oid, "objects": [oid]}
        items = list(seen.values())
        out_dir = lib_v3.RENDER / "run_v3" / "model_check" / which
    else:
        cand = json.load(open(a[1]))
        out_dir = lib_v3.RENDER / "run_v3" / "model_check" / pathlib_stem(a[1])
        for n, c in enumerate(cand):
            sid = 8000 + n
            thing = home.add_model(c["mesh"], 1.0, sid, f"cand{n}@1")
            if thing is None:
                items.append({"type": c["type"], "looks": c.get("looks", ""), "model": {"id": c["label"], "failed": True},
                              "oid": None, "objects": []})
                continue
            size = np.array(thing.root_scene_node.cumulative_bb.size())
            home.rom.remove_object_by_id(thing.object_id)
            sc = c["longest_m"] / float(size.max())
            thing = home.add_model(c["mesh"], sc, sid, f"cand{n}@{sc:.5f}")
            oid = f"__cand_{n}"
            import magnum as mn
            home.things[oid] = thing
            home.facts[oid] = {"sid": sid, "base": mn.Quaternion(), "size": size.tolist()}
            sz = np.array(thing.root_scene_node.cumulative_bb.size())
            items.append({"type": c["type"], "looks": c.get("looks", ""), "oid": oid, "objects": [],
                          "model": {"source": "objaverse", "id": c["label"], "looks_like": c.get("name", ""),
                                    "size_m": [round(float(v), 3) for v in sz]}})
    out_dir.mkdir(parents=True, exist_ok=True)
    for n, it in enumerate(items):
        it["picture"] = str(out_dir / f"{n:03d}.jpg")
        if it["oid"] is None:
            Image.new("RGB", (2 * S, S), (255, 0, 255)).save(it["picture"])
            continue
        photograph(home, it["oid"], home.facts[it["oid"]]["sid"]).save(it["picture"], quality=92)
    if do_ask:
        with ThreadPoolExecutor(4) as pool:
            answers = list(pool.map(lambda it: ask(it["picture"], it["type"], it["looks"]), items))
        for it, ans in zip(items, answers):
            it.update(verdict=ans.get("verdict"), reason=ans.get("reason"))
    # sheets: 4 columns x 6 rows of 2-view tiles (each 2*S x S shrunk to 480x240), with labels
    tw, th = 480, 240
    per = 24
    for k in range(0, len(items), per):
        chunk = items[k:k + per]
        sheet = Image.new("RGB", (4 * tw, 6 * (th + 30)), "white")
        d = ImageDraw.Draw(sheet)
        for n, it in enumerate(chunk):
            x, y = (n % 4) * tw, (n // 4) * (th + 30)
            sheet.paste(Image.open(it["picture"]).resize((tw, th)), (x, y + 30))
            m = it["model"]
            d.text((x + 3, y + 1), f"{k + n:03d} {it['type'][:24]} | {str(m.get('id'))[:12]} {str(m.get('looks_like', ''))[:22]}",
                   fill="black")
            sz = m.get("size_m") or []
            col = "black" if it.get("verdict") in (None, "looks_right") else "red"
            d.text((x + 3, y + 15), f"{'x'.join(f'{100 * v:.0f}' for v in sz)} cm  {it.get('verdict') or ''}", fill=col)
        sheet.save(out_dir / f"sheet_{k // per + 1}.jpg", quality=88)
    for it in items:
        it.pop("oid", None)
    lib.json_dump({"set": which, "verdicts": VERDICTS, "prompt": PROMPT, "items": items}, out_dir / "check.json")
    from collections import Counter
    print(out_dir, len(items), dict(Counter(it.get("verdict") for it in items)))


def pathlib_stem(p):
    import pathlib
    return pathlib.Path(p).stem


if __name__ == "__main__":
    sys.exit(main())
