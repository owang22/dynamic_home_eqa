"""E5 — regime inference from SPARSE diagnostic observations (H2 redesign).

The fair test the first H2 run lacked: inferable-regime households (personas a
human could guess), a SPARSE digest of a few semantically-loaded diagnostic
sightings (not dense snapshots the stats model can copy), an explicit
regime-reasoning prompt, and HELD-OUT regime-dependent targets.

  digest = a handful of DIAGNOSTIC-object sightings (yoga_mat in the living room
           at 05:15; scrubs leaving at 18:00) + a couple of ambient sightings.
           The held-out target objects NEVER appear in it.
  query  = a SHARED dependent object at a regime-revealing time (water_bottle at
           05:30 — living room for the fitness regime, nightstand for the nurse).

  classical (per-edge, fit on the sparse digest): no target observations -> backs
           off to the population prior -> predicts the TYPICAL home -> wrong when
           the regime moved it. The control.
  llm_named: sees the named diagnostic sightings -> should infer the persona
           ("yoga mat at 5am -> early fitness") -> predict the target's
           regime-consistent location.
  llm_anon: diagnostic names stripped (object_17 in the living room at 05:15) ->
           can hypothesize "early riser" but cannot tell fitness from night-shift
           -> the mechanism isolation.

Pre-registered: llm_named > llm_anon >= classical on the held-out targets. If
llm_named ~= classical, world-knowledge regime inference does not help even here.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from dynbelief.h2 import core
from dynbelief.experiments.streams import true_parent_at
from dynbelief.classical.run import make_arm, _belief, _rows_fields
from dynbelief.classical.filter import uniform_belief
from dynbelief.experiments.e1 import score_prediction
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

DIGEST_DAYS = [0, 1, 2, 3, 4]          # first-week weekdays (regime repeats weekly)
QUERY_DAYS = [7, 9]                      # later weekdays (Mon, Wed)
BANK = "atyp_regime_v1"

# Per household: diagnostic objects (+ the hour they are in their telling spot),
# ambient objects for a little non-diagnostic context, and the held-out targets
# (shared dependent objects) with the regime-revealing query hour.
CFG = {
  "regime_early_fitness_v1": {
      "diagnostic": [("yoga_mat", 5), ("dumbbells", 5), ("running_shoes", 7)],
      "ambient": [("bowl", 7), ("plate", 18)],
      "targets": [("water_bottle", 5), ("phone", 11), ("protein_shaker", 7)]},
  "regime_night_nurse_v1": {
      "diagnostic": [("scrubs", 18), ("badge", 18), ("stethoscope", 7)],
      "ambient": [("bowl", 8), ("plate", 16)],
      "targets": [("water_bottle", 5), ("phone", 11), ("keys", 11)]},
  "regime_wfh_hybrid_v1": {
      "diagnostic": [("headset", 10), ("webcam", 10), ("laptop_stand", 14)],
      "ambient": [("bowl", 7), ("remote", 21)],
      "targets": [("laptop", 14), ("coffee_mug", 14)]},
  "regime_office_commuter_v1": {
      "diagnostic": [("transit_card", 8), ("work_lanyard", 18), ("travel_mug", 8)],
      "ambient": [("bowl", 7), ("remote", 21)],
      "targets": [("laptop", 14), ("coffee_mug", 10)]},
}

REGIME_SCHEMA = {
    "type": "object",
    "properties": {
        "regime_hypothesis": {"type": "string"},
        "predictions": {"type": "array", "items": {"type": "object", "properties": {
            "receptacle": {"type": "string"}, "p": {"type": "number"}},
            "required": ["receptacle", "p"]}},
    },
    "required": ["regime_hypothesis", "predictions"],
}

_SYS = (
    "You are inferring a household's daily ROUTINE from a few object sightings, "
    "then predicting where a DIFFERENT object is at a given time. First, in "
    "'regime_hypothesis', reason about what persona/routine these sightings imply "
    "— e.g. exercise gear in the living room before dawn suggests an early-morning "
    "fitness routine; scrubs and a hospital badge leaving in the evening suggest a "
    "night-shift healthcare worker who sleeps during the day; a headset and webcam "
    "at a home desk suggest remote work. Then use that routine to predict the "
    "queried object's location — it may differ from where the object 'usually' "
    "lives. Give up to 3 candidate receptacles with probabilities."
)


def _digest_and_hist(h, cfg, days):
    """Sparse chronological sightings of diagnostic + ambient objects (NOT the
    targets). Returns (digest_text, hist_rows, sightings)."""
    sightings = []
    picks = [(o, hr) for (o, hr) in cfg["diagnostic"] for _ in (0, 1)] + cfg["ambient"]
    # 2 days per diagnostic object, 1 per ambient — spread across `days`
    di = 0
    for o, hr in cfg["diagnostic"]:
        for dd in (days[1], days[3]):
            t = dd * 1440 + hr * 60 + 10
            rec = true_parent_at(h["by_obj"], h["init"], o, t)
            if rec != "elsewhere":
                sightings.append((t, o, rec))
    for o, hr in cfg["ambient"]:
        t = days[2] * 1440 + hr * 60 + 5
        rec = true_parent_at(h["by_obj"], h["init"], o, t)
        if rec != "elsewhere":
            sightings.append((t, o, rec))
    sightings.sort()
    lines = [f"  Day {t // 1440}, {(t % 1440)//60:02d}:{(t % 1440) % 60:02d} — "
             f"{o} seen at {rec}" for (t, o, rec) in sightings]
    digest = "Observations:\n" + "\n".join(lines) if lines else "(no observations)"
    hist_by_t = defaultdict(dict)
    for (t, o, rec) in sightings:
        hist_by_t[t][o] = rec
    hist = [{"day": t // 1440, "t_min": t, "parents": parents}
            for t, parents in sorted(hist_by_t.items())]
    return digest, hist, sightings


def _target_eps(h, cfg, hh):
    eps = []
    for i, (obj, hr) in enumerate(cfg["targets"]):
        for j, qd in enumerate(QUERY_DAYS):
            t = qd * 1440 + hr * 60
            true = true_parent_at(h["by_obj"], h["init"], obj, t)
            eps.append({"bank": BANK, "household": hh, "stream": "regime_target",
                        "query_id": i * 10 + j, "object": obj, "t_query": t,
                        "true_receptacle": true, "moved_since_obs": None,
                        "last_obs": None, "last_obs_t": None, "held_out": True, "tercile": None})
    return eps


def _llm_regime(client, digest, cands, ep, temperature=0.0):
    obj = ep["object"]
    clk = f"{(ep['t_query'] % 1440)//60:02d}:{(ep['t_query'] % 1440) % 60:02d}"
    day = ep["t_query"] // 1440
    user = (f"{digest}\n\nCandidate receptacles: {', '.join(cands)}, elsewhere.\n\n"
            f"Question: on day {day} at {clk}, where is the {obj}?")
    try:
        out = json.loads(client.generate(_SYS, user, REGIME_SCHEMA, seed=7, temperature=temperature))
        preds, hyp = out["predictions"], out.get("regime_hypothesis", "")
    except Exception:
        preds, hyp = [], ""
    argmax, p_true, brier, logloss, top3 = score_prediction(preds, cands + ["elsewhere"], ep["true_receptacle"])
    return argmax, p_true, top3, hyp


def run(endpoint, model):
    client = OpenAIHTTPClient(endpoint, model)
    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    omap, rmap = core.anon_maps(BANK)
    rows, hyps = [], []
    for hh in core.households(BANK):
        base = hh.split("__")[0]
        cfg = CFG[base]
        h = core.load_hh(BANK, hh)
        digest, hist, _ = _digest_and_hist(h, cfg, DIGEST_DAYS)
        eps = _target_eps(h, cfg, hh)
        # classical control (fit on the sparse digest; targets unseen)
        rm = make_arm("C3", h["cand_set"], hist)[0] if hist else None
        for ep in eps:
            belief = _belief(rm, h["cand_set"], ep["object"], ep["t_query"], ep, "categorical") if rm else uniform_belief(h["cand_set"])
            argmax, p_true, brier, logloss, top3 = _rows_fields(belief, h["cand_set"], ep["true_receptacle"])
            rows.append(_row(ep, "classical", argmax, top3))
        # llm named
        named = list(pool.map(lambda ep: _llm_regime(client, digest, h["cands"], ep), eps))
        for ep, (am, pt, t3, hyp) in zip(eps, named):
            rows.append(_row(ep, "llm_named", am, t3)); hyps.append((hh, "named", ep["object"], hyp))
        # llm anon
        adigest = core.anon_digest(digest, omap, rmap)
        acands = [rmap[c] for c in h["cands"]]
        aeps = core.anon_eps(eps, omap, rmap)
        anon = list(pool.map(lambda ep: _llm_regime(client, adigest, acands, ep), aeps))
        for ep, (am, pt, t3, hyp) in zip(aeps, anon):
            rows.append(_row(ep, "llm_anon", am, t3)); hyps.append((hh, "anon", ep["object"], hyp))
        print(f"[e5] {hh} done", flush=True)
    pool.shutdown()
    core.OUT.mkdir(parents=True, exist_ok=True)
    (core.OUT / "e5_rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    (core.OUT / "e5_hypotheses.txt").write_text(
        "\n".join(f"[{hh} {mode}] q={obj}: {hyp}" for hh, mode, obj, hyp in hyps))
    report(rows, hyps)


def _row(ep, arm, argmax, top3):
    return {"bank": ep["bank"], "household": ep["household"], "arm": arm,
            "object": ep["object"], "true_receptacle": ep["true_receptacle"],
            "predicted": argmax, "correct": int(argmax == ep["true_receptacle"]),
            "top3_correct": int(top3)}


def report(rows, hyps=None):
    print("\n" + "=" * 68)
    print("E5 — regime inference on held-out regime-dependent targets")
    print("=" * 68)
    def acc(arm, hh=None):
        v = [r["correct"] for r in rows if r["arm"] == arm and (hh is None or r["household"] == hh)]
        return np.mean(v) if v else float("nan")
    t3 = lambda arm: np.mean([r["top3_correct"] for r in rows if r["arm"] == arm])
    print(f"\n{'arm':12} {'top1':>8} {'top3':>8}")
    for arm in ("classical", "llm_named", "llm_anon"):
        print(f"{arm:12} {acc(arm):>8.3f} {t3(arm):>8.3f}")
    print(f"\nper household (top1: classical / named / anon):")
    for hh in sorted({r["household"] for r in rows}):
        print(f"  {hh:32} {acc('classical',hh):.2f} / {acc('llm_named',hh):.2f} / {acc('llm_anon',hh):.2f}")
    c, n, a = acc("classical"), acc("llm_named"), acc("llm_anon")
    if n > a + 0.05 and n > c + 0.05:
        v = "REGIME INFERENCE via WORLD KNOWLEDGE (named > anon >= classical) — H2 supported"
    elif n > c + 0.05 and abs(n - a) <= 0.05:
        v = "adaptation helps but it's in-context stats (named~=anon > classical)"
    else:
        v = "regime inference does not help (named ~= classical) — H2 fails even here"
    print(f"\noverall: classical={c:.3f} named={n:.3f} anon={a:.3f}\n  -> {v}")
    if hyps:
        print("\nsample inferred regimes (named):")
        seen = set()
        for hh, mode, obj, hyp in hyps:
            if mode == "named" and hh not in seen:
                seen.add(hh); print(f"  {hh.split('__')[0]}: {hyp[:150]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    if args.report_only:
        rows = [json.loads(l) for l in (core.OUT / "e5_rows.jsonl").read_text().splitlines() if l.strip()]
        report(rows)
    else:
        run(args.endpoint, args.model)


if __name__ == "__main__":
    main()
