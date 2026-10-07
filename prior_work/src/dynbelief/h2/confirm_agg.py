"""Cross-model aggregate of the confirmatory run (item: multi-model)."""
import json, glob, pathlib
import numpy as np
from collections import defaultdict
from dynbelief.h2 import core
from dynbelief.h2.confirm import PREREG, QUERY_DAYS

ARMS = ["classical", "class_freq", "llm_named", "llm_anon", "e4_hybrid"]


def _boot(by_hh, nb=3000, seed=1):
    hhs = list(by_hh)
    if not hhs:
        return (float("nan"),)*2
    rng = np.random.default_rng(seed); m = []
    for _ in range(nb):
        pick = rng.integers(0, len(hhs), len(hhs))
        vals = [v for i in pick for v in by_hh[hhs[i]]]
        m.append(np.mean(vals) if vals else 0.0)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def load(label):
    p = core.OUT / f"confirm_rows_{label}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def acc(rows, arm, kind):
    by = defaultdict(list)
    for r in rows:
        if r["arm"] == arm and r["kind"] == kind:
            by[r["household"]].append(r["correct"])
    allv = [v for vs in by.values() for v in vs]
    if not allv:
        return None
    lo, hi = _boot(by)
    return np.mean(allv), lo, hi


def main():
    labels = [pathlib.Path(f).stem.replace("confirm_rows_", "")
              for f in sorted(glob.glob(str(core.OUT / "confirm_rows_*.jsonl")))]
    print("=" * 78)
    print(f"CONFIRMATORY — cross-model ({', '.join(labels)})")
    print("  3 unseen confusable pairs · 300 held-out queries/model · clustered 95% CI")
    print("=" * 78)
    for kind in ("target", "conventional"):
        print(f"\n### {kind.upper()} objects" +
              ("  (regime-flipped; the result)" if kind == "target" else "  (typical; reliability check)"))
        hdr = f"  {'arm':12}" + "".join(f"{l[:16]:>22}" for l in labels)
        print(hdr); print("  " + "-" * (len(hdr)-2))
        for arm in ARMS:
            cells = []
            for lb in labels:
                a = acc(load(lb), arm, kind)
                cells.append(f"{a[0]:.2f} [{a[1]:.2f},{a[2]:.2f}]" if a else "  -  ")
            print(f"  {arm:12}" + "".join(f"{c:>22}" for c in cells))
    # mechanism: named-anon on targets, per household, per model
    print(f"\n### Mechanism: named−anon on TARGETS (per household × model)")
    print(f"  {'household':26}{'prereg':10}" + "".join(f"{l[:14]:>16}" for l in labels))
    for hh_base in sorted(PREREG):
        pr = PREREG[hh_base]
        cells = []
        for lb in labels:
            rows = load(lb)
            nm = [r["correct"] for r in rows if hh_base in r["household"] and r["arm"]=="llm_named" and r["kind"]=="target"]
            an = [r["correct"] for r in rows if hh_base in r["household"] and r["arm"]=="llm_anon" and r["kind"]=="target"]
            cells.append(f"{(np.mean(nm)-np.mean(an)):+.2f}" if nm and an else "-")
        print(f"  {hh_base.replace('regime_','').replace('_v1',''):26}{pr:10}" + "".join(f"{c:>16}" for c in cells))
    # realistic-mix dominance: E4 vs endpoints at conventional-heavy weighting
    print(f"\n### Realistic-mix accuracy (75% conventional / 25% regime-shifted)")
    print(f"  {'arm':12}" + "".join(f"{l[:16]:>18}" for l in labels))
    for arm in ("class_freq", "llm_named", "e4_hybrid"):
        cells = []
        for lb in labels:
            t = acc(load(lb), arm, "target"); c = acc(load(lb), arm, "conventional")
            cells.append(f"{0.25*t[0]+0.75*c[0]:.3f}" if t and c else "-")
        print(f"  {arm:12}" + "".join(f"{c:>18}" for c in cells))


if __name__ == "__main__":
    main()
