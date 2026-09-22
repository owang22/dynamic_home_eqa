#!/usr/bin/env python3
"""Two paired questions on the story data (read-only; writes only into this directory).

A "square wave": on population person2x (two sick spells: days 14-20 and 28-34), does any method do better in the
   OPENING of the second spell (days 28-30) than in the opening of the first (days 14-16)? Paired per household.
B "indexed forever beats unindexed forever": on population person (one spell), cold accuracy in the settled lead-up
   (days 9-13) vs the late return (days 27-31), paired per household, for the never-forgets timetable, the 3-day
   timetable, the hedge, and every LLM arm.

Every window figure with fewer than MIN_N pooled answers is printed as "unusable", never as a percentage.
"""
import json, math, os, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.dirname(os.path.abspath(__file__))
MIN_N = 10

DATA = json.load(open(f"{ROOT}/story_data.json"))
EXTRA = json.load(open(f"{ROOT}/story_extra.json"))["llm_live"]

CLASSICAL = ["ttfrozen", "tt3d", "tt1d", "mf3d", "periodic", "perpetua", "lastseen", "bma"]
CLASSICAL_LABEL = {"ttfrozen": "timetable, never forgets", "tt3d": "timetable, 3-day", "tt1d": "timetable, 1-day",
                   "mf3d": "most-frequent, 3-day", "periodic": "periodic persistence", "perpetua": "perpetua*",
                   "lastseen": "last seen", "bma": "hedge over memory lengths"}
LLM = ["llm_naive_nomsg", "llm_retrieval_nomsg", "llm_longcontext_nomsg", "llm_reflect_nomsg", "llm_routine7_nomsg"]
LLM_LABEL = {"llm_naive_nomsg": "LLM recency buffer", "llm_retrieval_nomsg": "LLM retrieval",
             "llm_longcontext_nomsg": "LLM long context", "llm_reflect_nomsg": "LLM reflect",
             "llm_routine7_nomsg": "LLM routine-7"}
LABEL = dict(CLASSICAL_LABEL, **LLM_LABEL)


def cells(pop, method, hh):
    """-> {split: [per-day [n, ok, ...]]} or None if this method has no data for this household."""
    if method in CLASSICAL:
        return DATA[pop]["agents"].get(method, {}).get(hh)
    arm = EXTRA.get(pop, {}).get(method)
    return arm["cells"].get(hh) if arm else None


def households(pop, method):
    if method in CLASSICAL:
        return [h for h in DATA[pop]["hh"] if h in DATA[pop]["agents"].get(method, {})]
    arm = EXTRA.get(pop, {}).get(method)
    return sorted(arm["cells"]) if arm else []


def window(pop, method, hh, split, days):
    c = cells(pop, method, hh)
    if c is None or split not in c:
        return 0, 0
    series = c[split]
    n = sum(series[d][0] for d in days if d < len(series))
    ok = sum(series[d][1] for d in days if d < len(series))
    return n, ok


def paired(pop, method, split, days_a, days_b, min_n=MIN_N):
    """Per-household accuracy in each window and the paired difference b - a. Households are included only when
    BOTH windows have >= min_n answers for that household, so the two columns are the same set of households."""
    rows, dropped = [], []
    for hh in households(pop, method):
        na, oka = window(pop, method, hh, split, days_a)
        nb, okb = window(pop, method, hh, split, days_b)
        if na < min_n or nb < min_n:
            dropped.append((hh, na, nb))
            continue
        rows.append((hh, na, oka, nb, okb, 100 * okb / nb - 100 * oka / na))
    n = len(rows)
    if n == 0:
        return dict(n=0, rows=rows, dropped=dropped)
    diffs = [r[5] for r in rows]
    mean = statistics.mean(diffs)
    se = statistics.stdev(diffs) / math.sqrt(n) if n > 1 else float("nan")
    pool_a = (sum(r[1] for r in rows), sum(r[2] for r in rows))
    pool_b = (sum(r[3] for r in rows), sum(r[4] for r in rows))
    return dict(n=n, rows=rows, dropped=dropped, mean=mean, se=se, diffs=diffs,
                acc_a=statistics.mean(100 * r[2] / r[1] for r in rows),
                acc_b=statistics.mean(100 * r[4] / r[3] for r in rows),
                pool_a=pool_a, pool_b=pool_b,
                hh=[r[0] for r in rows])


def fmt_pct(n, ok):
    return f"{100 * ok / n:5.1f}%" if n >= MIN_N else " UNUSABLE"


def table(title, pop, methods, split, days_a, days_b, extra_days=None, extra_label=""):
    print(f"\n{title}   [population {pop}, split '{split}']")
    head = f"{'method':26s} {'n hh':>4s} {'win A':>8s} {'win B':>8s}"
    if extra_days:
        head += f" {extra_label:>9s}"
    head += f" {'B-A':>7s} {'SE':>6s} {'B-A/SE':>7s}"
    print(head)
    out = {}
    for m in methods:
        p = paired(pop, m, split, days_a, days_b)
        if p["n"] == 0:
            print(f"{LABEL[m]:26s} {'-':>4s}   no household has >= {MIN_N} answers in both windows "
                  f"(dropped: {p['dropped']})")
            continue
        line = f"{LABEL[m]:26s} {p['n']:4d} {p['acc_a']:7.1f}% {p['acc_b']:7.1f}%"
        if extra_days:
            ex = [window(pop, m, hh, split, extra_days) for hh in p["hh"]]
            exs = [100 * ok / n for n, ok in ex if n >= MIN_N]
            line += f" {statistics.mean(exs):8.1f}%" if len(exs) == len(ex) else f" {'UNUSABLE':>9s}"
        z = p["mean"] / p["se"] if p["se"] and not math.isnan(p["se"]) else float("nan")
        line += f" {p['mean']:+7.1f} {p['se']:6.1f} {z:+7.2f}"
        if p["dropped"]:
            line += "   [UNUSABLE window, dropped: " + ", ".join(f"{h} n={na}/{nb}" for h, na, nb in p["dropped"]) + "]"
        print(line)
        out[m] = p
    return out


def pooled_diff(pop, method, split, days_a, days_b, only_hh=None):
    """Supplementary question-level pooled difference with an independent-binomial SE (NOT the headline figure:
    questions inside a household are not independent). Same households in both windows by construction."""
    hs = [h for h in households(pop, method) if only_hh is None or h in only_hh]
    na = oka = nb = okb = 0
    for hh in hs:
        x = window(pop, method, hh, split, days_a); y = window(pop, method, hh, split, days_b)
        na += x[0]; oka += x[1]; nb += y[0]; okb += y[1]
    if na < MIN_N or nb < MIN_N:
        return None
    pa, pb = oka / na, okb / nb
    se = 100 * math.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb)
    return dict(n_hh=len(hs), na=na, nb=nb, a=100 * pa, b=100 * pb, diff=100 * (pb - pa), se=se)


def main():
    print("=" * 108)
    print("QUESTION A - the square wave: spell-2 opening (days 28-30) minus spell-1 opening (days 14-16), person2x")
    print("=" * 108)
    res_a = {}
    for split in ("all", "cold"):
        res_a[split] = table(f"A. paired spell-2 opening minus spell-1 opening", "person2x",
                             CLASSICAL + LLM, split, range(14, 17), range(28, 31),
                             extra_days=range(24, 28), extra_label="normal")
    LLM_HH = sorted(EXTRA["person2x"]["llm_naive_nomsg"]["cells"])
    print(f"\nA (matched): the SAME 3 households the LLM arms ran on ({', '.join(LLM_HH)}), so the classical")
    print("             and LLM columns are not comparing different household sets.")
    for split in ("all", "cold"):
        print(f"\n  [split '{split}']  {'method':26s} {'n hh':>4s} {'win A':>8s} {'win B':>8s} {'B-A':>7s} {'SE':>6s} {'B-A/SE':>7s}"
              f"   | pooled-question B-A (+/- binomial SE)")
        for m in CLASSICAL + LLM:
            p = paired("person2x", m, split, range(14, 17), range(28, 31))
            hs = [h for h in p.get("hh", []) if h in LLM_HH]
            if not hs:
                continue
            d = [dd for h, dd in zip(p["hh"], p["diffs"]) if h in LLM_HH]
            mean = statistics.mean(d); se = statistics.stdev(d) / math.sqrt(len(d)) if len(d) > 1 else float("nan")
            accs = [(window("person2x", m, h, split, range(14, 17)), window("person2x", m, h, split, range(28, 31))) for h in hs]
            a = statistics.mean(100 * x[1] / x[0] for x, _ in accs); b = statistics.mean(100 * y[1] / y[0] for _, y in accs)
            pd_ = pooled_diff("person2x", m, split, range(14, 17), range(28, 31), only_hh=LLM_HH)
            z = mean / se if se else float("nan")
            extra = f"   | {pd_['diff']:+5.1f} +/- {pd_['se']:.1f}" if pd_ else "   | unusable"
            print(f"  {'':11s}  {LABEL[m]:26s} {len(d):4d} {a:7.1f}% {b:7.1f}% {mean:+7.1f} {se:6.1f} {z:+7.2f}{extra}")
    print("\nA: per-household window sizes (spell-1 opening / spell-2 opening), confirming the same households:")
    for split in ("all", "cold"):
        for m in ("ttfrozen", "llm_naive_nomsg"):
            p = res_a[split].get(m)
            if p:
                print(f"  {split:4s} {LABEL[m]:26s} " + "  ".join(f"{h}:{na}/{nb}" for h, na, _, nb, _, _ in p["rows"]))

    print("\nper-household paired differences (spell2 - spell1, percentage points):")
    for split in ("all", "cold"):
        for m, p in res_a[split].items():
            print(f"  {split:4s} {LABEL[m]:26s} " + "  ".join(f"{h}:{d:+.0f}" for h, d in zip(p["hh"], p["diffs"])))

    print("\nA (supplementary) - 'never learn the sick routine at all': WITHIN spell 1, late (days 18-20) minus")
    print("  opening (days 14-16), paired per household. A method that learns the sick routine climbs here.")
    for split in ("all", "cold"):
        table("A-supp. within-spell-1 learning", "person2x", CLASSICAL + LLM, split, range(14, 17), range(18, 21))

    print("\n" + "=" * 108)
    print("QUESTION B - indexed forever vs unindexed forever: cold accuracy, lead-up (9-13) vs late return (27-31)")
    print("=" * 108)
    res_b = table("B. paired late return minus settled lead-up", "person",
                  ["ttfrozen", "tt3d", "bma"] + LLM, "cold", range(9, 14), range(27, 32))
    print("\nper-household paired differences (late return - lead-up, cold, percentage points):")
    for m, p in res_b.items():
        print(f"  {LABEL[m]:26s} " + "  ".join(f"{h}:{d:+.0f}" for h, d in zip(p["hh"], p["diffs"])))
    print("\npooled window totals for B (same households per row):")
    for m, p in res_b.items():
        print(f"  {LABEL[m]:26s} lead-up {p['pool_a'][1]}/{p['pool_a'][0]} = {fmt_pct(*p['pool_a'])}    "
              f"late return {p['pool_b'][1]}/{p['pool_b'][0]} = {fmt_pct(*p['pool_b'])}")

    LC_HH = sorted(EXTRA["person"]["llm_longcontext_nomsg"]["cells"])
    print(f"\nB (matched): every method restricted to the 3 households long context ran on ({', '.join(LC_HH)}).")
    print(f"  {'method':26s} {'n hh':>4s} {'lead-up':>8s} {'late':>8s} {'late-lead':>9s} {'SE':>6s}")
    for m in ["ttfrozen", "tt3d", "bma"] + LLM:
        p = res_b.get(m)
        if not p:
            continue
        d = [dd for h, dd in zip(p["hh"], p["diffs"]) if h in LC_HH]
        hs = [h for h in p["hh"] if h in LC_HH]
        if len(d) < 2:
            continue
        accs = [(window("person", m, h, "cold", range(9, 14)), window("person", m, h, "cold", range(27, 32))) for h in hs]
        a = statistics.mean(100 * x[1] / x[0] for x, _ in accs); b = statistics.mean(100 * y[1] / y[0] for _, y in accs)
        print(f"  {LABEL[m]:26s} {len(d):4d} {a:7.1f}% {b:7.1f}% {statistics.mean(d):+9.1f} "
              f"{statistics.stdev(d) / math.sqrt(len(d)):6.1f}")

    print("\nB (difference-of-differences): (late - lead) for the never-forgets timetable MINUS (late - lead) for")
    print("  each LLM arm, paired household by household. A positive number means the LLM lost MORE than the")
    print("  timetable did; this is the quantity the claim needs to be clearly above zero.")
    ttf = dict(zip(res_b["ttfrozen"]["hh"], res_b["ttfrozen"]["diffs"]))
    for m in LLM:
        p = res_b.get(m)
        if not p:
            continue
        d = [ttf[h] - dd for h, dd in zip(p["hh"], p["diffs"]) if h in ttf]
        mean = statistics.mean(d); se = statistics.stdev(d) / math.sqrt(len(d))
        print(f"  timetable-forever minus {LABEL[m]:24s} n={len(d):2d}  {mean:+6.1f} +/- {se:4.1f}  (z={mean / se:+.2f})")

    print("\nper-household window sizes (cold, person) - confirming both windows exist for the same households:")
    for m in ["ttfrozen"] + LLM:
        p = res_b.get(m)
        if p:
            print(f"  {LABEL[m]:26s} " + "  ".join(f"{h}:{na}/{nb}" for h, na, _, nb, _, _ in p["rows"]))

    json.dump({"A": {s: {m: {k: v for k, v in p.items() if k != "rows"} for m, p in res_a[s].items()} for s in res_a},
               "B": {m: {k: v for k, v in p.items() if k != "rows"} for m, p in res_b.items()}},
              open(f"{OUT}/paired.json", "w"), indent=1, default=str)
    print(f"\nwrote {OUT}/paired.json")


if __name__ == "__main__":
    main()
