"""E2 transition-kernel elicitation (feeds K2). Elicits q rows

    q_c[daypart, day-type, source] = P(destination one hour later | at source)

Grid reduced for affordability (brief): 6 dayparts x {weekday, weekend} = 12
(NOT 48 bins); expanded to the kernel's bins at use time. Sources capped at 6
per class (the receptacles the class plausibly visits, from the vocabulary; the
cap rule is logged). To stay well under ~3k calls/model we BATCH: ONE call per
(class, source) returns the full 6-daypart x 2-day-type distribution grid, so
the call count is sum_c |sources_c| per model, reported before running.

Source models gpt-5.4-mini + gpt-5.5 only (never Claude). 5 samples averaged.
Fixed hashed prompt. No profile text, no observations (one-shot prior). Rows
renormalized to sum 1; any renormalized row logged.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np

from dynbelief.e2.elicit import ALLOWED_MODELS

DAYPARTS = ["00-04", "04-08", "08-12", "12-16", "16-20", "20-24"]
DAYTYPES = ["weekday", "weekend"]
MAX_SOURCES = 6

_SYSTEM = (
    "You estimate short-horizon object movement in a home from general world "
    "knowledge only. Given an object currently at a named receptacle at a time "
    "of day, you give the probability distribution over where it will be ONE "
    "HOUR later. Use population-typical behaviour; do not assume a specific "
    "household schedule beyond the generic descriptor."
)


def build_prompt(descriptor, cls, source, receptacles):
    dests = ", ".join(receptacles + ["elsewhere"])
    return (f"Household type: {descriptor}.\n\n"
            f"Object class: {cls}. It is currently at: {source}.\n"
            f"Possible locations one hour later: {dests}.\n\n"
            f"For each of the {len(DAYPARTS)} dayparts ({', '.join(DAYPARTS)}) and "
            f"each day-type (weekday, weekend), give the probability distribution "
            f"over the possible locations one hour later (each distribution sums to ~1).")


def _schema(receptacles):
    dests = receptacles + ["elsewhere"]
    return {
        "type": "object",
        "properties": {"cells": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "daypart": {"type": "string", "enum": DAYPARTS},
                "day_type": {"type": "string", "enum": DAYTYPES},
                "distribution": {"type": "array",
                                 "items": {"type": "object",
                                           "properties": {"location": {"type": "string"},
                                                          "p": {"type": "number"}},
                                           "required": ["location", "p"],
                                           "additionalProperties": False}}},
            "required": ["daypart", "day_type", "distribution"],
            "additionalProperties": False}}},
        "required": ["cells"], "additionalProperties": False}


def sources_for_class(cls, receptacles, housekeep=None):
    """Cap MAX_SOURCES plausible sources per class. Rule (logged): the object's
    home-ish + kitchen/living surfaces + 'elsewhere' — generator-INDEPENDENT
    (uses only the receptacle vocabulary, never the profile). Here: the first
    MAX_SOURCES receptacles by a fixed lexical priority (sink/counter/table/
    sofa/nightstand/desk/hook), else vocabulary order."""
    priority = ["counter", "sink", "table", "sofa", "nightstand", "desk", "hook",
                "cupboard", "shelf", "stand"]
    def rank(r):
        for i, p in enumerate(priority):
            if p in r:
                return i
        return len(priority)
    return sorted(receptacles, key=rank)[:MAX_SOURCES]


def prompt_hash(descriptor, receptacles):
    return hashlib.sha256((_SYSTEM + descriptor + ",".join(receptacles)
                           + json.dumps(_schema(receptacles))).encode()).hexdigest()[:12]


def _daypart_idx(daypart):
    return DAYPARTS.index(daypart)


def elicit_class_source(client, descriptor, cls, source, receptacles, n_samples=5):
    """Returns {(daypart_idx, is_weekend): np.array over [receptacles+elsewhere]}
    averaged over samples. Logs renormalized rows count via return meta."""
    dests = receptacles + ["elsewhere"]
    didx = {d: i for i, d in enumerate(dests)}
    acc = {}
    renorm = 0
    raw = []
    for s in range(n_samples):
        txt = client.generate(_SYSTEM, build_prompt(descriptor, cls, source, receptacles),
                              _schema(receptacles), seed=2000 + s, temperature=0.7)
        parsed = json.loads(txt); raw.append(parsed)
        for cell in parsed.get("cells", []):
            key = (_daypart_idx(cell["daypart"]), int(cell["day_type"] == "weekend"))
            v = np.zeros(len(dests))
            for e in cell["distribution"]:
                if e["location"] in didx:
                    v[didx[e["location"]]] += max(0.0, float(e["p"]))
            if v.sum() <= 0:
                continue
            if abs(v.sum() - 1) > 0.05:
                renorm += 1
            acc.setdefault(key, []).append(v / v.sum())
    out = {k: np.mean(vs, axis=0) for k, vs in acc.items()}
    return out, {"renormalized_rows": renorm, "raw": raw}


def elicit_all(client, models, manual_dir, out_dir, bases):
    """Build q for each base profile: {(class,daypart,wknd,source): np.array over
    the base's candidate axis}. Writes results/e2/kernel_priors/<base>.npz-ish JSON."""
    from dynbelief.profiles.schema import load_profile, default_class
    out_dir.mkdir(parents=True, exist_ok=True)
    total_calls = 0
    for base, descriptor in bases.items():
        prof = load_profile(manual_dir / f"{base}.yaml")
        receptacles = sorted(prof.receptacle_ids)
        classes = sorted({p.cls for p in prof.placements.values()})
        # count calls first (report before running)
        plan = {c: sources_for_class(c, receptacles) for c in classes}
        n_calls = sum(len(v) for v in plan.values()) * len(models)
        total_calls += n_calls
        print(f"[elicit_kernel] {base}: {n_calls} calls "
              f"({len(classes)} classes x <= {MAX_SOURCES} sources x {len(models)} models)")
    print(f"[elicit_kernel] TOTAL {total_calls} calls across {len(bases)} bases")
    if total_calls > 3000 * len(models):
        print("[elicit_kernel] WARNING >3k/model — consider coarsening dayparts")
    # elicit
    from dynbelief.llm_agent.clients import OpenAIClient
    for base, descriptor in bases.items():
        prof = load_profile(manual_dir / f"{base}.yaml")
        receptacles = sorted(prof.receptacle_ids)
        cand = receptacles + ["elsewhere"]
        classes = sorted({p.cls for p in prof.placements.values()})
        q = {}
        renorm_total = 0
        for model in models:
            if not any(model.startswith(m) for m in ALLOWED_MODELS):
                raise ValueError(f"source must be one of {ALLOWED_MODELS}; got {model}")
            client = OpenAIClient(model=model)
            for cls in classes:
                for src in sources_for_class(cls, receptacles):
                    grid, meta = elicit_class_source(client, descriptor, cls, src, receptacles)
                    renorm_total += meta["renormalized_rows"]
                    for (dp, wk), dist in grid.items():
                        key = (cls, dp, wk, src)
                        q.setdefault(key, []).append(dist)
        q_avg = {f"{c}|{dp}|{wk}|{s}": np.mean(v, axis=0).tolist()
                 for (c, dp, wk, s), v in q.items()}
        (out_dir / f"{base}.json").write_text(json.dumps({
            "base": base, "descriptor": descriptor, "models": list(models),
            "candidates": cand, "renormalized_rows": renorm_total,
            "prompt_hash": prompt_hash(descriptor, receptacles),
            "source_cap_rule": "lexical priority sink/counter/table/sofa/nightstand/desk/hook",
            "q": q_avg}, indent=1))
        print(f"[elicit_kernel] wrote {base}: {len(q_avg)} q-rows, {renorm_total} renormalized")
