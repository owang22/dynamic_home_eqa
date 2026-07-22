"""E6 — regime-inference SHARPENING: held-out-target accuracy vs the number of
diagnostic sightings in the digest.

The days-seen axis that actually favours the LLM. Unlike E1 (observed objects,
where the stats model just copies), here the targets are HELD OUT, so more
diagnostic evidence lets the LLM sharpen its regime hypothesis and transfer
better — while classical stays at 0 (per-edge) and class_freq stays flat (no
regime awareness). Sightings are added BREADTH-FIRST (one per diagnostic object,
then seconds), so each extra sighting adds regime diversity.

Reuses the frozen confirmatory prompt/schema/digest-format and the confirmatory
bank/CFG. Reports named + anon curves (mechanism) with class_freq as a flat
reference. Run per model via --model.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from dynbelief.h2 import core, e0_baselines as e0
from dynbelief.h2.confirm import CFG, BANK, SIGHT_DAYS, _llm_pred
from dynbelief.h2.e5_regime import _SYS
from dynbelief.experiments.streams import true_parent_at
from dynbelief.profiles.schema import default_class, load_profile
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

LEVELS = [0, 1, 2, 3, 4, 6]          # number of diagnostic sightings shown
QUERY_DAYS = [7, 9, 11, 15]          # fewer than confirm (cost), still uniform


def _ordered_sightings(h, cfg):
    """Breadth-first diagnostic sightings: [obj0#1, obj1#1, obj2#1, obj0#2, ...].
    Each is (t, obj, rec) at a day where the object is in a telling (non-else) spot."""
    per_obj = []
    for o, hr in cfg["diag"]:
        s = []
        for dd in SIGHT_DAYS:
            if len(s) >= 2:
                break
            t = dd * 1440 + hr * 60 + 10
            rec = true_parent_at(h["by_obj"], h["init"], o, t)
            if rec != "elsewhere":
                s.append((t, o, rec))
        per_obj.append(s)
    ordered = []
    for r in range(2):
        for s in per_obj:
            if len(s) > r:
                ordered.append(s[r])
    return ordered


def _digest(sightings):
    if not sightings:
        return "(no observations)"
    lines = [f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — {o} seen at {rec}"
             for (t, o, rec) in sorted(sightings)]
    return "Observations:\n" + "\n".join(lines)


def _targets(h, cfg, hh):
    eps = []
    for obj, hr in cfg["targets"]:
        for qd in QUERY_DAYS:
            t = qd * 1440 + hr * 60
            eps.append({"bank": BANK, "household": hh, "object": obj, "t_query": t,
                        "true_receptacle": true_parent_at(h["by_obj"], h["init"], obj, t)})
    return eps


def _prior_sighting(h, ep):
    """The queried object's location one week earlier, same weekday+hour
    (regime-matched -> informative). Returns (t, obj, rec) or None."""
    t = ep["t_query"] - 7 * 1440
    if t < 0:
        return None
    rec = true_parent_at(h["by_obj"], h["init"], ep["object"], t)
    return (t, ep["object"], rec)


def run(endpoint, model, label, nonheldout=False):
    client = OpenAIHTTPClient(endpoint, model)
    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    e0._TYP = e0.typ_class_target()
    omap, rmap = core.anon_maps(BANK)
    rows = []
    for hh in core.households(BANK):
        base = hh.split("__")[0]; cfg = CFG[base]; h = core.load_hh(BANK, hh)
        room_of = {r.id: r.room for r in load_profile(core.MANUAL_DIR / f"{base}.yaml").receptacles}
        ordered = _ordered_sightings(h, cfg)
        eps = _targets(h, cfg, hh)
        acands = [rmap[c] for c in h["cands"]]
        # non-held-out: each query object observed one week prior (regime-matched)
        priors = {i: _prior_sighting(h, e) for i, e in enumerate(eps)} if nonheldout else {}
        for k in LEVELS:
            base_sights = ordered[:k]

            def mk(e_i, anon=False):
                e = eps[e_i]
                s = list(base_sights)
                if nonheldout and priors[e_i] is not None:
                    s = s + [priors[e_i]]           # add the object's own prior sighting
                dg = _digest(s)
                if anon:
                    return core.anon_digest(dg, omap, rmap), acands, core.anon_eps([e], omap, rmap)[0]
                return dg, h["cands"], e

            named = list(pool.map(lambda i: _llm_pred(client, _SYS, *mk(i, False)), range(len(eps))))
            anon = list(pool.map(lambda i: _llm_pred(client, _SYS, *mk(i, True)), range(len(eps))))
            for i, (e, nm, an) in enumerate(zip(eps, named, anon)):
                cf = e0.class_freq_predict(default_class(e["object"]), h["cand_set"], room_of)
                row = {"model": label, "household": hh, "level": k, "object": e["object"],
                       "named": int(nm[0] == e["true_receptacle"]),
                       "anon": int(an[0] == e["true_receptacle"]),
                       "class_freq": int(cf == e["true_receptacle"])}
                if nonheldout and priors[i] is not None:
                    row["last_obs"] = int(priors[i][2] == e["true_receptacle"])
                rows.append(row)
        print(f"[e6{'-nhq' if nonheldout else ''}:{label}] {hh} done", flush=True)
    pool.shutdown()
    core.OUT.mkdir(parents=True, exist_ok=True)
    suffix = "_nonheldout" if nonheldout else ""
    (core.OUT / f"e6_rows_{label}{suffix}.jsonl").write_text("".join(json.dumps(r)+"\n" for r in rows))
    report(label, nonheldout)


def _boot(by_hh, nb=2000, seed=0):
    hhs = list(by_hh); rng = np.random.default_rng(seed)
    if not hhs:
        return (np.nan, np.nan)
    m = [np.mean([v for i in rng.integers(0, len(hhs), len(hhs)) for v in by_hh[hhs[i]]]) for _ in range(nb)]
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def report(label, nonheldout=False):
    suffix = "_nonheldout" if nonheldout else ""
    rows = [json.loads(l) for l in (core.OUT / f"e6_rows_{label}{suffix}.jsonl").read_text().splitlines() if l.strip()]
    arms = ["named", "anon", "class_freq"] + (["last_obs"] if nonheldout else [])
    print("\n" + "=" * 72)
    print(f"E6 — accuracy vs #diagnostic sightings  (model={label}"
          f"{', NON-held-out: object observed 1wk prior' if nonheldout else ''})")
    print("=" * 72)
    print(f"  {'#sightings':>10}" + "".join(f"{a:>18}" for a in arms))
    for k in LEVELS:
        cells = []
        for arm in arms:
            by = defaultdict(list)
            for x in rows:
                if x["level"] == k and arm in x:
                    by[x["household"]].append(x[arm])
            allv = [v for vs in by.values() for v in vs]
            if not allv:
                cells.append(f"{'-':>18}"); continue
            lo, hi = _boot(by)
            cells.append(f"{np.mean(allv):.2f}[{lo:.2f},{hi:.2f}]".rjust(18))
        print(f"  {k:>10}" + "".join(cells))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", required=True)
    ap.add_argument("--nonheldout", action="store_true", help="queried object observed 1wk prior")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    if args.report_only:
        report(args.label, args.nonheldout)
    else:
        run(args.endpoint, args.model, args.label, args.nonheldout)


if __name__ == "__main__":
    main()
