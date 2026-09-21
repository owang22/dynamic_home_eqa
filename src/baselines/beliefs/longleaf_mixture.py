"""The treeLongLeaf mixture: :class:`~baselines.beliefs.
llm_hypothesis_mixture.LLMHypothesisMixture` over timetable documents
(:mod:`baselines.llm_hypotheses.longleaf`).

Differences from the flat mixture: particles are
:class:`~baselines.beliefs.timetable_hypothesis.TimetableBelief`; a
revision ADDS documents (and may revive retired ones) — the elicitor
returns ``{"new": [raw...], "revive": [ids], "dropped": [...],
"problems": [...]}``; the automatic prune RETIRES instead of deleting
(the document stays in ``retired`` with its last weight and day); the
triggers are the scheduled days, the anomaly bucket and quality (no
uncovered bank). The report carries the whole library — live and
retired, with weights, status and check history — so the revision
prompt can show it back.
"""

from __future__ import annotations

import collections
import os
from typing import Any, Dict, List, Optional

import math
import random

from baselines.beliefs.hypothesis_mixture import _MIN_LIKELIHOOD
from baselines.beliefs.llm_hypothesis_mixture import (
    MIN_LEAVES_AFTER_PRUNE, LLMHypothesisMixture)
from baselines.registry import build_registered_belief
from baselines.types import Observation
from baselines.beliefs.timetable_hypothesis import TimetableBelief
from baselines.llm_hypotheses.longleaf import (CLAIM_TRIGGER_AGAINST,
                                               CLAIM_TRIGGER_WEIGHT,
                                               is_longleaf_payload)
from baselines.types import DAY_SECONDS

CLAIM_TRIGGER_MIN_GAP_S = DAY_SECONDS
"""A claim-driven revision needs a full day since the episode start or
the last call: with 24 looks a day the sighting-count gap alone is met
on the tour afternoon, which is the premature revision the flat arm
suffered."""


class LongLeafMixture(LLMHypothesisMixture):

    def __init__(self, *args, **kwargs) -> None:
        self.retired: Dict[str, Dict[str, Any]] = {}
        self._weight_trace: Dict[int, Dict[str, float]] = {}
        self._library: Dict[str, Dict[str, Any]] = {}   # every doc ever
        self._last_reask_t = -1
        self._message_days: set = set()
        super().__init__(*args, **kwargs)

    @property
    def name(self) -> str:
        return self._label or f"LongLeafMixture({self._dir.name})"

    def _load_payload(self, payload: Any) -> List[dict]:
        if not is_longleaf_payload(payload):
            raise ValueError(f"{self.name}: the household file is not a "
                             f"longleaf library")
        self._graph = None
        raws = [dict(r) for r in payload["hypotheses"]]
        self._library = {r["hypothesis_id"]: r for r in raws}
        return raws

    def reset(self, context) -> None:
        super().reset(context)
        self.retired = {}
        self._weight_trace = {}
        self._last_reask_t = -1

    def _make_particle(self, raw, rng, vocabulary):
        # Confidence study: the document particles take the same empty-look
        # policy as the classical baselines (PARTICLE_NEGATIVE_HALF_LIFE_H env,
        # e.g. 1e-9 = off); unset = the package default (24 h).
        nhl = os.environ.get("PARTICLE_NEGATIVE_HALF_LIFE_H")
        return TimetableBelief(rng, raw, vocabulary=vocabulary,
                               negative_half_life_h=float(nhl) if nhl else None)

    @property
    def has_structure(self) -> bool:
        return True

    # ------------------------------------------------------------- trace

    def update(self, evidence) -> None:
        super().update(evidence)
        day = evidence.t // DAY_SECONDS
        self._weight_trace[day] = {k: round(v, 5)
                                   for k, v in self.leaf_weights.items()}

    # ----------------------------------------------------------- triggers

    def _recent_looks(self):
        return [row for row in self._look_log if row[0] > self._last_reask_t]

    def claims_gone_against(self) -> List[Dict[str, Any]]:
        """Live documents at or above :data:`CLAIM_TRIGGER_WEIGHT` with a
        claim that has resolved against them at least
        :data:`CLAIM_TRIGGER_AGAINST` times, and more often against than
        for, since the last call."""
        weights = self.leaf_weights
        looks = self._recent_looks()
        n_hyp = len(self._raw_hypotheses)
        # Confidence study: under tempered weights a library of n documents
        # sits near 1/n each, so a fixed 0.1 floor silences the trigger for
        # n > 10; the floor becomes half an equal share when that is lower.
        floor = CLAIM_TRIGGER_WEIGHT
        if os.environ.get("CLAIM_TRIGGER_RELATIVE", "0") == "1":
            floor = min(CLAIM_TRIGGER_WEIGHT, 0.5 / max(n_hyp, 1))
        out = []
        for raw, particle in zip(self._raw_hypotheses, self._particles[:n_hyp]):
            key = self._particle_key(raw)
            if weights.get(key, 0.0) < floor:
                continue
            if not isinstance(particle, TimetableBelief) or particle._hypothesis is None:
                continue
            for row in particle.claim_tallies(looks):
                if (row["against"] >= CLAIM_TRIGGER_AGAINST
                        and row["against"] > row["for"] + 0.5 * row["weak_for"]):
                    out.append({"hypothesis_id": key, "weight": weights[key], **row})
        return out

    def _todays_messages(self, t: int) -> List[str]:
        """The residents' dated messages for day ``t`` (the told arm's
        protocol carries them; the not-told arm's carries none)."""
        proto = getattr(self._context, "protocol", None) or {}
        day = t // DAY_SECONDS
        return [str(m.get("text", "")) for m in (proto.get("hint_messages") or [])
                if int(m.get("day_index", -1)) == day]

    def _maybe_reask(self, t: int) -> None:
        cfg = self._reask
        if cfg is None or self._elicitor is None or self.calls_made >= cfg.max_calls:
            return
        # A message from the residents ("it's the weekend", "X is home sick")
        # is a stated shift: revise once at the day's first question, so the
        # told arm can act on it the same day instead of waiting for a claim
        # to fail. Once per message day.
        day = t // DAY_SECONDS
        msgs = self._todays_messages(t)
        if msgs and day not in self._message_days:
            self._message_days.add(day)
            self._revise(t, "residents' message today: " + " ".join(msgs)[:120], "message")
            return
        # The gap counts from the episode start as well as from the last
        # call: a claim contradicted by two looks on the tour day is the
        # premature revision that hurt the flat arm.
        since = len(self._sighting_log) - max(self._last_reask_index, 0)
        since_t = t - max(self._last_reask_t, 0)
        if since >= cfg.min_gap and since_t >= CLAIM_TRIGGER_MIN_GAP_S:
            hit = self.claims_gone_against()
            if hit:
                top = max(hit, key=lambda r: r["weight"])
                self._revise(t, f"claim of {top['hypothesis_id']} (weight "
                                f"{top['weight']:.2f}) against {top['against']}x: "
                                f"{top['claim'][:60]}", "claim")
                return
        super()._maybe_reask(t)

    # ---------------------------------------------------------- revision

    def _apply_revision(self, report: Dict[str, Any], t: int, trigger: str,
                        event: Dict[str, Any]) -> bool:
        assert self._elicitor is not None
        report["claims_against"] = self.claims_gone_against()
        self._last_reask_t = t
        result = self._elicitor(report, [dict(h) for h in self._raw_hypotheses],
                                self._context) or {}
        new = [dict(r) for r in result.get("new", [])]
        revive = [i for i in result.get("revive", []) if i in self.retired]
        stamp = {"t": t, "day": t // DAY_SECONDS, "trigger": trigger,
                 "call_index": self.calls_made}
        problems = list(result.get("problems", []))
        if new or revive:
            revised = [dict(h) for h in self._raw_hypotheses]
            for i in revive:
                revised.append(dict(self.retired.pop(i)["raw"]))
                self.edit_log.append({**stamp, "op": "revive",
                                      "hypothesis_id": i})
            for r in new:
                self._library[r["hypothesis_id"]] = r
                revised.append(r)
                self.edit_log.append({**stamp,
                                      "op": ("fork" if r.get("forked_from")
                                             else "add_hypothesis"),
                                      "hypothesis_id": r["hypothesis_id"],
                                      "forked_from": r.get("forked_from"),
                                      "title": r.get("title", "")})
            self._entry_trigger = trigger   # the parent's entry rule may key on it (message parity)
            self._rebuild(revised)
            self._entry_trigger = None
        for row in result.get("dropped", []):
            self.rejected_ops.append({**stamp, "op": "add_hypothesis",
                                      "reason": row.get("error", ""),
                                      "bad_strings": row.get("bad_strings", [])})
        event["problems"] = problems
        event["operations"] = len(new) + len(revive)
        event["rejected"] = len(result.get("dropped", []))
        event["call_type"] = "revise"
        if trigger == "anomaly":
            event["anomaly_key"] = report.get("anomaly_firing")
        event["n_live_after"] = len(self._raw_hypotheses)
        event["n_retired_after"] = len(self.retired)
        return bool(new or revive)

    # ---------------------------------------------------------- fair entry

    def _rebuild(self, revised: List[dict]) -> None:
        """As the parent, then give every NEW document the log weight it
        would hold had it been in the mixture from the start: its
        replayed log-likelihood over the evidence log, measured against
        a fresh copy of the first statistical particle replayed the same
        way, anchored on that particle's current weight. The parent's
        rule (mean of the existing documents) buries a newcomer whenever
        the existing documents have already lost to the statistical
        particle — which is exactly when a revision is needed."""
        before = set(self.leaf_weights)
        super()._rebuild(revised)
        if os.environ.get("HYPOTHESIS_ENTRY", "mean") in ("share", "share_cap"):
            # Confidence study: a revised document is written FROM the evidence, so
            # its replayed log-likelihood over that evidence is hindsight and (being
            # untempered) puts it on top by construction; the parent's entry share
            # applies instead and the document earns weight forward from its birth.
            return
        n_hyp = len(self._raw_hypotheses)
        if n_hyp >= len(self._particles) or not self._evidence_log:
            return
        stat_index = n_hyp
        stat_lw = self._log_weights[stat_index]
        reference = build_registered_belief(
            dict(self._stat_specs[0]), random.Random(0))
        ref_score = self._replayed_log_weight(reference)
        for i, raw in enumerate(self._raw_hypotheses):
            key = self._particle_key(raw)
            if key in before:
                continue
            fresh = self._make_particle(raw, random.Random(0), self.known_objects)
            score = self._replayed_log_weight(fresh)
            self._log_weights[i] = stat_lw + (score - ref_score)
        top = max(self._log_weights)
        self._log_weights = [lw - top for lw in self._log_weights]

    def _replayed_log_weight(self, particle) -> float:
        """The tempered log-likelihood one particle accumulates over the
        evidence log (presence and absence halves, the mixture's decay),
        starting from reset. The absence skip test uses the particle's
        own mass, so this is the score it would earn alone."""
        particle.reset(self._context)
        acc = 0.0
        for event in self._evidence_log:
            ll = 0.0
            if isinstance(event, Observation):
                particle.ensure_object(event.object_id, event.object_class)
                mass = particle.predict_readonly(
                    event.object_id, event.t).distribution.get(event.receptacle_id, 0.0)
                ll += math.log(max(mass, _MIN_LIKELIHOOD))
            else:
                for obj in event.contents:
                    particle.ensure_object(obj, event.object_classes.get(obj, ""))
                    mass = particle.predict_readonly(obj, event.t).distribution.get(
                        event.receptacle_id, 0.0)
                    ll += math.log(max(mass, _MIN_LIKELIHOOD))
                if self._absence_weight > 0.0:
                    present = set(event.contents)
                    for obj in sorted(particle.known_objects):
                        if obj in present:
                            continue
                        mass = particle.predict_readonly(obj, event.t).distribution.get(
                            event.receptacle_id, 0.0)
                        if mass < self.absence_threshold:
                            continue
                        ll += self._absence_weight * math.log(
                            max(1.0 - mass, _MIN_LIKELIHOOD))
            acc = self._decay * acc + ll
            particle.update(event)
        return acc

    # ------------------------------------------------------------ retiring

    def _prune(self, t: int) -> None:
        """Retire documents under the floor for ``leaf_prune_days``
        days, never below MIN_LEAVES_AFTER_PRUNE live ones."""
        if self._leaf_prune_days <= 0:
            return
        day = t // DAY_SECONDS
        weights = self.leaf_weights
        for key, w in weights.items():
            if w < self._leaf_weight_floor:
                self._below_since.setdefault(key, day)
            else:
                self._below_since.pop(key, None)
        ripe = [k for k, since in self._below_since.items()
                if day - since >= self._leaf_prune_days and k in weights]
        pruned: set = set()
        for key in sorted(ripe, key=lambda k: weights[k]):
            if len(self._raw_hypotheses) - len(pruned) <= MIN_LEAVES_AFTER_PRUNE:
                break
            raw = next(h for h in self._raw_hypotheses
                       if self._particle_key(h) == key)
            self.retired[key] = {"raw": dict(raw), "retired_day": day,
                                 "last_weight": weights[key]}
            self.prune_log.append({"t": t, "day": day, "leaf_id": key,
                                   "hypothesis_id": key, "kind": "retire",
                                   "weight": weights[key],
                                   "below_since_day": self._below_since.get(key)})
            pruned.add(key)
        if pruned:
            self._remove_hypothesis_particles(pruned)

    # ------------------------------------------------------------- report

    def revision_report(self, t: int) -> Dict[str, Any]:
        from baselines.llm_hypotheses.prompt import per_object_statistics
        report = super().revision_report(t)
        weights = self.leaf_weights
        verdicts = {h["hypothesis_id"]: h.get("verdict")
                    for h in report["hypotheses"]}
        n_hyp = len(self._raw_hypotheses)
        tallies = {}
        for raw, particle in zip(self._raw_hypotheses, self._particles[:n_hyp]):
            if isinstance(particle, TimetableBelief) and particle._hypothesis is not None:
                tallies[self._particle_key(raw)] = particle.claim_tallies(self._look_log)
        library = []
        for raw in self._raw_hypotheses:
            i = self._particle_key(raw)
            library.append({"hypothesis_id": i, "title": raw.get("title", ""),
                            "forked_from": raw.get("forked_from"),
                            "status": "live", "weight": weights.get(i, 0.0),
                            "verdict": verdicts.get(i),
                            "claims": tallies.get(i, []),
                            "markdown": raw.get("markdown", "")})
        for i, row in self.retired.items():
            library.append({"hypothesis_id": i,
                            "title": row["raw"].get("title", ""),
                            "status": f"retired day {row['retired_day']}",
                            "weight": row["last_weight"], "verdict": None,
                            "markdown": row["raw"].get("markdown", "")})
        library.sort(key=lambda r: -r["weight"])
        table = report["known_objects"]
        sightings = [(row["t"], row["object"], row["actual"])
                     for row in self._sighting_log]
        report["uncovered_objects"] = [
            {**u, "summary": u["summary"].replace("never sighted",
                                                  "0 sightings so far")}
            for u in report["uncovered_objects"]]
        report.update({
            "hourly": self.hourly_profile(),
            "library": library,
            "library_raws": [dict(r) for r in self._library.values()],
            "absence_by_object": self.absence_by_object(),
            "object_table": self.object_table(t),
            "claims_against": self.claims_gone_against(),
            "statistics": per_object_statistics(
                sorted(table), sightings, t,
                unsighted_label="0 sightings so far")})
        return report

    def hourly_profile(self) -> List[Dict[str, Any]]:
        """Where each object was seen, by clock hour and weekday / weekend,
        from the robot's own sightings: the evidence that places an in-use
        window between two patrol passes. One row per object that has been
        seen on more than one receptacle."""
        from baselines.llm_hypotheses.protocol_text import weekday_index
        prof: Dict[str, Dict[str, Dict[int, collections.Counter]]] = collections.defaultdict(
            lambda: {"weekday": collections.defaultdict(collections.Counter),
                     "weekend": collections.defaultdict(collections.Counter)})
        for row in self._sighting_log:
            kind = "weekend" if weekday_index(row["t"] // DAY_SECONDS) in (5, 6) else "weekday"
            prof[row["object"]][kind][(row["t"] % DAY_SECONDS) // 3600][row["actual"]] += 1
        out = []
        for obj in sorted(prof):
            recs = {r for k in prof[obj].values() for c in k.values() for r in c}
            if len(recs) < 2:
                continue
            out.append({"object": obj,
                        "weekday": {h: dict(c) for h, c in sorted(prof[obj]["weekday"].items())},
                        "weekend": {h: dict(c) for h, c in sorted(prof[obj]["weekend"].items())}})
        return out

    def object_table(self, t: int) -> List[Dict[str, Any]]:
        """One row per sighted object: modal receptacle, sightings,
        distinct receptacles, share of sighted days at the modal place,
        and the weekday-daytime found / empty looks there — the
        statistics and the absence table in one."""
        seen_days: Dict[str, Dict[int, collections.Counter]] = collections.defaultdict(
            lambda: collections.defaultdict(collections.Counter))
        for row in self._sighting_log:
            seen_days[row["object"]][row["t"] // DAY_SECONDS][row["actual"]] += 1
        absence = {a["object"]: a for a in self.absence_by_object()}
        out = []
        for obj in sorted(seen_days):
            days = seen_days[obj]
            counter = collections.Counter()
            for c in days.values():
                counter.update(c)
            modal = counter.most_common(1)[0][0]
            days_modal = sum(1 for d in days if days[d].most_common(1)[0][0] == modal)
            a = absence.get(obj, {"found": 0, "empty": 0})
            out.append({"object": obj, "modal": modal,
                        "sightings": sum(counter.values()),
                        "distinct": len(counter), "days_seen": len(days),
                        "days_modal": days_modal,
                        "found": a["found"], "empty": a["empty"]})
        return out

    def absence_by_object(self, start_h: float = 9.0, end_h: float = 17.0
                          ) -> List[Dict[str, Any]]:
        """For EVERY known object: its modal receptacle, and how many
        looks at that receptacle during weekday ``start_h``-``end_h``
        found it versus found nothing — the out-of-house signal the
        positive-only statistics hide, rendered for objects no document
        sends away as much as for the ones some document does."""
        seen: Dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)
        for row in self._sighting_log:
            seen[row["object"]][row["actual"]] += 1
        out = []
        for obj in sorted(self.known_objects):
            if not seen.get(obj):
                continue
            modal = seen[obj].most_common(1)[0][0]
            empty = found = 0
            for t, receptacle, contents in self._look_log:
                if receptacle != modal:
                    continue
                day = t // DAY_SECONDS
                if day % 7 in (5, 6):
                    continue
                hour = (t % DAY_SECONDS) / 3600.0
                if not start_h <= hour < end_h:
                    continue
                if obj in contents:
                    found += 1
                else:
                    empty += 1
            out.append({"object": obj, "modal": modal, "sightings": sum(seen[obj].values()),
                        "found": found, "empty": empty})
        return out

    # -------------------------------------------------------- diagnostics

    def library_status(self) -> Dict[str, Dict[str, Any]]:
        weights = self.leaf_weights
        out = {k: {"status": "live", "weight": w} for k, w in weights.items()}
        for k, row in self.retired.items():
            out[k] = {"status": f"retired day {row['retired_day']}",
                      "weight": row["last_weight"]}
        return out

    def library_documents(self) -> List[Dict[str, Any]]:
        return [dict(r) for r in self._library.values()]

    def library_diagnostics(self) -> Dict[str, Any]:
        return {
            "is_longleaf": True,
            "status": self.library_status(),
            "weight_trace": {str(d): w for d, w in
                             sorted(self._weight_trace.items())},
            "edit_log": list(self.edit_log),
            "prune_log": list(self.prune_log),
            "rejected_ops": list(self.rejected_ops),
            "check_outcomes": list(self.check_outcomes),
            "bucket_trace": list(self.bucket_trace),
            "weight_spread": self.weight_spread(),
            "n_documents": len(self._library),
            "leaf_weight_floor": self._leaf_weight_floor,
            "leaf_prune_days": self._leaf_prune_days}


__all__ = ["LongLeafMixture"]
