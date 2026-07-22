"""Reflective-memory experiment driver (LLM phase).

Timeline per household: the agent lives through days 0..MEM_DAYS-1 of the FULL
event stream (diagnostic objects + regime targets + conventional distractors —
every object movement in the home), reflecting once at the end of each day into
its memory file. At each checkpoint D (days of experience) we freeze the memory
as of the end of day D-1 and ask the standard where-is-object queries on a fixed
FUTURE test week, so every checkpoint is a true forward prediction from the same
question set.

LLM arms generated here (per query):
  llm_direct — answers from its curated MEMORY ONLY (no raw stream). Tests whether
               ~15 curated lines retain the regime signal of ~hundreds of raw events.
  llm_nomem  — answers from the full RAW digest of all events up to D (no memory);
               the uncurated endpoint. (Confirmatory bank only.)
The direct call's full prediction list is STORED so the fusion arm (prior
injection, entropy-gated) and the kappa_max sweep run OFFLINE in report.py with
no further LLM calls. Classical arms also run offline there, fit on the IDENTICAL
event stream the LLM saw — same information, statistical vs semantic updating.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dynbelief.h2 import core, e7_learning as e7
from dynbelief.h2.confirm import CFG as CONF_CFG, BANK as CONF_BANK
from dynbelief.h2.e5_regime import REGIME_SCHEMA
from dynbelief.h2.e7_hybrid import DEV_BANK, DEV_CFG
from dynbelief.experiments.e1 import score_prediction
from dynbelief.experiments.streams import true_parent_at
from dynbelief.profiles.schema import load_profile
from dynbelief.reflect import memory as M
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

OUT = core.OUT.parent / "reflect"
MEM_DAYS = 14                                   # agent lives days 0..13
CKPTS = [1, 2, 3, 5, 7, 10, 14]                 # days of experience at query time
TEST_DAYS_CONF = list(range(14, 21))            # fixed future week (Mo..Su)
TEST_DAYS_DEV = [14, 16, 19]                    # Mo/We/Sa (dev: kappa sweep only)


def room_of(base):
    m = {r.id: r.room for r in load_profile(core.MANUAL_DIR / f"{base}.yaml").receptacles}
    m["elsewhere"] = "elsewhere"
    return m


def _fmt(t, obj, rec):
    return f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — {obj} seen at {rec}"


def stream_lines(h, t_lo, t_hi):
    """ALL object-movement events in [t_lo, t_hi), chronological, frozen format."""
    ev = [(t, o, r) for o, evs in h["by_obj"].items() for (t, r) in evs
          if t_lo <= t < t_hi]
    return [_fmt(t, o, r) for (t, o, r) in sorted(ev)]


def build_memory(client, bank, hh, h, label):
    """Sequential nightly reflection over MEM_DAYS. Saves per-day snapshots
    (json + md) and returns {days_of_experience: (md, H_bits)}."""
    snap_dir = OUT / "memory" / bank / f"{hh}__{label}"
    snap_dir.mkdir(parents=True, exist_ok=True)
    mem, md = dict(M.EMPTY_MEM), M.render_md(M.EMPTY_MEM, -1)
    out, metas = {}, []
    for d in range(MEM_DAYS):
        lines = stream_lines(h, d * 1440, (d + 1) * 1440)
        new = M.reflect_day(client, md, d, lines)
        failed = new is None
        if not failed:
            mem = new
        md = M.render_md(mem, d)
        hbits = M.entropy_bits(mem["hypotheses"])
        (snap_dir / f"day_{d:02d}.md").write_text(md)
        (snap_dir / f"day_{d:02d}.json").write_text(json.dumps(mem, indent=1))
        metas.append({"bank": bank, "hh": hh, "day": d, "H": round(hbits, 4),
                      "failed": failed,
                      "hyps": [{"persona": x.get("persona"), "prob": x.get("prob")}
                               for x in mem["hypotheses"]]})
        out[d + 1] = (md, hbits)
    (snap_dir / "meta.jsonl").write_text("".join(json.dumps(m) + "\n" for m in metas))
    print(f"[reflect:{bank}] {hh} memory built (H day13={out[MEM_DAYS][1]:.2f})", flush=True)
    return out


def _query(client, sys, context, cands, cand_set, obj, tq, true):
    clk = f"{(tq % 1440)//60:02d}:{(tq % 1440) % 60:02d}"
    user = (f"{context}\n\nCandidate receptacles: {', '.join(cands)}, elsewhere.\n\n"
            f"Question: on day {tq//1440} ({M.WEEKDAYS[(tq//1440) % 7]}) at {clk}, "
            f"where is the {obj}?")
    try:
        preds = json.loads(client.generate(sys, user, REGIME_SCHEMA,
                                           seed=7, temperature=0.0))["predictions"]
    except Exception:
        preds = []
    am, _, _, _, t3 = score_prediction(preds, cand_set, true)
    return am, int(t3), [{"receptacle": str(p.get("receptacle", "")),
                          "p": float(p.get("p", 0.0))} for p in preds][:3]


def run(endpoint, model, label, bank_name):
    bank, cfgmap = ((DEV_BANK, DEV_CFG) if bank_name == "dev" else (CONF_BANK, CONF_CFG))
    test_days = TEST_DAYS_DEV if bank_name == "dev" else TEST_DAYS_CONF
    do_nomem = bank_name != "dev"
    client = OpenAIHTTPClient(endpoint, model)
    OUT.mkdir(parents=True, exist_ok=True)

    hhs = list(cfgmap)
    data = {hh: core.load_hh(bank, hh) for hh in hhs}
    # memory building: parallel across households, sequential days within
    with ThreadPoolExecutor(max_workers=len(hhs)) as ex:
        mems = dict(zip(hhs, ex.map(
            lambda hh: build_memory(client, bank, hh, data[hh], label), hhs)))

    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    rows = []
    for hh in hhs:
        h = data[hh]; cfg = cfgmap[hh]
        cands, cand_set = h["cands"], h["cand_set"]
        rmap = room_of(hh)
        jobs = []
        for ckpt in CKPTS:
            md, hbits = mems[hh][ckpt]
            raw = "Observations:\n" + "\n".join(stream_lines(h, 0, ckpt * 1440))
            for (obj, hr) in cfg["targets"]:
                n_total = len(h["by_obj"].get(obj, []))
                for qd in test_days:
                    tq = qd * 1440 + hr * 60
                    true = true_parent_at(h["by_obj"], h["init"], obj, tq)
                    base = {"bank": bank, "hh": hh, "object": obj, "ckpt": ckpt,
                            "test_day": qd, "t_query": tq, "true": true,
                            "rarity": e7._rarity(n_total), "H": round(hbits, 4)}
                    jobs.append(("llm_direct", M.QUERY_SYS, f"YOUR MEMORY:\n{md}",
                                 obj, tq, true, base))
                    if do_nomem:
                        jobs.append(("llm_nomem", M.QUERY_SYS.replace(
                            "your MEMORY file: persona hypotheses with probabilities "
                            "plus selected evidence",
                            "the full log of observed events"), raw, obj, tq, true, base))

        def do(j):
            arm, sys, ctx, obj, tq, true, base = j
            am, t3, preds = _query(client, sys, ctx, cands, cand_set, obj, tq, true)
            r = {**base, "model": arm, "pred": am, "correct": int(am == true),
                 "room_correct": int(rmap.get(am, "x") == rmap.get(true, "y")),
                 "top3_correct": t3}
            if arm == "llm_direct":
                r["preds"] = preds                  # stored for offline fusion
            return r
        rows += list(pool.map(do, jobs))
        print(f"[reflect:{bank_name}] {hh} queries done ({len(jobs)})", flush=True)
    pool.shutdown()
    (OUT / f"rows_{bank_name}_{label}.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))
    print(f"[reflect:{bank_name}] wrote {len(rows)} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", default="deepseek")
    ap.add_argument("--bank", choices=["dev", "conf"], required=True)
    args = ap.parse_args()
    run(args.endpoint, args.model, args.label, args.bank)


if __name__ == "__main__":
    main()
