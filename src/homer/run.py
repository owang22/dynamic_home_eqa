"""Phase 4 — run every baseline through E1 and E2, emit the tidy results.

    PYTHONPATH=src python -m homer.run --out results

All numbers downstream (tables, the report) derive from
``results/raw_results.csv``; nothing is computed anywhere else. The unit
of analysis is the HOUSEHOLD (n=3): aggregates across households are
descriptive only and the tables keep per-household columns for that
reason. For E2 the spread across held-out draws is the meaningful
variance and is reported per household.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
from typing import Dict, List, Sequence

from homer.baselines import ALL_BASELINES
from homer.fremen import Fremen
from homer.loader import HOUSEHOLDS, read_traces
from homer.protocol import Query, build_queries, hourly_occupancy, \
    initial_placements

FREMEN_ORDER = 2


def _methods():
    return [cls() for cls in ALL_BASELINES] + [Fremen(order=FREMEN_ORDER)]


def _score(method, queries: Sequence[Query]) -> List[Dict[str, object]]:
    out = []
    for q in queries:
        dist = method.predict(q.object_id, q.timestamp)
        ranked = sorted(dist.items(), key=lambda kv: -kv[1])
        top1 = ranked[0][0] if ranked else None
        top3 = {r for r, _ in ranked[:3]}
        out.append({"correct": int(top1 == q.truth),
                    "top3_correct": int(q.truth in top3),
                    "query": q})
    return out


def run(out_dir: pathlib.Path, traces_dir: pathlib.Path, seed: int) -> None:
    masks = json.loads((traces_dir / "heldout_masks.json").read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: List[List[object]] = []
    header = ["method", "household", "protocol", "held_out_set",
              "object_held_out", "day_index", "hour", "object_id",
              "truth", "correct", "top3_correct"]

    for household in HOUSEHOLDS:
        h = household[-1]
        trace = read_traces(traces_dir, h)
        train = [r for r in trace if r.split == "train"]
        occupancy = hourly_occupancy(train)
        receptacles = sorted({r.receptacle_id for r in trace})
        initial = initial_placements(train)
        queries = build_queries(trace)

        # E1: no held-out objects.
        for method in _methods():
            method.fit(occupancy, receptacles, initial, heldout=())
            for s in _score(method, queries):
                q = s["query"]
                rows.append([method.name, h, "E1", "", 0, q.day_index,
                             int(q.timestamp // 60), q.object_id, q.truth,
                             s["correct"], s["top3_correct"]])

        # E2: per held-out draw, scored on the held-out objects only —
        # the observed objects' scores are already what E1 measures.
        for draw_idx, heldout in enumerate(masks["draws"][h]):
            held = set(heldout)
            hq = [q for q in queries if q.object_id in held]
            for method in _methods():
                method.fit(occupancy, receptacles, initial, heldout=heldout)
                for s in _score(method, hq):
                    q = s["query"]
                    rows.append([method.name, h, "E2", str(draw_idx), 1,
                                 q.day_index, int(q.timestamp // 60),
                                 q.object_id, q.truth, s["correct"],
                                 s["top3_correct"]])
        print(f"Household{h}: {len(queries)} E1 queries, "
              f"{len(masks['draws'][h])} E2 draws")

    with open(out_dir / "raw_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    provenance = {"seed": seed, "mask_seed": masks["seed"], "k": masks["k"],
                  "fremen_order": FREMEN_ORDER,
                  "query_hours": "07:00-23:00 hourly",
                  "n_rows": len(rows)}
    (out_dir / "provenance.json").write_text(json.dumps(provenance, indent=2))
    print(f"wrote {out_dir / 'raw_results.csv'} ({len(rows)} rows)")


def tables(out_dir: pathlib.Path) -> str:
    """Derive the two result tables from raw_results.csv alone."""
    with open(out_dir / "raw_results.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    methods = sorted({r["method"] for r in rows})
    households = sorted({r["household"] for r in rows})

    def acc(sub, key="correct"):
        return (sum(int(r[key]) for r in sub) / len(sub)) if sub else None

    lines = ["# HOMER+ pilot results", "",
             "Unit of analysis: the household (n=3). Aggregates are "
             "descriptive; no CIs are quoted because three households "
             "cannot support them.", "",
             "## E1 — standard localization (top-1 / top-3)", "",
             "| method | " + " | ".join(f"HH-{h}" for h in households)
             + " | mean |", "|---|" + "---|" * (len(households) + 1)]
    for m in methods:
        cells, accs = [], []
        for h in households:
            sub = [r for r in rows if r["method"] == m
                   and r["household"] == h and r["protocol"] == "E1"]
            a1, a3 = acc(sub), acc(sub, "top3_correct")
            accs.append(a1)
            cells.append(f"{a1:.3f} / {a3:.3f}")
        lines.append(f"| {m} | " + " | ".join(cells)
                     + f" | {sum(accs)/len(accs):.3f} |")

    lines += ["", "## E2 — held-out object generalization (top-1, "
              "mean over draws [min–max across draws])", ""]
    lines += ["| method | " + " | ".join(f"HH-{h}" for h in households)
              + " | mean |", "|---|" + "---|" * (len(households) + 1)]
    for m in methods:
        cells, accs = [], []
        for h in households:
            per_draw = []
            draws = sorted({r["held_out_set"] for r in rows
                            if r["household"] == h and r["protocol"] == "E2"})
            for d in draws:
                sub = [r for r in rows if r["method"] == m
                       and r["household"] == h and r["protocol"] == "E2"
                       and r["held_out_set"] == d]
                per_draw.append(acc(sub))
            mean = sum(per_draw) / len(per_draw)
            accs.append(mean)
            cells.append(f"{mean:.3f} [{min(per_draw):.3f}–"
                         f"{max(per_draw):.3f}]")
        lines.append(f"| {m} | " + " | ".join(cells)
                     + f" | {sum(accs)/len(accs):.3f} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("results"))
    ap.add_argument("--traces", type=pathlib.Path,
                    default=pathlib.Path("data/homer_traces"))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    run(args.out, args.traces, args.seed)
    text = tables(args.out)
    (args.out / "tables.md").write_text(text)
    print("\n" + text)


if __name__ == "__main__":
    main()
