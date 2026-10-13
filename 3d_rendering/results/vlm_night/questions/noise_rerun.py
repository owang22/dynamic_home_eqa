"""Rerun noise floor: the same arms asked again with an empty answer cache, so every model call is
made fresh (vLLM at temperature 0 is not exactly repeatable). Writes noise/run_<arm>.json, to be
compared item by item with search/run_<arm>.json.

    python noise_rerun.py "llm:truth:truth" "llm:truth:vlm"
"""
import json
import pathlib
import sys

import vlm
import search
from world import World

HERE = pathlib.Path(__file__).parent
vlm.CACHE = HERE / "noise" / "cache"
vlm.CACHE.mkdir(parents=True, exist_ok=True)
search.OUT = HERE / "noise"

W = World()
qs = json.loads((search.OUT / "questions.json").read_text())
for arm in sys.argv[1:]:
    rows = search.run_arm(W, qs, arm)
    print(arm, sum(r["result"] == "found" for r in rows), "found,",
          sum(r["result"] == "false find" for r in rows), "false finds", flush=True)
