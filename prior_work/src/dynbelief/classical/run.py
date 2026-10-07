"""Classical-arm evaluation runner (Bank/Eval revisions R1-R5) — STRICT parity.

Same frozen banks (v2.2 eval protocol), the THREE tagged query streams
(natural / moved_enriched / held_out; never pooled), extended classical D grid
{0,1,2,3,5,7,10,14,21,28}, n>=100 per (bank,D,stream) cell, and the same
scoring code path (dynbelief.experiments.e1.score_prediction; top-3 + implied
remainder; Brier + log-loss clipped [0.01,0.99]).

Within a cell every arm scores the IDENTICAL episodes (streams are deterministic)
-> free paired per-episode deltas (computed in summary.py). Each row carries
`estimator_used` (R4 audit) and `window_weekend_frac` (R1 covariate).

Fit once per (household, D, arm); reused across the three streams (the history
window depends only on D). Hyperparameters selected on held-out observation
likelihood within the window (L4); D<=2 uses a fixed penalty (R4 low-D fix,
logged `low_d_fixed`), not a failed CV that silently falls back.

Run:  python -m dynbelief.classical.run
"""
from __future__ import annotations

import json
import pathlib
import time

import numpy as np

from dynbelief.classical.filter import Filter, uniform_belief
from dynbelief.classical.oracle import C5Oracle, C5Particle
from dynbelief.classical.rates import (C0LastObs, C1Constant, C2Spectral,
                                       C3PeriodicGLM, C3GatedGLM, C4RegimeHMM)
from dynbelief.classical.rates.base import heldout_loglik, split_history
from dynbelief.experiments.e1 import score_prediction
from dynbelief.experiments.streams import (
    D_GRID_CLASSICAL, N_PER_CELL_CLASSICAL, STREAMS, load_gt, sample_stream,
    true_parent_at,
)
from dynbelief.profiles.schema import default_class, load_profile

K_SWEEP = [1, 2, 3, 5]
C_SWEEP = [0.1, 1.0, 10.0]
REGIME_SWEEP = [2, 3, 4]
# C5  = particle/trajectory oracle (TRUE ceiling, captures conditional dependence)
# C5m = marginal oracle (the marginal ceiling, for the two-number comparison)
ARMS = ["C0", "C1", "C2", "C2pe", "C3", "C3g", "C4", "C5", "C5m"]
ARM_MODEL_NAME = {"C0": "C0_lastobs", "C1": "C1_constant", "C2": "C2_spectral",
                  "C2pe": "C2_spectral_peredge", "C3": "C3_glm", "C3g": "C3g_gated",
                  "C4": "C4_regime",
                  "C5": "C5plus_particle", "C5m": "C5_marginal"}


def make_arm(arm: str, cands: list[str], hist: list[dict]) -> tuple[object, dict]:
    info: dict = {"arm": arm, "degenerate": False, "low_d_fixed": False, "hyper": None}
    fit_rows, val_rows = split_history(hist)
    have_val = bool(val_rows)                     # >=2 distinct days
    if arm == "C0":
        rm = C0LastObs(cands)
    elif arm == "C1":
        rm = C1Constant(cands)
    elif arm in ("C2", "C2pe"):
        if have_val:
            sc = {}
            for K in K_SWEEP:
                tmp = C2Spectral(cands, K=K); tmp.fit(fit_rows)
                sc[K] = heldout_loglik(tmp, val_rows, cands)
            K = _best(sc, 2)
            info["hyper"] = {"K": K, "heldout_ll": _round(sc)}
        else:
            K = 2; info["low_d_fixed"] = True       # R4: fixed penalty at D<=2
            info["hyper"] = {"K": K, "heldout_ll": None}
        rm = C2Spectral(cands, K=K)
    elif arm == "C3":
        if have_val:
            sc = {}
            for C in C_SWEEP:
                tmp = C3PeriodicGLM(cands, C=C); tmp.fit(fit_rows)
                sc[C] = heldout_loglik(tmp, val_rows, cands)
            C = _best(sc, 1.0)
            info["hyper"] = {"C": C, "heldout_ll": _round(sc)}
        else:
            C = 1.0; info["low_d_fixed"] = True       # R4 fixed penalty
            info["hyper"] = {"C": C, "heldout_ll": None}
        rm = C3PeriodicGLM(cands, C=C)
    elif arm == "C3g":                            # FROZEN canonical classical (BIC-gated periodic)
        if have_val:
            sc = {}
            for C in C_SWEEP:
                tmp = C3GatedGLM(cands, C=C); tmp.fit(fit_rows)
                sc[C] = heldout_loglik(tmp, val_rows, cands)
            C = _best(sc, 1.0)
            info["hyper"] = {"C": C, "heldout_ll": _round(sc)}
        else:
            C = 1.0; info["low_d_fixed"] = True
            info["hyper"] = {"C": C, "heldout_ll": None}
        rm = C3GatedGLM(cands, C=C)
    elif arm == "C4":
        sc = {n: C4RegimeHMM(cands, n_regimes=n).heldout_day_loglik(hist)
              for n in REGIME_SWEEP}
        valid = {n: v for n, v in sc.items() if v == v}
        n = max(valid, key=valid.get) if valid else 2
        info["low_d_fixed"] = not valid
        info["hyper"] = {"n_regimes": n, "n_restarts": 5, "heldout_ll": _round(sc)}
        rm = C4RegimeHMM(cands, n_regimes=n)
    else:
        raise ValueError(arm)
    t0 = time.time()
    rm.fit(hist)
    info["fit_seconds"] = round(time.time() - t0, 3)
    info["degenerate"] = bool(getattr(rm, "degenerate", False))
    return rm, info


def _best(sc, default):
    valid = {k: v for k, v in sc.items() if v == v}
    return max(valid, key=valid.get) if valid else default


def _round(sc):
    return {str(k): (round(v, 4) if v == v else None) for k, v in sc.items()}


def _belief(rm, cands_all, obj, t_query, ep, mode):
    """The single shared prediction path. Condition on the episode's last
    observation at its true time, then propagate to t_query (real elapsed
    interval — the belief decays toward the rate model's occupancy)."""
    f = Filter(rm, cands_all, obj, mode=mode, step_min=60)
    lo_r, lo_t = ep.get("last_obs"), ep.get("last_obs_t")
    if lo_r is None or lo_t is None:             # no history (held-out / D=0)
        f.reset(t_query)
        return f.predict(t_query)
    f.reset(int(lo_t))
    f.update((int(lo_t), lo_r))
    return f.predict(t_query)


def _rows_fields(belief, cand_set, true_recep):
    top3 = sorted(belief.items(), key=lambda kv: -kv[1])[:3]
    preds = [{"receptacle": r, "p": round(p, 6)} for r, p in top3]
    return score_prediction(preds, cand_set, true_recep)   # 5-tuple incl top3


def run_bank(bank, bank_dir, manual_dir, d_grid, arms, fits_log, oracle_cache):
    rows = []
    hh_names = [p.name for p in sorted(bank_dir.iterdir())
                if p.is_dir() and (p / "registry.json").exists()]
    for hh in hh_names:
        by_obj, init, observations, targets, reg = load_gt(bank_dir / hh)
        recep_label = {int(v): k for k, v in reg["receptacles"].items()}
        cands = sorted(r for r in recep_label.values() if r != "elsewhere")
        cand_set = cands + ["elsewhere"]
        heldout = set(targets["held_out"])
        oracle_arms = {"C5", "C5m"} & set(arms)
        if oracle_arms and hh not in oracle_cache:
            oracle_cache[hh] = _build_oracle(reg, hh, bank, manual_dir, cand_set, fits_log)
        orc = oracle_cache.get(hh)      # {"particle":..., "marginal":...} or None
        for D in d_grid:
            hist = [{"day": r["day"], "t_min": r["t_min"],
                     "parents": {o: v for o, v in r["parents"].items() if o not in heldout}}
                    for r in observations if r["day"] < D]
            fitted = {}
            for arm in arms:
                if arm == "C5":
                    fitted[arm] = ((orc or {}).get("particle"), {"arm": "C5", "degenerate": False,
                                   "low_d_fixed": False, "hyper": None, "fit_seconds": 0.0})
                elif arm == "C5m":
                    fitted[arm] = ((orc or {}).get("marginal"), {"arm": "C5m", "degenerate": False,
                                   "low_d_fixed": False, "hyper": None, "fit_seconds": 0.0})
                elif D == 0:
                    fitted[arm] = (None, {"arm": arm, "degenerate": False,
                                   "low_d_fixed": False, "hyper": None, "fit_seconds": 0.0})
                else:
                    fitted[arm] = make_arm(arm, cand_set, hist)
                info = dict(fitted[arm][1]); info.update(bank=bank, household=hh, history_days=D)
                fits_log.append(info)
            for stream in STREAMS:
                eps = sample_stream(bank_dir / hh, bank, hh, D, stream, N_PER_CELL_CLASSICAL)
                for arm in arms:
                    rm, info = fitted[arm]
                    if arm in ("C5", "C5m") and rm is None:
                        continue                  # oracle excluded (per-object shift)
                    mode = "per_edge" if arm == "C2pe" else "categorical"
                    for ep in eps:
                        obj, tq, true = ep["object"], ep["t_query"], ep["true_receptacle"]
                        if arm == "C5":            # particle oracle: direct conditional posterior
                            belief = rm.predict_belief(obj, ep.get("last_obs"),
                                                       ep.get("last_obs_t"), tq)
                            est = rm.estimator_for(obj)
                        elif rm is None:
                            belief = uniform_belief(cand_set); est = "d0_uniform"
                        else:
                            belief = _belief(rm, cand_set, obj, tq, ep, mode)
                            est = rm.estimator_for(obj) if hasattr(rm, "estimator_for") else "?"
                        argmax, p_true, brier, logloss, top3 = _rows_fields(belief, cand_set, true)
                        rows.append({
                            "bank": bank, "household": hh, "history_days": D,
                            "stream": stream, "query_id": ep["query_id"],
                            "object": obj, "class": default_class(obj),
                            "tercile": ep["tercile"], "held_out": ep["held_out"],
                            "t_query": tq, "true_receptacle": true,
                            "predicted": argmax, "p_true": round(p_true, 4),
                            "brier": round(brier, 4), "logloss": round(logloss, 4),
                            "correct": int(argmax == true), "top3_correct": top3,
                            "moved_since_obs": ep["moved_since_obs"],
                            "window_weekend_frac": ep["window_weekend_frac"],
                            "model": ARM_MODEL_NAME[arm], "state_mode": mode,
                            "estimator_used": est,
                            "degenerate_fit": bool(info["degenerate"] or info["low_d_fixed"]),
                        })
    return rows


def _build_oracle(reg, hh, bank, manual_dir, cand_set, fits_log):
    if reg.get("per_object_shift"):
        return None
    base = reg["profile"]["household"].split("__")[0]
    prof = load_profile(manual_dir / f"{base}.yaml")
    if reg["profile"].get("transformation"):
        from dynbelief.profiles import transforms
        tf = reg["profile"]["transformation"]
        prof = transforms.apply_transform(prof, tf["type"], **tf["params"])
    t0 = time.time()
    marginal = C5Oracle(prof, cand_set); marginal.fit([])
    particle = C5Particle(prof, cand_set); particle.fit()
    fits_log.append({"bank": bank, "household": hh, "arm": "C5/C5m", "history_days": "all",
                     "fit_seconds": round(time.time() - t0, 2), "degenerate": False,
                     "low_d_fixed": False,
                     "hyper": {"marginal_n_sims": marginal.n_sims,
                               "particle_n": particle.n_particles}})
    return {"marginal": marginal, "particle": particle}


def main(argv=None) -> int:
    import argparse
    from dynamic_home_eqa.paths import REPO_ROOT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--banks-root", type=pathlib.Path, default=REPO_ROOT / "banks")
    ap.add_argument("--manual-dir", type=pathlib.Path, default=REPO_ROOT / "profiles" / "manual")
    ap.add_argument("--out", type=pathlib.Path, default=REPO_ROOT / "results" / "classical")
    ap.add_argument("--arms", default=",".join(ARMS))
    args = ap.parse_args(argv)
    arms = args.arms.split(",")
    fits_log, oracle_cache, rows = [], {}, []
    t0 = time.time()
    for bank in ("typ_v1", "atyp_v2"):
        bd = args.banks_root / bank
        if bd.exists():
            rows += run_bank(bank, bd, args.manual_dir, D_GRID_CLASSICAL, arms,
                             fits_log, oracle_cache)
    # atyp_shift_v1 C4-attribution control at D=7 only (no C5)
    bd = args.banks_root / "atyp_shift_v1"
    if bd.exists():
        rows += run_bank("atyp_shift_v1", bd, args.manual_dir, [7],
                         [a for a in arms if a != "C5"], fits_log, oracle_cache)
    wall = time.time() - t0
    args.out.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    pd.DataFrame(rows).to_parquet(args.out / "rows.parquet", index=False)
    with open(args.out / "fits.jsonl", "w") as f:
        for r in fits_log:
            f.write(json.dumps(r) + "\n")
    print(f"[classical] {len(rows)} rows, {len(fits_log)} fits, wall {wall:.1f}s -> {args.out}")
    from dynbelief.classical.summary import write_summary
    write_summary(args.out, REPO_ROOT)
    _dump_regime_schedule(args)
    return 0


def _dump_regime_schedule(args) -> None:
    bank_dir = args.banks_root / "atyp_v2"
    t1 = next((p.name for p in bank_dir.iterdir() if "t1_night" in p.name), None)
    if t1 is None:
        return
    _by, _init, observations, _t, reg = load_gt(bank_dir / t1)
    recep_label = {int(v): k for k, v in reg["receptacles"].items()}
    cands = sorted(r for r in recep_label.values() if r != "elsewhere") + ["elsewhere"]
    hist = [r for r in observations if r["day"] < 14]
    c4 = C4RegimeHMM(cands, n_regimes=2); c4.fit(hist)
    days = sorted({r["day"] for r in hist})
    dows = "Mo Tu We Th Fr Sa Su".split()
    L = ["# W4 — learned regime schedule, T1 night-shift (D=14, K=2)", "",
         "| day | dow | P(R0) | argmax |", "|---|---|---|---|"]
    for i, d in enumerate(days):
        g = c4.regime_schedule[i]
        L.append(f"| {d} | {dows[d % 7]} | {g[0]:.2f} | R{int(np.argmax(g))} |")
    sep = len({int(np.argmax(c4.regime_schedule[i])) for i, d in enumerate(days)}) > 1
    L += ["", f"Regimes separate workday/off-day: {'YES' if sep else 'NO'} "
          f"(NO = the classical inferencer misses the two-regime structure the T1 "
          f"transform injected; the manifest's W2 day-type stats prove it exists — "
          f"the opening a language-prior arm is hypothesized to exploit)."]
    (args.out / "regime_schedule_t1.md").write_text("\n".join(L))


if __name__ == "__main__":
    raise SystemExit(main())
