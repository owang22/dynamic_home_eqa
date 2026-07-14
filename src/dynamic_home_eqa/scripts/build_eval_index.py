#!/usr/bin/env python3
"""
build_eval_index.py — W-0 ingest for the human-eval webapp.

Normalizes existing pipeline outputs (generation_result.json / manifest.json /
choices.jsonl / the render media directory) into one versioned index per
(run_id, household, day):

    eval_index/{run_id}/{folder}.json

The webapp frontend consumes ONLY these indexes — if pipeline output formats
change, only this script changes. Owner decision (2026-07-13): every pool
shows ACCEPTED events only — manifest changes, never rejected candidates —
so every indexed event is realized/renderable in principle.

`condition` is the future A/B field (populated NOW, displayed never to
raters): the generating model recorded in the manifest, e.g. "Qwen/Qwen3-32B"
vs "casperhansen/llama-3.3-70b-instruct-awq" — the qwen-style vs llama-style
comparison label.

Joins (best-effort, None where absent — the index is honest about gaps):
  - judge fields: manifest change -> selected proposal in generation_result
    ["displacements"] via (category, occupant, activity, relationship,
    resolved anchor), consuming each proposal at most once.
  - render refs: (label, t) -> render_manifest.json items (only events the
    render job sampled have media).
  - capability annotation: recomputed from plausibility.capability_factor
    (the manifest no longer carries a confidence field).

schema_version: 1
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import defaultdict

from dynamic_home_eqa.paths import REPO_ROOT
from dynamic_home_eqa.generation.llm_client import model_slug
from dynamic_home_eqa.plausibility import capability_factor
from dynamic_home_eqa.rooms import resolve_slot

SCHEMA_VERSION = 1
_MEDIA_DIR = REPO_ROOT / "results" / "reports" / "realism_eval_media"


def hour_to_clock(t: float) -> str:
    t = t % 24.0
    return f"{int(t):02d}:{int(round((t - int(t)) * 60)) % 60:02d}"


def _load_render_index(media_dir: pathlib.Path) -> dict[tuple[str, str], dict]:
    """{(folder, item_id-ish key): render entry} keyed by (folder, label, ~t)."""
    idx: dict[tuple, dict] = {}
    manifest_path = media_dir / "render_manifest.json"
    if not manifest_path.exists():
        return idx
    for item in json.loads(manifest_path.read_text()):
        idx[(item.get("folder"), item.get("label"), round(float(item.get("t_hours", -1)), 2))] = item
    return idx


def _mask_status(media_dir: pathlib.Path, render_item: dict) -> str | None:
    """after-panel mask status from the item's own signals JSON."""
    try:
        j = json.loads((media_dir / pathlib.Path(render_item["json"]).name).read_text())
        return j.get("automatic_signals", {}).get("after_status")
    except Exception:
        return None


def _join_judge_fields(changes: list[dict], displacements: list[dict],
                       room_instance_categories) -> dict[int, dict]:
    """Best-effort change-index -> {judge_score, judge_think_excerpt, stage_tag}.

    Each selected proposal is consumed at most once; key on the fields both
    sides share. Anchor is compared through resolve_slot so a proposal's
    census target lines up with the change's to_semantic (incl. ".tucked")."""
    remaining = list(displacements)
    out: dict[int, dict] = {}
    for ci, c in enumerate(changes):
        if c["change_type"] == "state_change":
            continue
        for pi, p in enumerate(remaining):
            if p.get("object_category") != c["object_category"]:
                continue
            if p.get("_occupant") != c.get("mover") and p.get("_activity") != c.get("activity"):
                continue
            try:
                slot = (
                    "away" if p.get("target_anchor") == "put_away"
                    else resolve_slot(p.get("target_anchor", ""), p.get("target_relationship", ""),
                                      room=p.get("_location"),
                                      room_instance_categories=room_instance_categories)
                )
            except Exception:
                slot = p.get("target_anchor")
            if slot != c.get("to_semantic"):
                continue
            out[ci] = {
                "judge_score": p.get("_judge_score"),
                "judge_think_excerpt": p.get("_judge_think"),
                "stage_tag": p.get("_judge_stage_tag"),
            }
            remaining.pop(pi)
            break
    return out


def build_index(folder_dir: pathlib.Path, run_id: str, media_dir: pathlib.Path) -> dict:
    gen = json.loads((folder_dir / "generation_result.json").read_text())
    man = json.loads((folder_dir / "manifest.json").read_text())
    changes = man["changes"]

    from dynamic_home_eqa.topdown_map import instance_room_positions
    try:
        ric = {room: {cat for cat, _ in cats}
               for room, cats in instance_room_positions(gen["scene_id"]).items()}
    except Exception:
        ric = None

    render_idx = _load_render_index(media_dir)
    judge_by_ci = _join_judge_fields(changes, gen.get("displacements", []), ric)

    age_band = {o.get("name"): o.get("age_band") for o in gen.get("persona", {}).get("occupants", [])}

    events = []
    trajectories: dict[str, list] = defaultdict(list)
    folder = folder_dir.name
    for ci, c in enumerate(changes):
        t = float(c["t"])
        rend = render_idx.get((folder, c["label"], round(t, 2)))
        cap_ok = capability_factor(c["object_category"], age_band.get(c.get("mover"))) >= 1.0
        judge = judge_by_ci.get(ci, {})
        events.append({
            "event_id": f"{folder}:{ci}",
            "t": t,
            "t_clock": hour_to_clock(t),
            "occupant": c.get("mover"),
            "activity": c.get("activity"),
            "object": c["label"],
            "category": c["object_category"],
            "relation": c.get("target_relationship"),
            "change_type": c["change_type"],
            "from_semantic": c.get("from_semantic"),
            "to_semantic": c.get("to_semantic"),
            "reason": c.get("reason", ""),
            "judge_score": judge.get("judge_score"),
            "judge_think_excerpt": judge.get("judge_think_excerpt"),
            "stage_tag": judge.get("stage_tag"),
            "render": {
                "png": rend.get("png") if rend else None,
                "json": rend.get("json") if rend else None,
                "mask_status": _mask_status(media_dir, rend) if rend else None,
            },
            "capability_ok": cap_ok,
        })
        if c["change_type"] != "state_change":
            trajectories[c["label"]].append(
                {"t": t, "t_clock": hour_to_clock(t),
                 "from": c.get("from_semantic"), "to": c.get("to_semantic")})

    try:
        media_ref = str(media_dir.resolve().relative_to(REPO_ROOT))
    except ValueError:
        media_ref = str(media_dir.resolve())  # outside the repo: keep absolute

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        # Where this run's render PNGs/JSONs live (repo-relative when under
        # REPO_ROOT). The webapp backend serves /media/{run_id}/... from
        # here instead of assuming one global media dir — runs that share
        # folder names (same scene+profile, different model) keep their
        # media separated by construction.
        "media_dir": media_ref,
        "condition": man.get("model", ""),
        "scene_id": gen["scene_id"],
        "profile": gen["profile"],
        "household_id": gen["household_id"],
        "day": gen.get("day", 0),
        "folder": folder,
        "day_context": man.get("day_context", {}),
        "occupants": [
            {"name": o.get("name"), "role": o.get("role"), "age_band": o.get("age_band"),
             "tidiness": o.get("tidiness"), "owned_items": o.get("owned_items", []),
             "bedroom_index": o.get("bedroom_index")}
            for o in gen.get("persona", {}).get("occupants", [])
        ],
        "activities": [
            {"occupant": tr.get("occupant_name"),
             "day_type": tr.get("day_type"), "day_scenario": tr.get("day_context"),
             "spans": tr.get("activities", [])}
            for tr in gen.get("traces", [])
        ],
        "events": events,
        "trajectories": dict(trajectories),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gen-dir", required=True, help="generation output dir (e.g. generation_out_labelset)")
    ap.add_argument("--run-id", default=None, help="default: model slug from the first manifest")
    ap.add_argument("--media-dir", default=str(_MEDIA_DIR))
    ap.add_argument("--out", default=str(REPO_ROOT / "eval_index"))
    args = ap.parse_args()

    gen_dir = pathlib.Path(args.gen_dir)
    if not gen_dir.is_absolute():
        gen_dir = REPO_ROOT / gen_dir
    folders = sorted(d for d in gen_dir.iterdir() if (d / "manifest.json").exists())
    if not folders:
        raise SystemExit(f"no generation folders under {gen_dir}")

    run_id = args.run_id
    if run_id is None:
        first = json.loads((folders[0] / "manifest.json").read_text())
        run_id = model_slug(first.get("model") or "unlabeled")

    out_dir = pathlib.Path(args.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    media_dir = pathlib.Path(args.media_dir)
    if not media_dir.is_absolute():
        media_dir = REPO_ROOT / media_dir  # anchor to the repo, not the caller's CWD

    for d in folders:
        idx = build_index(d, run_id, media_dir)
        path = out_dir / f"{d.name}.json"
        path.write_text(json.dumps(idx, indent=1))
        n_render = sum(1 for e in idx["events"] if e["render"]["png"])
        n_judge = sum(1 for e in idx["events"] if e["judge_score"] is not None)
        print(f"  {d.name}: {len(idx['events'])} events "
              f"(judge joined {n_judge}, rendered {n_render})  -> {path.relative_to(REPO_ROOT)}")
    print(f"run_id={run_id}  condition-labeled, schema_version={SCHEMA_VERSION}")


if __name__ == "__main__":
    main()
