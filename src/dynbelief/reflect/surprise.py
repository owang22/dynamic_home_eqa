"""SURPRISE strategy — classical-model-gated reflection (version22).

The nightly-reflection arm (llm_direct) calls the LLM once at the END of every
day regardless of what happened. Here the CLASSICAL model (C3g, refit each
morning on everything observed so far) is the MAIN ENGINE: each day's kept
observations are scored against its belief, and only when the day's evidence
SIGNIFICANTLY CONTRADICTS the current belief — >= MIN_DAY_SURPRISES sightings
with p_model(observed receptacle) < THRESH while the model was confident
elsewhere (max_p >= CONF_MIN), for objects the model has actually seen before —
does the agent notify the LLM to reflect. The reflection call is the same nightly rewrite as
memory.reflect_day, but the day's surprising lines are marked so the LLM knows
WHY it was woken up. Day 0 always reflects (there is no belief model yet — the
first day bootstraps the memory).

Everything else is held identical to run.py (same thinned true stream, same
distractor sightings, same checkpoints/test week/query prompt), so
llm_surprise rows merge directly into the report tables via --extra-rows.
Efficiency is part of the result: rows carry n_reflect (LLM reflection calls
made by that checkpoint; the nightly arm's count is ckpt).
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from dynbelief.h2 import core, e7_learning as e7
from dynbelief.classical.run import make_arm, _belief
from dynbelief.experiments.streams import true_parent_at
from dynbelief.reflect import memory as M
from dynbelief.reflect import run as R
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient

OUT = R.OUT
THRESH = 0.15          # surprise if p_model(observed rec) < THRESH (seen objects)
CONF_MIN = 0.55        # ...AND the model was confident somewhere else (max_p >=
                       # CONF_MIN): an unconfident belief cannot be contradicted,
                       # it is just ignorance — no reason to wake the LLM.
MIN_DAY_SURPRISES = 2  # day-level trigger: a single contradicting sighting can be
                       # noise/misplacement; >=2 independent contradictions in one
                       # day = the day significantly contradicts the belief model.
                       # (Offline sweep: >=1 fires 11.0/14 days — nearly nightly —
                       # >=2 fires 6.5/14, an actual efficiency difference.)


def _day_tuples(h, dist_objs, day):
    """The day's kept observation tuples (true thinned + distractor sightings),
    each tagged is_true."""
    lo, hi = day * 1440, (day + 1) * 1440
    true = [(t, o, r, True) for (t, o, r) in
            R.thinned_event_tuples(h["by_obj"], R.OBS_PER_DAY, lo, hi)]
    dist = [(t, o, r, False) for (t, o, r) in
            R.distractor_tuples(h, dist_objs, R.DISTRACTORS, lo, hi)]
    return sorted(true + dist)


def _surprising(rm, cand_set, seen_before, tup):
    """Does this observation contradict the current belief model? Only objects
    the model has prior events for can surprise it (a never-seen object's
    uniform belief is ignorance, not contradiction)."""
    t, obj, rec, _ = tup
    prev = seen_before.get(obj)
    if rm is None or prev is None:
        return False, None
    ep = {"object": obj, "t_query": t, "last_obs": prev[1], "last_obs_t": prev[0]}
    bel = _belief(rm, cand_set, obj, t, ep, "categorical")
    p = float(bel.get(rec, 0.0))
    return (p < THRESH and max(bel.values()) >= CONF_MIN), p


def build_memory_surprise(client, bank, hh, h, label, dist_objs, cand_set):
    """Sequential days; C3g refit each morning on all TRUE kept events so far;
    reflect only on surprising days (day 0 always). Returns
    ({days_of_experience: (md, H_bits, n_reflect)}, meta)."""
    snap_dir = OUT / "memory" / bank / f"{hh}__{label}"
    snap_dir.mkdir(parents=True, exist_ok=True)
    mem, md = dict(M.EMPTY_MEM), M.render_md(M.EMPTY_MEM, -1)
    out, metas, n_reflect = {}, [], 0
    hist_true = []                     # kept TRUE tuples so far (the engine's diet)
    seen_before = {}                   # obj -> (t, rec) of last kept TRUE sighting
    for d in range(R.MEM_DAYS):
        # morning refit on everything strictly before today
        obs_rows = [{"day": t // 1440, "t_min": t, "parents": {o: r}}
                    for (t, o, r) in hist_true]
        rm = make_arm("C3g", cand_set, obs_rows)[0] if obs_rows else None
        tuples = _day_tuples(h, dist_objs, d)
        marked, day_sup = [], []
        for tup in tuples:
            t, obj, rec, is_true = tup
            sup, p = _surprising(rm, cand_set, seen_before, tup)
            line = R._fmt(t, obj, rec)
            if sup:
                line += f"   *** SURPRISING: belief model expected this object elsewhere (p={p:.2f})"
                day_sup.append({"t": t, "obj": obj, "rec": rec, "p": round(p, 4)})
            marked.append(line)
            if is_true:
                hist_true.append((t, obj, rec))
                seen_before[obj] = (t, rec)
        do_reflect = (d == 0) or len(day_sup) >= MIN_DAY_SURPRISES
        failed = False
        if do_reflect:
            sys_extra = ("" if d == 0 else
                         " You were woken because the statistical belief model was "
                         "SURPRISED today: at least one marked observation contradicts "
                         "its learned expectations. Pay special attention to those lines.")
            new = M.reflect_day(_SysWrap(client, sys_extra), md, d, marked)
            failed = new is None
            if not failed:
                mem = new
            n_reflect += 1
        md = M.render_md(mem, d)
        hbits = M.entropy_bits(mem["hypotheses"])
        (snap_dir / f"day_{d:02d}.md").write_text(md)
        (snap_dir / f"day_{d:02d}.json").write_text(json.dumps(mem, indent=1))
        metas.append({"bank": bank, "hh": hh, "day": d, "H": round(hbits, 4),
                      "failed": failed, "reflected": do_reflect,
                      "n_surprises": len(day_sup), "surprises": day_sup,
                      "n_reflect_cum": n_reflect,
                      "hyps": [{"persona": x.get("persona"), "prob": x.get("prob")}
                               for x in mem["hypotheses"]]})
        out[d + 1] = (md, hbits, n_reflect)
    (snap_dir / "meta.jsonl").write_text("".join(json.dumps(m) + "\n" for m in metas))
    print(f"[surprise:{bank}] {hh}: {n_reflect}/{R.MEM_DAYS} days reflected "
          f"(H day13={out[R.MEM_DAYS][1]:.2f})", flush=True)
    return out, metas


class _SysWrap:
    """Client proxy appending a per-call suffix to the system prompt."""
    def __init__(self, client, sys_extra):
        self._c, self._x = client, sys_extra

    def generate(self, sys, user, schema, **kw):
        return self._c.generate(sys + self._x, user, schema, **kw)


def run(endpoint, model, label, bank_name):
    bank, cfgmap, test_days, _ = R.bank_of(bank_name)
    client = OpenAIHTTPClient(endpoint, model)
    OUT.mkdir(parents=True, exist_ok=True)
    hhs = list(cfgmap)
    data = {hh: core.load_hh(bank, hh) for hh in hhs}
    dist_of = {hh: cfgmap[hh].get("distractors") for hh in hhs}

    with ThreadPoolExecutor(max_workers=len(hhs)) as ex:
        built = dict(zip(hhs, ex.map(
            lambda hh: build_memory_surprise(client, bank, hh, data[hh], label,
                                             dist_of[hh], data[hh]["cand_set"]),
            hhs)))

    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    rows = []
    for hh in hhs:
        h = data[hh]; cfg = cfgmap[hh]
        cands, cand_set = h["cands"], h["cand_set"]
        rmap = R.room_of(hh)
        mems = built[hh][0]
        jobs = []
        for ckpt in R.CKPTS:
            md, hbits, n_ref = mems[ckpt]
            for (obj, hr) in cfg["targets"]:
                n_total = len(h["by_obj"].get(obj, []))
                for qd in test_days:
                    tq = qd * 1440 + hr * 60
                    true = true_parent_at(h["by_obj"], h["init"], obj, tq)
                    base = {"bank": bank, "hh": hh, "object": obj, "ckpt": ckpt,
                            "test_day": qd, "t_query": tq, "true": true,
                            "rarity": e7._rarity(n_total),
                            "obs_spec": R.obs_tag(R.OBS_PER_DAY) or "none",
                            "dist": R.DISTRACTORS, "n_reflect": n_ref,
                            "H": round(hbits, 4) if hbits == hbits else None}
                    jobs.append((md, obj, tq, true, base))

        def do(j):
            md, obj, tq, true, base = j
            am, t3, preds = R._query(client, M.QUERY_SYS, f"YOUR MEMORY:\n{md}",
                                     cands, cand_set, obj, tq, true)
            return {**base, "model": "llm_surprise", "pred": am,
                    "correct": int(am == true),
                    "room_correct": int(rmap.get(am, "x") == rmap.get(true, "y")),
                    "top3_correct": t3, "preds": preds}
        rows += list(pool.map(do, jobs))
        print(f"[surprise:{bank_name}] {hh} queries done ({len(jobs)})", flush=True)
    pool.shutdown()
    outf = OUT / f"rows_surprise_{bank_name}_{label}.jsonl"
    outf.write_text("".join(json.dumps(r) + "\n" for r in rows))
    tot = sum(built[hh][0][R.MEM_DAYS][2] for hh in hhs)
    print(f"[surprise:{bank_name}] wrote {len(rows)} rows -> {outf}")
    print(f"[surprise:{bank_name}] total reflection calls: {tot} "
          f"(nightly arm would be {len(hhs) * R.MEM_DAYS})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", default="surprise")
    ap.add_argument("--bank", choices=["conf", "v22", "v22dev", "v22b"], default="v22")
    ap.add_argument("--obs-per-day", default=None)
    ap.add_argument("--distractors", type=int, default=0)
    global THRESH
    ap.add_argument("--thresh", type=float, default=THRESH)
    args = ap.parse_args()
    THRESH = args.thresh
    R.OBS_PER_DAY = R.parse_obs_spec(args.obs_per_day)
    R.DISTRACTORS = args.distractors
    run(args.endpoint, args.model, args.label, args.bank)


if __name__ == "__main__":
    main()
