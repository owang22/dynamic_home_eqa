"""H2 shared core: identical-episode scoring of classical vs llm_digest,
parallelized LLM calls, digest builder, anonymizer, no-prior baselines.

The one invariant every H2 experiment relies on: for a given cell
(bank, household, D, stream) the SAME sampled episodes are scored by every
arm (sample_stream is seeded by (bank,hh,D,stream,n), so a fixed n gives a
byte-identical episode set). No arm sees anything another does not.
"""
from __future__ import annotations

import json
import pathlib
import random
import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief.classical.filter import uniform_belief
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.experiments.e1 import (build_prompt, SCHEMA, score_prediction,
                                      history_runs, render_history, last_observed)
from dynbelief.experiments.streams import load_gt, sample_stream
from dynbelief.profiles.schema import default_class, load_profile

BANKS_ROOT = REPO_ROOT / "banks"
MANUAL_DIR = REPO_ROOT / "profiles" / "manual"
OUT = REPO_ROOT / "reports" / "h2_adaptation"

D_GRID = [0, 1, 2, 3, 5, 7, 10, 13]
E1_STREAMS = ("natural", "moved_enriched")
N_PER_CELL = 8
MAX_WORKERS = 24
TEMP = 0.0


# ── household / candidate helpers ────────────────────────────────────────────

def households(bank: str):
    bd = BANKS_ROOT / bank
    return [p.name for p in sorted(bd.iterdir())
            if p.is_dir() and (p / "registry.json").exists()]


def load_hh(bank: str, hh: str):
    hd = BANKS_ROOT / bank / hh
    by_obj, init, observations, targets, reg = load_gt(hd)
    recep_label = {int(v): k for k, v in reg["receptacles"].items()}
    cands = sorted(r for r in recep_label.values() if r != "elsewhere")
    cand_set = cands + ["elsewhere"]
    heldout = set(targets["held_out"])
    return dict(hd=hd, by_obj=by_obj, init=init, observations=observations, targets=targets,
                reg=reg, cands=cands, cand_set=cand_set, heldout=heldout)


def hist_before(observations, heldout, D):
    return [{"day": r["day"], "t_min": r["t_min"],
             "parents": {o: v for o, v in r["parents"].items() if o not in heldout}}
            for r in observations if r["day"] < D]


# ── classical arm on a fixed episode set ─────────────────────────────────────

def score_classical(arm: str, cand_set, hist, eps, D):
    rm = None if D == 0 else make_arm(arm, cand_set, hist)[0]
    rows = []
    for ep in eps:
        if rm is None:
            belief = uniform_belief(cand_set)
        else:
            belief = _belief(rm, cand_set, ep["object"], ep["t_query"], ep, "categorical")
        argmax, p_true, brier, logloss, top3 = _rows_fields(belief, cand_set, ep["true_receptacle"])
        rows.append(_row(ep, D, arm, argmax, p_true, top3))
    return rows


# ── llm arm on a fixed episode set (PARALLEL) ────────────────────────────────

def _llm_one(client, hist_text, cands, ep, temperature):
    system, user = build_prompt(hist_text, cands, ep["object"], ep["t_query"], None)
    try:
        preds = json.loads(client.generate(system, user, SCHEMA, seed=7,
                                            temperature=temperature))["predictions"]
    except Exception:
        preds = []
    argmax, p_true, brier, logloss, top3 = score_prediction(preds, cands + ["elsewhere"],
                                                            ep["true_receptacle"])
    return argmax, p_true, top3


def score_llm(client, hist_text, cand_list, eps, D, arm_label,
              temperature=TEMP, pool: ThreadPoolExecutor | None = None):
    """cand_list = candidate receptacles WITHOUT elsewhere (build_prompt adds it)."""
    own = pool is None
    pool = pool or ThreadPoolExecutor(max_workers=MAX_WORKERS)
    try:
        results = list(pool.map(lambda ep: _llm_one(client, hist_text, cand_list, ep, temperature), eps))
    finally:
        if own:
            pool.shutdown()
    rows = []
    for ep, (argmax, p_true, top3) in zip(eps, results):
        rows.append(_row(ep, D, arm_label, argmax, p_true, top3))
    return rows


def _row(ep, D, arm, argmax, p_true, top3):
    return {"bank": ep["bank"], "household": ep["household"], "history_days": D,
            "stream": ep["stream"], "query_id": ep["query_id"], "arm": arm,
            "object": ep["object"], "class": default_class(ep["object"]),
            "tercile": ep.get("tercile"), "held_out": ep.get("held_out", False),
            "moved_since_obs": ep.get("moved_since_obs"),
            "true_receptacle": ep["true_receptacle"], "predicted": argmax,
            "p_true": round(float(p_true), 4), "correct": int(argmax == ep["true_receptacle"]),
            "top3_correct": int(top3)}


# ── anonymization (E2/E3): consistent within a bank ──────────────────────────

def anon_maps(bank: str):
    """Stable object->object_N and receptacle->recep_M maps across a whole bank
    (union of all households' vocab), so ids are consistent bank-wide."""
    objs, recs = set(), set()
    for hh in households(bank):
        h = load_hh(bank, hh)
        objs |= set(h["by_obj"].keys()) if isinstance(h["by_obj"], dict) else set()
        recs |= set(h["cands"])
        objs |= {o for r in h["observations"] for o in r["parents"]}
        objs |= set(h["targets"]["observed"]) | set(h["targets"]["held_out"])
    omap = {o: f"object_{i}" for i, o in enumerate(sorted(objs))}
    rmap = {r: f"recep_{i}" for i, r in enumerate(sorted(recs))}
    rmap["elsewhere"] = "elsewhere"
    return omap, rmap


def anon_digest(hist_text: str, omap, rmap) -> str:
    """Replace every object/receptacle token in the rendered digest. Longest-
    first so no id is a prefix of another."""
    s = hist_text
    for k, v in sorted(list(omap.items()) + list(rmap.items()),
                       key=lambda kv: -len(kv[0])):
        s = s.replace(k, v)
    return s


def anon_eps(eps, omap, rmap):
    out = []
    for ep in eps:
        e = dict(ep)
        e["object"] = omap.get(ep["object"], ep["object"])
        e["true_receptacle"] = rmap.get(ep["true_receptacle"], ep["true_receptacle"])
        if ep.get("last_obs") in rmap:
            e["last_obs"] = rmap[ep["last_obs"]]
        out.append(e)
    return out


# ── reassigned-object set for atyp_authored_v1 (role-swapped placements) ──────

# receptacles whose ROLE is deliberately reassigned (a bowl holding keys, a
# laundry basket holding toys, a desk mug holding pens, and the studio's
# repurposed surfaces standing in for nightstand/desk).
_ROLE_SWAP_RECEPS = {"entry_bowl_e1", "desk_mug_o1", "toy_basket_l1"}


def typ_class_modal_room():
    """class -> most common resting ROOM across the typ_v1 bank profiles."""
    from collections import Counter
    room_of = {}
    cnt = {}
    for hh in households("typ_v1"):
        prof = load_profile(MANUAL_DIR / f"{load_hh('typ_v1', hh)['reg']['profile']['household'].split('__')[0]}.yaml")
        rooms = {r.id: r.room for r in prof.receptacles}
        for o, pl in prof.placements.items():
            c = default_class(o)
            cnt.setdefault(c, Counter())[rooms.get(pl.home, "?")] += 1
    return {c: k.most_common(1)[0][0] for c, k in cnt.items()}


def reassigned_objects(hh: str) -> set:
    """Objects in an atyp_authored household whose home is role-swapped: home
    room differs from the class's typ-modal room, OR home is a role-swap
    receptacle."""
    base = hh.split("__")[0]
    prof = load_profile(MANUAL_DIR / f"{base}.yaml")
    rooms = {r.id: r.room for r in prof.receptacles}
    typ_room = typ_class_modal_room()
    out = set()
    for o, pl in prof.placements.items():
        c = default_class(o)
        home_room = rooms.get(pl.home)
        if pl.home in _ROLE_SWAP_RECEPS:
            out.add(o)
        elif c in typ_room and home_room != typ_room[c]:
            out.add(o)
    return out
