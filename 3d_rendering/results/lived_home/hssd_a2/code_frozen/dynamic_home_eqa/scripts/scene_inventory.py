#!/usr/bin/env python3
"""
scene_inventory.py — what objects a scene comes with, before generation
touches it: every HSSD-baked object instance (the "predefined" furniture and
decor you see in renders — beds, tables, the big potted plants), grouped by
tier role, plus per-room placement.

Usage:
    python -m dynamic_home_eqa.scripts.scene_inventory 102344022
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene_id")
    ap.add_argument("--per-room", action="store_true", help="also list rooms -> categories")
    args = ap.parse_args()

    from dynamic_home_eqa.env.inventory import (
        TIER1_FURNITURE, TIER2_HSSD_NATIVE, load_scene_state,
    )
    from dynamic_home_eqa.topdown_map import instance_room_positions

    state = load_scene_state(args.scene_id)
    counts: Counter = Counter(inst.category for inst in state.instances.values())

    def tier_of(cat: str) -> str:
        if cat in TIER1_FURNITURE:
            return "Tier-1 anchor (fixed furniture)"
        if cat in TIER2_HSSD_NATIVE:
            return "Tier-2a native movable"
        return "other scene decor (not in any tier — visible but untracked)"

    by_tier: dict[str, list] = defaultdict(list)
    for cat, n in sorted(counts.items()):
        by_tier[tier_of(cat)].append((cat, n))
    print(f"scene {args.scene_id}: {sum(counts.values())} tracked object instances, "
          f"{len(counts)} categories\n")
    for tier in ("Tier-1 anchor (fixed furniture)", "Tier-2a native movable",
                 "other scene decor (not in any tier — visible but untracked)"):
        if by_tier.get(tier):
            print(tier + ":")
            for cat, n in by_tier[tier]:
                print(f"  {cat:20s} x{n}")
            print()

    # Full baked scene contents (everything HSSD placed, including decor the
    # tracking tiers ignore): raw scene_instance.json joined to the HSSD
    # semantics CSV. This is where the "very nice plants" live when they
    # aren't tracked instances.
    import csv as _csv
    import json as _json
    from dynamic_home_eqa.paths import HSSD_DIR
    scene_path = HSSD_DIR / "scenes-uncluttered" / f"{args.scene_id}.scene_instance.json"
    sem_path = HSSD_DIR / "semantics" / "objects.csv"
    cat_by_hash = {}
    with open(sem_path) as f:
        for row in _csv.DictReader(f):
            cat_by_hash[row["id"]] = row.get("main_category", "?")
    raw = _json.loads(scene_path.read_text())
    full = Counter(cat_by_hash.get(o.get("template_name", "").split("/")[-1], "?")
                   for o in raw.get("object_instances", []))
    print(f"FULL baked scene: {sum(full.values())} object instances, "
          f"{len(full)} categories (incl. untracked decor):")
    for cat, n in full.most_common():
        print(f"  {cat:24s} x{n}")
    print()

    if args.per_room:
        print("rooms -> categories (census):")
        for room, cats in sorted(instance_room_positions(args.scene_id).items()):
            print(f"  {room:15s} {', '.join(f'{c}x{len(v)}' for c, v in sorted(cats.items()))}")


if __name__ == "__main__":
    main()
