"""Diagnostic probes for the cold-start study, per household.

Three questions, each answered from the arm outputs without any LLM:

1. **Is single-winner collapse warranted?** From per-particle
   distributions at question time: the mixture's log-loss against a
   uniform average of the particles, the best single particle, a
   per-day oracle pick and a per-question oracle pick; how often the
   day's best particle changes; the best-vs-second gap per day.
   Then, by replaying the fixed mixture: the true mean weight per day
   and the cumulative sighting likelihood each particle earned — the
   quantity the weights integrate — against its question log-loss.
2. **Are two arms really identical?** Exact correct counts, the
   both/only/neither split, and the questions where their argmax
   differs.
3. **Where did re-asking lose and gain?** Fixed set vs re-asking,
   question by question: flips per week, per object, the truth and the
   prediction at the lost questions, and rest-map agreement across
   hypotheses after the last revision.

Writes ``figures/probes.md`` and returns the numbers for the report.
"""

from __future__ import annotations

import collections
import gzip
import json
import math
import pathlib
import random
from typing import Any, Dict, List, Sequence

import numpy as np

from baselines.bank import JsonlBank
from baselines.beliefs.llm_hypothesis_mixture import LLMHypothesisMixture
from baselines.household_analysis import bank_path
from baselines.llm_hypotheses.analyze_cold_start import canon, score
from baselines.llm_hypotheses.elicit import DEFAULT_OUT_DIR
from baselines.llm_hypotheses.run_cold_start import STUDY_DIR
from baselines.types import DAY_SECONDS

EPS = 1e-3


def label(name: str) -> str:
    return ("hyp" + name.split("(")[1].rstrip(")")[1:] if name.startswith("HypothesisProgram")
            else "stat")


def load(household: str, arm: str) -> List[dict]:
    p = STUDY_DIR / household / arm / "per_question.jsonl.gz"
    return [json.loads(l) for l in gzip.open(p, "rt")] if p.exists() else []


def merged(d: Dict[str, float]) -> Dict[str, float]:
    out: Dict[str, float] = collections.defaultdict(float)
    for k, v in d.items():
        out[canon(k)] += v
    return out


def ll(d: Dict[str, float], truth: str) -> float:
    return -math.log(max(d.get(truth, 0.0), EPS))


def weighting_probe(household: str, arm: str) -> Dict[str, Any]:
    rows = load(household, arm)
    rows = [r for r in rows if r.get("particles")]
    names = list(rows[0]["particles"]); labels = [label(n) for n in names]
    truths = [canon(r["truth"]) for r in rows]
    P = np.array([[ll(merged(r["particles"][n]), t) for n in names] for r, t in zip(rows, truths)])
    days = np.array([r["t_query"] // DAY_SECONDS for r in rows])
    mix = np.array([score(r)[1] for r in rows])
    uniform = np.array([-math.log(max(np.mean([merged(r["particles"][n]).get(t, 0.0) for n in names]), EPS))
                        for r, t in zip(rows, truths)])
    day_best, gaps, day_oracle = [], [], 0.0
    for d in sorted(set(days)):
        m = days == d; means = P[m].mean(0); s = np.sort(means)
        day_best.append(labels[int(means.argmin())]); gaps.append(float(s[1] - s[0])); day_oracle += means.min() * m.sum()
    return {"arm": arm, "n": len(rows), "labels": labels,
            "mixture": float(mix.mean()), "uniform_average": float(uniform.mean()),
            "single_best": float(P.mean(0).min()), "single_best_particle": labels[int(P.mean(0).argmin())],
            "per_day_oracle": float(day_oracle / len(rows)), "per_question_oracle": float(P.min(1).mean()),
            "per_particle": dict(zip(labels, [float(x) for x in P.mean(0)])),
            "day_best_sequence": day_best,
            "day_best_changes": sum(1 for a, b in zip(day_best, day_best[1:]) if a != b),
            "median_best_vs_second_gap": float(np.median(gaps))}


def replay_weights(household: str, condition: str) -> Dict[str, Any]:
    """True mean weight per day and cumulative sighting likelihood per
    particle for the FIXED set (no LLM involved)."""
    episode = next(JsonlBank(bank_path(household, 0)).episodes())
    m = LLMHypothesisMixture(random.Random(0), DEFAULT_OUT_DIR / "hypotheses" / condition)
    m.reset(episode.agent_view())
    for o in episode.initial_observations:
        m.update(o)
    labels = [label(p.name) for p in m.particles]
    per_day: Dict[int, List[List[float]]] = collections.defaultdict(list)
    for ev in episode.evidence_stream():
        per_day[ev.t // DAY_SECONDS].append(m.weights); m.update(ev)
    leader = {int(d): (labels[int(np.mean(w, 0).argmax())], float(np.mean(w, 0).max())) for d, w in per_day.items()}
    hyps = json.loads((DEFAULT_OUT_DIR / "hypotheses" / condition / f"{household}.json").read_text())["hypotheses"]
    out_moves = {("hyp" + h["hypothesis_id"][1:]): sum(1 for a in h["activities"] for mv in a["moves"] if mv["to"] == "OUT_OF_HOUSE") for h in hyps}
    return {"labels": labels, "leader_per_day": leader,
            "presence": dict(zip(labels, [float(x) for x in m.presence_totals])),
            "absence": dict(zip(labels, [float(x) for x in m.absence_totals])),
            "out_of_house_moves": out_moves,
            "days_led_by": collections.Counter(v[0] for v in leader.values())}


def identity_probe(household: str, a: str, b: str) -> Dict[str, Any]:
    A = {r["question_id"]: r for r in load(household, a)}; B = {r["question_id"]: r for r in load(household, b)}
    ca = cb = both = a_only = b_only = argdiff = 0; objs: collections.Counter = collections.Counter()
    for q in A:
        if q not in B: continue
        ta, _ = score(A[q]); tb, _ = score(B[q]); ca += ta; cb += tb
        both += ta and tb; a_only += ta and not tb; b_only += tb and not ta
        if canon(max(A[q]["dist"], key=A[q]["dist"].get)) != canon(max(B[q]["dist"], key=B[q]["dist"].get)):
            argdiff += 1; objs[A[q]["object_id"]] += 1
    return {"a": a, "b": b, "n": len(A), "correct_a": ca, "correct_b": cb, "both_right": both,
            "a_only_right": a_only, "b_only_right": b_only, "argmax_differs": argdiff,
            "argmax_differs_objects": objs.most_common(8)}


def reask_probe(household: str, condition: str) -> Dict[str, Any]:
    F = {r["question_id"]: r for r in load(household, f"passive__llm_fixed__cold_{condition}")}
    R = {r["question_id"]: r for r in load(household, f"passive__llm__cold_{condition}")}
    if not F or not R:
        return {}
    weeks = (("d3-6", 3, 6), ("d7-13", 7, 13), ("d14-20", 14, 20), ("d21-27", 21, 27))
    wk = {w: collections.Counter() for w, _, _ in weeks}
    lost: collections.Counter = collections.Counter(); gained: collections.Counter = collections.Counter()
    lldiff: collections.Counter = collections.Counter()
    truth_at_lost: collections.Counter = collections.Counter(); pred_at_lost: collections.Counter = collections.Counter()
    for q in F:
        if q not in R: continue
        tf, lf = score(F[q]); tr, lr = score(R[q]); d = F[q]["t_query"] // DAY_SECONDS
        w = next(w for w, lo, hi in weeks if lo <= d <= hi)
        if tf and not tr:
            wk[w]["lost"] += 1; lost[F[q]["object_id"]] += 1
            truth_at_lost[canon(R[q]["truth"])] += 1; pred_at_lost[canon(max(R[q]["dist"], key=R[q]["dist"].get))] += 1
        elif tr and not tf:
            wk[w]["gained"] += 1; gained[F[q]["object_id"]] += 1
        lldiff[F[q]["object_id"]] += lr - lf
    diag = json.loads((STUDY_DIR / household / f"passive__llm__cold_{condition}" / "diagnostics.json").read_text())
    rests = []
    for h in diag["final_hypotheses"]:
        r = h.get("rest") or {}
        if isinstance(r, list): r = {e["target"]: e.get("at", e.get("to")) for e in r}
        rests.append(r)
    objs = set().union(*rests) if rests else set()
    agree = sum(1 for o in objs if sum(o in r for r in rests) == len(rests) and len({r[o] for r in rests}) == 1)
    return {"condition": condition, "by_week": {w: dict(c) for w, c in wk.items()},
            "lost_most": lost.most_common(8), "gained_most": gained.most_common(8),
            "log_loss_damage": [(o, round(v, 1)) for o, v in lldiff.most_common(8)],
            "truth_at_lost": truth_at_lost.most_common(5), "predicted_at_lost": pred_at_lost.most_common(5),
            "rest_entries_after_revision": len(objs), "rest_agreed_by_all_hypotheses": agree,
            "reask_events": [(e["day"], e["reason"].split()[0], e["changed"]) for e in diag["reask"]["events"]]}


def write_probes(household: str) -> str:
    out = STUDY_DIR / household / "figures"; out.mkdir(exist_ok=True)
    L = [f"# Probes — {household}", ""]
    conds = [c for c in ("cold_named", "cold_anonymized")
             if (STUDY_DIR / household / f"passive__llm_fixed__{c}").exists()]
    L += ["## 1. Is single-winner collapse warranted?", "",
          "Log-loss per question (lower is better), from each particle's own distribution at question time.", ""]
    L += ["| arm | mixture (actual weights) | uniform average | single best particle | per-day oracle pick | per-question oracle pick | day-best changes | median best-vs-2nd gap |",
          "|---|---|---|---|---|---|---|---|"]
    probes = {}
    for c in conds:
        for kind in ("llm_fixed", "llm"):
            arm = f"passive__{kind}__{c}"
            if not (STUDY_DIR / household / arm).exists(): continue
            p = weighting_probe(household, arm); probes[arm] = p
            L.append(f"| {arm.replace('passive__', '').replace('__', ' · ')} | {p['mixture']:.3f} | {p['uniform_average']:.3f} | {p['single_best']:.3f} ({p['single_best_particle']}) | {p['per_day_oracle']:.3f} | {p['per_question_oracle']:.3f} | {p['day_best_changes']}/{len(p['day_best_sequence']) - 1} days | {p['median_best_vs_second_gap']:.3f} |")
    L.append("")
    for c in conds:
        w = replay_weights(household, c)
        L += [f"### Fixed set, {c}: who held the weight, and why", "",
              "Days led by each hypothesis (true weights, replayed): " + ", ".join(f"{k} {v}" for k, v in w["days_led_by"].most_common()), "",
              "| particle | sighting log-likelihood earned (presence) | (absence, weighted) | question log-loss | OUT_OF_HOUSE moves |", "|---|---|---|---|---|"]
        p = probes.get(f"passive__llm_fixed__{c}", {}).get("per_particle", {})
        for lab in w["labels"]:
            L.append(f"| {lab} | {w['presence'][lab]:.0f} | {w['absence'][lab]:.0f} | {p.get(lab, float('nan')):.3f} | {w['out_of_house_moves'].get(lab, '—')} |")
        L.append("")
    if len(conds) == 2:
        idp = identity_probe(household, "passive__llm_fixed__cold_named", "passive__llm_fixed__cold_anonymized")
        L += ["## 2. Named vs anonymized fixed sets — question by question", "",
              f"- correct: named {idp['correct_a']}, anonymized {idp['correct_b']} of {idp['n']}",
              f"- both right {idp['both_right']}, named-only {idp['a_only_right']}, anonymized-only {idp['b_only_right']}",
              f"- argmax differs on {idp['argmax_differs']} questions ({idp['argmax_differs'] / idp['n']:.1%}); objects: {idp['argmax_differs_objects']}", ""]
    L += ["## 3. Re-asking vs fixed set — where it lost and gained", ""]
    for c in conds:
        r = reask_probe(household, c.replace("cold_", ""))
        if not r: continue
        L += [f"### {c}", "", f"Re-asks: {r['reask_events']}", "",
              "| week | fixed right, re-ask wrong | re-ask right, fixed wrong |", "|---|---|---|"]
        for w, cnt in r["by_week"].items():
            L.append(f"| {w} | {cnt.get('lost', 0)} | {cnt.get('gained', 0)} |")
        L += ["", f"- objects where re-asking lost most: {r['lost_most']}", f"- objects where it gained most: {r['gained_most']}",
              f"- log-loss damage per object (summed, re-ask − fixed): {r['log_loss_damage']}",
              f"- at the lost questions, truth was: {r['truth_at_lost']}; re-ask predicted: {r['predicted_at_lost']}",
              f"- after the last revision: {r['rest_entries_after_revision']} objects have rest entries, and all hypotheses give the SAME rest for {r['rest_agreed_by_all_hypotheses']} of them", ""]
    text = "\n".join(L) + "\n"; (out / "probes.md").write_text(text); return text


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--household", default="hh_001")
    print(write_probes(ap.parse_args().household))
