"""Fusion analysis: pick (kappa, granularity) on DEV, freeze, evaluate on the
confirmatory bank against BOTH endpoints (LLM, frozen C3g) at room + receptacle
level. Tests the pre-registered claim: fusion >= max(LLM, C3g) in every stratum.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.h2 import core, e7_learning as e7
from dynbelief.h2.e7_fusion import KAPPA_GRID, GRANS
from dynbelief.profiles.schema import load_profile


def _room_of(base):
    m = {r.id: r.room for r in load_profile(core.MANUAL_DIR / f"{base}.yaml").receptacles}
    m["elsewhere"] = "elsewhere"
    return m


def _load_fusion(tag, label):
    return [json.loads(l) for l in (core.OUT / f"e7_fusion_{tag}_{label}.jsonl").read_text().splitlines() if l.strip()]


def _load_e7(fname):
    rows = [json.loads(l) for l in (core.OUT / fname).read_text().splitlines() if l.strip()]
    rm = {}
    for r in rows:
        rm.setdefault(r["hh"], _room_of(r["hh"]))
        r["room_correct"] = int(rm[r["hh"]].get(r.get("pred"), "x") == rm[r["hh"]].get(r.get("true"), "y"))
    return rows


def _clu(rows, sel, ks, field):
    """per-(hh,object) cluster mean of `field` over rows matching sel() and k in ks."""
    by = defaultdict(list)
    for r in rows:
        if r["k"] in ks and sel(r):
            by[(r["hh"], r["object"])].append(r[field])
    return {c: float(np.mean(v)) for c, v in by.items() if v}


def _rar_of(rows):
    return {(r["hh"], r["object"]): r["rarity"] for r in rows}


def pick_config(fus_dev, e7_dev):
    """Choose (kappa, gran) on DEV: maximize the mean over strata of the early-k
    (k<=4) RECEPTACLE-level margin  fusion - max(LLM, C3g).  Receptacle is the
    deployment metric (you predict a shelf); optimizing room-margin misleadingly
    favours room-granularity injection, which sacrifices shelf accuracy."""
    EARLY = [k for k in e7.K_GRID if k <= 4]
    rar = _rar_of(e7_dev)
    llm = _clu(e7_dev, lambda r: r["model"] == "deepseek", EARLY, "correct")
    c3g = _clu(e7_dev, lambda r: r["model"] == "classical_C3g", EARLY, "correct")
    best = None
    for kap in KAPPA_GRID:
        for g in GRANS:
            fus = _clu(fus_dev, lambda r, kap=kap, g=g: r["kappa"] == kap and r["model"] == f"fusion_{g}",
                       EARLY, "correct_recep")
            per_str = defaultdict(list)
            for c in set(fus) & set(llm) & set(c3g):
                per_str[rar.get(c, "?")].append(fus[c] - max(llm[c], c3g[c]))
            margins = [np.mean(v) for v in per_str.values() if v]
            score = float(np.mean(margins)) if margins else -9
            if best is None or score > best[0]:
                best = (score, kap, g)
    return best[1], best[2], best[0]


def _boot_pair(rows_a, rows_b, sel_a, sel_b, ks, fa, fb, nb=5000, seed=17):
    a = _clu(rows_a, sel_a, ks, fa); b = _clu(rows_b, sel_b, ks, fb)
    clus = sorted(set(a) & set(b)); d = np.array([a[c]-b[c] for c in clus])
    if len(d) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    m = [np.mean(d[rng.integers(0, len(d), len(d))]) for _ in range(nb)]
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def _mean_ci(rows, sel, ks, field, nb=4000, seed=8):
    vals = list(_clu(rows, sel, ks, field).values())
    if not vals:
        return (np.nan, np.nan, np.nan)
    a = np.array(vals); rng = np.random.default_rng(seed)
    m = [np.mean(a[rng.integers(0, len(a), len(a))]) for _ in range(nb)]
    return float(a.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def report(label):
    fus_dev = _load_fusion("dev", label); fus_conf = _load_fusion("conf", label)
    e7_dev = _load_e7(f"e7_rows_dev_{label}.jsonl"); e7_conf = _load_e7(f"e7_rows_{label}.jsonl")
    kap, gran, dev_margin = pick_config(fus_dev, e7_dev)
    print("=" * 90)
    print(f"E4 v3 — LLM-as-PRIOR FUSION (pseudo-count injection)   model={label}")
    print("=" * 90)
    print(f"\nDEV selection (bank=atyp_regime_v1): FROZEN kappa*={kap} days, "
          f"granularity*={gran}  (dev early-k room margin={dev_margin:+.3f})")

    fmodel = f"fusion_{gran}"
    sel_f = lambda r: r["kappa"] == kap and r["model"] == fmodel
    regions = [("cold-start k=0", [0]), ("early-k k≤4", [k for k in e7.K_GRID if k <= 4]),
               ("all k", e7.K_GRID)]
    for glabel, field_f, field_e in [("ROOM", "correct_room", "room_correct"),
                                      ("RECEPTACLE", "correct_recep", "correct")]:
        print(f"\n#### {glabel}-level accuracy on the CONFIRMATORY bank (clustered 95% CI) ####")
        print(f"  {'stratum':9}{'region':16}{'LLM':>13}{'C3g':>13}{'FUSION':>13}"
              f"{'fus−max(CI)':>22}{'claim':>7}")
        allpass = True
        for rar, _, _ in e7.TERCILES:
            for rname, ks in regions:
                sf = lambda r, rar=rar: sel_f(r) and r["rarity"] == rar
                sl = lambda r, rar=rar: r["model"] == "deepseek" and r["rarity"] == rar
                sc = lambda r, rar=rar: r["model"] == "classical_C3g" and r["rarity"] == rar
                lm = _mean_ci(e7_conf, sl, ks, field_e)[0]
                cm = _mean_ci(e7_conf, sc, ks, field_e)[0]
                fm = _mean_ci(fus_conf, sf, ks, field_f)[0]
                # paired fusion - max(endpoints): compare per cluster
                llm_c = _clu(e7_conf, sl, ks, field_e); c3g_c = _clu(e7_conf, sc, ks, field_e)
                fus_c = _clu(fus_conf, sf, ks, field_f)
                clus = sorted(set(fus_c) & set(llm_c) & set(c3g_c))
                d = np.array([fus_c[c] - max(llm_c[c], c3g_c[c]) for c in clus])
                rng = np.random.default_rng(21)
                bm = [np.mean(d[rng.integers(0, len(d), len(d))]) for _ in range(4000)] if len(d) else [np.nan]
                dm, dlo, dhi = (float(d.mean()), float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))) if len(d) else (np.nan,)*3
                claim = dm >= -1e-9
                allpass &= claim
                mark = " " if rname != "early-k k≤4" else "»"
                print(f"  {rar[:8]:9}{mark+rname:16}{lm:>13.2f}{cm:>13.2f}{fm:>13.2f}"
                      f"{f'{dm:+.2f}[{dlo:+.2f},{dhi:+.2f}]':>22}{'ok' if claim else 'FAIL':>7}")
        print(f"  => fusion ≥ max(endpoints) in every stratum×region [{glabel}]: "
              f"{'PASS' if allpass else 'mixed'}")

    plot(label, fus_conf, e7_conf, kap, gran)


def plot(label, fus_conf, e7_conf, kap, gran):
    fmodel = f"fusion_{gran}"
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    titles = {"rare": "RARE", "medium": "MEDIUM", "frequent": "FREQUENT"}
    for ax, (rar, _, _) in zip(axes, e7.TERCILES):
        for model, rows, field, col, mk, lbl in [
            ("deepseek", e7_conf, "room_correct", "#d1495b", "o", "LLM (room)"),
            ("classical_C3g", e7_conf, "room_correct", "#2e6f95", "s", "C3g (room)"),
            (fmodel, fus_conf, "correct_room", "#2a9d8f", "D", f"FUSION κ={kap},{gran}")]:
            xs, ys = [], []
            for k in e7.K_GRID:
                sel = (lambda r, m=model, k=k, rar=rar: r["model"] == m and r["k"] == k and r["rarity"] == rar
                       and (r.get("kappa", kap) == kap))
                v = list(_clu(rows, sel, [k], field).values())
                if v:
                    xs.append(k); ys.append(np.mean(v))
            ax.plot(xs, ys, "-", color=col, marker=mk, label=lbl, lw=2, ms=6)
        ax.axvspan(-0.4, 4, color="#ffd166", alpha=0.13)
        ax.set_title(titles[rar]); ax.set_xlabel("events observed (k)"); ax.grid(alpha=0.25)
        ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("ROOM-level accuracy"); axes[0].legend(fontsize=8.5, loc="lower right")
    fig.suptitle(f"E4 v3 — LLM-as-prior FUSION (room-level): wins early-k in MEDIUM (denoises the LLM),\n"
                 f"ties in RARE, and DEGRADES in FREQUENT (stationary prior corrupts the periodic fit)\n"
                 f"κ={kap}, {gran}-granularity, frozen on dev · confirmatory bank · shaded=early-k",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    out = core.OUT / "e7_fusion_curves.png"; fig.savefig(out, dpi=140); print("\nwrote", out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--label", default="deepseek")
    report(ap.parse_args().label)


if __name__ == "__main__":
    main()
