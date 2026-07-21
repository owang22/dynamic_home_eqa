"""D1 — Elicited-vs-true dynamics, direct comparison. No filter, no injection.

For each object class we compare the LLM-elicited prior against generator truth
and report the divergence SEPARATELY for the two components the E2 bug taught us
to separate:

  PLACEMENT  (where it lives): TV distance between the elicited occupancy
             distribution (home + secondary, normalized over receptacles) and
             the generator's marginal occupancy. Also top-1 home agreement.
  PERSISTENCE(how long it stays): the elicited daily move count
             (MOVE_RATE_PER_DAY[move_rate]) vs the generator's measured moves/
             day. Reported as a signed log2 ratio so "systematically too short
             dwell" == "systematically too many moves" shows up as a positive
             mean with a tight sign.

The hypothesis (from the E2 note): homes are ~right, timing is wrong, and the
wrong component is persistence — precisely the quantity the injection bug
destroyed. If elicited dwell is systematically too short across classes, that is
the diagnosis in one figure: LLMs know WHERE things live, not HOW LONG they stay
— which is exactly what breaks a temporal model and exactly what a counting
model supplies.

Models: gpt-5.5 (existing mixture-averaged priors in results/e2/priors_gpt55)
and any live OpenAI-compatible endpoint (e.g. the local DeepSeek-V4-Flash
server) elicited fresh here. NEVER Claude (it drafted the profiles).
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
from collections import defaultdict

import numpy as np

from dynbelief.profiles.schema import load_profile, default_class
from dynbelief.profiles.generator import simulate
from dynbelief.classical.oracle import C5Oracle
from dynbelief.e2.elicit import (build_prompt, SCHEMA, _SYSTEM, MOVE_RATE_PER_DAY,
                                 mixture_average)
from dynbelief.e2.inject import _occupancy_dist
from dynbelief.e2.run import BASE_DESCRIPTORS
from dynamic_home_eqa.paths import REPO_ROOT

MANUAL_DIR = REPO_ROOT / "profiles" / "manual"
GPT55_PRIORS = REPO_ROOT / "results" / "e2" / "priors_gpt55"
OUT_DIR = REPO_ROOT / "results" / "e2" / "d1"


# ── generator truth ─────────────────────────────────────────────────────────

def oracle_truth(prof, cand):
    """Per class: (occupancy dist over cand, moves/day). Occupancy is the
    day-averaged marginal over receptacles; moves/day is measured from the
    generator (mean over instances and days)."""
    oracle = C5Oracle(prof, cand, n_sims=150); oracle.fit([])
    idx = {c: i for i, c in enumerate(cand)}
    # class -> instances
    cls_objs = defaultdict(list)
    for o in prof.placements:
        cls_objs[default_class(o)].append(o)
    occ, moves = {}, {}
    # day-averaged occupancy from the oracle's own week-bucket table
    for cls, objs in cls_objs.items():
        acc = np.zeros(len(cand))
        for o in objs:
            v = oracle._occ.get(o)
            if v is not None:
                acc += v.mean(0)                 # average over time bins
        s = acc.sum()
        occ[cls] = acc / s if s > 0 else np.full(len(cand), 1.0 / len(cand))
    # moves/day measured directly from the generator
    n_days = 28
    cnt = defaultdict(float)
    for s in range(40):
        ev, _, _ = simulate(prof, n_days=n_days, seed=70000 + s)
        for e in ev:
            cnt[default_class(e["label"])] += 1
    for cls, objs in cls_objs.items():
        moves[cls] = cnt[cls] / (40 * n_days * len(objs))
    return occ, moves, idx


# ── elicited -> comparable quantities ───────────────────────────────────────

def elicited_occ(elic_cls, cand):
    """Elicited home+secondary -> full occupancy over the candidate axis."""
    home, dist = _occupancy_dist(elic_cls, cand)
    return np.array([dist.get(c, 0.0) for c in cand]), home


def tv(a, b):
    return 0.5 * float(np.abs(a - b).sum())


# ── one (model, base) comparison ────────────────────────────────────────────

def _resting_tv(e_occ, t_occ, el_idx):
    """TV between the two distributions restricted to NON-elsewhere receptacles
    (both renormalized). Isolates 'does it know the resting place' from 'how
    much time is the object away', which the day-averaged marginal conflates."""
    e = e_occ.copy(); t = t_occ.copy()
    e[el_idx] = 0.0; t[el_idx] = 0.0
    if e.sum() > 0: e = e / e.sum()
    if t.sum() > 0: t = t / t.sum()
    return tv(e, t)


def compare(prof, cand, elic_prior: dict) -> list[dict]:
    occ_t, moves_t, idx = oracle_truth(prof, cand)
    el_idx = idx["elsewhere"]
    rows = []
    for cls, elic in elic_prior.items():
        if cls not in occ_t:
            continue
        e_occ, e_home = elicited_occ(elic, cand)
        t_occ = occ_t[cls]
        # true resting home = argmax over NON-elsewhere receptacles
        t_rest = t_occ.copy(); t_rest[el_idx] = -1.0
        t_home = cand[int(np.argmax(t_rest))]
        elic_set = {elic.get("home")} | set(elic.get("secondary", {}).keys())
        m_elic = MOVE_RATE_PER_DAY.get(elic.get("move_rate", "low"), 0.6)
        m_true = moves_t[cls]
        # signed log2 ratio of moves (persistence): +ve => elicited moves MORE
        # (dwell too SHORT); guard both sides off zero.
        lr = math.log2((m_elic + 0.05) / (m_true + 0.05))
        rows.append({
            "class": cls,
            "placement_tv": round(tv(e_occ, t_occ), 4),           # full axis (incl. elsewhere)
            "resting_tv": round(_resting_tv(e_occ, t_occ, el_idx), 4),  # resting-only
            "home_match": int(e_home == t_home),                  # top-1 resting home
            "home_in_set": int(t_home in elic_set),               # soft: knew the resting place at all
            "elic_home": e_home, "true_home": t_home,
            "moves_elicited": round(m_elic, 3), "moves_true": round(m_true, 3),
            "persistence_log2ratio": round(lr, 3),
            "dwell_h_elicited": round(24.0 / m_elic, 1) if m_elic > 0 else None,
            "dwell_h_true": round(24.0 / m_true, 1) if m_true > 0 else None,
        })
    return rows


def elicit_live(client, descriptor, classes, receptacles, n_samples, seed0=1000):
    samples = []
    for s in range(n_samples):
        txt = client.generate(_SYSTEM, build_prompt(descriptor, classes, receptacles),
                              SCHEMA, seed=seed0 + s, temperature=0.7)
        try:
            samples.append(json.loads(txt))
        except json.JSONDecodeError:
            continue
    return mixture_average(samples, classes, receptacles)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--live-model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--live-label", default="deepseek-v4-flash")
    ap.add_argument("--n-samples", type=int, default=3)
    ap.add_argument("--no-live", action="store_true", help="gpt-5.5 (cached) only")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    client = None
    if not args.no_live:
        from dynbelief.llm_agent.clients import local_qwen
        client = local_qwen(endpoint=args.endpoint, model=args.live_model)

    all_rows = []
    for base, descriptor in BASE_DESCRIPTORS.items():
        prof = load_profile(MANUAL_DIR / f"{base}.yaml")
        cand = sorted(prof.receptacle_ids) + ["elsewhere"]
        classes = sorted({p.cls for p in prof.placements.values()})

        # gpt-5.5 (cached)
        pf = GPT55_PRIORS / f"{base}.json"
        if pf.exists():
            gp = json.loads(pf.read_text())["prior"]
            for r in compare(prof, cand, gp):
                all_rows.append({"model": "gpt-5.5", "base": base, **r})

        # live endpoint (e.g. DeepSeek) — reuse the cached elicitation if present
        cachef = OUT_DIR / f"elicited_{args.live_label}_{base}.json"
        if not args.no_live or cachef.exists():
            if cachef.exists():
                elic = json.loads(cachef.read_text())
            else:
                elic = elicit_live(client, descriptor, classes, cand[:-1], args.n_samples)
                cachef.write_text(json.dumps(elic, indent=1))
            for r in compare(prof, cand, elic):
                all_rows.append({"model": args.live_label, "base": base, **r})
        print(f"[d1] {base} done ({len(all_rows)} rows)")

    (OUT_DIR / "d1_rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in all_rows))
    _report(all_rows)


def _report(rows: list[dict]) -> None:
    by_model = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)
    print("\n" + "=" * 74)
    print("D1 — elicited vs generator truth: PLACEMENT vs PERSISTENCE")
    print("=" * 74)
    for model, rs in by_model.items():
        rtv = np.mean([r["resting_tv"] for r in rs])
        hm = np.mean([r["home_match"] for r in rs])
        hset = np.mean([r["home_in_set"] for r in rs])
        lrs = [r["persistence_log2ratio"] for r in rs]
        pos = np.mean([1 if x > 0 else 0 for x in lrs])
        print(f"\n### {model}  ({len(rs)} class-instances over {len({r['base'] for r in rs})} households)")
        print(f"  PLACEMENT (where it lives)")
        print(f"      knew resting home (in elicited set) = {hset:.0%}   top-1 home match = {hm:.0%}")
        print(f"      resting-only TV distance            = {rtv:.3f}   (elsewhere excluded)")
        print(f"  PERSISTENCE (how long it stays)")
        print(f"      mean log2(moves ratio) = {np.mean(lrs):+.2f}   median = {np.median(lrs):+.2f}   "
              f"(>0 => dwell too SHORT)")
        print(f"      share dwell-too-short  = {pos:.0%}   "
              f"median moves/day: elicited={np.median([r['moves_elicited'] for r in rs]):.2f} "
              f"true={np.median([r['moves_true'] for r in rs]):.2f}")
    print("\n" + "-" * 74)
    print("Read: high 'knew resting home' + low resting-TV => WHERE is ~right.")
    print("      one-signed persistence ratio (share>>50%) => HOW LONG is systematically wrong.")


if __name__ == "__main__":
    main()
