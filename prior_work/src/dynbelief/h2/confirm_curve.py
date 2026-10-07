"""ANONYMIZATION LEARNING CURVE — accuracy vs DAYS OF EVIDENCE AVAILABLE.

Why this module exists (read before comparing to confirm.py's numbers):
  confirm.py is a SINGLE-POINT confirmatory. Its digest is built once over days
  0-11 and capped at 2 sightings per diagnostic object; QUERY_DAYS only varies
  WHEN the question is asked, never how much has been seen. Accuracy against
  query day there is flat-with-noise, NOT a learning curve.

This module varies the one thing that makes a learning curve: the digest is
TRUNCATED at an evidence cutoff D and D is swept. The x-axis is therefore
"days of observation available", and every arm sees exactly the same evidence
at each D. Two deliberate departures from confirm.py, both required for a curve
and neither affecting the frozen single-point result:
  1. The 2-sighting-per-object cap is LIFTED (it bounds the frozen digest; with
     it on, evidence saturates by ~day 3 and the curve is flat by construction).
  2. QUERY_DAYS is reduced to 4 days, all >= max(CUTOFFS), so a prediction is
     never made for a time BEFORE the evidence window. Cost control + clean
     temporal ordering.
So the D=11 point here is NOT the confirmatory number and must not be reported
as one. FROZEN and shared with confirm.py: _SYS, REGIME_SCHEMA, the
"Day D, HH:MM — obj seen at rec" line format, CFG, and the anon maps.

Arms (all four share the identical truncated digest at each D):
  llm_named  — semantics + structure.
  llm_anon   — receptacle names stripped to recep_N. THE ARM OF INTEREST:
               its slope is learning with NO world knowledge.
  classical  — C3 per-edge. Flat 0 by construction (queried objects are HELD
               OUT, so there is no edge to learn); included because that flatness
               is the point — it has no transfer channel at all.
  class_freq — static population class table. Flat by construction (ignores the
               digest entirely); the honest non-learning prior baseline.

  python -m dynbelief.h2.confirm_curve --model <M> --label <L>
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from dynbelief.h2 import core
from dynbelief.h2.e5_regime import _SYS                      # FROZEN
from dynbelief.h2 import e0_baselines as e0
from dynbelief.h2.confirm import BANK, CFG, _llm_pred, _boot
from dynbelief.experiments.streams import true_parent_at
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.classical.filter import uniform_belief
from dynbelief.profiles.schema import default_class, load_profile
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

CUTOFFS = [0, 1, 2, 3, 5, 8, 11]          # days of evidence available
CURVE_QUERY_DAYS = [11, 14, 15, 18]       # all >= max(CUTOFFS): never predict the past


def _digest_upto(h, cfg, cutoff):
    """FROZEN line format; evidence restricted to days <= cutoff, cap lifted."""
    sightings = []
    for o, hr in cfg["diag"]:
        for dd in range(0, cutoff + 1):
            t = dd * 1440 + hr * 60 + 10
            rec = true_parent_at(h["by_obj"], h["init"], o, t)
            if rec != "elsewhere":
                sightings.append((t, o, rec))
    sightings.sort()
    lines = [f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — {o} seen at {rec}"
             for (t, o, rec) in sightings]
    digest = "Observations:\n" + "\n".join(lines) if lines else "(no observations)"
    by_t = defaultdict(dict)
    for (t, o, rec) in sightings:
        by_t[t][o] = rec
    hist = [{"day": t//1440, "t_min": t, "parents": p} for t, p in sorted(by_t.items())]
    return digest, hist, len(sightings)


def _queries(h, cfg, hh):
    eps = []
    for kind, key in (("target", "targets"), ("conventional", "conv")):
        for obj, hr in cfg[key]:
            for qd in CURVE_QUERY_DAYS:
                t = qd * 1440 + hr * 60
                eps.append({"bank": BANK, "household": hh, "kind": kind,
                            "object": obj, "t_query": t, "held_out": True,
                            "true_receptacle": true_parent_at(h["by_obj"], h["init"], obj, t),
                            "last_obs": None})
    return eps


def run(endpoint, model, label):
    client = OpenAIHTTPClient(endpoint, model)
    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    e0._TYP = e0.typ_class_target()
    omap, rmap = core.anon_maps(BANK)
    rows = []
    for hh in core.households(BANK):
        base = hh.split("__")[0]; cfg = CFG[base]; h = core.load_hh(BANK, hh)
        room_of = {r.id: r.room for r in load_profile(core.MANUAL_DIR / f"{base}.yaml").receptacles}
        eps = _queries(h, cfg, hh)
        acands = [rmap[c] for c in h["cands"]]
        for D in CUTOFFS:
            digest, hist, n_sight = _digest_upto(h, cfg, D)
            adigest = core.anon_digest(digest, omap, rmap)
            rm = make_arm("C3", h["cand_set"], hist)[0] if hist else None
            named = list(pool.map(lambda e: _llm_pred(client, _SYS, digest, h["cands"], e), eps))
            anon = list(pool.map(
                lambda e: _llm_pred(client, _SYS, adigest, acands,
                                    core.anon_eps([e], omap, rmap)[0]), eps))
            for k, ep in enumerate(eps):
                b = {"model": label, "bank": BANK, "household": hh, "kind": ep["kind"],
                     "object": ep["object"], "true": ep["true_receptacle"],
                     "evidence_days": D, "n_sightings": n_sight,
                     "query_day": ep["t_query"] // 1440}
                bel = (_belief(rm, h["cand_set"], ep["object"], ep["t_query"], ep, "categorical")
                       if rm else uniform_belief(h["cand_set"]))
                cam = _rows_fields(bel, h["cand_set"], ep["true_receptacle"])[0]
                cf = e0.class_freq_predict(default_class(ep["object"]), h["cand_set"], room_of)
                a_true = rmap.get(ep["true_receptacle"], ep["true_receptacle"])
                rows += [
                    {**b, "arm": "classical", "correct": int(cam == ep["true_receptacle"])},
                    {**b, "arm": "class_freq", "correct": int(cf == ep["true_receptacle"])},
                    {**b, "arm": "llm_named", "correct": int(named[k][0] == ep["true_receptacle"])},
                    # same scoring fix as confirm.py: anon predictions are recep_N,
                    # so they must be scored against the ANONYMIZED truth.
                    {**b, "arm": "llm_anon", "correct": int(anon[k][0] == a_true)},
                ]
            print(f"[curve:{label}] {hh} D={D} ({n_sight} sightings) done", flush=True)
    pool.shutdown()
    core.OUT.mkdir(parents=True, exist_ok=True)
    f = core.OUT / f"curve_rows_{label}.jsonl"
    f.write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"[curve] wrote {len(rows)} rows -> {f}")
    report(label)


def report(label):
    p = core.OUT / f"curve_rows_{label}.jsonl"
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    print(f"\n=== {label}: accuracy vs days of evidence (clustered CI by household) ===")
    print(f"{'D':>3} {'n_sight':>8} " + "".join(f"{a:>22}" for a in
          ("classical", "class_freq", "llm_named", "llm_anon")))
    for D in CUTOFFS:
        sub = [r for r in rows if r["evidence_days"] == D]
        ns = int(sum(r["n_sightings"] for r in sub if r["arm"] == "classical")
                 / max(1, sum(r["arm"] == "classical" for r in sub)))
        cells = []
        for arm in ("classical", "class_freq", "llm_named", "llm_anon"):
            by_hh = defaultdict(list)
            for r in sub:
                if r["arm"] == arm:
                    by_hh[r["household"]].append(r["correct"])
            allv = [v for vs in by_hh.values() for v in vs]
            lo, hi = _boot(by_hh)
            cells.append(f"{sum(allv)/len(allv):.3f} [{lo:.2f},{hi:.2f}]".rjust(22))
        print(f"{D:>3} {ns:>8} " + "".join(cells))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", required=True)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    report(args.label) if args.report_only else run(args.endpoint, args.model, args.label)


if __name__ == "__main__":
    main()
