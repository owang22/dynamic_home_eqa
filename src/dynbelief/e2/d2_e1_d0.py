"""D2 — E1 at D=0 on typ vs atyp banks. Prior quality measured END-TO-END,
no injection anywhere.

At D=0 the model has NO household observations, so its prediction is pure prior
(charter/profile-text OFF => the profile prose is never shown either). The
typ-vs-atyp accuracy GAP at D=0 is therefore a clean, filter-free readout of how
well a model's population-typical prior transfers to an atypical household.

We add a capability axis: gpt-5.5 (existing typ curve, results/e1) is the
frontier reference on typ; a local OpenAI-compatible endpoint (DeepSeek-V4-Flash
here) is run fresh on BOTH banks to get the full typ-vs-atyp gap for a second
capability tier. NEVER Claude.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import defaultdict

import numpy as np

from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief.experiments.e1 import run_streams_llm

OUT = REPO_ROOT / "results" / "e1"


def _acc(rows, bank, held=None, moved=None):
    sel = [r for r in rows if r["bank"] == bank
           and (held is None or r["held_out"] == held)
           and (moved is None or r["moved_since_obs"] == moved)]
    if not sel:
        return None, 0
    return float(np.mean([r["correct"] for r in sel])), len(sel)


def report(rows_by_model: dict[str, list[dict]]) -> None:
    print("\n" + "=" * 76)
    print("D2 — E1 accuracy at D=0 (pure prior): typ_v1 vs atyp_v2")
    print("=" * 76)
    print(f"\n{'model':22s} {'typ acc':>9} {'atyp acc':>9} {'gap':>7}   {'n/bank':>7}")
    print("-" * 62)
    for model, rows in rows_by_model.items():
        d0 = [r for r in rows if r["history_days"] == 0 and r.get("profile_text") in (False, None)]
        t, nt = _acc(d0, "typ_v1")
        a, na = _acc(d0, "atyp_v2")
        if t is None and a is None:
            continue
        gap = (t - a) if (t is not None and a is not None) else float("nan")
        ts = f"{t:.3f}" if t is not None else "  -  "
        as_ = f"{a:.3f}" if a is not None else "  -  "
        gs = f"{gap:+.3f}" if not np.isnan(gap) else "  -  "
        print(f"{model:22s} {ts:>9} {as_:>9} {gs:>7}   {nt or na:>7}")
    # held-out only (the transfer-critical slice) for models with both banks
    print("\nHeld-out objects only (no instance ever observed -> hardest prior transfer):")
    print(f"{'model':22s} {'typ':>9} {'atyp':>9} {'gap':>7}")
    print("-" * 52)
    for model, rows in rows_by_model.items():
        d0 = [r for r in rows if r["history_days"] == 0 and r.get("profile_text") in (False, None)]
        t, _ = _acc(d0, "typ_v1", held=True)
        a, _ = _acc(d0, "atyp_v2", held=True)
        if t is None:
            continue
        gs = f"{(t-a):+.3f}" if a is not None else "  -  "
        as_ = f"{a:.3f}" if a is not None else "  -  "
        print(f"{model:22s} {t:>9.3f} {as_:>9} {gs:>7}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", default="deepseek-v4-flash")
    ap.add_argument("--no-live", action="store_true", help="report from cached rows only")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    rows_by_model: dict[str, list[dict]] = {}

    # gpt-5.5: existing E1 rows (typ curve; contains D=0)
    gpt = OUT / "rows_classical_grid_gpt-5.5.jsonl"
    if gpt.exists():
        rows_by_model["gpt-5.5"] = [json.loads(l) for l in gpt.read_text().splitlines() if l.strip()]

    # live endpoint (DeepSeek): run E1 at D=0 only, charter OFF, both banks
    if not args.no_live:
        from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient
        client = OpenAIHTTPClient(args.endpoint, args.model)
        # SAME stream-episode method gpt-5.5 used (apples-to-apples), D=0 only,
        # n_per_cell=8 => matches gpt-5.5's 48 D=0 rows/bank.
        rows = run_streams_llm(
            client, REPO_ROOT / "banks", REPO_ROOT / "profiles" / "manual",
            banks=("typ_v1", "atyp_v2"), d_grid=(0,),
            streams=("natural", "moved_enriched"), n_per_cell=8)
        outf = OUT / f"rows_D0_{args.label}.jsonl"
        outf.write_text("".join(json.dumps(r) + "\n" for r in rows))
        print(f"[d2] wrote {len(rows)} rows -> {outf}")
        rows_by_model[args.label] = rows

    report(rows_by_model)


if __name__ == "__main__":
    main()
