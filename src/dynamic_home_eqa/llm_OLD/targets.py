"""
llm_prior/targets.py — enumerates L0's elicitation target tuples: (axis,
category_or_variable_key, time_bin, scene, profile), each carrying the
exact D1 kernel state-space support to elicit a distribution over (so the
LLM's location prior and the fitted kernel are scored on identical
support, never a drifted independent guess at what the options are) plus
the generator's own persona text and a room-inventory description built
without touching any train-day event.

Only tuples with at least one real train-split event in that (category,
time_bin) bucket are enumerated — an untested combination has no
empirical frequency to score a prior against, so eliciting one would be
unscoreable, not merely thin.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass

from dynamic_home_eqa.embodied.attribution import fit_location_kernels_from_train, fit_state_kernels_from_train
from dynamic_home_eqa.embodied.experiment_config import FrozenConfig
from dynamic_home_eqa.embodied.posterior import OUTSIDE, bucket_changes_by_time_of_day
from dynamic_home_eqa.env.inventory import inventory_for_generation
from dynamic_home_eqa.rooms import slot_room

N_TIME_BUCKETS = 4  # matches embodied.posterior.bucket_changes_by_time_of_day's own default


@dataclass(frozen=True)
class ElicitationTarget:
    axis: str                    # "location" | "state"
    key: str                     # category ("book") for location, "category::variable" for state
    time_bin: int                # 0..N_TIME_BUCKETS-1
    support: tuple[str, ...]     # the exact D1 kernel state-space support to elicit a distribution over
    scene: str
    profile: str


def render_persona(persona: dict) -> str:
    """Verbatim rendering of generation_result.json's own "persona" dict
    into prompt text — no paraphrasing, no summarizing, so the LLM sees
    exactly what the generator's persona stage produced. household_type
    and schedule_notes are itself persona output (not train-day events:
    they describe routine/structure, not any specific day's realized
    change), consistent with the "scene described only by profile and
    room inventory, never train-day events" rule."""
    lines = [f"Household type: {persona['household_type']}"]
    for occ in persona["occupants"]:
        lines.append(
            f"- {occ['name']} ({occ['role']}, {occ['age_band']}): wakes ~{occ['typical_wake']}h, "
            f"sleeps ~{occ['typical_sleep']}h. {occ['habits']}"
        )
    lines.append(f"Schedule notes: {persona['schedule_notes']}")
    return "\n".join(lines)


def render_room_inventory(scene_id: str, known_categories: tuple[str, ...] = ()) -> str:
    """{category: count} from env.inventory.inventory_for_generation (the
    same pre-clutter-pass inventory the generation pipeline itself
    consults), grouped by room via rooms.slot_room — reads only the
    scene's static furniture layout, never any manifest's changes list.

    known_categories (L0 rerun fix, 2026-07-07): inventory_for_generation
    only tracks Tier-1 furniture and assumed Tier-3 mobile items — it does
    NOT include Tier-2b clutter (book, candle, cup, ...), which is exactly
    most of what L0's location-prior targets ask about. v1 never told the
    model these categories existed at all; models correctly (from their
    view) inferred "not in inventory -> doesn't exist -> OUTSIDE" for
    every one of them, and v1's degenerate scores partly measured that
    inference, not a real prior. Fixed by appending any category in
    known_categories not already covered by the furniture census as a
    flat "also present" list — NO room, count, or position, which would
    be exactly the location/dynamics leak this function must avoid. This
    is standing category-presence inventory (what a robot knows exists in
    the home after a patrol), not a specific day's realized location."""
    counts = inventory_for_generation(scene_id)
    by_room: dict[str, list[str]] = {}
    for category, count in sorted(counts.items()):
        room = slot_room(category) or "unknown"
        by_room.setdefault(room, []).append(f"{category} x{count}")
    lines = [f"{room}: {', '.join(items)}" for room, items in sorted(by_room.items())]

    also_present = sorted(set(known_categories) - set(counts))
    if also_present:
        lines.append(
            "Also present somewhere in the household (exact current location not tracked here): "
            + ", ".join(also_present)
        )
    return "\n".join(lines)


def _occurring_time_bins(train_manifests: list[dict], keys: set[str], is_state: bool) -> dict[str, set[int]]:
    """{key: {time_bin, ...}} — every (category-or-variable-key, time_bin)
    pair with at least one real train-split change event, per
    bucket_changes_by_time_of_day's own bucketing."""
    per_bucket = bucket_changes_by_time_of_day(train_manifests, n_buckets=N_TIME_BUCKETS)
    occurring: dict[str, set[int]] = {k: set() for k in keys}
    for bucket_idx, changes in enumerate(per_bucket):
        for c in changes:
            if is_state:
                if c.get("change_type") != "state_change":
                    continue
                key = f"{c['object_category']}::{c['state_variable']}"
            else:
                key = c.get("object_category")
            if key in occurring:
                occurring[key].add(bucket_idx)
    return occurring


def enumerate_location_targets(out_dir: pathlib.Path, config: FrozenConfig) -> list[ElicitationTarget]:
    kernels = fit_location_kernels_from_train(out_dir, config)
    train_manifests = [json.loads((out_dir / f / "manifest.json").read_text()) for f in config.train_folders]
    occurring = _occurring_time_bins(train_manifests, set(kernels.keys()), is_state=False)

    targets = []
    for category, kernel in sorted(kernels.items()):
        support = tuple(s for s in kernel.states if s != OUTSIDE) + (OUTSIDE,)
        for time_bin in sorted(occurring.get(category, ())):
            targets.append(ElicitationTarget(
                axis="location", key=category, time_bin=time_bin, support=support,
                scene=config.scene, profile=config.profile,
            ))
    return targets


def enumerate_state_targets(out_dir: pathlib.Path, config: FrozenConfig) -> list[ElicitationTarget]:
    if not config.state_train_folders:
        return []
    kernels = fit_state_kernels_from_train(out_dir, config)
    train_manifests = [
        json.loads((out_dir / f / "manifest.json").read_text()) for f in config.state_train_folders
    ]
    occurring = _occurring_time_bins(train_manifests, set(kernels.keys()), is_state=True)

    targets = []
    for key, kernel in sorted(kernels.items()):
        support = tuple(kernel.states)
        for time_bin in sorted(occurring.get(key, ())):
            targets.append(ElicitationTarget(
                axis="state", key=key, time_bin=time_bin, support=support,
                scene=config.scene, profile=config.profile,
            ))
    return targets


def enumerate_targets(out_dir: pathlib.Path, config: FrozenConfig) -> list[ElicitationTarget]:
    return enumerate_location_targets(out_dir, config) + enumerate_state_targets(out_dir, config)
