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


def main():
    rows = load()
    if not rows:
        print("no rows yet")
        return 1
    hh = sorted({r["household"] for r in rows})
    days = sorted({r["day_index"] for r in rows})
    print(f"{len(rows)} rows, {len(hh)} households, days {min(days)}-{max(days)}")

    NH = len({r["household"] for r in rows})
    acc = per_day(rows, "correct", n_hh=NH)
    agr = per_day(rows, "agreement", n_hh=NH)
    post = [r for r in rows if not r["_warm"]]
    lac = per_day(post, "lac_size", n_hh=NH)
    aps = per_day(post, "aps_size", n_hh=NH)
    cov = per_day(post, "lac_covered", n_hh=NH)
    covA = per_day(post, "aps_covered", n_hh=NH)
    n_by = collections.Counter(r["day_index"] for r in rows)

    lead_a = [acc[d] for d in LEAD if d in acc]
    lead_g = [agr[d] for d in LEAD if d in agr]
    # While the run is still inside the settled fortnight there is no baseline to divide by, so fall back to raw
    # values and say so on the chart rather than refusing to draw - this script is called repeatedly in flight.
    normalised = bool(lead_a and lead_g)
    ba, bg = (st.mean(lead_a), st.mean(lead_g)) if normalised else (1.0, 1.0)

    fig, ax = plt.subplots(2, 1, figsize=(11, 7.2), sharex=True,
                           gridspec_kw={"height_ratios": [1, 1.15]})
    maxd = max(days)
    warm_last = max((r["day_index"] for r in rows if r["_warm"]), default=0)
    SHIFT_DAY = 14
    for A in ax:
        if warm_last:
            A.axvspan(0.5, warm_last + .5, color="#b0b0b0", alpha=.22, lw=0)
        # only shade a stage the data has actually reached - with maxd < 13.5 the old call drew the span
        # BACKWARDS, colouring settled days 9-13 as if the resident were already ill.
        if maxd > 13.5:
            A.axvspan(13.5, min(23.5, maxd + .5), color="#f0c987", alpha=.45, lw=0)
        if maxd > 23.5:
            A.axvspan(23.5, maxd + .5, color="#bcdcc8", alpha=.45, lw=0)
        A.grid(alpha=.25)
        if maxd >= SHIFT_DAY:
            A.axvline(SHIFT_DAY, color="#c0392b", lw=1.4, ls="-", alpha=.85, zorder=5)

    d1 = sorted(acc)
    ax[0].axhline(1.0, color="#888", ls=":", lw=1)
    ax[0].plot(d1, [acc[d] / ba for d in d1], "o-", color="#2a78d6", lw=2.5, ms=5, label="accuracy")
    g1 = sorted(agr)
    ax[0].plot(g1, [agr[d] / bg for d in g1], "s--", color="#c0392b", lw=2, ms=5,
               label=f"agreement over k={rows[0]['k']} samples")
    ax[0].set_ylabel("relative to the settled week" if normalised else "raw value (0-1)")
    ax[0].set_title("If the uncertainty signal worked, the red line would fall when the blue one does" if normalised
                    else "Settled week not yet complete - raw values, not yet normalised", fontsize=11)
    if maxd >= SHIFT_DAY:
        ax[0].annotate("day 14: the routine changes", xy=(SHIFT_DAY, ax[0].get_ylim()[0]),
                       xytext=(SHIFT_DAY + 0.6, ax[0].get_ylim()[0] + 0.04 * (ax[0].get_ylim()[1] - ax[0].get_ylim()[0])),
                       fontsize=9, color="#c0392b")
    ax[0].legend(fontsize=9, loc="lower left")

    d2 = sorted(lac)
    if not d2:
        ax[1].text(0.5, 0.5, "conformal sets appear once a day clears the threshold warm-up",
                   transform=ax[1].transAxes, ha="center", fontsize=10, color="#777")
    ax[1].plot(d2, [lac[d] for d in d2], "o-", color="#199e70", lw=2.2, ms=4.5, label="conformal set size (LAC)")
    # APS is off the page by request (22 Sept). The fix and the offline replay stay in the code and the notes,
    # because the empty-set bug is worth having recorded, but LAC alone is what the figure shows.
    if False:
        d3 = sorted(aps)
        ax[1].plot(d3, [aps[d] for d in d3], "^--", color="#7a3aa7", lw=1.8, ms=4.5, alpha=.85,
                   label="conformal set size (APS)")
    ax[1].set_ylabel("places the robot must name")
    ax[1].set_xlabel("day")
    ax[1].legend(fontsize=8.5, loc="upper left", framealpha=.9)
    d4 = sorted(cov)
    if d4:                       # nothing to draw until a day clears both the warm-up and the 10-answer rule
        ax2 = ax[1].twinx()
        ax2.plot(d4, [100 * cov[d] for d in d4], "s:", color="#888", lw=1.6, ms=4, label="coverage (LAC)")
        ax2.axhline(90, color="#333", ls="--", lw=1.3)
        ax2.set_ylabel("% of the time the truth was in the set", color="#555")
        ax2.set_ylim(40, 103)
        ax2.text(min(d4) + .2, 91.5, "90% promised", fontsize=8, color="#333")

    # Partial state is stamped ON the chart, not only in a note: a live figure that looks finished is a trap, and
    # early in a run every day is thin, so an unmasked partial line shows a shape that is pure noise.
    import subprocess, time as _t
    try:
        live = int(subprocess.run(["bash", "-c", "ps -eo cmd | grep -c \'[u]q_llm_samples\'"],
                                  capture_output=True, text=True).stdout.strip() or 0)
    except Exception:
        live = 0
    thin = [d for d in days if n_by[d] < MIN_N]
    pct = 100 * len(rows) / 1488.0
    banner = (f"IN PROGRESS \u2014 {len(rows)} of ~1488 questions ({pct:.0f}%), days 1\u2013{max(days)} of 31, "
              f"{len(hh)} households, {live} arm{'s' if live != 1 else ''} still running"
              if live else
              f"COMPLETE \u2014 {len(rows)} questions, days {min(days)}\u2013{max(days)}, {len(hh)} households")
    fig.text(0.5, 0.945, banner, ha="center", fontsize=10, weight="bold",
             color="#8a5a00" if live else "#199e70",
             bbox=dict(boxstyle="round,pad=0.35", fc="#fdf3dd" if live else "#e8f5ee",
                       ec="#d9a441" if live else "#199e70", lw=1))
    note = f"rebuilt {_t.strftime('%H:%M')}; grey band = the threshold's warm-up, where coverage is not yet meaningful"
    if thin:
        note += f"; days blanked unless all {len(hh)} households have reached them"
    note += f"; first {WARMUP} questions per household excluded from the set-size panel (threshold warm-up)"
    fig.suptitle("Long-context memory, no message, sampled 10 times per question: does its uncertainty notice?",
                 fontsize=12.5)
    fig.text(0.5, 0.005, note, ha="center", fontsize=8.5, color="#666")
    fig.tight_layout(rect=(0, 0.02, 1, 0.93))
    out = os.path.join(ROOT, "samples_uncertainty.png")
    fig.savefig(out, dpi=125)
    print("wrote", out)

    # numbers for the write-up, printed so they are never typed by hand
    sick = [d for d in (14, 15, 16) if d in acc]
    if sick and normalised:
        sa = st.mean(acc[d] for d in sick)
        sg = st.mean(agr[d] for d in sick)
        print(f"  settled: accuracy {100*ba:.0f}%  agreement {bg:.2f}")
        print(f"  days 14-16: accuracy {100*sa:.0f}%  agreement {sg:.2f}")
        print(f"  CHANGE: accuracy {100*(sa-ba):+.0f} points, agreement {sg-bg:+.2f}")
    if lac and sick:
        ls = [lac[d] for d in LEAD if d in lac]
        ss = [lac[d] for d in sick if d in lac]
        if ls and ss:
            print(f"  LAC set size: settled {st.mean(ls):.2f} -> days 14-16 {st.mean(ss):.2f} "
                  f"({st.mean(ss)/st.mean(ls):.2f}x)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
