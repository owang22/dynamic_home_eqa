"""E4 v2 — the EVIDENCE-ROUTED hybrid, with a dev/test wall.

Item 4, upgraded per the E7 crossover: instead of routing LLM-vs-table by a
regime-shift flag, route by EVIDENCE. Per object, if the number of events observed
for THAT object is below a frozen threshold tau* (the rare regime where the
per-edge classical provably has not learned), take the LLM's regime-conditioned
prediction; otherwise defer to the frozen gated-C3 classical. The routing rule is
exactly the rare/frequent crossover from the E7 curves turned into a mechanism.

Dev/test wall: tau* is chosen ONLY on the design bank (atyp_regime_v1, 4 dev
households) as the smallest events-observed k at which pooled C3g catches the
pooled LLM; it is then FROZEN and applied unchanged to the confirmatory bank
(atyp_regime_confirm_v1, 6 held-out households).

Pre-registered claim: within EVERY rarity stratum, hybrid accuracy >= max(LLM,
C3g) -- it inherits the LLM's head start on rare objects (few events -> route LLM)
and classical's ceiling on frequent objects (many events -> route C3g).

Uses the E7 v2 per-(object,k,query) rows for both banks (run e7_learning on each
bank first). No new LLM prompt/schema -- reuses the frozen ones through E7.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np

from dynbelief.h2 import core, e7_learning as e7
from dynbelief.h2.e5_regime import CFG as _E5CFG

DEV_BANK = "atyp_regime_v1"
# normalize the dev CFG (e5 uses "diagnostic"/"ambient"/"targets") to the E7 shape
DEV_CFG = {hh: {"diag": c["diagnostic"], "targets": c["targets"]}
           for hh, c in _E5CFG.items()}


def run_dev(endpoint, model, label):
    """Generate the DEV-bank E7 curves used to pick tau* (writes e7_rows_dev_*)."""
    e7.run(endpoint, model, label, bank=DEV_BANK, cfgmap=DEV_CFG, tag="dev_")


def _load(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def _pooled_by_k(rows, model, rarity=None):
    """mean accuracy per events-observed k, pooled over objects (optionally within
    one rarity stratum)."""
    by = defaultdict(list)
    for r in rows:
        if r["model"] == model and (rarity is None or r["rarity"] == rarity):
            by[r["k"]].append(r["correct"])
    return {k: float(np.mean(v)) for k, v in by.items()}


def pick_tau_stratum(dev_rows, llm_label, rarity):
    """Per-stratum tau*: smallest k where dev C3g >= dev LLM within this rarity
    stratum; a large sentinel (always-LLM) if classical never catches up on dev."""
    llm = _pooled_by_k(dev_rows, llm_label, rarity)
    cls = _pooled_by_k(dev_rows, "classical_C3g", rarity)
    ks = sorted(set(llm) & set(cls))
    for k in ks:
        if k > 0 and cls[k] >= llm[k]:
            return k
    return 10**9   # classical never overtakes on dev -> always route LLM


def pick_tau(dev_rows, llm_label):
    """tau* = smallest k at which pooled classical (C3g) >= pooled LLM on DEV.
    Below tau*, LLM leads -> route LLM; at/above, classical has caught up."""
    llm = _pooled_by_k(dev_rows, llm_label)
    cls = _pooled_by_k(dev_rows, "classical_C3g")
    ks = sorted(set(llm) & set(cls))
    for k in ks:
        if k > 0 and cls[k] >= llm[k]:
            return k, llm, cls
    return (max(ks) + 1 if ks else 1), llm, cls   # classical never catches -> always LLM


def _boot(by_clu, nb=3000, seed=5):
    clus = list(by_clu)
    if not clus:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed); m = []
    for _ in range(nb):
        pick = rng.integers(0, len(clus), len(clus))
        vals = [v for i in pick for v in by_clu[clus[i]]]
        m.append(np.mean(vals) if vals else 0.0)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def evaluate(conf_rows, llm_label, tau):
    """Build the hybrid arm on the confirmatory rows by routing each (object,k,
    query) triple: LLM if k < tau[rarity] else C3g. `tau` is a dict rarity->threshold
    (a scalar is broadcast to all strata). Report per rarity stratum: LLM, C3g,
    hybrid means with clustered CIs, and the pre-registered check."""
    if not isinstance(tau, dict):
        tau = {rar: tau for rar, _, _ in e7.TERCILES}
    # Rows come per query as a group of arms {classical_C3g, classical_C1, <llm>}
    # sharing the same (hh,object,k). Rebuild those groups by key + occurrence index
    # (row emission order is stable within a key), then route each group.
    triples = defaultdict(dict)
    order = defaultdict(int)
    for r in conf_rows:
        key = (r["hh"], r["object"], r["k"])
        i = order[(key, r["model"])]
        triples[(key, i)][r["model"]] = r
        order[(key, r["model"])] += 1
    strata = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # rar->arm->clu->[correct]
    for (key, i), d in triples.items():
        if llm_label not in d or "classical_C3g" not in d:
            continue
        rr = d[llm_label]; rar = rr["rarity"]; clu = (rr["hh"], rr["object"])
        k = rr["k"]
        hyb = d[llm_label]["correct"] if k < tau[rar] else d["classical_C3g"]["correct"]
        strata[rar][llm_label][clu].append(d[llm_label]["correct"])
        strata[rar]["classical_C3g"][clu].append(d["classical_C3g"]["correct"])
        strata[rar]["hybrid"][clu].append(hyb)
    return strata


def report(llm_label="deepseek"):
    dev = _load(core.OUT / f"e7_rows_dev_{llm_label}.jsonl")
    conf = _load(core.OUT / f"e7_rows_{llm_label}.jsonl")
    tau_g, dllm, dcls = pick_tau(dev, llm_label)
    tau_s = {rar: pick_tau_stratum(dev, llm_label, rar) for rar, _, _ in e7.TERCILES}
    print("=" * 78)
    print(f"E4 v2 — EVIDENCE-ROUTED HYBRID   (model={llm_label})")
    print("=" * 78)
    print(f"\nDEV threshold selection (bank={DEV_BANK}):  pooled accuracy vs k")
    print(f"  {'k':>4}{'LLM':>10}{'C3g':>10}")
    for k in sorted(set(dllm) & set(dcls)):
        print(f"  {k:>4}{dllm[k]:>10.2f}{dcls[k]:>10.2f}")
    print(f"\n  GLOBAL  tau* = {tau_g} events")
    print(f"  RARITY-AWARE tau* (per stratum, from dev): "
          + ", ".join(f"{r}={'∞' if tau_s[r]>=10**8 else tau_s[r]}" for r in tau_s))

    def _eval_and_print(tau, header):
        strata = evaluate(conf, llm_label, tau)
        print(f"\n{header}  — clustered 95% CI (bank=atyp_regime_confirm_v1):")
        print(f"  {'stratum':10}{'LLM':>22}{'C3g':>22}{'hybrid':>22}{'  claim':>10}")
        ok_all = True
        for rar, _, _ in e7.TERCILES:
            s = strata.get(rar)
            if not s:
                continue
            cells = {}; means = {}
            for arm in (llm_label, "classical_C3g", "hybrid"):
                allv = [v for vs in s[arm].values() for v in vs]
                lo, hi = _boot(s[arm]); means[arm] = np.mean(allv)
                cells[arm] = f"{np.mean(allv):.2f}[{lo:.2f},{hi:.2f}]".rjust(22)
            claim = means["hybrid"] >= max(means[llm_label], means["classical_C3g"]) - 1e-9
            ok_all &= claim
            print(f"  {rar:10}" + cells[llm_label] + cells["classical_C3g"] +
                  cells["hybrid"] + f"{'PASS' if claim else 'FAIL':>10}")
        print(f"  => claim (hybrid ≥ max(endpoints) in EVERY stratum): "
              f"{'PASS' if ok_all else 'FAIL'}")
        return ok_all

    _eval_and_print(tau_g, "[A] GLOBAL threshold (literal item-4 rule)")
    _eval_and_print(tau_s, "[B] RARITY-AWARE threshold (dev-frozen per stratum)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", default="deepseek")
    ap.add_argument("--run-dev", action="store_true", help="generate DEV-bank E7 curves")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    if args.run_dev:
        run_dev(args.endpoint, args.model, args.label)
    report(args.label)


if __name__ == "__main__":
    main()
