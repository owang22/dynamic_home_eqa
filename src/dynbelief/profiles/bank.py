"""Profile episode-bank builder (Phase A2-A4).

Produces the three frozen banks the experiments run on, all off the same
profile object vocabulary + layout schema:

  typ_v1         3 VERIFIED typical households (the profiles/manual bases)
  atyp_v1        registered transforms of the typical bases (phase_shift +10h)
  atyp_shift_v1  atyp_v1 logs with each object's event stream independently
                 phase-offset (LOG-level, not a profile transform): destroys
                 the shared-routine structure, preserves per-object marginals.
                 Control bank for C4.

Per household (spec A2-A4):
  * 30 simulated days; 4 designated query times/day; per-day look budget 3.
  * 20 target objects stratified by ground-truth receptacle-change rate into
    low/med/high terciles.
  * 5 HELD-OUT objects (class-disjoint from the 15 observed): they appear in
    ground truth and queries but are stripped from every observation history /
    memory shown to a model (A3, for C4 attribution). The bank marks them; the
    experiment harness does the stripping.
  * Ground-truth tables (A4): per (object, query_time) true receptacle; per
    (class, dt) displacement hazard.

Freeze contract (hard rule): each bank is generated ONCE at a fixed seed,
written to banks/<name>/, and hash-manifested. The builder calls
validate_profile and refuses any profile that FAILs or is not VERIFIED
(dev override: allow_draft=True, which stamps the manifest non_reportable).
"""
from __future__ import annotations

import bisect
import hashlib
import json
import pathlib
import random
from dataclasses import dataclass, field, asdict
from typing import Optional

from dynbelief import ELSEWHERE_ID, ELSEWHERE_LABEL, MIN_PER_DAY
from dynbelief.profiles.schema import (
    Profile, load_profile, default_class, require_verified, DAY_IDX as DAY_IDX_LOCAL)
from dynbelief.profiles import transforms
from dynbelief.profiles.generator import simulate
from dynbelief.anchors import validate_profile as vc

DEFAULT_QUERY_HOURS = [9, 13, 18, 21]     # 4 designated query times / day
HAZARD_DT_GRID_MIN = [60, 120, 240, 480, 780, 1200]  # 1h .. 20h


# ── household + bank specs ───────────────────────────────────────────────────

@dataclass
class HouseholdSpec:
    profile: str                                  # base profile id in profiles/manual
    transform: Optional[dict] = None              # {"type":..., "params":{...}} or None
    per_object_shift: bool = False                # atyp_shift_v1 log-level op


@dataclass
class BankSpec:
    name: str
    households: list[HouseholdSpec]
    n_days: int = 30
    query_hours: list[int] = field(default_factory=lambda: list(DEFAULT_QUERY_HOURS))
    budget_per_day: int = 3
    n_targets: int = 20
    n_heldout: int = 5
    obs_per_day: tuple[int, int] = (2, 4)   # K jittered full-home snapshots / day
    seed: int = 20260718


# Banks (redefinition 2026-07-19): "atypical" = a REALISTIC distinct household a
# day-schedule LLM prior should mishandle, NOT a phase-shift artifact. night_shift
# is matched to single_adult (same home/objects/placements, day-job vs night-job),
# giving the cleanest C1/C2 pair. atyp_shift is the C4 control: night_shift logs
# with each object independently phase-offset (destroys shared routine, preserves
# per-object marginals). More atypical counterparts (roommates/family) to come.
def default_bank_specs() -> dict[str, BankSpec]:
    # Addendum v2: atypicals are registered TRANSFORMS producing realistic
    # distinct households (T1 night-shift-with-reversion, T2 workday patterns),
    # each validated 0-FAIL with bindings/placements inherited byte-for-byte.
    typ_bases = ["single_adult_typ_v1", "college_roommates_typ_v1", "family4_typ_v1"]
    typ = [HouseholdSpec(b) for b in typ_bases]
    atyp = [
        HouseholdSpec("single_adult_typ_v1", transform={"type": "night_shift_reversion", "params": {}}),
        HouseholdSpec("single_adult_typ_v1", transform={"type": "workday_pattern", "params": {"pattern": "three_twelves"}}),
        HouseholdSpec("family4_typ_v1", transform={"type": "workday_pattern", "params": {"pattern": "weekend_worker"}}),
    ]
    # C4 control: per-object log-level phase scramble of the T1 atypical.
    atyp_shift = [HouseholdSpec("single_adult_typ_v1",
                                transform={"type": "night_shift_reversion", "params": {}},
                                per_object_shift=True)]
    return {
        "typ_v1": BankSpec("typ_v1", typ),
        "atyp_v2": BankSpec("atyp_v2", atyp),
        "atyp_shift_v1": BankSpec("atyp_shift_v1", atyp_shift),
    }


# ── profile resolution ───────────────────────────────────────────────────────

def resolve_profile(hh: HouseholdSpec, manual_dir: pathlib.Path) -> Profile:
    ch = load_profile(manual_dir / f"{hh.profile}.yaml")
    if hh.transform:
        ch = transforms.apply_transform(ch, hh.transform["type"], **hh.transform["params"])
    return ch


# ── per-object phase shift (atyp_shift_v1, log-level) ────────────────────────

def apply_per_object_shift(events: list[dict], placements: dict, n_days: int,
                           rng: random.Random) -> list[dict]:
    """Offset each object's event t_min stream by an independent random phase
    (mod horizon), preserving per-object inter-event structure while
    decorrelating objects. Returns a new event list (init state re-derived by
    the caller from placements)."""
    horizon = n_days * MIN_PER_DAY
    by_obj: dict[str, list[dict]] = {}
    for e in events:
        by_obj.setdefault(e["label"], []).append(e)
    shifted: list[dict] = []
    for obj, evs in by_obj.items():
        off = rng.randrange(horizon)
        for e in evs:
            ne = dict(e)
            ne["t_min"] = (e["t_min"] + off) % horizon
            shifted.append(ne)
    shifted.sort(key=lambda e: (e["t_min"], e["label"]))
    return shifted


def rebuild_snapshots(events: list[dict], placements: dict, n_days: int) -> list[dict]:
    """Replay events forward from the placement homes to produce a 00:00
    snapshot for every day (the ReplayWorld contract)."""
    state = {o: p.home for o, p in placements.items()}
    ev = sorted(events, key=lambda e: e["t_min"])
    ts = [e["t_min"] for e in ev]
    snaps = []
    for day in range(n_days):
        t = day * MIN_PER_DAY
        hi = bisect.bisect_right(ts, t - 1) if day > 0 else 0
        # replay strictly-before t for a 00:00 snapshot reflecting prior events
        # (day 0 snapshot = initial homes)
        snaps.append(None)  # placeholder; fill below
    # single forward pass
    cur = dict(state)
    idx = 0
    for day in range(n_days):
        t = day * MIN_PER_DAY
        while idx < len(ev) and ev[idx]["t_min"] < t:
            cur[ev[idx]["label"]] = ev[idx]["parent_label"]
            idx += 1
        snaps[day] = {"day": day, "t_min": t, "parents": dict(sorted(cur.items()))}
    return snaps


# ── ground truth: true receptacle at t, per-class hazards ────────────────────

def _state_series(events: list[dict], placements: dict):
    ev = sorted(events, key=lambda e: e["t_min"])
    ts = [e["t_min"] for e in ev]
    init = {o: p.home for o, p in placements.items()}
    return ev, ts, init


def true_parent_at(ev, ts, init, obj: str, t: int) -> str:
    """Receptacle label of obj at minute t (inclusive)."""
    cur = init.get(obj, ELSEWHERE_LABEL)
    hi = bisect.bisect_right(ts, t)
    for e in ev[:hi]:
        if e["label"] == obj:
            cur = e["parent_label"]
    return cur


def class_hazards(events: list[dict], placements: dict, n_days: int,
                  dt_grid=HAZARD_DT_GRID_MIN) -> dict:
    """Per (class, dt): P(receptacle at t+dt != receptacle at t), sampled over
    a grid of t across the horizon. Aggregated over all objects of the class."""
    ev, ts, init = _state_series(events, placements)
    horizon = n_days * MIN_PER_DAY
    sample_ts = list(range(0, horizon, 120))   # every 2h
    by_class: dict[str, dict[int, list[int]]] = {}
    for obj, p in placements.items():
        cls = p.cls
        cd = by_class.setdefault(cls, {dt: [] for dt in dt_grid})
        for t in sample_ts:
            for dt in dt_grid:
                if t + dt >= horizon:
                    continue
                a = true_parent_at(ev, ts, init, obj, t)
                b = true_parent_at(ev, ts, init, obj, t + dt)
                cd[dt].append(int(a != b))
    out = {}
    for cls, cd in by_class.items():
        out[cls] = {str(dt): (round(sum(v) / len(v), 4) if v else None)
                    for dt, v in cd.items()}
    return out


def object_change_rate(events: list[dict], placements: dict, n_days: int) -> dict:
    moves: dict[str, int] = {}
    for e in events:
        moves[e["label"]] = moves.get(e["label"], 0) + 1
    return {o: moves.get(o, 0) / n_days for o in placements}


def observation_coverage(events, observations, placements, window_min=240) -> float:
    """W1: fraction of ground-truth MOVEMENTS observed within `window_min`.
    A night-active household's moves may be systematically less observed by a
    day-anchored snapshot schedule; compare this across banks before trusting
    a cross-bank C1 result."""
    obs_by_obj: dict[str, list[int]] = {}
    for row in observations:
        for o in row["parents"]:
            obs_by_obj.setdefault(o, []).append(row["t_min"])
    for v in obs_by_obj.values():
        v.sort()
    moves = [e for e in events if e.get("moved_by") not in ("init", None)]
    if not moves:
        return float("nan")
    covered = 0
    for e in moves:
        ts = obs_by_obj.get(e["label"], [])
        i = bisect.bisect_left(ts, e["t_min"])
        if i < len(ts) and ts[i] - e["t_min"] <= window_min:
            covered += 1
    return round(covered / len(moves), 4)


def daytype_movement_stats(events, placements, n_days, workdays: set[int] | None) -> dict:
    """W2: per-class daily movement rate split by workday vs off-day, so a
    transform's two-regime structure is verifiable. workdays = set of weekday
    indices (Mo=0); None -> report per-day-of-week counts only."""
    wd = workdays or set()
    nd_work = sum(1 for d in range(n_days) if (d % 7) in wd)
    nd_off = n_days - nd_work
    work: dict[str, int] = {}
    off: dict[str, int] = {}
    cls_of = {o: p.cls for o, p in placements.items()}
    for e in events:
        if e.get("moved_by") in ("init", None):
            continue
        c = cls_of.get(e["label"], "?")
        if (e["t_min"] // MIN_PER_DAY) % 7 in wd:
            work[c] = work.get(c, 0) + 1
        else:
            off[c] = off.get(c, 0) + 1
    classes = sorted(set(cls_of.values()))
    return {"workdays": sorted(wd), "n_workdays": nd_work, "n_offdays": nd_off,
            "per_class": {c: {"workday_rate": round(work.get(c, 0) / nd_work, 3) if nd_work else None,
                              "offday_rate": round(off.get(c, 0) / nd_off, 3) if nd_off else None}
                          for c in classes}}


def sample_observations(ev, ts, init, placements: dict, n_days: int,
                        obs_per_day: tuple[int, int], rng: random.Random) -> list[dict]:
    """The SHARED observation stream (bank invariant): per day, K in
    [obs_per_day] full-home snapshots at jittered times spread across 24h (one
    per equal time-bin, so time-of-day and per-object staleness both vary and
    no fixed-hour confound recurs). Each row is the true state of EVERY object
    at that instant; the experiment strips held-out objects when building a
    model's memory. Every arm (LLM + classical) reads this identical stream."""
    kmin, kmax = obs_per_day
    rows = []
    for day in range(n_days):
        k = rng.randint(kmin, kmax)
        step = MIN_PER_DAY / k
        times = sorted({min(MIN_PER_DAY - 1, int(rng.uniform(i * step, (i + 1) * step)))
                        for i in range(k)})
        for tm in times:
            t = day * MIN_PER_DAY + tm
            rows.append({"day": day, "t_min": t,
                         "parents": {o: true_parent_at(ev, ts, init, o, t)
                                     for o in sorted(placements)}})
    return rows


# ── target selection: 20 stratified + 5 held-out class-disjoint ──────────────

def select_targets(rate: dict, placements: dict, n_targets: int, n_heldout: int,
                   rng: random.Random) -> tuple[list[str], list[str], dict]:
    """Pick n_targets objects balanced across low/med/high terciles of the
    change rate; designate n_heldout of them whose CLASSES do not appear among
    the observed targets. Returns (observed, heldout, tercile_of)."""
    objs = sorted(placements, key=lambda o: (rate[o], o))
    n = len(objs)
    # tercile boundaries by rank
    t1, t2 = n // 3, 2 * n // 3
    tercile_of = {}
    for i, o in enumerate(objs):
        tercile_of[o] = "low" if i < t1 else ("med" if i < t2 else "high")
    buckets = {"low": [], "med": [], "high": []}
    for o in objs:
        buckets[tercile_of[o]].append(o)
    for b in buckets.values():
        rng.shuffle(b)

    n_targets = min(n_targets, n)
    # round-robin across terciles for balance
    chosen: list[str] = []
    order = ["low", "med", "high"]
    i = 0
    while len(chosen) < n_targets and any(buckets[k] for k in order):
        k = order[i % 3]
        if buckets[k]:
            chosen.append(buckets[k].pop())
        i += 1

    # held-out: choose classes present in `chosen`, then pull 5 objects whose
    # class is used by nothing else remaining in the observed set.
    n_heldout = min(n_heldout, max(0, len(chosen) - 3))
    by_class: dict[str, list[str]] = {}
    for o in chosen:
        by_class.setdefault(default_class(o), []).append(o)
    # candidate held-out classes = classes with exactly one target object
    singleton_classes = [c for c, v in by_class.items() if len(v) == 1]
    rng.shuffle(singleton_classes)
    heldout: list[str] = []
    for c in singleton_classes:
        if len(heldout) >= n_heldout:
            break
        heldout.append(by_class[c][0])
    observed = [o for o in chosen if o not in set(heldout)]
    return observed, heldout, tercile_of


# ── query sampling ───────────────────────────────────────────────────────────

def sample_queries(targets: list[str], n_days: int, query_hours: list[int],
                   rng: random.Random) -> list[dict]:
    """One query per designated time slot; object drawn from targets, balanced
    round-robin with shuffling so every target recurs across days."""
    queries = []
    pool: list[str] = []
    qid = 0
    for day in range(n_days):
        for h in query_hours:
            if not pool:
                pool = list(targets)
                rng.shuffle(pool)
            obj = pool.pop()
            queries.append({"query_id": qid, "day": day,
                            "t_query": day * MIN_PER_DAY + h * 60,
                            "object": obj, "query_hour": h})
            qid += 1
    return queries


# ── build one household + one bank ───────────────────────────────────────────

def _int_ids(profile: Profile):
    obj_ids = {lbl: i for i, lbl in enumerate(sorted(profile.placements))}
    recep_ids = {ELSEWHERE_LABEL: ELSEWHERE_ID}
    for i, rid in enumerate(sorted(profile.receptacle_ids), start=1):
        recep_ids[rid] = i
    return obj_ids, recep_ids


def build_household(hh: HouseholdSpec, spec: BankSpec, manual_dir: pathlib.Path,
                    out_dir: pathlib.Path, allow_draft: bool) -> dict:
    profile = resolve_profile(hh, manual_dir)
    # validate + gate. Addendum scoping: V6a/V6b (ATUS/HOMER) gate the TYPICAL
    # base only; the atypical is valid by inheritance if (a) V1-V5 pass on the
    # TRANSFORMED profile, (b) the transform is registered (it is, via
    # apply_transform), and (c) the base is VERIFIED with no anchor FAIL.
    from dynbelief.profiles.schema import validate_structural, has_fail
    checks, _ = vc.validate(manual_dir / f"{hh.profile}.yaml")  # base profile provenance
    base_fail = any(c.status == "FAIL" for c in checks)
    require_verified(profile, allow_draft=allow_draft)
    if base_fail and not allow_draft:
        raise RuntimeError(f"{hh.profile}: base anchor validation FAIL; refusing to freeze")
    if hh.transform and has_fail(validate_structural(profile)) and not allow_draft:
        raise RuntimeError(f"{profile.household}: transformed profile FAILs V1-V5 "
                           f"(broken transformation); refusing to freeze")

    seed = int(hashlib.sha256(f"{spec.name}:{profile.household}:{spec.seed}"
                              .encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    events, snapshots, meta = simulate(profile, n_days=spec.n_days, seed=seed)

    if hh.per_object_shift:
        events = apply_per_object_shift(events, profile.placements, spec.n_days, rng)
        snapshots = rebuild_snapshots(events, profile.placements, spec.n_days)

    rate = object_change_rate(events, profile.placements, spec.n_days)
    observed, heldout, tercile_of = select_targets(
        rate, profile.placements, spec.n_targets, spec.n_heldout, rng)
    targets = observed + heldout
    queries = sample_queries(targets, spec.n_days, spec.query_hours, rng)

    # shared observation stream (the bank invariant) + ground truth
    ev, ts, init = _state_series(events, profile.placements)
    observations = sample_observations(ev, ts, init, profile.placements, spec.n_days,
                                       spec.obs_per_day, rng)
    gt_rows = []
    for q in queries:
        gt_rows.append({**q,
                        "true_receptacle": true_parent_at(ev, ts, init, q["object"], q["t_query"]),
                        "true_room": profile.room_of(true_parent_at(ev, ts, init, q["object"], q["t_query"])),
                        "tercile": tercile_of[q["object"]],
                        "held_out": q["object"] in set(heldout),
                        "class": default_class(q["object"])})
    hazards = class_hazards(events, profile.placements, spec.n_days)

    # atypicality distance + W1 coverage + W2 day-type stats
    distance, workdays = None, None
    if hh.transform:
        base_ch = load_profile(manual_dir / f"{hh.profile}.yaml")
        distance = transforms.atypicality_distance(base_ch, profile)
        tp = hh.transform.get("params", {})
        if hh.transform["type"] == "night_shift_reversion":
            workdays = ({DAY_IDX_LOCAL[d] for d in tp["workdays"]} if tp.get("workdays")
                        else {0, 1, 2, 3, 4})
        elif hh.transform["type"] == "workday_pattern":
            from dynbelief.profiles.transforms import _T2_PATTERNS
            workdays = {DAY_IDX_LOCAL[d] for d in _T2_PATTERNS[tp["pattern"]]["workdays"]}
    coverage = observation_coverage(events, observations, profile.placements)
    daytype = daytype_movement_stats(events, profile.placements, spec.n_days, workdays)

    # write episode dir (ReplayWorld format)
    hdir = out_dir / profile.household
    hdir.mkdir(parents=True, exist_ok=True)
    obj_ids, recep_ids = _int_ids(profile)
    recep_meta = {str(i): {"label": lbl,
                           "room": None if lbl == ELSEWHERE_LABEL else profile.room_of(lbl),
                           "category": None if lbl == ELSEWHERE_LABEL else default_class(lbl)}
                  for lbl, i in recep_ids.items()}
    (hdir / "registry.json").write_text(json.dumps({
        "scene_id": profile.household, "n_days": spec.n_days,
        "days": list(range(spec.n_days)), "objects": obj_ids, "receptacles": recep_ids,
        "receptacle_meta": recep_meta, "elsewhere_id": ELSEWHERE_ID,
        "object_class": {o: p.cls for o, p in profile.placements.items()},
        "profile": {"household": profile.household, "status": profile.status,
                    "derived_from": profile.derived_from,
                    "transformation": profile.transformation},
        "per_object_shift": hh.per_object_shift,
    }, indent=1))
    with open(hdir / "events.jsonl", "w") as f:
        for e in sorted(events, key=lambda e: (e["t_min"], e["label"])):
            f.write(json.dumps({"t_min": e["t_min"], "object_id": obj_ids[e["label"]],
                                "parent_id": recep_ids[e["parent_label"]],
                                "states": {}, "moved_by": e["moved_by"]}) + "\n")
    for snap in snapshots:
        (hdir / f"snapshot_day{snap['day']}.json").write_text(json.dumps({
            "t_min": snap["t_min"], "day": snap["day"],
            "parents": {str(obj_ids[o]): recep_ids[p] for o, p in snap["parents"].items()},
            "states": {}}, indent=1))

    # write per-household tables
    (hdir / "targets.json").write_text(json.dumps({
        "observed": observed, "held_out": heldout,
        "tercile_of": {o: tercile_of[o] for o in targets},
        "change_rate": {o: round(rate[o], 4) for o in targets},
        "class_of": {o: default_class(o) for o in targets}}, indent=1))
    _write_jsonl(hdir / "queries.jsonl", queries)
    _write_jsonl(hdir / "ground_truth.jsonl", gt_rows)
    _write_jsonl(hdir / "observations.jsonl", observations)   # shared memory substrate
    (hdir / "class_hazards.json").write_text(json.dumps(hazards, indent=1))

    return {
        "household": profile.household, "base_profile": hh.profile,
        "status": profile.status, "transformation": profile.transformation,
        "per_object_shift": hh.per_object_shift,
        "n_objects": len(profile.placements), "n_events": len(events),
        "n_targets": len(targets), "n_observed": len(observed), "n_heldout": len(heldout),
        "n_queries": len(queries), "n_observations": len(observations), "seed": seed,
        "tercile_counts": {t: sum(1 for o in targets if tercile_of[o] == t)
                           for t in ("low", "med", "high")},
        "atypicality_distance": distance,
        "observation_coverage": coverage,
        "daytype_movement": daytype,
        "anchor_base_fail": base_fail,
    }


def _write_jsonl(path: pathlib.Path, rows: list[dict]):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _hash_dir(d: pathlib.Path) -> dict[str, str]:
    out = {}
    for p in sorted(d.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(d))] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    return out


def build_bank(spec: BankSpec, manual_dir: pathlib.Path, banks_root: pathlib.Path,
               allow_draft: bool = False) -> dict:
    out_dir = banks_root / spec.name
    out_dir.mkdir(parents=True, exist_ok=True)
    envelope_hash = ""
    ep = pathlib.Path(__file__).resolve().parents[1] / "anchors" / "envelope.yaml"
    if ep.exists():
        envelope_hash = hashlib.sha256(ep.read_bytes()).hexdigest()[:16]

    households = [build_household(hh, spec, manual_dir, out_dir, allow_draft)
                  for hh in spec.households]
    non_reportable = any(h["status"] != "VERIFIED" or h["anchor_base_fail"]
                         for h in households)
    manifest = {
        "bank": spec.name,
        "bank_version": "2.2",  # R5: streams+extended-grid eval protocol
        "spec": {**asdict(spec), "households": [asdict(h) for h in spec.households]},
        "non_reportable": non_reportable,
        "non_reportable_reason": ("built under --allow-draft off DRAFT/anchor-FAIL profiles"
                                  if non_reportable else None),
        "envelope_hash": envelope_hash,
        "atypicality_distances": {h["household"]: h["atypicality_distance"]
                                  for h in households if h.get("atypicality_distance") is not None},
        "coverage": {h["household"]: h["observation_coverage"] for h in households},
        "households": households,
        "file_hashes": _hash_dir(out_dir),
    }
    # file_hashes must exclude the manifest itself; write after hashing
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return manifest


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    import argparse
    from dynamic_home_eqa.paths import REPO_ROOT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bank", choices=list(default_bank_specs()) + ["all"], default="all")
    ap.add_argument("--allow-draft", action="store_true",
                    help="dev mode: build off DRAFT/anchor-FAIL profiles (manifest marked non_reportable)")
    ap.add_argument("--banks-root", type=pathlib.Path, default=REPO_ROOT / "banks")
    ap.add_argument("--manual-dir", type=pathlib.Path, default=REPO_ROOT / "profiles" / "manual")
    ap.add_argument("--days", type=int, default=None, help="override n_days (dev/throwaway)")
    ap.add_argument("--targets", type=int, default=None, help="override n_targets (dev)")
    args = ap.parse_args(argv)

    specs = default_bank_specs()
    names = list(specs) if args.bank == "all" else [args.bank]
    for name in names:
        spec = specs[name]
        if args.days:
            spec.n_days = args.days
        if args.targets:
            spec.n_targets = args.targets
        m = build_bank(spec, args.manual_dir, args.banks_root, allow_draft=args.allow_draft)
        flag = " [NON-REPORTABLE]" if m["non_reportable"] else " [reportable]"
        print(f"[bank] {name}{flag}: {len(m['households'])} households, "
              f"{sum(h['n_queries'] for h in m['households'])} queries -> "
              f"{args.banks_root / name}")
        for h in m["households"]:
            print(f"    {h['household']:44s} obs={h['n_observed']} held={h['n_heldout']} "
                  f"terciles={h['tercile_counts']} events={h['n_events']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
