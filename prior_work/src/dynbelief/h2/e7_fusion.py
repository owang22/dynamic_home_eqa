"""E4 v3 — LLM-as-PRIOR fusion (pseudo-count injection), the correct hybrid structure.

The router (e7_hybrid) failed because SELECTION needs a decision boundary in event
count that predicts which arm wins, and the curves show no such boundary exists
(C3g and LLM tie in the very stratum classical was meant to own). FUSION needs no
boundary: express the LLM's regime-conditioned prediction as kappa days of
pseudo-observations, PREPEND them to the object's real events (the existing
e2.inject mechanism), and fit the frozen classical (C3g) on the combined stream.

  * k=0  -> the fit sees only the pseudo-obs -> posterior = the LLM regime prior
           (inherits the cold-start win: 0.31/0.50/0.24 vs classical's 0.00).
  * k>>0 -> real events outnumber the kappa pseudo-obs -> posterior = C3g
           (inherits the frequent-object periodic ceiling).
  * between -> interpolates by evidence weight PER EDGE. No threshold, no router.

Hierarchical option (matches each source to its granularity): the LLM knows
room+timing, not shelf, so inject at ROOM granularity (sample the pseudo-obs room
from the LLM's room distribution, receptacle uniform within room) and let C3g's
real events own receptacle-within-room. Tested against shelf-level injection; the
winner is chosen on the dev bank.

Both knobs -- kappa (equivalent prior sample size, in days) and the injection
granularity -- are selected on the DEV bank (atyp_regime_v1), FROZEN, then
evaluated on the confirmatory bank. Scored at BOTH room and receptacle level.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from dynbelief import MIN_PER_DAY
from dynbelief.h2 import core, e7_learning as e7
from dynbelief.h2.confirm import CFG as CONF_CFG, BANK as CONF_BANK
from dynbelief.h2.e5_regime import CFG as _E5CFG, _SYS, REGIME_SCHEMA
from dynbelief.h2.e7_hybrid import DEV_BANK, DEV_CFG
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.classical.filter import uniform_belief
from dynbelief.e2.inject import inject, OBS_HOURS, OBS_PER_DAY
from dynbelief.experiments.streams import true_parent_at
from dynbelief.profiles.schema import load_profile
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

KAPPA_GRID = [1, 2, 3, 5, 8]                 # dev-swept prior weight (days)
GRANS = ["room", "recep"]                    # dev-selected injection granularity


def _room_of(base):
    m = {r.id: r.room for r in load_profile(core.MANUAL_DIR / f"{base}.yaml").receptacles}
    m["elsewhere"] = "elsewhere"
    return m


def _llm_recep_dist(client, digest, cands, obj, tq):
    """One LLM call -> normalized distribution over cand_set (+elsewhere) for the
    object at time tq under the inferred regime."""
    clk = f"{(tq % 1440)//60:02d}:{(tq % 1440) % 60:02d}"; day = tq // 1440
    user = (f"{digest}\n\nCandidate receptacles: {', '.join(cands)}, elsewhere.\n\n"
            f"Question: on day {day} at {clk}, where is the {obj}?")
    cand_set = cands + ["elsewhere"]
    dist = {c: 0.0 for c in cand_set}
    try:
        out = json.loads(client.generate(_SYS, user, REGIME_SCHEMA, seed=7, temperature=0.0))
        for pr in out["predictions"]:
            r = str(pr.get("receptacle", ""))
            if r in dist:
                dist[r] += min(max(float(pr.get("p", 0.0)), 0.0), 1.0)
    except Exception:
        pass
    z = sum(dist.values())
    if z <= 0:
        return {c: 1.0/len(cand_set) for c in cand_set}
    return {c: v/z for c, v in dist.items()}


def _pseudo_from_llm(recep_dist, room_of, cands, obj, kappa, gran, seed):
    """kappa days of pseudo-snapshots of ONE object drawn from the LLM prior.
    gran='recep': sample receptacle from recep_dist directly (shelf-level prior).
    gran='room' : sample a ROOM (mass = sum of its receptacles' LLM prob), then a
                  receptacle UNIFORM within that room (room-level prior -> C3g owns
                  the shelf)."""
    rng = np.random.default_rng(seed)
    cand_set = list(recep_dist)
    room_of = dict(room_of); room_of["elsewhere"] = "elsewhere"
    if gran == "room":
        room_mass = defaultdict(float)
        for r in cand_set:
            room_mass[room_of.get(r, "elsewhere")] += recep_dist[r]
        rooms = list(room_mass); rw = np.array([room_mass[x] for x in rooms])
        rw = rw / rw.sum() if rw.sum() > 0 else np.full(len(rooms), 1/len(rooms))
        in_room = {rm: [r for r in cand_set if room_of.get(r, "elsewhere") == rm] for rm in rooms}
    else:
        recs = cand_set; rw_r = np.array([recep_dist[r] for r in recs])
        rw_r = rw_r / rw_r.sum()
    rows = []
    for d in range(kappa):
        for base in OBS_HOURS:
            t = d * MIN_PER_DAY + base + int(rng.integers(-60, 61))
            if gran == "room":
                rm = rooms[int(rng.choice(len(rooms), p=rw))]
                choices = in_room[rm] or cand_set
                rec = choices[int(rng.integers(0, len(choices)))]
            else:
                rec = recs[int(rng.choice(len(recs), p=rw_r))]
            rows.append({"day": d, "t_min": t, "parents": {obj: rec}})
    return rows


def _fit_predict(recep_dist, room_of, cands, cand_set, obj, first_k, kappa, gran, qpts, seed):
    """Fusion prediction per query: fit C3g on inject(pseudo_llm, real first_k)."""
    real = [{"day": t//1440, "t_min": t, "parents": {obj: r}} for (t, r) in first_k]
    pseudo = _pseudo_from_llm(recep_dist, room_of, cands, obj, kappa, gran, seed)
    combined = inject(pseudo, real)
    rm = make_arm("C3g", cand_set, combined)[0]
    out = []
    for (qd, tq, true) in qpts:
        lo = [(t, r) for (t, r) in first_k if t < tq]
        last_r, last_t = (lo[-1][1], lo[-1][0]) if lo else (None, None)
        ep = {"object": obj, "t_query": tq, "last_obs": last_r, "last_obs_t": last_t}
        bel = _belief(rm, cand_set, obj, tq, ep, "categorical")
        pred = _rows_fields(bel, cand_set, true)[0]
        out.append((pred, true))
    return out


def run(endpoint, model, label, bank, cfgmap, diag_key, tag):
    """Generate fusion rows for one bank across kappa x granularity x k."""
    client = OpenAIHTTPClient(endpoint, model)
    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    rows = []
    for hh in cfgmap:
        h = core.load_hh(bank, hh); cfg = cfgmap[hh]
        cand_set = h["cand_set"]; cands = h["cands"]; room_of = _room_of(hh)
        diag = cfg[diag_key]
        diag_sight = e7._diag_digest_and_hist(h, {"diag": diag})
        for obj, hr in cfg["targets"]:
            tev = e7._target_events(h, obj)
            n_total = len(h["by_obj"].get(obj, [])); rar = e7._rarity(n_total)
            qpts = [(qd, qd*1440+hr*60, true_parent_at(h["by_obj"], h["init"], obj, qd*1440+hr*60))
                    for qd in e7.TEST_DAYS]
            # LLM regime prior: one call, persona-only digest, at a representative test time
            pdigest = e7._digest(diag_sight)
            rdist = _llm_recep_dist(client, pdigest, cands, obj, e7.TEST_DAYS[0]*1440 + hr*60)
            for k in e7.K_GRID:
                first_k = tev[:min(k, len(tev))]
                for kappa in KAPPA_GRID:
                    for gran in GRANS:
                        preds = _fit_predict(rdist, room_of, cands, cand_set, obj,
                                             first_k, kappa, gran, qpts, seed=100+k)
                        for (pred, true) in preds:
                            rows.append({"model": f"fusion_{gran}", "kappa": kappa,
                                         "hh": hh, "object": obj, "rarity": rar,
                                         "k": min(k, len(tev)), "pred": pred, "true": true,
                                         "correct_recep": int(pred == true),
                                         "correct_room": int(room_of.get(pred, "x") ==
                                                             room_of.get(true, "y"))})
            print(f"[fusion:{tag}] {hh}:{obj} ({rar}) done", flush=True)
    pool.shutdown()
    core.OUT.mkdir(parents=True, exist_ok=True)
    (core.OUT / f"e7_fusion_{tag}_{label}.jsonl").write_text("".join(json.dumps(r)+"\n" for r in rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", default="deepseek")
    ap.add_argument("--bank", choices=["dev", "conf"], required=True)
    args = ap.parse_args()
    if args.bank == "dev":
        run(args.endpoint, args.model, args.label, DEV_BANK, DEV_CFG, "diag", "dev")
    else:
        run(args.endpoint, args.model, args.label, CONF_BANK, CONF_CFG, "diag", "conf")


if __name__ == "__main__":
    main()
