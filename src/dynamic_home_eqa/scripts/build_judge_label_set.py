#!/usr/bin/env python3
"""
build_judge_label_set.py — extract a human-labeling CSV of judge candidates
(Phase 1a of the prompting-infrastructure work).

Reads generation_result.json from a set of generation folders (each must
carry the post-P0 `candidates` field: every grounded candidate with its
strict-judge `_judge_score` and full context), selects ~N candidates that
deliberately span the quality range — obvious positives, obvious negatives
(electronics at meals, appliance-surface placements, food in the bathroom),
and the murky middle — and writes one CSV row per candidate.

Each row carries the full context a labeler needs (scene, occupant, activity,
time window, object, relation, anchor, room, proposed reason) plus a
machine-suggested band mapped from the strict-judge score. The `band` column
is prefilled with that suggestion for the human to correct; `machine_band`
preserves the original suggestion so human-vs-machine agreement is
measurable; `notes` is for the labeler.

Selection is deterministic (fixed --seed). The EVAL/EXEMPLAR split happens
later, on the returned labels, not here.

Usage:
    python -m dynamic_home_eqa.scripts.build_judge_label_set \
        --folders 102343992_family_with_kids 102344022_family_with_kids \
                  102344049_family_with_kids \
        --gen-dir generation_out_labelset --n 60
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import random

from dynamic_home_eqa.judge_eval.metrics import BAND_LABEL, score_to_band
from dynamic_home_eqa.paths import REPO_ROOT

# True mobile electronics (NOT keys/wallet — those plausibly sit on a
# counter during cooking; the canonical negative is a laptop at the meal).
_ELECTRONICS = {"laptop", "phone", "tablet", "computer"}
_MEAL_KEYWORDS = ("breakfast", "lunch", "dinner", "meal", "cook", "snack", "eat")
# Furniture tokens (the part AFTER the "." in a room.furniture_N anchor) that
# cannot hold a placed object — putting something ON these is absurd. Note
# "tv" appears as a ROOM prefix (tv.couch_1 = a couch in the TV room), so it
# is deliberately NOT here: match the furniture token only.
_APPLIANCE_FURNITURE = ("fridge", "oven", "stove", "microwave", "dishwasher", "toilet")
_BATHROOM_ROOMS = ("bathroom", "toilet", "washroom")
_EATING_SURFACES = ("table", "counter", "island")
_FOOD_DRINK = {"cup", "bottle", "drinkware", "bowl", "plate", "food"}
_SURFACE_RELS = {"on", "on_top", "inside", "within"}


def _anchor_parts(anchor: str) -> tuple[str, str]:
    """Split a 'room.furniture_N' anchor into (room, furniture_token). For a
    bare region anchor ('kitchen') the room is the whole string and furniture
    is ''. Trailing _N index is stripped from the furniture token."""
    a = (anchor or "").lower()
    if "." in a:
        room, furn = a.split(".", 1)
    else:
        room, furn = a, ""
    furn = furn.rsplit("_", 1)[0] if furn and furn.rsplit("_", 1)[-1].isdigit() else furn
    return room, furn


def obvious_negative(c: dict) -> str:
    """Return a short reason if this candidate is an obvious behavioral
    negative regardless of the judge's score, else ''. Reasons are about the
    TARGET (anchor room/furniture), not the occupant's own location. Used to
    guarantee the label set contains clear negatives."""
    obj = (c.get("object_category") or "").lower()
    rel = (c.get("target_relationship") or "").lower()
    activity = (c.get("_activity") or "").lower()
    room, furn = _anchor_parts(c.get("target_anchor") or "")
    if (obj in _ELECTRONICS and any(k in activity for k in _MEAL_KEYWORDS)
            and rel in _SURFACE_RELS and any(s in furn for s in _EATING_SURFACES)):
        return "electronics on the eating surface during a meal"
    if rel in _SURFACE_RELS and any(a in furn for a in _APPLIANCE_FURNITURE):
        return "placed on an appliance surface"
    if obj in _FOOD_DRINK and any(b in room for b in _BATHROOM_ROOMS):
        return "food/drink in the bathroom"
    return ""


def obvious_positive(c: dict) -> bool:
    obj = (c.get("object_category") or "").lower()
    rel = (c.get("target_relationship") or "").lower()
    activity = (c.get("_activity") or "").lower()
    _room, furn = _anchor_parts(c.get("target_anchor") or "")
    return (
        obj in _FOOD_DRINK
        and rel in _SURFACE_RELS
        and any(s in furn for s in _EATING_SURFACES)
        and any(k in activity for k in _MEAL_KEYWORDS)
    )


def _dedup_key(c: dict) -> tuple:
    return (
        c.get("_scene"), c.get("_occupant"), c.get("_activity"),
        c.get("object_category"), c.get("target_relationship"), c.get("target_anchor"),
    )


def collect_candidates(folders: list[str], gen_dir: pathlib.Path) -> list[dict]:
    out: list[dict] = []
    for folder in folders:
        path = gen_dir / folder / "generation_result.json"
        if not path.exists():
            print(f"  [skip] {path} not found")
            continue
        d = json.loads(path.read_text())
        cands = d.get("candidates")
        if not cands:
            print(f"  [warn] {folder}: no 'candidates' field — regenerate with post-P0 code")
            continue
        for c in cands:
            c = dict(c)
            c["_scene"] = d.get("scene_id", folder.split("_")[0])
            c["_folder"] = folder
            out.append(c)
    return out


def _select_from_pool(pool: list[dict], k: int, rng: random.Random) -> list[dict]:
    """Pick k candidates from one pool: a floor of obvious negatives and
    positives (so the set isn't just the judge's own distribution), then a
    band-stratified fill for range coverage."""
    picked: list[dict] = []
    picked_keys: set[tuple] = set()

    def take(c: dict) -> bool:
        key = _dedup_key(c)
        if key not in picked_keys and len(picked) < k:
            picked.append(c)
            picked_keys.add(key)
            return True
        return False

    negatives = [c for c in pool if c["_neg"]]
    positives = [c for c in pool if c["_pos"]]
    rng.shuffle(negatives)
    rng.shuffle(positives)
    floor = max(2, k // 5)
    for c in negatives[:floor]:
        take(c)
    for c in positives[:floor]:
        take(c)

    by_band: dict[int, list[dict]] = {0: [], 1: [], 2: [], 3: []}
    for c in pool:
        by_band[c["_band"]].append(c)
    for b in by_band:
        rng.shuffle(by_band[b])
    idx = {b: 0 for b in by_band}
    while len(picked) < k and any(idx[b] < len(by_band[b]) for b in by_band):
        for b in (3, 2, 1, 0):
            if len(picked) >= k:
                break
            while idx[b] < len(by_band[b]):
                c = by_band[b][idx[b]]
                idx[b] += 1
                if take(c):
                    break
    return picked


def select_spanning(cands: list[dict], n: int, seed: int) -> list[dict]:
    """Deterministically pick ~n candidates spanning the band range, balanced
    across scenes so one large scene can't dominate the eval set."""
    rng = random.Random(seed)
    seen: dict[tuple, dict] = {}
    for c in cands:
        seen.setdefault(_dedup_key(c), c)
    pool = list(seen.values())
    for c in pool:
        c["_band"] = score_to_band(float(c.get("_judge_score", 0.0)))
        c["_neg"] = obvious_negative(c)
        c["_pos"] = obvious_positive(c)

    by_scene: dict[str, list[dict]] = {}
    for c in pool:
        by_scene.setdefault(c.get("_scene", "?"), []).append(c)

    scenes = sorted(by_scene)
    base = n // len(scenes)
    rem = n - base * len(scenes)
    picked: list[dict] = []
    for i, scene in enumerate(scenes):
        quota = base + (1 if i < rem else 0)
        picked.extend(_select_from_pool(by_scene[scene], quota, rng))
    return picked[:n]


_COLUMNS = [
    "candidate_id", "scene", "occupant", "activity", "time_window",
    "object_category", "target_relationship", "target_anchor", "room",
    "reason", "assumed_from",
    "judge_score", "machine_band", "machine_band_label",
    "flag",            # 'obvious-negative: ...' / 'obvious-positive' / ''
    "band",            # PREFILLED with machine_band — the human corrects THIS
    "notes",
]


def write_csv(cands: list[dict], out_path: pathlib.Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(_COLUMNS)
        for i, c in enumerate(cands):
            band = c["_band"]
            flag = (f"obvious-negative: {c['_neg']}" if c["_neg"]
                    else ("obvious-positive" if c["_pos"] else ""))
            w.writerow([
                f"c{i:03d}",
                c.get("_scene", ""),
                c.get("_occupant", ""),
                c.get("_activity", ""),
                f"{float(c.get('_start', 0)):.1f}-{float(c.get('_end', 0)):.1f}h",
                c.get("object_category", ""),
                c.get("target_relationship", ""),
                c.get("target_anchor", ""),
                c.get("_location", ""),
                c.get("reason", ""),
                c.get("assumed_from", ""),
                f"{float(c.get('_judge_score', 0.0)):.2f}",
                band,
                BAND_LABEL[band],
                flag,
                band,            # band prefilled = machine suggestion, human corrects
                "",
            ])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folders", nargs="+", required=True, help="generation folder names under --gen-dir")
    ap.add_argument("--gen-dir", default="generation_out_labelset", help="dir holding the folders (rel to repo root ok)")
    ap.add_argument("--n", type=int, default=60, help="target candidate count")
    ap.add_argument("--seed", type=int, default=0, help="deterministic selection seed")
    ap.add_argument("--out", default="results/judge_label_set/candidates_to_label.csv")
    args = ap.parse_args()

    gen_dir = pathlib.Path(args.gen_dir)
    if not gen_dir.is_absolute():
        gen_dir = REPO_ROOT / gen_dir
    out_path = pathlib.Path(args.out)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path

    cands = collect_candidates(args.folders, gen_dir)
    print(f"collected {len(cands)} candidates from {len(args.folders)} folder(s)")
    picked = select_spanning(cands, args.n, args.seed)
    write_csv(picked, out_path)

    bands = [c["_band"] for c in picked]
    n_neg = sum(1 for c in picked if c["_neg"])
    n_pos = sum(1 for c in picked if c["_pos"])
    print(f"selected {len(picked)} candidates (seed={args.seed})")
    print(f"  band spread: " + ", ".join(f"{b}={bands.count(b)}" for b in (3, 2, 1, 0)))
    print(f"  obvious negatives: {n_neg}   obvious positives: {n_pos}")
    print(f"  wrote {out_path}")


if __name__ == "__main__":
    main()
