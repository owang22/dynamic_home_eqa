"""STAR-style memory-loop study: LLM-vs-scripted recall on a fixed subset.

An exploration, not a headline experiment: what does an LLM reasoning
over retrieved memory do in this setting, and does it beat a script
that mimics it? Roster on the fixed 400-question subset: NeverSense,
SequentialSearch, the best VoI configuration from
``results/voi_policies/`` for that (belief, budget), the scripted
recall-then-verify control, and the LLM memory loop. Beliefs
LastObservation and PerpetuaStar only (one weak-confidence model, one
honest-confidence model -- the reason is in
``results/voi_policies/findings.md``); budgets 24 and 90.

The subset: 400 questions from the same 10 test households as
``results/voi_policies/`` (the reference split of
``representative_grid``), 200 per budget, stratified evenly across the
three question regimes of ``exclusion_migration_replay.question_facts``
(``stale_in_house`` / ``came_back`` / ``truly_out``). The sampled ids
are written to ``subset.json`` so every policy sees exactly the same
questions. Regime labels read ground truth -- legitimate here because
the sampler is part of the evaluation design, not an agent.

Runner semantics: every arm replays the FULL episode day by day (the
identical observation diet and the real shared per-day budget), and the
per-question records are kept for the sampled questions only. The two
STAR arms run under the study-local runner below, which mirrors
``harness.run_episode`` exactly (delivery order, budget accounting,
forced answers, exact-match scoring) plus the two things the harness
cannot do: it feeds every piece of evidence to the policy's memory
index, and it commits the selector's own answer
(:attr:`~baselines.policies.star_memory_loop.StarMemoryLoopPolicy.answer_override`)
when one exists. In the LLM cells the LLM selector engages ONLY on
sampled questions; on all other questions the scripted control acts
(and spends budget) in its place, so the budget state a sampled
question sees is realistic without paying ~22 000 LLM calls per cell.

Stages (``--stage``, outputs under ``results/star_memory_loop/``):

  subset    sample the 400 questions -> ``subset.json``
  offline   NeverSense / SequentialSearch / best-VoI / scripted cells
            -> ``questions/<cell>.jsonl.gz``, no server needed
  llm       the LLM cells against a served model
            (``--endpoint``, default ``http://127.0.0.1:8300``;
            ``--model`` default ``Qwen/Qwen3.8-27B`` to match
            ``llm_generate.py``) -> question dumps + ``llm_run.json``
            (serving provenance, cache hit rate, tokens, wall time)
  report    ``summary.csv``, ``by_regime.csv``, ``failures.csv``

Usage:
  PYTHONPATH=src python -m baselines.star_study --stage subset offline report
  PYTHONPATH=src python -m baselines.star_study --stage llm --workers 4 \\
      --endpoint http://127.0.0.1:8300 --model Qwen/Qwen3.8-27B
"""

from __future__ import annotations

import argparse
import collections
import datetime
import json
import logging
import pathlib
import time
from typing import (Any, Dict, Iterator, List, Mapping, Optional, Sequence,
                    Set, Tuple)

from baselines.beliefs.base import BeliefModel
from baselines.cli import _derived_rng
from baselines.exclusion_migration_replay import REGIMES, question_facts
from baselines.policies.base import DecisionPolicy
from baselines.policies.never_sense import NeverSense
from baselines.policies.sequential_search import SequentialSearch
from baselines.policies.star_memory_loop import (ActionSelector, LoopView,
                                                 QwenSelector, ScriptedRecallThenVerify,
                                                 StarAction,
                                                 StarMemoryLoopPolicy)
from baselines.policies.voi_sense import (VoIBudgetPriceSense,
                                          VoIThresholdSense)
from baselines.representative_grid import (BELIEF_SPECS, REPO_ROOT,
                                           EpisodeRef, build_belief,
                                           episode_index, fleet_bank_paths,
                                           llm_rooms, load_episode,
                                           provenance, read_dump,
                                           reference_split, run_pool,
                                           write_csv, write_dump)
from baselines.types import (AnswerNow, Episode, Question, Sense,
                             SenseResult)

logger = logging.getLogger(__name__)

OUT_DIR = REPO_ROOT / "results" / "star_memory_loop"
SUBSET_PATH = OUT_DIR / "subset.json"

STUDY_BELIEFS = ("LastObservation", "PerpetuaStar")
STUDY_BUDGETS = (24, 90)
N_QUESTIONS = 400
"""Total sampled (question, budget) pairs: 200 per budget, ~67 per
regime -- the same order as STARBench's 360 tasks."""
SUBSET_SEED = 0
DEFAULT_ENDPOINT = "http://127.0.0.1:8300"
DEFAULT_MODEL = "Qwen/Qwen3.8-27B"
LLM_SEED = 0

BEST_VOI: Mapping[Tuple[str, int], Dict[str, Any]] = {
    # Best VoI configuration per (belief, budget) from
    # results/voi_policies/findings.md ("Summary: best VoI policy per
    # cell"): kind + params, display slug fixed as "VoIBest".
    ("LastObservation", 24): {"kind": "voi_budget_price", "gamma": 0.1,
                              "lam0": 0.05},
    ("LastObservation", 90): {"kind": "voi_budget_price", "gamma": 0.1,
                              "lam0": 0.05},
    ("PerpetuaStar", 24): {"kind": "voi_budget_price", "gamma": 0.01,
                           "lam0": 0.05},
    ("PerpetuaStar", 90): {"kind": "voi_threshold", "lam": 0.05},
}

OFFLINE_POLICIES = ("NeverSense", "SequentialSearch", "VoIBest",
                    "StarScripted")
LLM_POLICY = "StarQwen"


# ------------------------------------------------------------- subset

VOI_PROVENANCE = REPO_ROOT / "results" / "voi_policies" / "provenance.json"


def study_split() -> Dict[str, str]:
    """household -> calibration|test, read from the VoI study's stored
    provenance (the split every comparison number used) and checked
    against the re-derived reference split -- a drift is a hard error,
    never a silent re-split."""
    stored: Dict[str, str] = json.loads(
        VOI_PROVENANCE.read_text())["split"]
    derived = reference_split(episode_index(fleet_bank_paths()))
    if derived != stored:
        raise ValueError(
            f"household split drifted: {VOI_PROVENANCE} stores {stored}, "
            f"re-derivation gives {derived}")
    return stored


def _test_refs() -> List[EpisodeRef]:
    refs = episode_index(fleet_bank_paths())
    split = study_split()
    return [r for r in refs if split[r.household_id] == "test"]


def build_subset(seed: int = SUBSET_SEED) -> Dict[str, Any]:
    """Sample the fixed subset and write ``subset.json``."""
    refs = _test_refs()
    pool: Dict[str, List[Dict[str, Any]]] = {r: [] for r in REGIMES}
    for ref in refs:
        episode = load_episode(ref.bank_path, ref.episode_id,
                               ref.budget_per_day)
        facts = question_facts(episode)
        for fact in facts.values():
            pool[fact.regime].append({
                "question_id": fact.question_id,
                "object_id": fact.object_id, "t_query": fact.t_query,
                "regime": fact.regime, "episode_id": ref.episode_id,
                "household_id": ref.household_id,
                "bank_path": ref.bank_path})
    for regime in REGIMES:
        pool[regime].sort(key=lambda q: str(q["question_id"]))
    rng = _derived_rng(seed, "star_subset")
    per_budget = N_QUESTIONS // len(STUDY_BUDGETS)
    base, extra = divmod(per_budget, len(REGIMES))
    sampled: Dict[str, List[Dict[str, Any]]] = {}
    shortfalls: Dict[str, int] = {}
    remaining = {r: list(pool[r]) for r in REGIMES}
    for budget in STUDY_BUDGETS:
        want = {r: base + (1 if i < extra else 0)
                for i, r in enumerate(REGIMES)}
        chosen: List[Dict[str, Any]] = []
        for regime in REGIMES:
            available = remaining[regime]
            take = min(want[regime], len(available))
            if take < want[regime]:
                shortfalls[f"budget{budget}:{regime}"] = want[regime] - take
            picks = rng.sample(available, take)
            for p in picks:
                available.remove(p)
            chosen.extend(dict(p, budget=budget) for p in picks)
        # Top up from the biggest remaining pools if a regime ran short.
        while len(chosen) < per_budget:
            regime = max(REGIMES, key=lambda r: len(remaining[r]))
            if not remaining[regime]:
                break
            pick = rng.choice(remaining[regime])
            remaining[regime].remove(pick)
            chosen.append(dict(pick, budget=budget))
        sampled[f"budget{budget}"] = sorted(
            chosen, key=lambda q: str(q["question_id"]))
    doc: Dict[str, Any] = {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "seed": seed, "n_total": sum(len(v) for v in sampled.values()),
        "per_regime_available": {r: len(pool[r]) for r in REGIMES},
        "shortfalls": shortfalls, "questions": sampled}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SUBSET_PATH.write_text(json.dumps(doc, indent=2))
    logger.info("subset: %d questions (%s); shortfalls: %s", doc["n_total"],
                {k: len(v) for k, v in sampled.items()}, shortfalls or "none")
    return doc


def load_subset() -> Dict[str, Any]:
    if not SUBSET_PATH.exists():
        raise FileNotFoundError(
            f"{SUBSET_PATH} missing -- run --stage subset first")
    doc: Dict[str, Any] = json.loads(SUBSET_PATH.read_text())
    return doc


# ------------------------------------------------- study-local runner

def run_star_episode(belief: BeliefModel, policy: StarMemoryLoopPolicy,
                     episode: Episode) -> Iterator[Dict[str, Any]]:
    """Mirror of ``harness.run_episode`` for the STAR policy (module
    docstring): identical stream delivery and budget accounting, plus
    memory feeding and the selector's answer override."""
    context = episode.agent_view()
    belief.reset(context)
    policy.reset(context)
    for obs in episode.initial_observations:
        belief.update(obs)
        policy.observe(obs)
    cursor = 0
    evidence = episode.evidence_stream()
    for day_index, day_questions in enumerate(episode.questions_by_day):
        budget = episode.budget_per_day
        for question in day_questions:
            while (cursor < len(evidence)
                   and evidence[cursor].t <= question.t_query):
                belief.update(evidence[cursor])
                policy.observe(evidence[cursor])
                cursor += 1
            budget_before = budget
            forced = False
            last_sense: Optional[SenseResult] = None
            n_senses = 0
            while True:
                prediction = belief.predict(question.object_id,
                                            question.t_query)
                action = policy.decide(question, prediction, budget,
                                       question.t_query, last_sense)
                if isinstance(action, AnswerNow):
                    break
                assert isinstance(action, Sense)
                if action.receptacle_id in episode.unsensable_receptacle_ids:
                    raise ValueError(
                        f"{policy.name} asked to sense unsensable "
                        f"receptacle {action.receptacle_id!r}")
                if budget <= 0:
                    forced = True
                    break
                budget -= 1
                n_senses += 1
                contents = episode.receptacle_contents(
                    action.receptacle_id, question.t_query)
                last_sense = SenseResult(
                    receptacle_id=action.receptacle_id,
                    t=question.t_query, contents=contents)
                belief.update(last_sense)
                policy.observe(last_sense)
            override = policy.answer_override
            answer = override if override is not None else prediction.argmax
            truth = episode.true_location(question.object_id,
                                          question.t_query)
            confidence = float(prediction.distribution.get(answer, 0.0))
            yield {
                "episode_id": episode.episode_id,
                "household_id": episode.household_id,
                "belief": belief.name, "policy": policy.name,
                "day_index": day_index,
                "question_id": question.question_id,
                "object_id": question.object_id,
                "t_query": question.t_query,
                "answer_receptacle": answer, "confidence": confidence,
                "answer_overridden": override is not None,
                "truth_receptacle": truth, "correct": answer == truth,
                "budget_before": budget_before,
                "budget_spent": budget_before - budget,
                "budget_after": budget, "forced_answer": forced,
                "star": policy.last_question_stats,
                "working_memory": list(policy.last_working_memory),
            }


class RoutingSelector(ActionSelector):
    """LLM on the sampled questions, the scripted control everywhere
    else -- so the budget state a sampled question sees is what a
    full-episode scripted spender would leave (module docstring)."""

    def __init__(self, llm: ActionSelector, scripted: ActionSelector,
                 engage_question_ids: Set[str]) -> None:
        self._llm = llm
        self._scripted = scripted
        self._engaged = engage_question_ids

    @property
    def name(self) -> str:
        return f"Routed({self._llm.name})"

    def reset(self) -> None:
        self._llm.reset()
        self._scripted.reset()

    def select(self, view: LoopView) -> StarAction:
        if view.question.question_id in self._engaged:
            return self._llm.select(view)
        return self._scripted.select(view)


# --------------------------------------------------------------- cells

def _build_policy(policy_key: str, belief_key: str, budget: int,
                  ref: EpisodeRef, rooms: Mapping[str, str],
                  engaged: Set[str], endpoint: str, model: str,
                  cache_path: Optional[pathlib.Path],
                  seed: int) -> Tuple[DecisionPolicy, Optional[Any]]:
    """(policy, cached client or None). The client is returned so the
    caller can report cache stats after the run."""
    rng = _derived_rng(seed, "star_policy", policy_key, belief_key,
                       str(budget), ref.episode_id)
    if policy_key == "NeverSense":
        return NeverSense(), None
    if policy_key == "SequentialSearch":
        return SequentialSearch(rng), None
    if policy_key == "VoIBest":
        spec = BEST_VOI[(belief_key, budget)]
        if spec["kind"] == "voi_threshold":
            return VoIThresholdSense(rng, lam=float(spec["lam"])), None
        return VoIBudgetPriceSense(
            rng, gamma=float(spec["gamma"]), budget_per_day=budget,
            questions_per_day=ref.questions_per_day,
            lam0=float(spec["lam0"])), None
    if policy_key == "StarScripted":
        return StarMemoryLoopPolicy(ScriptedRecallThenVerify(),
                                    rooms=rooms), None
    if policy_key == LLM_POLICY:
        from baselines.memory.serving import CachedStructuredClient
        assert cache_path is not None
        client = CachedStructuredClient(endpoint, model, cache_path)
        selector = RoutingSelector(
            QwenSelector(client.generate, seed=LLM_SEED),
            ScriptedRecallThenVerify(), engaged)
        return StarMemoryLoopPolicy(selector, rooms=rooms), client
    raise ValueError(f"unknown policy {policy_key!r}")


def run_cell_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Worker: one (belief, policy, budget, episode) replay; returns the
    sampled-question records plus cell bookkeeping."""
    policy_key = str(task["policy_key"])
    belief_key = str(task["belief_key"])
    budget = int(task["budget"])
    ref: EpisodeRef = task["ref"]
    sampled: Dict[str, str] = dict(task["sampled"])  # qid -> regime
    episode = load_episode(ref.bank_path, ref.episode_id, budget)
    belief_rng = _derived_rng(int(task["seed"]), "star_belief", belief_key,
                              policy_key, str(budget), ref.episode_id)
    belief = build_belief(belief_key, dict(BELIEF_SPECS[belief_key]),
                          belief_rng, ref.bank_path)
    rooms = llm_rooms(ref.bank_path)
    cache_path = (pathlib.Path(str(task["cache_path"]))
                  if task.get("cache_path") else None)
    policy, client = _build_policy(
        policy_key, belief_key, budget, ref, rooms, set(sampled),
        str(task.get("endpoint", "")), str(task.get("model", "")),
        cache_path, int(task["seed"]))
    t0 = time.time()
    rows: List[Dict[str, Any]] = []
    if isinstance(policy, StarMemoryLoopPolicy):
        record_iter = run_star_episode(belief, policy, episode)
    else:
        from baselines.agent import Agent
        from baselines.harness import run_episode
        agent = Agent(belief=belief, policy=policy)
        record_iter = (r.to_json_dict() for r in run_episode(agent, episode))
    for row in record_iter:
        qid = str(row["question_id"])
        if qid in sampled:
            row = dict(row)
            row["regime"] = sampled[qid]
            row.pop("belief_state", None)
            row.pop("distribution", None)
            rows.append(row)
    out: Dict[str, Any] = {
        "cell": (belief_key, policy_key, budget),
        "episode_id": ref.episode_id, "rows": rows,
        "wall_seconds": round(time.time() - t0, 1)}
    if client is not None:
        out["cache_stats"] = client.cache_stats()
    return out


def _cell_slug(belief_key: str, policy_key: str, budget: int) -> str:
    return f"{belief_key}__{policy_key}__{budget}"


def _sampled_by_episode(subset: Dict[str, Any],
                        budget: int) -> Dict[str, Dict[str, str]]:
    """episode_id -> {question_id -> regime} for one budget."""
    out: Dict[str, Dict[str, str]] = {}
    for q in subset["questions"][f"budget{budget}"]:
        out.setdefault(str(q["episode_id"]), {})[
            str(q["question_id"])] = str(q["regime"])
    return out


def run_stage(policy_keys: Sequence[str], subset: Dict[str, Any],
              workers: int, endpoint: str = "", model: str = "",
              seed: int = 0) -> Dict[str, Any]:
    refs = {r.episode_id: r for r in _test_refs()}
    tasks: List[Dict[str, Any]] = []
    for budget in STUDY_BUDGETS:
        by_episode = _sampled_by_episode(subset, budget)
        for belief_key in STUDY_BELIEFS:
            for policy_key in policy_keys:
                for episode_id, sampled in sorted(by_episode.items()):
                    task: Dict[str, Any] = {
                        "policy_key": policy_key, "belief_key": belief_key,
                        "budget": budget, "ref": refs[episode_id],
                        "sampled": sampled, "seed": seed}
                    if policy_key == LLM_POLICY:
                        task["endpoint"] = endpoint
                        task["model"] = model
                        task["cache_path"] = str(
                            OUT_DIR / "llm_cache"
                            / f"{_cell_slug(belief_key, policy_key, budget)}"
                              f".jsonl")
                    tasks.append(task)
    t0 = time.time()
    results = run_pool(run_cell_task, tasks, workers)
    by_cell: Dict[Tuple[str, str, int], List[Dict[str, Any]]] = {}
    for res in results:
        by_cell.setdefault(tuple(res["cell"]), []).append(res)
    for cell, group in sorted(by_cell.items()):
        rows = [row for res in group for row in res["rows"]]
        rows.sort(key=lambda r: str(r["question_id"]))
        write_dump(rows, OUT_DIR / "questions"
                   / f"{_cell_slug(cell[0], cell[1], cell[2])}.jsonl.gz")
    cache_totals: Dict[str, Any] = collections.defaultdict(int)
    for res in results:
        for key, value in (res.get("cache_stats") or {}).items():
            if isinstance(value, int):
                cache_totals[key] += value
    return {"wall_seconds": round(time.time() - t0, 1),
            "n_tasks": len(tasks),
            "cache_totals": dict(cache_totals) or None}


# --------------------------------------------------------------- report

SUMMARY_FIELDS = ["belief", "policy", "budget", "n", "task_accuracy",
                  "senses_per_question", "forced_answer_rate",
                  "recalls_per_question", "answered_from_memory_rate",
                  "answer_overridden_rate", "unparseable", "illegal",
                  "fallbacks", "step_cap_hits"]
REGIME_FIELDS = ["belief", "policy", "budget", "regime", "n",
                 "task_accuracy", "senses_per_question"]


def report_stage() -> None:
    summary: List[Dict[str, Any]] = []
    by_regime: List[Dict[str, Any]] = []
    for path in sorted((OUT_DIR / "questions").glob("*.jsonl.gz")):
        belief_key, policy_key, budget_s = path.stem.replace(
            ".jsonl", "").split("__")
        rows = list(read_dump(path))
        if not rows:
            continue
        n = len(rows)
        star_rows = [r for r in rows if r.get("star")]
        row: Dict[str, Any] = {
            "belief": belief_key, "policy": policy_key, "budget": budget_s,
            "n": n,
            "task_accuracy": round(
                sum(bool(r["correct"]) for r in rows) / n, 4),
            "senses_per_question": round(
                sum(int(r["budget_spent"]) for r in rows) / n, 4),
            "forced_answer_rate": round(
                sum(bool(r["forced_answer"]) for r in rows) / n, 4)}
        if star_rows:
            m = len(star_rows)
            totals: Dict[str, int] = collections.defaultdict(int)
            for r in star_rows:
                for key, value in r["star"].items():
                    totals[key] += int(value)
            row.update({
                "recalls_per_question": round(totals["recalls"] / m, 4),
                "answered_from_memory_rate": round(
                    totals["answered_from_memory"] / m, 4),
                "answer_overridden_rate": round(
                    sum(bool(r["answer_overridden"]) for r in star_rows)
                    / m, 4),
                "unparseable": totals["unparseable"],
                "illegal": totals["illegal"],
                "fallbacks": totals["fallbacks"],
                "step_cap_hits": totals["step_cap_hits"]})
        summary.append(row)
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            groups.setdefault(str(r.get("regime")), []).append(r)
        for regime, rr in sorted(groups.items()):
            by_regime.append({
                "belief": belief_key, "policy": policy_key,
                "budget": budget_s, "regime": regime, "n": len(rr),
                "task_accuracy": round(
                    sum(bool(r["correct"]) for r in rr) / len(rr), 4),
                "senses_per_question": round(
                    sum(int(r["budget_spent"]) for r in rr) / len(rr), 4)})
    write_csv(summary, OUT_DIR / "summary.csv", SUMMARY_FIELDS)
    write_csv(by_regime, OUT_DIR / "by_regime.csv", REGIME_FIELDS)
    logger.info("report: %d cells -> %s", len(summary), OUT_DIR)


# ----------------------------------------------------------------- main

def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(message)s")
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", nargs="+", required=True,
                    choices=("subset", "offline", "llm", "report"))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if "subset" in args.stage:
        build_subset(args.seed)
    if "offline" in args.stage:
        subset = load_subset()
        info = run_stage(OFFLINE_POLICIES, subset, args.workers,
                         seed=args.seed)
        logger.info("offline stage: %s", info)
        refs = _test_refs()
        provenance(OUT_DIR, refs, study_split(),
                   stage="offline", subset_seed=subset["seed"],
                   run_info=info)
    if "llm" in args.stage:
        from baselines.memory.serving import server_provenance
        subset = load_subset()
        serving = server_provenance(args.endpoint)
        info = run_stage([LLM_POLICY], subset, args.workers,
                         endpoint=args.endpoint, model=args.model,
                         seed=args.seed)
        (OUT_DIR / "llm_run.json").write_text(json.dumps({
            "model": args.model, "endpoint": args.endpoint,
            "temperature": 0.0, "seed": LLM_SEED,
            "serving": serving, "run_info": info,
            "generated": datetime.datetime.now().isoformat(
                timespec="seconds")}, indent=2))
        logger.info("llm stage: %s", info)
    if "report" in args.stage:
        report_stage()


if __name__ == "__main__":
    main()
