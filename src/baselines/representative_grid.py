"""The representative grid: the shared runner behind the oracle-posterior,
value-of-information and delayed-label studies.

Every study evaluates the same cells on the same data:

* **Beliefs** ``LastObservation``, ``PeriodicPersistence``,
  ``PerpetuaStar``, ``LLMBelief`` (cached completions only: a cell that
  would need new LLM calls is skipped and the skip recorded) and
  ``OracleBelief`` (:mod:`baselines.beliefs.oracle_program_posterior`).
* **Policies** ``NeverSense``, ``SequentialSearch`` and whatever the study
  adds (built by :func:`build_policy` from a :class:`PolicySpec`).
* **Budgets** 24 and 90 senses per day (``REPRESENTATIVE_BUDGETS``); a
  study may add a soft-budget arm (``budget=None``: the cap is set to
  :data:`SOFT_BUDGET`, so cost is what the policy chooses to spend).
* **Households** the 20 seed-0 fleet banks of
  ``results/conformal_sweep_v2/`` under its calibration/test split
  (:func:`reference_split` reads the split from that directory and
  checks it against :func:`~baselines.conformal.calibration.household_split`
  at seed 0). Cells are evaluated on the TEST households; calibration
  households provide conformal tables, ACI scores and (delayed-label
  study) the mining-reliability measurement.

One task = one (belief, policy, budget, episode); tasks run in a process
pool. Each task writes its question records (the harness's JSON form plus
``first_confidence``, the belief's confidence at the question's first
decision, and ``ess`` for the oracle belief) to
``questions/<belief>__<policy>__<budget>.jsonl.gz`` and returns the
per-question scalars the aggregates need. :func:`aggregate_rows` turns
them into the grid csv (one row per cell) and the per-day csv (one row
per cell x query day: the per-day accuracy every run logs).

Randomness: every generator derives from ``seed`` through
:func:`baselines.cli._derived_rng`, keyed on the belief, the policy slug
and the episode, so identical inputs give identical csvs.
"""

from __future__ import annotations

import concurrent.futures
import csv
import dataclasses
import datetime
import gzip
import json
import logging
import pathlib
from dataclasses import dataclass, field
from typing import (Any, Callable, Dict, Iterator, List, Mapping, Optional,
                    Sequence, Tuple)

from baselines.agent import Agent
from baselines.bank import JsonlBank
from baselines.beliefs.base import BeliefModel
from baselines.cli import _derived_rng, git_state
from baselines.conformal.calibration import (AgeFn, CalibrationPair,
                                             QhatTable, collect_pairs,
                                             household_split)
from baselines.harness import QuestionRecord, run_episode
from baselines.policies.base import DecisionPolicy
from baselines.policies.conformal_sense import ConformalSense, belief_age_fn
from baselines.policies.never_sense import NeverSense
from baselines.policies.resolvable_mass_sense import ResolvableMassSense
from baselines.policies.sequential_search import SequentialSearch
from baselines.registry import build_registered_belief
from baselines.types import Episode, EpisodeContext, Prediction, Question

logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REFERENCE_SWEEP = REPO_ROOT / "results" / "conformal_sweep_v2"
"""The conformal sweep whose households and split every study reuses."""
FLEET_BANK_DIR = REPO_ROOT / "banks" / "baselines" / "fleet"
FLEET_BANK_GLOB = "*__hh_0??_bank.jsonl"
"""The 20 seed-0 fleet banks (the sweep's ``--bank`` glob)."""

REPRESENTATIVE_BUDGETS: Tuple[int, ...] = (24, 90)
SOFT_BUDGET = 1_000_000
"""Per-day cap in the soft-budget arm: never binding."""
SPLIT_SEED = 0
CALIB_FRAC = 0.5

BELIEF_SPECS: Mapping[str, Dict[str, Any]] = {
    "LastObservation": {"name": "last_observation"},
    "PeriodicPersistence": {"name": "periodic_persistence"},
    "PerpetuaStar": {"name": "perpetua_star"},
    "LLMBelief": {"name": "llm"},
    "OracleBelief": {"name": "oracle_program_posterior"},
}
"""Representative beliefs by display key -> registry spec (defaults: the
frozen/candidate settings every earlier report used)."""

LLM_COMPLETIONS = (REPO_ROOT / "reports" / "baselines" / "llm_floor"
                   / "completions.jsonl")
"""The only LLM completions that exist: the llm_floor run's cache."""


# ------------------------------------------------------------ households

def fleet_bank_paths(bank_dir: pathlib.Path = FLEET_BANK_DIR
                     ) -> List[pathlib.Path]:
    paths = sorted(bank_dir.glob(FLEET_BANK_GLOB))
    if not paths:
        raise FileNotFoundError(f"no fleet banks under {bank_dir}")
    return paths


@dataclass(frozen=True)
class EpisodeRef:
    bank_path: str
    episode_id: str
    household_id: str
    budget_per_day: int
    questions_per_day: int
    n_days: int


def episode_index(bank_paths: Sequence[pathlib.Path]) -> List[EpisodeRef]:
    refs = []
    for path in bank_paths:
        for ep in JsonlBank(path=path).episodes():
            refs.append(EpisodeRef(
                str(path), ep.episode_id, ep.household_id, ep.budget_per_day,
                max(len(d) for d in ep.questions_by_day), ep.n_days))
    return refs


def reference_split(refs: Sequence[EpisodeRef],
                    sweep_dir: pathlib.Path = REFERENCE_SWEEP
                    ) -> Dict[str, str]:
    """household -> ``calibration`` | ``test``, as the reference sweep
    used it; recomputed from the households and checked against the
    sweep's ``calibration.json`` so a drifted bank set cannot pass
    unnoticed."""
    ids = {r.household_id for r in refs}
    split = household_split(ids, SPLIT_SEED, CALIB_FRAC)
    stored_path = sweep_dir / "budget90" / "calibration.json"
    if stored_path.exists():
        stored = json.loads(stored_path.read_text())["split"]
        if stored != split:
            raise ValueError(
                f"household split differs from {stored_path}: recomputed "
                f"{split} vs stored {stored}")
    return split


def load_episode(bank_path: str, episode_id: str,
                 budget: Optional[int]) -> Episode:
    """One episode by id, its per-day budget overridden (None: the
    soft-budget cap)."""
    for episode in JsonlBank(path=pathlib.Path(bank_path)).episodes():
        if episode.episode_id == episode_id:
            cap = SOFT_BUDGET if budget is None else budget
            return dataclasses.replace(episode, budget_per_day=cap)
    raise KeyError(f"{episode_id} not in {bank_path}")


# --------------------------------------------------------------- beliefs

def llm_answers() -> Dict[str, Optional[str]]:
    """The llm_floor completions keyed by prompt key."""
    answers: Dict[str, Optional[str]] = {}
    if not LLM_COMPLETIONS.exists():
        return answers
    with open(LLM_COMPLETIONS) as fh:
        for line in fh:
            c = json.loads(line)
            answers[str(c["key"])] = c.get("text")
    return answers


def llm_rooms(bank_path: str) -> Dict[str, str]:
    rooms: Dict[str, str] = {}
    with open(bank_path) as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("kind") == "room_visit":
                for rec in r["contents"]:
                    rooms.setdefault(rec, r["room"])
    return rooms


def build_belief(belief_key: str, spec: Mapping[str, Any], rng: Any,
                 bank_path: str) -> BeliefModel:
    """A belief from its representative spec; the LLM belief gets the
    completions cache and the bank's room map."""
    spec = dict(spec)
    if spec["name"] == "llm":
        from baselines.beliefs.llm_belief import PromptCache
        spec.setdefault("cache", PromptCache(answers=llm_answers()))
        spec.setdefault("rooms", llm_rooms(bank_path))
    return build_registered_belief(spec, rng)


def llm_pending_fraction(ref: EpisodeRef) -> float:
    """Share of the LLM belief's QUERIED-object predictions a passive
    replay of ``ref`` cannot answer from the cache. Any positive value
    means the cell would need new LLM calls."""
    from baselines.beliefs.llm_belief import LLMBelief
    episode = load_episode(ref.bank_path, ref.episode_id, ref.budget_per_day)
    belief = build_belief("LLMBelief", BELIEF_SPECS["LLMBelief"],
                          _derived_rng(0, "llm_probe", ref.episode_id),
                          ref.bank_path)
    assert isinstance(belief, LLMBelief)
    agent = Agent(belief=belief, policy=NeverSense())
    pending = n = 0
    agent.reset(episode.agent_view())
    for obs in episode.initial_observations:
        agent.observe(obs)
    cursor, evidence = 0, episode.evidence_stream()
    for day in episode.questions_by_day:
        for q in day:
            while cursor < len(evidence) and evidence[cursor].t <= q.t_query:
                agent.observe(evidence[cursor])
                cursor += 1
            agent.predict(q)
            diag = belief.last_prediction_diagnostics()
            n += 1
            pending += int(diag is not None and diag.get("pending", 0.0) > 0)
    return pending / n if n else 0.0


# --------------------------------------------------------------- policies

@dataclass(frozen=True)
class PolicySpec:
    """One policy to build per (belief, episode): ``kind`` picks the class,
    ``params`` (sorted pairs, hashable) its constructor arguments; large
    fitted objects (conformal tables, score lists) travel in ``fitted``
    keyed by belief, outside the slug."""

    kind: str
    params: Tuple[Tuple[str, Any], ...] = ()
    label: str = ""

    @property
    def slug(self) -> str:
        if self.label:
            return self.label
        parts = [self.kind] + [f"{k}{v:g}" if isinstance(v, float)
                               else f"{k}{v}" for k, v in self.params]
        return "_".join(parts)

    def get(self, key: str, default: Any = None) -> Any:
        return dict(self.params).get(key, default)


def build_policy(spec: PolicySpec, belief: BeliefModel, rng: Any,
                 context: EpisodeContext,
                 fitted: Optional[Mapping[str, Any]] = None) -> DecisionPolicy:
    """A policy instance for one cell. ``fitted`` carries per-belief
    conformal objects (``table``: a :class:`QhatTable`, ``scores``: the
    calibration nonconformity scores)."""
    fitted = fitted or {}
    if spec.kind == "never_sense":
        return NeverSense()
    if spec.kind == "sequential_search":
        return SequentialSearch(rng, confidence_threshold=float(
            spec.get("confidence_threshold", 1.0)))
    age_fn: AgeFn = belief_age_fn(belief)
    if spec.kind == "conformal_global":
        table: QhatTable = fitted["table"]
        return ConformalSense(rng, table, age_fn, binned=False)
    if spec.kind == "resolvable_mass":
        return ResolvableMassSense(rng, fitted["table"], age_fn, False,
                                   float(spec.get("tau")))
    if spec.kind == "voi_threshold":
        from baselines.policies.voi_sense import VoIThresholdSense
        return VoIThresholdSense(rng, lam=float(spec.get("lam")))
    if spec.kind == "voi_budget_price":
        from baselines.policies.voi_sense import VoIBudgetPriceSense
        return VoIBudgetPriceSense(
            rng, gamma=float(spec.get("gamma")),
            budget_per_day=int(spec.get("budget_per_day")),
            questions_per_day=int(spec.get("questions_per_day")),
            lam0=float(spec.get("lam0")))
    if spec.kind == "aci":
        from baselines.policies.aci_sense import ACISense
        return ACISense(rng, fitted["scores"], float(spec.get("alpha")),
                        float(spec.get("gamma")), age_fn,
                        str(spec.get("feedback")))
    raise ValueError(f"unknown policy kind {spec.kind!r}")


# ------------------------------------------------------------ recording

class RecordingAgent:
    """An :class:`Agent` that remembers, per question, the belief's
    confidence at the FIRST decision and the belief's diagnostics after
    the answer. Same interface as :class:`Agent`; the harness only uses
    that interface."""

    def __init__(self, belief: BeliefModel, policy: DecisionPolicy) -> None:
        self.belief = belief
        self.policy = policy
        self._question_id: Optional[str] = None
        self.first_confidence = 0.0
        self.first_prediction: Optional[Prediction] = None

    @property
    def name(self) -> str:
        return f"{self.belief.name}+{self.policy.name}"

    def reset(self, context: EpisodeContext) -> None:
        self.belief.reset(context)
        self.policy.reset(context)
        self._question_id = None

    def observe(self, evidence: Any) -> None:
        self.belief.update(evidence)

    def predict(self, question: Question) -> Prediction:
        prediction = self.belief.predict(question.object_id, question.t_query)
        if self._question_id != question.question_id:
            self._question_id = question.question_id
            self.first_confidence = prediction.confidence
            self.first_prediction = prediction
        return prediction

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, last_sense: Any = None) -> Any:
        return self.policy.decide(question, prediction, budget_remaining,
                                  question.t_query, last_sense)


@dataclass(frozen=True)
class QuestionSummary:
    """Per-question scalars returned through the pool.

    ``budget_spent`` is a COST (a sense costs 1 in the robot's room and
    ``1 + c`` elsewhere), so it parts company with the sense COUNT
    ``n_senses`` as soon as the room-change cost is non-zero; both are
    carried because the study reports accuracy against each."""

    household_id: str
    day_index: int
    correct: bool
    belief_accuracy: float
    budget_spent: float
    forced: bool
    first_confidence: float
    ess: Optional[float] = None
    n_senses: int = 0
    same_room_senses: int = 0


def summarize(record: QuestionRecord, first_confidence: float,
              ess: Optional[float]) -> QuestionSummary:
    return QuestionSummary(record.household_id, record.day_index,
                           record.correct, record.belief_accuracy,
                           record.budget_spent, record.forced_answer,
                           first_confidence, ess, record.n_senses,
                           record.same_room_senses)


def ess_of(belief: BeliefModel) -> Optional[float]:
    ess = getattr(belief, "effective_sample_size", None)
    return float(ess()) if callable(ess) else None


# ------------------------------------------------------------------ tasks

@dataclass
class GridTask:
    """One (belief, policy, budget, episode) replay."""

    belief_key: str
    belief_spec: Dict[str, Any]
    policy: PolicySpec
    budget: Optional[int]
    ref: EpisodeRef
    seed: int
    part_path: str
    fitted: Dict[str, Any] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)
    room_change_cost: float = 0.0

    @property
    def budget_label(self) -> str:
        return "soft" if self.budget is None else str(self.budget)

    @property
    def cost_label(self) -> str:
        return f"{self.room_change_cost:g}"

    @property
    def cell(self) -> Tuple[str, str, str, str]:
        """The grid cell. The room-change cost is the fourth coordinate;
        studies that do not set it all report "0", and the c = 0 column
        is what earlier studies' cells mean."""
        return (self.belief_key, self.policy.slug, self.budget_label,
                self.cost_label)


def make_agent(task: GridTask, episode: Episode
               ) -> Tuple[RecordingAgent, BeliefModel, DecisionPolicy]:
    belief_name = str(task.belief_spec["name"])
    policy_rng = _derived_rng(task.seed, "policy", belief_name,
                              task.policy.slug, task.budget_label,
                              episode.episode_id)
    belief_rng = _derived_rng(task.seed, belief_name, task.policy.slug,
                              task.budget_label, episode.episode_id)
    belief = build_belief(task.belief_key, task.belief_spec, belief_rng,
                          task.ref.bank_path)
    policy = build_policy(task.policy, belief, policy_rng,
                          episode.agent_view(), task.fitted)
    return RecordingAgent(belief, policy), belief, policy


def write_dump(rows: Sequence[Dict[str, Any]], path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


def read_dump(path: pathlib.Path) -> Iterator[Dict[str, Any]]:
    with gzip.open(path, "rt") as fh:
        for line in fh:
            yield json.loads(line)


def run_plain_task(task: GridTask) -> Dict[str, Any]:
    """Worker: one replay through the harness, no feedback loop."""
    episode = load_episode(task.ref.bank_path, task.ref.episode_id,
                           task.budget)
    agent, belief, policy = make_agent(task, episode)
    summaries: List[QuestionSummary] = []
    rows: List[Dict[str, Any]] = []
    routine = getattr(belief, "routine_prediction", None)
    for record in run_episode(
            agent,          # type: ignore[arg-type]
            episode, room_change_cost=task.room_change_cost):
        ess = ess_of(belief)
        summaries.append(summarize(record, agent.first_confidence, ess))
        row = record.to_json_dict()
        row["first_confidence"] = agent.first_confidence
        # The belief's argmax BEFORE this question's senses: what the
        # robot would have answered on arrival, which is what question 4
        # ("is the likeliest receptacle in the room I'm standing in?")
        # is about.
        first = agent.first_prediction
        row["first_argmax"] = None if first is None else first.argmax
        row["room_change_cost"] = task.room_change_cost
        if ess is not None:
            row["ess"] = ess
        if callable(routine):
            # The routine oracle's own answer on the same question: the
            # no-observation comparison OracleBelief is measured against.
            row["routine_argmax"] = routine(record.object_id,
                                            record.t_query).argmax
        rows.append(row)
    write_dump(rows, pathlib.Path(task.part_path))
    return {"cell": task.cell, "belief": belief.name, "policy": policy.name,
            "episode_id": episode.episode_id, "summaries": summaries,
            "budget_per_day": episode.budget_per_day}


def run_pool(fn: Callable[[Any], Dict[str, Any]], tasks: Sequence[Any],
             workers: int) -> List[Dict[str, Any]]:
    if workers <= 1:
        return [fn(t) for t in tasks]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(fn, t) for t in tasks]
        out = []
        for i, fut in enumerate(futures, start=1):
            out.append(fut.result())
            if i % 10 == 0 or i == len(futures):
                logger.info("%d/%d tasks done", i, len(futures))
        return out


# ------------------------------------------------------------ calibration

def passive_pairs(belief_key: str, spec: Mapping[str, Any],
                  refs: Sequence[EpisodeRef], seed: int, workers: int
                  ) -> Dict[str, List[CalibrationPair]]:
    """Calibration pairs per household from one passive walk per
    episode (the never-sensing agent of the reference sweep)."""
    tasks = [{"belief_key": belief_key, "spec": dict(spec), "ref": r,
              "seed": seed} for r in refs]
    out: Dict[str, List[CalibrationPair]] = {}
    for res in run_pool(_passive_task, tasks, workers):
        out.setdefault(res["household_id"], []).extend(res["pairs"])
    return out


def _passive_task(task: Dict[str, Any]) -> Dict[str, Any]:
    ref: EpisodeRef = task["ref"]
    episode = load_episode(ref.bank_path, ref.episode_id, ref.budget_per_day)
    belief_name = str(task["spec"]["name"])
    rng = _derived_rng(task["seed"], belief_name, "NeverSense",
                       episode.episode_id)
    belief = build_belief(task["belief_key"], task["spec"], rng,
                          ref.bank_path)
    agent = Agent(belief=belief, policy=NeverSense())
    passive = collect_pairs(agent, episode, belief_age_fn(belief))
    return {"household_id": episode.household_id, "pairs": list(passive.pairs)}


# ------------------------------------------------------------- aggregates

GRID_FIELDS = ["belief", "policy", "budget", "room_change_cost",
               "belief_name", "policy_name",
               "n_households", "n_questions", "task_accuracy",
               "belief_accuracy", "senses_per_question", "senses_per_day",
               "cost_per_question", "cost_per_day",
               "same_room_sense_fraction",
               "forced_answer_rate", "median_ess"]
DAY_FIELDS = ["belief", "policy", "budget", "room_change_cost", "day_index",
              "n", "task_accuracy", "belief_accuracy", "senses_per_question",
              "cost_per_question"]


def aggregate_rows(results: Sequence[Dict[str, Any]]
                   ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """(grid rows, per-day rows) from the pool results, one grid row per
    cell and one day row per cell x query day.

    ``senses_per_question`` counts SENSES and ``cost_per_question`` sums
    what they cost; the two coincide exactly at ``room_change_cost = 0``,
    which is what makes a c = 0 column comparable to results produced
    before the cost model existed.
    """
    by_cell: Dict[Tuple[str, ...], List[Dict[str, Any]]] = {}
    for res in results:
        by_cell.setdefault(tuple(res["cell"]), []).append(res)
    grid: List[Dict[str, Any]] = []
    days: List[Dict[str, Any]] = []
    for cell, group in sorted(by_cell.items()):
        summaries: List[QuestionSummary] = [
            s for res in group for s in res["summaries"]]
        n = len(summaries)
        day_keys = {(s.household_id, s.day_index) for s in summaries}
        spent = sum(s.budget_spent for s in summaries)
        senses = sum(s.n_senses for s in summaries)
        same_room = sum(s.same_room_senses for s in summaries)
        ess = sorted(s.ess for s in summaries if s.ess is not None)
        cost_label = cell[3] if len(cell) > 3 else "0"
        grid.append({
            "belief": cell[0], "policy": cell[1], "budget": cell[2],
            "room_change_cost": cost_label,
            "belief_name": group[0]["belief"], "policy_name": group[0]["policy"],
            "n_households": len({s.household_id for s in summaries}),
            "n_questions": n,
            "task_accuracy": round(sum(s.correct for s in summaries) / n, 6),
            "belief_accuracy": round(
                sum(s.belief_accuracy for s in summaries) / n, 6),
            "senses_per_question": round(senses / n, 6),
            "senses_per_day": round(senses / len(day_keys), 6),
            "cost_per_question": round(spent / n, 6),
            "cost_per_day": round(spent / len(day_keys), 6),
            "same_room_sense_fraction": (round(same_room / senses, 6)
                                         if senses else ""),
            "forced_answer_rate": round(sum(s.forced for s in summaries) / n, 6),
            "median_ess": (round(ess[len(ess) // 2], 3) if ess else ""),
        })
        per_day: Dict[int, List[QuestionSummary]] = {}
        for s in summaries:
            per_day.setdefault(s.day_index, []).append(s)
        for day, ss in sorted(per_day.items()):
            days.append({
                "belief": cell[0], "policy": cell[1], "budget": cell[2],
                "room_change_cost": cost_label,
                "day_index": day, "n": len(ss),
                "task_accuracy": round(sum(s.correct for s in ss) / len(ss), 6),
                "belief_accuracy": round(
                    sum(s.belief_accuracy for s in ss) / len(ss), 6),
                "senses_per_question": round(
                    sum(s.n_senses for s in ss) / len(ss), 6),
                "cost_per_question": round(
                    sum(s.budget_spent for s in ss) / len(ss), 6)})
    return grid, days


def write_csv(rows: Sequence[Mapping[str, Any]], path: pathlib.Path,
              fields: Optional[Sequence[str]] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(fields or (list(rows[0]) if rows else []))
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: pathlib.Path) -> List[Dict[str, str]]:
    with open(path) as fh:
        return list(csv.DictReader(fh))


def provenance(out: pathlib.Path, refs: Sequence[EpisodeRef],
               split: Mapping[str, str], **extra: Any) -> None:
    commit, dirty = git_state(REPO_ROOT)
    doc = {"generated": datetime.datetime.now().isoformat(timespec="seconds"),
           "git_commit": commit, "git_dirty": dirty,
           "reference_sweep": str(REFERENCE_SWEEP.relative_to(REPO_ROOT)),
           "banks": sorted({r.bank_path for r in refs}),
           "split": dict(sorted(split.items())), **extra}
    out.mkdir(parents=True, exist_ok=True)
    (out / "provenance.json").write_text(json.dumps(doc, indent=2))


def part_path(out: pathlib.Path, task_cell: Sequence[str],
              episode_id: str) -> str:
    """Where one episode's records for ``task_cell`` are staged.

    A zero room-change cost leaves the name exactly as it was before the
    cost model existed, so a study that does not use it keeps its
    ``questions/<belief>__<policy>__<budget>.jsonl.gz`` filenames."""
    belief, policy, budget = task_cell[0], task_cell[1], task_cell[2]
    cost = task_cell[3] if len(task_cell) > 3 else "0"
    stem = f"{belief}__{policy}__{budget}"
    if cost not in ("", "0"):
        stem += f"__c{cost}"
    return str(out / "parts" / stem / f"{episode_id}.jsonl.gz")


def merge_parts(out: pathlib.Path) -> None:
    """Concatenate every cell's per-episode parts into
    ``questions/<belief>__<policy>__<budget>.jsonl.gz`` and drop them."""
    parts_dir = out / "parts"
    if not parts_dir.exists():
        return
    for cell_dir in sorted(parts_dir.iterdir()):
        target = out / "questions" / f"{cell_dir.name}.jsonl.gz"
        target.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(target, "wt") as dst:
            for part in sorted(cell_dir.glob("*.jsonl.gz")):
                with gzip.open(part, "rt") as src:
                    for line in src:
                        dst.write(line)
                part.unlink()
        cell_dir.rmdir()
    parts_dir.rmdir()


def fmt(x: Any, digits: int = 3) -> str:
    return "" if x in ("", None) else f"{float(x):.{digits}f}"
