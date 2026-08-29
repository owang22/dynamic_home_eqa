# ADAPTED 2026-08-28 from src/revamp_v2/simulate.py
# (source commit 0d7c3b5e3723d1bf1f46c99dae40780fbde0951e) for the
# self-contained src/households package. Owned copy: edit in place.
# Changes from source, all mechanical:
#   - the simulator body is the vendored .simulate_activities module;
#     load_v1() returns it (name kept so callers read unchanged) instead
#     of importlib-loading profiles/revamp_v1/simulate_activities.py;
#   - expand_calendar is a package-relative import, no sys.path insert;
#   - PROFILES_DIR -> profiles/households (the new data root).
#!/usr/bin/env python3
"""L3 realization for revamp_v2: routine_program.yaml -> timeline_seed<N>/.

Expands the program (expand_calendar.expand), then runs the UNCHANGED
vendored simulator body (households.simulate_activities; its
simulate()/write_outputs() are called directly — extended, never forked) with two additions, both drawing from their own
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
  python -m households.simulate profiles/households/generated/<slug>/hh1 --seed 0 \
      [--days N] [--out .../timeline_seed0]
"""
from __future__ import annotations

import argparse

import json
import math
import pathlib
import random


import yaml

from dynamic_home_eqa.generation.cache import make_seed

HERE = pathlib.Path(__file__).resolve().parent


from . import expand_calendar as xc

PARAMS_PATH = HERE / "realization_params.yaml"


REPO_ROOT = HERE.parent.parent
PROFILES_DIR = REPO_ROOT / "profiles" / "households"


def load_v1():
    """The simulator body: the vendored module, not a runtime file load.
    The name survives from the revamp_v2 original so call sites read
    unchanged."""
    from . import simulate_activities
    return simulate_activities


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

    original_sample_after = sa.sample_after

    def sample_after_with_noop(rule, rng_):
        # v3 rules carry `noop_p`: the chance this firing leaves the
        # object where it is (the NO_OP mass of the authored dist, lifted
        # out by the expander). v1's own move() treats a None destination
        # as "no move", so the wrapper needs no other support. Rules
        # without noop_p draw NOTHING extra — the v1 RNG stream is
        # untouched and the byte-for-byte regression holds.
        if "noop_p" in rule and rng_.random() < rule["noop_p"]:
            return None
        return original_sample_after(rule, rng_)

    sa.realize = realize_with_fragments
    sa.sample_after = sample_after_with_noop
    try:
        log, hourly, blocks, stats = sa.simulate(acts, motions, days, seed)
    finally:
        sa.realize = original_realize
        sa.sample_after = original_sample_after

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
    # v3 accounting, previously computed but never surfaced in meta.json
    stats["synthesized_during"] = acts.get("synthesized_during", [])
    stats["merged_away_blocks"] = acts.get("merged_away_blocks", [])
    stats["skipped_away_lingers"] = acts.get("skipped_away_lingers", [])
    stats["skips_per_activity"] = dict(sorted(skips.items()))
    stats["fragment_bouts_per_activity"] = dict(sorted(frag_stats.items()))
    return log, hourly, blocks, stats, acts, motions


def tag_event_kinds(log: list[dict]) -> list[dict]:
    """Additive `kind` on every event, by MECHANISM rather than by count:
    `carry_pickup` for an activity rule landing an object ON a person,
    `carry_putdown` for one taking it OFF a person, `misplace` for
    p_misplace drift, `tidy` for tidy-walk returns, `rule` for everything
    else the program's rules did. Purely additive JSONL field — every
    downstream consumer (export_bank, spatialize, the viewer) reads the
    existing keys and must run unchanged; the regression fixture bypasses
    this (it calls write_outputs on the raw simulate output), so v1
    byte-equality holds.

    The carry cycle is classified by what the event DOES (on/off a
    person), not by which code injected it: the expander's
    carry-on-departure pickups and an authored take-along rule ("backpack
    goes to work") are the same pick-up-set-down cycle, and the measured
    storm (hh9: fragmented work_away bouts re-firing authored person
    rules, ~98 events on 12-bout days) was entirely authored. A
    person-to-person move is a handoff, not a carry leg — `rule`."""
    for e in log:
        by = e.get("by", "")
        from_person = str(e["from"]).startswith(xc.PERSON)
        to_person = str(e["to"]).startswith(xc.PERSON)
        if by == "misplace":
            kind = "misplace"
        elif by.startswith("tidy:"):
            kind = "tidy"
        elif by.startswith("activity:") and to_person and not from_person:
            kind = "carry_pickup"
        elif by.startswith("activity:") and from_person and not to_person:
            kind = "carry_putdown"
        else:
            kind = "rule"
        e["kind"] = kind
    return log


CARRY_KINDS = ("carry_pickup", "carry_putdown")


def suppress_carry_rehome(log: list[dict], hourly: list[dict],
                          rehome_min: float) -> int:
    """Kill the bout×items carry storm at its source: within one calendar
    day, a carry_putdown followed by that same object's very next event
    being the inverse carry_pickup (same person, same spot, nothing moved
    it in between — adjacency in the object's own event chain proves
    that), less than `rehome_min` minutes later, means the person
    plausibly kept the bag packed between two close trips. Both events
    are removed and the hourly snapshots in the gap are patched to keep
    the item on its person, so events.jsonl and hourly.csv stay one
    consistent story. Returns the number of suppressed pairs; call AFTER
    tag_event_kinds."""
    if rehome_min <= 0:
        return 0
    by_obj: dict[str, list[int]] = {}
    for i, e in enumerate(log):
        by_obj.setdefault(e["object"], []).append(i)
    drop: set[int] = set()
    for obj, idxs in by_obj.items():
        j = 0
        while j + 1 < len(idxs):
            a, b = log[idxs[j]], log[idxs[j + 1]]
            if (a["kind"] == "carry_putdown" and b["kind"] == "carry_pickup"
                    and b["to"] == a["from"]          # back on the same person
                    and b["from"] == a["to"]          # from the same spot
                    and b["t"] - a["t"] < rehome_min
                    and b["t"] // 1440 == a["t"] // 1440):
                drop.add(idxs[j])
                drop.add(idxs[j + 1])
                for row in hourly:
                    if a["t"] < row["t"] <= b["t"]:
                        row[obj] = a["from"]
                j += 2
            else:
                j += 1
    if drop:
        log[:] = [e for i, e in enumerate(log) if i not in drop]
    return len(drop) // 2


def write_timeline(hh_dir: pathlib.Path, out: pathlib.Path, days: int,
                   seed: int) -> dict:
    """Full L3 for one household dir; returns the final meta dict."""
    sa = load_v1()
    params = load_params()
    program = yaml.safe_load((hh_dir / "routine_program.yaml").read_text())
    # owners fallback for pre-injection programs (see story_calendar):
    # without object_owners the v3 expander synthesizes no person legs.
    persona_path = hh_dir / "persona.yaml"
    if not program.get("object_owners") and persona_path.exists():
        try:
            _per = yaml.safe_load(persona_path.read_text())
            program["object_owners"] = {
                o["id"]: o["owner"]
                for o in (_per.get("object_inventory") or [])}
        except Exception:
            pass
    days = days or int(program["days"])
    log, hourly, blocks, stats, acts, motions = simulate_program(
        program, days, seed, sa=sa, params=params)
    tag_event_kinds(log)
    carry_cfg = params.get("carry_on_departure", {})
    stats["carry_rehome_suppressed"] = suppress_carry_rehome(
        log, hourly, float(carry_cfg.get("carry_rehome_min", 0)))
    sa.write_outputs(out, motions, log, hourly, blocks, stats, days, seed,
                     hh_dir)
    # The expanded program in revamp_v1's own object_motions shape: a
    # generated artifact (never authored) that lets the UNCHANGED
    # visualization/spatialize.py and the topdown viewer consume a
    # revamp_v2 household exactly like a revamp_v1 one.
    (hh_dir / "expanded_motions.yaml").write_text(
        "# GENERATED by src/households/simulate.py from routine_program.yaml\n"
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
        "skip": params["skip"], "fragmentation": params["fragmentation"],
        "carry_on_departure": params.get("carry_on_departure", {})}
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
    _main()
