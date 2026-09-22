"""Uncertainty-aware wrappers around the most-frequent counter, as patrol-harness agents.

    python3 -m baselines.patrol.uq_agents --bank hh_s10_t03.jsonl --out log.jsonl --agent none|ocp|martingale|bma [options]

See results/confidence_shift_2026-09-20/uq/METHODS.md for the papers, the adaptations and the
expectations.  Every agent replays the bank's evidence stream (patrol visits, walkthrough, found-it
feedback) through the counter and answers each question with one in-house spot and a confidence,
logging the classical row format plus agent columns.

* ``none``        the plain counter (``--half-life`` optional); must equal the classical log.
* ``ocp``         online conformal with decaying step sizes (Angelopoulos, Barber, Bates 2024), score
                  ``1 - Rel * p(y)`` with Rel the freshness of the object's evidence (Ren et al. 2024,
                  relevance-weighted scores); set = spots with score <= q_t; confidence = 1/|set|;
                  ``--look`` spends the free look when the set holds more than one spot.
* ``nexcp``       conformal beyond exchangeability (Barber, Candès, Ramdas, Tibshirani 2023): weighted
                  quantile of the past scores with time-decaying weights (``--tau-w`` hours), unit mass at +inf.
* ``martingale``  conformal test martingale over the question errors (Vovk; e-detectors, Shin et al.
                  2024); when it crosses 1/delta the counter's counts are discounted for every object
                  and the calibration window restarts.
* ``bma``         fixed-share model averaging over counters with several half-lives (Herbster and
                  Warmuth 1998; Raftery et al. 2010); confidence = top probability of the mixture.
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
from baselines.beliefs.last_observation import LastObservation
from baselines.beliefs.timetable import TimetableConfig, TimetableLookup
from baselines.patrol.bocpd import NEGATIVE, DiscountedMostFrequent
from baselines.patrol.run import choose_room, look_results, spots_only
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE, Observation, SenseResult

DIST_MIN = 1e-4
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
TOL = 1e-6


class DiscountedTimetable(TimetableLookup):
    """Timetable whose bin counts can be discounted at chosen instants (the martingale reset):
    a sighting made at ``t_obs`` weighs the product of every factor applied after it, on top
    of the half-life decay.  With no discount applied it is the plain TimetableLookup."""

    def __init__(self, rng: random.Random, config: TimetableConfig, **kw) -> None:
        super().__init__(rng, config, **kw)
        self._discounts: List[Tuple[int, float, Optional[frozenset]]] = []

    def reset(self, context) -> None:
        super().reset(context)
        self._discounts = []

    def discount(self, t: int, factor: float, objects=None) -> None:
        """``objects=None`` discounts every object (a global reset); otherwise only the named object ids —
        mirrors ``DiscountedMostFrequent.discount`` in bocpd.py (P4: this used to accept and silently drop
        ``objects``, so every "targeted" reset was actually global; every prior caller passed ``objects=None``
        so nothing prior was affected, but a real per-object/per-person reset needs this to work)."""
        self._discounts.append((t, factor, None if objects is None else frozenset(objects)))

    def weight_since(self, t_obs: int, t: int, object_id: Optional[str] = None) -> float:
        w = 1.0
        for ta, f, objs in self._discounts:
            if t_obs < ta <= t and (objs is None or object_id in objs):
                w *= f
        return w

    def _predict_for_object(self, object_id: str, history: List[Tuple[int, str]], t: int):
        """Overrides the base's ``_predict_for_object`` (not ``_predict_from_history``) because only this hook
        receives ``object_id`` — needed to look up this object's own discount weight."""
        if not history:
            return self._cold_start(object_id, t)
        if not self._discounts:
            return super()._predict_from_history(history, t)
        query_bin = self._config.bin_of(t)
        in_bin = [(ot, rec) for ot, rec in history if self._config.bin_of(ot) == query_bin]
        if not in_bin and self._config.empty_bin == "last_seen":
            return super()._predict_from_history(history, t)
        pool = in_bin if in_bin else history
        counts: Dict[str, float] = {}
        for ot, rec in pool:
            age = 1.0 if self._half_life_s is None else 2.0 ** (-max(0, t - ot) / self._half_life_s)
            counts[rec] = counts.get(rec, 0.0) + age * self.weight_since(ot, t, object_id)
        return self.dirichlet_normalized(counts, tie_break_recency=pool)


def make_belief(base: str, rng: random.Random, half_life: Optional[float], negative: str, bin_hours: int, day0: int):
    if base == "mostfreq":
        return DiscountedMostFrequent(rng, half_life_h=half_life, **NEGATIVE[negative])
    if base == "lastseen":
        # no half-life or discount support (one-hot on the latest sighting has nothing to decay or discount);
        # exists so the planning metric (task 2) can read a full `dist` for last-seen, which the classical log
        # does not serialize.
        return LastObservation(rng, **NEGATIVE[negative])
    cfg = TimetableConfig(bin_hours=bin_hours, day_scheme="all", day0_weekday=day0)
    return DiscountedTimetable(rng, cfg, half_life_h=half_life, **NEGATIVE[negative])


# ------------------------------------------------------------------ pieces --

class DecayingStepConformal:
    """q_{t+1} = q_t + eta_t (err_t - alpha), eta_t = max(eta_min, eta_0 t^(-1/2-eps)); sets in score space."""

    def __init__(self, alpha: float = 0.1, eta0: float = 0.05, eps: float = 0.1, eta_min: float = 0.005, warm: int = 20):
        self.alpha, self.eta0, self.eps, self.eta_min, self.warm = alpha, eta0, eps, eta_min, warm
        self.q = 1.0                       # everything in the set until the warm start
        self.t = 0
        self._first: List[float] = []

    def set_of(self, scores: Dict[str, float]) -> set:
        return {y for y, s in scores.items() if s <= self.q}

    def update(self, err: bool, score: Optional[float] = None) -> None:
        """``score`` = this question's nonconformity of the truth; the first ``warm`` scores set q to their
        conservative (1 - alpha) quantile, then the decaying-step update runs from there."""
        if len(self._first) < self.warm:
            if score is not None:
                self._first.append(score)
            if len(self._first) == self.warm:
                k = math.ceil((self.warm + 1) * (1 - self.alpha))
                self.q = sorted(self._first)[min(k, self.warm) - 1]
            return
        self.t += 1
        eta = max(self.eta_min, self.eta0 * self.t ** (-0.5 - self.eps))
        self.q += eta * ((1.0 if err else 0.0) - self.alpha)
        self.q = min(max(self.q, 0.0), 1.0)


class WeightedQuantileConformal:
    """Conformal beyond exchangeability (Barber, Candès, Ramdas, Tibshirani 2023): the (1 - alpha) quantile of the
    time-weighted past scores plus a unit point mass at +inf; ``tau_w`` is the weight half-life in hours (None = plain
    split conformal over every past score)."""

    def __init__(self, alpha: float = 0.1, tau_w: Optional[float] = 24.0, warm: int = 20):
        self.alpha, self.tau_w, self.warm = alpha, tau_w, warm
        self.hist: List[Tuple[int, float]] = []
        self.q = 1.0

    def quantile(self, t: int) -> float:
        if len(self.hist) < self.warm:
            return 1.0
        ws = [(s, 1.0 if self.tau_w is None else 2.0 ** (-max(0, t - ti) / (self.tau_w * 3600.0))) for ti, s in self.hist]
        total = sum(w for _, w in ws) + 1.0
        need = (1.0 - self.alpha) * total
        acc = 0.0
        for s, w in sorted(ws):
            acc += w
            if acc >= need:
                return s
        return 1.0     # the +inf mass carries the quantile: everything is in the set

    def update(self, t: int, score: float) -> None:
        self.hist.append((t, score))


class MixtureMartingale:
    """Simple-mixture conformal test martingale over conformal p-values of the question scores.

    ``cusum=True`` (default) makes it the CUSUM e-detector of Shin, Ramdas, Rinaldo 2024: every grid
    point's product restarts at 1 whenever it falls below 1 (``M_t = max(M_{t-1}, 1) * e_t``), so a long
    stationary stretch cannot drive the wealth to ~0 and bury a later change (the plain martingale did
    exactly that on the regime banks: ~0 after two days, never fired).  Threshold 1/delta; the CUSUM
    version has an average-run-length guarantee, not Ville's, so delta defaults to 1e-3."""

    def __init__(self, rng: random.Random, delta: float = 0.001, min_window: int = 20, grid: int = 20, cusum: bool = True,
                 window: Optional[int] = None):
        self.rng, self.delta, self.min_window, self.cusum, self.window = rng, delta, min_window, cusum, window
        self.eps = [(i + 0.5) / grid for i in range(grid)]
        self.reset()

    def reset(self) -> None:
        self.scores: List[float] = []
        self.log_terms = [0.0] * len(self.eps)   # log prod eps p^(eps-1) per grid point
        self.value = 1.0
        self.last_p = 1.0

    def step(self, s: float) -> float:
        n = len(self.scores)
        if n >= self.min_window:
            greater = sum(1 for x in self.scores if x > s)
            equal = sum(1 for x in self.scores if x == s)
            p = (greater + self.rng.random() * (equal + 1)) / (n + 1)
            p = min(max(p, 1e-6), 1.0)
            self.last_p = p
            for i, e in enumerate(self.eps):
                base = max(self.log_terms[i], 0.0) if self.cusum else self.log_terms[i]
                self.log_terms[i] = base + math.log(e) + (e - 1.0) * math.log(p)
            m = max(self.log_terms)
            self.value = math.exp(m) * sum(math.exp(v - m) for v in self.log_terms) / len(self.eps)
        self.scores.append(s)
        if self.window is not None and len(self.scores) > self.window:   # sliding calibration window: the recent regime
            del self.scores[0]
        return self.value

    @property
    def fired(self) -> bool:
        return self.value >= 1.0 / self.delta


# ------------------------------------------------------------------ replay --

def parse_half_lives(spec: str) -> List[Optional[float]]:
    out = []
    for tok in spec.split(","):
        tok = tok.strip()
        out.append(None if tok in ("inf", "none", "") else float(tok))
    return out


def run(bank_path: pathlib.Path, agent: str, a, seed: int = 0) -> Tuple[List[dict], dict]:
    lines = bank_path.read_text().splitlines()
    header = json.loads(lines[0])
    # question rows carry `stage` (calendar stage of the day) and `moment` (the activity) in the regime banks
    qmeta = {}
    for l in lines[1:]:
        if '"question"' in l:
            r = json.loads(l)
            if r.get("kind") == "question":
                qmeta[r["question_id"]] = {k: r[k] for k in ("stage", "moment") if k in r}
    stages = {int(k): v for k, v in (header.get("stages") or {}).items() if v}
    owners = {}   # object_id suffix "_<name>" -> resident_id
    for res in (header.get("protocol") or {}).get("residents") or []:
        if res.get("name") and res.get("resident_id"):
            owners[str(res["name"]).lower()] = res["resident_id"]

    def owner_of(object_id: str) -> Optional[str]:
        return owners.get(object_id.rsplit("_", 1)[-1].lower())
    episode = next(iter(JsonlBank(bank_path).episodes()))
    day0 = WEEKDAYS.index(header["day0_weekday"]) if header.get("day0_weekday") in WEEKDAYS else 0
    tag = {"household": header["household_id"], "patrol_hours": header.get("patrol_hours"), "look": "on" if a.look else "off",
           "patrol_label": header.get("patrol_label", ""), "seed": int(header.get("seed", seed)), "agent": agent,
           "base": a.base, "negative_evidence": a.negative}
    context = episode.agent_view()
    half_lives = parse_half_lives(a.half_lives) if agent == "bma" else [a.half_life]
    beliefs = [make_belief(a.base, random.Random(f"{seed}:{k}"), hl, a.negative, a.bin_hours, day0) for k, hl in enumerate(half_lives)]
    n_per_day = {}
    for day in episode.questions_by_day:
        for q in day:
            n_per_day[q.day_index] = n_per_day.get(q.day_index, 0) + 1
    for b in beliefs:
        b.reset(context)
        for obs in episode.initial_observations:
            b.update(obs)
    K = len(beliefs)
    weights = [1.0 / K] * K
    group_weights: Dict[str, List[float]] = {}   # --group object|person: one weight vector per key (object id or owner)
    rooms: Dict[str, List[str]] = {}
    for rec in context.sensable_receptacle_ids:
        room = episode.receptacle_rooms.get(rec)
        if room is not None and rec not in (ON_PERSON, OUT_OF_HOUSE):
            rooms.setdefault(room, []).append(rec)
    rooms = {r: sorted(v) for r, v in sorted(rooms.items())}
    spots = [r for r in context.sensable_receptacle_ids if r not in (ON_PERSON, OUT_OF_HOUSE)]
    last_seen: Dict[str, int] = {}          # object -> time of last positive sighting (for Rel)
    person_conformal: Dict[str, DecayingStepConformal] = {}

    def conformal_of(key: str) -> DecayingStepConformal:
        if key not in person_conformal:
            person_conformal[key] = DecayingStepConformal(a.alpha, a.eta0, a.eps, a.eta_min)
        return person_conformal[key]

    nexcp = WeightedQuantileConformal(a.alpha, None if a.tau_w <= 0 else a.tau_w)
    # martingale: one detector (agent-level, the pre-existing behaviour) or one per person (--group person, task 3);
    # `--detector off` never fires on its own, for the told-oracle agent below.
    person_mart: Dict[str, MixtureMartingale] = {}

    def mart_of(key: str) -> MixtureMartingale:
        if key not in person_mart:
            # the "global" detector keeps the exact old seed string (no suffix) so --group global reproduces every
            # existing mart_tt/mart_tt72 log to the digit; only the new per-person detectors (--group person) get one
            seed_str = f"{seed}:uq:{agent}" if key == "global" else f"{seed}:uq:{agent}:{key}"
            person_mart[key] = MixtureMartingale(random.Random(seed_str), a.delta, a.min_window,
                                                  cusum=(a.detector == "cusum"), window=a.window or None)
        return person_mart[key]

    mart = mart_of("global")
    fires: List[dict] = []
    weight_log: List[dict] = []
    seen_q: Dict[str, tuple] = {}           # object -> (last sighting time, truth) at its previous question
    person_objects: Dict[str, set] = {}     # owner (or "shared") -> object ids seen so far, for a targeted reset
    oracle_schedule: Dict[Tuple[int, str], float] = {}   # (day_index, owner) -> discount factor, told-oracle upper bound
    for tok in (a.oracle_schedule or "").split(","):
        tok = tok.strip()
        if not tok:
            continue
        day_s, owner_s = tok.split(":")
        oracle_schedule[(int(day_s), owner_s)] = a.factor
    oracle_done: set = set()

    def group_key(object_id: str) -> Optional[str]:
        if a.group == "object":
            return object_id
        if a.group == "person":
            return owner_of(object_id) or "shared"    # an object nobody owns (household-common) gets its own vector
        return None                                     # "global": one shared vector

    def w_of(object_id: str) -> List[float]:
        key = group_key(object_id)
        return weights if key is None else group_weights.get(key, [1.0 / K] * K)

    def mixed(object_id: str, t: int) -> Tuple[Dict[str, float], float, str, List[Dict[str, float]]]:
        dists = []
        raw_top = 0.0
        raw_arg = None
        for b in beliefs:
            pred = b.predict(object_id, t)
            d, _ = spots_only(dict(pred.distribution))
            dists.append(d)
            if pred.distribution.get(pred.argmax, 0.0) > raw_top:
                raw_top, raw_arg = pred.distribution.get(pred.argmax, 0.0), pred.argmax
        mix: Dict[str, float] = {}
        for w, d in zip(w_of(object_id), dists):
            for s, p in d.items():
                mix[s] = mix.get(s, 0.0) + w * p
        return mix, raw_top, raw_arg, dists

    def sighting(object_id: str, rec: str, t: int, cls: str) -> None:
        """A positive sighting: score each counter against the seen spot, fixed-share the weights, remember it.

        ``--score predictive`` (default, unchanged): the counter's own predictive probability of the seen spot
        (log-loss / Bayes mixing) — rewards calibration, not hit rate; a smoother-but-wronger counter can win.
        ``--score hit``: 1.0 if the counter's argmax equals the seen spot else a floor, i.e. plain 0-1 accuracy —
        rewards whichever counter is more often literally right, immune to how it spreads the rest of its mass.
        ``--score tempered``: the predictive probability raised to ``--temper-gamma`` (< 1), which compresses the
        dynamic range so one very confident miss does not crash a counter's weight for the rest of the window."""
        nonlocal weights
        for b in beliefs:
            b.ensure_object(object_id, cls)
        if K > 1 and rec not in (ON_PERSON, OUT_OF_HOUSE):
            liks = []
            for b in beliefs:
                d, _ = spots_only(dict(b.predict(object_id, t).distribution))
                p = max(d.get(rec, 0.0), 1e-3)
                if a.score == "hit":
                    argmax = max(d, key=lambda s: (d[s], s)) if d else None
                    liks.append(1.0 if argmax == rec else 0.05)
                elif a.score == "tempered":
                    liks.append(p ** a.temper_gamma)
                else:
                    liks.append(p)
            key = group_key(object_id)
            base = weights if key is None else group_weights.get(key, [1.0 / K] * K)
            w = [wk * lk for wk, lk in zip(base, liks)]
            z = sum(w)
            w = [(1 - a.share) * x / z + a.share / K for x in w]
            if key is None:
                weights = w
            else:
                group_weights[key] = w
        person_objects.setdefault(owner_of(object_id) or "shared", set()).add(object_id)
        last_seen[object_id] = t

    def fold(item) -> None:
        if isinstance(item, SenseResult):
            for o in sorted(item.contents):
                sighting(o, item.receptacle_id, item.t, item.object_classes.get(o, ""))
        elif isinstance(item, Observation):
            sighting(item.object_id, item.receptacle_id, item.t, item.object_class)
        for b in beliefs:
            b.update(item)

    evidence = episode.evidence_stream()
    questions = sorted((q for day in episode.questions_by_day for q in day), key=lambda q: (q.t_query, q.question_id))
    cursor = 0
    records = []
    seen_days: set = set()
    for q in questions:
        while cursor < len(evidence) and evidence[cursor].t <= q.t_query:
            fold(evidence[cursor])
            cursor += 1
        if agent == "martingale" and q.day_index not in seen_days:
            seen_days.add(q.day_index)
            for (day, owner), factor in oracle_schedule.items():
                if day == q.day_index and (day, owner) not in oracle_done:
                    for b in beliefs:
                        b.discount(q.t_query, factor, objects=person_objects.get(owner))
                    oracle_done.add((day, owner))
                    fires.append({"t": q.t_query, "day": q.day_index, "question_id": q.question_id, "owner": owner, "oracle": True})
        for b in beliefs:
            b.ensure_object(q.object_id, q.object_class)
        dist, raw_top, raw_arg, _ = mixed(q.object_id, q.t_query)
        owner = owner_of(q.object_id)
        rec = {**tag, "belief": beliefs[0].name if K == 1 else f"BMA({beliefs[0].name.split('(')[0]},{a.half_lives})", "day_index": q.day_index,
               "question_id": q.question_id, "object_id": q.object_id, "object_class": q.object_class, "t_query": q.t_query,
               **({"stage": stages[q.day_index]} if q.day_index in stages else {}),
               **qmeta.get(q.question_id, {}), **({"owner": owner} if owner else {})}
        if abs(sum(dist.values()) - 1.0) > TOL:
            raise AssertionError(f"{q.question_id}: mixed distribution sums to {sum(dist.values())}")
        if K > 1 and abs(sum(w_of(q.object_id)) - 1.0) > TOL:
            raise AssertionError(f"{q.question_id}: BMA weights sum to {sum(w_of(q.object_id))}")
        # ---- conformal set (ocp); --group person (task 3 follow-up): one q_t per resident (+ "shared"), so a
        # break in one person's error stream only widens THEIR sets, not the household's shared threshold
        if agent == "ocp":
            person_key = (owner or "shared") if a.group == "person" else "global"
            conformal = conformal_of(person_key)
            age = q.t_query - last_seen.get(q.object_id, -10 ** 9)
            rel = 1.0 if a.tau <= 0 else 2.0 ** (-max(0, age) / (a.tau * 3600.0))
            scores = {s: 1.0 - rel * dist.get(s, 0.0) for s in spots}
            cset = conformal.set_of(scores)
            if a.look and len(cset) > 1:
                set_mass = {s: dist.get(s, 0.0) for s in cset}
                room = choose_room(set_mass, rooms, "top")
                for r in look_results(episode, room, rooms[room], q.t_query):
                    fold(r)
                dist, raw_top, raw_arg, _ = mixed(q.object_id, q.t_query)
                rec.update({"look_room": room, "set_before_look": len(cset)})
                scores = {s: 1.0 - rel * dist.get(s, 0.0) for s in spots}
                cset = conformal.set_of(scores)
            rec.update({"set_size": len(cset), "q_t": round(conformal.q, 4), "rel": round(rel, 4), "conformal_group": person_key})
        if agent == "nexcp":
            qt = nexcp.quantile(q.t_query)
            scores = {s: 1.0 - dist.get(s, 0.0) for s in spots}
            cset = {y for y, sc in scores.items() if sc <= qt}
            rec.update({"set_size": len(cset), "q_t": round(qt, 4)})
        answer = max(dist, key=lambda s: (dist[s], s)) if dist else raw_arg
        truth = episode.true_location(q.object_id, q.t_query)
        rec.update({"answer": answer, "top_prob": round(dist.get(answer, 0.0), 4), "raw_answer": raw_arg,
                    "raw_top_prob": round(raw_top, 4), "truth": truth, "correct": answer == truth,
                    "dist": {s: round(p, 5) for s, p in sorted(dist.items()) if p >= DIST_MIN}})
        if agent == "ocp":
            covered = truth in cset
            if answer in spots and scores[answer] <= conformal.q and answer not in cset:
                raise AssertionError(f"{q.question_id}: argmax has score <= q_t but is not in the set")
            rec.update({"covered": covered, "conf_set": round(1.0 / max(1, len(cset)), 4)})
            conformal.update(not covered, 1.0 - rel * dist.get(truth, 0.0))   # found-it feedback reveals the truth
        elif agent == "nexcp":
            covered = truth in cset
            rec.update({"covered": covered, "conf_set": round(1.0 / max(1, len(cset)), 4)})
            nexcp.update(q.t_query, 1.0 - dist.get(truth, 0.0))
        elif agent == "martingale":
            # a repeat of the same question with no new sighting of the object in between (the bank asks the
            # same object several times inside one activity, minutes apart, before the found-it feedback lands)
            # is the same error observed again, not fresh evidence: it does not move the detector
            dupkey = (last_seen.get(q.object_id), truth)
            dup = a.dedupe and seen_q.get(q.object_id) == dupkey
            seen_q[q.object_id] = dupkey
            # --group person (task 3): one detector per owner, stepped only on that owner's questions, firing and
            # resetting only that owner's known bins — "shared"/household-common objects get their own detector too.
            person_key = (owner or "shared") if a.group == "person" else "global"
            m_obj = mart_of(person_key)
            s = 1.0 - dist.get(truth, 0.0)
            m = m_obj.value if dup else m_obj.step(s)
            if not math.isfinite(m) or not (0.0 < m_obj.last_p <= 1.0):
                raise AssertionError(f"{q.question_id}: martingale {m} p {m_obj.last_p}")
            rec.update({"martingale": round(m, 3), "p_value": round(m_obj.last_p, 4), "dup": dup, "detector_group": person_key})
            if a.detector != "off" and m_obj.fired and not dup:
                target_objects = person_objects.get(person_key) if a.group == "person" else None
                for b in beliefs:
                    b.discount(q.t_query + 1, a.factor, objects=target_objects)
                fires.append({"t": q.t_query, "day": q.day_index, "question_id": q.question_id, "martingale": round(m, 2), "owner": person_key})
                m_obj.reset()
                rec["fired"] = True
        elif agent == "bma":
            wq = w_of(q.object_id)
            rec.update({"weights": {str(hl): round(w, 4) for hl, w in zip(half_lives, wq)}})
            weight_log.append({"t": q.t_query, "day": q.day_index, "object_id": q.object_id, "weights": [round(w, 4) for w in wq]})
        records.append(rec)
    got = {}
    for r in records:
        got[r["day_index"]] = got.get(r["day_index"], 0) + 1
    if got != n_per_day:
        raise AssertionError(f"rows per day {got} != bank questions per day {n_per_day}")
    side = {"household": header["household_id"], "agent": agent, "params": {k: v for k, v in vars(a).items() if k not in ("bank", "out")},
            "shift_days": header.get("shift_days"), "fires": fires, "weights": weight_log, "half_lives": [str(h) for h in half_lives]}
    return records, side


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--agent", default="none", choices=("none", "ocp", "nexcp", "martingale", "bma"))
    ap.add_argument("--negative", default="off", choices=tuple(NEGATIVE))
    ap.add_argument("--base", default="timetable", choices=("mostfreq", "timetable", "lastseen"), help="the counter the wrapper sits on")
    ap.add_argument("--bin-hours", type=int, default=2, help="timetable bin width (the regime classical runs use 2)")
    ap.add_argument("--half-life", type=float, default=None, help="counter half-life in hours (none = no forgetting)")
    # ocp
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--eta0", type=float, default=0.05)
    ap.add_argument("--eps", type=float, default=0.1)
    ap.add_argument("--eta-min", type=float, default=0.005)
    ap.add_argument("--tau", type=float, default=24.0, help="relevance half-life in hours; 0 = no relevance weighting")
    ap.add_argument("--look", action="store_true", help="explore until confident: free look while the set holds > 1 spot")
    # nexcp
    ap.add_argument("--tau-w", type=float, default=24.0, help="weight half-life in hours for the weighted quantile; 0 = unweighted")
    # martingale
    ap.add_argument("--delta", type=float, default=0.001, help="fire when the detector reaches 1/delta")
    ap.add_argument("--detector", default="cusum", choices=("cusum", "mixture", "off"),
                     help="CUSUM e-detector (restarting), the plain mixture martingale, or off (never fires on its own — for --oracle-schedule)")
    ap.add_argument("--factor", type=float, default=0.1, help="count discount applied at a fire")
    ap.add_argument("--min-window", type=int, default=20)
    ap.add_argument("--window", type=int, default=0, help="sliding calibration window (non-duplicate scores); 0 = everything since the last reset")
    ap.add_argument("--no-dedupe", dest="dedupe", action="store_false", help="let repeated questions (same object, no new sighting) step the detector")
    ap.add_argument("--oracle-schedule", default="", help="martingale only: 'day:owner,day:owner' — force a targeted reset of that owner's known bins "
                     "at the start of each named day regardless of detection (the told upper bound); combine with --detector off for a pure oracle")
    # bma
    ap.add_argument("--half-lives", default=None, help="BMA half-lives; default 6,12,24,48,96,inf (mostfreq) or 24,72,168,inf (timetable)")
    ap.add_argument("--share", type=float, default=0.02, help="fixed-share switching rate toward uniform at every sighting")
    ap.add_argument("--group", default="global", choices=("global", "object", "person"),
                     help="one weight vector for the household (global), one per object, or one per resident who owns the object (person)")
    ap.add_argument("--per-object", action="store_true", help="deprecated alias for --group object")
    ap.add_argument("--score", default="predictive", choices=("predictive", "hit", "tempered"),
                     help="what a sighting scores each counter on: its predictive probability of the seen spot (log-loss), a 0-1 hit on its argmax, or a tempered (dynamic-range-compressed) predictive probability")
    ap.add_argument("--temper-gamma", type=float, default=0.3, help="exponent for --score tempered (< 1 compresses; 1.0 == predictive)")
    a = ap.parse_args(argv)
    if a.per_object and a.group == "global":
        a.group = "object"
    if a.half_lives is None:
        a.half_lives = "6,12,24,48,96,inf" if a.base == "mostfreq" else "24,72,168,inf"
    recs, side = run(a.bank, a.agent, a)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    a.out.with_suffix(".side.json").write_text(json.dumps(side, indent=1, sort_keys=True))
    n_ok = sum(r["correct"] for r in recs)
    extra = ""
    if a.agent in ("ocp", "nexcp"):
        extra = f" coverage {sum(r['covered'] for r in recs) / len(recs):.3f} mean set {sum(r['set_size'] for r in recs) / len(recs):.1f}"
    if a.agent == "martingale":
        extra = f" fires {len(side['fires'])} on days {sorted({f['day'] for f in side['fires']})} shift={side['shift_days']}"
    if a.agent == "bma":
        extra = f" final weights {recs[-1]['weights']}"
    print(f"{side['household']} {a.agent} base={a.base} hl={a.half_life} {n_ok}/{len(recs)}{extra}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
