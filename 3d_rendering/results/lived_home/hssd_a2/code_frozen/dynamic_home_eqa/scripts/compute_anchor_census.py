#!/usr/bin/env python3
"""
compute_anchor_census.py — Realizable-Anchor Vocabulary round, Part 1:
one-time, per-scene precomputation of a room-qualified, receptacle-backed
furniture census, joining three data sources per furniture INSTANCE (not
category):

  1. Identity + position — env/inventory.py's load_furniture_instances
     (a supplement, not a replacement, to load_furniture_census: the
     existing category->position-list shape stays for its two existing
     callers; this needs per-instance identity to join against).
  2. Receptacle backing — find_receptacles(sim) + the scene's own
     .rec_filter.json "active" list, the exact mechanism
     build_realized_day.resolve_furniture_receptacles already uses.
     Reimplemented locally (not calling that function directly) only
     because it returns raw_had_any as a bool, not the raw count this
     census records per instance — same source data, same join, no new
     placement logic invented.
  3. Room label — generation/regions.py's region_for_point on the
     instance's real position. Geometry wins: this deliberately does NOT
     apply the foundIn consistency gate generation/inventory.py's
     room_inventory_from_scene_state uses for movable-object room
     counting (see env/anchor_census.py's own module docstring for why
     that gate is the wrong tool for an anchor census — confirmed on the
     fixture scene this decision alone lifts room-tag coverage from
     ~39% to ~88%, the remainder being instances outside any region
     volume at all, recorded under excluded_no_region rather than
     dropped silently).

Bed rule: a region containing at least
one real `bed` instance is decisively labeled a bedroom, whatever HSSD's
own region name says — the fixture scene has three regions HSSD labels
"office" that each contain a bed + wardrobe + stand (obviously bedrooms),
plus an "other_room" with a bed. The bed is the single most reliable
signal a region is where someone sleeps; no other category gets an
override rule (a couch in an office is still an office).

Room-name dedup: two regions normalising to the same name (two bedrooms,
including bed-rule conversions) get a deterministic _1/_2/... suffix,
ordered by the region's own index in scene_regions.regions (the same
first-in-JSON-order tie-break region_for_point's own multi-match
resolution already uses elsewhere in this codebase). A normalised name
with only one matching region stays bare (no suffix).

Instance-label dedup within a (room, category) group: kitchen.counter_1,
kitchen.counter_2, ordered by the live rigid object's own .handle string
— stable across runs of the same scene (load order is deterministic; the
handle is only used here, at compute time, as a sort key, never
persisted — see env/anchor_census.py's own docstring for why persisting
a live handle string would be unsafe).

Output: data/anchor_census/<scene_id>.json (see env/anchor_census.py,
which owns the read-side schema/accessors this script's output must
match — CENSUS_VERSION lives there, not here) plus one markdown table
per scene under
results/reports/anchor_census/<scene_id>_anchor_census.md.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA

_REPORT_DIR = _DYNAMIC_EQA / "results" / "reports" / "anchor_census"


# Rename ambiguous HSSD region names at label-definition time so a room and an
# object never share a token the LLM sees. "tv" is an HSSD room name AND a
# furniture/object category ("tv" the appliance) — rename the ROOM to
# "tv_room" so the proposer/judge see "tv_room.couch_1" as a place, distinct
# from the "tv" object. Aliasing to living_room (rooms._ALIASES / rooms_match /
# slot_room) still holds, so activity-location matching is unaffected.
_ROOM_RENAME: dict[str, str] = {"tv": "tv_room"}


def _disambiguated_room_names(scene_regions, bedroom_indices: frozenset = frozenset()) -> dict[int, str]:
    """{region_index: final_room_name}. `bedroom_indices` is the bed-rule
    override set — those regions' base name becomes "bedroom" BEFORE
    dedup, so a converted office and a real bedroom share one numbering
    sequence. See module docstring for both rules."""
    def _base(i, region) -> str:
        nm = "bedroom" if i in bedroom_indices else region.normalised
        return _ROOM_RENAME.get(nm, nm)
    base_names = {i: _base(i, region) for i, region in enumerate(scene_regions.regions)}
    by_name: dict[str, list[int]] = collections.defaultdict(list)
    for i in sorted(base_names):
        by_name[base_names[i]].append(i)
    names: dict[int, str] = {}
    for norm_name, indices in by_name.items():
        if len(indices) == 1:
            names[indices[0]] = norm_name
        else:
            for n, i in enumerate(indices, start=1):
                names[i] = f"{norm_name}_{n}"
    return names


def _region_index_for_point(point, scene_regions):
    """(index, region) for the first region containing `point`, or
    (None, None) — same first-match-wins logic as
    generation.regions.region_for_point, just also returning the index
    _disambiguated_room_names is keyed on."""
    from dynamic_home_eqa.generation.regions import point_in_region

    for i, region in enumerate(scene_regions.regions):
        if point_in_region(point, region):
            return i, region
    return None, None


def compute_anchor_census(scene_id: str, sim) -> dict:
    """Pure orchestration: env/inventory.py's instance census for
    identity, generation/regions.py for room geometry, habitat-lab's
    find_receptacles + this scene's .rec_filter.json for receptacle
    backing — no new placement or geometry logic invented here."""
    from dynamic_home_eqa.env.anchor_census import CENSUS_VERSION
    from dynamic_home_eqa.env.inventory import load_furniture_instances
    from dynamic_home_eqa.generation.regions import load_scene_regions
    from dynamic_home_eqa.scripts.build_realized_day import find_live_object_at_xz
    from dynamic_home_eqa.topdown_map import HSSD_DIR

    instances = load_furniture_instances(scene_id)
    scene_regions = load_scene_regions(scene_id)

    if scene_regions is None:
        # No region annotations at all for this scene -- every instance is
        # unresolvable, not silently empty.
        return {
            "scene_id": scene_id, "census_version": CENSUS_VERSION,
            "anchors": {},
            "excluded_no_region": [
                {"category": inst.category, "position": list(inst.position)} for inst in instances
            ],
            "anomalies": [],
        }

    # First pass: geometric region assignment for every instance — done
    # before naming, because the bed rule (see module docstring) needs to
    # know which regions contain a bed before any region gets its final
    # room name.
    assigned: list = []  # (instance, region_index)
    excluded_no_region = []
    for inst in instances:
        idx, region = _region_index_for_point(inst.position, scene_regions)
        if region is None:
            excluded_no_region.append({"category": inst.category, "position": list(inst.position)})
        else:
            assigned.append((inst, idx))

    bedroom_indices = frozenset(idx for inst, idx in assigned if inst.category == "bed")
    room_names = _disambiguated_room_names(scene_regions, bedroom_indices)

    # Receptacle lookup — same source/join as
    # build_realized_day.resolve_furniture_receptacles, reimplemented
    # locally only to expose the raw count (see module docstring).
    from habitat.datasets.rearrange.samplers.receptacle import find_receptacles

    filter_path = pathlib.Path(HSSD_DIR) / "scene_filter_files" / f"{scene_id}.rec_filter.json"
    active_names = set(json.loads(filter_path.read_text())["active"]) if filter_path.exists() else None
    all_receptacles = find_receptacles(sim)
    by_parent: dict[str, list] = collections.defaultdict(list)
    for r in all_receptacles:
        by_parent[r.parent_object_handle].append(r)

    anomalies: list[str] = []
    # (room, category) -> [(live_handle_str, instance, n_active, n_raw), ...]
    grouped: dict[tuple[str, str], list] = collections.defaultdict(list)

    for inst, idx in assigned:
        room = room_names[idx]

        furniture = find_live_object_at_xz(sim, inst.position)
        if furniture is None:
            anomalies.append(
                f"{inst.category} at {inst.position}: classified room={room!r} but no live "
                f"rigid object found at that position — excluded from the census entirely "
                f"(no handle to join receptacles against)."
            )
            continue

        raw = by_parent.get(furniture.handle, [])
        active = raw if active_names is None else [r for r in raw if r.unique_name in active_names]
        grouped[(room, inst.category)].append((furniture.handle, inst, len(active), len(raw)))

    anchors: dict[str, dict] = {}
    for (room, category), items in grouped.items():
        items.sort(key=lambda t: t[0])  # deterministic: by live handle string
        for n, (_handle, inst, n_active, n_raw) in enumerate(items, start=1):
            label = f"{room}.{category}_{n}"
            anchors[label] = {
                "category": category, "room": room, "position": list(inst.position),
                "active_receptacles": n_active, "raw_receptacles": n_raw,
                "curated_out": n_raw > 0 and n_active == 0,
            }

    return {
        "scene_id": scene_id, "census_version": CENSUS_VERSION,
        "anchors": anchors, "excluded_no_region": excluded_no_region, "anomalies": anomalies,
    }


def _write_markdown_report(census: dict) -> pathlib.Path:
    scene_id = census["scene_id"]
    anchors = census["anchors"]
    lines = [
        f"# Anchor census — scene {scene_id}",
        "",
        f"{len(anchors)} anchors across "
        f"{len({r['room'] for r in anchors.values()})} rooms. "
        f"{len(census['excluded_no_region'])} instances excluded (no region volume). "
        f"{len(census['anomalies'])} anomalies (see below).",
        "",
        "## Anchors",
        "",
        "| label | category | room | active_receptacles | raw_receptacles | curated_out |",
        "|---|---|---|---|---|---|",
    ]
    for label, rec in sorted(anchors.items()):
        lines.append(
            f"| {label} | {rec['category']} | {rec['room']} | {rec['active_receptacles']} | "
            f"{rec['raw_receptacles']} | {rec['curated_out']} |"
        )

    lines += ["", "## Excluded — no region volume contains this instance", ""]
    if census["excluded_no_region"]:
        lines += ["| category | position |", "|---|---|"]
        for e in sorted(census["excluded_no_region"], key=lambda e: e["category"]):
            lines.append(f"| {e['category']} | {[round(v, 2) for v in e['position']]} |")
    else:
        lines.append("(none)")

    lines += ["", "## Anomalies", ""]
    if census["anomalies"]:
        for a in census["anomalies"]:
            lines.append(f"- {a}")
    else:
        lines.append("(none)")

    _REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = _REPORT_DIR / f"{scene_id}_anchor_census.md"
    path.write_text("\n".join(lines) + "\n")
    return path


_DEFAULT_TEST_SCENE = "102343992"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenes", nargs="+", default=[_DEFAULT_TEST_SCENE])
    args = ap.parse_args()

    from dynamic_home_eqa.env.anchor_census import save_anchor_census
    from dynamic_home_eqa.scripts.realism_render_job import _make_render_sim

    for scene_id in args.scenes:
        sim = _make_render_sim(scene_id)
        try:
            census = compute_anchor_census(scene_id, sim)
        finally:
            sim.close()

        json_path = save_anchor_census(census)
        md_path = _write_markdown_report(census)

        n_rooms = len({r["room"] for r in census["anchors"].values()})
        n_surface = sum(1 for r in census["anchors"].values() if r["active_receptacles"] >= 1)
        print(f"{scene_id}: {len(census['anchors'])} anchors, {n_rooms} rooms, "
              f"{n_surface} with >=1 active receptacle (surface-eligible), "
              f"{len(census['excluded_no_region'])} excluded (no region), "
              f"{len(census['anomalies'])} anomalies")
        print(f"  wrote {json_path}")
        print(f"  wrote {md_path}")


if __name__ == "__main__":
    main()
