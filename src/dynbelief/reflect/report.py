"""Reflective-memory offline phase: classical arms, entropy-gated fusion, the
kappa_max dev sweep, evaluation tables, and figures. No LLM calls — consumes the
stored rows (with per-query prediction lists + memory entropy) from run.py.

Arms compared (all see the IDENTICAL event stream up to checkpoint D):
  classical_C3g / classical_C1 — statistical updating only (fit on the full stream).
  llm_direct  — semantic only: answers from the curated memory.
  llm_nomem   — semantic only, uncurated: answers from the raw digest.
  fusion      — statistical AND semantic: the memory-conditioned per-query LLM
                belief becomes kappa_eff days of pseudo-observations for the target
                (kappa_eff = round(kappa_max * (1 - H/H_max)), H = memory entropy),
                prepended to the target's real events; a mini-C3g refit of that
                target edge overrides the base model's occupancy for it (rates and
                every other object stay fit on real data only).
  fusion_flat — ablation: same but kappa_eff = kappa_max regardless of entropy;
                isolates what the entropy gate contributes.

kappa_max is swept on the DEV bank, frozen, then applied to the confirmatory bank.
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
from dynbelief.h2.confirm import CFG as CONF_CFG, BANK as CONF_BANK
from dynbelief.h2.e7_fusion import _pseudo_from_llm
from dynbelief.h2.e7_hybrid import DEV_BANK, DEV_CFG
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.classical.filter import uniform_belief
from dynbelief.reflect import memory as M
from dynbelief.reflect.run import OUT, CKPTS, room_of

KAPPA_MAX_GRID = [1, 2, 3, 5, 8]
ARANK = ["llm_direct", "llm_nomem", "fusion", "fusion_flat",
         "classical_C3g", "classical_C1"]
COLORS = {"llm_direct": "#d1495b", "llm_nomem": "#e58c8a", "fusion": "#2a9d8f",
          "fusion_flat": "#94d2bd", "classical_C3g": "#2e6f95", "classical_C1": "#8d99ae"}


def _load_rows(bank_name, label):
    p = OUT / f"rows_{bank_name}_{label}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def _stream_rows(h, t_hi):
    rows = [{"day": t // 1440, "t_min": t, "parents": {o: r}}
            for o, evs in h["by_obj"].items() for (t, r) in evs if t < t_hi]
    rows.sort(key=lambda r: r["t_min"])
    return rows


class _FusedRM:
    """Base C3g fit on real data, with the TARGET object's occupancy overridden by
    a mini refit on (pseudo-prior + its real events). Rates stay real-data."""
    def __init__(self, base, mini, obj):
        self.base, self.mini, self.obj = base, mini, obj
        self.candidates = base.candidates

    def occupancy(self, o, r, t):
        return (self.mini if o == self.obj else self.base).occupancy(o, r, t)

    def rate(self, o, r, t):
        return self.base.rate(o, r, t)


class _Ctx:
    """Per-(bank) cache of household data, streams, base fits, and last-obs."""
    def __init__(self, bank, cfgmap):
        self.bank, self.cfgmap = bank, cfgmap
        self.h = {hh: core.load_hh(bank, hh) for hh in cfgmap}
        self.rooms = {hh: room_of(hh) for hh in cfgmap}
        self._base = {}

    def base_arm(self, hh, ckpt, arm="C3g"):
        key = (hh, ckpt, arm)
        if key not in self._base:
            obs = _stream_rows(self.h[hh], ckpt * 1440)
            self._base[key] = make_arm(arm, self.h[hh]["cand_set"], obs)[0] if obs else None
        return self._base[key]

    def last_obs(self, hh, obj, tq, ckpt):
        ev = [(t, r) for (t, r) in self.h[hh]["by_obj"].get(obj, [])
              if t < min(tq, ckpt * 1440)]
        return (ev[-1][1], ev[-1][0]) if ev else (None, None)


def _predict(rm, cand_set, obj, tq, last):
    if rm is None:
        bel = uniform_belief(cand_set)
    else:
        ep = {"object": obj, "t_query": tq, "last_obs": last[0], "last_obs_t": last[1]}
        bel = _belief(rm, cand_set, obj, tq, ep, "categorical")
    return _rows_fields(bel, cand_set, None)[0]


def classical_rows(ctx, test_rows):
    """C3g + C1 predictions for every (hh, object, ckpt, test_day) in the LLM rows."""
    keys = sorted({(r["hh"], r["object"], r["ckpt"], r["test_day"], r["t_query"],
                    r["true"], r["rarity"]) for r in test_rows})
    out = []
    for (hh, obj, ckpt, qd, tq, true, rar) in keys:
        cand_set = ctx.h[hh]["cand_set"]; last = ctx.last_obs(hh, obj, tq, ckpt)
        for arm in ("C3g", "C1"):
            pred = _predict(ctx.base_arm(hh, ckpt, arm), cand_set, obj, tq, last)
            out.append({"model": f"classical_{arm}", "hh": hh, "object": obj,
                        "ckpt": ckpt, "test_day": qd, "true": true, "rarity": rar,
                        "pred": pred, "correct": int(pred == true),
                        "room_correct": int(ctx.rooms[hh].get(pred, "x") ==
                                            ctx.rooms[hh].get(true, "y"))})
    return out


def _dist_from_preds(preds, cand_set):
    d = {c: 0.0 for c in cand_set}
    for p in preds or []:
        r = p.get("receptacle")
        if r in d:
            d[r] += max(0.0, float(p.get("p", 0.0)))
    z = sum(d.values())
    return {c: v / z for c, v in d.items()} if z > 0 else \
        {c: 1.0 / len(cand_set) for c in cand_set}


def fusion_rows(ctx, direct_rows, kappa_max, gated=True, tag="fusion"):
    """Entropy-gated prior injection per query, mini-refit of the target edge."""
    out = []
    for r in direct_rows:
        hh, obj, ckpt, tq = r["hh"], r["object"], r["ckpt"], r["t_query"]
        h = ctx.h[hh]; cand_set = h["cand_set"]; cands = h["cands"]
        w = M.prior_weight(r["H"]) if gated else 1.0
        keff = int(round(kappa_max * w))
        base = ctx.base_arm(hh, ckpt, "C3g")
        last = ctx.last_obs(hh, obj, tq, ckpt)
        if keff <= 0 or base is None:
            rm = base                                # unsure memory -> pure classical
        else:
            dist = _dist_from_preds(r.get("preds"), cand_set)
            pseudo = _pseudo_from_llm(dist, ctx.rooms[hh], cands, obj, keff,
                                      "recep", seed=100 + ckpt)
            treal = [{"day": t // 1440, "t_min": t, "parents": {obj: rec}}
                     for (t, rec) in h["by_obj"].get(obj, []) if t < ckpt * 1440]
            mini = make_arm("C3g", cand_set, pseudo + treal)[0]
            rm = _FusedRM(base, mini, obj)
        pred = _predict(rm, cand_set, obj, tq, last)
        out.append({"model": tag, "hh": hh, "object": obj, "ckpt": ckpt,
                    "test_day": r["test_day"], "true": r["true"], "rarity": r["rarity"],
                    "H": r["H"], "kappa_eff": keff, "pred": pred,
                    "correct": int(pred == r["true"]),
                    "room_correct": int(ctx.rooms[hh].get(pred, "x") ==
                                        ctx.rooms[hh].get(r["true"], "y"))})
    return out


def sweep_kappa(label):
    """DEV: pick kappa_max maximizing pooled receptacle accuracy of gated fusion."""
    ctx = _Ctx(DEV_BANK, DEV_CFG)
    direct = [r for r in _load_rows("dev", label) if r["model"] == "llm_direct"]
    print(f"kappa_max sweep on DEV ({len(direct)} queries):")
    best = None
    for km in KAPPA_MAX_GRID:
        acc = float(np.mean([r["correct"] for r in fusion_rows(ctx, direct, km)]))
        print(f"  kappa_max={km}:  fusion acc={acc:.3f}")
        if best is None or acc > best[1]:
            best = (km, acc)
    print(f"  => FROZEN kappa_max* = {best[0]}")
    return best[0]


def _boot(by_clu, nb=3000, seed=23):
    clus = list(by_clu)
    if not clus:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    m = [np.mean([v for i in rng.integers(0, len(clus), len(clus))
                  for v in by_clu[clus[i]]]) for _ in range(nb)]
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def _cell(rows, model, ckpts, rar, field):
    by = defaultdict(list)
    for r in rows:
        if r["model"] == model and r["ckpt"] in ckpts and (rar is None or r["rarity"] == rar):
            by[(r["hh"], r["object"])].append(r[field])
    allv = [v for vs in by.values() for v in vs]
    if not allv:
        return None
    lo, hi = _boot(by)
    return float(np.mean(allv)), lo, hi


def evaluate(label, kappa_max):
    ctx = _Ctx(CONF_BANK, CONF_CFG)
    llm = _load_rows("conf", label)
    direct = [r for r in llm if r["model"] == "llm_direct"]
    rows = (llm + classical_rows(ctx, direct)
            + fusion_rows(ctx, direct, kappa_max, gated=True, tag="fusion")
            + fusion_rows(ctx, direct, kappa_max, gated=False, tag="fusion_flat"))
    (OUT / f"all_rows_conf_{label}.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))
    for field, gl in (("correct", "RECEPTACLE"), ("room_correct", "ROOM")):
        print(f"\n#### {gl}-level accuracy vs days of experience "
              f"(confirmatory, clustered 95% CI) ####")
        for rar in ["rare", "medium", "frequent", None]:
            print(f"\n  ### {'ALL' if rar is None else rar.upper()}")
            print("  " + f"{'days':>5}" + "".join(f"{m[:13]:>16}" for m in ARANK))
            for ck in CKPTS:
                cells = []
                for m in ARANK:
                    c = _cell(rows, m, [ck], rar, field)
                    cells.append(f"{c[0]:.2f}[{c[1]:.2f},{c[2]:.2f}]".rjust(16)
                                 if c else f"{'-':>16}")
                print("  " + f"{ck:>5}" + "".join(cells))
    return rows


def figures(label, rows):
    # accuracy vs days per stratum (room level)
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.7), sharey=True)
    for ax, (rar, _, _) in zip(axes, e7.TERCILES):
        for m in ARANK:
            xs, ys = [], []
            for ck in CKPTS:
                c = _cell(rows, m, [ck], rar, "room_correct")
                if c:
                    xs.append(ck); ys.append(c[0])
            ls = "--" if m.startswith("classical") or m == "fusion_flat" else "-"
            ax.plot(xs, ys, ls, color=COLORS[m], marker="o", ms=4, lw=1.8, label=m)
        n = len({(r['hh'], r['object']) for r in rows if r['rarity'] == rar})
        ax.set_title(f"{rar.upper()} (n={n} objs)"); ax.grid(alpha=0.25)
        ax.set_xlabel("days of experience"); ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("ROOM-level accuracy (fixed future test week)")
    axes[0].legend(fontsize=7.5, loc="lower right")
    fig.suptitle("Reflective memory — all arms see the SAME event stream; "
                 "updates are statistical (classical), semantic (LLM), or both (fusion)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT / "reflect_curves.png", dpi=140)
    # entropy trajectories
    fig2, ax = plt.subplots(figsize=(8, 4.2))
    for hh in CONF_CFG:
        p = OUT / "memory" / CONF_BANK / f"{hh}__{label}" / "meta.jsonl"
        if not p.exists():
            continue
        meta = [json.loads(l) for l in p.read_text().splitlines()]
        ax.plot([m["day"] for m in meta], [m["H"] for m in meta], "-o", ms=3,
                label=hh.replace("regime_", "").replace("_v1", ""))
    ax.axhline(M.H_MAX, color="#999", ls=":", lw=1)
    ax.text(0.1, M.H_MAX + 0.02, "uniform (no idea)", fontsize=8, color="#777")
    ax.set_xlabel("day"); ax.set_ylabel("hypothesis entropy H (bits)")
    ax.set_title("Memory uncertainty over time — entropy of the top-3 persona hypotheses")
    ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig2.tight_layout()
    fig2.savefig(OUT / "reflect_entropy.png", dpi=140)
    print("wrote", OUT / "reflect_curves.png", "and", OUT / "reflect_entropy.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="deepseek")
    ap.add_argument("--kappa-max", type=int, default=None,
                    help="skip the dev sweep and use this frozen value")
    ap.add_argument("--sweep-only", action="store_true")
    args = ap.parse_args()
    km = args.kappa_max if args.kappa_max is not None else sweep_kappa(args.label)
    if args.sweep_only:
        return
    rows = evaluate(args.label, km)
    figures(args.label, rows)


if __name__ == "__main__":
    main()
