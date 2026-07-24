"""reflect_DAG driver — arms for Changes 1-3 on the SAME confirmatory banks.

Reuses the frozen artifacts wherever possible (no re-elicitation of what exists):
  - persona + per-query LLM prior distributions: the stored llm_direct rows /
    memory snapshots from the VERSION22 runs (rows_v22*_distractor_d*.jsonl).
  - classical C3g: frozen, fit offline on the identical thinned stream.
New LLM calls (budget-logged): the per-household activity STRUCTURE proposal
(1 call) and the CounterfactCoT contrasts (2 x <=8 calls per household).

Arms emitted (rows JSONL, mergeable with the reflect tables):
  dag_persona_only     - alias of the stored llm_direct rows (baseline).
  dag_persona_dag      - persona + activity_DAG: ActivityTiedRates(llm structure)
                         + Tier-3 fusion of the stored per-query LLM prior at the
                         activity node (kappa from Tier-1 alpha*, since Tier-2 is
                         contingent on the calibration check).
  dag_persona_dag_cf   - same + Tier-2/3 kappa scaled by the household's
                         do-contrast (Change 2), unit constant U dev-calibrated.
  dag_only             - activity_DAG with NO persona conditioning in the
                         structure prompt (secondary check).
  dag_stat_params      - LLM structure, NO prior injection (llm_structure +
                         stat_params rung of the ladder).
  dag_no_llm_structure - no tying at all == frozen C3g (per-edge); logged as an
                         arm name for the ladder table.
  dag_scrambled        - LLM structure with object->activity assignments
                         scrambled (graceful-degradation control).

Usage:
  python -m dynbelief.reflect_dag.run_dag --bank v22 --level 6 [--endpoint ...]
Writes reports/reflect_dag/rows_dag_<bank>_d<level>.jsonl + structures/ dumps.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from dynbelief.h2 import core, e7_learning as e7
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.classical.filter import uniform_belief
from dynbelief.experiments.streams import true_parent_at
import dynbelief.reflect.run as R
from dynbelief.reflect.report import _load_rows
from dynbelief.reflect_dag.activity_graph import ActivityTiedRates, ActivityStructure
from dynbelief.reflect_dag.structure_elicit import (llm_structure, oracle_structure,
                                                    scramble_structure)
from dynbelief.reflect_dag.counterfact_elicit import do_contrast
from dynbelief.reflect_dag import precision_fusion as PF
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

OUT = core.OUT.parent / "reflect_dag"
CKPTS = R.CKPTS


def _thin_obs(h, ckpt):
    kept = R.thinned_event_tuples(h["by_obj"], R.OBS_PER_DAY, 0, ckpt * 1440)
    return kept, [{"day": t // 1440, "t_min": t, "parents": {o: r}} for (t, o, r) in kept]


def _digest_lines(h, dist_objs):
    """Sparse diagnostic digest = the first week's thinned lines (true stream
    only, no distractors — the structure prompt sees the same evidence class as
    the confirm-digest protocol)."""
    return R.stream_lines(h, 0, 7 * 1440, None)


def _persona_of(bank_dir, hh, label):
    """Persona string from the stored day-13 reflection memory (top hypothesis)."""
    p = R.OUT / "memory" / bank_dir / f"{hh}__{label}" / "day_13.json"
    if p.exists():
        try:
            mem = json.loads(p.read_text())
            hyps = mem.get("hypotheses") or []
            if hyps:
                return max(hyps, key=lambda x: x.get("prob", 0)).get("persona", "")
        except Exception:
            pass
    return ""


def _prior_dists(rows, hh):
    """(obj, ckpt, t_query) -> prior distribution from the stored llm_direct
    predictions (the same prior the old fusion consumed)."""
    out = {}
    for r in rows:
        if r["model"] == "llm_direct" and r["hh"] == hh and r.get("preds"):
            d = defaultdict(float)
            for p in r["preds"]:
                d[p["receptacle"]] += max(0.0, float(p["p"]))
            out[(r["object"], r["ckpt"], r["t_query"])] = dict(d)
    return out


def run(bank_key, level, endpoint, model, alpha_star, U, do_cf=True, reuse=False):
    bank_dir, cfgmap, test_days, _ = R.bank_of(bank_key)
    R.OBS_PER_DAY = ("rand", 3.0)
    R.DISTRACTORS = level
    label = f"distractor_d{level}"
    stored = _load_rows(bank_key, label)
    client = OpenAIHTTPClient(endpoint, model) if endpoint else None
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "structures").mkdir(exist_ok=True)

    rows, budget = [], defaultdict(int)
    for hh, cfg in cfgmap.items():
        h = core.load_hh(bank_dir, hh)
        cand_set = h["cand_set"]
        rmap = R.room_of(hh)
        persona = _persona_of(bank_dir, hh, label)
        digest = _digest_lines(h, None)
        priors = _prior_dists(stored, hh)
        observed_all = sorted({o for o, evs in h["by_obj"].items() if evs})

        # ── structure proposals ──
        cached = OUT / "structures" / f"{hh}_d{level}.json"
        if reuse and cached.exists():
            # offline re-run: reuse the stored LLM structures + contrast (no calls)
            d = json.loads(cached.read_text())
            def _st(k):
                x = d[k]
                return ActivityStructure(x["persona"], x["activity_objects"],
                                         x.get("atypical_activities") or [], x.get("source", "llm"))
            s_llm, s_noP, s_scr = _st("llm"), _st("no_persona"), _st("scrambled")
            contrast, cf_details, cf_calls = d.get("contrast", 0.0), d.get("cf_details", []), 0
        elif client is not None:
            s_llm = llm_structure(client, persona, "Observations:\n" + "\n".join(digest),
                                  observed_all)
            budget["structure_calls"] += 1
            s_noP = llm_structure(client, "(no persona inferred)",
                                  "Observations:\n" + "\n".join(digest), observed_all)
            budget["structure_calls"] += 1
            s_scr = scramble_structure(s_llm, seed=13)
            contrast, cf_details, cf_calls = 0.0, [], 0
            if do_cf and persona:
                contrast, cf_details, cf_calls = do_contrast(client, persona, digest)
                budget["cf_calls"] += cf_calls
        else:
            s_llm = s_noP = oracle_structure(hh.split("__")[0], set(observed_all),
                                             str(core.MANUAL_DIR))
            s_scr = scramble_structure(s_llm, seed=13)
            contrast, cf_details, cf_calls = 0.0, [], 0
        if not (reuse and cached.exists()):
            cached.write_text(json.dumps({
                "persona": persona, "llm": s_llm.__dict__, "no_persona": s_noP.__dict__,
                "scrambled": s_scr.__dict__, "contrast": contrast,
                "cf_details": cf_details}, indent=1, default=list))

        # ── per-checkpoint fits + queries ──
        for ckpt in CKPTS:
            kept, obs = _thin_obs(h, ckpt)
            c3g = make_arm("C3g", cand_set, obs)[0] if obs else None
            fits = {}
            for tag, st in (("dag", s_llm), ("dagonly", s_noP), ("scr", s_scr)):
                rm = ActivityTiedRates(cand_set, st)
                rm.fit(obs)
                fits[tag] = rm
            for (obj, hr) in cfg["targets"]:
                n_total = len(h["by_obj"].get(obj, []))
                for qd in test_days:
                    tq = qd * 1440 + hr * 60
                    true = true_parent_at(h["by_obj"], h["init"], obj, tq)
                    ev = [(t, r) for (t, o, r) in kept if o == obj and t < min(tq, ckpt * 1440)]
                    last = (ev[-1][1], ev[-1][0]) if ev else (None, None)
                    ep = {"object": obj, "t_query": tq, "last_obs": last[0],
                          "last_obs_t": last[1]}
                    prior = priors.get((obj, ckpt, tq))

                    def pred_of(rm):
                        if rm is None:
                            bel = uniform_belief(cand_set)
                        else:
                            bel = _belief(rm, cand_set, obj, tq, ep, "categorical")
                        return _rows_fields(bel, cand_set, None)[0]

                    base_row = {"bank": bank_dir, "hh": hh, "object": obj,
                                "ckpt": ckpt, "test_day": qd, "t_query": tq,
                                "true": true, "dist": level,
                                "rarity": e7._rarity(n_total),
                                "contrast": round(contrast, 4)}

                    def emit(arm, rm):
                        p = pred_of(rm)
                        rows.append({**base_row, "model": arm, "pred": p,
                                     "correct": int(p == true),
                                     "room_correct": int(rmap.get(p, "x") == rmap.get(true, "y"))})

                    emit("dag_stat_params", fits["dag"])          # tying only
                    emit("dag_only_stat", fits["dagonly"])        # no-persona tying
                    emit("dag_scrambled", fits["scr"])            # control
                    emit("dag_no_llm_structure", c3g)             # ladder floor == C3g
                    # Tier-3 fusion arms (prior at the activity node). DATA
                    # precision n_g = max(group pooled count, object's OWN event
                    # count): a rare object borrows its activity group's count
                    # (the tying win), but a DATA-RICH object is never overridden
                    # by the prior — its own evidence already makes its estimate
                    # at least that precise, so the prior fades as it should.
                    if prior:
                        own = len([1 for (t, o, r) in kept if o == obj and t < ckpt * 1440])
                        ng = max(fits["dag"].group_neff(obj), own)
                        emit("dag_persona_dag",
                             PF.PrecisionFusedRM(fits["dag"], obj, prior,
                                                 kappa=alpha_star, n_g=ng))
                        emit("dag_persona_dag_cf",
                             PF.PrecisionFusedRM(fits["dag"], obj, prior,
                                                 kappa=PF.kappa_edge(U, contrast), n_g=ng))
        print(f"[dag:{bank_key} d{level}] {hh} done (contrast={contrast:.2f})", flush=True)

    outf = OUT / f"rows_dag_{bank_key}_d{level}.jsonl"
    outf.write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"[dag] wrote {len(rows)} rows -> {outf}; llm budget: {dict(budget)}")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", choices=["v22", "v22b"], default="v22")
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--reuse-structures", action="store_true",
                    help="reuse stored LLM structures + contrast (offline re-run, no LLM calls)")
    ap.add_argument("--offline", action="store_true",
                    help="no LLM: oracle structure, no contrast (dev/debug)")
    ap.add_argument("--alpha-star", type=float, required=True,
                    help="Tier-1 alpha* (estimate with report_dag --tier1 first)")
    ap.add_argument("--unit-constant", type=float, required=True,
                    help="Tier-3 unit constant U (dev-calibrated)")
    args = ap.parse_args()
    run(args.bank, args.level, None if args.offline else args.endpoint,
        args.model, args.alpha_star, args.unit_constant, reuse=args.reuse_structures)


if __name__ == "__main__":
    main()
