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
``periodic``, ``lastobs``, ``mostfreq``, ``perpetua``, ``routine_posterior`` (the routine-knowledge
ceiling, formerly ``oracle``), ``log_reader*`` and ``notebook_mixture``
(both active-only, ``:named|anonymized:f0``; the notebook mixture
writes its notebooks and look/forecast/population logs into the arm
folder). Graph conditions are
``graph_named`` / ``graph_anonymized`` (the elicit ``--graph`` output).
``search`` on an active arm swaps the random-slice VoI policy for
:class:`~baselines.policies.sequential_search.SequentialSearch` (sense
receptacles in belief order until found; the no-LLM reference on a
cold-start bank, where a uniform belief values one look below the VoI
lambda and the threshold policy never senses).
``b<beta>`` on an active graph arm swaps the random-slice VoI policy
for :class:`~baselines.policies.assumption_disambiguation.
AssumptionDisambiguationSense` at that beta (``b0`` is the myopic
policy, decision for decision).

Diagnostics additionally carry the graph arm's traces
(``graph_diagnostics``), the bank's ``premises`` with the assumption-
recovery verdict, and ``tour_absent_objects`` (objects the tour did not
see) so the analysis can report that stratum apart from the tour-visible
one.
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
                                             LongLeafRevisionElicitor,
                                             RevisionElicitor,
                                             TreeRevisionElicitor)
from baselines.passive_eval import (AWAY_EQUIVALENCE, PassiveProtocolConfig,
                                    evaluate_continuous)
from baselines.registry import build_registered_belief
from baselines.types import DAY_SECONDS as DAY_SECONDS_

logger = logging.getLogger(__name__)

STUDY_DIR = DEFAULT_OUT_DIR / "runs"
"""Where runs live: ``runs/<run>/<household>__bank<seed>/``. Inside,
``arms/`` is grouped so the directory reads by importance —
``arms/active/`` (the arms that matter: the robot senses),
``arms/passive/`` (fixed patrol, no policy), ``arms/anonymized/`` (the
name-ablation condition, either protocol) and ``arms/incomplete/``
(stopped or broken runs, kept for their logs) — with ``figures/`` and
a ``README.md`` at the top. Superseded runs go to ``archive/``."""

ARM_GROUPS = ("active", "passive", "anonymized", "incomplete")


def arm_group(arm_dirname: str) -> str:
    """Which ``arms/`` subfolder an arm belongs in, from its name."""
    if arm_dirname.startswith("_"):
        return "incomplete"
    if "anonymized" in arm_dirname:
        return "anonymized"
    return "active" if arm_dirname.startswith("active") else "passive"
VOI_LAMBDA = 0.05
"""Myopic VoI price, the convention across the repo's studies; held
fixed across every arm so differences come from the belief."""


TREE_SCHEDULED_DAYS = [3]
LONGLEAF_SCHEDULED_DAYS: List[int] = []
"""treeLongLeaf revisions are event-driven: a weighted document's claim
going against it, the anomaly bucket, prediction quality. No scheduled
days. Calls are cheap (index + fetched documents, cached prefix), so
the cap is generous."""
LONGLEAF_MAX_CALLS = 12
"""The tree arm's only scheduled revision (Phase 3 brief): the graph
arm's day-0/1 calls on almost no evidence hurt it."""

SELECTED_ACTIVE = SELECTED.with_name("selected_active.json")
"""eps / half-life re-selected under the active protocol (24 senses a
day), on a household other than the one reported."""


def belief_spec(kind: str, condition: Optional[str], household: str,
                client: Optional[CachedThinkingClient], episode,
                log_dir: pathlib.Path, reask: Dict[str, Any],
                hyp_subdir: str = "", protocol: str = "passive") -> Dict[str, Any]:
    if kind == "periodic":
        return {"name": "periodic_persistence"}
    if kind == "lastobs":
        return {"name": "last_observation"}
    if kind == "mostfreq":
        return {"name": "most_frequent", "half_life_h": 24.0}
    if kind == "perpetua":
        return {"name": "perpetua"}
    if kind == "mostfreq72":
        # The no-LLM comparison arm and the mixture's own statistical
        # particle: best of the statistical slate under merged scoring.
        return {"name": "most_frequent", "half_life_h": 72.0}
    if kind == "routine_posterior":
        # A ceiling on ROUTINE knowledge only: a posterior over
        # re-realizations of the household program, with no per-object
        # learning from sightings — a model that reads sightings can beat
        # it. eps / half-life are selected per protocol (the passive
        # selection is worse than passive on the active stream).
        cfg = json.loads(SELECTED.read_text())
        if protocol == "active" and SELECTED_ACTIVE.exists():
            cfg = json.loads(SELECTED_ACTIVE.read_text())
        return {"name": "oracle_program_posterior", "eps": cfg["eps"],
                "half_life_h": cfg["half_life_h"]}
    if kind in ("log_reader", "log_reader_notes", "log_reader_aided"):
        assert condition in ("named", "anonymized"), \
            "log_reader arms take a condition: named | anonymized"
        assert client is not None, "the log reader needs a served model"
        from baselines.llm_hypotheses.log_reader import LogReaderBrain
        from baselines.llm_hypotheses.prompt import build_anonymization_maps
        if condition == "anonymized":
            omap, rmap, cmap = build_anonymization_maps(episode)
        else:
            omap, rmap, cmap = {}, {}, {}
        brain = LogReaderBrain(client, notes=(kind == "log_reader_notes"),
                               aided=(kind == "log_reader_aided"),
                               omap=omap, rmap=rmap, cmap=cmap,
                               log_dir=log_dir.parent / "notes")
        label = {"log_reader_notes": "LogReaderNotes",
                 "log_reader_aided": "LogReaderAided"}.get(kind, "LogReader")
        return {"name": "log_reader", "brain": brain,
                "label": f"{label}({condition})"}
    if kind in ("notebook_mixture", "notebook_voi", "notebook_llmDecide",
                "notebook_fixed", "notebook_notes"):
        assert condition in ("named", "anonymized"), \
            f"{kind} takes a condition: named | anonymized"
        assert client is not None, "the notebook mixture needs a served model"
        from baselines.llm_hypotheses.notebook_mixture import (
            CONFIGS, NotebookMixtureBrain)
        from baselines.llm_hypotheses.prompt import build_anonymization_maps
        if condition == "anonymized":
            omap, rmap, cmap = build_anonymization_maps(episode)
        else:
            omap, rmap, cmap = {}, {}, {}
        # The brain writes straight into the arm folder: notebooks/,
        # looks.jsonl, forecasts.jsonl, population.jsonl, calls.jsonl.
        days = [d for d in episode.questions_by_day if d]
        qpd = (sum(len(d) for d in days) / len(days)) if days else 24.0
        config = dataclasses.replace(CONFIGS[kind], questions_per_day=qpd)
        brain = NotebookMixtureBrain(client, omap=omap, rmap=rmap, cmap=cmap,
                                     log_dir=log_dir.parent, config=config,
                                     resident_names=_resident_first_names(household))
        return {"name": "notebook_mixture", "brain": brain,
                "label": f"{config.label}({condition})"}
    if kind in ("llm", "llm_fixed", "graph", "graph_fixed", "tree",
                "tree_fixed", "longleaf", "longleaf_fixed"):
        assert condition, ("llm arms need a condition (tour_named/"
                           "tour_anonymized; graph_named/graph_anonymized; "
                           "tree_named/tree_anonymized)")
        reasking = kind in ("llm", "graph", "tree", "longleaf")
        spec: Dict[str, Any] = {
            "name": ("tree_hypothesis_mixture" if kind.startswith("tree")
                     else "longleaf_mixture" if kind.startswith("longleaf")
                     else "llm_hypothesis_mixture"),
            "hypotheses_dir": str(DEFAULT_OUT_DIR / "hypotheses" / condition
                                  / hyp_subdir),
            "label": f"LLMHyp({condition}{',reask' if reasking else ',fixed'})"}
        if reasking:
            assert client is not None, "re-asking arm needs a served model"
            if kind == "tree":
                # Tree triggers: scheduled day 3 only, the anomaly bucket,
                # then quality. No uncovered-bank trigger, one call type.
                reask = {**reask, "scheduled_days": TREE_SCHEDULED_DAYS,
                         "new_class_triggers": False, "call_types": False}
            if kind == "longleaf":
                # Library triggers: scheduled days 3, 7, 14; anomaly;
                # quality. No uncovered bank; one call type.
                reask = {**reask, "scheduled_days": LONGLEAF_SCHEDULED_DAYS,
                         "new_class_triggers": False, "call_types": False,
                         "max_calls": max(int(reask.get("max_calls", 0)),
                                          LONGLEAF_MAX_CALLS)}
            spec["reask"] = reask
            elicitor_cls = (GraphRevisionElicitor if kind == "graph"
                            else TreeRevisionElicitor if kind == "tree"
                            else LongLeafRevisionElicitor if kind == "longleaf"
                            else RevisionElicitor)
            elicitor = elicitor_cls(
                client, episode, anonymized=condition.endswith("anonymized"),
                log_dir=log_dir)
            if kind == "graph":
                elicitor.call_types = bool(reask.get("call_types", True))
            spec["elicitor"] = elicitor
        return spec
    raise SystemExit(f"unknown belief kind {kind!r}")


def _resident_first_names(household: str) -> Dict[str, str]:
    """resident id -> first name from the household's persona (the bank
    carries ids only; objects are named after their owners, e.g.
    ``phone_sofia``, so the agents need the link)."""
    import glob
    import yaml
    for p in glob.glob(f"../profiles/households/*/*/{household}/persona.yaml") + \
            glob.glob(f"profiles/households/*/*/{household}/persona.yaml"):
        try:
            persona = yaml.safe_load(open(p))
            return {r["id"]: str(r.get("name", "")).split()[0]
                    for r in persona.get("residents", []) if r.get("name")}
        except Exception:      # a persona we cannot read is no names
            return {}
    return {}


def parse_arm(arm: str):
    parts = arm.split(":")
    protocol, kind = parts[0], parts[1]
    condition = None
    fraction = None
    beta = None
    search = False
    for part in parts[2:]:
        if part == "search":
            search = True
        elif part.startswith("f") and part[1:].replace(".", "", 1).isdigit():
            fraction = float(part[1:])
        elif part.startswith("b") and part[1:].replace(".", "", 1).isdigit():
            beta = float(part[1:])
        else:
            condition = part
    if protocol not in ("passive", "active"):
        raise SystemExit(f"arm {arm!r}: protocol must be passive|active")
    if protocol == "active" and fraction is None:
        raise SystemExit(f"arm {arm!r}: active arms need f<fraction>")
    if kind.startswith("log_reader") and protocol != "active":
        raise SystemExit(f"arm {arm!r}: the log reader is a policy; run it "
                         f"as active:<kind>:<condition>:f0")
    if kind.startswith("notebook") and protocol != "active":
        raise SystemExit(f"arm {arm!r}: the notebook mixture chooses its own "
                         f"looks; run it as active:{kind}:<condition>:f0")
    if beta is not None and not kind.startswith(("graph", "tree")):
        raise SystemExit(f"arm {arm!r}: b<beta> needs a graph or tree belief")
    if search and (protocol != "active" or beta is not None
                   or kind.startswith("log_reader")
                   or kind.startswith("notebook")):
        raise SystemExit(f"arm {arm!r}: search is an active policy for a "
                         f"belief model (not with b<beta>, the log reader "
                         f"or the notebook mixture)")
    return protocol, kind, condition, fraction, beta, search


def tour_absent_objects(episode) -> List[str]:
    """Objects the installation tour did not see — membership is defined
    by the tour alone. The mid-day tour makes this stratum systematically
    different from the tour-visible objects, so it is reported apart.
    (Was ``late_discovered_objects``, which named the stratum for
    something that had not happened when it was fixed.)"""
    seen = {obs.object_id for obs in episode.initial_observations}
    return sorted(o for o in episode.object_classes if o not in seen)


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
            bank_seed: int = 0, hyp_subdir: str = "",
            days: Optional[int] = None) -> pathlib.Path:
    protocol, kind, condition, fraction, beta, search = parse_arm(arm)
    if kind == "oracle":          # retired name
        raise SystemExit("arm kind 'oracle' is now 'routine_posterior'")
    # <run>/<household>__bank<seed>/arms/<group>/<arm>/ — grouped by what
    # the arm is, so the household directory reads by importance.
    arm_dirname = arm.replace(":", "__")
    out_dir = (out_root / f"{household}__bank{bank_seed}" / "arms"
               / arm_group(arm_dirname) / arm_dirname)
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
    if days is not None:
        # A short run for a cost or behaviour check: the first `days`
        # days of questions, everything else about the bank unchanged.
        episode = dataclasses.replace(
            episode, questions_by_day=episode.questions_by_day[:days])
    client = (CachedThinkingClient(endpoint, model, DEFAULT_OUT_DIR / "cache")
              if kind in ("llm", "graph", "tree", "longleaf")
              or kind.startswith(("log_reader", "notebook"))
              else None)
    late = set(tour_absent_objects(episode))
    spec = belief_spec(kind, condition, household, client, episode,
                       out_dir / "revisions", reask, hyp_subdir,
                       protocol=protocol)
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
                "tour_absent": question.object_id in late,
                "ess": _ess(belief)})

        evaluate_continuous(episode, belief, config, on_prediction=capture)
        policy_info: Dict[str, Any] = {"policy": None}
    else:
        policy_rng = _derived_rng(rng_seed, "tour_start_policy", arm,
                                  episode.episode_id)
        if kind.startswith("log_reader"):
            from baselines.llm_hypotheses.log_reader import LogReaderPolicy
            policy = LogReaderPolicy(spec["brain"])
        elif kind.startswith("notebook"):
            from baselines.llm_hypotheses.notebook_mixture import (
                NotebookMixturePolicy)
            policy = NotebookMixturePolicy(spec["brain"])
        elif beta is not None and kind.startswith("tree"):
            from baselines.policies.label_disambiguation import (
                LabelDisambiguationSense)
            policy = LabelDisambiguationSense(
                policy_rng, lam=VOI_LAMBDA, belief=belief, beta=beta)
        elif beta is not None:
            from baselines.policies.assumption_disambiguation import (
                AssumptionDisambiguationSense)
            policy = AssumptionDisambiguationSense(
                policy_rng, lam=VOI_LAMBDA, belief=belief, beta=beta)
        elif search:
            policy = build_policy({"name": "sequential_search"}, policy_rng)
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
                "tour_absent": record.object_id in late,
                "ess": _ess(belief)})
        if kind.startswith("notebook"):
            # The last day's end-of-day review and the final notebooks.
            spec["brain"].finish()
        policy_info = {"policy": policy.name, "fraction": fraction,
                       "beta": beta, "lambda": VOI_LAMBDA,
                       "random_senses": getattr(policy, "random_senses", None),
                       "sense_split": getattr(policy, "sense_split", None)}

    with gzip.open(out_dir / "per_question.jsonl.gz", "wt") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    diagnostics: Dict[str, Any] = {
        "arm": arm, "household": household, "belief": belief.name,
        "protocol": protocol, "days": episode.n_days, **policy_info,
        "tour_absent_objects": sorted(late),
        "premises": dict(episode.premises),
        "wall_seconds": round(time.monotonic() - started, 1)}
    if kind.startswith("notebook"):
        diagnostics["notebook_mixture"] = belief.brain.diagnostics()
        diagnostics["log_loss_valid"] = True
    elif hasattr(belief, "brain"):
        diagnostics["log_reader"] = belief.brain.stats()
        diagnostics["log_loss_valid"] = False
        diagnostics["decisions"] = belief.brain.decisions
        diagnostics["notes_versions"] = belief.brain.notes_versions
    if hasattr(belief, "graph_diagnostics"):
        from baselines.llm_hypotheses.assumption_graph import (
            premise_recovered)
        diagnostics["graph"] = belief.graph_diagnostics()
        # Flat arms have no assumptions to match: N/A, not 0.
        diagnostics["assumption_recovery"] = (
            premise_recovered(belief.graph, episode.premises)
            if belief.graph is not None else None)
    if hasattr(belief, "library_diagnostics"):
        from baselines.llm_hypotheses.longleaf import write_library
        diagnostics["library"] = belief.library_diagnostics()
        write_library(out_dir / "library", belief.library_documents(),
                      belief.library_status())
    if hasattr(belief, "tree_diagnostics"):
        from baselines.llm_hypotheses.hypothesis_tree import label_recovered
        diagnostics["tree"] = belief.tree_diagnostics()
        diagnostics["label_recovery"] = label_recovered(
            belief.tree, belief.leaf_weights, episode.premises)
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
                             if k not in ("elicitor", "brain")},
        "reask": spec.get("reask", reask), "rng_seed": rng_seed,
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
    ap.add_argument("--anomaly-repeats", type=int, default=3,
                    help="graph arm: bucket recurrences that fire a "
                         "diversify call (0 disables the anomaly trigger)")
    ap.add_argument("--anomaly-p", type=float, default=0.05)
    ap.add_argument("--settled-weight", type=float, default=0.9)
    ap.add_argument("--no-call-types", action="store_true",
                    help="graph arm: one revision call type with every "
                         "operation but deletion (the phase-1 protocol)")
    ap.add_argument("--rng-seed", type=int, default=0)
    ap.add_argument("--bank-dir", type=pathlib.Path, default=None,
                    help="bank directory (default: the fleet's)")
    ap.add_argument("--bank-seed", type=int, default=0,
                    help="question-bank seed; the bank file carries it")
    ap.add_argument("--hyp-subdir", default="",
                    help="subdirectory under hypotheses/<condition>/ holding "
                         "this bank's elicitation")
    ap.add_argument("--days", type=int, default=None,
                    help="run only the first N days of questions")
    args = ap.parse_args()
    reask = {"window": args.reask_window, "threshold": args.reask_threshold,
             "scheduled_days": list(args.reask_days),
             "max_calls": args.reask_max_calls, "min_gap": args.reask_window,
             "new_class_triggers": not args.no_new_class_trigger,
             "uncovered_bank_max": args.uncovered_bank_max,
             "uncovered_bank_ramp": not args.no_bank_ramp,
             "anomaly_repeats": args.anomaly_repeats,
             "anomaly_p": args.anomaly_p,
             "settled_weight": args.settled_weight,
             "call_types": not args.no_call_types}
    run_arm(args.household, args.arm, args.endpoint, args.model,
            args.out_dir, reask, args.rng_seed, bank_dir=args.bank_dir,
            bank_seed=args.bank_seed, hyp_subdir=args.hyp_subdir,
            days=args.days)


if __name__ == "__main__":
    main()
