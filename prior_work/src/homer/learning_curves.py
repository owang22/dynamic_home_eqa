"""Learning curves: accuracy on the FIXED test queries as training grows.

SUPERSEDED: produced output archived in
``superseded/homer_pilot_2026_08/``; retained for regeneration.

For each prefix size N, methods are fitted on N training days and scored
on the same fixed query set as the headline tables (hourly, all test
days). HOMER+ training days are independently sampled schedule variations
with no weekday structure (see the spectra), so which days land in a
prefix is luck; curves are therefore averaged over several seeded random
day ORDERINGS rather than read off a single chronological prefix — the
project's standing phase-averaging rule for learning curves.

E1 curves: every method, full query set. E2 curves: the two genuinely
distinct behaviours — the shared per-object fallback (all per-object
methods are identical on held-out objects by construction) and the pooled
model — scored on held-out queries, overall and on the moved-only slice
(truth != initial placement), averaged over the mask draws. Initial
placements are the TRUE day-0 arrangement regardless of prefix: they are
granted side information in the protocol, not something learned.

    PYTHONPATH=src python -m homer.learning_curves          # ~15 min
"""

from __future__ import annotations

import csv
import pathlib
import random
from typing import Dict, List, Sequence

from homer.baselines import ALL_BASELINES, Modal
from homer.fremen import Fremen
from homer.loader import HOUSEHOLDS, TraceRow, read_traces
from homer.protocol import build_queries, hourly_occupancy, \
    initial_placements

N_GRID = (1, 2, 4, 8, 16, 32, 48, 65)
N_PERMS = 3
FREMEN_ORDER = 2


def _methods():
    return [cls() for cls in ALL_BASELINES if cls.name != "uniform"] \
        + [Fremen(order=FREMEN_ORDER)]


def main() -> None:
    out_dir = pathlib.Path("results")
    traces_dir = pathlib.Path("data/homer_traces")
    import json
    masks = json.loads((traces_dir / "heldout_masks.json").read_text())
    rows: List[List[object]] = []

    for household in HOUSEHOLDS:
        h = household[-1]
        trace = read_traces(traces_dir, h)
        train = [r for r in trace if r.split == "train"]
        all_days = sorted({r.day_index for r in train})
        receptacles = sorted({r.receptacle_id for r in trace})
        initial = initial_placements(train)
        queries = build_queries(trace)
        held_sets = masks["draws"][h]

        for perm in range(N_PERMS):
            order = list(all_days)
            random.Random(1000 * perm + ord(h)).shuffle(order)
            for n in N_GRID:
                chosen = set(order[:n])
                sub = [r for r in train if r.day_index in chosen]
                occ = hourly_occupancy(sub)
                # E1: all methods, full query set.
                for method in _methods():
                    method.fit(occ, receptacles, initial, heldout=())
                    hits = 0
                    for q in queries:
                        d = method.predict(q.object_id, q.timestamp)
                        top1 = max(d, key=lambda k: d[k]) if d else None
                        hits += int(top1 == q.truth)
                    rows.append([h, "E1", method.name, perm, n, "",
                                 hits / len(queries), ""])
                # E2: fallback + pooled, held-out queries, both slices.
                for draw_idx, held in enumerate(held_sets):
                    hq = [q for q in queries if q.object_id in set(held)]
                    moved = [q for q in hq
                             if q.truth != initial.get(q.object_id)]
                    from homer.baselines import Pooled
                    for method in (Modal(), Pooled()):
                        name = ("fallback" if method.name == "modal"
                                else method.name)
                        method.fit(occ, receptacles, initial, heldout=held)
                        def acc(qs):
                            if not qs:
                                return ""
                            hits = 0
                            for q in qs:
                                d = method.predict(q.object_id, q.timestamp)
                                top1 = (max(d, key=lambda k: d[k])
                                        if d else None)
                                hits += int(top1 == q.truth)
                            return hits / len(qs)
                        rows.append([h, "E2", name, perm, n, draw_idx,
                                     acc(hq), acc(moved)])
        print(f"Household{h} done")

    with open(out_dir / "learning_curves.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["household", "protocol", "method", "perm", "n_days",
                    "draw", "accuracy", "accuracy_moved_only"])
        w.writerows(rows)
    print(f"wrote {out_dir / 'learning_curves.csv'} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
