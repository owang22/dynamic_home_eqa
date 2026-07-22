"""E7 v2 — POOLED learning curves on the EVENTS-OBSERVED axis, stratified by
object rarity. The aggregation-fixed replacement for the four-panel v1.

Why v2 (reviewer fix): v1 plotted one object per household -- four anecdotes at
~7-14 queries/point (accuracy moved in 1/7 steps = noise). And it used DAYS on the
x-axis, which confounds rarity (14 days = 5 events for a rare laptop, 65 for a
frequent mug). v2 fixes both:

  * x-axis = EVENTS-OBSERVED of the target object (k = 0,1,2,4,8,16). This puts
    rare and frequent objects on ONE comparable axis: the claim becomes clean --
    the classical learner needs ~N events per object to reach ceiling; the LLM
    needs ~1 diagnostic sighting per household (regime transfer), so it is already
    near-ceiling at k=0-1 and roughly flat.
  * POOLED over all 18 regime-conditioned target objects x 6 households, STRATIFIED
    into rarity terciles (rare<=47, medium<=78, frequent>78 events/30d), with
    clustered bootstrap CIs (cluster = household x object).

Design (dev/test wall respected -- reuses the FROZEN _SYS / REGIME_SCHEMA /
digest format / _llm_pred, and the FROZEN C3g classical):
  * Observations are event-based & sparse and drawn ONLY from days [0, OBS_HORIZON).
    Tests are on days [OBS_HORIZON, HORIZON_END) at the object's regime hour -> a
    true forward prediction with no leakage.
  * At budget k the classical arm (C3g) sees the first k events of the TARGET
    object (per-edge; diagnostics are irrelevant to a per-edge learner). The LLM
    gets the persona DIAGNOSTIC digest (fixed, ~2 sightings/persona-object -> the
    regime is revealed) PLUS the same first k target events, rendered in the frozen
    digest format. At k=0 the LLM has ONLY the diagnostics: pure regime transfer.

Arms: DeepSeek (LLM, regime prompt) vs C3g (frozen classical) vs C1 (persistence
reference). Expected: LLM high & flat from k~1; C3g creeps up with k and only
reaches/overtakes the LLM in the FREQUENT tercile, where objects actually supply
enough events; in the RARE tercile C3g's curve truncates early (few events exist)
and stays low -- world knowledge buys the adaptation the events never can.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from dynbelief.h2 import core
from dynbelief.h2.confirm import CFG, BANK, _llm_pred
from dynbelief.h2.e5_regime import _SYS
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.classical.filter import uniform_belief
from dynbelief.experiments.streams import true_parent_at
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

K_GRID = [0, 1, 2, 4, 8, 16]                 # events-observed of the target object
OBS_HORIZON = 21                             # observe events from days [0,21)
HORIZON_END = 28                             # test on days [21,28)
TEST_DAYS = list(range(OBS_HORIZON, HORIZON_END))
SIGHT_DAYS = list(range(0, 12))
# rarity terciles by events/30d (from the 18-object enumeration)
TERCILES = [("rare", 0, 47), ("medium", 47, 78), ("frequent", 78, 10**9)]


def _rarity(n):
    for lab, lo, hi in TERCILES:
        if lo < n <= hi or (lab == "rare" and n <= hi):
            return lab
    return "frequent"


def _diag_digest_and_hist(h, cfg):
    """FROZEN diagnostic-only digest (persona reveal): up to 2 telling sightings
    per diagnostic object, in the confirmatory format. Returns (digest, hist)."""
    sightings = []
    for o, hr in cfg["diag"]:
        found = 0
        for dd in SIGHT_DAYS:
            if found >= 2:
                break
            t = dd * 1440 + hr * 60 + 10
            rec = true_parent_at(h["by_obj"], h["init"], o, t)
            if rec != "elsewhere":
                sightings.append((t, o, rec)); found += 1
    return sightings


def _target_events(h, obj):
    """The target object's own movement events within the observation horizon,
    time-ordered: list of (t, rec) with t < OBS_HORIZON*1440."""
    return [(t, r) for (t, r) in h["by_obj"].get(obj, []) if t < OBS_HORIZON * 1440]


def _digest(sightings):
    lines = [f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — {o} seen at {rec}"
             for (t, o, rec) in sorted(sightings)]
    return "Observations:\n" + "\n".join(lines) if lines else "(no observations)"


def _obs_rows(sightings, tgt_events, obj):
    """Combined classical/LLM observation rows: persona sightings + first-k target
    events, as {day,t_min,parents}."""
    rows = [{"day": t//1440, "t_min": t, "parents": {o: rec}} for (t, o, rec) in sightings]
    rows += [{"day": t//1440, "t_min": t, "parents": {obj: rec}} for (t, rec) in tgt_events]
    rows.sort(key=lambda r: r["t_min"])
    return rows


def run(endpoint, model, label, bank=BANK, cfgmap=CFG, tag=""):
    client = OpenAIHTTPClient(endpoint, model)
    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    rows = []
    for hh in cfgmap:
        h = core.load_hh(bank, hh); cfg = cfgmap[hh]
        cand_set = h["cand_set"]; cands = h["cands"]
        diag_sight = _diag_digest_and_hist(h, cfg)
        for obj, hr in cfg["targets"]:
            tev = _target_events(h, obj)
            n_total = len(h["by_obj"].get(obj, []))
            rar = _rarity(n_total)
            # test queries: object at regime hour on the late test week (forward)
            qpts = [(qd, qd*1440 + hr*60,
                     true_parent_at(h["by_obj"], h["init"], obj, qd*1440 + hr*60))
                    for qd in TEST_DAYS]
            for k in K_GRID:
                kk = min(k, len(tev))
                first_k = tev[:kk]
                obs = _obs_rows(diag_sight, first_k, obj)
                # LLM digest = frozen format over persona + first-k target events
                digest = _digest(diag_sight + [(t, obj, r) for (t, r) in first_k])
                # classical arms fit on target events ONLY (per-edge learner)
                tgt_obs = [{"day": t//1440, "t_min": t, "parents": {obj: r}} for (t, r) in first_k]
                c3g = make_arm("C3g", cand_set, tgt_obs)[0] if tgt_obs else None
                c1 = make_arm("C1", cand_set, tgt_obs)[0] if tgt_obs else None

                def llm_one(qp):
                    qd, tq, true = qp
                    ep = {"object": obj, "t_query": tq, "true_receptacle": true}
                    am, top3c = _llm_pred(client, _SYS, digest, cands, ep)  # top3c: 0/1
                    return am, int(top3c)
                llm_out = list(pool.map(llm_one, qpts))

                def _emit(model, pred, top3c, true):
                    rows.append({"model": model, "hh": hh, "object": obj, "rarity": rar,
                                 "n_total": n_total, "k": kk, "pred": pred, "true": true,
                                 "correct": int(pred == true), "top3_correct": int(top3c)})
                for (qd, tq, true), (lam, ltop3) in zip(qpts, llm_out):
                    # classical last_obs = target's most recent observed event < tq
                    lo = [(t, r) for (t, r) in first_k if t < tq]
                    last_r, last_t = (lo[-1][1], lo[-1][0]) if lo else (None, None)
                    ep = {"object": obj, "t_query": tq, "last_obs": last_r, "last_obs_t": last_t}
                    for arm, rm in (("C3g", c3g), ("C1", c1)):
                        if rm is None:
                            bel = uniform_belief(cand_set)
                        else:
                            bel = _belief(rm, cand_set, obj, tq, ep, "categorical")
                        am, _, _, _, top3c = _rows_fields(bel, cand_set, true)
                        _emit("classical_"+arm, am, top3c, true)
                    _emit(label, lam, ltop3, true)
            print(f"[e7v2:{label}] {hh}:{obj} (n={n_total},{rar}) done", flush=True)
    pool.shutdown()
    core.OUT.mkdir(parents=True, exist_ok=True)
    (core.OUT / f"e7_rows_{tag}{label}.jsonl").write_text("".join(json.dumps(r)+"\n" for r in rows))
    if not tag:
        report(label)


def _boot(by_clu, nb=3000, seed=3):
    clus = list(by_clu)
    if not clus:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed); m = []
    for _ in range(nb):
        pick = rng.integers(0, len(clus), len(clus))
        vals = [v for i in pick for v in by_clu[clus[i]]]
        m.append(np.mean(vals) if vals else 0.0)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def report(label):
    rows = [json.loads(l) for l in (core.OUT / f"e7_rows_{label}.jsonl").read_text().splitlines() if l.strip()]
    arms = [label, "classical_C3g", "classical_C1"]
    print("\n" + "=" * 78)
    print(f"E7 v2 — accuracy vs EVENTS-OBSERVED, pooled & rarity-stratified (model={label})")
    print("  clustered 95% CI (cluster = household x object)")
    print("=" * 78)
    for rar, _, _ in TERCILES:
        objs = sorted({(r["hh"], r["object"]) for r in rows if r["rarity"] == rar})
        print(f"\n### {rar.upper()} tercile  ({len(objs)} objects)")
        print(f"  {'k(events)':>9}" + "".join(f"{a[:14]:>20}" for a in arms))
        for k in K_GRID:
            cells = []
            for a in arms:
                by = defaultdict(list)
                for r in rows:
                    if r["rarity"] == rar and r["model"] == a and r["k"] == k:
                        by[(r["hh"], r["object"])].append(r["correct"])
                allv = [v for vs in by.values() for v in vs]
                if not allv:
                    cells.append(f"{'-':>20}"); continue
                lo, hi = _boot(by)
                cells.append(f"{np.mean(allv):.2f}[{lo:.2f},{hi:.2f}]".rjust(20))
            print(f"  {k:>9}" + "".join(cells))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", required=True)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    report(args.label) if args.report_only else run(args.endpoint, args.model, args.label)


if __name__ == "__main__":
    main()
