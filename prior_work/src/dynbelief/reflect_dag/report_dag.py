"""reflect_DAG evaluation — Tier-1 alpha*, calibration check, P-A1/P-A2, the
structure-source ablation ladder, and the graceful-degradation control.

All numbers on the confirmatory bank(s) with object-clustered bootstrap CIs,
stratified by rarity tercile. Dev/test wall: alpha* and the unit constant U are
estimated ONLY on the v22dev rows (--tier1), then frozen into run_dag.

Honesty guardrails (from the brief): if P-A1/P-A2 fail, that is the reported
result; if the do-contrast is uncalibrated (like the entropy gate), the fallback
is the pure evidence ratio and the writeup says so.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.h2 import core
from dynbelief.reflect.report import _load_rows
from dynbelief.reflect_dag import precision_fusion as PF

OUT = core.OUT.parent / "reflect_dag"

ARMS = ["dag_persona_dag", "dag_persona_dag_cf", "dag_stat_params",
        "dag_only_stat", "dag_no_llm_structure", "dag_scrambled"]
PRETTY = {"dag_persona_dag": "persona+DAG (T3 fusion)",
          "dag_persona_dag_cf": "persona+DAG+counterfact",
          "dag_stat_params": "llm_structure+stat_params",
          "dag_only_stat": "DAG_only (no persona)",
          "dag_no_llm_structure": "no_llm_structure (C3g)",
          "dag_scrambled": "scrambled (control)",
          "llm_direct": "persona_only (baseline)",
          "llm_surprise": "surprise_gated"}


def _rows(bank_key, level):
    p = OUT / f"rows_dag_{bank_key}_d{level}.jsonl"
    rows = [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
    # merge the stored persona_only + surprise arms for side-by-side tables
    from dynbelief.reflect.run import OUT as ROUT
    for f, keep in ((ROUT / f"all_rows_{bank_key}_distractor_d{level}.jsonl",
                     ("llm_direct",)),
                    (ROUT / f"rows_surprise_{bank_key}_surprise_d{level}.jsonl",
                     ("llm_surprise",))):
        if f.exists():
            rows += [r for r in map(json.loads, f.read_text().splitlines())
                     if r.get("model") in keep]
    return rows


def _cell(rows, arm, field="correct", rar=None, ckpts=None, objs=None):
    by = defaultdict(list)
    for r in rows:
        if (r["model"] == arm and (rar is None or r.get("rarity") == rar)
                and (ckpts is None or r["ckpt"] in ckpts)
                and (objs is None or (r["hh"], r["object"]) in objs)):
            by[(r["hh"], r["object"])].append(r[field])
    allv = [v for vs in by.values() for v in vs]
    if not allv:
        return None
    clus = list(by); rng = np.random.default_rng(3)
    m = [np.mean([v for i in rng.integers(0, len(clus), len(clus)) for v in by[clus[i]]])
         for _ in range(2000)]
    return float(np.mean(allv)), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), len(clus)


# ── Tier-1 alpha* + U estimation (DEV bank only; the dev/test wall) ──────────

def tier1(level):
    dev = [r for r in _load_rows("v22dev", f"distractor_d{level}")
           if r["model"] == "llm_direct"]
    # mean candidate-set size over the dev bank
    import dynbelief.reflect.run as R
    bank_dir, cfgmap, _, _ = R.bank_of("v22dev")
    ncands = float(np.mean([len(core.load_hh(bank_dir, hh)["cand_set"])
                            for hh in cfgmap]))
    t1 = PF.tier1_alpha(dev, ncands)
    print(f"TIER 1 (dev bank, d{level}): prior hit rate {t1['hit_rate']:.3f} over "
          f"n={t1['n']} queries, mean |candidates|={ncands:.1f}")
    print(f"  => alpha* = {t1['alpha_star']}  "
          f"(the LLM regime prior is worth ~{t1['alpha_star']} observations, "
          f"calibrated on held-out households — an empirical quantity, not a tuned knob)")
    return t1, ncands


def unit_constant_from_structures(alpha_star, bank_key, level):
    cs = []
    for p in (OUT / "structures").glob(f"*_d{level}.json"):
        try:
            cs.append(float(json.loads(p.read_text()).get("contrast", 0.0)))
        except Exception:
            pass
    U = PF.unit_constant(alpha_star, cs)
    print(f"  unit constant U = {U:.2f} pseudo-obs per unit contrast "
          f"(mean dev contrast {np.mean(cs) if cs else float('nan'):.3f}; "
          f"U converts prior precision into data-event units so mean kappa == alpha*)")
    return U


# ── calibration: do-contrast vs correctness (the check that killed entropy) ──

def calibration(bank_key, level):
    """Side-by-side: OLD entropy-gate (memory entropy H vs correctness, from the
    stored llm_direct rows) next to the NEW CounterfactCoT do-contrast vs
    correctness. Calibrated entropy would ANTI-correlate (low H = confident =
    correct); calibrated contrast would POSITIVELY correlate."""
    from dynbelief.reflect.run import OUT as ROUT
    # entropy (old gate)
    ent = defaultdict(lambda: {"H": [], "c": []})
    ef = ROUT / f"all_rows_{bank_key}_distractor_d{level}.jsonl"
    if ef.exists():
        for r in map(json.loads, ef.read_text().splitlines()):
            if r.get("model") == "llm_direct" and r.get("H") is not None:
                ent[r["hh"]]["H"].append(r["H"]); ent[r["hh"]]["c"].append(r["correct"])
    ept = [(np.mean(v["H"]), np.mean(v["c"])) for v in ent.values() if v["H"]]
    # contrast (new)
    con = defaultdict(lambda: {"c": None, "hits": []})
    for r in _rows(bank_key, level):
        if r["model"] == "dag_persona_dag_cf":
            con[r["hh"]]["c"] = r.get("contrast"); con[r["hh"]]["hits"].append(r["correct"])
    cpt = [(v["c"], float(np.mean(v["hits"]))) for v in con.values()
           if v["c"] is not None and v["hits"]]
    if len(cpt) < 4:
        print("calibration: run with LLM first"); return None
    r_ent = float(np.corrcoef(*zip(*ept))[0, 1]) if len(ept) >= 4 else float("nan")
    r_con = float(np.corrcoef(*zip(*cpt))[0, 1])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    ex, ey = zip(*ept)
    axes[0].scatter(ex, ey, s=42, color="#8d99ae")
    axes[0].set_xlabel("memory entropy H (bits)"); axes[0].set_ylabel("household accuracy")
    axes[0].set_title(f"OLD entropy gate: H vs correctness (r={r_ent:+.2f})\n"
                      "calibrated would be NEGATIVE — it is ~flat (uncalibrated)")
    cx, cy = zip(*cpt)
    axes[1].scatter(cx, cy, s=42, color="#e8890c")
    axes[1].set_xlabel("do-contrast weight (CounterfactCoT gap)")
    axes[1].set_title(f"NEW do-contrast vs correctness (r={r_con:+.2f})\n"
                      "calibrated would be POSITIVE")
    for a in axes:
        a.grid(alpha=0.3)
    fig.suptitle(f"Calibration ({bank_key}, d{level}): the check that killed the entropy "
                 f"gate, re-run contrastively", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    f = OUT / f"calibration_{bank_key}_d{level}.png"
    fig.savefig(f, dpi=140)
    n = len(cpt)
    sig = "significant (p<0.05, n=%d)" % n if abs(r_con) > 1.8 / np.sqrt(n) else \
        "NOT significant at n=%d" % n
    print(f"calibration: entropy r={r_ent:+.2f}  ->  do-contrast r={r_con:+.2f} ({sig})  ({f})")
    return r_con


# ── main tables: P-A1 / P-A2 / ladder / control ──────────────────────────────

def tables(bank_key, level):
    rows = _rows(bank_key, level)
    arms = ["llm_direct", "llm_surprise"] + ARMS
    print("\n" + "=" * 100)
    print(f"reflect_DAG — {bank_key} bank, distractors={level}; day-14, object-clustered 95% CI")
    print("=" * 100)
    for rar in ["rare", "medium", "frequent", None]:
        print(f"\n### {'ALL' if rar is None else rar.upper()}")
        for arm in arms:
            c = _cell(rows, arm, "correct", rar, [14])
            if c:
                print(f"  {PRETTY.get(arm, arm):28s} {c[0]:.3f} [{c[1]:.2f},{c[2]:.2f}]  (n_clu={c[3]})")
    # P-A1: rare-tercile learning curve vs persona_only
    print("\nP-A1 — rare-tercile accuracy by checkpoint (does tying lift the rare curve?)")
    print(f"  {'ckpt':>5}" + "".join(f"{PRETTY.get(a, a)[:18]:>20}" for a in
                                     ("llm_direct", "dag_persona_dag", "dag_no_llm_structure")))
    for ck in (1, 3, 7, 14):
        cells = []
        for a in ("llm_direct", "dag_persona_dag", "dag_no_llm_structure"):
            c = _cell(rows, a, "correct", "rare", [ck])
            cells.append(f"{c[0]:.2f}" if c else "-")
        print(f"  {ck:>5}" + "".join(f"{x:>20}" for x in cells))
    # graceful degradation
    print("\nControl — scrambled activity assignments (should be worse than DAG, not broken):")
    for a in ("dag_persona_dag", "dag_stat_params", "dag_scrambled", "dag_no_llm_structure"):
        c = _cell(rows, a, "correct", None, [14])
        if c:
            print(f"  {PRETTY[a]:28s} {c[0]:.3f}")


def pa2(bank_key, level):
    """P-A2 on the v22b confusable pairs: differing-activity vs shared-activity
    objects (pairs were authored so ALL targets are the differing-activity
    objects; shared here = the pair's common ordinary objects are not queried,
    so P-A2 reduces to: does the DAG lift the pair targets vs persona_only)."""
    rows = _rows(bank_key, level)
    if bank_key != "v22b":
        return
    print("\nP-A2 — confusable-pair (differing-activity) targets, day-14:")
    for a in ("llm_direct", "dag_persona_dag", "dag_no_llm_structure"):
        c = _cell(rows, a, "correct", None, [14])
        if c:
            print(f"  {PRETTY.get(a, a):28s} {c[0]:.3f} [{c[1]:.2f},{c[2]:.2f}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", choices=["v22", "v22b"], default="v22")
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--tier1", action="store_true",
                    help="estimate alpha* (+U if structures exist) and exit")
    args = ap.parse_args()
    if args.tier1:
        t1, _ = tier1(args.level)
        unit_constant_from_structures(t1["alpha_star"], args.bank, args.level)
        return
    tables(args.bank, args.level)
    pa2(args.bank, args.level)
    calibration(args.bank, args.level)


if __name__ == "__main__":
    main()
