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


def bank_of(bank_name):
    """(bank_dir, cfgmap, test_days, nomem_allowed) for a --bank choice.
    v22/v22dev are the VERSION22 banks (12 varied households / 4 dev; see
    reflect/v22.py) whose cfgs also carry the static-distractor object pool."""
    from dynbelief.reflect.v22 import (V22_BANK, V22_DEV_BANK, V22B_BANK,
                                       V22_CFG, V22_DEV_CFG, V22B_CFG)
    return {
        "conf":   (CONF_BANK, CONF_CFG, TEST_DAYS_CONF, True),
        "dev":    (DEV_BANK, DEV_CFG, TEST_DAYS_DEV, False),
        "v22":    (V22_BANK, V22_CFG, TEST_DAYS_CONF, True),
        "v22dev": (V22_DEV_BANK, V22_DEV_CFG, TEST_DAYS_DEV, False),
        "v22b":   (V22B_BANK, V22B_CFG, TEST_DAYS_CONF, True),
    }[bank_name]


def room_of(hh):
    """Receptacle -> room map for a household. Seed-variant instances carry an
    "__i{n}" suffix (bank.HouseholdSpec.instance); the base profile is the part
    before "__"."""
    base = hh.split("__")[0]
    m = {r.id: r.room for r in load_profile(core.MANUAL_DIR / f"{base}.yaml").receptacles}
    m["elsewhere"] = "elsewhere"
    return m


def _fmt(t, obj, rec):
    return f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — {obj} seen at {rec}"


# Observation rate: how many object-movement events per calendar DAY the whole
# SYSTEM sees before questioning. None = see everything (saturated: one day already
# reveals a strongly-conditioned persona). A small setting STARVES the early days so
# the days-of-experience axis becomes an information axis. Spec forms:
#   None        -> see all events
#   int N       -> fixed cap: keep <=N events per day
#   ("rand", m) -> random: keep Poisson(m) events per day (capped at available)
# The SAME thinned event set feeds every arm (LLM memory/digest AND the classical &
# fusion fits) via thinned_event_tuples — equal information across arms.
OBS_PER_DAY = None


def parse_obs_spec(s):
    """CLI/string -> spec. 'none'/'' -> None; '5' -> 5; 'rand3'/'rand:3' -> ('rand',3)."""
    if s is None or str(s).lower() in ("", "none"):
        return None
    s = str(s).lower()
    if s.startswith("rand"):
        return ("rand", float(s.replace("rand", "").lstrip(":")))
    return int(s)


def obs_tag(spec):
    """Filename/label suffix for an obs spec (matches --obs-per-day)."""
    if spec is None:
        return ""
    if isinstance(spec, tuple):
        return f"orand{int(spec[1])}"
    return f"o{spec}"


def _day_keep_count(spec, day, available):
    if spec is None:
        return available
    if isinstance(spec, tuple) and spec[0] == "rand":
        import numpy as _np
        n = int(_np.random.default_rng(2000 + day).poisson(spec[1]))
        return min(max(n, 0), available)
    return min(int(spec), available)


def thinned_event_tuples(by_obj, spec, t_lo=0, t_hi=10 ** 12):
    """The SINGLE source of truth for what the system observes. Returns the sorted
    (t, obj, rec) tuples kept in [t_lo, t_hi) under `spec`. Per-day subsample seeded
    by day index (1000+day for which events, 2000+day for the random count) so the
    kept set is deterministic and stable as the query window grows."""
    ev = [(t, o, r) for o, evs in by_obj.items() for (t, r) in evs if t_lo <= t < t_hi]
    ev.sort()
    if spec is None:
        return ev
    import numpy as _np
    by_day = {}
    for e in ev:
        by_day.setdefault(e[0] // 1440, []).append(e)
    kept = []
    for day, evs in by_day.items():
        k = _day_keep_count(spec, day, len(evs))
        if k >= len(evs):
            kept += evs
        elif k > 0:
            idx = _np.random.default_rng(1000 + day).choice(len(evs), size=k, replace=False)
            kept += [evs[i] for i in sorted(idx)]
    kept.sort()
    return kept


# Distractor observation system (version22): per day, N extra sightings of
# STATIC distractor objects (a chair by the dining table, a pillow on a bed —
# things that essentially never move) are reported alongside the true thinned
# events. They inflate observations/day WITHOUT adding information: the sighted
# location is always the object's static home. Distractor objects never appear
# in queries (queries use only cfg targets), so they cannot inflate accuracy —
# they only test whether an arm's memory/updating is robust to clutter. The
# classical arms are provably unaffected (per-edge fits; distractor sightings
# touch only distractor objects), so report.py does not need to inject them.
DISTRACTORS = 0


def distractor_tuples(h, dist_objs, n_per_day, t_lo=0, t_hi=10 ** 12):
    """Deterministic (t, obj, rec) sightings of static distractor objects:
    n_per_day per calendar day at random minutes in [07:00, 22:00), object drawn
    uniformly from the household's distractor pool, location = its true (static)
    receptacle. Seeded per day (4000+day) so the set is stable as windows grow."""
    if not n_per_day or not dist_objs:
        return []
    import numpy as _np
    out = []
    d_lo, d_hi = t_lo // 1440, (t_hi - 1) // 1440
    for day in range(max(0, d_lo), d_hi + 1):
        rng = _np.random.default_rng(4000 + day)
        for _ in range(int(n_per_day)):
            t = day * 1440 + int(rng.integers(7 * 60, 22 * 60))
            obj = dist_objs[int(rng.integers(len(dist_objs)))]
            if t_lo <= t < t_hi:
                out.append((t, obj, true_parent_at(h["by_obj"], h["init"], obj, t)))
    out.sort()
    return out


def stream_lines(h, t_lo, t_hi, dist_objs=None):
    """Frozen-format lines of the thinned event set in [t_lo, t_hi) (uses the module
    OBS_PER_DAY spec), merged with DISTRACTORS/day static-object sightings."""
    ev = thinned_event_tuples(h["by_obj"], OBS_PER_DAY, t_lo, t_hi)
    ev = sorted(ev + distractor_tuples(h, dist_objs, DISTRACTORS, t_lo, t_hi))
    return [_fmt(t, o, r) for (t, o, r) in ev]


def build_memory(client, bank, hh, h, label, dist_objs=None):
    """Sequential nightly reflection over MEM_DAYS. Saves per-day snapshots
    (json + md) and returns {days_of_experience: (md, H_bits)}."""
    snap_dir = OUT / "memory" / bank / f"{hh}__{label}"
    snap_dir.mkdir(parents=True, exist_ok=True)
    mem, md = dict(M.EMPTY_MEM), M.render_md(M.EMPTY_MEM, -1)
    out, metas = {}, []
    for d in range(MEM_DAYS):
        lines = stream_lines(h, d * 1440, (d + 1) * 1440, dist_objs)
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
        # small budget: the answer is a ~200-token JSON; a large budget makes
        # prompt+max_tokens overflow --max-model-len on long raw digests (the bug
        # that zeroed the original llm_nomem rows at late checkpoints)
        preds = json.loads(client.generate(sys, user, REGIME_SCHEMA,
                                           seed=7, temperature=0.0,
                                           max_tokens=1024))["predictions"]
    except Exception:
        preds = []
    am, _, _, _, t3 = score_prediction(preds, cand_set, true)
    return am, int(t3), [{"receptacle": str(p.get("receptacle", "")),
                          "p": float(p.get("p", 0.0))} for p in preds][:3]


def run(endpoint, model, label, bank_name, arms=("direct", "nomem"), out_suffix=""):
    bank, cfgmap, test_days, nomem_ok = bank_of(bank_name)
    do_direct = "direct" in arms
    do_nomem = "nomem" in arms and nomem_ok
    client = OpenAIHTTPClient(endpoint, model)
    OUT.mkdir(parents=True, exist_ok=True)

    hhs = list(cfgmap)
    data = {hh: core.load_hh(bank, hh) for hh in hhs}
    dist_of = {hh: cfgmap[hh].get("distractors") for hh in hhs}
    # memory building (only the direct arm reads memory): parallel across
    # households, sequential days within
    if do_direct:
        with ThreadPoolExecutor(max_workers=len(hhs)) as ex:
            mems = dict(zip(hhs, ex.map(
                lambda hh: build_memory(client, bank, hh, data[hh], label,
                                        dist_of[hh]), hhs)))
    else:
        mems = {hh: {ck: ("", float("nan")) for ck in CKPTS} for hh in hhs}

    pool = ThreadPoolExecutor(max_workers=core.MAX_WORKERS)
    rows = []
    for hh in hhs:
        h = data[hh]; cfg = cfgmap[hh]
        cands, cand_set = h["cands"], h["cand_set"]
        rmap = room_of(hh)
        jobs = []
        for ckpt in CKPTS:
            md, hbits = mems[hh][ckpt]
            raw = "Observations:\n" + "\n".join(
                stream_lines(h, 0, ckpt * 1440, dist_of[hh]))
            for (obj, hr) in cfg["targets"]:
                n_total = len(h["by_obj"].get(obj, []))
                for qd in test_days:
                    tq = qd * 1440 + hr * 60
                    true = true_parent_at(h["by_obj"], h["init"], obj, tq)
                    base = {"bank": bank, "hh": hh, "object": obj, "ckpt": ckpt,
                            "test_day": qd, "t_query": tq, "true": true,
                            "rarity": e7._rarity(n_total),
                            "obs_spec": obs_tag(OBS_PER_DAY) or "none",
                            "dist": DISTRACTORS,
                            "H": round(hbits, 4) if hbits == hbits else None}
                    if do_direct:
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
    (OUT / f"rows_{bank_name}_{label}{out_suffix}.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))
    print(f"[reflect:{bank_name}] wrote {len(rows)} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:8400")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--label", default="deepseek")
    ap.add_argument("--bank", choices=["dev", "conf", "v22", "v22dev", "v22b"], required=True)
    ap.add_argument("--arms", default="direct,nomem",
                    help="comma list from {direct,nomem}")
    ap.add_argument("--out-suffix", default="")
    ap.add_argument("--obs-per-day", default=None,
                    help="events/day the SYSTEM sees (all arms). 'none' (all), 'N' "
                         "(fixed cap), 'randN' (Poisson mean N). Starves early days.")
    ap.add_argument("--distractors", type=int, default=0,
                    help="static-distractor sightings/day added to every stream "
                         "(v22 banks; see reflect/v22.py)")
    args = ap.parse_args()
    global OBS_PER_DAY, DISTRACTORS
    OBS_PER_DAY = parse_obs_spec(args.obs_per_day)
    DISTRACTORS = args.distractors
    run(args.endpoint, args.model, args.label, args.bank,
        arms=tuple(args.arms.split(",")), out_suffix=args.out_suffix)


if __name__ == "__main__":
    main()
