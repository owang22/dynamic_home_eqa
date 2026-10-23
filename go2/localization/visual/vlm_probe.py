"""VLM permanence probe (task 4): ask a local VLM which visible things are fixed / rarely moved / movable, with
boxes, and build keep-masks (True = not movable) at 640x360. Results cached per picture in
cache/vlm_<model>/<id>.json (with latency). Concurrency is capped (27B: 3, 8B: 2; other agents share them).
    python3 vlm_probe.py --model 27b --ids results/vlm_probe_ids.json
    python3 vlm_probe.py --model 27b --split x_22v20,x_20v22      # all clean pictures of those splits
"""
from __future__ import annotations

import argparse
import base64
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

import vcommon as V

HERE = Path(__file__).resolve().parent
MODELS = {"27b": ("http://127.0.0.1:8300/v1/chat/completions", "Qwen/Qwen3.8-27B", 2),
          "8b": ("http://127.0.0.1:8301/v1/chat/completions", "Qwen/Qwen3-VL-8B-Instruct-FP8", 2)}
SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "maxItems": 25, "items": {"type": "object", "properties": {
    "name": {"type": "string", "maxLength": 50},
    "permanence": {"type": "string", "enum": ["fixed", "rarely_moved", "movable", "person"]},
    "box": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 1000}, "minItems": 4, "maxItems": 4}},
    "required": ["name", "permanence", "box"]}}}, "required": ["items"]}
ASK = ("A picture from a robot dog's camera, 0.4 m above the floor, in a university robotics lab. The robot wants to "
       "recognise this place again on another day, when chairs, bags, boxes and people may have moved.\n"
       "List up to 25 visible things, largest first. For each:\n"
       "- name: specific and visual (e.g. 'wooden door with metal kick plate', 'whiteboard', 'ceiling light panel', "
       "'tall light-wood cabinet', 'office chair', 'cardboard box').\n"
       "- permanence: 'fixed' = part of the building (walls, doors, door frames, windows, ceiling, ceiling lights, "
       "vents, pipes, wall-mounted whiteboards/TVs/fire extinguishers, built-in counters); 'rarely_moved' = heavy "
       "furniture that stays for months (desks, tall cabinets, filing cabinets, shelving units, sofas, fridges, "
       "large printers, water dispensers); 'movable' = things that move day to day (office chairs, boxes, bags, "
       "bottles, cups, cables, tripods, carts, buckets, mops, jackets, laptops, small robots, monitors on desks "
       "count as rarely_moved); 'person' = people.\n"
       "- box: [x1, y1, x2, y2] around it, in picture coordinates scaled 0-1000 (0,0 = top-left, 1000,1000 = "
       "bottom-right).")


def ask(model, rec):
    url, name, _ = MODELS[model]
    out = HERE / "cache" / f"vlm_{model}" / f"{rec['id']}.json"
    if out.exists():
        return json.loads(out.read_text())
    b = open(rec["path"], "rb").read()
    body = {"model": name, "temperature": 0, "max_tokens": 2500,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(b).decode()}},
                {"type": "text", "text": ASK}]}],
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_schema", "json_schema": {"name": "a", "schema": SCHEMA}}}
    t0 = time.time()
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            resp = json.loads(r.read())
        ch = resp["choices"][0]
        res = {"items": json.loads(ch["message"]["content"])["items"], "latency_s": time.time() - t0,
               "finish": ch.get("finish_reason"), "tokens": resp.get("usage", {}).get("completion_tokens")}
    except Exception as e:  # noqa: BLE001
        res = {"items": [], "latency_s": time.time() - t0, "error": str(e)[:200]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res))
    return res


def keep_mask(items, drop=("movable", "person"), w=640, h=360):
    """True = keep. Boxes of movable things and people are removed, except where a fixed / rarely-moved box that is
    smaller sits on top (boxes overlap a lot; the smaller box is the more specific one)."""
    m = np.ones((h, w), bool)
    for it in sorted(items, key=lambda i: -(i["box"][2] - i["box"][0]) * (i["box"][3] - i["box"][1])):
        x1, y1, x2, y2 = it["box"]
        x1, x2 = sorted((int(x1 * w / 1000), int(x2 * w / 1000))); y1, y2 = sorted((int(y1 * h / 1000), int(y2 * h / 1000)))
        m[y1:y2, x1:x2] = it["permanence"] not in drop
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="27b", choices=list(MODELS))
    ap.add_argument("--ids", default=None)
    ap.add_argument("--split", default=None)
    a = ap.parse_args()
    R = V.load_records()
    if a.ids:
        want = set(json.load(open(a.ids)))
        recs = [r for r in R if r["id"] in want]
    else:
        import vpr_eval as E
        sp = E.splits(R, "clean")
        idx = set()
        for s in a.split.split(","):
            q, db, _ = sp[s]; idx |= set(q.tolist()) | set(db.tolist())
        recs = [R[i] for i in sorted(idx)]
    t0 = time.time()
    with ThreadPoolExecutor(MODELS[a.model][2]) as ex:
        res = list(ex.map(lambda r: ask(a.model, r), recs))
    lat = [x["latency_s"] for x in res]
    print(f"{a.model}: {len(recs)} pictures in {time.time()-t0:.0f} s wall; latency per picture median {np.median(lat):.1f} s, "
          f"p90 {np.percentile(lat, 90):.1f} s; errors {sum('error' in x for x in res)}; items/picture {np.mean([len(x['items']) for x in res]):.1f}")


if __name__ == "__main__":
    main()
