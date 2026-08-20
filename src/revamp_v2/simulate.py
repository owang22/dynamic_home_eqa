#!/usr/bin/env python3
"""L3 realization for revamp_v2: routine_program.yaml -> timeline_seed<N>/.

Expands the program (expand_calendar.expand), then runs the UNCHANGED
revamp_v1 simulator body (profiles/revamp_v1/simulate_activities.py is
loaded as a module and its simulate()/write_outputs() are called directly —
extended, never forked) with two additions, both drawing from their own
seeded streams so a program that uses neither reproduces the v1 timeline
byte-for-byte:

1. Per-day skip: each realized calendar item is dropped with its `skip_p`
   BEFORE jitter; a skipped block takes its synthesized linger with it.
   Skips are counted per activity in meta.json.
2. Bout fragmentation: a block whose activity declares
   `fragment: {mean_bouts: k}` realizes as N ~ max(1, Poisson(k))
   non-overlapping sub-bouts inside its realized window, each firing the
   block's bindings (gated by their `only_from`, which is what prevents
   re-trigger spam).

Jitter classes stay exactly the v1 implementation and values; the copies in
realization_params.yaml are asserted equal at load, never redefined.

Usage:
  python src/revamp_v2/simulate.py profiles/revamp_v2/<slug>/hh1 --seed 0 \
      [--days N] [--out .../timeline_seed0]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import pathlib
import random
import sys

import yaml

from dynamic_home_eqa.generation.cache import make_seed

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import expand_calendar as xc  # noqa: E402  (same-directory module)

PARAMS_PATH = HERE / "realization_params.yaml"


REPO_ROOT = HERE.parent.parent
PROFILES_DIR = REPO_ROOT / "profiles" / "revamp_v2"


def load_v1():
    """The revamp_v1 simulator, loaded read-only from its own directory."""
    path = REPO_ROOT / "profiles" / "revamp_v1" / "simulate_activities.py"
    spec = importlib.util.spec_from_file_location("rv1_simulate_activities",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def load_params() -> dict:
    return yaml.safe_load(PARAMS_PATH.read_text())


def _poisson(rng: random.Random, lam: float) -> int:
    """Knuth sampler; lam is schema-bounded small (<= 6)."""
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= limit:
            return k - 1


def apply_skips(acts: dict, rng: random.Random) -> dict[str, int]:
    """Drop items with skip_p (draws only where skip_p > 0), plus their
    linger followers. Mutates acts; returns per-activity skip counts."""
    skipped: dict[str, int] = {}
    dropped_uids: set[str] = set()
    for entry in acts["calendar"]:
        kept = []
        for item in entry["activities"]:
            if item.get("_follows") in dropped_uids:
                continue
            if item.get("skip_p") and rng.random() < item["skip_p"]:
                skipped[item["a"]] = skipped.get(item["a"], 0) + 1
                dropped_uids.add(item.get("uid", ""))
                continue
            kept.append(item)
        entry["activities"] = kept
    return skipped


def fragment_blocks(blocks: list[dict], motions: dict, rng: random.Random,
                    min_bout: float, stats: dict[str, int]) -> list[dict]:
    """Replace each fragmenting block with its sub-bouts (order preserved)."""
    out: list[dict] = []
    for b in blocks:
        frag = motions["object_motions"].get(b["activity"], {}).get("fragment")
        width = b["t1"] - b["t0"]
        if not frag or width < 2 * min_bout:
            out.append(b)
            continue
        n = max(1, _poisson(rng, float(frag["mean_bouts"])))
        n = min(n, int(width // min_bout))
        if n <= 1:
            out.append(b)
            stats[b["activity"]] = stats.get(b["activity"], 0) + 1
            continue
        cuts = sorted(b["t0"] + rng.uniform(0, width) for _ in range(n - 1))
        edges = [b["t0"]] + cuts + [b["t1"]]
        merged = [edges[0]]
        for e in edges[1:-1]:
            if e - merged[-1] >= min_bout and b["t1"] - e >= min_bout:
                merged.append(e)
        merged.append(b["t1"])
        for i in range(len(merged) - 1):
            sub = dict(b)
            sub["t0"], sub["t1"] = int(round(merged[i])), int(round(merged[i + 1]))
            out.append(sub)
            stats[b["activity"]] = stats.get(b["activity"], 0) + 1
    # Sub-bouts of one resident's block can interleave with another
    # resident's; re-sort so residents.jsonl stays chronological. Stable
    # and by t0 only, so an unfragmented run is bit-identical to v1's
    # already-sorted list.
    out.sort(key=lambda b: b["t0"])
    return out


def simulate_program(program: dict, days: int, seed: int,
                     sa=None, params: dict | None = None):
    """(log, hourly, blocks, stats, acts, motions) for one realization."""
    sa = sa or load_v1()
    params = params or load_params()
    assert params["jitter_classes"] == sa.JITTER_CLASSES, (
        "realization_params.yaml jitter_classes drifted from the v1 "
        "simulator's calibrated values — they are one source of truth")

    carry_cfg = params.get("carry_on_departure", {})
    acts, motions = xc.expand(
        program,
        carry_on_departure=bool(carry_cfg.get("enabled", True)),
        carry_p=float(carry_cfg.get("carry_p", 0.85)))
    sa.validate(acts, motions)

    hh = program["household"]
    skip_rng = random.Random(make_seed(hh, seed, "l3_skip"))
    frag_rng = random.Random(make_seed(hh, seed, "l3_frag"))
    skips = apply_skips(acts, skip_rng)

    frag_stats: dict[str, int] = {}
    min_bout = float(params["fragmentation"]["min_bout_minutes"])
    original_realize = sa.realize

    def realize_with_fragments(acts_, motions_, rng_, days_):
        blocks = original_realize(acts_, motions_, rng_, days_)
        return fragment_blocks(blocks, motions_, frag_rng, min_bout,
                               frag_stats)

    sa.realize = realize_with_fragments
    try:
        log, hourly, blocks, stats = sa.simulate(acts, motions, days, seed)
    finally:
        sa.realize = original_realize

    # Every deterministic normalization the expander applied, reported
    # rather than silent — a reader of a timeline can see exactly what the
    # authored program said and what could not be honoured.
    stats["vacuous_arc_drops"] = acts.get("vacuous_drops", [])
    stats["dropped_sleep_resets"] = acts.get("dropped_sleep_resets", [])
    stats["dropped_sleep_fragments"] = acts.get("dropped_sleep_fragments", [])
    stats["derived_only_from"] = acts.get("derived_only_from", [])
    stats["orphaned_rules"] = acts.get("orphaned_rules", [])
    stats["unscheduled_activities"] = acts.get("unscheduled_activities", [])
    stats["inert_objects"] = acts.get("inert_objects", [])
    stats["carried_on_departure"] = acts.get("carried_on_departure", [])
    stats["left_behind_by_trip"] = acts.get("left_behind_by_trip", [])
    stats["carried_putdowns_at_start"] = acts.get(
        "carried_putdowns_at_start", [])
    stats["skips_per_activity"] = dict(sorted(skips.items()))
    stats["fragment_bouts_per_activity"] = dict(sorted(frag_stats.items()))
    return log, hourly, blocks, stats, acts, motions


def write_timeline(hh_dir: pathlib.Path, out: pathlib.Path, days: int,
                   seed: int) -> dict:
    """Full L3 for one household dir; returns the final meta dict."""
    sa = load_v1()
    params = load_params()
    program = yaml.safe_load((hh_dir / "routine_program.yaml").read_text())
    days = days or int(program["days"])
    log, hourly, blocks, stats, _, motions = simulate_program(
        program, days, seed, sa=sa, params=params)
    sa.write_outputs(out, motions, log, hourly, blocks, stats, days, seed,
                     hh_dir)
    # The expanded program in revamp_v1's own object_motions shape: a
    # generated artifact (never authored) that lets the UNCHANGED
    # visualization/spatialize.py and the topdown viewer consume a
    # revamp_v2 household exactly like a revamp_v1 one.
    (hh_dir / "expanded_motions.yaml").write_text(
        "# GENERATED by src/revamp_v2/simulate.py from routine_program.yaml\n"
        "# (revamp_v1 object_motions shape, for spatialize.py/the viewer).\n"
        + yaml.safe_dump(motions, sort_keys=False, width=100,
                         allow_unicode=True))

    meta = json.loads((out / "meta.json").read_text())
    build_log = hh_dir / "build_log.json"
    if build_log.exists():
        b = json.loads(build_log.read_text())
        meta["provenance"] = {k: b[k] for k in
                              ("model", "prompts", "builder_version",
                               "accepted_attempt", "n_attempts")
                              if k in b}
    meta["realization_params"] = {
        "skip": params["skip"], "fragmentation": params["fragmentation"]}
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("household", type=pathlib.Path,
                    help="household dir holding routine_program.yaml")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--days", type=int, default=None,
                    help="default: the program's own `days`")
    ap.add_argument("--out", type=pathlib.Path, default=None)
    args = ap.parse_args()
    out = args.out or args.household / f"timeline_seed{args.seed}"
    meta = write_timeline(args.household, out, args.days, args.seed)
    s = meta["activity_stats"]
    print(f"{meta['household']}: {meta['n_events']} events over "
          f"{meta['days']} days ({s['blocks']} blocks, "
          f"{sum(s.get('skips_per_activity', {}).values())} skipped, "
          f"{sum(s.get('fragment_bouts_per_activity', {}).values())} "
          f"fragment bouts) -> {out}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(HERE))
    _main()
