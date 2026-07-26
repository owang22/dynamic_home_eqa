"""Jobs 1-4: mechanism of the evidence-following decay.

J1  Disentangle observation-COUNT from DAY / context-length (they are collinear
    by construction: objects with many observations are also later in the run).
J2  Classify the LLM's OVERRIDES — does it revert toward its own revealed PRIOR
    (prior gravity) or to some other routine-consistent guess?
J3  Ns + clustered CIs on every fidelity bin and override bar; override RATE
    reported next to override accuracy.
J4  ENVIRONMENT oracle fidelity: P(most-recent observation still correct at query
    time) from ground truth — the ceiling any echo-the-last-sighting policy can
    reach, and the principled justification for SOME overriding.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np

from dynbelief.two_capacities.diagnostics import rows_of


def _trace(arm):
    """Yield per-answer records with the arm's evidence state at that moment."""
    rows = rows_of(arm)
    by_hh = defaultdict(list)
    for r in rows:
        by_hh[r["hh"]].append(r)
    out = []
    for hh, rs in by_hh.items():
        rs.sort(key=lambda r: r["t"])
        last, nobs, lastday = {}, defaultdict(int), {}
        n_hist = 0                    # total observations held (context length proxy)
        first_pred = {}               # revealed prior: first answer with 0 obs of it
        for r in rs:
            if r["action"] == "answer" and nobs[r["obj"]] == 0:
                first_pred.setdefault(r["obj"], r["pred"])
            if r["action"] == "answer" and r["obj"] in last:
                out.append(dict(hh=hh, obj=r["obj"], kind=r["kind"], day=r["day"],
                                n_obs=nobs[r["obj"]], n_hist=n_hist,
                                lag=r["day"] - lastday[r["obj"]],
                                last_obs=last[r["obj"]], pred=r["pred"],
                                true=r["true"], correct=r["correct"],
                                follow=int(r["pred"] == last[r["obj"]]),
                                last_obs_still_true=int(last[r["obj"]] == r["true"]),
                                prior=first_pred.get(r["obj"])))
            if r["action"] == "resense":
                last[r["obj"]] = r["true"]; nobs[r["obj"]] += 1
                lastday[r["obj"]] = r["day"]; n_hist += 1
    return out


def _clu_ci(vals_by_clu, nb=3000, seed=7):
    clus = list(vals_by_clu)
    if not clus:
        return (float("nan"),) * 3, 0
    rng = np.random.default_rng(seed)
    m = [np.mean([v for i in rng.integers(0, len(clus), len(clus))
                  for v in vals_by_clu[clus[i]]]) for _ in range(nb)]
    allv = [v for vs in vals_by_clu.values() for v in vs]
    return (float(np.mean(allv)), float(np.percentile(m, 2.5)),
            float(np.percentile(m, 97.5))), len(allv)


def _by_obj(recs, field, filt=lambda r: True):
    d = defaultdict(list)
    for r in recs:
        if filt(r):
            d[(r["hh"], r["obj"])].append(r[field])
    return d


# ── J1: count vs day ─────────────────────────────────────────────────────────

def j1_count_vs_day(arm="llm"):
    recs = _trace(arm)
    print("=" * 92)
    print(f"J1 — is the fidelity decay driven by observation COUNT or by DAY/context length? [{arm}]")
    print("=" * 92)
    # matched: hold day-band fixed, vary count
    print("  MATCHED — follow-rate by n_obs WITHIN each day band (isolates count):")
    bands = [(0, 4), (5, 9), (10, 15)]
    print(f"    {'day band':>10}" + "".join(f"{f'n={k}' if k < 4 else 'n>=4':>12}" for k in range(1, 5)))
    for b0, b1 in bands:
        cells = []
        for k in range(1, 5):
            sel = [r for r in recs if b0 <= r["day"] <= b1
                   and (r["n_obs"] == k if k < 4 else r["n_obs"] >= 4)]
            cells.append(f"{np.mean([r['follow'] for r in sel]):.2f}({len(sel)})" if len(sel) >= 15
                         else f"{'-':>10}")
        print(f"    {f'{b0}-{b1}':>10}" + "".join(f"{c:>12}" for c in cells))
    print("  MATCHED — follow-rate by day band WITHIN each n_obs (isolates day/context):")
    print(f"    {'n_obs':>10}" + "".join(f"{f'd{b0}-{b1}':>12}" for b0, b1 in bands))
    for k in range(1, 5):
        cells = []
        for b0, b1 in bands:
            sel = [r for r in recs if b0 <= r["day"] <= b1
                   and (r["n_obs"] == k if k < 4 else r["n_obs"] >= 4)]
            cells.append(f"{np.mean([r['follow'] for r in sel]):.2f}({len(sel)})" if len(sel) >= 15
                         else f"{'-':>10}")
        print(f"    {(str(k) if k < 4 else '>=4'):>10}" + "".join(f"{c:>12}" for c in cells))
    # logistic regression: follow ~ n_obs + day + n_hist
    try:
        from sklearn.linear_model import LogisticRegression
        X = np.array([[r["n_obs"], r["day"], r["n_hist"]] for r in recs], float)
        y = np.array([r["follow"] for r in recs])
        Xs = (X - X.mean(0)) / X.std(0)
        lr = LogisticRegression(max_iter=2000).fit(Xs, y)
        names = ["n_obs (per-object evidence)", "day", "n_hist (context length)"]
        print("\n  LOGISTIC REGRESSION follow ~ standardized predictors (log-odds per 1 SD):")
        for nm, c in zip(names, lr.coef_[0]):
            print(f"    {nm:32s} {c:+.3f}")
        print("    (more negative = stronger driver of overriding)")
    except Exception as e:
        print("  regression skipped:", e)


# ── J2: what do overrides revert TO? ─────────────────────────────────────────

def j2_override_targets(arms=("llm", "llm_v1_pinned", "classical", "hybrid")):
    print("\n" + "=" * 92)
    print("J2 — when an arm OVERRIDES its own last observation, what does it answer?")
    print("     prior = the arm's OWN first prediction for that object before it had any"
          " observation of it (its revealed prior)")
    print("=" * 92)
    for arm in arms:
        recs = [r for r in _trace(arm) if r["prior"] is not None]
        ov = [r for r in recs if not r["follow"]]
        if not ov:
            continue
        to_prior = np.mean([r["pred"] == r["prior"] for r in ov])
        # baseline: how often would a random non-last-obs answer hit the prior?
        base = np.mean([r["prior"] != r["last_obs"] for r in ov]) / 13.0
        to_prior_correct = ([r["correct"] for r in ov if r["pred"] == r["prior"]])
        to_other_correct = ([r["correct"] for r in ov if r["pred"] != r["prior"]])
        print(f"  {arm:14s} overrides={len(ov):5d}  -> reverts to its PRIOR "
              f"{to_prior:.1%} (chance ~{base:.1%})  |  acc when reverting to prior "
              f"{np.mean(to_prior_correct) if to_prior_correct else float('nan'):.3f}"
              f"  vs other overrides {np.mean(to_other_correct) if to_other_correct else float('nan'):.3f}")
    # prior gravity vs accumulated evidence — the key curve
    print("\n  PRIOR GRAVITY vs accumulated evidence [llm]: P(answer == revealed prior)")
    recs = [r for r in _trace("llm") if r["prior"] is not None]
    print(f"    {'n_obs':>8}{'P(pred==prior)':>18}{'P(override)':>14}{'n':>8}")
    for k in range(1, 6):
        sel = [r for r in recs if (r["n_obs"] == k if k < 5 else r["n_obs"] >= 5)]
        if len(sel) < 15:
            continue
        print(f"    {(str(k) if k < 5 else '>=5'):>8}"
              f"{np.mean([r['pred'] == r['prior'] for r in sel]):>18.3f}"
              f"{np.mean([1 - r['follow'] for r in sel]):>14.3f}{len(sel):>8}")


# ── J3: Ns + clustered CIs on every bin/bar ──────────────────────────────────

def j3_bins_with_ci(arms=("classical", "llm", "llm_v1_pinned", "llm_selfconf", "hybrid")):
    print("\n" + "=" * 92)
    print("J3 — fidelity bins and override bars with Ns and object-clustered 95% CIs")
    print("=" * 92)
    for arm in arms:
        recs = _trace(arm)
        if not recs:
            continue
        print(f"\n  [{arm}]")
        print(f"    {'n_obs bin':>10}{'follow-rate [95% CI]':>28}{'n_queries':>11}{'n_objects':>11}")
        for k in (1, 2, 3, 4, 5):
            sel = [r for r in recs if (r["n_obs"] == k if k < 5 else r["n_obs"] >= 5)]
            if not sel:
                continue
            d = defaultdict(list)
            for r in sel:
                d[(r["hh"], r["obj"])].append(r["follow"])
            (m, lo, hi), n = _clu_ci(d)
            print(f"    {(str(k) if k < 5 else '>=5'):>10}"
                  f"{f'{m:.3f} [{lo:.3f},{hi:.3f}]':>28}{n:>11}{len(d):>11}")
        # override rate AND accuracy, both with CIs
        dfol = _by_obj(recs, "correct", lambda r: r["follow"] == 1)
        dovr = _by_obj(recs, "correct", lambda r: r["follow"] == 0)
        (mf, lf, hf), nf = _clu_ci(dfol)
        (mo, lo_, ho), no = _clu_ci(dovr)
        rate = no / (nf + no)
        print(f"    override RATE {rate:.3f} ({no}/{nf+no})  |  acc FOLLOW "
              f"{mf:.3f} [{lf:.3f},{hf:.3f}] (n={nf})  |  acc OVERRIDE "
              f"{mo:.3f} [{lo_:.3f},{ho:.3f}] (n={no})")


# ── J4: the environment's own fidelity ceiling ───────────────────────────────

def j4_environment_fidelity():
    print("\n" + "=" * 92)
    print("J4 — ENVIRONMENT fidelity: P(most-recent observation still correct at query time)")
    print("     = the ceiling of a perfect echo-the-last-sighting policy. If < 1, SOME")
    print("     overriding is principled; the question is whether the override is skilled.")
    print("=" * 92)
    for arm in ("classical", "llm", "hybrid"):
        recs = _trace(arm)
        if not recs:
            continue
        d = _by_obj(recs, "last_obs_still_true")
        (m, lo, hi), n = _clu_ci(d)
        print(f"  {arm:12s} echo-ceiling {m:.3f} [{lo:.3f},{hi:.3f}] (n={n})")
        print("      by lag (days since that observation): " + "  ".join(
            f"{lag}d:{np.mean([r['last_obs_still_true'] for r in recs if min(r['lag'],3)==lag]):.2f}"
            for lag in range(4)))
    recs = _trace("llm")
    ov = [r for r in recs if not r["follow"]]
    stale = [r for r in ov if not r["last_obs_still_true"]]
    print(f"\n  LLM overrides: {len(ov)} total; the last observation was ACTUALLY stale in "
          f"{len(stale)/len(ov):.1%} of them")
    print(f"  Of those correctly-suspected-stale overrides, it named the RIGHT new location "
          f"{np.mean([r['correct'] for r in stale]):.1%} of the time")
    print("  => the impulse to override is often justified; the destination guess is not.")


def main():
    j1_count_vs_day()
    j2_override_targets()
    j3_bins_with_ci()
    j4_environment_fidelity()


if __name__ == "__main__":
    main()
