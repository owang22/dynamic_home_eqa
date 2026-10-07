"""E3 — regime-transfer (the sharpest test; per-edge models cannot compete).

Give the digest observations covering only a SUBSET of the deliberately-
reassigned objects (splits: 4-of-R and 8-of-R observed) plus all conventional
observations. Query the HELD-OUT reassigned objects.

  classical (per-edge): provably learns NOTHING about held-out objects from the
                        observed ones -> back-off prior only. This is the F1
                        independence property as a control.
  llm_digest:           should, if regime inference is real, generalize
                        ("bed=sofa, desk=dining -> studio conversion -> the
                        toy basket likely holds books").

Run in named and anonymized forms. Pre-registered: on held-out targets,
llm_named > llm_anon ~= classical. If llm_named ~= classical, regime transfer
failed.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from dynbelief.h2 import core
from dynbelief.experiments.streams import true_parent_at
from dynbelief.profiles.schema import default_class
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

D_HIST = 7          # a week of observations so the regime is inferable
N_Q = 4             # query times per held-out object
QH = [8, 12, 16, 20]  # query hours on day D_HIST


def _held_queries(h, held_objs, bank, hh):
    """Episodes for held-out objects at D_HIST (unobserved -> no last_obs)."""
    eps = []
    for i, obj in enumerate(sorted(held_objs)):
        for j, hr in enumerate(QH):
            t = D_HIST * 1440 + hr * 60
            true = true_parent_at(h["by_obj"], h["init"], obj, t)
            eps.append({"bank": bank, "household": hh, "stream": "heldout_reassigned",
                        "query_id": i * 10 + j, "object": obj, "t_query": t,
                        "true_receptacle": true, "moved_since_obs": None,
                        "last_obs": None, "last_obs_t": None, "held_out": True,
                        "tercile": None})
    return eps


def run(banks, endpoint, model):
    client = OpenAIHTTPClient(endpoint, model)
    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    rows = []
    for bank in banks:
        omap, rmap = core.anon_maps(bank)
        for hh in core.households(bank):
            h = core.load_hh(bank, hh)
            # reassigned set (authored) or a fixed regime-dependent subset (timing)
            if bank == "atyp_authored_v1":
                R = sorted(core.reassigned_objects(hh) & set(h["by_obj"]))
            else:  # atyp_v2 timing: use the movable, schedule-driven objects
                R = sorted([o for o in h["by_obj"] if len(h["by_obj"][o]) >= 3])
            if len(R) < 3:
                continue
            # Fixed held-out set (queried); vary how much OTHER reassigned
            # evidence the digest contains: few (1) vs much (all remaining).
            held = set(R[:2])
            evidence = R[2:]
            splits = {"few_evidence": set(evidence[:1]), "much_evidence": set(evidence)}
            for split_name, observed_reassigned in splits.items():
                # exclude from the digest: the held set AND any reassigned NOT in
                # this split's observed set (so only conventional + observed
                # reassigned appear).
                exclude = held | (set(evidence) - observed_reassigned)
                digest = core.render_history(core.history_runs(h["observations"], exclude, D_HIST))
                hist = core.hist_before(h["observations"], exclude, D_HIST)
                eps = _held_queries(h, held, bank, hh)
                if not eps:
                    continue
                # classical control (per-edge; held objects have no counts)
                for r in core.score_classical("C3", h["cand_set"], hist, eps, D_HIST):
                    r["split"] = split_name; r["arm"] = "classical"; rows.append(r)
                # llm_digest named
                for r in core.score_llm(client, digest, h["cands"], eps, D_HIST,
                                        "llm_named", pool=pool):
                    r["split"] = split_name; rows.append(r)
                # llm_digest anon
                adigest = core.anon_digest(digest, omap, rmap)
                aeps = core.anon_eps(eps, omap, rmap)
                for r in core.score_llm(client, adigest, [rmap[c] for c in h["cands"]],
                                        aeps, D_HIST, "llm_anon", pool=pool):
                    r["split"] = split_name; rows.append(r)
            print(f"[e3] {bank}/{hh} done ({len(rows)} rows)", flush=True)
    pool.shutdown()
    core.OUT.mkdir(parents=True, exist_ok=True)
    (core.OUT / "e3_rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    report(rows)


def report(rows):
    banks = sorted({r["bank"] for r in rows})
    print("\n" + "=" * 72)
    print("E3 — regime transfer to HELD-OUT reassigned objects")
    print("=" * 72)
    for bank in banks:
        print(f"\n### {bank}")
        print(f"  {'split':>8}  {'classical':>10}  {'llm_named':>10}  {'llm_anon':>10}")
        for split in sorted({r["split"] for r in rows if r["bank"] == bank}):
            def a(arm):
                v = [r["correct"] for r in rows if r["bank"] == bank
                     and r["split"] == split and r["arm"] == arm]
                return np.mean(v) if v else None
            c, n, an = a("classical"), a("llm_named"), a("llm_anon")
            print(f"  {split:>8}  {c:>10.3f}  {n:>10.3f}  {an:>10.3f}")
        # verdict
        c = np.mean([r["correct"] for r in rows if r["bank"] == bank and r["arm"] == "classical"])
        n = np.mean([r["correct"] for r in rows if r["bank"] == bank and r["arm"] == "llm_named"])
        an = np.mean([r["correct"] for r in rows if r["bank"] == bank and r["arm"] == "llm_anon"])
        if n > an + 0.05 and n > c + 0.05:
            v = "REGIME TRANSFER via world knowledge (llm_named > anon ~ classical)"
        elif n <= c + 0.05:
            v = "regime transfer FAILED (llm_named ~= classical)"
        else:
            v = "partial / in-context (named>classical but anon~named)"
        print(f"  overall: classical={c:.3f} named={n:.3f} anon={an:.3f}  ->  {v}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--banks", default="atyp_authored_v1,atyp_v2")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    if args.report_only:
        rows = [json.loads(l) for l in (core.OUT / "e3_rows.jsonl").read_text().splitlines() if l.strip()]
        report(rows)
    else:
        run(args.banks.split(","), args.endpoint, args.model)


if __name__ == "__main__":
    main()
