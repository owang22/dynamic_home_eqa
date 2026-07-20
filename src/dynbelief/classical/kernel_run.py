"""Kernel-arm evaluation (transition-kernel brief). E1 arms K0/K1/K5; E2 arms
K1/K2/K3. Same banks/streams/scoring as before. PRIMARY metric = Brier
(top-1 -> appendix only: on moved_enriched it degenerates to the enrichment
ratio for any argmax that stays on the last-seen receptacle). Emits the D1
(sparsity/backoff) and D2 (discarded-pair) diagnostics.
"""
from __future__ import annotations

import json
import pathlib
import time

import numpy as np

from dynbelief.classical.kernel import KernelModel
from dynbelief.classical.oracle import C5Particle
from dynbelief.experiments.e1 import score_prediction
from dynbelief.experiments.streams import (D_GRID_CLASSICAL, N_PER_CELL_CLASSICAL,
                                           STREAMS, load_gt, sample_stream)
from dynbelief.profiles.schema import default_class, load_profile
from dynbelief.profiles import transforms

BIN_HOURS = 4                       # cadence-matched (obs ~7h apart; 1h/2h unusable)


def _k0_belief(cand_set, ep):
    r = ep.get("last_obs")
    if r is None:
        return {c: 1.0 / len(cand_set) for c in cand_set}
    return {c: (1.0 if c == r else 0.0) for c in cand_set}


def _score(belief, cand_set, true):
    top3 = sorted(belief.items(), key=lambda kv: -kv[1])[:3]
    preds = [{"receptacle": r, "p": p} for r, p in top3]
    return score_prediction(preds, cand_set, true)


def _oracle(reg, manual_dir, cand_set):
    if reg.get("per_object_shift"):
        return None
    base = reg["profile"]["household"].split("__")[0]
    prof = load_profile(manual_dir / f"{base}.yaml")
    if reg["profile"].get("transformation"):
        tf = reg["profile"]["transformation"]
        prof = transforms.apply_transform(prof, tf["type"], **tf["params"])
    p = C5Particle(prof, cand_set); p.fit()
    return p


def run_e1(banks_root, manual_dir, out_dir, arms=("K0", "K1", "K5")):
    rows, diag = [], []
    t0 = time.time()
    for bank in ("typ_v1", "atyp_v2"):
        bank_dir = banks_root / bank
        if not bank_dir.exists():
            continue
        for hh in sorted(p.name for p in bank_dir.iterdir()
                         if p.is_dir() and (p / "registry.json").exists()):
            by_obj, init, observations, targets, reg = load_gt(bank_dir / hh)
            recep = {int(v): k for k, v in reg["receptacles"].items()}
            cand_set = sorted(r for r in recep.values() if r != "elsewhere") + ["elsewhere"]
            heldout = set(targets["held_out"])
            oracle = _oracle(reg, manual_dir, cand_set) if "K5" in arms else None
            for D in D_GRID_CLASSICAL:
                hist = [{"day": r["day"], "t_min": r["t_min"],
                         "parents": {o: v for o, v in r["parents"].items() if o not in heldout}}
                        for r in observations if r["day"] < D]
                k1 = KernelModel(cand_set, bin_hours=BIN_HOURS) if D > 0 else None
                if k1:
                    k1.fit(hist)
                    # D2 diagnostic: discard fraction at 1h/2h/4h for this (hh,D)
                    if D in (7, 14, 28):
                        for bh in (1, 2, 4):
                            km = KernelModel(cand_set, bin_hours=bh); km.fit(hist)
                            diag.append({"bank": bank, "household": hh, "history_days": D,
                                         "bin_hours": bh, "discard_frac": round(km.discard_frac, 3),
                                         "kept": km.kept})
                for stream in STREAMS:
                    eps = sample_stream(bank_dir / hh, bank, hh, D, stream, N_PER_CELL_CLASSICAL)
                    for arm in arms:
                        if arm == "K5" and oracle is None:
                            continue
                        for ep in eps:
                            obj, tq, true = ep["object"], ep["t_query"], ep["true_receptacle"]
                            level = "-"
                            if arm == "K0":
                                belief = _k0_belief(cand_set, ep)
                            elif arm == "K1":
                                if k1 is None:
                                    belief = {c: 1.0 / len(cand_set) for c in cand_set}
                                else:
                                    belief, level = k1.predict_belief(
                                        obj, ep.get("last_obs"), ep.get("last_obs_t"), tq)
                            else:  # K5
                                belief, level = oracle.predict_belief(
                                    obj, ep.get("last_obs"), ep.get("last_obs_t"), tq), oracle.used
                            argmax, p_true, brier, logloss, t3 = _score(belief, cand_set, true)
                            rows.append({
                                "bank": bank, "household": hh, "history_days": D,
                                "stream": stream, "query_id": ep["query_id"], "arm": arm,
                                "object": obj, "class": default_class(obj),
                                "held_out": ep["held_out"], "moved_since_obs": ep["moved_since_obs"],
                                "true_receptacle": true, "predicted": argmax,
                                "p_true": round(p_true, 4), "brier": round(brier, 4),
                                "logloss": round(logloss, 4), "correct": int(argmax == true),
                                "top3_correct": t3, "backoff_level": level,
                            })
        print(f"[kernel] {bank} done ({time.time()-t0:.0f}s, {len(rows)} rows)")
    out_dir.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    pd.DataFrame(rows).to_parquet(out_dir / "rows_e1.parquet", index=False)
    pd.DataFrame(diag).to_json(out_dir / "diag_discard.jsonl", orient="records", lines=True)
    print(f"[kernel] E1: {len(rows)} rows, wall {time.time()-t0:.0f}s -> {out_dir}")
    _write_e1_summary(out_dir, pd.DataFrame(rows), pd.DataFrame(diag))


def _write_e1_summary(out_dir, df, diag):
    from dynbelief.experiments.stats import boot_ci, fmt_ci, paired_delta_ci
    D_SHOW = [0, 1, 2, 3, 5, 7, 10, 14, 21, 28]
    me = df[df["stream"] == "moved_enriched"]
    L = ["# Kernel arms (K0/K1/K5) — E1, Brier-PRIMARY", "",
         f"{len(df)} rows. Transition kernel replaces marginal C1-C4. bin_hours="
         f"{BIN_HOURS} (cadence-matched; 1h/2h discard >90% of pairs, see D2). "
         "PRIMARY = Brier (lower better); top-3 secondary; top-1 in appendix.", ""]
    # D2 sparsity
    if len(diag):
        L += ["## D2 — discarded-pair fraction by bin width (why bins are wide)", "",
              "| bin | mean discard frac | mean kept pairs |", "|---|---|---|"]
        for bh in (1, 2, 4):
            s = diag[diag["bin_hours"] == bh]
            L.append(f"| {bh}h | {s['discard_frac'].mean():.2%} | {s['kept'].mean():.0f} |")
        L += ["", "1h/2h bins discard almost every pair at this observation cadence "
              "(~7h between snapshots) -> 4h operational. This is a data-density limit, "
              "not a modeling choice; EM was deliberately avoided (states are observed).", ""]
    # Brier curve (moved_enriched) + not-moved
    for metric, lab, lo in (("brier", "Brier (PRIMARY, lower=better)", True),
                            ("top3_correct", "top-3 acc (secondary)", False)):
        L += [f"## {lab} vs D (moved_enriched, mean [95% CI])", "",
              "| arm | " + " | ".join(f"D{d}" for d in D_SHOW) + " |", "|---|" + "---|" * len(D_SHOW)]
        for arm in ("K0", "K1", "K5"):
            cells = []
            for d in D_SHOW:
                s = me[(me["arm"] == arm) & (me["history_days"] == d)]
                cells.append(fmt_ci(*boot_ci(s[metric])) if len(s) else "-")
            L.append(f"| {arm} | " + " | ".join(cells) + " |")
        L.append("")
    # paired K1-K0 (Brier), pooled D>=1
    L += ["## Paired K1 - K0 (Brier; same episodes; moved_enriched, pooled D>=1)", "",
          "| slice | ΔBrier [95% CI] | n |", "|---|---|---|"]
    def key(r): return (r["bank"], r["household"], r["history_days"], r["stream"], r["query_id"])
    for slc, f in [("all", lambda r: True), ("moved", lambda r: r["moved_since_obs"] == 1),
                   ("not-moved", lambda r: r["moved_since_obs"] == 0)]:
        base = me[(me["history_days"] >= 1)]
        k0 = {key(r): r["brier"] for _, r in base[base["arm"] == "K0"].iterrows() if f(r)}
        k1 = {key(r): r["brier"] for _, r in base[base["arm"] == "K1"].iterrows() if f(r)}
        m, ci, n = paired_delta_ci(k1, k0)
        L.append(f"| {slc} | {fmt_ci(m, ci)} | {n} |")
    L += ["", "Negative ΔBrier = K1 better-calibrated than last-obs parroting. This is "
          "the headline the marginal arms could not move (their paired Δacc was ~0)."]
    # D4: K1 vs K5 gap by slice (Brier)
    L += ["", "## D4 — K1 vs K5 headroom by slice (moved_enriched Brier, pooled D>=1)", "",
          "| slice | K0 | K1 | K5 |", "|---|---|---|---|"]
    for slc, f in [("moved", 1), ("not-moved", 0)]:
        s = me[(me["history_days"] >= 1) & (me["moved_since_obs"] == f)]
        L.append(f"| {slc} | {s[s.arm=='K0']['brier'].mean():.3f} | "
                 f"{s[s.arm=='K1']['brier'].mean():.3f} | {s[s.arm=='K5']['brier'].mean():.3f} |")
    (out_dir / "summary_e1.md").write_text("\n".join(L))
    print(f"[kernel] E1 summary -> {out_dir/'summary_e1.md'}")


def main(argv=None) -> int:
    import argparse
    from dynamic_home_eqa.paths import REPO_ROOT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--banks-root", type=pathlib.Path, default=REPO_ROOT / "banks")
    ap.add_argument("--manual-dir", type=pathlib.Path, default=REPO_ROOT / "profiles" / "manual")
    ap.add_argument("--out", type=pathlib.Path, default=REPO_ROOT / "results" / "kernel")
    args = ap.parse_args(argv)
    run_e1(args.banks_root, args.manual_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
