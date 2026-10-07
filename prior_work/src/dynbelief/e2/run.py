"""E2 runner — one-shot prior help vs harm.

Two phases:
  --elicit   one-time API calls (gpt-5.4-mini + gpt-5.5), mixture-average per
             base profile -> results/e2/priors/<base>.json (+ raw dumps).
  (default)  offline eval grid: {typ_v1, atyp_v2} x D x kappa x {P0,Pllm,Porc}
             x {natural, moved_enriched}, primary family C3 + secondary C1.
             Every arm = identical filter+rate family; only the injected prior
             differs. -> results/e2/rows.parquet + summary + endpoints.

All fits share the pseudo-observation injection (inject.py); P0 injects
nothing (== the C-arm), Pllm the elicited pseudo-obs, Porc the oracle pseudo-obs.
"""
from __future__ import annotations

import json
import pathlib
import time

from dynbelief.classical.filter import Filter, uniform_belief
from dynbelief.classical.oracle import C5Oracle
from dynbelief.classical.rates import C1Constant, C3PeriodicGLM
from dynbelief.e2.elicit import elicit, mixture_average
from dynbelief.e2.inject import (KAPPA_DAYS, inject, pseudo_from_elicited,
                                 pseudo_from_oracle)
from dynbelief.experiments.e1 import score_prediction
from dynbelief.experiments.streams import load_gt, sample_stream
from dynbelief.profiles.schema import default_class, load_profile
from dynbelief.profiles import transforms

BASE_DESCRIPTORS = {
    "single_adult_typ_v1": "a single working adult's home",
    "college_roommates_typ_v1": "a home shared by two college students",
    "family4_typ_v1": "a two-parent, two-child family home",
}
D_GRID = [0, 1, 2, 3, 5, 7, 10, 14, 21, 28]
KAPPAS = ["weak", "moderate", "strong"]
STREAMS = ("natural", "moved_enriched")
N_PER_CELL = 60
FAMILIES = {"C3": C3PeriodicGLM, "C1": C1Constant}


# ── elicitation phase ────────────────────────────────────────────────────────

def do_elicit(manual_dir: pathlib.Path, out_dir: pathlib.Path, models) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for base, descriptor in BASE_DESCRIPTORS.items():
        prof = load_profile(manual_dir / f"{base}.yaml")
        classes = sorted({p.cls for p in prof.placements.values()})
        receptacles = sorted(prof.receptacle_ids)
        all_samples = []
        raw_dir = out_dir / "raw" / base
        for model in models:
            samples = elicit(model, descriptor, classes, receptacles,
                             n_samples=5, out_dir=raw_dir)
            all_samples += samples
        prior = mixture_average(all_samples, classes, receptacles)
        (out_dir / "priors").mkdir(parents=True, exist_ok=True)
        (out_dir / "priors" / f"{base}.json").write_text(json.dumps({
            "base": base, "descriptor": descriptor, "models": list(models),
            "n_samples_total": len(all_samples), "prior": prior}, indent=1))
        print(f"[e2] elicited {base}: {sum(1 for v in prior.values() if v)}/{len(classes)} classes")


# ── per-model prior rebuild (OFFLINE — reuses saved raw dumps, no API) ────────

MODEL_TAG = {"gpt-5.4-mini": "mini", "gpt-5.5": "gpt55"}


def rebuild_per_model(manual_dir: pathlib.Path, out_dir: pathlib.Path, models) -> None:
    """Re-derive one prior PER MODEL from the raw elicitation dumps already on
    disk (results/e2/raw/<base>/raw_<model>.json). Mixture-average within a
    single model's samples only — never pooling mini and gpt-5.5 — so the two
    models' priors stay separable (they have different capabilities). Writes
    out_dir/priors_<tag>/<base>.json for each model. NO API calls."""
    for model in models:
        tag = MODEL_TAG.get(model, model.replace("/", "_"))
        pdir = out_dir / f"priors_{tag}"
        pdir.mkdir(parents=True, exist_ok=True)
        for base, descriptor in BASE_DESCRIPTORS.items():
            prof = load_profile(manual_dir / f"{base}.yaml")
            classes = sorted({p.cls for p in prof.placements.values()})
            receptacles = sorted(prof.receptacle_ids)
            raw_f = out_dir / "raw" / base / f"raw_{model.replace('/', '_')}.json"
            if not raw_f.exists():
                print(f"[e2] MISSING raw dump: {raw_f}"); continue
            samples = json.loads(raw_f.read_text())["samples"]
            prior = mixture_average(samples, classes, receptacles)
            (pdir / f"{base}.json").write_text(json.dumps({
                "base": base, "descriptor": descriptor, "models": [model],
                "n_samples_total": len(samples), "prior": prior}, indent=1))
        print(f"[e2] rebuilt per-model priors ({model} -> {tag}) -> {pdir}")


# ── eval phase ───────────────────────────────────────────────────────────────

def _fit(family_cls, cand_set, hist):
    rm = family_cls(cand_set)
    rm.fit(hist)
    return rm


def _belief(rm, cand_set, ep):
    f = Filter(rm, cand_set, ep["object"], step_min=60)
    lo_r, lo_t = ep.get("last_obs"), ep.get("last_obs_t")
    if lo_r is None or lo_t is None:
        f.reset(ep["t_query"])
        return f.predict(ep["t_query"])
    f.reset(int(lo_t)); f.update((int(lo_t), lo_r))
    return f.predict(ep["t_query"])


def _score_rows(rm, cand_set, eps, bank, hh, D, kappa, prior, family, stream):
    rows = []
    for ep in eps:
        if rm is None:
            belief = uniform_belief(cand_set)
        else:
            belief = _belief(rm, cand_set, ep)
        top3 = sorted(belief.items(), key=lambda kv: -kv[1])[:3]
        preds = [{"receptacle": r, "p": p} for r, p in top3]
        argmax, p_true, brier, logloss, t3 = score_prediction(preds, cand_set, ep["true_receptacle"])
        rows.append({
            "bank": bank, "household": hh, "history_days": D, "kappa": kappa,
            "prior": prior, "family": family, "stream": stream,
            "query_id": ep["query_id"], "object": ep["object"],
            "class": default_class(ep["object"]), "held_out": ep["held_out"],
            "moved_since_obs": ep["moved_since_obs"], "true_receptacle": ep["true_receptacle"],
            "predicted": argmax, "p_true": round(p_true, 4), "brier": round(brier, 4),
            "logloss": round(logloss, 4), "correct": int(argmax == ep["true_receptacle"]),
            "top3_correct": t3,
        })
    return rows


def run_eval(banks_root, manual_dir, priors_dir, out_dir) -> None:
    priors = {p.stem: json.loads(p.read_text())["prior"]
              for p in (priors_dir).glob("*.json")}
    rows = []
    t0 = time.time()
    for bank in ("typ_v1", "atyp_v2"):
        bank_dir = banks_root / bank
        if not bank_dir.exists():
            continue
        for hh in sorted(p.name for p in bank_dir.iterdir()
                         if p.is_dir() and (p / "registry.json").exists()):
            by_obj, init, observations, targets, reg = load_gt(bank_dir / hh)
            recep_label = {int(v): k for k, v in reg["receptacles"].items()}
            cand_set = sorted(r for r in recep_label.values() if r != "elsewhere") + ["elsewhere"]
            heldout = set(targets["held_out"])
            base = reg["profile"]["household"].split("__")[0]
            obj_class = {o: default_class(o) for o in targets["observed"] + targets["held_out"]}
            elic = priors.get(base, {})
            prof = load_profile(manual_dir / f"{base}.yaml")
            if reg["profile"].get("transformation"):
                tf = reg["profile"]["transformation"]
                prof = transforms.apply_transform(prof, tf["type"], **tf["params"])
            oracle = C5Oracle(prof, cand_set, n_sims=120); oracle.fit([])
            for D in D_GRID:
                real = [{"day": r["day"], "t_min": r["t_min"],
                         "parents": {o: v for o, v in r["parents"].items() if o not in heldout}}
                        for r in observations if r["day"] < D]
                streams = {s: sample_stream(bank_dir / hh, bank, hh, D, s, N_PER_CELL)
                           for s in STREAMS}
                for fam_name, fam_cls in FAMILIES.items():
                    p0 = _fit(fam_cls, cand_set, real) if D > 0 else None
                    for s in STREAMS:
                        rows += _score_rows(p0, cand_set, streams[s], bank, hh, D,
                                            "n/a", "P0", fam_name, s)
                    for kappa in KAPPAS:
                        kd = KAPPA_DAYS[kappa]
                        ps_llm = pseudo_from_elicited(elic, obj_class, cand_set, kd, seed=7)
                        ps_orc = pseudo_from_oracle(oracle, obj_class, cand_set, kd, seed=7)
                        for prior_name, pseudo in (("Pllm", ps_llm), ("Porc", ps_orc)):
                            rm = _fit(fam_cls, cand_set, inject(real, pseudo))
                            for s in STREAMS:
                                rows += _score_rows(rm, cand_set, streams[s], bank, hh,
                                                    D, kappa, prior_name, fam_name, s)
            print(f"[e2] {bank}/{hh} done ({time.time()-t0:.0f}s, {len(rows)} rows)")
    out_dir.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    pd.DataFrame(rows).to_parquet(out_dir / "rows.parquet", index=False)
    print(f"[e2] {len(rows)} rows, wall {time.time()-t0:.0f}s -> {out_dir}")
    from dynbelief.e2.endpoints import write_endpoints
    write_endpoints(out_dir, banks_root)


def main(argv=None) -> int:
    import argparse
    from dynamic_home_eqa.paths import REPO_ROOT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--elicit", action="store_true", help="run the one-time API elicitation")
    ap.add_argument("--rebuild-per-model", action="store_true",
                    help="OFFLINE: re-derive one prior per model from saved raw dumps")
    ap.add_argument("--models", default="gpt-5.4-mini,gpt-5.5")
    ap.add_argument("--banks-root", type=pathlib.Path, default=REPO_ROOT / "banks")
    ap.add_argument("--manual-dir", type=pathlib.Path, default=REPO_ROOT / "profiles" / "manual")
    ap.add_argument("--out", type=pathlib.Path, default=REPO_ROOT / "results" / "e2")
    ap.add_argument("--priors-dir", type=pathlib.Path, default=None,
                    help="prior dir to eval (default <out>/priors); use for per-model runs")
    args = ap.parse_args(argv)
    if args.elicit:
        do_elicit(args.manual_dir, args.out, args.models.split(","))
        return 0
    if args.rebuild_per_model:
        rebuild_per_model(args.manual_dir, args.out, args.models.split(","))
        return 0
    priors_dir = args.priors_dir or (args.out / "priors")
    run_eval(args.banks_root, args.manual_dir, priors_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
