"""Calibration baseline: adaptive conformal inference wrapped around a belief.

    python3 -m baselines.patrol.aci --log most_frequent_with_dist.jsonl --out wrapped.jsonl [--gamma 0.02] [--method aci|dtaci]

Gibbs and Candes, "Adaptive Conformal Inference Under Distribution Shift"
(NeurIPS 2021), adapted from regression intervals to discrete locations
(reference code: github.com/Rose-STL-Lab/CPTC, algos/aci.py and dtaci.py):

* nonconformity of a question = 1 - p(true spot) under the belief;
* the prediction set at level alpha_t is every spot whose probability is at
  least ``1 - q_t``, where ``q_t`` is the (1 - alpha_t) empirical quantile
  (with the n+1 correction) of the past nonconformity scores in the
  calibration window;
* error = the true spot is outside the set;
* ``alpha_{t+1} = alpha_t + gamma * (alpha - err_t)`` (ACI), or the
  DtACI mixture of experts over a grid of gammas (Gibbs and Candes, JMLR
  2025), using the experts' probability-weighted mean alpha.

The point answer is untouched (the belief's argmax), so accuracy is the
belief's own; what changes is the reported confidence: ``conf_threshold``
= 1 - q_t, the probability bar a spot must clear to be in the set (it
drops when the belief has been missing), and ``set_size``.  ``top_prob``
is carried through for reference.

Input rows need ``question_id``, ``day_index`` (or ``day``), ``t_query``,
``truth`` and ``dist`` (a spots-only distribution: the output of
``patrol.bocpd --variant none`` or a mixture arm's ``live.jsonl``).  The
run is one household at a time, in question order.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from typing import Dict, List, Sequence

from baselines.patrol.run import spots_only

DEFAULT_GAMMAS = (0.001, 0.002, 0.004, 0.008, 0.016, 0.032, 0.064, 0.128)


def conservative_quantile(scores: Sequence[float], level: float) -> float:
    """The k-th smallest score with k = ceil((n + 1) * level); 1.0 (everything
    in the set) when k exceeds n, 0.0 when the level is at or below 0."""
    n = len(scores)
    if level <= 0:
        return 0.0
    k = math.ceil((n + 1) * level)
    if n == 0 or k > n:
        return 1.0
    return sorted(scores)[k - 1]


def pinball(u: float, alpha: float) -> float:
    return alpha * u - min(u, 0.0)


def wrap(rows: List[dict], alpha: float = 0.1, gamma: float = 0.02, method: str = "aci", window: int = 0,
         gammas: Sequence[float] = DEFAULT_GAMMAS, sigma: float = 1 / 1000, eta: float = 2.72) -> List[dict]:
    rows = sorted(rows, key=lambda r: (int(r["t_query"]), r["question_id"]))
    scores: List[float] = []
    alpha_t = alpha
    k = len(gammas)
    expert_alphas = [alpha] * k
    expert_ws = [1.0] * k
    expert_probs = [1.0 / k] * k
    out = []
    for r in rows:
        dist, _ = spots_only({kk: float(v) for kk, v in r["dist"].items()})
        truth = r["truth"]
        s = 1.0 - dist.get(truth, 0.0)
        cal = scores[-window:] if window else scores
        if method == "dtaci":
            alpha_t = sum(p * a for p, a in zip(expert_probs, expert_alphas))
        # the set at level alpha_t
        if alpha_t >= 1:
            q_t, in_set = 0.0, set()
        elif alpha_t <= 0:
            q_t, in_set = 1.0, set(dist)
        else:
            q_t = conservative_quantile(cal, 1.0 - alpha_t)
            in_set = {rec for rec, p in dist.items() if 1.0 - p <= q_t}
        err = 0.0 if truth in in_set else 1.0
        top = max(dist, key=lambda rec: (dist[rec], rec)) if dist else None
        out.append({**{kk: v for kk, v in r.items() if kk != "dist"},
                    "day_index": int(r.get("day_index", r.get("day"))),
                    "score": round(s, 5), "alpha_t": round(alpha_t, 5), "q_t": round(q_t, 5),
                    "conf_threshold": round(1.0 - q_t, 5), "set_size": len(in_set), "covered": err == 0.0,
                    "top_in_set": top in in_set, "top_prob": round(dist.get(top, 0.0), 4) if top else 0.0,
                    "aci_method": method, "gamma": gamma})
        # updates
        if method == "aci":
            alpha_t += gamma * (alpha - err)
        else:
            # conformity p-value of the new score among the calibration scores
            beta = (1 + sum(1 for c in cal if c >= s)) / (len(cal) + 1)
            losses = [pinball(beta - a, alpha) for a in expert_alphas]
            expert_alphas = [a + g * (alpha - (1.0 if a > beta else 0.0)) for a, g in zip(expert_alphas, gammas)]
            logw = [math.log(w + 1e-300) - eta * l for w, l in zip(expert_ws, losses)]
            m = max(logw)
            bar = [math.exp(v - m) for v in logw]
            z = sum(bar) + 1e-300
            expert_ws = [(1 - sigma) * b / z + sigma / k for b in bar]
            zz = sum(expert_ws)
            expert_probs = [w / zz for w in expert_ws]
        scores.append(s)
    return out


def summarize(rows: List[dict]) -> Dict[int, dict]:
    days = sorted({r["day_index"] for r in rows})
    out = {}
    for d in days + [None]:
        sub = [r for r in rows if d is None or r["day_index"] == d]
        out[d if d is not None else "all"] = {
            "n": len(sub), "coverage": round(sum(r["covered"] for r in sub) / len(sub), 3),
            "set_size": round(sum(r["set_size"] for r in sub) / len(sub), 2),
            "conf_threshold": round(sum(r["conf_threshold"] for r in sub) / len(sub), 3),
            "accuracy": round(sum(1 for r in sub if r.get("correct", r.get("answer") == r.get("truth"))) / len(sub), 3)}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", type=pathlib.Path, required=True, help="rows with dist (one household)")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--gamma", type=float, default=0.02)
    ap.add_argument("--method", default="aci", choices=("aci", "dtaci"))
    ap.add_argument("--window", type=int, default=0, help="calibration window in questions (0 = all past)")
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in a.log.open() if l.strip()]
    rows = [r for r in rows if "dist" in r]
    wrapped = wrap(rows, a.alpha, a.gamma, a.method, a.window)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w") as f:
        for r in wrapped:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    summ = summarize(wrapped)
    print(json.dumps(summ["all"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
