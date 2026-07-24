"""Start-time normalization test for the day-5 hump (mechanism #4 disambiguation).

The hump is a SHARED upstream artifact (it appears in the uncurated raw digest and
in bare C3g, synchronized), so we probe it on C3g — free, no LLM. Two flavours of
#4 remain:
  (b-data) pure data-quantity / sparse-fit: the peak sits at a fixed NUMBER OF
           DAYS regardless of which weekday training starts on.
  (b-week) weekly-cycle alignment: the peak sits at a fixed CALENDAR structure
           (e.g. training covering one clean Mon-Fri block), so it MOVES when the
           start weekday moves.

Test: vary the training-window START OFFSET s in {Mo..Su}; for each, fit C3g on the
thinned observations of days [s, s+D) and evaluate on the SAME fixed test week
(days 14-20, its true weekly structure). Windows are capped so s+D <= 13 (never
touch the test). Plot accuracy vs D, one curve per start weekday.

  peak at the same D for every start weekday  -> data-quantity / sparse-fit (b-data)
  peak-D shifts with the start weekday         -> weekly-cycle alignment  (b-week)

Pooled over the expanded confirmatory pool (version22 + version22b, 24 households),
no distractors (they don't touch the per-edge classical fit).
"""
from __future__ import annotations

import json
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dynbelief.h2 import core
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.classical.filter import uniform_belief
from dynbelief.experiments.streams import true_parent_at
import dynbelief.reflect.run as R

WD = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
# Test week moved to days 21-27 (a clean Mon-Su week) so the TRAINING window can
# run out to D=14 for EVERY start offset (max s+D = 6+14 = 20 < 21, no leakage) —
# this is what lets the full peak-THEN-DECAY hump show, not just the rise.
D_GRID = [1, 2, 3, 5, 7, 10, 14]
OFFSETS = [0, 1, 2, 3, 4, 5, 6]          # start weekday of "day 0 of experience"
TEST_DAYS = list(range(21, 28))          # fixed Mon-Su test week (week 4)
_TEST_GAP = 21
OBS = ("rand", 3.0)


def _window_obs(h, s, D):
    """Thinned obs rows for calendar days [s, s+D). Per-day thinning seed is fixed,
    so shifting the window just selects different calendar days of the SAME stream."""
    R.OBS_PER_DAY = OBS
    kept = R.thinned_event_tuples(h["by_obj"], OBS, s * 1440, (s + D) * 1440)
    return [{"day": t // 1440, "t_min": t, "parents": {o: r}} for (t, o, r) in kept], kept


def _last_obs(kept, obj, t_hi):
    ev = [(t, r) for (t, o, r) in kept if o == obj and t < t_hi]
    return (ev[-1][1], ev[-1][0]) if ev else (None, None)


def curves(banks=("v22", "v22b")):
    hh_data = []
    for bk in banks:
        bank_dir, cfg, _, _ = R.bank_of(bk)
        for hh, c in cfg.items():
            hh_data.append((core.load_hh(bank_dir, hh), c["targets"]))
    # acc[offset][D] pooled over (hh, object, test_day)
    acc = {s: {} for s in OFFSETS}
    for s in OFFSETS:
        for D in D_GRID:
            if s + D > _TEST_GAP - 1:                       # never overlap the test week
                acc[s][D] = float("nan"); continue
            hits = []
            for h, targets in hh_data:
                cs = h["cand_set"]
                obs, kept = _window_obs(h, s, D)
                rm = make_arm("C3g", cs, obs)[0] if obs else None
                for (obj, hr) in targets:
                    for qd in TEST_DAYS:
                        tq = qd * 1440 + hr * 60
                        true = true_parent_at(h["by_obj"], h["init"], obj, tq)
                        if rm is None:
                            bel = uniform_belief(cs)
                        else:
                            lo = _last_obs(kept, obj, (s + D) * 1440)
                            ep = {"object": obj, "t_query": tq,
                                  "last_obs": lo[0], "last_obs_t": lo[1]}
                            bel = _belief(rm, cs, obj, tq, ep, "categorical")
                        pred = _rows_fields(bel, cs, None)[0]
                        hits.append(int(pred == true))
            acc[s][D] = float(np.mean(hits))
        print(f"start {WD[s % 7]} (offset {s}): "
              + "  ".join(f"D{D}:{acc[s][D]:.2f}" for D in D_GRID if acc[s][D] == acc[s][D]),
              flush=True)
    return acc


def main():
    acc = curves()
    # peak-D per start weekday
    print("\npeak-D by start weekday:")
    for s in OFFSETS:
        vals = [(D, acc[s][D]) for D in D_GRID if acc[s][D] == acc[s][D]]
        pk = max(vals, key=lambda kv: kv[1])[0]
        print(f"  start {WD[s % 7]}: peak @ D={pk}")
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    cmap = plt.cm.viridis(np.linspace(0, 0.92, len(OFFSETS)))
    for s, col in zip(OFFSETS, cmap):
        xs = [D for D in D_GRID if acc[s][D] == acc[s][D]]
        ys = [acc[s][D] for D in xs]
        ax.plot(xs, ys, "-o", color=col, ms=5, lw=2, label=f"start {WD[s % 7]}")
    ax.set_xlabel("days of experience D (training window = days [start, start+D))")
    ax.set_ylabel("C3g receptacle accuracy on the fixed test week")
    ax.grid(alpha=0.25); ax.legend(fontsize=8.5, title="window start weekday", ncol=2)
    ax.set_title("Start-time normalization of the hump (C3g, the shared-mechanism proxy)\n"
                 "peaks aligned at the same D -> data-quantity/sparse-fit; peaks shifting "
                 "with start weekday -> weekly-cycle alignment", fontsize=11)
    fig.tight_layout()
    out = R.OUT / "hump_startshift.png"
    fig.savefig(out, dpi=140); print("\nwrote", out)


if __name__ == "__main__":
    main()
