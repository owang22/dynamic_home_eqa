"""E0 — no-prior baselines to complete H1. Does the LLM zero-shot prior even
BEAT dumb no-prior baselines? If LLM-atyp still beats uniform, H1 is "the
prior's advantage collapses under atypicality", not "the prior is harmful".

Baselines (no LLM), scored on the SAME D=0 episodes the LLM saw (sample_stream
is seeded, so a fixed n reproduces the identical set):
  uniform     — predict uniformly over candidates; accuracy = mean(1/n_cand).
  class_freq  — b2's static class prior: predict the candidate best matching the
                class's typ-population modal (room, receptacle-category). No
                household data, no decay dynamics.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict

import numpy as np

from dynbelief.h2 import core
from dynbelief.experiments.streams import sample_stream
from dynbelief.profiles.schema import default_class, load_profile


def _recep_cat(rid: str) -> str:
    import re
    return re.sub(r"_[a-z]?\d+$", "", rid).split("_")[0]


def typ_class_target():
    """class -> (modal room, modal receptacle-category) across typ_v1 profiles."""
    room_c, cat_c = defaultdict(Counter), defaultdict(Counter)
    for hh in core.households("typ_v1"):
        base = core.load_hh("typ_v1", hh)["reg"]["profile"]["household"].split("__")[0]
        prof = load_profile(core.MANUAL_DIR / f"{base}.yaml")
        rooms = {r.id: r.room for r in prof.receptacles}
        for o, pl in prof.placements.items():
            c = default_class(o)
            room_c[c][rooms.get(pl.home, "?")] += 1
            cat_c[c][_recep_cat(pl.home)] += 1
    return {c: (room_c[c].most_common(1)[0][0], cat_c[c].most_common(1)[0][0])
            for c in room_c}


def class_freq_predict(cls, cand_set, room_of):
    """Pick the candidate best matching the class's typ-modal (room, category)."""
    tgt = _TYP.get(cls)
    if tgt is None:
        return cand_set[0]
    room, cat = tgt
    in_room = [c for c in cand_set if c != "elsewhere" and room_of.get(c) == room]
    if in_room:
        by_cat = [c for c in in_room if _recep_cat(c) == cat]
        return (by_cat or in_room)[0]
    by_cat = [c for c in cand_set if c != "elsewhere" and _recep_cat(c) == cat]
    return (by_cat or [c for c in cand_set if c != "elsewhere"] or cand_set)[0]


_TYP = {}


def run():
    global _TYP
    _TYP = typ_class_target()
    banks = ["typ_v1", "atyp_v2", "atyp_authored_v1"]
    rows = []
    for bank in banks:
        for hh in core.households(bank):
            h = core.load_hh(bank, hh)
            room_of = {r_id: None for r_id in h["cand_set"]}
            prof = load_profile(core.MANUAL_DIR / f"{h['reg']['profile']['household'].split('__')[0]}.yaml")
            room_of = {r.id: r.room for r in prof.receptacles}
            for stream in core.E1_STREAMS:
                eps = sample_stream(h["hd"], bank, hh, 0, stream, core.N_PER_CELL)
                for ep in eps:
                    n = len(h["cand_set"])
                    rows.append({"bank": bank, "arm": "uniform", "correct": 1.0 / n,
                                 "stream": stream, "class": default_class(ep["object"])})
                    pred = class_freq_predict(default_class(ep["object"]), h["cand_set"], room_of)
                    rows.append({"bank": bank, "arm": "class_freq",
                                 "correct": int(pred == ep["true_receptacle"]),
                                 "stream": stream, "class": default_class(ep["object"])})
    # LLM zero-shot from the D2 cache
    for f, lbl in [("rows_D0_deepseek-v4-flash.jsonl", None),
                   ("rows_D0_deepseek-v4-flash_authored.jsonl", None)]:
        p = core.REPO_ROOT / "results" / "e1" / f
        if p.exists():
            for l in p.read_text().splitlines():
                if not l.strip():
                    continue
                r = json.loads(l)
                if r["history_days"] == 0:
                    rows.append({"bank": r["bank"], "arm": "llm_zeroshot",
                                 "correct": r["correct"], "stream": r.get("stream"),
                                 "class": r["class"]})
    core.OUT.mkdir(parents=True, exist_ok=True)
    (core.OUT / "e0_rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    _report(rows)


def _report(rows):
    banks = ["typ_v1", "atyp_v2", "atyp_authored_v1"]
    arms = ["uniform", "class_freq", "llm_zeroshot"]
    print("\n" + "=" * 68)
    print("E0 — no-prior baselines vs LLM zero-shot (D=0), per bank")
    print("=" * 68)
    print(f"\n{'bank':20s} " + " ".join(f"{a:>13}" for a in arms))
    print("-" * 68)
    acc = defaultdict(dict)
    for bank in banks:
        for arm in arms:
            v = [r["correct"] for r in rows if r["bank"] == bank and r["arm"] == arm]
            acc[bank][arm] = float(np.mean(v)) if v else None
        cells = " ".join((f"{acc[bank][a]:>13.3f}" if acc[bank][a] is not None else f"{'-':>13}")
                         for a in arms)
        print(f"{bank:20s} {cells}")
    print("\nVerdict per bank (is the zero-shot prior HARMFUL = below uniform?):")
    for bank in banks:
        z, u, cf = acc[bank]["llm_zeroshot"], acc[bank]["uniform"], acc[bank]["class_freq"]
        if z is None:
            continue
        vs_u = "beats" if z > u else "BELOW"
        vs_cf = "beats" if (cf is None or z > cf) else ("ties" if abs(z-(cf or 0))<0.03 else "below")
        print(f"  {bank:20s} llm={z:.3f}  {vs_u} uniform({u:.3f}), {vs_cf} class_freq({cf:.3f})")


if __name__ == "__main__":
    run()
