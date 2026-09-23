#!/usr/bin/env python3
"""PART 2. Confidence is concentration; change evidence is likelihood. Two functionals of one posterior.

    C_t = max_x p_t(x)            peakedness  ("confidence", the number used everywhere in this project)
    L_t = -log p_t(y_t)           surprise at the truth (the per-observation term a CUSUM accumulates)

Read-only on the logs; prints tables. Run from anywhere:
    python3 part2_change_evidence.py
"""
import collections
import glob
import json
import math
import os
import statistics as st

REG = "/home/oliver/robot/dynamic_home_eqa/results/confidence_shift_2026-09-20/uq/regime/sick10_owner"
# The distribution-logging classical methods. Perpetua* logs NO dist anywhere in results/ (checked), so the
# third member of F9's classical trio cannot be included here; the 24h timetable stands in its place and the
# deliverable says so.
DIRS = {"none_tt": "never-forgets timetable", "none_tt72": "3-day timetable",
        "none_tt24": "1-day timetable", "none_lastseen": "last seen"}
ORDER = ["none_tt", "none_tt72", "none_tt24", "none_lastseen"]
WINDOWS = {"settled 9-13": range(9, 14), "sick 14-16": range(14, 17), "spell 17-23": range(17, 24),
           "back 24-26": range(24, 27), "after 27-31": range(27, 32)}
FLOOR = 1e-6
MIN_CELL = 10


def load(d):
    """hh -> list of rows we need."""
    out = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(REG, d, "hh_s*_t03.jsonl"))):
        hh = os.path.basename(f).split("_t03")[0]
        for line in open(f):
            r = json.loads(line)
            dist = r["dist"]
            p_truth = max(FLOOR, float(dist.get(r["truth"], 0.0)))
            out[hh].append(dict(day=r["day_index"], obj=r["object_id"], truth=r["truth"],
                                conf=max(dist.values()), nll=-math.log(p_truth),
                                ok=bool(r["correct"]), ent=-sum(p * math.log(p) for p in dist.values() if p > 0)))
    return out


def mse(v):
    v = [x for x in v if x is not None]
    if not v:
        return None, None, 0
    return st.mean(v), (st.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else 0.0), len(v)


def fmt(t, w=15):
    m, s, n = t
    return ("  --  " if m is None else f"{m:+6.3f} ± {s:5.3f}").rjust(w)


def auc(pos, neg):
    """P(X_pos > X_neg) + 0.5 P(=), the rank statistic. 0.5 = no separation."""
    if not pos or not neg:
        return None
    allv = sorted(pos + neg)
    rank = {}
    i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1] == allv[i]:
            j += 1
        r = (i + j) / 2 + 1
        rank[allv[i]] = r
        i = j + 1
    rsum = sum(rank[v] for v in pos)
    n1, n0 = len(pos), len(neg)
    return (rsum - n1 * (n1 + 1) / 2) / (n1 * n0)


def main():
    data = {d: load(d) for d in ORDER}
    print("rows per method:", {DIRS[d]: sum(len(v) for v in h.values()) for d, h in data.items()})
    print("households:", {DIRS[d]: len(h) for d, h in data.items()})
    print()

    print("=" * 118)
    print("TABLE 13  the two functionals across the arc. Per household first, then mean ± se over households.")
    print("  C = max probability (confidence).  L = -log p(truth).  H = entropy of the same posterior.")
    print("=" * 118)
    print(f"{'method':24s} {'window':13s} {'C':>15} {'L':>15} {'H':>15} {'accuracy %':>15} {'n q/cell':>9}")
    per_window = {}
    for d in ORDER:
        for wn, days in WINDOWS.items():
            cs, ls, hs, ac, nq = [], [], [], [], []
            for hh, rows in data[d].items():
                cell = [r for r in rows if r["day"] in days]
                if len(cell) < MIN_CELL:
                    continue
                cs.append(st.mean(r["conf"] for r in cell))
                ls.append(st.mean(r["nll"] for r in cell))
                hs.append(st.mean(r["ent"] for r in cell))
                ac.append(100 * sum(1 for r in cell if r["ok"]) / len(cell))
                nq.append(len(cell))
            if not cs:
                continue
            per_window[(d, wn)] = (mse(cs), mse(ls))
            print(f"{DIRS[d]:24s} {wn:13s} {fmt(mse(cs))} {fmt(mse(ls))} {fmt(mse(hs))} "
                  f"{fmt(mse(ac))} {st.mean(nq):>9.0f}")
        print()

    print("=" * 112)
    print("TABLE 14  movement at the shift, in settled-week standard deviations of the DAILY mean.")
    print("  (mean over days 14-16 minus mean over days 9-13) / sd of the five settled daily means,")
    print("  computed per household, then averaged.")
    print("=" * 112)
    print(f"{'method':24s} {'C shift (sd)':>18} {'L shift (sd)':>18} {'ratio L/C':>12} {'n hh':>6}")
    for d in ORDER:
        cz, lz = [], []
        for hh, rows in data[d].items():
            def daily(stat, days):
                by = collections.defaultdict(list)
                for r in rows:
                    if r["day"] in days:
                        by[r["day"]].append(r[stat])
                return [st.mean(v) for _, v in sorted(by.items()) if len(v) >= 3]
            for stat, acc in (("conf", cz), ("nll", lz)):
                base = daily(stat, range(9, 14))
                sick = daily(stat, range(14, 17))
                if len(base) >= 3 and sick:
                    sd = st.stdev(base)
                    acc.append((st.mean(sick) - st.mean(base)) / sd if sd > 1e-9 else None)
        c, l = mse(cz), mse(lz)
        ratio = abs(l[0] / c[0]) if (c[0] and abs(c[0]) > 1e-9) else float("inf")
        print(f"{DIRS[d]:24s} {fmt(c, 18)} {fmt(l, 18)} {ratio:>12.1f} {c[2]:>6}")
    print()

    print("=" * 112)
    print("TABLE 15  separation: AUC for 'the regime has changed', days 14-16 against days 9-13.")
    print("  Question level inside a household, then mean ± se over households. 0.5 = no separation.")
    print("  C is scored in BOTH directions because the formalisation does not say which way it would go.")
    print("=" * 112)
    print(f"{'method':24s} {'AUC of C':>16} {'AUC of -C':>16} {'AUC of L':>16} {'AUC of H':>16} {'n hh':>6}")
    for d in ORDER:
        ac, al, ah = [], [], []
        for hh, rows in data[d].items():
            pos = [r for r in rows if 14 <= r["day"] <= 16]
            neg = [r for r in rows if 9 <= r["day"] <= 13]
            if len(pos) < MIN_CELL or len(neg) < MIN_CELL:
                continue
            ac.append(auc([r["conf"] for r in pos], [r["conf"] for r in neg]))
            al.append(auc([r["nll"] for r in pos], [r["nll"] for r in neg]))
            ah.append(auc([r["ent"] for r in pos], [r["ent"] for r in neg]))
        c, l, h = mse(ac), mse(al), mse(ah)
        cneg = mse([1 - x for x in ac])
        print(f"{DIRS[d]:24s} {fmt(c, 16)} {fmt(cneg, 16)} {fmt(l, 16)} {fmt(h, 16)} {c[2]:>6}")
    print()

    print("=" * 118)
    print("TABLE 16  THE SHARP PREDICTION. Inside days 14-16, is confidence HIGHER on the objects that moved?")
    print("  'moved' = the object's truth differs from its own modal truth over days 9-13 (>=3 settled")
    print("  sightings required). Point-biserial r per household, then mean ± se.")
    print("=" * 118)
    print(f"{'method':24s} {'r(C, moved)':>16} {'C | moved':>15} {'C | stayed':>15} "
          f"{'acc | moved':>13} {'acc | stayed':>13} {'% moved':>9} {'n hh':>5}")
    for d in ORDER:
        rs, cm, cs2, am, as2, fm = [], [], [], [], [], []
        for hh, rows in data[d].items():
            mode = {}
            cnt = collections.defaultdict(collections.Counter)
            for r in rows:
                if 9 <= r["day"] <= 13:
                    cnt[r["obj"]][r["truth"]] += 1
            for o, c in cnt.items():
                if sum(c.values()) >= 3:
                    mode[o] = c.most_common(1)[0][0]
            cell = [r for r in rows if 14 <= r["day"] <= 16 and r["obj"] in mode]
            if len(cell) < MIN_CELL:
                continue
            x = [r["conf"] for r in cell]
            y = [1.0 if r["truth"] != mode[r["obj"]] else 0.0 for r in cell]
            if len(set(y)) < 2 or st.pstdev(x) < 1e-9:
                continue
            mx, my = st.mean(x), st.mean(y)
            num = sum((a - mx) * (b - my) for a, b in zip(x, y))
            den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
            rs.append(num / den if den else None)
            mv = [r for r, b in zip(cell, y) if b]
            sv = [r for r, b in zip(cell, y) if not b]
            if len(mv) >= 5 and len(sv) >= 5:
                cm.append(st.mean(r["conf"] for r in mv))
                cs2.append(st.mean(r["conf"] for r in sv))
                am.append(100 * sum(1 for r in mv if r["ok"]) / len(mv))
                as2.append(100 * sum(1 for r in sv if r["ok"]) / len(sv))
            fm.append(100 * my)
        r_, a_, b_, c_, e_, f_ = mse(rs), mse(cm), mse(cs2), mse(am), mse(as2), mse(fm)
        pct = "   --  " if f_[0] is None else f"{f_[0]:>7.1f}%"
        print(f"{DIRS[d]:24s} {fmt(r_, 16)} {fmt(a_, 15)} {fmt(b_, 15)} {fmt(c_, 13)} {fmt(e_, 13)} "
              f"{pct:>9} {r_[2]:>5}")
    print()

    print("=" * 112)
    print("TABLE 16b  the same contrast at the QUESTION level: mean C on the questions the method got right")
    print("  vs wrong, inside days 14-16 and inside the settled week. If C orders questions usefully,")
    print("  C|right > C|wrong. Per household, then mean ± se.")
    print("=" * 112)
    print(f"{'method':24s} {'window':13s} {'C | right':>15} {'C | wrong':>15} {'difference':>15} {'n hh':>6}")
    for d in ORDER:
        for wn, days in (("settled 9-13", range(9, 14)), ("sick 14-16", range(14, 17)),
                         ("back 24-26", range(24, 27))):
            r_, w_, df = [], [], []
            for hh, rows in data[d].items():
                cell = [x for x in rows if x["day"] in days]
                ok = [x["conf"] for x in cell if x["ok"]]
                no = [x["conf"] for x in cell if not x["ok"]]
                if len(ok) >= 5 and len(no) >= 5:
                    r_.append(st.mean(ok)); w_.append(st.mean(no))
                    df.append(st.mean(ok) - st.mean(no))
            if not df:
                continue
            print(f"{DIRS[d]:24s} {wn:13s} {fmt(mse(r_), 15)} {fmt(mse(w_), 15)} {fmt(mse(df), 15)} "
                  f"{mse(df)[2]:>6}")
        print()

    print("=" * 112)
    print("TABLE 17  control: is the confidence tracking REGULARITY of the settled past? r(C, settled")
    print("  truth-entropy of that object) inside days 14-16, and r(settled entropy, moved).")
    print("=" * 112)
    print(f"{'method':24s} {'r(C, regularity)':>20} {'r(regularity, moved)':>22} {'n hh':>6}")
    for d in ORDER:
        r1, r2 = [], []
        for hh, rows in data[d].items():
            cnt = collections.defaultdict(collections.Counter)
            for r in rows:
                if 9 <= r["day"] <= 13:
                    cnt[r["obj"]][r["truth"]] += 1
            reg, mode = {}, {}
            for o, c in cnt.items():
                n = sum(c.values())
                if n >= 3:
                    # regularity = 1 - normalised entropy of the settled truths: 1 means always in one place
                    h = -sum((v / n) * math.log(v / n) for v in c.values())
                    reg[o] = 1 - h / math.log(max(2, len(c)))
                    mode[o] = c.most_common(1)[0][0]
            cell = [r for r in rows if 14 <= r["day"] <= 16 and r["obj"] in reg]
            if len(cell) < MIN_CELL:
                continue

            def corr(x, y):
                if len(set(x)) < 2 or len(set(y)) < 2:
                    return None
                mx, my = st.mean(x), st.mean(y)
                den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
                return sum((a - mx) * (b - my) for a, b in zip(x, y)) / den if den else None
            xs = [reg[r["obj"]] for r in cell]
            r1.append(corr([r["conf"] for r in cell], xs))
            r2.append(corr(xs, [1.0 if r["truth"] != mode[r["obj"]] else 0.0 for r in cell]))
        print(f"{DIRS[d]:24s} {fmt(mse(r1), 20)} {fmt(mse(r2), 22)} {mse(r1)[2]:>6}")
    print()

    print("=" * 112)
    print("TABLE 18  a detector built from L: per-day mean L standardised on the settled week, and the day")
    print("  a one-sided CUSUM (drift = settled mean, threshold = 4 settled sd) first fires. Per household.")
    print("=" * 112)
    print("  C is run in BOTH directions, since C FALLS at the shift; the fair comparison is -C.")
    print(f"{'method':24s} {'L fires day':>20} {'n':>6} {'+C fires day':>20} {'n':>6} "
          f"{'-C fires day':>20} {'n':>6}")
    for d in ORDER:
        firedL, firedC, firedD, nL, nC = [], [], [], 0, 0
        for hh, rows in data[d].items():
            by = collections.defaultdict(list)
            for r in rows:
                by[r["day"]].append(r)
            base = {s: [st.mean(x[s] for x in by[dd]) for dd in range(9, 14) if len(by.get(dd, [])) >= 3]
                    for s in ("nll", "conf")}
            for s, acc, sign in (("nll", firedL, 1), ("conf", firedC, 1), ("conf", firedD, -1)):
                b = base[s]
                if len(b) < 3:
                    continue
                b = [sign * x for x in b]
                mu, sd = st.mean(b), st.stdev(b)
                if sd < 1e-9:
                    continue
                cum, day = 0.0, None
                for dd in range(14, 32):
                    if len(by.get(dd, [])) < 3:
                        continue
                    z = (sign * st.mean(x[s] for x in by[dd]) - mu) / sd
                    cum = max(0.0, cum + z)          # one-sided upward CUSUM
                    if cum > 4 and day is None:
                        day = dd
                        break
                if s == "nll":
                    nL += 1
                elif sign == 1:
                    nC += 1
                if day:
                    acc.append(day)
        print(f"{DIRS[d]:24s} {fmt(mse(firedL), 20)} {f'{len(firedL)}/{nL}':>6} "
              f"{fmt(mse(firedC), 20)} {f'{len(firedC)}/{nC}':>6} "
              f"{fmt(mse(firedD), 20)} {f'{len(firedD)}/{nC}':>6}")


if __name__ == "__main__":
    main()
