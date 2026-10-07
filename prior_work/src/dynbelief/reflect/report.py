"""Reflective-memory offline phase: classical arms, pure evidence-ratio fusion, the
alpha_max dev sweep, evaluation tables, and figures. No LLM calls — consumes the
stored rows (with per-query prediction lists + memory entropy) from run.py.

Arms compared (all see the IDENTICAL event stream up to checkpoint D):
  classical_C3g / classical_C1 — statistical updating only (fit on the full stream).
  llm_direct  — semantic only: answers from the curated memory.
  llm_nomem   — semantic only, uncurated: answers from the raw digest.
  fusion      — statistical AND semantic, PURE EVIDENCE-RATIO. The memory-conditioned
                per-query LLM belief becomes a CONSTANT alpha pseudo-COUNTS on the
                target edge, fit together with the edge's real events — so the prior's
                influence is automatically ~alpha/(alpha+n) against the classical
                confidence n (the edge's real event count): decisive on unseen edges,
                vanishing on data-rich ones. A mini-C3g refit of that edge overrides
                the base model's occupancy for it; rates and every other object stay
                fit on real data only. NO entropy term (the entropy diagnostic showed
                LLM hypothesis entropy does not predict accuracy in any model), NO gate.

alpha is swept on the DEV bank (held-out accuracy), frozen, then applied to conf.
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
from dynbelief.h2.e7_hybrid import DEV_BANK, DEV_CFG
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.classical.filter import uniform_belief
from dynbelief.reflect import memory as M
from dynbelief.reflect.run import OUT, CKPTS, room_of

ALPHA_GRID = [1, 2, 3, 5, 8]         # pseudo-count budget alpha (dev-swept, frozen)
ARANK = ["llm_direct", "llm_nomem", "fusion", "classical_C3g", "classical_C1"]
COLORS = {"llm_direct": "#d1495b", "llm_nomem": "#e58c8a", "fusion": "#2a9d8f",
          "classical_C3g": "#2e6f95", "classical_C1": "#8d99ae"}


def _bank_pair(bank_key):
    """(conf_key, conf_bank, conf_cfg, dev_key, dev_bank, dev_cfg) for --bank.
    'conf' = the original regime_v1 pairing; 'v22' = the version22 banks."""
    if bank_key == "conf":
        return ("conf", CONF_BANK, CONF_CFG, "dev", DEV_BANK, DEV_CFG)
    if bank_key == "v22":
        from dynbelief.reflect.v22 import (V22_BANK, V22_DEV_BANK, V22_CFG,
                                           V22_DEV_CFG)
        return ("v22", V22_BANK, V22_CFG, "v22dev", V22_DEV_BANK, V22_DEV_CFG)
    if bank_key == "v22b":
        # the expansion pairs reuse the version22_dev alpha wall (same reflect
        # protocol); their confirmatory bank is version22b.
        from dynbelief.reflect.v22 import (V22B_BANK, V22_DEV_BANK, V22B_CFG,
                                           V22_DEV_CFG)
        return ("v22b", V22B_BANK, V22B_CFG, "v22dev", V22_DEV_BANK, V22_DEV_CFG)
    if bank_key == "typ":
        # TYPICAL households (P1 contrast class); shares the v22dev alpha wall.
        from dynbelief.reflect.v22 import (V22TYP_BANK, V22TYP_CFG, V22_DEV_BANK,
                                           V22_DEV_CFG)
        return ("typ", V22TYP_BANK, V22TYP_CFG, "v22dev", V22_DEV_BANK, V22_DEV_CFG)
    raise ValueError(bank_key)


def _load_rows(bank_name, label):
    p = OUT / f"rows_{bank_name}_{label}.jsonl"
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    # nomem context-overflow fix: if a rerun with the corrected token budget
    # exists, its llm_nomem rows supersede the originals (which silently zeroed
    # on prompt+max_tokens > max-model-len at late checkpoints)
    fix = OUT / f"rows_{bank_name}_{label}_nomemfix.jsonl"
    if fix.exists():
        fixed = [json.loads(l) for l in fix.read_text().splitlines() if l.strip()]
        rows = [r for r in rows if r["model"] != "llm_nomem"] + \
               [r for r in fixed if r["model"] == "llm_nomem"]
    return rows


def _stream_rows(by_obj, t_hi):
    rows = [{"day": t // 1440, "t_min": t, "parents": {o: r}}
            for o, evs in by_obj.items() for (t, r) in evs if t < t_hi]
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
    """Per-(bank) cache of household data, streams, base fits, and last-obs.

    CRITICAL: the classical & fusion arms fit on the SAME thinned event set the LLM
    saw (obs_spec), reconstructed deterministically via thinned_event_tuples — else
    the classical baseline would get the full stream while the LLM was starved (the
    equal-information requirement). `self.thin[hh]` is the thinned per-object events."""
    def __init__(self, bank, cfgmap, obs_spec=None):
        from dynbelief.reflect.run import thinned_event_tuples
        self.bank, self.cfgmap = bank, cfgmap
        self.h = {hh: core.load_hh(bank, hh) for hh in cfgmap}
        self.rooms = {hh: room_of(hh) for hh in cfgmap}
        self.obs_spec = obs_spec
        self.thin = {}
        for hh in cfgmap:
            kept = thinned_event_tuples(self.h[hh]["by_obj"], obs_spec)
            d = defaultdict(list)
            for (t, o, r) in kept:
                d[o].append((t, r))
            self.thin[hh] = d
        self._base = {}

    def base_arm(self, hh, ckpt, arm="C3g"):
        key = (hh, ckpt, arm)
        if key not in self._base:
            obs = _stream_rows(self.thin[hh], ckpt * 1440)   # THINNED stream
            self._base[key] = make_arm(arm, self.h[hh]["cand_set"], obs)[0] if obs else None
        return self._base[key]

    def last_obs(self, hh, obj, tq, ckpt):
        ev = [(t, r) for (t, r) in self.thin[hh].get(obj, [])   # THINNED
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


def _pseudo_counts(dist, obj, alpha, seed):
    """alpha pseudo-OBSERVATIONS of the target sampled from the LLM belief,
    spread over the pseudo-day grid (3/day at the OBS_HOURS cadence). These are
    Bayesian pseudo-counts: at fit time they COMPETE against the target edge's
    real event count n, so the prior's influence is automatically ~alpha/(alpha+n)
    — strong on unseen edges, vanishing on data-rich ones. No gate needed."""
    from dynbelief.e2.inject import OBS_HOURS
    from dynbelief import MIN_PER_DAY
    rng = np.random.default_rng(seed)
    recs = list(dist); w = np.array([dist[r] for r in recs])
    w = w / w.sum()
    rows = []
    for i in range(alpha):
        d, slot = divmod(i, len(OBS_HOURS))
        t = d * MIN_PER_DAY + OBS_HOURS[slot] + int(rng.integers(-60, 61))
        rec = recs[int(rng.choice(len(recs), p=w))]
        rows.append({"day": d, "t_min": t, "parents": {obj: rec}})
    return rows


def fusion_rows(ctx, direct_rows, alpha, tag="fusion"):
    """PURE EVIDENCE-RATIO fusion (entropy dropped). A CONSTANT alpha pseudo-counts
    of the memory-conditioned LLM belief are injected into the target edge and fit
    jointly with that edge's real events; the prior's influence is automatically
    ~alpha/(alpha+n) against the classical confidence n (real event count). No
    entropy term — the entropy diagnostic showed LLM hypothesis entropy does not
    predict accuracy in any model (flat-to-inverted), so trust comes from the
    evidence ratio alone. alpha is swept on dev and frozen."""
    out = []
    for r in direct_rows:
        hh, obj, ckpt, tq = r["hh"], r["object"], r["ckpt"], r["t_query"]
        h = ctx.h[hh]; cand_set = h["cand_set"]
        base = ctx.base_arm(hh, ckpt, "C3g")
        last = ctx.last_obs(hh, obj, tq, ckpt)
        if alpha <= 0 or base is None:
            rm = base
        else:
            dist = _dist_from_preds(r.get("preds"), cand_set)
            pseudo = _pseudo_counts(dist, obj, alpha, seed=100 + ckpt)
            treal = [{"day": t // 1440, "t_min": t, "parents": {obj: rec}}
                     for (t, rec) in ctx.thin[hh].get(obj, []) if t < ckpt * 1440]  # THINNED
            mini = make_arm("C3g", cand_set, pseudo + treal)[0]
            rm = _FusedRM(base, mini, obj)
        pred = _predict(rm, cand_set, obj, tq, last)
        out.append({"model": tag, "hh": hh, "object": obj, "ckpt": ckpt,
                    "test_day": r["test_day"], "true": r["true"], "rarity": r["rarity"],
                    "H": r.get("H"), "alpha": alpha, "pred": pred,
                    "correct": int(pred == r["true"]),
                    "room_correct": int(ctx.rooms[hh].get(pred, "x") ==
                                        ctx.rooms[hh].get(r["true"], "y"))})
    return out


def _obs_spec_of(rows):
    """Recover the obs spec the run used from the rows (falls back to None)."""
    from dynbelief.reflect.run import parse_obs_spec
    tags = {r.get("obs_spec") for r in rows if r.get("obs_spec")}
    tag = next(iter(tags), None)
    if not tag or tag == "none":
        return None
    if tag.startswith("orand"):
        return ("rand", float(tag.replace("orand", "")))
    return int(tag.replace("o", ""))


def sweep_alpha(label, obs_spec, bank_key="conf"):
    """DEV: pick alpha maximizing pooled receptacle accuracy of ratio fusion."""
    _, _, _, dev_key, dev_bank, dev_cfg = _bank_pair(bank_key)
    ctx = _Ctx(dev_bank, dev_cfg, obs_spec)
    direct = [r for r in _load_rows(dev_key, label) if r["model"] == "llm_direct"]
    print(f"alpha sweep on DEV ({len(direct)} queries, held-out accuracy):")
    best = None
    for am in ALPHA_GRID:
        acc = float(np.mean([r["correct"] for r in fusion_rows(ctx, direct, am)]))
        print(f"  alpha={am}:  fusion acc={acc:.3f}")
        if best is None or acc > best[1]:
            best = (am, acc)
    print(f"  => FROZEN alpha* = {best[0]}")
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


def evaluate(label, alpha, obs_spec, bank_key="conf", extra_rows=None):
    conf_key, conf_bank, conf_cfg, _, _, _ = _bank_pair(bank_key)
    ctx = _Ctx(conf_bank, conf_cfg, obs_spec)
    llm = _load_rows(conf_key, label)
    direct = [r for r in llm if r["model"] == "llm_direct"]
    rows = (llm + classical_rows(ctx, direct)
            + fusion_rows(ctx, direct, alpha, tag="fusion")
            + list(extra_rows or []))
    (OUT / f"all_rows_{conf_key}_{label}.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))
    present = {r["model"] for r in rows}
    arank = [m for m in ARANK if m in present] + sorted(present - set(ARANK))
    for field, gl in (("correct", "RECEPTACLE"), ("room_correct", "ROOM")):
        print(f"\n#### {gl}-level accuracy vs days of experience "
              f"(confirmatory, clustered 95% CI) ####")
        for rar in ["rare", "medium", "frequent", None]:
            print(f"\n  ### {'ALL' if rar is None else rar.upper()}")
            print("  " + f"{'days':>5}" + "".join(f"{m[:13]:>16}" for m in arank))
            for ck in CKPTS:
                cells = []
                for m in arank:
                    c = _cell(rows, m, [ck], rar, field)
                    cells.append(f"{c[0]:.2f}[{c[1]:.2f},{c[2]:.2f}]".rjust(16)
                                 if c else f"{'-':>16}")
                print("  " + f"{ck:>5}" + "".join(cells))
    return rows


def figures(label, rows, bank_key="conf"):
    _, conf_bank, conf_cfg, _, _, _ = _bank_pair(bank_key)
    # accuracy vs days per stratum: RECEPTACLE row (top, the deployment metric) +
    # ROOM row (bottom, coarser). Receptacle is less saturated and separates arms.
    fig, axes = plt.subplots(2, 3, figsize=(15.5, 8.6), sharex=True)
    for row_i, (field, gl) in enumerate([("correct", "RECEPTACLE"), ("room_correct", "ROOM")]):
        for ax, (rar, _, _) in zip(axes[row_i], e7.TERCILES):
            for m in ARANK:
                xs, ys = [], []
                for ck in CKPTS:
                    c = _cell(rows, m, [ck], rar, field)
                    if c:
                        xs.append(ck); ys.append(c[0])
                ls = "--" if m.startswith("classical") else "-"
                ax.plot(xs, ys, ls, color=COLORS[m], marker="o", ms=4, lw=1.8, label=m)
            n = len({(r['hh'], r['object']) for r in rows if r['rarity'] == rar})
            if row_i == 0:
                ax.set_title(f"{rar.upper()} (n={n} objs)")
            ax.grid(alpha=0.25); ax.set_ylim(-0.03, 1.03)
            if row_i == 1:
                ax.set_xlabel("days of experience")
        axes[row_i][0].set_ylabel(f"{gl}-level accuracy\n(fixed future test week)")
    axes[0][2].legend(fontsize=7.5, loc="lower right")
    fig.suptitle(f"Reflective memory ({label}) — receptacle (top) & room (bottom); "
                 "all arms see the SAME event stream (statistical / semantic / both)",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT / f"reflect_curves_{label}.png", dpi=140)
    # entropy trajectories
    fig2, ax = plt.subplots(figsize=(8, 4.2))
    for hh in conf_cfg:
        p = OUT / "memory" / conf_bank / f"{hh}__{label}" / "meta.jsonl"
        if not p.exists():
            continue
        meta = [json.loads(l) for l in p.read_text().splitlines()]
        ax.plot([m["day"] for m in meta], [m["H"] for m in meta], "-o", ms=3,
                label=hh.replace("regime_", "").replace("_v1", ""))
    ax.axhline(M.H_MAX, color="#999", ls=":", lw=1)
    ax.text(0.1, M.H_MAX + 0.02, "uniform (no idea)", fontsize=8, color="#777")
    ax.set_xlabel("day"); ax.set_ylabel("hypothesis entropy H (bits)")
    ax.set_title(f"Memory uncertainty over time ({label}) — entropy of the top-3 persona hypotheses")
    ax.legend(fontsize=8); ax.grid(alpha=0.25)
    fig2.tight_layout()
    fig2.savefig(OUT / f"reflect_entropy_{label}.png", dpi=140)
    print("wrote", OUT / f"reflect_curves_{label}.png", "and",
          OUT / f"reflect_entropy_{label}.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="deepseek")
    ap.add_argument("--bank", choices=["conf", "v22", "v22b", "typ"], default="conf")
    ap.add_argument("--alpha-max", type=int, default=None,
                    help="skip the dev sweep and use this frozen value")
    ap.add_argument("--obs-per-day", default=None,
                    help="obs spec the run used (none/N/randN); default: read from rows")
    ap.add_argument("--extra-rows", default=None,
                    help="jsonl of extra pre-scored rows (e.g. the surprise arm) "
                         "to merge into the tables/figures")
    ap.add_argument("--sweep-only", action="store_true")
    args = ap.parse_args()
    from dynbelief.reflect.run import parse_obs_spec
    conf_key = _bank_pair(args.bank)[0]
    # obs spec: explicit CLI wins, else recover from the conf rows the run recorded
    if args.obs_per_day is not None:
        obs_spec = parse_obs_spec(args.obs_per_day)
    else:
        obs_spec = _obs_spec_of(_load_rows(conf_key, args.label))
    am = (args.alpha_max if args.alpha_max is not None
          else sweep_alpha(args.label, obs_spec, args.bank))
    if args.sweep_only:
        return
    extra = None
    if args.extra_rows:
        from pathlib import Path
        extra = [json.loads(l) for l in Path(args.extra_rows).read_text().splitlines()
                 if l.strip()]
    rows = evaluate(args.label, am, obs_spec, args.bank, extra_rows=extra)
    figures(args.label, rows, args.bank)


if __name__ == "__main__":
    main()
