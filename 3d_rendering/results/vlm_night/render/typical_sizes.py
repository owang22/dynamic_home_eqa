"""Typical real-world size of every object type in household A, for the v3 size check.

    ~/miniconda3/envs/dynamic_eqa/bin/python typical_sizes.py [--snapshot 4 1000]

Asks the local Qwen3.8-27B (vLLM, port 8300; text only, thinking off, temperature 0, output
forced by a JSON schema) for the three sides in cm of each type, given every `looks` the
household's objects of that type have, as the thing usually sits in a home (clothes and
towels folded, umbrella closed, belt coiled, bags empty and flat). At most 4 requests at a time.
Answers are cached in typical_sizes_v3.json; a type already there is not asked again.

HAND entries below replace the model's answer where it said it was unsure or where its
answer was checked and found wrong; each entry says why. The file records which source
each size came from ("qwen" or "hand").
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import lib

OUT = lib.CODE / "typical_sizes_v3.json"
URL = "http://127.0.0.1:8300/v1/chat/completions"
MODEL = "Qwen/Qwen3.8-27B"
SCHEMA = {"type": "object", "properties": {
    "what_it_is": {"type": "string", "maxLength": 120},
    "longest_cm": {"type": "number", "minimum": 0.5, "maximum": 300},
    "middle_cm": {"type": "number", "minimum": 0.1, "maximum": 300},
    "shortest_cm": {"type": "number", "minimum": 0.05, "maximum": 300},
    "sure": {"type": "boolean"}},
    "required": ["what_it_is", "longest_cm", "middle_cm", "shortest_cm", "sure"]}
PROMPT = """A household object list has an item of type "{typ}". The household's items of this type are described as: {looks}.

Give the typical real-world size of one such item as it usually sits in a home: clothes, towels, sheets and cloths folded; an umbrella closed; a belt coiled; bags empty and lying flat; food in the packaging named (for example "eggs, six brown carton" means a carton holding six eggs, not one egg). If the type names several small things (forks, keys, batteries), give the size of the bunch or pack as it would lie together.

Answer with the three sides of its bounding box in centimetres (longest, middle, shortest), a short phrase saying what you took it to be, and whether you are sure of the size to within about 30%."""

# Hand sizes (cm, longest/middle/shortest) where the model was unsure or checked wrong.
HAND: dict[str, tuple[float, float, float, str]] = {
    "restaurant receipt": (21, 8, 0.1, "Qwen said 100 cm (a till roll); one receipt is about 21 x 8 cm"),
    "market herbs": (25, 12, 10, "Qwen took dried herbs in a jar; the object is fresh basil and mint in a glass"),
    "painkillers": (8, 5, 5, "Qwen took a bottle of liquid; the object is a blue bottle of pills"),
    "piano music book": (31, 23, 1, "Qwen said 40 x 30 cm; a usual piano score is about 31 x 23 cm"),
}


def ask(typ, looks):
    body = {"model": MODEL, "temperature": 0.0, "max_tokens": 300,
            "messages": [{"role": "user", "content": PROMPT.format(typ=typ, looks="; ".join(looks))}],
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_schema", "json_schema": {"name": "size", "schema": SCHEMA}}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            out = json.loads(urllib.request.urlopen(req, timeout=600).read())
            return json.loads(out["choices"][0]["message"]["content"])
        except Exception:  # noqa: BLE001
            if attempt == 2:
                raise
            time.sleep(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", nargs=2, default=["4", "1000"])
    a = ap.parse_args()
    snap = json.load(lib.snapshot_path(int(a.snapshot[0]), a.snapshot[1]).open())
    looks = defaultdict(set)
    for o in snap["objects"].values():
        looks[o["type"]].add(o.get("looks") or "")
    have = json.loads(OUT.read_text()) if OUT.exists() else {"types": {}}
    todo = [t for t in sorted(looks) if t not in have["types"]]
    t0 = time.time()
    with ThreadPoolExecutor(4) as pool:
        for typ, ans in zip(todo, pool.map(lambda t: ask(t, sorted(looks[t])), todo)):
            have["types"][typ] = {"looks": sorted(looks[typ]), "qwen": ans}
    for typ, v in have["types"].items():
        q = v["qwen"]
        dims = sorted([q["longest_cm"], q["middle_cm"], q["shortest_cm"]], reverse=True)
        if typ in HAND:
            *dims, why = HAND[typ]
            v.update(source="hand", why=why)
        else:
            v.update(source="qwen", why=None)
        v["dims_cm"] = [round(float(d), 1) for d in dims]
    have["note"] = ("typical size of each object type (cm, sorted longest first); source qwen = local "
                    "Qwen3.8-27B, text only, thinking off, JSON schema; hand = set by hand (see why)")
    have["prompt"] = PROMPT
    lib.json_dump(have, OUT)
    print(f"{len(todo)} asked in {time.time() - t0:.0f} s; {len(have['types'])} types in {OUT}")


if __name__ == "__main__":
    main()
