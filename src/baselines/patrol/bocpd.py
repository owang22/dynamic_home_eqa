"""Change-detection baseline: BOCPD over the counter's surprise, global count reset.

    python3 -m baselines.patrol.bocpd --bank hh_s10_p2.jsonl --out log.jsonl --variant detect|told|none
                                      [--granularity patrol|day] [--hazard 20] [--recent 2] [--threshold 0.5] [--strength 1.0]

The belief is the frozen study's most-frequent counter (sighting histogram,
Dirichlet mean, negative evidence off, spots-only answers).  Its *surprise*
is the mean log-loss of its prediction on the patrol's positive sightings,
computed before those sightings are folded in; one value per patrol instant
(``patrol``) or per day (``day``: the mean over the day's patrols, stepped at
the first patrol of the next day).

Bayesian online changepoint detection (Adams and MacKay, 2007) runs over
that series with a constant hazard ``1/hazard`` and a Normal-Gamma model of
the surprise (unknown mean and variance, Student-t predictive).  When the
run-length posterior puts at least ``threshold`` of its mass on run lengths
of at most ``recent`` steps, the counter's sighting counts for **every**
object are multiplied by ``1 - strength * mass`` (once per ``recent``-step
window).  Variants:

* ``detect`` -- the reset is triggered by the detector (not-told arm);
* ``told``   -- the reset (factor ``1 - strength``) is triggered by the
                residents' message at the first question of each message
                day; the detector still runs and is logged, but never
                resets (the "trust nothing" control);
* ``listed`` -- the reset is triggered by the message but applied only to
                the objects on the affected list for that household-day
                (``--lists``: the output of ``patrol.affected_llm``); the
                targeted counterpart of ``told``;
* ``none``   -- no reset: the plain most-frequent counter, with the full
                distribution logged (the input the conformal wrapper needs).

Log rows carry the classical harness fields (answer, top_prob, correct,
truth, ...) plus ``dist`` (spots-only distribution, entries above 1e-4),
``reset_mass`` (the detector's recent-change mass at question time),
``discount`` (the product of the factors applied so far on that day) and a
``fires`` list in the sidecar ``<out>.fires.json`` (time, mass, factor,
day, trigger) with the surprise series.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import sys
from typing import Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.beliefs.most_frequent import MostFrequentLocation
from baselines.patrol.run import spots_only
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE, Prediction, SenseResult

NEGATIVE = {"off": {"negative_half_life_h": 1e-9}, "on": {}}
"""Most-frequent specs: empty-look suppression off (the frozen config's
stated setting) or on (the package default, 24 h half-life, which is what
the earlier held-out classical logs actually ran with)."""
DIST_MIN = 1e-4


class DiscountedMostFrequent(MostFrequentLocation):
    """Most-frequent counter whose sighting counts can be discounted at
    chosen instants: a sighting made at ``t_obs`` weighs the product of
    every factor applied after ``t_obs``.  Nothing else changes."""

    def __init__(self, rng: random.Random, **kw) -> None:
        super().__init__(rng, **kw)
        self._discounts: List[Tuple[int, float]] = []

    @property
    def name(self) -> str:
        return "MostFrequentLocation" if self._half_life_s is None else f"MostFrequentLocation(hl={self._half_life_s / 3600:g}h)"

    def reset(self, context) -> None:
        super().reset(context)
        self._discounts = []

    def discount(self, t: int, factor: float, objects: Optional[set] = None) -> None:
        """Apply ``factor`` at ``t`` to every object (``objects`` None) or to the named ones only."""
        self._discounts.append((t, factor, None if objects is None else frozenset(objects)))

    def weight_since(self, t_obs: int, t: int, object_id: Optional[str] = None) -> float:
        """Product of the discount factors applied after ``t_obs`` up to ``t`` that cover ``object_id``."""
        w = 1.0
        for ta, f, objs in self._discounts:
            if t_obs < ta <= t and (objs is None or object_id in objs):
                w *= f
        return w

    def _predict_for_object(self, object_id: str, history: List[Tuple[int, str]], t: int) -> Prediction:
        if not history:
            return super()._predict_for_object(object_id, history, t)
        counts: Dict[str, float] = {}
        for ot, rec in history:
            age = 1.0 if self._half_life_s is None else 2.0 ** (-max(0, t - ot) / self._half_life_s)
            counts[rec] = counts.get(rec, 0.0) + age * self.weight_since(ot, t, object_id)
        return self.dirichlet_normalized(counts, tie_break_recency=history)

    def negative_factors(self, object_id: str, t: int) -> Dict[str, float]:
        """Empty looks are forgotten by the same discounts: the suppression
        ``2^(-age/half-life)`` of an empty look at ``t_obs`` is scaled by
        the factors applied after it (no-op when suppression is off)."""
        looks = self.negative_observations(object_id, t)
        if not looks:
            return {}
        allowed = set(self._context.sensable_receptacle_ids) | {ON_PERSON}
        half_life_s = self.negative_half_life_h * 3600.0
        return {rec: 1.0 - self.weight_since(t_obs, t, object_id) * 2.0 ** (-max(0, t - t_obs) / half_life_s)
                for rec, t_obs in looks.items() if rec in allowed}


class Bocpd:
    """Adams-MacKay with a Normal-Gamma (unknown mean, unknown variance)
    observation model and constant hazard.  ``step(x)`` returns the
    run-length posterior; ``recent_mass(k)`` is P(run length <= k)."""

    def __init__(self, hazard: float, mu0: float, kappa0: float = 1.0, alpha0: float = 2.0, beta0: float = 1.0):
        self.h = 1.0 / hazard
        self.mu0, self.kappa0, self.alpha0, self.beta0 = mu0, kappa0, alpha0, beta0
        self.mu = [mu0]
        self.kappa = [kappa0]
        self.alpha = [alpha0]
        self.beta = [beta0]
        self.r = [1.0]

    @staticmethod
    def _student_t_pdf(x: float, df: float, loc: float, scale2: float) -> float:
        z = (x - loc) ** 2 / (df * scale2)
        lg = math.lgamma((df + 1) / 2) - math.lgamma(df / 2)
        return math.exp(lg) / math.sqrt(df * math.pi * scale2) * (1 + z) ** (-(df + 1) / 2)

    def step(self, x: float) -> List[float]:
        n = len(self.r)
        pred = []
        for i in range(n):
            df = 2 * self.alpha[i]
            scale2 = self.beta[i] * (self.kappa[i] + 1) / (self.alpha[i] * self.kappa[i])
            pred.append(self._student_t_pdf(x, df, self.mu[i], scale2))
        growth = [self.r[i] * pred[i] * (1 - self.h) for i in range(n)]
        cp = sum(self.r[i] * pred[i] * self.h for i in range(n))
        new_r = [cp] + growth
        z = sum(new_r)
        if z <= 0:
            new_r = [1.0] + [0.0] * n
            z = 1.0
        self.r = [v / z for v in new_r]
        # posterior updates for every run length, then a fresh prior at r=0
        mu, kappa, alpha, beta = [self.mu0], [self.kappa0], [self.alpha0], [self.beta0]
        for i in range(n):
            k, m, a, b = self.kappa[i], self.mu[i], self.alpha[i], self.beta[i]
            mu.append((k * m + x) / (k + 1))
            kappa.append(k + 1)
            alpha.append(a + 0.5)
            beta.append(b + k * (x - m) ** 2 / (2 * (k + 1)))
        self.mu, self.kappa, self.alpha, self.beta = mu, kappa, alpha, beta
        # keep the tail short
        if len(self.r) > 400:
            self.r, self.mu, self.kappa, self.alpha, self.beta = (v[:400] for v in (self.r, self.mu, self.kappa, self.alpha, self.beta))
            z = sum(self.r)
            self.r = [v / z for v in self.r]
        return self.r

    def recent_mass(self, k: int) -> float:
        return sum(self.r[: k + 1])


def surprise_of(belief: DiscountedMostFrequent, item: SenseResult, movers: bool) -> List[float]:
    """-log p(seen spot) under the counter's spots-only prediction, for
    every object sighted in ``item`` (before it is folded in).  With
    ``movers`` only objects already seen in at least two different spots
    count: the objects that never move say nothing about a routine shift
    and dilute the mean."""
    out = []
    for o in sorted(item.contents):
        if o not in belief.known_objects:
            belief.ensure_object(o, item.object_classes.get(o, ""))
        if movers and len({rec for _, rec in belief._history.get(o, [])}) < 2:
            continue
        pred = belief.predict(o, item.t)
        dist, _ = spots_only(dict(pred.distribution))
        out.append(-math.log(max(dist.get(item.receptacle_id, 0.0), 1e-6)))
    return out


def run(bank_path: pathlib.Path, variant: str, granularity: str, hazard: float, recent: int,
        threshold: float, strength: float, seed: int = 0, negative: str = "off", movers: bool = False,
        lists: Optional[Dict[int, set]] = None, half_life_h: Optional[float] = None) -> Tuple[List[dict], dict]:
    header = json.loads(bank_path.read_text().splitlines()[0])
    episode = next(iter(JsonlBank(bank_path).episodes()))
    tag = {"household": header["household_id"], "patrol_hours": header["patrol_hours"], "look": "off",
           "patrol_label": header.get("patrol_label", f"p{header['patrol_hours']}"), "seed": int(header.get("seed", seed)),
           "variant": variant, "granularity": granularity, "negative_evidence": negative, "movers": movers,
           "half_life_h": half_life_h}
    rng = random.Random(f"{seed}:bocpd:{variant}")
    belief = DiscountedMostFrequent(rng, half_life_h=half_life_h, **NEGATIVE[negative])
    context = episode.agent_view()
    belief.reset(context)
    for obs in episode.initial_observations:
        belief.update(obs)
    message_days = sorted({int(m["day_index"]) for m in header.get("hint_messages", [])})
    evidence = episode.evidence_stream()
    questions = sorted((q for day in episode.questions_by_day for q in day), key=lambda q: (q.t_query, q.question_id))

    # --- pass 1: surprise per patrol instant, folding the evidence in as we go
    # (the detector and the resets are replayed in pass 2 with the questions
    # interleaved, so the belief here is a throwaway copy)
    probe = DiscountedMostFrequent(random.Random(0), half_life_h=half_life_h, **NEGATIVE[negative])
    probe.reset(context)
    for obs in episode.initial_observations:
        probe.update(obs)
    per_instant: Dict[int, List[float]] = {}
    for item in evidence:
        if isinstance(item, SenseResult):
            per_instant.setdefault(item.t, []).extend(surprise_of(probe, item, movers))
            for o in item.contents:
                probe.ensure_object(o, item.object_classes.get(o, ""))
        probe.update(item)
    instants = sorted(per_instant)
    series = [(t, sum(v) / len(v)) for t in instants for v in [per_instant[t]] if v]
    if granularity == "day":
        by_day: Dict[int, List[float]] = {}
        for t, x in series:
            by_day.setdefault(t // DAY_SECONDS, []).append(x)
        # a day's value is stepped at the first instant of the next day
        series = [((d + 1) * DAY_SECONDS, sum(v) / len(v)) for d, v in sorted(by_day.items())]
    # Detector prior from the second half of the walkthrough day (day 0: the
    # counter starts empty, so the morning's surprise is the cold start, not
    # the household).  Those steps are also fed to the detector so the run
    # length is not trivially short when day 1 starts; no reset before day 1.
    warm = [x for t, x in series if DAY_SECONDS // 2 <= t < DAY_SECONDS]
    steps = [(t, x) for t, x in series if t >= DAY_SECONDS // 2]
    mu0 = sum(warm) / len(warm) if warm else 1.0
    var0 = (sum((x - mu0) ** 2 for x in warm) / max(1, len(warm) - 1)) if len(warm) > 1 else 0.25
    det = Bocpd(hazard=hazard, mu0=mu0, kappa0=1.0, alpha0=2.0, beta0=max(0.02, 2.0 * var0))

    # --- pass 2: replay with questions, detector steps and resets interleaved
    cursor = 0
    step_i = 0
    fires: List[dict] = []
    mass_log: List[dict] = []
    reset_mass = 0.0
    last_fire_step = -10 ** 9
    day_discount: Dict[int, float] = {}
    told_done: set = set()
    records = []

    def apply_reset(t: int, mass: float, trigger: str, objects: Optional[set] = None) -> None:
        factor = max(0.0, 1.0 - strength * mass)
        belief.discount(t, factor, objects)
        d = t // DAY_SECONDS
        day_discount[d] = day_discount.get(d, 1.0) * factor
        fires.append({"t": t, "day": d, "mass": round(mass, 4), "factor": round(factor, 4), "trigger": trigger,
                      "objects": sorted(objects) if objects is not None else None})

    def advance_detector(upto: int) -> None:
        nonlocal step_i, reset_mass, last_fire_step
        while step_i < len(steps) and steps[step_i][0] <= upto:
            t, x = steps[step_i]
            det.step(x)
            reset_mass = det.recent_mass(recent)
            mass_log.append({"t": t, "day": t // DAY_SECONDS, "x": round(x, 4), "mass": round(reset_mass, 4)})
            # no reset before day 1 nor before the run length can exceed ``recent``
            if (variant == "detect" and t >= DAY_SECONDS and step_i >= len(warm) + recent + 1
                    and reset_mass >= threshold and step_i - last_fire_step > recent):
                apply_reset(t, reset_mass, "detect")
                last_fire_step = step_i
            step_i += 1

    for q in questions:
        while cursor < len(evidence) and evidence[cursor].t <= q.t_query:
            item = evidence[cursor]
            if isinstance(item, SenseResult):
                for o in item.contents:
                    belief.ensure_object(o, item.object_classes.get(o, ""))
            belief.update(item)
            cursor += 1
            advance_detector(item.t)
        advance_detector(q.t_query)
        if variant == "told" and q.day_index in message_days and q.day_index not in told_done:
            told_done.add(q.day_index)
            apply_reset(q.t_query, 1.0, "message")
        if variant == "listed" and q.day_index in message_days and q.day_index not in told_done:
            told_done.add(q.day_index)
            apply_reset(q.t_query, 1.0, "message+list", set((lists or {}).get(q.day_index, set())))
        belief.ensure_object(q.object_id, q.object_class)
        pred = belief.predict(q.object_id, q.t_query)
        dist, dropped = spots_only(dict(pred.distribution))
        answer = max(dist, key=lambda r: (dist[r], r)) if dist else pred.argmax
        truth = episode.true_location(q.object_id, q.t_query)
        records.append({**tag, "belief": belief.name, "day_index": q.day_index, "question_id": q.question_id,
                        "object_id": q.object_id, "object_class": q.object_class, "t_query": q.t_query,
                        "answer": answer, "top_prob": round(dist.get(answer, 0.0), 4),
                        "raw_answer": pred.argmax, "raw_top_prob": round(pred.distribution.get(pred.argmax, 0.0), 4),
                        "p_outside": round(dropped, 4), "truth": truth, "correct": answer == truth,
                        "dist": {r: round(p, 5) for r, p in sorted(dist.items()) if p >= DIST_MIN},
                        "reset_mass": round(reset_mass, 4), "discount": round(day_discount.get(q.day_index, 1.0), 4)})
    side = {"household": header["household_id"], "variant": variant, "granularity": granularity, "negative_evidence": negative, "movers": movers,
            "params": {"hazard": hazard, "recent": recent, "threshold": threshold, "strength": strength},
            "prior": {"mu0": mu0, "var0": var0}, "shift_days": header["shift_days"], "message_days": message_days,
            "series": mass_log, "fires": fires}
    return records, side


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--variant", default="detect", choices=("detect", "told", "listed", "none"))
    ap.add_argument("--lists", type=pathlib.Path, default=None, help="affected_llm lists.jsonl (variant listed)")
    ap.add_argument("--granularity", default="patrol", choices=("patrol", "day"))
    ap.add_argument("--hazard", type=float, default=20.0, help="expected run length between changes, in steps")
    ap.add_argument("--recent", type=int, default=2, help="'recent change' = run length at most this many steps")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--strength", type=float, default=1.0, help="factor = 1 - strength * mass")
    ap.add_argument("--negative", default="off", choices=tuple(NEGATIVE), help="empty-look suppression")
    ap.add_argument("--movers", action="store_true", help="surprise over objects already seen in two or more spots")
    ap.add_argument("--half-life", type=float, default=None, help="sighting half-life in hours (forgetting); default none")
    a = ap.parse_args(argv)
    lists = None
    if a.variant == "listed":
        hh = json.loads(a.bank.read_text().splitlines()[0])["household_id"]
        lists = {int(r["day_index"]): set(r["objects"]) for r in (json.loads(l) for l in a.lists.open()) if r["household"] == hh}
    recs, side = run(a.bank, a.variant, a.granularity, a.hazard, a.recent, a.threshold, a.strength, negative=a.negative,
                     movers=a.movers, lists=lists, half_life_h=a.half_life)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    a.out.with_suffix(".fires.json").write_text(json.dumps(side, indent=1, sort_keys=True))
    n_ok = sum(r["correct"] for r in recs)
    print(f"{side['household']} {a.variant}/{a.granularity}/neg-{a.negative} {n_ok}/{len(recs)} fires={len(side['fires'])} "
          f"on days {sorted({f['day'] for f in side['fires']})} shift={side['shift_days']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
