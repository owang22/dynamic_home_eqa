"""CONFIRMATORY run — frozen prompt/schema/digest from E5, applied to 3 NEW
confusable pairs never seen during design (dev/test wall). E5 = design study;
this = the result.

Arms:
  classical   — C3 per-edge (control; 0 on held-out by construction).
  class_freq  — the STRONGEST simple baseline (item 3): the typ-population class
                table that BEAT the LLM zero-shot in E0. Places conventionally ->
                should fail specifically on regime-FLIPPED objects. The honest
                comparison, reported instead of classical's 0.00.
  llm_named   — frozen E5 regime prompt/schema/digest, named.
  llm_anon    — same, semantics stripped (mechanism isolation).
  e4_hybrid   — item 4: the LLM reads the digest ONCE and emits a revised
                per-object prior (regime-aware home); consumed as a static prior.
                Designed to inherit the LLM's transfer on regime-dependent objects
                and the frequency table's reliability on conventional ones.

Query design is UNIFORM: every household's regime-dependent TARGETS and a matched
set of CONVENTIONAL held-out objects, each queried at a fixed hour across the same
weekday grid. Clustered bootstrap CIs (by household). Multi-model via --model.

FROZEN (do not edit after pre-registration): e5_regime._SYS, REGIME_SCHEMA, and
the "Day D, HH:MM — obj seen at rec" digest format.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from dynbelief.h2 import core
from dynbelief.h2.e5_regime import _SYS, REGIME_SCHEMA          # FROZEN
from dynbelief.h2 import e0_baselines as e0
from dynbelief.experiments.streams import true_parent_at
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.classical.filter import uniform_belief
from dynbelief.experiments.e1 import score_prediction
from dynbelief.profiles.schema import default_class, load_profile
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

BANK = "atyp_regime_confirm_v1"
SIGHT_DAYS = list(range(0, 12))                 # search window for diagnostic sightings
QUERY_DAYS = [7, 8, 9, 10, 11, 14, 15, 16, 17, 18]   # weekdays of weeks 2-3 (uniform)

# (object, query hour). targets = regime-flipped; conventional = typical.
CFG = {
 "regime_retiree_gardener_v1": {
   "diag": [("gardening_gloves", 9), ("watering_can", 9), ("newspaper", 7)],
   "targets": [("coffee_mug", 10), ("phone", 10), ("reading_glasses", 15)],
   "conv": [("plate", 5), ("bowl", 5)]},
 "regime_wfh_senior_v1": {
   "diag": [("laptop", 10), ("headset", 10), ("webcam", 14)],
   "targets": [("coffee_mug", 14), ("phone", 14), ("reading_glasses", 11)],
   "conv": [("plate", 5), ("bowl", 5)]},
 "regime_toddler_home_v1": {
   "diag": [("sippy_cup", 7), ("board_book", 19), ("toy_blocks", 10)],
   "targets": [("cushion", 16), ("blanket", 16), ("ball", 10)],
   "conv": [("plate", 5), ("bowl", 5)]},
 "regime_pet_heavy_v1": {
   "diag": [("dog_leash", 7), ("food_bowl", 8), ("chew_toy", 15)],
   "targets": [("cushion", 11), ("blanket", 16), ("ball", 15)],
   "conv": [("plate", 5), ("bowl", 5)]},
 "regime_shift_rotator_v1": {
   "diag": [("work_badge", 5), ("hi_vis_vest", 5), ("thermos", 5)],
   "targets": [("laptop", 20), ("phone", 10), ("keys", 20)],
   "conv": [("plate", 5), ("bowl", 5)]},
 "regime_frequent_traveler_v1": {
   "diag": [("suitcase", 20), ("passport", 20), ("packing_cubes", 20)],
   "targets": [("laptop", 14), ("phone", 21), ("keys", 14)],
   "conv": [("plate", 5), ("bowl", 5)]},
}
# Pre-registration lives in reports/h2_adaptation/PREREGISTRATION.md, written
# BEFORE any confirmatory LLM call.


def _digest_hist(h, cfg):
    """FROZEN format; robust day-selection: for each diagnostic object find up to
    2 days where it is in a non-elsewhere (telling) spot."""
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
    sightings.sort()
    lines = [f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — {o} seen at {rec}"
             for (t, o, rec) in sightings]
    digest = "Observations:\n" + "\n".join(lines) if lines else "(no observations)"
    by_t = defaultdict(dict)
    for (t, o, rec) in sightings:
        by_t[t][o] = rec
    hist = [{"day": t//1440, "t_min": t, "parents": p} for t, p in sorted(by_t.items())]
    return digest, hist


def _queries(h, cfg, hh):
    eps = []
    for kind, key in (("target", "targets"), ("conventional", "conv")):
        for i, (obj, hr) in enumerate(cfg[key]):
            for j, qd in enumerate(QUERY_DAYS):
                t = qd * 1440 + hr * 60
                true = true_parent_at(h["by_obj"], h["init"], obj, t)
                eps.append({"bank": BANK, "household": hh, "kind": kind,
                            "object": obj, "t_query": t, "true_receptacle": true,
                            "last_obs": None, "held_out": True})
    return eps


def _llm_pred(client, sys, digest, cands, ep, temperature=0.0):
    clk = f"{(ep['t_query']%1440)//60:02d}:{(ep['t_query']%1440)%60:02d}"
    day = ep["t_query"]//1440
    user = (f"{digest}\n\nCandidate receptacles: {', '.join(cands)}, elsewhere.\n\n"
            f"Question: on day {day} at {clk}, where is the {ep['object']}?")
    try:
        out = json.loads(client.generate(sys, user, REGIME_SCHEMA, seed=7, temperature=temperature))
        preds = out["predictions"]
    except Exception:
        preds = []
    am, pt, br, ll, t3 = score_prediction(preds, cands + ["elsewhere"], ep["true_receptacle"])
    return am, t3


_E4_SCHEMA = {"type": "object", "properties": {
    "regime_hypothesis": {"type": "string"},
    "placements": {"type": "array", "items": {"type": "object", "properties": {
        "object": {"type": "string"}, "receptacle": {"type": "string"},
        "regime_shifted": {"type": "boolean"}},
        "required": ["object", "receptacle", "regime_shifted"]}}},
    "required": ["regime_hypothesis", "placements"]}
_E4_SYS = (_SYS + " You will be given a LIST of objects. For EACH, decide whether "
           "the inferred routine RELOCATES it from its usual home ('regime_shifted': "
           "true) and, if so, give the regime-shifted receptacle; if the routine does "
           "NOT move it ('regime_shifted': false), still give your best receptacle. "
           "Only set regime_shifted=true when the persona specifically implies a "
           "non-standard location for that object.")


def _e4_prior(client, digest, cands, objs):
    """ONE call/household: LLM emits, per object, (receptacle, regime_shifted).
    The FUSION rule (item 4) is applied by the caller: use the LLM receptacle where
    regime_shifted, else defer to the class-frequency table. Returns
    {object: (receptacle, regime_shifted)}."""
    user = (f"{digest}\n\nCandidate receptacles: {', '.join(cands)}, elsewhere.\n\n"
            f"For each of these objects give (receptacle, regime_shifted) under the "
            f"inferred routine: {', '.join(objs)}.")
    try:
        out = json.loads(client.generate(_E4_SYS, user, _E4_SCHEMA, seed=7, temperature=0.0))
        return ({p["object"]: (p["receptacle"], bool(p.get("regime_shifted", False)))
                 for p in out["placements"]}, out.get("regime_hypothesis", ""))
    except Exception:
        return {}, ""


def run(endpoint, model, label):
    client = OpenAIHTTPClient(endpoint, model)
    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    e0._TYP = e0.typ_class_target()
    omap, rmap = core.anon_maps(BANK)
    rows, hyps = [], []
    for hh in core.households(BANK):
        base = hh.split("__")[0]; cfg = CFG[base]; h = core.load_hh(BANK, hh)
        room_of = {r.id: r.room for r in load_profile(core.MANUAL_DIR / f"{base}.yaml").receptacles}
        digest, hist = _digest_hist(h, cfg)
        eps = _queries(h, cfg, hh)
        rm = make_arm("C3", h["cand_set"], hist)[0] if hist else None
        # E4: one prior call for all queried objects
        objs = sorted({e["object"] for e in eps})
        e4map, e4hyp = _e4_prior(client, digest, h["cands"], objs)
        hyps.append((hh, e4hyp))
        # llm named/anon (parallel)
        adigest = core.anon_digest(digest, omap, rmap); acands = [rmap[c] for c in h["cands"]]
        named = list(pool.map(lambda e: _llm_pred(client, _SYS, digest, h["cands"], e), eps))
        anon = list(pool.map(lambda e: _llm_pred(client, _SYS, adigest, acands, core.anon_eps([e], omap, rmap)[0]), eps))
        for k, ep in enumerate(eps):
            base_row = {"model": label, "bank": BANK, "household": hh, "kind": ep["kind"],
                        "object": ep["object"], "true": ep["true_receptacle"]}
            # classical
            bel = _belief(rm, h["cand_set"], ep["object"], ep["t_query"], ep, "categorical") if rm else uniform_belief(h["cand_set"])
            cam = _rows_fields(bel, h["cand_set"], ep["true_receptacle"])[0]
            rows.append({**base_row, "arm": "classical", "correct": int(cam == ep["true_receptacle"])})
            # class_freq
            cf = e0.class_freq_predict(default_class(ep["object"]), h["cand_set"], room_of)
            rows.append({**base_row, "arm": "class_freq", "correct": int(cf == ep["true_receptacle"])})
            # llm named/anon
            rows.append({**base_row, "arm": "llm_named", "correct": int(named[k][0] == ep["true_receptacle"])})
            rows.append({**base_row, "arm": "llm_anon", "correct": int(anon[k][0] == ep["true_receptacle"])})
            # e4 FUSION: where the LLM flags a regime shift, take its PER-QUERY
            # (regime + time aware) prediction -> inherits the named transfer on
            # shifted objects; otherwise defer to the class-frequency table ->
            # inherits its reliability on conventional objects.
            _, shifted = e4map.get(ep["object"], (None, False))
            e4p = named[k][0] if shifted else cf
            rows.append({**base_row, "arm": "e4_hybrid", "correct": int(e4p == ep["true_receptacle"])})
        print(f"[confirm:{label}] {hh} done", flush=True)
    pool.shutdown()
    core.OUT.mkdir(parents=True, exist_ok=True)
    outf = core.OUT / f"confirm_rows_{label}.jsonl"
    with outf.open("a") as f:
        pass
    (core.OUT / f"confirm_rows_{label}.jsonl").write_text("".join(json.dumps(r)+"\n" for r in rows))
    (core.OUT / f"confirm_hyp_{label}.txt").write_text("\n".join(f"[{hh}] {hyp}" for hh, hyp in hyps))
    report([label])
    return rows


# semantics-necessary (predict named>>anon) vs structure-sufficient (named~=anon)
PREREG = {"regime_retiree_gardener_v1": "semantics", "regime_wfh_senior_v1": "structure",
          "regime_toddler_home_v1": "semantics", "regime_pet_heavy_v1": "semantics",
          "regime_shift_rotator_v1": "semantics", "regime_frequent_traveler_v1": "structure"}


def _boot(vals_by_hh, nb=2000, seed=0):
    hhs = list(vals_by_hh); rng = np.random.default_rng(seed)
    if not hhs:
        return (float("nan"),)*2
    means = []
    for _ in range(nb):
        pick = rng.integers(0, len(hhs), len(hhs))
        pool = [v for i in pick for v in vals_by_hh[hhs[i]]]
        means.append(np.mean(pool) if pool else 0.0)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def report(labels):
    for label in labels:
        p = core.OUT / f"confirm_rows_{label}.jsonl"
        if not p.exists():
            continue
        rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        print("\n" + "=" * 72)
        print(f"CONFIRMATORY — model={label}  (n={len({(r['household'],r['object'],r['kind']) for r in rows if r['arm']=='classical'})*len(QUERY_DAYS)//len(QUERY_DAYS)} queries/arm)")
        print("=" * 72)
        arms = ["classical", "class_freq", "llm_named", "llm_anon", "e4_hybrid"]
        for kind in ("target", "conventional"):
            print(f"\n  [{kind} objects]   (clustered 95% CI by household)")
            for arm in arms:
                by_hh = defaultdict(list)
                for r in rows:
                    if r["arm"] == arm and r["kind"] == kind:
                        by_hh[r["household"]].append(r["correct"])
                allv = [v for vs in by_hh.values() for v in vs]
                if not allv:
                    continue
                lo, hi = _boot(by_hh)
                print(f"    {arm:12} {np.mean(allv):.3f}  [{lo:.2f},{hi:.2f}]")
        # semantics gap per pre-registered household (targets only)
        print(f"\n  named-anon gap on TARGETS, by pre-registration:")
        for hh in sorted({r["household"] for r in rows}):
            nm = np.mean([r["correct"] for r in rows if r["household"]==hh and r["arm"]=="llm_named" and r["kind"]=="target"])
            an = np.mean([r["correct"] for r in rows if r["household"]==hh and r["arm"]=="llm_anon" and r["kind"]=="target"])
            pr = PREREG.get(hh.split("__")[0], "?")
            hit = "OK" if ((pr=="semantics" and nm-an>0.10) or (pr=="structure" and abs(nm-an)<=0.10)) else "MISS"
            print(f"    {hh.split('__')[0]:28} pred={pr:9} named-anon={nm-an:+.2f}  [{hit}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", required=True)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    if args.report_only:
        report([args.label])
    else:
        run(args.endpoint, args.model, args.label)


if __name__ == "__main__":
    main()
