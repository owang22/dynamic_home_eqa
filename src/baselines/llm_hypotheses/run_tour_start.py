"""Tour-start + re-asking study: run one arm, write everything the
analysis needs.

An ARM is one belief under one protocol on one household:

* passive — :func:`baselines.passive_eval.evaluate_continuous`: the
  fixed patrol stream, no policy, scored at question times under
  :data:`~baselines.passive_eval.AWAY_EQUIVALENCE`. The belief metric,
  comparable to the earlier rounds.
* active — :func:`baselines.harness.run_episode` with a decision
  policy: the patrol stream PLUS what the policy senses. The harness
  scores exact match by contract; the analysis rescores its logged
  distributions under the same equivalence.

The LLM arms carry the re-asking layer, so the LLM is called
mid-episode; those calls need the served model and are cached by
request hash, so a rerun is free. Every arm writes to
``<out>/<arm>/``: ``per_question.jsonl.gz`` (mixture distribution,
each particle's distribution, ESS, truth), ``diagnostics.json``
(re-ask events, sighting-quality series, ESS history, elicitor calls,
policy spend), and ``provenance.json``.

Usage (one arm per process; a launcher runs them side by side):
  python -m baselines.llm_hypotheses.run_tour_start --household hh_001 \
      --arm passive:llm:tour_named --endpoint http://127.0.0.1:8300
Arms: ``passive:<belief>[:<condition>]`` or
``active:<belief>[:<condition>]:f<fraction>[:b<beta>]`` with belief in
``llm`` (re-asking), ``llm_fixed`` (no re-asking), ``graph`` (the
assumption-graph arm, re-asking with operations), ``graph_fixed``,
``periodic``, ``mostfreq``, ``oracle``. Graph conditions are
``graph_named`` / ``graph_anonymized`` (the elicit ``--graph`` output).
``b<beta>`` on an active graph arm swaps the random-slice VoI policy
for :class:`~baselines.policies.assumption_disambiguation.
AssumptionDisambiguationSense` at that beta (``b0`` is the myopic
policy, decision for decision).

Diagnostics additionally carry the graph arm's traces
(``graph_diagnostics``), the bank's ``premises`` with the assumption-
recovery verdict, and ``late_discovered_objects`` (objects first
sighted after day 0) so the analysis can report late-discovery accuracy
apart from the tour-visible stratum.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import gzip
import json
import logging
import pathlib
import time
from typing import Any, Dict, List, Optional

from baselines.agent import Agent
from baselines.bank import JsonlBank
from baselines.cli import _derived_rng, build_policy, git_state
from baselines.distribution_metrics import SELECTED
from baselines.harness import run_episode
from baselines.household_analysis import REPO_ROOT, bank_path
from baselines.llm_hypotheses.elicit import DEFAULT_OUT_DIR, CachedThinkingClient
from baselines.llm_hypotheses.revise import (GraphRevisionElicitor,
                                             RevisionElicitor)
from baselines.passive_eval import (AWAY_EQUIVALENCE, PassiveProtocolConfig,
                                    evaluate_continuous)
from baselines.registry import build_registered_belief
from baselines.types import DAY_SECONDS as DAY_SECONDS_

logger = logging.getLogger(__name__)

STUDY_DIR = DEFAULT_OUT_DIR / "tour_start"
VOI_LAMBDA = 0.05
"""Myopic VoI price, the convention across the repo's studies; held
fixed across every arm so differences come from the belief."""


def belief_spec(kind: str, condition: Optional[str], household: str,
                client: Optional[CachedThinkingClient], episode,
                log_dir: pathlib.Path, reask: Dict[str, Any],
                hyp_subdir: str = "") -> Dict[str, Any]:
    if kind == "periodic":
        return {"name": "periodic_persistence"}
    if kind == "mostfreq":
        return {"name": "most_frequent", "half_life_h": 24.0}
    if kind == "mostfreq72":
        # The no-LLM comparison arm and the mixture's own statistical
        # particle: best of the statistical slate under merged scoring.
        return {"name": "most_frequent", "half_life_h": 72.0}
    if kind == "oracle":
        cfg = json.loads(SELECTED.read_text())
        return {"name": "oracle_program_posterior", "eps": cfg["eps"],
                "half_life_h": cfg["half_life_h"]}
    if kind in ("llm", "llm_fixed", "graph", "graph_fixed"):
        assert condition, ("llm arms need a condition (tour_named/"
                           "tour_anonymized; graph_named/graph_anonymized)")
        reasking = kind in ("llm", "graph")
        spec: Dict[str, Any] = {
            "name": "llm_hypothesis_mixture",
            "hypotheses_dir": str(DEFAULT_OUT_DIR / "hypotheses" / condition
                                  / hyp_subdir),
            "label": f"LLMHyp({condition}{',reask' if reasking else ',fixed'})"}
        if reasking:
            assert client is not None, "re-asking arm needs a served model"
            spec["reask"] = reask
            elicitor_cls = (GraphRevisionElicitor if kind == "graph"
                            else RevisionElicitor)
            spec["elicitor"] = elicitor_cls(
                client, episode, anonymized=condition.endswith("anonymized"),
                log_dir=log_dir)
        return spec
    raise SystemExit(f"unknown belief kind {kind!r}")


def parse_arm(arm: str):
    parts = arm.split(":")
    protocol, kind = parts[0], parts[1]
    condition = None
    fraction = None
    beta = None
    for part in parts[2:]:
        if part.startswith("f") and part[1:].replace(".", "", 1).isdigit():
            fraction = float(part[1:])
        elif part.startswith("b") and part[1:].replace(".", "", 1).isdigit():
            beta = float(part[1:])
        else:
            condition = part
    if protocol not in ("passive", "active"):
        raise SystemExit(f"arm {arm!r}: protocol must be passive|active")
    if protocol == "active" and fraction is None:
        raise SystemExit(f"arm {arm!r}: active arms need f<fraction>")
    if beta is not None and not kind.startswith("graph"):
        raise SystemExit(f"arm {arm!r}: b<beta> needs a graph belief")
    return protocol, kind, condition, fraction, beta


def late_discovered_objects(episode) -> List[str]:
    """Objects whose first sighting in the ambient stream (tour included)
    falls after day 0 — the stratum the random-time tour makes
    systematically different from the tour-visible objects."""
    first: Dict[str, int] = {}
    for obs in episode.initial_observations:
        first.setdefault(obs.object_id, obs.t)
    for event in episode.evidence_stream():
        objs = ([event.object_id] if hasattr(event, "object_id")
                else list(event.contents))
        for obj in objs:
            if obj not in first or event.t < first[obj]:
                first[obj] = event.t
    return sorted(obj for obj in episode.object_classes
                  if obj not in first or first[obj] >= DAY_SECONDS_)


def _ess(belief) -> Optional[float]:
    """The mixture's effective sample size, None for beliefs without one
    (the oracle exposes a same-named METHOD over its realizations; only
    the hypothesis mixture's property is the quantity plotted here)."""
    from baselines.beliefs.hypothesis_mixture import HypothesisMixture
    return (belief.effective_sample_size
            if isinstance(belief, HypothesisMixture) else None)


def _particle_rows(belief, object_id: str, t: int) -> Optional[Dict[str, Dict[str, float]]]:
    from baselines.beliefs.hypothesis_mixture import HypothesisMixture
    if not isinstance(belief, HypothesisMixture):
        return None
    names = [p.name for p in belief.particles]
    dists = belief.particle_distributions(object_id, t)
    return {n: {k: round(v, 6) for k, v in d.items() if v > 1e-6}
            for n, d in zip(names, dists)}


def run_arm(household: str, arm: str, endpoint: str, model: str,
            out_root: pathlib.Path, reask: Dict[str, Any],
            rng_seed: int = 0, bank_dir: Optional[pathlib.Path] = None,
            bank_seed: int = 0, hyp_subdir: str = "") -> pathlib.Path:
    protocol, kind, condition, fraction, beta = parse_arm(arm)
    # <study>/<household>__bank<seed>/arms/<arm>/ — arms under one folder so
    # the household directory itself holds only figures and tables.
    out_dir = (out_root / f"{household}__bank{bank_seed}" / "arms"
               / arm.replace(":", "__"))
    out_dir.mkdir(parents=True, exist_ok=True)
    path = bank_path(household, bank_seed, bank_dir)
    with open(path) as fh:
        header = json.loads(fh.readline())
    if header.get("first_question_day") != 0:
        raise SystemExit(
            f"{path}: header first_question_day="
            f"{header.get('first_question_day')!r}; this study needs banks "
            f"exported with --first-question-day 0 (questions from the tour "
            f"day on)")
    episode = next(JsonlBank(path=path).episodes())
    client = (CachedThinkingClient(endpoint, model, DEFAULT_OUT_DIR / "cache")
              if kind in ("llm", "graph") else None)
    late = set(late_discovered_objects(episode))
    spec = belief_spec(kind, condition, household, client, episode,
                       out_dir / "revisions", reask, hyp_subdir)
    rng = _derived_rng(rng_seed, "tour_start", arm, episode.episode_id)
    belief = build_registered_belief(dict(spec), rng)
    rows: List[Dict[str, Any]] = []
    started = time.monotonic()

    if protocol == "passive":
        config = PassiveProtocolConfig(seed=rng_seed,
                                       location_equivalence=AWAY_EQUIVALENCE)

        def capture(question, prediction, truth) -> None:
            # prediction/truth arrive already under the equivalence rule
            rows.append({
                "question_id": question.question_id,
                "object_id": question.object_id, "t_query": question.t_query,
                "truth": truth, "argmax": prediction.argmax,
                "dist": {k: round(v, 6) for k, v in
                         prediction.distribution.items() if v > 1e-6},
                "particles": _particle_rows(belief, question.object_id,
                                            question.t_query),
                "late_discovered": question.object_id in late,
                "ess": _ess(belief)})

        evaluate_continuous(episode, belief, config, on_prediction=capture)
        policy_info: Dict[str, Any] = {"policy": None}
    else:
        policy_rng = _derived_rng(rng_seed, "tour_start_policy", arm,
                                  episode.episode_id)
        if beta is not None:
            from baselines.policies.assumption_disambiguation import (
                AssumptionDisambiguationSense)
            policy = AssumptionDisambiguationSense(
                policy_rng, lam=VOI_LAMBDA, belief=belief, beta=beta)
        else:
            policy = build_policy({"name": "random_slice_voi",
                                   "lam": VOI_LAMBDA, "fraction": fraction},
                                  policy_rng)
        for record in run_episode(Agent(belief, policy), episode):
            rows.append({
                "question_id": record.question_id,
                "object_id": record.object_id, "t_query": record.t_query,
                "day_index": record.day_index,
                "truth": record.truth_receptacle,
                "argmax": record.answer_receptacle,
                "dist": {k: round(v, 6) for k, v in
                         record.distribution.items() if v > 1e-6},
                "budget_spent": record.budget_spent,
                "n_senses": record.n_senses,
                "belief_state": record.belief_state,
                "particles": _particle_rows(belief, record.object_id,
                                            record.t_query),
                "late_discovered": record.object_id in late,
                "ess": _ess(belief)})
        policy_info = {"policy": policy.name, "fraction": fraction,
                       "beta": beta, "lambda": VOI_LAMBDA,
                       "random_senses": getattr(policy, "random_senses", None),
                       "sense_split": getattr(policy, "sense_split", None)}

    with gzip.open(out_dir / "per_question.jsonl.gz", "wt") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    diagnostics: Dict[str, Any] = {
        "arm": arm, "household": household, "belief": belief.name,
        "protocol": protocol, **policy_info,
        "late_discovered_objects": sorted(late),
        "premises": dict(episode.premises),
        "wall_seconds": round(time.monotonic() - started, 1)}
    if hasattr(belief, "graph_diagnostics"):
        from baselines.llm_hypotheses.assumption_graph import (
            premise_recovered)
        diagnostics["graph"] = belief.graph_diagnostics()
        diagnostics["assumption_recovery"] = premise_recovered(
            belief.graph, episode.premises)
    if hasattr(belief, "reask_diagnostics"):
        diagnostics["reask"] = belief.reask_diagnostics()
        diagnostics["ess_history"] = list(belief.ess_history)
        diagnostics["final_weights"] = dict(zip(
            [p.name for p in belief.particles], belief.weights))
        diagnostics["final_hypotheses"] = belief._raw_hypotheses
        elicitor = spec.get("elicitor")
        if elicitor is not None:
            diagnostics["elicitor_calls"] = elicitor.calls
    if client is not None:
        diagnostics["llm"] = {"live_calls": client.calls,
                              "cache_hits": client.cache_hits,
                              "live_generation_seconds": round(
                                  client.generation_seconds, 1)}
    (out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=1))
    (out_dir / "provenance.json").write_text(json.dumps({
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds"),
        "git": dict(zip(("commit", "dirty"), git_state(REPO_ROOT))),
        "arm": arm, "spec": {k: v for k, v in spec.items()
                             if k != "elicitor"},
        "reask": reask, "rng_seed": rng_seed,
        "location_equivalence": [list(g) for g in AWAY_EQUIVALENCE]},
        indent=1))
    logger.info("arm %s done: %d questions -> %s", arm, len(rows), out_dir)
    return out_dir


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--household", default="hh_001")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--endpoint", default="http://127.0.0.1:8300")
    ap.add_argument("--model", default="Qwen/Qwen3.8-27B")
    ap.add_argument("--out-dir", type=pathlib.Path, default=STUDY_DIR)
    ap.add_argument("--reask-window", type=int, default=40)
    ap.add_argument("--reask-threshold", type=float, default=-2.3)
    ap.add_argument("--reask-days", type=int, nargs="*", default=[3, 7])
    ap.add_argument("--reask-max-calls", type=int, default=4)
    ap.add_argument("--uncovered-bank-max", type=int, default=4)
    ap.add_argument("--no-new-class-trigger", action="store_true",
                    help="disable the uncovered-bank trigger")
    ap.add_argument("--no-bank-ramp", action="store_true",
                    help="fixed bank threshold instead of the day ramp")
    ap.add_argument("--rng-seed", type=int, default=0)
    ap.add_argument("--bank-dir", type=pathlib.Path, default=None,
                    help="bank directory (default: the fleet's)")
    ap.add_argument("--bank-seed", type=int, default=0,
                    help="question-bank seed; the bank file carries it")
    ap.add_argument("--hyp-subdir", default="",
                    help="subdirectory under hypotheses/<condition>/ holding "
                         "this bank's elicitation")
    args = ap.parse_args()
    reask = {"window": args.reask_window, "threshold": args.reask_threshold,
             "scheduled_days": list(args.reask_days),
             "max_calls": args.reask_max_calls, "min_gap": args.reask_window,
             "new_class_triggers": not args.no_new_class_trigger,
             "uncovered_bank_max": args.uncovered_bank_max,
             "uncovered_bank_ramp": not args.no_bank_ramp}
    run_arm(args.household, args.arm, args.endpoint, args.model,
            args.out_dir, reask, args.rng_seed, bank_dir=args.bank_dir,
            bank_seed=args.bank_seed, hyp_subdir=args.hyp_subdir)


if __name__ == "__main__":
    main()
