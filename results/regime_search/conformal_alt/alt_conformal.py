#!/usr/bin/env python3
"""Alternative conformal wrappers on the SAME base learner and the SAME questions.

Every method is replayed off the per-question distributions already on disk in
uq/regime/<regime>/ocp_tt/hh_*_t03.jsonl (the never-forgets timetable's `dist`, the
freshness weight `rel`, and the truth).  No belief model is re-run, so every method
sees byte-identical predictions and the identical question set.

Methods (all alpha = 0.1, i.e. a 90% coverage target, all on score 1 - rel * p(y)):
  ocp_base   DecayingStepConformal(eta0=.05, eps=.1, eta_min=.005)   <- the shipped agent
  fix_eta05  same, eta pinned at 0.05 (eta_min = eta0, so the decay never bites)
  fix_eta02  same, eta pinned at 0.02
  wq_tau24   WeightedQuantileConformal(tau_w=24h)
  wq_tau12   WeightedQuantileConformal(tau_w=12h)
"""
import collections, json, os, pathlib, sys

ROOT = pathlib.Path("/home/oliver/robot/dynamic_home_eqa")
sys.path.insert(0, str(ROOT / "src"))
from baselines.patrol.uq_agents import DecayingStepConformal, WeightedQuantileConformal  # noqa

UQ = ROOT / "results/confidence_shift_2026-09-20/uq/regime"
OUT = ROOT / "results/regime_search/conformal_alt"
ALPHA = 0.1

METHODS = ["ocp_base", "fix_eta05", "fix_eta02", "wq_tau24", "wq_tau12"]
LABEL = {"ocp_base": "DecayingStep (shipped, eta_min=.005)", "fix_eta05": "Fixed step eta=0.05",
         "fix_eta02": "Fixed step eta=0.02", "wq_tau24": "WeightedQuantile tau_w=24h",
         "wq_tau12": "WeightedQuantile tau_w=12h"}


def make(name):
    if name == "ocp_base":
        return DecayingStepConformal(ALPHA, eta0=0.05, eps=0.1, eta_min=0.005)
    if name == "fix_eta05":
        return DecayingStepConformal(ALPHA, eta0=0.05, eps=0.1, eta_min=0.05)
    if name == "fix_eta02":
        return DecayingStepConformal(ALPHA, eta0=0.02, eps=0.1, eta_min=0.02)
    if name == "wq_tau24":
        return WeightedQuantileConformal(ALPHA, tau_w=24.0)
    if name == "wq_tau12":
        return WeightedQuantileConformal(ALPHA, tau_w=12.0)
    raise KeyError(name)


def load_rows(regime):
    """Per household, the question stream in the order the agent saw it."""
    out = {}
    for f in sorted((UQ / regime / "ocp_tt").glob("hh_s*_t03.jsonl")):
        hh = f.name.split("_t03")[0]
        rows = [json.loads(l) for l in f.read_text().splitlines()]
        # the logged order is already (t_query, question_id); assert it
        key = [(r["t_query"], r["question_id"]) for r in rows]
        assert key == sorted(key), f"{f} not in query order"
        lens = {len(r["dist"]) for r in rows}
        assert len(lens) == 1, f"{f}: dist length varies {sorted(lens)} - spots cannot be recovered"
        warm = [r["set_size"] for r in rows if r["q_t"] == 1.0]
        assert set(warm) == lens, f"{f}: warm-start set size {set(warm)} != #spots {lens}"
        out[hh] = rows
    return out


def replay(rows, name):
    """-> list of (day_index, set_size, covered) for this household under method `name`."""
    c = make(name)
    wq = isinstance(c, WeightedQuantileConformal)
    res = []
    for r in rows:
        rel, dist, truth = r["rel"], r["dist"], r["truth"]
        scores = {s: 1.0 - rel * p for s, p in dist.items()}     # dist covers every spot (asserted above)
        q = c.quantile(r["t_query"]) if wq else c.q
        cset = {s for s, sc in scores.items() if sc <= q}
        covered = truth in cset
        s_truth = 1.0 - rel * dist.get(truth, 0.0)
        if wq:
            c.update(r["t_query"], s_truth)
        else:
            c.update(not covered, s_truth)
        res.append((r["day_index"], len(cset), covered, q))
    return res


def series(regime):
    """-> (per-day dict per method, per-day n, baseline-reproduction diagnostics)."""
    hhs = load_rows(regime)
    per = {m: collections.defaultdict(lambda: [0, 0, 0.0]) for m in METHODS}   # day -> [n, ncov, sum_set]
    n_day = {m: collections.Counter() for m in METHODS}
    mismatch = {"set": 0, "cov": 0, "n": 0}
    for hh, rows in sorted(hhs.items()):
        for m in METHODS:
            for (day, ss, cov, _q), r in zip(replay(rows, m), rows):
                c = per[m][day]; c[0] += 1; c[1] += int(cov); c[2] += ss
                n_day[m][day] += 1
                if m == "ocp_base":
                    mismatch["n"] += 1
                    mismatch["set"] += int(ss != r["set_size"])
                    mismatch["cov"] += int(cov != bool(r["covered"]))
    ns = {m: dict(n_day[m]) for m in METHODS}
    base = ns[METHODS[0]]
    for m in METHODS:
        assert ns[m] == base, f"{regime}: question count differs for {m}"
    return per, base, mismatch


def stat(per, m, days):
    n = sum(per[m][d][0] for d in days if d in per[m])
    if not n:
        return None
    return sum(per[m][d][2] for d in days if d in per[m]) / n


def cov(per, m, days):
    n = sum(per[m][d][0] for d in days if d in per[m])
    if not n:
        return None
    return 100.0 * sum(per[m][d][1] for d in days if d in per[m]) / n


def first_exceed(per, m, base_days, scan_days, mult=1.5):
    b = stat(per, m, base_days)
    for d in scan_days:
        s = stat(per, m, [d])
        if s is not None and s > mult * b:
            return d, b
    return None, b


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dump = {}
    # NB the two banks are NOT the same run: sick2x_owner's FIRST spell is days 14-20 (stages say
    # "return" from day 21), while sick10_owner's runs 14-23.  The question streams are identical
    # through day 20 and diverge from day 21 on.
    for regime, spells in (("sick10_owner", [(14, 23)]), ("sick2x_owner", [(14, 20), (28, 34)])):
        per, ns, mm = series(regime)
        print(f"\n=== {regime} ===")
        print(f"  baseline reproduction: {mm['n']} questions, set-size mismatches {mm['set']}, "
              f"coverage mismatches {mm['cov']}")
        days = sorted(ns)
        print(f"  days {days[0]}..{days[-1]}, n/day identical across all {len(METHODS)} methods: True")
        dump[regime] = {"n_per_day": {str(d): ns[d] for d in days}, "spells": spells,
                        "repro_mismatch": mm,
                        "series": {m: {str(d): [per[m][d][0], per[m][d][1], round(per[m][d][2], 4)] for d in days}
                                   for m in METHODS}}
        for m in METHODS:
            line = [f"  {LABEL[m]:<38}"]
            line.append(f"cov(d14)={cov(per,m,[14]):5.1f}%")
            d, b = first_exceed(per, m, range(9, 14), range(14, 24))
            line.append(f"pre(9-13)set={b:4.2f} first>1.5x: {('day %d' % d) if d else 'never'}")
            lo, hi = spells[0]
            pk = max(((stat(per, m, [x]), x) for x in range(14, 24) if x in per[m]))
            line.append(f"peak(14-23)={pk[0]:5.2f} (d{pk[1]})")
            line.append(f"set(20-23)={stat(per,m,range(20,24)):4.2f}")
            line.append(f"set(last4 of spell {lo}-{hi})={stat(per,m,range(hi-3,hi+1)):4.2f}")
            print(" ".join(line))
        if len(spells) > 1:
            print("  --- second spell (days 28-34) ---")
            for m in METHODS:
                line = [f"  {LABEL[m]:<38}"]
                line.append(f"cov(d28)={cov(per,m,[28]):5.1f}%")
                d, b = first_exceed(per, m, range(23, 28), range(28, 35))
                line.append(f"pre(23-27)set={b:4.2f} first>1.5x: {('day %d' % d) if d else 'never'}")
                pk = max(((stat(per, m, [x]), x) for x in range(28, 35) if x in per[m]))
                line.append(f"peak(28-34)={pk[0]:5.2f} (d{pk[1]})")
                line.append(f"set(31-34)={stat(per,m,range(31,35)):4.2f}")
                line.append(f"cov(28-34)={cov(per,m,range(28,35)):5.1f}%")
                print(" ".join(line))
        print("  n per day:", {d: ns[d] for d in days})
    print("\n=== why the weighted quantile is so wide (sick10_owner) ===")
    rows_all = load_rows("sick10_owner")
    for tau in (12.0, 24.0, 72.0):
        deg = tot = 0; W_sum = 0.0
        for rows in rows_all.values():
            c = WeightedQuantileConformal(ALPHA, tau_w=tau)
            for r in rows:
                t = r["t_query"]
                if len(c.hist) >= c.warm:
                    W = sum(2.0 ** (-max(0, t - ti) / (tau * 3600.0)) for ti, _ in c.hist)
                    W_sum += W; tot += 1
                    deg += int((1.0 - ALPHA) * (W + 1.0) > W)   # the +inf mass alone -> the whole house
                c.update(t, 1.0 - r["rel"] * r["dist"].get(r["truth"], 0.0))
        print(f"  tau_w={tau:4.0f}h  mean effective sample W={W_sum/tot:5.2f}  "
              f"questions where the +inf point mass alone decides the quantile (set = whole house): {100*deg/tot:4.1f}%"
              f"   [alpha=0.1 needs W >= 9]")
    (OUT / "alt_conformal.json").write_text(json.dumps(dump, indent=1))
    print("\nwrote", OUT / "alt_conformal.json")


if __name__ == "__main__":
    main()
