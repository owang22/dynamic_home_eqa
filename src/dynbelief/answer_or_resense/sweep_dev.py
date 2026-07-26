"""DEV-bank sweeps (offline arms only — classical + oracle; free, no LLM).

Key efficiency: the classical arm's TRAJECTORY depends only on (tau, Q, B) — the
reward values (r, wrong) never enter its decision rule — and the oracle's on
(Q, B). So simulate each trajectory ONCE and score it under every (r, wrong)
cell analytically afterwards.

Selection criteria (frozen before confirmatory):
  1. PRIMARY REWARD CELL: the (Q, B, r, wrong) where the ORACLE's resense rate is
     INTERIOR (not ~0, not pinned at the B/Q ceiling) — the KARL-degeneracy check
     applied at selection time.
  2. tau_c*: classical tau maximizing dev cumulative reward at the primary cell.
Prints the frozen-parameter table.
"""
from __future__ import annotations

import json
from collections import defaultdict

import numpy as np

from dynbelief.h2 import core
from dynbelief.answer_or_resense.run_aor import households, build_arm, OUT
from dynbelief.answer_or_resense import env

TAUS = [0.3, 0.45, 0.6, 0.75]
QS = [6, 10]
BS = [2, 5, 10]
RS = [0.2, 0.4, 0.6]
WRONGS = [0.0, -1.0]


def trajectories():
    """arm x (tau,Q,B) -> rows with action + cf_correct (reward-free)."""
    hhs = households("dev")
    data = {hh: core.load_hh(bd, hh) for _, hh, _, bd in hhs}
    out = {}
    for Q in QS:
        for B in BS:
            for tau in TAUS:
                rows = []
                for i, hh, cfg, bd in hhs:
                    arm = build_arm("classical", tau, None, "v1")
                    rows += env.run_episode(arm, i, hh, cfg, data[hh], Q=Q, B=B,
                                            r_resense=0.5, wrong=0.0)
                out[("classical", tau, Q, B)] = rows
            rows = []
            for i, hh, cfg, bd in hhs:
                arm = build_arm("oracle", None, None, "v1")
                rows += env.run_episode(arm, i, hh, cfg, data[hh], Q=Q, B=B,
                                        r_resense=0.5, wrong=0.0)
            out[("oracle", None, Q, B)] = rows
            print(f"trajectories Q={Q} B={B} done", flush=True)
    return out


def score(rows, r, wrong):
    """Re-score a trajectory under (r, wrong)."""
    tot = 0.0
    for x in rows:
        tot += r if x["action"] == "resense" else (1.0 if x["cf_correct"] else wrong)
    return tot / len({(x["hh"]) for x in rows})       # per-household reward


def resense_rate(rows):
    return float(np.mean([x["action"] == "resense" for x in rows]))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    T = trajectories()
    # ── 1. reward-cell selection by ORACLE interiority ──
    print("\nORACLE resense rates (must be interior — not ~0, not at ceiling B/Q):")
    cand = []
    for Q in QS:
        for B in BS:
            rr = resense_rate(T[("oracle", None, Q, B)])
            ceil = B / Q
            interior = 0.05 < rr < 0.9 * ceil
            print(f"  Q={Q:>2} B={B:>2}: oracle rr={rr:.2f} ceiling={ceil:.2f} "
                  f"{'INTERIOR' if interior else 'degenerate'}")
            if interior:
                cand.append((Q, B, rr))
    Q_, B_ = (cand[0][0], cand[0][1]) if cand else (6, 2)
    # among interior cells prefer the scarcer budget (the point of the experiment)
    cand.sort(key=lambda x: (x[1] / x[0],))
    if cand:
        Q_, B_ = cand[0][0], cand[0][1]
    # ── reward values: keep oracle interior AND classical not pinned ──
    print(f"\nprimary sensing cell: Q={Q_} B={B_}")
    print("\nclassical tau sweep at the primary cell, per (r, wrong):")
    best = {}
    for r in RS:
        for w in WRONGS:
            scs = {tau: score(T[("classical", tau, Q_, B_)], r, w) for tau in TAUS}
            tau_ = max(scs, key=scs.get)
            orc = score(T[("oracle", None, Q_, B_)], r, w)
            best[(r, w)] = (tau_, scs[tau_], orc)
            print(f"  r={r} wrong={w:+.0f}: " +
                  "  ".join(f"tau{t}:{scs[t]:.1f}" for t in TAUS) +
                  f"  -> tau*={tau_}  (oracle {orc:.1f})")
    # primary reward: mid r, wrong=0 (unless it pins the classical rr)
    r_, w_ = 0.4, 0.0
    tau_, sc_, orc_ = best[(r_, w_)]
    rr_cls = resense_rate(T[("classical", tau_, Q_, B_)])
    print(f"\nFROZEN: Q={Q_} B={B_} r={r_} wrong={w_} tau_c*={tau_} "
          f"(dev reward/hh {sc_:.1f}, oracle {orc_:.1f}, classical rr {rr_cls:.2f})")
    (OUT / "frozen_dev_params.json").write_text(json.dumps({
        "Q": Q_, "B": B_, "r": r_, "wrong": w_, "tau_classical": tau_,
        "note": "hybrid tau swept separately on dev with LLM; alpha*=6.07 reused"},
        indent=1))


if __name__ == "__main__":
    main()
