"""results/classical/summary.md — C0-C5 (+ mini) with bootstrap CIs, paired
per-episode deltas, and the R4 diagnostics. Streams are NEVER pooled (R3):
every learning-curve/moved table runs on `moved_enriched`; `natural` gives the
deployment-distribution reweight; `held_out` is the C4-attribution slice.

log-loss clip [0.01, 0.99] applied uniformly (LLM rows re-scored from p_true).
"""
from __future__ import annotations

import json
import math
import pathlib
from collections import defaultdict

import pandas as pd

from dynbelief.experiments.stats import boot_ci, fmt_ci, monotone_trend, paired_delta_ci

CLIP = (0.01, 0.99)
D_SHOW = [0, 1, 2, 3, 5, 7, 10, 14, 21, 28]
ARM_ORDER = ["C0_lastobs", "C1_constant", "C2_spectral", "C2_spectral_peredge",
             "C3_glm", "C4_regime", "C5_marginal", "C5plus_particle",
             "LLM_gpt-5.4-mini"]


def _ll(p):
    return -math.log(min(CLIP[1], max(CLIP[0], p)))


def _load_llm(repo):
    f = repo / "results" / "e1" / "rows_classical_grid_gpt-5.4-mini.jsonl"
    if not f.exists():
        return pd.DataFrame()
    df = pd.DataFrame(json.loads(l) for l in f.open())
    df["model"] = "LLM_gpt-5.4-mini"
    df["logloss"] = df["p_true"].map(_ll)
    if "estimator_used" not in df:
        df["estimator_used"] = "llm"
    if "top3_correct" not in df:
        df["top3_correct"] = float("nan")
    return df


def _key(r):
    return (r["bank"], r["household"], r["history_days"], r["stream"], r["query_id"])


def write_summary(out_dir: pathlib.Path, repo: pathlib.Path) -> None:
    dfc = pd.read_parquet(out_dir / "rows.parquet")
    dfc["logloss"] = dfc["p_true"].map(_ll)
    dfl = _load_llm(repo)
    df = pd.concat([dfc, dfl], ignore_index=True) if len(dfl) else dfc
    arms = [a for a in ARM_ORDER if a in set(df["model"])]
    L = ["# Classical arms vs LLM — E1 (streams, extended D grid, bootstrap CIs)",
         "",
         f"{len(dfc)} classical + {len(dfl)} LLM rows. Streams NOT pooled (R3). "
         f"Curves/moved on `moved_enriched` (~50% moved by construction); "
         f"`natural` for deployment reweight; `held_out` for attribution. "
         f"n/cell target 100 (classical). log-loss clip [0.01,0.99]. CIs = 2000x "
         f"percentile bootstrap.", ""]

    # ── learning curves on moved_enriched, per bank, with CIs ────────────────
    me = df[df["stream"] == "moved_enriched"]
    for bank in ("typ_v1", "atyp_v2"):
        sub = me[me["bank"] == bank]
        if not len(sub):
            continue
        for metric, label in (("correct", "top-1 accuracy"), ("top3_correct", "top-3 accuracy")):
            L += [f"## {bank} — {label} vs D (moved_enriched, mean [95% CI])", "",
                  "| arm | " + " | ".join(f"D{d}" for d in D_SHOW) + " |",
                  "|---|" + "---|" * len(D_SHOW)]
            for a in arms:
                cells = []
                for d in D_SHOW:
                    s = sub[(sub["model"] == a) & (sub["history_days"] == d)]
                    vals = s[metric].dropna()
                    cells.append(fmt_ci(*boot_ci(vals)) if len(vals) else "-")
                L.append(f"| {a} | " + " | ".join(cells) + " |")
            L.append("")

    # ── paired per-episode delta (arm - C0) on moved_enriched, pooled D>=1 ────
    L += ["## Paired delta vs C0 (arm - C0, same episodes; moved_enriched, "
          "pooled D>=1)", "", "| arm | Δacc [95% CI] | Δbrier [95% CI] | n pairs |",
          "|---|---|---|---|"]
    ref = {_key(r): r for _, r in me[(me["model"] == "C0_lastobs")
                                     & (me["history_days"] >= 1)].iterrows()}
    for a in arms:
        if a == "C0_lastobs":
            continue
        armrows = {_key(r): r for _, r in me[(me["model"] == a)
                                             & (me["history_days"] >= 1)].iterrows()}
        av = {k: v["correct"] for k, v in armrows.items()}
        rv = {k: v["correct"] for k, v in ref.items()}
        bd_a = {k: v["brier"] for k, v in armrows.items()}
        bd_r = {k: v["brier"] for k, v in ref.items()}
        m, ci, n = paired_delta_ci(av, rv)
        bm, bci, _ = paired_delta_ci(bd_a, bd_r)
        L.append(f"| {a} | {fmt_ci(m, ci)} | {fmt_ci(bm, bci)} | {n} |")
    L.append("")

    # ── moved vs not-moved with C5 callout + natural-reweighted calibration ───
    L += ["## Moved vs not-moved (moved_enriched, pooled D>=1)", "",
          "| arm | not-moved acc | MOVED acc | MOVED top-3 | MOVED Brier | Brier rewt->natural |",
          "|---|---|---|---|---|---|"]
    natrate = _natural_moved_rate(df)
    pooled = me[me["history_days"] >= 1]
    for a in arms:
        s = pooled[pooled["model"] == a]
        nm = s[s["moved_since_obs"] == 0]; mv = s[s["moved_since_obs"] == 1]
        bnm = nm["brier"].mean() if len(nm) else float("nan")
        bmv = mv["brier"].mean() if len(mv) else float("nan")
        rew = natrate * bmv + (1 - natrate) * bnm
        L.append(f"| {a} | {_m(nm,'correct')} | {_m(mv,'correct')} | "
                 f"{_m(mv,'top3_correct')} | {_m(mv,'brier')} | {rew:.3f} |")
    c5mv = pooled[(pooled["model"] == "C5plus_particle") & (pooled["moved_since_obs"] == 1)]
    if len(c5mv):
        mc, cc = boot_ci(c5mv["correct"])
        L += ["", f"**C5+ (particle oracle, true ceiling) MOVED accuracy = {fmt_ci(mc, cc)}** "
              f"(n={len(c5mv)}). The gap arm->C5 is model failure; C5->1.0 is "
              f"irreducible generator stochasticity. Calibration reweighted to the "
              f"natural moved-rate w={natrate:.2f} (moved_enriched's 0.5 base rate "
              f"would misstate deployment)."]

    # ── held-out attribution (held_out stream) ───────────────────────────────
    ho = df[(df["stream"] == "held_out") & (df["history_days"] >= 1)]
    L += ["", "## Held-out objects (held_out stream, pooled D>=1) — C4 attribution",
          "", "| arm | acc [95% CI] |", "|---|---|"]
    for a in arms:
        s = ho[ho["model"] == a]
        L.append(f"| {a} | {fmt_ci(*boot_ci(s['correct'])) if len(s) else '-'} |")

    # ── per transformation family (atyp, moved_enriched) ─────────────────────
    fam = {"t1_night": "T1 night", "t2_three": "T2 3x12", "t2_weekend": "T2 weekend"}
    at = me[(me["bank"] == "atyp_v2") & (me["history_days"] >= 1)]
    L += ["", "## atyp_v2 per transformation family (moved_enriched acc, pooled D>=1)",
          "", "| arm | " + " | ".join(fam.values()) + " |", "|---|" + "---|" * len(fam)]
    for a in arms:
        cells = [_m(at[(at["model"] == a) & (at["household"].str.contains(k))], "correct")
                 for k in fam]
        L.append(f"| {a} | " + " | ".join(cells) + " |")

    # ── R4 diagnostics ───────────────────────────────────────────────────────
    L += ["", "## R4 diagnostics", ""]
    # C0/C5 flatness across D (should be ~flat by construction)
    L.append("**Flatness (C0, C5 must be D-invariant; |trend|~1 = flag):**")
    for a in ("C0_lastobs", "C5_marginal", "C5plus_particle"):
        s = me[(me["model"] == a) & (me["history_days"] >= 1)]   # D>=1: D0 is uniform for all
        if not len(s):
            continue
        by_d = s.groupby("history_days")["correct"].mean()
        tr = monotone_trend(list(by_d.index), list(by_d.values))
        flag = " ⚠️ MONOTONE" if abs(tr) > 0.8 else " ok"
        L.append(f"- {a}: trend={tr:+.2f}{flag}")
    # fallback audit: cells (bank,D,arm on observed streams) with >20% fallback
    L.append("")
    L.append("**Fallback audit (>20% fallback rows in a cell, natural+moved_enriched):**")
    obs_streams = dfc[dfc["stream"] != "held_out"]
    flagged = []
    for (bank, d, model), g in obs_streams.groupby(["bank", "history_days", "model"]):
        frac = g["estimator_used"].astype(str).str.startswith("fallback").mean()
        if frac > 0.20:
            flagged.append((bank, d, model, round(frac, 2)))
    if flagged:
        for (b, d, mdl, fr) in sorted(flagged):
            L.append(f"- {b} D={d} {mdl}: {fr:.0%} fallback (cell annotated)")
    else:
        L.append("- none (>20%): the low-D fixed-penalty fix removed the prior "
                 "C3 fallback storm; held_out fallbacks are by construction and "
                 "reported in their own stream.")

    # ── W5 per-edge cost ─────────────────────────────────────────────────────
    L += ["", "## W5 per-edge renormalization cost (C2, moved_enriched pooled D>=1)",
          "", "| mode | acc | Brier |", "|---|---|---|"]
    for a, lab in (("C2_spectral", "categorical"), ("C2_spectral_peredge", "per_edge")):
        s = pooled[pooled["model"] == a]
        if len(s):
            L.append(f"| {lab} | {_m(s,'correct')} | {_m(s,'brier')} |")

    L += ["", "Streams reported separately (never pooled). See fits.jsonl for "
          "per-cell hyperparameters/timings/low_d_fixed flags and "
          "regime_schedule_t1.md for the W4 check."]
    (out_dir / "summary.md").write_text("\n".join(L))
    print(f"[classical] summary -> {out_dir/'summary.md'}")


def _m(s, col):
    return f"{s[col].mean():.3f}" if len(s) else "-"


def _natural_moved_rate(df) -> float:
    nat = df[(df["stream"] == "natural") & (df["history_days"] >= 1)]
    return float(nat["moved_since_obs"].mean()) if len(nat) else 0.2
