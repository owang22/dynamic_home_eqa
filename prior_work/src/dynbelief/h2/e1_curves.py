"""E1 — adaptation curves: accuracy vs observation-days D for
{classical (C3 persistence+periodic), llm_digest, llm_zeroshot} x 3 banks.

llm_zeroshot is just the D=0 point of llm_digest (empty digest), so it is the
flat reference line, not a separate arm. classical and llm_digest are scored on
IDENTICAL episodes per cell (sample_stream seeded by (bank,hh,D,stream,n)).

Pre-registered signature: in atyp banks, llm_digest starts near the zero-shot
floor and CROSSES ABOVE classical at small D; in typ, both rise together.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from dynbelief.h2 import core
from dynbelief.experiments.streams import sample_stream
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient


def run(banks, endpoint, model, n_per_cell, out_name="e1_rows.jsonl"):
    client = OpenAIHTTPClient(endpoint, model)
    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    rows = []
    for bank in banks:
        for hh in core.households(bank):
            h = core.load_hh(bank, hh)
            for D in core.D_GRID:
                hist = core.hist_before(h["observations"], h["heldout"], D)
                digest = core.render_history(core.history_runs(h["observations"], h["heldout"], D))
                for stream in core.E1_STREAMS:
                    eps = sample_stream(h["hd"], bank, hh, D, stream, n_per_cell)
                    if not eps:
                        continue
                    rows += core.score_classical("C3", h["cand_set"], hist, eps, D)
                    rows += core.score_llm(client, digest, h["cands"], eps, D,
                                           "llm_digest", pool=pool)
            print(f"[e1] {bank}/{hh} done ({len(rows)} rows)", flush=True)
    pool.shutdown()
    core.OUT.mkdir(parents=True, exist_ok=True)
    (core.OUT / out_name).write_text("".join(json.dumps(r) + "\n" for r in rows))
    report(rows)
    return rows


def _acc(rows, bank, arm, D):
    v = [r["correct"] for r in rows if r["bank"] == bank and r["arm"] == arm
         and r["history_days"] == D]
    return (float(np.mean(v)), len(v)) if v else (None, 0)


def _boot_ci(rows, bank, arm, D, nb=1000, seed=0):
    sel = [r for r in rows if r["bank"] == bank and r["arm"] == arm and r["history_days"] == D]
    if not sel:
        return (None, None)
    by_obj = defaultdict(list)
    for r in sel:
        by_obj[r["object"]].append(r["correct"])
    clusters = list(by_obj.values())
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(nb):
        pick = rng.integers(0, len(clusters), len(clusters))
        vals = [x for i in pick for x in clusters[i]]
        means.append(np.mean(vals))
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def report(rows):
    banks = sorted({r["bank"] for r in rows})
    print("\n" + "=" * 78)
    print("E1 — adaptation curves: accuracy vs D (classical C3 vs llm_digest)")
    print("=" * 78)
    for bank in banks:
        print(f"\n### {bank}")
        print(f"  {'D':>3}  {'classical':>18}  {'llm_digest':>18}   winner")
        cross = None
        for D in core.D_GRID:
            c, nc = _acc(rows, bank, "C3", D)
            l, nl = _acc(rows, bank, "llm_digest", D)
            if c is None or l is None:
                continue
            cl, cu = _boot_ci(rows, bank, "C3", D)
            ll, lu = _boot_ci(rows, bank, "llm_digest", D)
            win = "llm" if l > c else ("classical" if c > l else "tie")
            if cross is None and l >= c and D > 0:
                cross = D
            print(f"  {D:>3}  {c:>6.3f} [{cl:.2f},{cu:.2f}]   {l:>6.3f} [{ll:.2f},{lu:.2f}]   {win}")
        # crossover: smallest D>0 where llm >= classical AND stays (report first)
        z0, _ = _acc(rows, bank, "llm_digest", 0)
        print(f"  zero-shot floor (D=0 llm) = {z0:.3f}   | crossover (llm>=classical) at D={cross}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--banks", default="typ_v1,atyp_v2,atyp_authored_v1")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--n-per-cell", type=int, default=core.N_PER_CELL)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    if args.report_only:
        rows = [json.loads(l) for l in (core.OUT / "e1_rows.jsonl").read_text().splitlines() if l.strip()]
        report(rows)
    else:
        run(args.banks.split(","), args.endpoint, args.model, args.n_per_cell)


if __name__ == "__main__":
    main()
