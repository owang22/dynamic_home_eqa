"""Generate simulator variants (weekday-regularity knobs) and score them with
truth-only oracles, without editing the simulator's files: every knob is a
module attribute or a loaded spec, patched in this process before
``situation_sim.run.generate`` runs.

    python3 -m baselines.patrol.sim_variants --seeds 0-9 --out ../data/situation_sim/variants \
        --variants base jitter_half whims_off leave_off moods_off habits_up all

Oracles per scored day (in-house truths at activity-driven question moments
are not needed here; uniform daytime minutes suffice for repeatability):
  routine  = location at the same clock time on the previous weekday
             (Sat and Sun compare with Friday; Mon with Friday; Tue with Mon)
  recency  = location at the last 8 h patrol pass (00:00 / 08:00 / 16:00)
Repeatability that rises Wed->Fri and falls on Sat is what a learner needs.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import subprocess
import sys
from typing import Dict, List

from baselines.patrol.sweep import parse_seeds
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE

VARIANTS: Dict[str, dict] = {
    "base": {},
    "jitter_half": {"jitter": 0.5},
    "jitter_third": {"jitter": 0.34},
    "whims_off": {"whims": 0.0},
    "leave_off": {"leave": 0.0},
    "moods_off": {"moods": 0.0},
    "habits_up": {"habits_weekday": 0.9},
    "regular": {"jitter": 0.5, "whims": 0.0, "leave": 0.0, "moods": 0.0},
    "regular_habits": {"jitter": 0.5, "whims": 0.0, "leave": 0.0, "moods": 0.0, "habits_weekday": 0.9},
    "all": {"jitter": 0.34, "whims": 0.0, "leave": 0.0, "moods": 0.0, "habits_weekday": 0.9},
}


def apply(knobs: dict) -> None:
    """Patch the simulator's knobs in this process."""
    import situation_sim.placement as pl
    import situation_sim.timing_constants as tc
    import situation_sim.run as run
    if "jitter" in knobs:
        f = float(knobs["jitter"])
        for k in tc.JITTER_CLASSES_MIN:
            tc.JITTER_CLASSES_MIN[k] = max(1, int(round(tc.JITTER_CLASSES_MIN[k] * f)))
        tc.JITTER_SCALE_MAX = 1.0 if f < 1 else tc.JITTER_SCALE_MAX
    if "whims" in knobs:
        for k in ("whim_base", "whim_untidy", "whim_hurry", "whim_distract", "whim_min", "whim_max"):
            pl.PARAMS[k] = float(knobs["whims"])
    if "leave" in knobs:
        for k in ("leave_untidy", "leave_low_energy", "dump_hurry", "dump_untidy", "carry_next_distract"):
            pl.PARAMS[k] = float(knobs["leave"])
    if "moods" in knobs:
        orig = run.load_episodes

        def load_eps(*a, **kw):
            eps = orig(*a, **kw)
            for spec in eps.values():
                spec["p_day"] = {k: v * float(knobs["moods"]) for k, v in spec["p_day"].items()}
            return eps
        run.load_episodes = load_eps
    if "habits_weekday" in knobs:
        orig_a = run.load_activities

        def load_acts(*a, **kw):
            acts = orig_a(*a, **kw)
            for group in ("hobbies", "chores"):
                for spec in acts.get("habits", {}).get(group, {}).values():
                    if "p" in spec and "weekday" in spec["p"] and spec["p"]["weekday"] > 0:
                        spec["p"]["weekday"] = float(knobs["habits_weekday"])
            return acts
        run.load_activities = load_acts


def generate(variant: str, seeds: List[int], out: pathlib.Path) -> None:
    """Each variant in its own subprocess so the patches never leak."""
    for s in seeds:
        d = out / variant / f"hh_s{s}"
        if (d / "hidden_state.json").exists():
            continue
        code = (f"import sys; sys.path.insert(0, '.'); from baselines.patrol.sim_variants import apply, VARIANTS; "
                f"apply(VARIANTS[{variant!r}]); import pathlib; from situation_sim.run import generate; "
                f"generate({s}, pathlib.Path({str(d)!r}), 8, 'Tuesday')")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(pathlib.Path(__file__).resolve().parents[2]),
                           capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(r.stderr[-1500:])


def oracles(variant_dir: pathlib.Path, seeds: List[int]) -> Dict[str, Dict[int, float]]:
    from baselines.patrol.bank import _Truth
    names = {1: "Wed", 2: "Thu", 3: "Fri", 4: "Sat", 5: "Sun", 6: "Mon", 7: "Tue"}
    prev_weekday = {1: 0, 2: 1, 3: 2, 4: 3, 5: 3, 6: 3, 7: 6}   # compare with: Tue(walkthrough day), Wed, Thu, Fri, Fri, Fri, Mon
    hits = {"routine": {d: [0, 0] for d in range(1, 8)}, "recency": {d: [0, 0] for d in range(1, 8)},
            "routine_movers": {d: [0, 0] for d in range(1, 8)}, "recency_movers": {d: [0, 0] for d in range(1, 8)}}
    for s in seeds:
        d = variant_dir / f"hh_s{s}"
        rows = [json.loads(l) for l in open(d / "events.jsonl")]
        st = json.loads((d / "hidden_state.json").read_text())
        objs = st["household"]["objects"]
        truth = _Truth([r for r in rows if r["kind"] == "truth"])
        movable = sorted(o for o, sp in objs.items() if not sp.get("static"))
        rng = random.Random(s)
        # movers: objects seen on more than one receptacle over the week
        seen = {o: set() for o in movable}
        for r in rows:
            if r["kind"] == "truth" and r["object_id"] in seen and r["receptacle_id"] not in (ON_PERSON, OUT_OF_HOUSE):
                seen[r["object_id"]].add(r["receptacle_id"])
        movers = {o for o, v in seen.items() if len(v) > 1}
        for day in range(1, 8):
            for _ in range(600):
                m = rng.randrange(7 * 60, 23 * 60); o = rng.choice(movable)
                t = day * DAY_SECONDS + m * 60
                now = truth.at(o, t)
                if now in (ON_PERSON, OUT_OF_HOUSE, None):
                    continue
                pd = prev_weekday[day]
                tr = pd * DAY_SECONDS + m * 60
                routine = truth.at(o, tr) if tr >= 18 * 3600 else None
                last_pass = day * DAY_SECONDS + (m // 480) * 480 * 60
                recency = truth.at(o, last_pass)
                for key, val in (("routine", routine), ("recency", recency)):
                    h = hits[key][day]; h[0] += val == now; h[1] += 1
                    if o in movers:
                        h2 = hits[key + "_movers"][day]; h2[0] += val == now; h2[1] += 1
    return {k: {names[d]: (v[0] / v[1] if v[1] else float("nan")) for d, v in dd.items()} for k, dd in hits.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--variants", nargs="+", default=list(VARIANTS))
    a = ap.parse_args(argv)
    seeds = parse_seeds(a.seeds)
    for v in a.variants:
        generate(v, seeds, a.out)
        o = oracles(a.out / v, seeds)
        print(f"== {v:16s} {VARIANTS[v]}")
        for k in ("recency", "routine", "recency_movers", "routine_movers"):
            print(f"   {k:15s} " + " ".join(f"{d} {100 * x:3.0f}" for d, x in o[k].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
