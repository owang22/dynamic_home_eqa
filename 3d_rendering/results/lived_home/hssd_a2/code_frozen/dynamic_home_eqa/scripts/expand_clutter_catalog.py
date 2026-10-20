"""expand_clutter_catalog.py — the offline "LLM proposes, we cheaply approve"
loop for growing the clutter vocabulary without hand-enumerating every object.

Rationale (Option B from the design discussion): the per-run clutter schema is
a closed enum, which guarantees every proposed object is placeable — but it
means new rooms (bathroom, laundry, office, garage) stay empty until someone
lists their objects by hand. Instead: ask the LLM's household prior for the
small movable objects that live in each under-served room, then run each
candidate through a CHEAP approval gate — "can we model where it lives?" =
does its room resolve to a CANONICAL_ROOM. No mesh required: this is about
NOMINAL LOCATION for the EQA world, not rendering. Approved candidates are
written to data/objects/clutter_room_map.json {category: canonical_room},
which env/inventory.py folds into TIER2_CLUTTER_CATALOG (enum inclusion) and
generation/clutter injects as placement guidance (routing).

    python -m dynamic_home_eqa.scripts.expand_clutter_catalog [--rooms ...]
"""
from __future__ import annotations

import argparse
import json
import os
import re

from dynamic_home_eqa.paths import REPO_ROOT
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient
from dynamic_home_eqa.rooms import CANONICAL_ROOMS, normalise_room_name
from dynamic_home_eqa.env.inventory import TIER2_CLUTTER_CATALOG

# under-served rooms are the default target; social rooms already work
_DEFAULT_ROOMS = ["bathroom", "laundry_room", "office", "bedroom", "outdoor"]
_CAT_RE = re.compile(r"^[a-z][a-z_]{1,28}[a-z]$")   # snake_case, sane length


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rooms", nargs="+", default=_DEFAULT_ROOMS)
    ap.add_argument("--per-room", type=int, default=6)
    ap.add_argument("--model", default="Qwen/Qwen3.6-35B-A3B")
    ap.add_argument("--endpoint", default=os.environ.get("GENERATION_ENDPOINT",
                                                         "http://127.0.0.1:8300"))
    ap.add_argument("--out", default=str(REPO_ROOT / "data/objects/clutter_room_map.json"))
    ap.add_argument("--count", type=int, default=2, help="catalog max-instances per new category")
    args = ap.parse_args()

    client = OpenAIHTTPClient(args.endpoint, args.model)
    rooms = [r for r in args.rooms if normalise_room_name(r) in CANONICAL_ROOMS]
    schema = {
        "type": "object", "additionalProperties": False, "required": rooms,
        "properties": {r: {"type": "array", "minItems": 3, "maxItems": args.per_room,
                           "items": {"type": "string", "maxLength": 30}} for r in rooms},
    }
    system = ("You know what small, MOVABLE household objects realistically live "
              "in each room — the kind a person picks up and puts down (not "
              "furniture, not fixtures, not built-ins). For each room, list "
              "distinct such objects as short lowercase snake_case category "
              "names (e.g. hand_towel, toothbrush, hair_dryer). Everyday, "
              "concrete, physically graspable objects only.")
    user = ("Rooms: " + ", ".join(r.replace("_", " ") for r in rooms)
            + "\nList the movable objects for each room.")
    raw = client.generate(system, user, schema, seed=7, temperature=0.4)
    proposed = json.loads(raw)

    existing = set(TIER2_CLUTTER_CATALOG)
    approved: dict[str, str] = {}
    rejected: list[tuple[str, str, str]] = []
    for room, cats in proposed.items():
        canon = normalise_room_name(room)
        for cat in cats:
            c = cat.strip().lower().replace(" ", "_").replace("-", "_")
            if not _CAT_RE.match(c):
                rejected.append((c, room, "bad_name")); continue
            if c in existing or c in approved:
                rejected.append((c, room, "already_known")); continue
            if canon not in CANONICAL_ROOMS:
                rejected.append((c, room, "unroutable_room")); continue
            approved[c] = canon

    payload = {"version": 1, "source": f"llm:{args.model}(seed7)",
               "default_count": args.count, "map": approved}
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=1)
    print(f"approved {len(approved)} new categories -> {args.out}")
    by_room: dict[str, list] = {}
    for c, r in approved.items():
        by_room.setdefault(r, []).append(c)
    for r, cs in sorted(by_room.items()):
        print(f"  {r}: {', '.join(sorted(cs))}")
    print(f"rejected {len(rejected)} "
          f"({sum(1 for _,_,why in rejected if why=='already_known')} already known, "
          f"{sum(1 for _,_,why in rejected if why=='unroutable_room')} unroutable, "
          f"{sum(1 for _,_,why in rejected if why=='bad_name')} bad name)")


if __name__ == "__main__":
    main()
