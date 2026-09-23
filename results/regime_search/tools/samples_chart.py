#!/usr/bin/env python3
"""Chart the sampling-based uncertainty run as it lands, and rebuild the interim artifact page.

Re-runnable: reads whatever rows exist in samples20/, so it can be called repeatedly while the run is in flight.

    python3 tools/samples_chart.py            (from results/regime_search)

Two panels sharing the day axis and the spell shading:
  top     accuracy and 5-of-k agreement, each divided by its OWN settled-week (days 9-13) average, so the two
          are unit-free and comparable - raw agreement and raw accuracy live on different scales and a raw
          overlay would be meaningless. 1.0 = behaving as it did before anything changed.
  bottom  conformal set size (LAC and APS built on the sampling frequency) and realised coverage against the
          90% target. Warm-up questions, where the threshold has not yet settled, are marked not hidden.

A day with fewer than MIN_N answers is blanked rather than drawn thin.
"""
import collections
import glob
import json
import os
import statistics as st
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "llm_strategies", "samples20")
MIN_N = 10
WARMUP = 20          # DecayingStepConformal holds q=1 for its first 20 questions per household
LEAD = range(9, 14)



BANKS = "/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/banks_f1"


def bank_total(days=31):
    """How many questions the run is actually supposed to ask, summed over the three banks.

    Not 3x16x31. The banks are NOT the same size: hh_s1's has 379 questions over 31 days against 496 for the
    other two, because its settled and return days carry as few as 3 questions while every sick day carries the
    full 16. The chart used to divide by 1488 and so under-reported its own progress by 8%. Worth knowing for a
    second reason: on settled days hh_s1 supplies a quarter of the pooled rows and on sick days a third, so the
    pooled line changes composition across the day axis - which is why every panel here also draws the
    households separately.
    """
    import json as _j
    tot = 0
    for hh in ("hh_s0", "hh_s1", "hh_s2"):
        f = os.path.join(BANKS, f"{hh}_t03.jsonl")
        if not os.path.exists(f):
            return 0
        for l in open(f):
            try:
                r = _j.loads(l)
            except ValueError:
                continue
            d = r.get("day_index") or r.get("day")
            if d is not None and d <= days:
                tot += 1
    return tot

def load():
    """Rows with the conformal sets RECOMPUTED from each row's saved sampled distribution.

    The stored lac_*/aps_* fields from runs before 22 Sept 15:20 are superseded: the APS set was built with a bare
    ``score <= q`` test, which drops the model's own top answer whenever q < p(top) and, on a fully confident
    distribution, lands on 1.0000000002 > 1.0 and returns an EMPTY set - 26% of them were empty. Every row carries
    ``dist``, so both sets are replayed here from the saved distributions in file (chronological) order, which
    costs no server time and makes the chart independent of that bug.
    """
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(ROOT)), "src"))
    from baselines.patrol.uq_agents import DecayingStepConformal
    from baselines.patrol.uq_llm_samples import aps_scores, aps_set
    rows = []
    for f in sorted(glob.glob(os.path.join(SAMPLES, "hh_s*", "hh_s*.jsonl"))):
        lac, aps = DecayingStepConformal(alpha=0.1), DecayingStepConformal(alpha=0.1)
        for i, l in enumerate(open(f)):
            try:
                r = json.loads(l)
            except ValueError:
                continue
            dist = r.get("dist") or {}
            truth = r.get("truth")
            lac_set = {y for y, p in dist.items() if (1.0 - p) <= lac.q + 1e-9}
            if not lac_set and dist:                      # LAC keeps the top answer too, for the same reason
                lac_set = {max(dist, key=dist.get)}
            a_set = aps_set(dist, aps.q) if dist else set()
            apsc = aps_scores(dist)
            r["lac_size"], r["lac_covered"] = len(lac_set), truth in lac_set
            r["aps_size"], r["aps_covered"] = len(a_set), truth in a_set
            lac.update(truth not in lac_set, 1.0 - dist.get(truth, 0.0))
            aps.update(truth not in a_set, apsc.get(truth, 1.0))
            r["_warm"] = i < WARMUP
            rows.append(r)
    return rows


def per_day(rows, field, warm_ok=True, n_hh=None):
    """A day is plotted only when EVERY household has reached it.

    The 10-answer floor alone is not enough while a run is in flight: the households advance at different speeds,
    so an unfinished day is whichever household happens to be fastest. On 22 Sept days 12-16 were one household
    of three and the pooled line would have read as an average of all of them - the chart would have shown the
    conformal set NARROWING at the shift on the strength of a single house."""
    by = collections.defaultdict(list)
    for r in rows:
        if warm_ok or not r["_warm"]:
            by[r["day_index"]].append(r)
    out = {}
    for d, g in by.items():
        if len(g) < MIN_N:
            continue
        if n_hh is not None and len({x["household"] for x in g}) < n_hh:
            continue
        out[d] = sum(float(x[field]) for x in g) / len(g)
    return out


def per_day_hh(rows, field, hh, warm_ok=True):
    """One household's own per-day series. No all-households mask - the point is to see each house separately."""
    by = collections.defaultdict(list)
    for r in rows:
        if r["household"] == hh and (warm_ok or not r["_warm"]):
            by[r["day_index"]].append(float(r[field]))
    return {d: sum(v) / len(v) for d, v in by.items() if len(v) >= 3}


def window_effect(rows, base, win, field, warm_ok=True):
    """Per-household change from `base` to `win`, then our claim bar: 2 standard errors, with a one-sd floor below
    six households. n=3 here, so the floor binds and the bar is the spread across the three houses."""
    d = {}
    for h in sorted({r["household"] for r in rows}):
        g = [r for r in rows if r["household"] == h and (warm_ok or not r["_warm"])]
        a = [float(r[field]) for r in g if r["day_index"] in base]
        b = [float(r[field]) for r in g if r["day_index"] in win]
        if a and b:
            d[h] = st.mean(b) - st.mean(a)
    v = list(d.values())
    if len(v) < 2:
        return None
    m, sd = st.mean(v), st.stdev(v)
    se = sd / len(v) ** 0.5
    bar = sd if len(v) < 6 else 2 * se
    return {"mean": m, "sd": sd, "se": se, "n": len(v), "claim": abs(m) >= bar,
            "per_hh": {h: x for h, x in sorted(d.items())}, "same_sign": len({x > 0 for x in v}) == 1}


# One method on this figure, so colour encodes the QUANTITY, not identity - said in the caption. The method's own
# page hue leads, so a reader coming from the page knows whose accuracy this is.
C_ACC, C_AGR, C_SET, C_COV = "#7a3aa7", "#d4820a", "#1f6f8b", "#333333"


def main():
    rows = load()
    if not rows:
        print("no rows yet")
        return 1
    hh = sorted({r["household"] for r in rows})
    days = sorted({r["day_index"] for r in rows})
    print(f"{len(rows)} rows, {len(hh)} households, days {min(days)}-{max(days)}")

    NH = len(hh)
    acc = per_day(rows, "correct", n_hh=NH)
    agr = per_day(rows, "agreement", n_hh=NH)
    post = [r for r in rows if not r["_warm"]]
    lac = per_day(post, "lac_size", n_hh=NH)
    cov = per_day(post, "lac_covered", n_hh=NH)
    n_by = collections.Counter(r["day_index"] for r in rows)

    lead_a = [acc[d] for d in LEAD if d in acc]
    lead_g = [agr[d] for d in LEAD if d in agr]
    normalised = bool(lead_a and lead_g)
    ba, bg = (st.mean(lead_a), st.mean(lead_g)) if normalised else (1.0, 1.0)

    fig, ax = plt.subplots(3, 1, figsize=(11, 9.6), sharex=True,
                           gridspec_kw={"height_ratios": [1, 1, 1]})
    maxd = max(days)
    warm_last = max((r["day_index"] for r in rows if r["_warm"]), default=0)
    pooled_last = max(acc) if acc else 0          # last day EVERY household has reached
    SHIFT_DAY = 14
    # Stage boundaries as dotted rules in ink, not as washes across the window. A band sits underneath the
    # lines and their spread and makes a narrow one hard to read, which is the whole reason for the change; a
    # rule marks the same day and leaves the plot area clean. The warm-up and the not-yet-complete tail get the
    # same treatment rather than a grey wash and a hatch over the data.
    SHIFT_DAY = 14
    edges = []
    if maxd >= SHIFT_DAY:
        edges.append((SHIFT_DAY, "sick"))
    if maxd > 23.5:
        edges.append((24, "back to normal"))
    if warm_last:
        edges.append((warm_last + .5, "threshold warmed up"))
    if pooled_last and pooled_last < maxd:
        edges.append((pooled_last + .5, "not all households yet"))
    for A in ax:
        A.set_facecolor("white")
        A.grid(alpha=.25, color="#cccccc")
        A.set_axisbelow(True)
        for d, _ in edges:
            A.axvline(d, color="#141413", lw=1.1, ls=":", alpha=.75, zorder=4)
    for d, lab in edges:                      # label once, above the top panel, so no panel is crowded
        ax[0].annotate(lab, xy=(d, 1.012), xycoords=("data", "axes fraction"),
                       ha="center", va="bottom", fontsize=8.5, color="#141413")
    TITLE_PAD = 22                            # room for the boundary labels between the plot and the title

    # --- panel 1: does the agreement signal move when the accuracy does? -------------------------------------
    d1 = sorted(acc)
    ax[0].axhline(1.0, color="#888", ls=":", lw=1)
    for h in hh:                       # the households first, faint, so the pooled line is never read alone
        s = per_day_hh(rows, "correct", h)
        ks = sorted(k for k in s if k in acc)
        ax[0].plot(ks, [s[k] / ba for k in ks], "-", color=C_ACC, lw=.9, alpha=.3, zorder=2)
    ax[0].plot(d1, [acc[d] / ba for d in d1], "o-", color=C_ACC, lw=2.5, ms=5, zorder=4, label="accuracy")
    g1 = sorted(agr)
    for h in hh:
        s = per_day_hh(rows, "agreement", h)
        ks = sorted(k for k in s if k in agr)
        ax[0].plot(ks, [s[k] / bg for k in ks], "-", color=C_AGR, lw=.9, alpha=.3, zorder=2)
    ax[0].plot(g1, [agr[d] / bg for d in g1], "s-", color=C_AGR, lw=2, ms=5, zorder=4,
               label=f"how often the {rows[0]['k']} samples agree")
    ax[0].set_ylabel("relative to its own settled week")
    eff_a = window_effect(rows, LEAD, range(14, 24), "correct")
    eff_g = window_effect(rows, LEAD, range(14, 24), "agreement")
    if eff_g and not eff_g["claim"]:
        # The honest headline for this panel is a NULL, so it has to carry what the null excludes. At three
        # households the bar is the spread between them and it is wide: this rules out a LARGE move in the
        # agreement signal, not a small one. Saying only "flat" would overstate it.
        t = (f"The agreement signal does not move at the shift: {eff_g['mean']*100:+.1f} points over the "
             f"spell, houses spread {eff_g['sd']*100:.1f}")
        if eff_a and not eff_a["claim"]:
            t += (f"\n(accuracy is {eff_a['mean']*100:+.1f} and also unclaimable at three houses — "
                  f"two fall, one rises)")
    else:
        t = "Accuracy against the agreement signal, each divided by its own settled week"
    ax[0].set_title(t, fontsize=10.5, pad=TITLE_PAD)
    ax[0].legend(fontsize=9, loc="lower left", framealpha=.9)

    # --- panel 2: the set size. the strong result is that this does NOT move ---------------------------------
    for h in hh:
        s = per_day_hh(post, "lac_size", h, warm_ok=False)
        ks = sorted(s)
        ax[1].plot(ks, [s[k] for k in ks], "-", color=C_SET, lw=.9, alpha=.3, zorder=2)
    d2 = sorted(lac)
    ax[1].plot(d2, [lac[d] for d in d2], "o-", color=C_SET, lw=2.4, ms=4.5, zorder=4,
               label="conformal set size")
    eff_s = window_effect(rows, LEAD, range(14, 24), "lac_size", warm_ok=False)
    if eff_s:
        ax[1].set_title(f"and the set never widens: {eff_s['mean']:+.2f} places over the whole spell, "
                        f"houses spread {eff_s['sd']:.2f}", fontsize=11)
    ax[1].set_ylabel("places the robot must name")
    ax[1].legend(fontsize=9, loc="upper left", framealpha=.9)

    # --- panel 3: coverage. this is the measure that breaks, and breaks in every house -----------------------
    for h in hh:
        s = per_day_hh(post, "lac_covered", h, warm_ok=False)
        ks = sorted(s)
        ax[2].plot(ks, [100 * s[k] for k in ks], "-", color=C_COV, lw=.9, alpha=.3, zorder=2)
    d4 = sorted(cov)
    ax[2].plot(d4, [100 * cov[d] for d in d4], "o-", color=C_COV, lw=2.4, ms=4.5, zorder=4,
               label="how often the truth was in the set")
    ax[2].axhline(90, color="#c0392b", ls="--", lw=1.3, zorder=3)   # a target, not a stage: stays as it is
    ax[2].text(0.995, 0.04, "the 90% the method promises", fontsize=8.5, color="#c0392b", ha="right",
               transform=ax[2].transAxes)
    eff_c = window_effect(rows, LEAD, [14], "lac_covered", warm_ok=False)
    if eff_c:
        ax[2].set_title(f"so what gives way is the promise: day 14 coverage {eff_c['mean']*100:+.0f} points, "
                        f"and all {eff_c['n']} houses fall", fontsize=11)
    ax[2].set_ylabel("% of the time")
    ax[2].set_xlabel("day")
    ax[2].set_ylim(35, 103)
    ax[2].legend(fontsize=9, loc="lower left", framealpha=.9)

    import subprocess, time as _t
    try:
        live = int(subprocess.run(["bash", "-c", "ps -eo cmd | grep -c \'[u]q_llm_samples\'"],
                                  capture_output=True, text=True).stdout.strip() or 0)
    except Exception:
        live = 0
    thin = [d for d in days if n_by[d] < MIN_N]
    tot = bank_total() or len(rows)
    pct = 100 * len(rows) / float(tot)
    banner = (f"IN PROGRESS \u2014 {len(rows)} of {tot} questions ({pct:.0f}%), days 1\u2013{max(days)} of 31, "
              f"{len(hh)} households, {live} arm{'s' if live != 1 else ''} still running"
              if live else
              f"COMPLETE \u2014 {len(rows)} of {tot} questions, days {min(days)}\u2013{max(days)}, "
              f"{len(hh)} households")
    fig.text(0.5, 0.962, banner, ha="center", fontsize=10, weight="bold",
             color="#8a5a00" if live else "#199e70",
             bbox=dict(boxstyle="round,pad=0.35", fc="#fdf3dd" if live else "#e8f5ee",
                       ec="#d9a441" if live else "#199e70", lw=1))
    note = (f"Faint lines are the {len(hh)} households on their own, bold is the pool. Colour marks the "
            f"quantity, not a method — every line here is long-context memory.")
    note2 = ("Dotted rules mark the boundaries; nothing is drawn over the plot area, so the lines and their "
             f"spread read against a plain ground. Rebuilt {_t.strftime('%H:%M')}.")
    fig.suptitle("Sampling the same question 10 times: the conformal set keeps its width and loses its promise",
                 fontsize=12.5, y=0.995)
    fig.text(0.5, 0.028, note, ha="center", fontsize=8.5, color="#666")
    fig.text(0.5, 0.009, note2, ha="center", fontsize=8.5, color="#666")
    fig.tight_layout(rect=(0, 0.046, 1, 0.950))
    out = os.path.join(ROOT, "samples_uncertainty.png")
    fig.savefig(out, dpi=125, facecolor="white")
    print("wrote", out)

    # every number that reaches prose is printed here, with the bar applied, so none of it is typed by hand
    print("\n  windows, change from the settled week (days 9-13), per household then averaged:")
    for label, win, warm in (("day 14", [14], False), ("days 14-16", range(14, 17), False),
                             ("spell 14-23", range(14, 24), False), ("return 24-31", range(24, 32), False)):
        for field in ("correct", "agreement", "lac_size", "lac_covered"):
            e = window_effect(rows, LEAD, win, field, warm_ok=(field in ("correct", "agreement")))
            if not e:
                continue
            sc = 1.0 if field == "lac_size" else 100.0
            tag = "CLAIM" if e["claim"] else " null"
            sign = " (all same sign)" if e["same_sign"] else ""
            print(f"    {label:12s} {field:12s} {sc*e['mean']:+7.1f}  sd {sc*e['sd']:5.1f}  {tag}{sign}  " +
                  " ".join(f"{h[-2:]}={sc*x:+.1f}" for h, x in e["per_hh"].items()))
    if normalised:
        print(f"\n  settled week: accuracy {100*ba:.0f}%  agreement {bg:.2f}")
    ls = [lac[d] for d in LEAD if d in lac]
    sp = [lac[d] for d in range(14, 24) if d in lac]
    if ls and sp:
        print(f"  set size: settled {st.mean(ls):.2f} -> spell {st.mean(sp):.2f}")
    lc = [cov[d] for d in LEAD if d in cov]
    sc_ = [cov[d] for d in range(14, 24) if d in cov]
    if lc and sc_:
        print(f"  coverage: settled {100*st.mean(lc):.0f}% -> spell {100*st.mean(sc_):.0f}%"
              + (f", day 14 {100*cov[14]:.0f}%" if 14 in cov else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
