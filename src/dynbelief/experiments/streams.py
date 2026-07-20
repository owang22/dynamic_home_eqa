"""Three tagged, non-mixing query streams per household (Bank/Eval revisions R3).

Streams are generated deterministically (fixed seed derived from
bank+household+D+stream) so EVERY arm scores the identical episodes within a
cell — a prerequisite for the paired per-episode deltas (R2). Query sets are
drawn INDEPENDENTLY per D cell (R2); the observation history each model fits on
is untouched by the choice of stream (enrichment changes measurement
resolution, not learning).

  natural         query times ~ uniform on day D over observed target objects;
                  natural moved-since-last-observation rate (~15-25%).
  moved_enriched  query times sampled so ~50% of episodes are moved-since-last-
                  observation (transition-adjacent from ground truth). Headline
                  learning-curve + moved-slice analyses run here.
  held_out        queries on the held-out objects (no history) on day D.

Each episode carries the window weekday/weekend composition of its history
window [0, D) as a covariate (R1: off-cycle D values vary weekday composition;
log it to de-confound weekly-structure learning from window length).

D grids (R1): classical (free) vs LLM (paid).
"""
from __future__ import annotations

import bisect
import hashlib
import json
import pathlib
import random

from dynbelief import MIN_PER_DAY

STREAMS = ("natural", "moved_enriched", "held_out")
D_GRID_CLASSICAL = [0, 1, 2, 3, 5, 7, 10, 14, 21, 28]
D_GRID_LLM = [0, 1, 3, 7, 14, 28]
N_PER_CELL_CLASSICAL = 100
N_PER_CELL_LLM = 36
QUERY_HOURS_LO, QUERY_HOURS_HI = 6 * 60, 23 * 60   # sample query minute in-day


def _seed(bank: str, hh: str, D: int, stream: str) -> int:
    h = hashlib.sha256(f"{bank}|{hh}|{D}|{stream}".encode()).hexdigest()
    return int(h[:12], 16)


# ── ground-truth reconstruction from events.jsonl ────────────────────────────

def load_gt(hh_dir: pathlib.Path):
    reg = json.loads((hh_dir / "registry.json").read_text())
    recep_label = {v: k for k, v in reg["receptacles"].items()}
    obj_label = {v: k for k, v in reg["objects"].items()}
    events = [json.loads(l) for l in (hh_dir / "events.jsonl").open()]
    ev = [{"t_min": e["t_min"], "label": obj_label[e["object_id"]],
           "parent_label": recep_label[e["parent_id"]]} for e in events]
    ev.sort(key=lambda e: e["t_min"])
    # per object: sorted (t, parent) list + home (registry object_class -> home
    # unknown here; use the day-0 snapshot as the initial state)
    snap0 = json.loads((hh_dir / "snapshot_day0.json").read_text())
    init = {obj_label[int(o)]: recep_label[p] for o, p in snap0["parents"].items()}
    by_obj: dict[str, list] = {}
    for e in ev:
        by_obj.setdefault(e["label"], []).append((e["t_min"], e["parent_label"]))
    observations = [json.loads(l) for l in (hh_dir / "observations.jsonl").open()]
    targets = json.loads((hh_dir / "targets.json").read_text())
    return by_obj, init, observations, targets, reg


def true_parent_at(by_obj, init, obj, t):
    seq = by_obj.get(obj, [])
    cur = init.get(obj, "elsewhere")
    lo, hi = 0, bisect.bisect_right([s[0] for s in seq], t)
    for i in range(hi):
        cur = seq[i][1]
    return cur


def last_observed_before(observations, obj, t, D):
    """(receptacle, t_obs) of obj's most recent snapshot with day<D and t_min<t."""
    best = None
    for row in observations:
        if row["day"] >= D or row["t_min"] >= t:
            continue
        if obj in row["parents"]:
            if best is None or row["t_min"] > best[1]:
                best = (row["parents"][obj], row["t_min"])
    return best


def weekend_frac(D: int) -> float:
    if D <= 0:
        return float("nan")
    return sum(1 for d in range(D) if d % 7 >= 5) / D


# ── stream sampling ──────────────────────────────────────────────────────────

def _candidate_episodes(by_obj, init, observations, objs, D, no_history=False):
    """All (obj, t_query, moved) candidates on day D for the given objects.
    no_history=True (held_out stream): the object is unobserved — NO last
    observation is provided to any model (C4-attribution: held-out objects are
    stripped from all memory), and `moved` is defined relative to home."""
    day = D if D < 30 else 29
    cands = []
    for obj in objs:
        for t in range(day * MIN_PER_DAY + QUERY_HOURS_LO,
                        day * MIN_PER_DAY + QUERY_HOURS_HI, 20):
            obs = None if no_history else last_observed_before(observations, obj, t, D)
            true = true_parent_at(by_obj, init, obj, t)
            if D == 0 or obs is None:
                moved = (true != init.get(obj, "elsewhere"))    # moved from home
                lo_r, lo_t = None, None
            else:
                moved = (true != obs[0])
                lo_r, lo_t = obs[0], obs[1]
            cands.append({"object": obj, "t_query": t, "moved": moved,
                          "true_receptacle": true, "last_obs": lo_r, "last_obs_t": lo_t})
    return cands


def sample_stream(hh_dir: pathlib.Path, bank: str, hh: str, D: int,
                  stream: str, n: int) -> list[dict]:
    by_obj, init, observations, targets, reg = load_gt(hh_dir)
    rng = random.Random(_seed(bank, hh, D, stream))
    observed = targets["observed"]
    held = targets["held_out"]
    objs = held if stream == "held_out" else observed
    cands = _candidate_episodes(by_obj, init, observations, objs, D,
                                no_history=(stream == "held_out"))
    if not cands:
        return []
    if stream == "moved_enriched":
        moved = [c for c in cands if c["moved"]]
        notmoved = [c for c in cands if not c["moved"]]
        rng.shuffle(moved); rng.shuffle(notmoved)
        half = n // 2
        picked = moved[:half] + notmoved[:n - half]
        # if one bucket is short, backfill from the other (log the realized rate)
        if len(picked) < n:
            rest = (moved[half:] + notmoved[n - half:])
            rng.shuffle(rest)
            picked += rest[: n - len(picked)]
    else:
        rng.shuffle(cands)
        picked = cands[:n]
    rng.shuffle(picked)
    wf = weekend_frac(D)
    tercile = {o: t for o, t in targets["tercile_of"].items()}
    out = []
    for i, c in enumerate(picked):
        out.append({
            "bank": bank, "household": hh, "history_days": D, "stream": stream,
            "query_id": i, "object": c["object"], "t_query": c["t_query"],
            "day": D, "true_receptacle": c["true_receptacle"],
            "moved_since_obs": int(c["moved"]), "last_obs": c["last_obs"],
            "last_obs_t": c.get("last_obs_t"), "held_out": stream == "held_out",
            "class": _cls(c["object"]), "tercile": tercile.get(c["object"]),
            "window_weekend_frac": None if wf != wf else round(wf, 3),
        })
    return out


def _cls(obj):
    from dynbelief.profiles.schema import default_class
    return default_class(obj)


def realized_moved_rate(episodes: list[dict]) -> float:
    return (sum(e["moved_since_obs"] for e in episodes) / len(episodes)
            if episodes else float("nan"))


def build_all_streams(banks_root: pathlib.Path, bank: str, d_grid, n_per_cell,
                      streams=STREAMS) -> list[dict]:
    """All episodes for a bank across the D grid and streams (deterministic)."""
    bank_dir = banks_root / bank
    eps = []
    for hh in sorted(p.name for p in bank_dir.iterdir()
                     if p.is_dir() and (p / "registry.json").exists()):
        for D in d_grid:
            for stream in streams:
                eps += sample_stream(bank_dir / hh, bank, hh, D, stream, n_per_cell)
    return eps
