"""E2 pre-registered endpoints (computed FIRST; exploratory kept separate).

  1. Day-0 delta (Pllm - P0), typ bank      — the help
  2. Day-0 delta (Pllm - P0), atyp bank     — the harm
  3. Crossover day: first D where P0 >= Pllm, per (household, kappa), plotted
     against atypicality_distance
  4. NOT-MOVED accuracy at low D vs the C0/P0 reference — where a misaligned
     prior does its damage (moved episodes are ceiling-limited)
  5. Porc sanity: Porc - P0 >= 0 across the grid (machinery check)

Primary family = C3; headline uses moved_enriched for curves and its natural
counterpart for the not-moved harm slice. All deltas bootstrap-CI'd, paired
per episode where possible.
"""
from __future__ import annotations

import json
import pathlib

import pandas as pd

from dynbelief.experiments.stats import boot_ci, fmt_ci, paired_delta_ci

D_GRID = [0, 1, 2, 3, 5, 7, 10, 14, 21, 28]


def _key(r):
    return (r["bank"], r["household"], r["history_days"], r["stream"], r["query_id"])


def _paired(df, arm_prior, ref_prior, D, bank, kappa, metric="correct", stream=None):
    a = df[(df["prior"] == arm_prior) & (df["history_days"] == D) & (df["bank"] == bank)
           & ((df["kappa"] == kappa) if arm_prior != "P0" else True)]
    r = df[(df["prior"] == ref_prior) & (df["history_days"] == D) & (df["bank"] == bank)]
    if stream:
        a = a[a["stream"] == stream]; r = r[r["stream"] == stream]
    av = {_key(x): x[metric] for _, x in a.iterrows()}
    rv = {_key(x): x[metric] for _, x in r.iterrows()}
    return paired_delta_ci(av, rv)


def write_endpoints(out_dir: pathlib.Path, banks_root: pathlib.Path) -> None:
    df = pd.read_parquet(out_dir / "rows.parquet")
    df = df[df["family"] == "C3"]                      # primary family
    dist = _distances(banks_root)
    L = ["# E2 — one-shot prior help vs harm (pre-registered endpoints, family C3)",
         "", "Prior injected as pseudo-observations at equivalent-sample-size "
         "kappa in {weak:1d, moderate:7d, strong:28d}. P0 = uninformative "
         "(no pseudo-obs). Elicited from gpt-5.4-mini + gpt-5.5 (never Claude). "
         "Deltas are paired per-episode, moved_enriched unless noted, 95% CI.", ""]

    # Endpoint 1 & 2 — Day-0 delta (Pllm - P0)
    L += ["## E1&2: Day-0 delta (Pllm - P0) — help (typ) vs harm (atyp)", "",
          "| kappa | typ_v1 Δacc [CI] | atyp_v2 Δacc [CI] |", "|---|---|---|"]
    for kappa in ("weak", "moderate", "strong"):
        cells = []
        for bank in ("typ_v1", "atyp_v2"):
            m, ci, n = _paired(df, "Pllm", "P0", 0, bank, kappa)
            cells.append(fmt_ci(m, ci))
        L.append(f"| {kappa} | {cells[0]} | {cells[1]} |")
    L += ["", "(At D=0 P0 is the uniform prior; Pllm is the elicited prior with no "
          "household data. Help = Pllm>>P0 on typ; harm shows as a smaller/near-zero "
          "or negative advantage on atyp, and sharpens at low nonzero D below.)", ""]

    # Endpoint 4 — NOT-MOVED accuracy at low D (the harm mechanism)
    L += ["## E4: NOT-MOVED accuracy at low D (natural stream) — the harm slice", "",
          "A misaligned strong prior predicts phantom movement on easy (not-moved) "
          "episodes. Table: not-moved accuracy, strong kappa.", "",
          "| bank | prior | D1 | D2 | D3 | D5 |", "|---|---|---|---|---|---|"]
    nat = df[(df["stream"] == "natural") & (df["moved_since_obs"] == 0)]
    for bank in ("typ_v1", "atyp_v2"):
        for prior, kappa in (("P0", None), ("Pllm", "strong"), ("Porc", "strong")):
            cells = []
            for D in (1, 2, 3, 5):
                s = nat[(nat["bank"] == bank) & (nat["history_days"] == D)
                        & (nat["prior"] == prior)
                        & ((nat["kappa"] == kappa) if kappa else True)]
                cells.append(f"{s['correct'].mean():.3f}" if len(s) else "-")
            L.append(f"| {bank} | {prior}{'/'+kappa if kappa else ''} | " + " | ".join(cells) + " |")
    L += ["", "Harm = Pllm below P0 on atyp not-moved episodes (the prior overrides "
          "a correct 'still there'); on typ the aligned prior should not hurt.", ""]

    # Endpoint 3 — crossover day vs atypicality_distance
    L += ["## E3: crossover day (first D where P0 >= Pllm) vs atypicality_distance", "",
          "| household | dist | kappa | crossover D |", "|---|---|---|---|"]
    me = df[df["stream"] == "moved_enriched"]
    for bank in ("typ_v1", "atyp_v2"):
        for hh in sorted(me[me["bank"] == bank]["household"].unique()):
            for kappa in ("weak", "moderate", "strong"):
                cd = _crossover(me, bank, hh, kappa)
                L.append(f"| {hh[:36]} | {dist.get(hh, 0.0):.3f} | {kappa} | {cd} |")
    L += ["", "Hypothesis: crossover D increases with kappa and with distance "
          "(a stronger, more-wrong prior takes longer for data to overcome).", ""]

    # Endpoint 5 — Porc sanity
    L += ["## E5: Porc - P0 machinery check (must be >= 0 across the grid)", "",
          "| bank | kappa | mean Δacc (pooled D) [CI] | min cell Δacc |", "|---|---|---|---|"]
    ok = True
    for bank in ("typ_v1", "atyp_v2"):
        for kappa in ("weak", "moderate", "strong"):
            deltas = []
            for D in D_GRID:
                m, ci, n = _paired(me, "Porc", "P0", D, bank, kappa)
                if m == m:
                    deltas.append(m)
            pooled_m, pooled_ci = boot_ci(deltas) if deltas else (float("nan"), (0, 0))
            mn = min(deltas) if deltas else float("nan")
            ok = ok and (mn >= -0.05)
            L.append(f"| {bank} | {kappa} | {fmt_ci(pooled_m, pooled_ci)} | {mn:.3f} |")
    L += ["", f"**Machinery check: {'PASS' if ok else 'FAIL'}** — Porc "
          f"{'helps (>=0) everywhere; injection works, so Pllm harm is prior content'if ok else 'does NOT help everywhere; injection machinery suspect, Pllm results void'}.",
          "", "Exploratory analyses (kappa x distance surfaces, per-class harm) "
          "are in rows.parquet, kept separate from these pre-registered endpoints."]
    (out_dir / "summary.md").write_text("\n".join(L))
    print(f"[e2] endpoints -> {out_dir/'summary.md'}")


def _crossover(me, bank, hh, kappa):
    """First D>=1 where P0 accuracy >= Pllm accuracy (moved_enriched)."""
    for D in [d for d in D_GRID if d >= 1]:
        p0 = me[(me["bank"] == bank) & (me["household"] == hh) & (me["history_days"] == D)
                & (me["prior"] == "P0")]["correct"].mean()
        pl = me[(me["bank"] == bank) & (me["household"] == hh) & (me["history_days"] == D)
                & (me["prior"] == "Pllm") & (me["kappa"] == kappa)]["correct"].mean()
        if p0 == p0 and pl == pl and p0 >= pl:
            return D
    return ">28"


def _distances(banks_root):
    out = {}
    for bank in ("typ_v1", "atyp_v2"):
        m = banks_root / bank / "manifest.json"
        if m.exists():
            man = json.loads(m.read_text())
            out.update(man.get("atypicality_distances", {}))
            for h in man.get("households", []):
                out.setdefault(h["household"], 0.0)
    return out
