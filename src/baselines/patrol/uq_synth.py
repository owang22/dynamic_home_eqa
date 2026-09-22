"""Trivial-case checks for the uq wrappers on synthetic score streams (no bank, no belief).

    python3 -m baselines.patrol.uq_synth

Scores are nonconformity values in [0, 1] (1 - p(truth)).  Stationary segment: Beta(2, 5) (mean 0.29);
after the shift: Beta(5, 2) (mean 0.71).  Checks: decaying-step conformal coverage 0.90 +- 0.03 on the
stationary segment with q_t settling; martingale below 10 before the shift (over 20 seeds), above 100
within 60 steps after it.
"""
from __future__ import annotations

import random
import statistics as st

from baselines.patrol.uq_agents import DecayingStepConformal, MixtureMartingale


def main() -> int:
    ok = True
    # ---- conformal
    covs, qsd = [], []
    for seed in range(20):
        rng = random.Random(seed)
        c = DecayingStepConformal()
        hits, qs = [], []
        for t in range(1000):
            s = rng.betavariate(2, 5)
            covered = s <= c.q
            if t >= 200:
                hits.append(covered)
                qs.append(c.q)
            c.update(not covered, s)
        covs.append(sum(hits) / len(hits))
        qsd.append(st.pstdev(qs[-100:]))
    print(f"conformal, stationary Beta(2,5): coverage after 200 steps {st.mean(covs):.3f} (min {min(covs):.3f}, max {max(covs):.3f}); "
          f"sd of q over the last 100 steps {st.mean(qsd):.4f}")
    ok &= abs(st.mean(covs) - 0.9) <= 0.03 and st.mean(qsd) < 0.05
    # ---- martingale
    pre_max, detect_at = [], []
    for seed in range(20):
        rng = random.Random(100 + seed)
        m = MixtureMartingale(rng, delta=0.01, cusum=False)
        mx, det = 0.0, None
        for t in range(600):
            s = rng.betavariate(2, 5) if t < 300 else rng.betavariate(5, 2)
            v = m.step(s)
            if t < 300:
                mx = max(mx, v)
            elif det is None and v >= 100:
                det = t - 300
        pre_max.append(mx)
        detect_at.append(det)
    print(f"martingale: max before the shift {max(pre_max):.2f} (mean {st.mean(pre_max):.2f}); "
          f"steps to cross 100 after the shift: {sorted(d if d is not None else 999 for d in detect_at)}")
    ok &= max(pre_max) < 10 and all(d is not None and d <= 60 for d in detect_at)
    # ---- one-sided: an improving model (scores fall) must not fire
    fired = 0
    for seed in range(20):
        rng = random.Random(200 + seed)
        m = MixtureMartingale(rng, delta=0.01, cusum=False)
        for t in range(600):
            s = rng.betavariate(5, 2) if t < 300 else rng.betavariate(2, 5)
            if m.step(s) >= 100:
                fired += 1
                break
    print(f"martingale on an improving stream (scores fall at t=300): fired in {fired}/20 seeds (want 0)")
    ok &= fired == 0
    # ---- CUSUM e-detector (the roster's default): false alarms at 1000 over 1000 stationary steps, and a mild shift
    # (90% -> 50% accuracy, scores two-class) detected within ~1-2 days of 32 questions
    cross = 0
    for seed in range(50):
        rng = random.Random(300 + seed)
        m = MixtureMartingale(rng)
        cross += any(m.step(rng.betavariate(2, 5)) >= 1000 for t in range(1000))
    det = []
    for seed in range(50):
        rng = random.Random(400 + seed)
        m = MixtureMartingale(rng)
        d = None
        for t in range(700):
            ok_q = rng.random() < (0.9 if t < 400 else 0.5)
            v = m.step(rng.uniform(0.02, 0.3) if ok_q else rng.uniform(0.6, 1.0))
            if t >= 400 and d is None and v >= 1000:
                d = t - 400
        det.append(d if d is not None else 999)
    det.sort()
    print(f"cusum e-detector (threshold 1000): false alarms in {cross}/50 stationary streams of 1000 steps (want <= 3); "
          f"mild shift 90% -> 50% accuracy detected after median {det[25]} steps, max {det[-1]} (want median <= 40, all <= 100)")
    ok &= cross <= 3 and det[25] <= 40 and det[-1] <= 100
    print("ALL CHECKS PASS" if ok else "A CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
