"""Two-Capacities Section 1 — free diagnostics on the existing answer-or-resense
confirmatory logs (no model calls).

D1  within-object before/after-resense accuracy deltas (Capacity B headline).
D2  Capacity A decomposed: RANKING (AUROC of confidence vs correctness; action as
    a binary ranker) vs LEVEL (ECE + operating-point gap).
D3  plot hygiene notes are implemented in figures.py (oracle dropped from
    risk-coverage; per-split ceilings annotated); here we quantify the llm_thresh
    confound (its resense rate over days) so it can be documented.

All accuracies use cf_correct (the counterfactual answer correctness, logged for
every query including resensed ones) — immune to action-selection bias.
"""
from __future__ import annotations

import json
from collections import defaultdict

import numpy as np

from dynbelief.answer_or_resense.run_aor import OUT as AOR_OUT

OUT = AOR_OUT.parent / "two_capacities"
ARMS = ["classical", "llm", "hybrid", "llm_thresh", "oracle"]


def rows_of(arm, tag="frozen", bank="conf"):
    f = AOR_OUT / f"rows_{arm}_{bank}_{tag}.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines()] if f.exists() else []


def _boot_delta(pairs, nb=4000, seed=5):
    """object-clustered bootstrap CI on the mean paired delta."""
    if not pairs:
        return (float("nan"),) * 3
    rng = np.random.default_rng(seed)
    v = np.array(pairs)
    m = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(nb)]
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


# ── D1: within-object before/after first resense ─────────────────────────────

def d1_before_after(arms=ARMS):
    print("=" * 88)
    print("D1 — within-object accuracy BEFORE vs AFTER the object's FIRST resense")
    print("     (cf_correct; paired per-(hh,object) delta, object-clustered 95% CI)")
    print("=" * 88)
    results = {}
    for arm in arms:
        rows = rows_of(arm)
        if not rows:
            continue
        by_obj = defaultdict(list)
        for r in rows:
            by_obj[(r["hh"], r["obj"], r["kind"])].append(r)
        for kind in ("typical", "atypical"):
            deltas, befores, afters = [], [], []
            for (hh, obj, k), qs in by_obj.items():
                if k != kind:
                    continue
                qs.sort(key=lambda r: r["t"])
                first = next((i for i, r in enumerate(qs) if r["action"] == "resense"), None)
                if first is None or first == 0 or first == len(qs) - 1:
                    continue          # need queries on both sides
                b = np.mean([r["cf_correct"] for r in qs[:first]])
                a = np.mean([r["cf_correct"] for r in qs[first + 1:]])
                deltas.append(a - b); befores.append(b); afters.append(a)
            m, lo, hi = _boot_delta(deltas)
            results[(arm, kind)] = (m, lo, hi, len(deltas),
                                    float(np.mean(befores)) if befores else float("nan"),
                                    float(np.mean(afters)) if afters else float("nan"))
            sep = " *" if (lo > 0 or hi < 0) else ""
            print(f"  {arm:11s} {kind[:4]}: before {results[(arm,kind)][4]:.2f} -> "
                  f"after {results[(arm,kind)][5]:.2f}   delta {m:+.2f} "
                  f"[{lo:+.2f},{hi:+.2f}] (n={len(deltas)}){sep}")
    return results


def d1_by_resense_count(arms=ARMS):
    print("\nD1b — answer accuracy (cf) vs resenses ACCUMULATED on that object")
    hdr = f"  {'arm':11s}" + "".join(f"{k:>8}" for k in ["0", "1", "2", "3+"])
    print(hdr + "   (pooled splits)")
    for arm in arms:
        rows = rows_of(arm)
        if not rows:
            continue
        seen = defaultdict(int)
        acc = defaultdict(list)
        for r in sorted(rows, key=lambda r: (r["hh"], r["obj"], r["t"])):
            k = (r["hh"], r["obj"])
            bucket = min(seen[k], 3)
            acc[bucket].append(r["cf_correct"])
            if r["action"] == "resense":
                seen[k] += 1
        print(f"  {arm:11s}" + "".join(
            f"{np.mean(acc[b]):>8.2f}" if acc[b] else f"{'-':>8}" for b in range(4)))


def d1_decay(arms=("llm", "classical", "hybrid")):
    print("\nD1c — accuracy vs DAYS SINCE the object's last resense (does a gain wash out?)")
    print(f"  {'arm':11s}" + "".join(f"{k:>8}" for k in ["same-day", "1d", "2d", "3d+"]))
    for arm in arms:
        rows = rows_of(arm)
        if not rows:
            continue
        last = {}
        acc = defaultdict(list)
        for r in sorted(rows, key=lambda r: (r["hh"], r["obj"], r["t"])):
            k = (r["hh"], r["obj"])
            if k in last:
                dd = r["day"] - last[k]
                acc[min(dd, 3)].append(r["cf_correct"])
            if r["action"] == "resense":
                last[k] = r["day"]
        print(f"  {arm:11s}" + "".join(
            f"{np.mean(acc[b]):>8.2f}" if acc[b] else f"{'-':>8}" for b in range(4)))


# ── D2: Capacity A — ranking vs level ────────────────────────────────────────

def _auroc(scores, labels):
    """AUROC via rank statistic."""
    s, y = np.asarray(scores, float), np.asarray(labels, int)
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    ranks = np.argsort(np.argsort(np.concatenate([pos, neg]))) + 1
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2)
                 / (len(pos) * len(neg)))


def d2_ranking_vs_level():
    print("\n" + "=" * 88)
    print("D2 — Capacity A decomposed: RANKING (AUROC, higher=knows what it doesn't know)")
    print("     vs LEVEL (does it act at the right threshold)")
    print("=" * 88)
    for arm in ("llm", "hybrid", "llm_thresh", "classical"):
        rows = rows_of(arm)
        if not rows:
            continue
        for kind in ("typical", "atypical"):
            k = [r for r in rows if r["kind"] == kind]
            # verbalized (LLM arms) — sanitized to [0,1]
            vb = [(r["verbal_conf"], r["cf_correct"]) for r in k
                  if r.get("verbal_conf") is not None and 0 <= r["verbal_conf"] <= 1]
            au_v = _auroc([x[0] for x in vb], [x[1] for x in vb]) if vb else float("nan")
            # internal confidence
            ic = [(r["conf"], r["cf_correct"]) for r in k if r.get("conf") is not None]
            au_c = _auroc([x[0] for x in ic], [x[1] for x in ic]) if ic else float("nan")
            # ACTION as a binary ranker: resense should target would-be-wrong
            res = [r for r in k if r["action"] == "resense"]
            ans = [r for r in k if r["action"] == "answer"]
            sens = (np.mean([1 - r["cf_correct"] for r in res]) if res else float("nan"))
            err = 1 - np.mean([r["cf_correct"] for r in k])
            rr = len(res) / len(k)
            print(f"  {arm:11s} {kind[:4]}: AUROC verbal={au_v:.2f} internal={au_c:.2f} | "
                  f"P(would-be-wrong|resensed)={sens:.2f} vs base err={err:.2f} | "
                  f"resense rate {rr:.2f} vs err {err:.2f} (ratio {rr/err:.2f})")


def d3_llm_thresh_confound():
    print("\n" + "=" * 88)
    print("D3 — llm_thresh confound documentation: its resense rate collapses as C3g's")
    print("     posterior sharpens, while the LLM (whose answers it uses) has not improved")
    print("=" * 88)
    rows = rows_of("llm_thresh")
    for kind in ("typical", "atypical"):
        k = [r for r in rows if r["kind"] == kind]
        by = defaultdict(list)
        for r in k:
            by[r["day"]].append(r["action"] == "resense")
        days = sorted(by)
        rr = [f"d{d}:{np.mean(by[d]):.2f}" for d in days[::2]]
        print(f"  {kind[:4]}: " + "  ".join(rr))
    bad = [r for arm in ("llm", "hybrid", "llm_thresh") for r in rows_of(arm)
           if r.get("verbal_conf") is not None and not (0 <= r["verbal_conf"] <= 1)]
    tot = sum(len([r for r in rows_of(a) if r.get("verbal_conf") is not None])
              for a in ("llm", "hybrid", "llm_thresh"))
    print(f"\n  off-scale verbalized confidences: {len(bad)}/{tot} ({len(bad)/tot:.1%}) — "
          f"values like 3 or 85 (rating-scale / percent leakage); excluded from ECE/AUROC, logged")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d1_before_after()
    d1_by_resense_count()
    d1_decay()
    d2_ranking_vs_level()
    d3_llm_thresh_confound()


if __name__ == "__main__":
    main()


# ── D4 (added after the prompt audit): evidence-FOLLOWING, the corrected test ──

def d4_follow_own_evidence(arms=("classical", "llm", "llm_v1_pinned",
                                 "llm_selfconf", "hybrid")):
    """The corrected Capacity-B test.

    D1's before/after delta was CONFOUNDED: classical's "before" is 0.000 because
    with no observations it is uniform over ~14 candidates, while the LLM's
    "before" is 0.42 because it has a conventional prior. So classical's +0.59
    delta mostly measures "went from nothing to something", not superior
    integration. The unconfounded question is: does the arm ANSWER WITH its own
    most-recent observation of that object, and does that fidelity hold as
    evidence accumulates?"""
    print("\n" + "=" * 88)
    print("D4 — does the arm answer with its OWN most-recent observation of the object?")
    print("=" * 88)
    for arm in arms:
        rows = rows_of(arm)
        if not rows:
            continue
        by_hh = defaultdict(list)
        for r in rows:
            by_hh[r["hh"]].append(r)
        follow, fol_acc, ovr_acc, ovr_moved = [], [], [], []
        buckets = defaultdict(list)
        for hh, rs in by_hh.items():
            rs.sort(key=lambda r: r["t"])
            last, nobs = {}, defaultdict(int)
            for r in rs:
                if r["action"] == "answer" and r["obj"] in last:
                    lo = last[r["obj"]]
                    hit = r["pred"] == lo
                    follow.append(hit)
                    buckets[min(nobs[r["obj"]], 4)].append(hit)
                    (fol_acc if hit else ovr_acc).append(r["correct"])
                    if not hit:
                        ovr_moved.append(r["true"] != lo)
                if r["action"] == "resense":
                    last[r["obj"]] = r["true"]; nobs[r["obj"]] += 1
        print(f"  {arm:14s} follow-rate {np.mean(follow):.3f} | "
              f"acc when FOLLOWING {np.mean(fol_acc):.3f} | "
              f"acc when OVERRIDING {np.mean(ovr_acc):.3f} "
              f"(object had truly moved in {np.mean(ovr_moved):.0%} of overrides)")
        if arm.startswith("llm"):
            print("      follow-rate by #observations held: " + "  ".join(
                f"{k}{'+' if k == 4 else ''}obs:{np.mean(buckets[k]):.2f}"
                for k in sorted(buckets)))
