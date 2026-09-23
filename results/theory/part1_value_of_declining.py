#!/usr/bin/env python3
"""PART 1. Closed form for the value of being allowed to decline, tested against the measured F9 numbers.

    V = E_s[(1 - 2 q(s))^+],  q(s) = P(correct | confidence signal s)

Read-only on the logs; prints tables. Nothing here fits a parameter: q(s) is a plug-in estimate from
binned confidence, and every comparison is stated before it is computed (see the deliverable .md).

Usage:  python3 part1_value_of_declining.py            (prints all tables)
"""
import collections
import glob
import json
import math
import os
import random
import statistics as st

ROOT = "/home/oliver/robot/dynamic_home_eqa/results"
CLS = os.path.join(ROOT, "regime_search", "sick10_owner", "classical")
LLM = os.path.join(ROOT, "confidence_shift_2026-09-20", "uq", "llm_strategies", "chain_person", "nottold")
WANT = {"TimetableLookup(bin=2h,days=all)": "ttfrozen",
        "TimetableLookup(bin=2h,days=all,hl=72h)": "tt3d",
        "PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)": "perpetua",
        "LastObservation": "lastseen"}
NAME = {"ttfrozen": "never-forgets timetable", "tt3d": "3-day timetable", "perpetua": "Perpetua*",
        "longcontext": "long-context", "lastseen": "last seen"}
ORDER = ["ttfrozen", "tt3d", "perpetua", "longcontext"]
WINDOWS = {"settled 9-13": range(9, 14), "sick 14-16": range(14, 17), "spell 17-23": range(17, 24),
           "back 24-26": range(24, 27), "after 27-31": range(27, 32)}
MIN_CELL = 10          # cells under 10 questions are not reported
MIN_BIN = 10           # no q(s) estimate from fewer than this many questions
MIN_BIN_CF = 8         # the same, inside a cross-fitting half (halves are half the size)


# ---------------------------------------------------------------- loading
def load():
    """method -> hh -> [(day, conf, correct)] -- exactly the rows decision_extra.py scores."""
    rows = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in sorted(glob.glob(os.path.join(CLS, "hh_s*_t03.jsonl"))):
        hh = os.path.basename(f).split("_t03")[0]
        for line in open(f):
            r = json.loads(line)
            m = WANT.get(r["belief"])
            if m:
                rows[m][hh].append((r["day_index"], float(r["top_prob"]), bool(r["correct"])))
    for d in sorted(glob.glob(os.path.join(LLM, "hh_s*_longcontext_nottold_lookoff"))):
        hh = os.path.basename(d).split("_t03")[0]
        p = os.path.join(d, "run_log.jsonl")
        if not os.path.exists(p):
            continue
        for line in open(p):
            r = json.loads(line)
            c = r.get("raw_confidence")
            if c is not None:
                rows["longcontext"][hh].append((r["day_index"], float(c), bool(r["correct"])))
    return rows


def cell(by_hh, hh, days):
    return [(c, ok) for d, c, ok in by_hh[hh] if d in days]


def qpd(by_hh, hh, days):
    """Questions per day for THIS household in THIS window: households differ (16/day down to 4/day on
    some days), so the per-question -> per-day conversion has to be per household, not a global 16."""
    ds = collections.Counter(d for d, _, _ in by_hh[hh] if d in days)
    return (sum(ds.values()) / len(ds)) if ds else 0.0


# ---------------------------------------------------------------- the formula
def bins_by_rank(pairs, K):
    """Quantile (rank) bins that never split a tied confidence value, each >= MIN_BIN if possible.

    Rank-based binning is the estimator the invariance argument needs: it depends on the ORDER of the
    confidences only, so any strictly monotone relabelling of the signal leaves it untouched."""
    groups = collections.OrderedDict()
    for c, ok in sorted(pairs, key=lambda x: x[0]):
        groups.setdefault(c, []).append(ok)
    target = max(MIN_BIN, math.ceil(len(pairs) / K))
    out, cur = [], []
    for c, oks in groups.items():
        cur.extend(oks)
        if len(cur) >= target:
            out.append(cur)
            cur = []
    if cur:
        if out and len(cur) < MIN_BIN:
            out[-1].extend(cur)          # merge a short tail bin upward
        else:
            out.append(cur)
    return out


def V_from_bins(bs):
    """V = E_s[(1-2q(s))^+], plus its decomposition into mass below 1/2 and mean shortfall.

    Returns (V per question, mass m, mean shortfall d, n bins used, min bin size)."""
    n = sum(len(b) for b in bs)
    tot, below_n, below_sum = 0.0, 0, 0.0
    for b in bs:
        q = sum(b) / len(b)
        gap = 1 - 2 * q
        if gap > 0:
            tot += gap * len(b)
            below_n += len(b)
            below_sum += gap * len(b)
    V = tot / n
    m = below_n / n
    d = (below_sum / below_n) if below_n else 0.0
    return V, m, d, len(bs), min(len(b) for b in bs)


def V_cell(pairs, K):
    return V_from_bins(bins_by_rank(pairs, K))


def V_null(pairs, K, reps=400, seed=0):
    """The same estimator on shuffled labels: what a signal carrying NO information scores.

    The plug-in is upward biased (Jensen: E max(0, noise) > 0), and this measures the bias in place."""
    rnd = random.Random(seed)
    oks = [ok for _, ok in pairs]
    cs = [c for c, _ in pairs]
    vals = []
    for _ in range(reps):
        rnd.shuffle(oks)
        vals.append(V_cell(list(zip(cs, oks)), K)[0])
    return st.mean(vals)


# ---------------------------------------------------------------- the measurement (F9's estimator)
def day_scores(seq, bar):
    per = collections.defaultdict(int)
    for day, conf, ok in seq:
        per[day] += 0 if conf <= bar else (1 if ok else -1)
    return per


def window_score_hh(seq, bar, days):
    per = day_scores(seq, bar)
    present = [d for d in days if d in per]
    return (sum(per[d] for d in present) / len(present)) if present else None


def candidate_bars(by_hh):
    vals = sorted({round(c, 3) for seq in by_hh.values() for _, c, _ in seq})
    if not vals:
        return [-1.0]
    step = max(1, len(vals) // 60)
    return [-1.0] + vals[::step]


def measured_gain(by_hh, days):
    """F9's number, reproduced, and its per-household parts (one shared bar, chosen with hindsight)."""
    bars = candidate_bars(by_hh)

    def mean_at(b):
        v = [window_score_hh(s, b, days) for s in by_hh.values()]
        v = [x for x in v if x is not None]
        return st.mean(v) if v else -99
    best_bar = max(bars, key=mean_at)
    per_hh = {h: window_score_hh(s, best_bar, days) - window_score_hh(s, -1.0, days)
              for h, s in by_hh.items()}
    return best_bar, mean_at(best_bar) - mean_at(-1.0), per_hh


def measured_gain_own_bar(by_hh, days):
    """Like-for-like with the formula: each HOUSEHOLD gets its own hindsight threshold."""
    per_hh = {}
    for h, s in by_hh.items():
        bars = candidate_bars({h: s})
        forced = window_score_hh(s, -1.0, days)
        best = max(window_score_hh(s, b, days) for b in bars)
        per_hh[h] = best - forced
    return per_hh


def mse(v):
    v = [x for x in v if x is not None]
    if not v:
        return None, None, 0
    return st.mean(v), (st.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else 0.0), len(v)


def fmt(m, s, n=None):
    if m is None:
        return "  --  "
    return f"{m:+5.2f} ± {s:4.2f}" + (f" ({n})" if n else "")


# ---------------------------------------------------------------- report
def main():
    rows = load()
    per_day_q = {}
    for m, by_hh in rows.items():
        cnt = [len([1 for d, _, _ in s if d == dd]) for s in by_hh.values() for dd in range(1, 32)]
        per_day_q[m] = st.mean([c for c in cnt if c])
    print("questions per day per household (mean over hh-days, households differ):",
          {NAME[m]: round(v, 2) for m, v in per_day_q.items()})
    print()

    K = 4
    out = {}
    print("=" * 118)
    print(f"TABLE 1  predicted V (per question and per day) vs measured F9 gain. rank bins K={K}, "
          f"mean ± se over households")
    print("=" * 118)
    hdr = f"{'method':22s} {'window':13s} {'n_hh':>4} {'V/question':>16} {'V/day pred':>16} " \
          f"{'V/day null':>12} {'V/day corr':>16} {'F9 measured':>12} {'own-bar meas':>16}"
    print(hdr)
    for m in ORDER:
        by_hh = rows[m]
        for wn, days in WINDOWS.items():
            cells = {h: cell(by_hh, h, days) for h in by_hh}
            cells = {h: p for h, p in cells.items() if len(p) >= MIN_CELL}
            if not cells:
                continue
            Q = {h: qpd(by_hh, h, days) for h in cells}
            Vs = {h: V_cell(p, K) for h, p in cells.items()}
            nulls = {h: V_null(p, K, seed=hash(h) % 1000) for h, p in cells.items()}
            vq = mse([Vs[h][0] for h in cells])
            vd = mse([Vs[h][0] * Q[h] for h in cells])
            vn = mse([nulls[h] * Q[h] for h in cells])
            vc = mse([(Vs[h][0] - nulls[h]) * Q[h] for h in cells])
            bar, gain, per_hh = measured_gain(by_hh, days)
            gm = mse([per_hh[h] for h in cells])
            own = mse(list(measured_gain_own_bar(by_hh, days).values()))
            mm = mse([Vs[h][1] for h in cells])
            dd = mse([Vs[h][2] for h in cells])
            nb = mse([float(Vs[h][3]) for h in cells])
            mb = min(Vs[h][4] for h in cells)
            out[(m, wn)] = dict(vq=vq, vd=vd, vn=vn, vc=vc, meas=gm, own=own, mass=mm, short=dd,
                                bar=bar, nb=nb, minbin=mb, n=len(cells), qpd=st.mean(list(Q.values())),
                                nq=st.mean([len(p) for p in cells.values()]))
            print(f"{NAME[m]:22s} {wn:13s} {len(cells):>4} {fmt(*vq):>16} {fmt(*vd):>16} "
                  f"{fmt(*vn):>12} {fmt(*vc):>16} {gain:>+12.2f} {fmt(*own):>16}")
        print()

    print("=" * 110)
    print("TABLE 2  decomposition  V = m * d   (m = mass with q(s) < 1/2, d = mean shortfall 1-2q there)")
    print("=" * 110)
    print(f"{'method':22s} {'window':13s} {'mass m':>16} {'shortfall d':>16} {'m*d /question':>16} "
          f"{'m*d /day':>12} {'bins':>6} {'min bin':>8} {'n q/cell':>9}")
    for m in ORDER:
        for wn in WINDOWS:
            o = out.get((m, wn))
            if not o:
                continue
            md = o["mass"][0] * o["short"][0]
            print(f"{NAME[m]:22s} {wn:13s} {fmt(*o['mass']):>16} {fmt(*o['short']):>16} "
                  f"{md:>16.3f} {md*o['qpd']:>12.2f} {o['nb'][0]:>6.1f} {o['minbin']:>8} "
                  f"{o['nq']:>9.0f}")
        print()

    print("=" * 104)
    print("TABLE 3  binning sensitivity: V per day, rank bins with K = 2,3,4,6,8 (mean over households)")
    print("=" * 104)
    print(f"{'method':22s} {'window':13s} " + "".join(f"{'K='+str(k):>10}" for k in (2, 3, 4, 6, 8))
          + f"{'  fixed-width 0.1':>18}{'  fixed-width 0.2':>18}")
    for m in ORDER:
        for wn, days in WINDOWS.items():
            by_hh = rows[m]
            cells = {h: cell(by_hh, h, days) for h in by_hh}
            cells = {h: p for h, p in cells.items() if len(p) >= MIN_CELL}
            if not cells:
                continue
            Q = {h: qpd(by_hh, h, days) for h in cells}
            line = ""
            for k in (2, 3, 4, 6, 8):
                line += f"{st.mean([V_cell(p, k)[0]*Q[h] for h, p in cells.items()]):>10.2f}"
            for w in (0.1, 0.2):
                vals = []
                for h, p in cells.items():
                    g = collections.defaultdict(list)
                    for c, ok in p:
                        g[min(int(c / w), int(1 / w))].append(ok)
                    bs = [b for b in g.values() if len(b) >= MIN_BIN]
                    # short bins merged into their nearest kept neighbour keeps the mass honest
                    short = [b for b in g.values() if len(b) < MIN_BIN]
                    if bs:
                        for b in short:
                            bs[min(range(len(bs)), key=lambda i: len(bs[i]))].extend(b)
                    else:
                        bs = [sum(g.values(), [])]
                    vals.append(V_from_bins(bs)[0])
                line += f"{st.mean([v*Q[h] for v, h in zip(vals, cells)]):>18.2f}"
            print(f"{NAME[m]:22s} {wn:13s} " + line)
        print()

    print("=" * 96)
    print("TABLE 4  invariance: V per day under relabellings of the confidence signal")
    print("  monotone  s -> s^3   and  s -> (s+3)/(s+4)   |   non-monotone  s -> |s-0.5|")
    print("  ECE = |mean confidence - accuracy| in the window, to show the LEVEL moves when V does not")
    print("=" * 96)
    print(f"{'method':22s} {'window':13s} {'V raw':>8} {'V s^3':>8} {'V mob':>8} {'V |s-.5|':>10} "
          f"{'ECE raw':>9} {'ECE s^3':>9} {'ECE mob':>9}")
    for m in ORDER:
        by_hh = rows[m]
        for wn, days in WINDOWS.items():
            cells = {h: cell(by_hh, h, days) for h in by_hh}
            cells = {h: p for h, p in cells.items() if len(p) >= MIN_CELL}
            if not cells:
                continue
            Q = {h: qpd(by_hh, h, days) for h in cells}
            def V_of(f):
                return st.mean([V_cell([(f(c), ok) for c, ok in p], K)[0] * Q[h]
                                for h, p in cells.items()])
            def ece_of(f):
                return st.mean([abs(st.mean([f(c) for c, _ in p]) - st.mean([1.0 if ok else 0.0 for _, ok in p]))
                                for p in cells.values()])
            print(f"{NAME[m]:22s} {wn:13s} {V_of(lambda c: c):>8.3f} {V_of(lambda c: c**3):>8.3f} "
                  f"{V_of(lambda c: (c+3)/(c+4)):>8.3f} {V_of(lambda c: abs(c-0.5)):>10.3f} "
                  f"{ece_of(lambda c: c):>9.3f} {ece_of(lambda c: c**3):>9.3f} "
                  f"{ece_of(lambda c: (c+3)/(c+4)):>9.3f}")
        print()

    print("=" * 80)
    print("TABLE 5  context: forced accuracy and the marginal mass below 1/2 (accuracy, not q(s))")
    print("=" * 80)
    print(f"{'method':22s} {'window':13s} {'accuracy %':>16} {'forced score/day':>18}")
    for m in ORDER:
        by_hh = rows[m]
        for wn, days in WINDOWS.items():
            cells = {h: cell(by_hh, h, days) for h in by_hh}
            cells = {h: p for h, p in cells.items() if len(p) >= MIN_CELL}
            if not cells:
                continue
            acc = mse([100 * sum(1 for _, ok in p if ok) / len(p) for p in cells.values()])
            forced = mse([window_score_hh(by_hh[h], -1.0, days) for h in cells])
            print(f"{NAME[m]:22s} {wn:13s} {fmt(*acc):>16} {fmt(*forced):>18}")
        print()

    print("=" * 104)
    print("TABLE 6  the MEASURED estimator against its own null: F9's gain when the correctness labels are")
    print("  shuffled inside each household-window (200 draws). A hindsight threshold on a signal carrying")
    print("  no information still scores above zero; this is how much.")
    print("=" * 104)
    print(f"{'method':22s} {'window':13s} {'F9 gain':>9} {'null mean':>10} {'null p95':>9} {'p-value':>9} "
          f"{'own-bar':>9} {'own null':>9} {'own p95':>9} {'p-value':>9}")
    REPS = 200
    for m in ORDER:
        by_hh = rows[m]
        for wn, days in WINDOWS.items():
            _, gain, _ = measured_gain(by_hh, days)
            own = st.mean(list(measured_gain_own_bar(by_hh, days).values()))
            rnd = random.Random(12345)
            nulls, onulls = [], []
            for _ in range(REPS):
                sh = {}
                for h, seq in by_hh.items():
                    inw = [i for i, (d, _, _) in enumerate(seq) if d in days]
                    oks = [seq[i][2] for i in inw]
                    rnd.shuffle(oks)
                    q = list(seq)
                    for i, ok in zip(inw, oks):
                        q[i] = (q[i][0], q[i][1], ok)
                    sh[h] = q
                nulls.append(measured_gain(sh, days)[1])
                onulls.append(st.mean(list(measured_gain_own_bar(sh, days).values())))
            nulls.sort(); onulls.sort()
            pv = sum(1 for v in nulls if v >= gain) / REPS
            opv = sum(1 for v in onulls if v >= own) / REPS
            print(f"{NAME[m]:22s} {wn:13s} {gain:>9.2f} {st.mean(nulls):>10.2f} {nulls[int(.95*REPS)]:>9.2f} "
                  f"{pv:>9.3f} {own:>9.2f} {st.mean(onulls):>9.2f} {onulls[int(.95*REPS)]:>9.2f} {opv:>9.3f}")
        print()

    print("=" * 96)
    print("TABLE 7  only the ORDER matters: V per day when the distinct confidence values are relabelled by")
    print("  a RANDOM permutation (200 draws, same marginal confidences, same labels, order destroyed)")
    print("=" * 96)
    print(f"{'method':22s} {'window':13s} {'V raw':>9} {'V scrambled':>13} {'scrambled p95':>15} "
          f"{'label-shuffle null':>19}")
    for m in ORDER:
        by_hh = rows[m]
        for wn, days in WINDOWS.items():
            cells = {h: cell(by_hh, h, days) for h in by_hh}
            cells = {h: p for h, p in cells.items() if len(p) >= MIN_CELL}
            if not cells:
                continue
            Q = {h: qpd(by_hh, h, days) for h in cells}
            raw = st.mean([V_cell(p, K)[0] * Q[h] for h, p in cells.items()])
            rnd = random.Random(999)
            vals = []
            for _ in range(200):
                tot = []
                for h, p in cells.items():
                    vs = sorted({c for c, _ in p})
                    perm = list(vs)
                    rnd.shuffle(perm)
                    mp = dict(zip(vs, perm))
                    tot.append(V_cell([(mp[c], ok) for c, ok in p], K)[0] * Q[h])
                vals.append(st.mean(tot))
            vals.sort()
            nullv = st.mean([V_null(p, K, seed=hash(h) % 1000) * Q[h] for h, p in cells.items()])
            print(f"{NAME[m]:22s} {wn:13s} {raw:>9.2f} {st.mean(vals):>13.2f} {vals[190]:>15.2f} "
                  f"{nullv:>19.2f}")
        print()

    print("=" * 104)
    print("TABLE 8  does finer binning close the gap? corrected V per day (raw minus label-shuffle null)")
    print("  for the first sick days, by number of rank bins")
    print("=" * 104)
    print(f"{'method':22s} " + "".join(f"{'K='+str(k):>22}" for k in (2, 3, 4, 6, 8)))
    for m in ORDER:
        by_hh = rows[m]
        days = WINDOWS["sick 14-16"]
        cells = {h: cell(by_hh, h, days) for h in by_hh}
        cells = {h: p for h, p in cells.items() if len(p) >= MIN_CELL}
        Q = {h: qpd(by_hh, h, days) for h in cells}
        line = ""
        for k in (2, 3, 4, 6, 8):
            v = [(V_cell(p, k)[0] - V_null(p, k, seed=hash(h) % 1000)) * Q[h] for h, p in cells.items()]
            line += f"{fmt(*mse(v)[:2]):>22}"
        print(f"{NAME[m]:22s} " + line)
    print()

    print("=" * 112)
    print("TABLE 9  HONEST cross-fitted value of declining. The decline rule (which rank bins have q<1/2) is")
    print("  fitted on a random half of the cell and its value is measured on the other half, 200 splits.")
    print("  This estimator has null EXPECTATION ZERO, so no bias subtraction is needed; it is a lower bound")
    print("  on V (it pays for not knowing q exactly), and m, d are measured out of sample.")
    print("=" * 112)
    print(f"{'method':22s} {'window':13s} {'V/day honest':>17} {'mass m':>16} {'shortfall d':>16} "
          f"{'m*d/day':>9} {'F9 meas':>8}")
    SPL = 200
    for m in ORDER:
        by_hh = rows[m]
        for wn, days in WINDOWS.items():
            cells = {h: cell(by_hh, h, days) for h in by_hh}
            cells = {h: p for h, p in cells.items() if len(p) >= MIN_CELL}
            if not cells:
                continue
            Q = {h: qpd(by_hh, h, days) for h in cells}
            perV, perM, perD = [], [], []
            for h, pairs in cells.items():
                rnd = random.Random(7 + hash(h) % 997)
                vs, ms, ds = [], [], []
                for _ in range(SPL):
                    idx = list(range(len(pairs)))
                    rnd.shuffle(idx)
                    halves = [(idx[:len(idx) // 2], idx[len(idx) // 2:]),
                              (idx[len(idx) // 2:], idx[:len(idx) // 2])]
                    for ia, ib in halves:
                      A = [pairs[i] for i in ia]
                      B = [pairs[i] for i in ib]
                      if len(A) < 2 * MIN_BIN_CF or len(B) < MIN_BIN_CF:
                          continue
                      # bins on A, as confidence cut points, with q on each
                      bs, cuts, cur, curc = [], [], [], []
                      groups = collections.OrderedDict()
                      for c, ok in sorted(A, key=lambda x: x[0]):
                          groups.setdefault(c, []).append(ok)
                      target = max(MIN_BIN_CF, math.ceil(len(A) / K))
                      for c, oks in groups.items():
                          cur.extend(oks)
                          curc.append(c)
                          if len(cur) >= target:
                              bs.append(cur); cuts.append(curc[-1]); cur, curc = [], []
                      if cur:
                          if bs:
                              bs[-1].extend(cur); cuts[-1] = curc[-1] if curc else cuts[-1]
                          else:
                              bs.append(cur); cuts.append(curc[-1])
                      cuts[-1] = float("inf")
                      decline = [sum(b) / len(b) < 0.5 for b in bs]
                      dec_n, dec_reg = 0, 0.0
                      for c, ok in B:
                          j = next(i for i, cut in enumerate(cuts) if c <= cut)
                          if decline[j]:
                              dec_n += 1
                              dec_reg += (-1.0 if ok else 1.0)      # avoided regret on this question
                      vs.append(dec_reg / len(B))
                      ms.append(dec_n / len(B))
                      ds.append((dec_reg / dec_n) if dec_n else 0.0)
                if vs:
                    perV.append(st.mean(vs) * Q[h]); perM.append(st.mean(ms)); perD.append(st.mean(ds))
            if not perV:
                continue
            vv, mm2, dd2 = mse(perV), mse(perM), mse(perD)
            _, gain, _ = measured_gain(by_hh, days)
            print(f"{NAME[m]:22s} {wn:13s} {fmt(*vv):>17} {fmt(*mm2):>16} {fmt(*dd2):>16} "
                  f"{mm2[0]*dd2[0]*st.mean(list(Q.values())):>9.2f} {gain:>8.2f}")
        print()


if __name__ == "__main__":
    main()
