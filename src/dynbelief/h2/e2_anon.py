"""E2 — anonymization control (the mechanism test).

Rerun llm_digest on the atyp banks with semantics stripped: object names ->
object_N, receptacles -> recep_M, consistent within a bank, times intact, same
episodes re-templated with the same anonymous ids.

  named >> anon  => the advantage is WORLD KNOWLEDGE (regime recognition from
                    semantics). H2 mechanism supported.
  named ~= anon  => the LLM is doing generic in-context statistics; the H2
                    mechanism claim must be DROPPED even if E1 looks good.

Named numbers are reused from E1 (identical episodes/digest); this module runs
the anonymized arm and reports the gap.
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


def run(banks, endpoint, model, n_per_cell):
    client = OpenAIHTTPClient(endpoint, model)
    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    rows = []
    for bank in banks:
        omap, rmap = core.anon_maps(bank)
        for hh in core.households(bank):
            h = core.load_hh(bank, hh)
            anon_cands = [rmap[c] for c in h["cands"]]
            for D in core.D_GRID:
                digest = core.render_history(core.history_runs(h["observations"], h["heldout"], D))
                adigest = core.anon_digest(digest, omap, rmap)
                for stream in core.E1_STREAMS:
                    eps = sample_stream(h["hd"], bank, hh, D, stream, n_per_cell)
                    if not eps:
                        continue
                    aeps = core.anon_eps(eps, omap, rmap)
                    rows += core.score_llm(client, adigest, anon_cands, aeps, D,
                                           "llm_digest_anon", pool=pool)
            print(f"[e2] {bank}/{hh} anon done ({len(rows)} rows)", flush=True)
    pool.shutdown()
    core.OUT.mkdir(parents=True, exist_ok=True)
    (core.OUT / "e2_rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    report(rows)


def _acc(rows, bank, arm, D):
    v = [r["correct"] for r in rows if r["bank"] == bank and r["arm"] == arm
         and r["history_days"] == D]
    return float(np.mean(v)) if v else None


def report(anon_rows):
    e1 = core.OUT / "e1_rows.jsonl"
    named = [json.loads(l) for l in e1.read_text().splitlines() if l.strip()] if e1.exists() else []
    banks = sorted({r["bank"] for r in anon_rows})
    print("\n" + "=" * 74)
    print("E2 — named vs anonymized llm_digest (mechanism test)")
    print("=" * 74)
    for bank in banks:
        print(f"\n### {bank}")
        print(f"  {'D':>3}  {'named':>8}  {'anon':>8}  {'gap(named-anon)':>16}")
        gaps = []
        for D in core.D_GRID:
            nmd = _acc(named, bank, "llm_digest", D)
            an = _acc(anon_rows, bank, "llm_digest_anon", D)
            if nmd is None or an is None:
                continue
            gaps.append(nmd - an)
            print(f"  {D:>3}  {nmd:>8.3f}  {an:>8.3f}  {nmd-an:>+16.3f}")
        if gaps:
            mg = np.mean(gaps)
            verdict = ("WORLD KNOWLEDGE (named >> anon)" if mg > 0.05
                       else "IN-CONTEXT STATS (named ~= anon) -> drop H2 mechanism claim"
                       if abs(mg) <= 0.05 else "anon > named (??)")
            print(f"  mean gap = {mg:+.3f}  ->  {verdict}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--banks", default="atyp_v2,atyp_authored_v1")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--n-per-cell", type=int, default=core.N_PER_CELL)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    if args.report_only:
        rows = [json.loads(l) for l in (core.OUT / "e2_rows.jsonl").read_text().splitlines() if l.strip()]
        report(rows)
    else:
        run(args.banks.split(","), args.endpoint, args.model, args.n_per_cell)


if __name__ == "__main__":
    main()
