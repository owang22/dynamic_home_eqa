"""FreMEn spectrum inspection plots — the brief's trust-but-verify step.

One figure per household: the mean amplitude spectrum over every fitted
(object, receptacle) model, on a log-period axis. The 24 h harmonic family
should dominate; the 7-day components should carry ~no amplitude, because
HOMER+ days are independently sampled schedule variations with no weekday
structure. If a spectrum ever contradicts that, FreMEn's inputs — not its
math — are the first suspect.

    PYTHONPATH=src python -m homer.spectra
"""

from __future__ import annotations

import collections
import pathlib

import numpy as np

from homer.fremen import Fremen, MIN_PER_DAY
from homer.loader import HOUSEHOLDS, read_traces
from homer.protocol import hourly_occupancy, initial_placements

_INK, _MUTED, _GRID, _HUE = "#33322e", "#6f6d64", "#dddbd2", "#2a78d6"


def main() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = pathlib.Path("reports/homer_spectra")
    out.mkdir(parents=True, exist_ok=True)
    traces = pathlib.Path("data/homer_traces")
    for household in HOUSEHOLDS:
        h = household[-1]
        trace = read_traces(traces, h)
        train = [r for r in trace if r.split == "train"]
        occ = hourly_occupancy(train)
        model = Fremen(order=2)
        model.fit(occ, sorted({r.receptacle_id for r in trace}),
                  initial_placements(train), heldout=())
        # Full projection spectrum (not only the kept components): refit
        # amplitude at every candidate for the mean series.
        sums: collections.Counter = collections.Counter()
        n = 0
        for obj, per_rec in model._models.items():
            for rec, spec in per_rec.items():
                for period, amp in spec.spectrum():
                    sums[period] += amp
                n += 1
        periods = sorted(sums)
        amps = [sums[p] / n for p in periods]
        fig, ax = plt.subplots(figsize=(9, 3.6))
        ax.stem([p / 60 for p in periods], amps, basefmt=" ",
                linefmt=_HUE, markerfmt=" ")
        ax.set_xscale("log")
        for mark, label in ((24, "24 h"), (12, "12 h"), (168, "7 d")):
            ax.axvline(mark, color=_MUTED, linestyle=":", linewidth=1)
            ax.text(mark, ax.get_ylim()[1] * 0.95, f" {label}",
                    fontsize=8, color=_MUTED, va="top")
        ax.set_xlabel("period (hours, log scale)", color=_INK, fontsize=9)
        ax.set_ylabel("mean kept amplitude", color=_INK, fontsize=9)
        ax.set_title(f"Household{h} — FreMEn amplitude by period "
                     f"(mean over {n} object-receptacle models)",
                     loc="left", fontsize=10, color=_INK)
        ax.yaxis.grid(True, color=_GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        fig.savefig(out / f"Household{h}.png", dpi=150)
        plt.close(fig)
        top = sorted(((sums[p] / n, p) for p in periods), reverse=True)[:3]
        print(f"Household{h}: top mean-amplitude periods "
              + ", ".join(f"{p/60:.1f}h ({a:.4f})" for a, p in top))
    print(f"wrote {out}/Household*.png")


if __name__ == "__main__":
    main()
