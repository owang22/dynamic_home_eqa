"""Belief: the routine oracle's realization ensemble, weighted by the
observation history (display name ``OracleBelief``).

:mod:`baselines.routine_oracle` re-realizes a household's ``program.yaml``
at many seeds and answers each question with the modal receptacle across
realizations, ignoring observations. This model keeps that seed ensemble
alive for the whole episode and weights each realization by how well it
agrees with everything the agent has seen; ``predict(object_id, t)`` is
the weighted distribution of the object's location at ``t`` across the
realizations. It is a diagnostic ceiling on routine knowledge, not a
deployable model: it reads the household's own program.

**Ensemble.** The routine oracle's default seed count
(:data:`~baselines.routine_oracle.DEFAULT_ORACLE_SEEDS`, 800) at the
routine oracle's seeds (``ORACLE_SEED_BASE + 1 ..``); the bank's own
world, the seed-0 realization, is never one of them (it would leak the
ground truth). Realizations are projected through the same truth loader
the bank export uses, so a realization's receptacle ids mean exactly
what bank truth means, and a realization's location at ``t`` is read the
way ``routine_oracle`` verified against ``hourly.csv`` (change points at
minute resolution; the location at ``t`` is the newest change point at
or before ``t``). One realization's change points are expanded once into
a minute-resolution grid per object, so every lookup is an array index.

**Weighting** is soft, never a hard filter. Every observation multiplies
each realization's weight: a positive sighting of O at R at ``t`` leaves
a realization that also has O at R at ``t`` unchanged and multiplies a
disagreeing one by ``eps``; an empty look (a sense of R at ``t`` whose
contents lack O) does the same with agreement inverted. Log-weights are
updated incrementally per observation and normalized only when a
prediction or the degeneracy diagnostic asks for them. Empty looks are
therefore in the weights already, so the base pipeline's negative-
evidence step is skipped (``consumes_negative_evidence_natively``); the
floor mix and the sighting-at-the-prediction-instant short circuit apply
as for every model.

**Degeneracy diagnostic.** :meth:`effective_sample_size` is
``1 / sum(w_i^2)`` over the normalized weights (800 when every
realization is equally consistent, 1 when a single one carries all the
mass); :meth:`last_prediction_diagnostics` reports it next to every
prediction so a run can log it per question.

All times are seconds since episode start.
"""

from __future__ import annotations

import logging
import math
import pathlib
import random
import re
from typing import (Callable, Dict, List, Mapping, Optional, Sequence, Tuple,
                    Union)

import numpy as np
from numpy.typing import NDArray

from baselines.beliefs.base import DEFAULT_FLOOR_MASS, BeliefModel
from baselines.types import (DAY_SECONDS, EpisodeContext, Observation,
                             Prediction, SenseResult)

logger = logging.getLogger(__name__)

DEFAULT_EPS = 0.05
"""Multiplier a realization's weight takes for every observation it
disagrees with. Constructor argument; never tuned per bank."""

MINUTE = 60
_EPISODE_SEED = re.compile(r"timeline_seed(\d+)$")

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_REALIZATION_CACHE = (_REPO_ROOT / "banks" / "baselines"
                             / "oracle_realizations")
"""Where realized change points are cached (under ``banks/``: machine-
local, regenerable, not tracked). One file per (household, bank seed,
seed range)."""


# ------------------------------------------------------------- ensemble

class RealizationEnsemble:
    """Minute-resolution location grid of every object across the
    re-realizations of one household program.

    ``grid[object_id]`` is a ``uint8[n_seeds, n_minutes]`` array of codes
    into ``receptacle_ids``. Built from change points (the truth loader's
    projection of each realization); ``minute_index`` clips times past the
    horizon to the last minute, as ``truth_at`` holds the final location.
    """

    def __init__(self, seeds: Sequence[int], receptacle_ids: Sequence[str],
                 n_minutes: int,
                 change_points: Mapping[str, Sequence[Sequence[Tuple[int, str]]]]
                 ) -> None:
        if len(receptacle_ids) > 255:
            raise ValueError("RealizationEnsemble: more than 255 receptacles")
        self.seeds = tuple(int(s) for s in seeds)
        self.receptacle_ids = tuple(receptacle_ids)
        self.n_minutes = int(n_minutes)
        code = {r: i for i, r in enumerate(self.receptacle_ids)}
        self.grid: Dict[str, NDArray[np.uint8]] = {}
        for obj, per_seed in change_points.items():
            if len(per_seed) != len(self.seeds):
                raise ValueError(
                    f"RealizationEnsemble: {obj} has {len(per_seed)} "
                    f"realizations for {len(self.seeds)} seeds")
            arr = np.zeros((len(self.seeds), self.n_minutes), dtype=np.uint8)
            for s, points in enumerate(per_seed):
                if not points or points[0][0] != 0:
                    raise ValueError(
                        f"RealizationEnsemble: {obj} seed {self.seeds[s]} "
                        f"change points must start at t=0")
                for i, (t, rec) in enumerate(points):
                    start = min(self.n_minutes, t // MINUTE)
                    end = (self.n_minutes if i + 1 == len(points)
                           else min(self.n_minutes, points[i + 1][0] // MINUTE))
                    if end > start:
                        arr[s, start:end] = code[rec]
                    elif i + 1 == len(points) and start >= self.n_minutes:
                        pass            # change past the horizon: ignored
            self.grid[obj] = arr

    @property
    def n_seeds(self) -> int:
        return len(self.seeds)

    @property
    def objects(self) -> Tuple[str, ...]:
        return tuple(self.grid)

    def minute_index(self, t: int) -> int:
        return min(self.n_minutes - 1, max(0, int(t) // MINUTE))

    def codes_at(self, object_id: str, t: int) -> NDArray[np.uint8]:
        """Receptacle code of ``object_id`` at ``t`` in every realization."""
        return self.grid[object_id][:, self.minute_index(t)]

    # ----------------------------------------------------- persistence

    def save(self, path: pathlib.Path) -> None:
        """Change points only (the grid is rebuilt on load): a flat table
        of (seed index, object index, minute, receptacle code)."""
        objects = list(self.grid)
        rows: List[Tuple[int, int, int, int]] = []
        for oi, obj in enumerate(objects):
            arr = self.grid[obj]
            for s in range(arr.shape[0]):
                row = arr[s]
                changes = np.flatnonzero(np.diff(row.astype(np.int16))) + 1
                rows.append((s, oi, 0, int(row[0])))
                rows.extend((s, oi, int(m), int(row[m])) for m in changes)
        table = np.array(rows, dtype=np.int32)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path, table=table, seeds=np.array(self.seeds, dtype=np.int64),
            receptacles=np.array(self.receptacle_ids), objects=np.array(objects),
            n_minutes=np.array(self.n_minutes))

    @classmethod
    def load(cls, path: pathlib.Path) -> "RealizationEnsemble":
        with np.load(path, allow_pickle=False) as data:
            table = data["table"]
            seeds = [int(s) for s in data["seeds"]]
            receptacles = [str(r) for r in data["receptacles"]]
            objects = [str(o) for o in data["objects"]]
            n_minutes = int(data["n_minutes"])
        points: Dict[str, List[List[Tuple[int, str]]]] = {
            obj: [[] for _ in seeds] for obj in objects}
        for s, oi, m, code in table.tolist():
            points[objects[oi]][s].append((m * MINUTE, receptacles[code]))
        return cls(seeds, receptacles, n_minutes, points)

    # ------------------------------------------------------ realization

    @classmethod
    def realize(cls, household_dir: pathlib.Path, n_days: int,
                seeds: Sequence[int]) -> "RealizationEnsemble":
        """Re-realize ``household_dir/program.yaml`` at every seed through
        the routine oracle's machinery."""
        import yaml

        from baselines.routine_oracle import _load_realizer, _realized_truth

        program_path = household_dir / "program.yaml"
        if not program_path.exists():
            raise FileNotFoundError(
                f"OracleBelief: no stored program at {program_path}")
        program = yaml.safe_load(program_path.read_text())
        if int(program["days"]) != n_days:
            raise ValueError(
                f"OracleBelief: program days {program['days']} != episode "
                f"days {n_days} for {household_dir}")
        sim = _load_realizer()
        engine = sim.load_v1()
        params = sim.load_params()
        per_object: Dict[str, List[List[Tuple[int, str]]]] = {}
        receptacles: List[str] = []
        seen = set()
        for k, seed in enumerate(seeds):
            truth = _realized_truth(sim, engine, params, program,
                                    household_dir, int(seed))
            if k == 0:
                per_object = {obj: [] for obj in sorted(truth)}
            if set(truth) != set(per_object):
                raise ValueError(
                    f"OracleBelief: seed {seed} realization of "
                    f"{household_dir} has a different object set")
            for obj, points in truth.items():
                per_object[obj].append([(int(t), str(r)) for t, r in points])
                for _, r in points:
                    if r not in seen:
                        seen.add(r)
                        receptacles.append(r)
        return cls(seeds, sorted(receptacles), n_days * DAY_SECONDS // MINUTE,
                   per_object)


def ensemble_cache_path(cache_dir: pathlib.Path, household_id: str,
                        bank_seed: int, seeds: Sequence[int]) -> pathlib.Path:
    return (cache_dir / f"{household_id}__bankseed{bank_seed}__"
                        f"seeds{min(seeds)}-{max(seeds)}.npz")


def oracle_seeds(bank_seed: int, n_seeds: int) -> Tuple[int, ...]:
    """The routine oracle's seed range for a bank: ``ORACLE_SEED_BASE +
    bank_seed * 10_000 + 1 ..`` (the convention of ``llm_floor`` and
    ``household_analysis``); seed 0, the bank's world, is never in it."""
    from baselines.routine_oracle import ORACLE_SEED_BASE

    base = ORACLE_SEED_BASE + bank_seed * 10_000
    return tuple(range(base + 1, base + n_seeds + 1))


def bank_seed_of(episode_id: str) -> int:
    """The realization seed a bank episode was exported from
    (``hh_001_timeline_seed0`` -> 0)."""
    m = _EPISODE_SEED.search(episode_id)
    if m is None:
        raise ValueError(
            f"OracleBelief: cannot read the bank seed from episode id "
            f"{episode_id!r} (expected a 'timeline_seed<k>' suffix)")
    return int(m.group(1))


def load_or_realize(household_dir: pathlib.Path, household_id: str,
                    episode_id: str, n_days: int, n_seeds: int,
                    cache_dir: Optional[pathlib.Path] = DEFAULT_REALIZATION_CACHE
                    ) -> RealizationEnsemble:
    """The ensemble for one bank episode, from the cache when present."""
    seeds = oracle_seeds(bank_seed_of(episode_id), n_seeds)
    path = (None if cache_dir is None
            else ensemble_cache_path(cache_dir, household_id,
                                     bank_seed_of(episode_id), seeds))
    if path is not None and path.exists():
        return RealizationEnsemble.load(path)
    ensemble = RealizationEnsemble.realize(household_dir, n_days, seeds)
    if path is not None:
        ensemble.save(path)
        logger.info("OracleBelief: cached %d realizations of %s at %s",
                    len(seeds), household_id, path)
    return ensemble


def default_household_dir(household_id: str) -> pathlib.Path:
    """The generated household's directory (holds ``program.yaml``)."""
    from baselines.household_analysis import GENERATED, MODEL_SLUG

    return GENERATED / MODEL_SLUG / household_id


EnsembleLoader = Callable[[EpisodeContext], RealizationEnsemble]


def default_loader(n_seeds: int,
                   cache_dir: Optional[pathlib.Path] = DEFAULT_REALIZATION_CACHE,
                   household_dir: Optional[pathlib.Path] = None
                   ) -> EnsembleLoader:
    """Loader used by the registry: the household's generated program,
    the routine oracle's seed range, the on-disk cache."""
    def load(context: EpisodeContext) -> RealizationEnsemble:
        hh_dir = household_dir or default_household_dir(context.household_id)
        return load_or_realize(hh_dir, context.household_id,
                               context.episode_id, context.n_days, n_seeds,
                               cache_dir)
    return load


# --------------------------------------------------------------- belief

class OracleProgramPosterior(BeliefModel):
    """Realization ensemble weighted by consistency with the observations.

    ``ensemble`` is either a :class:`RealizationEnsemble` (unit tests,
    one-household drivers) or a loader called with the episode context at
    :meth:`reset`. ``eps`` is the per-disagreement weight multiplier.
    """

    consumes_negative_evidence_natively = True

    def __init__(self, rng: random.Random,
                 ensemble: Union[RealizationEnsemble, EnsembleLoader],
                 eps: float = DEFAULT_EPS,
                 floor_mass: float = DEFAULT_FLOOR_MASS,
                 negative_half_life_h: Optional[float] = None) -> None:
        super().__init__(rng, floor_mass=floor_mass,
                         negative_half_life_h=negative_half_life_h)
        if not 0.0 < eps < 1.0:
            raise ValueError(f"OracleBelief: eps {eps} outside (0, 1)")
        self._eps = float(eps)
        self._log_eps = math.log(self._eps)
        self._source = ensemble
        self._ensemble: Optional[RealizationEnsemble] = None
        self._codes: Dict[str, NDArray[np.uint8]] = {}   # object -> uint8[S, M]
        self._code_of: Dict[str, int] = {}        # context receptacle -> code
        self._logw: NDArray[np.float64] = np.zeros(0)
        self._last: Optional[Dict[str, float]] = None
        self.n_observations = 0

    @property
    def name(self) -> str:
        return "OracleBelief"

    @property
    def eps(self) -> float:
        return self._eps

    @property
    def ensemble(self) -> RealizationEnsemble:
        if self._ensemble is None:
            raise RuntimeError("OracleBelief: reset() first")
        return self._ensemble

    # ------------------------------------------------------------ setup

    def reset(self, context: EpisodeContext) -> None:
        super().reset(context)
        ens = (self._source if isinstance(self._source, RealizationEnsemble)
               else self._source(context))
        unknown = set(ens.receptacle_ids) - set(context.receptacle_ids)
        if unknown:
            raise ValueError(
                f"OracleBelief: realizations use receptacles the bank does "
                f"not have: {sorted(unknown)}")
        missing = set(context.object_classes) - set(ens.objects)
        if missing:
            raise ValueError(
                f"OracleBelief: bank objects missing from the realizations: "
                f"{sorted(missing)} — the stored program has drifted from "
                f"the bank")
        # Re-code the ensemble's receptacles into the context's index space
        # so a prediction is one bincount over the context vocabulary.
        remap = np.array([context.receptacle_ids.index(r)
                          for r in ens.receptacle_ids], dtype=np.uint8)
        self._codes = {obj: remap[ens.grid[obj]]
                       for obj in context.object_classes}
        self._code_of = {r: i for i, r in enumerate(context.receptacle_ids)}
        self._ensemble = ens
        self._logw = np.zeros(ens.n_seeds, dtype=np.float64)
        self._last = None
        self.n_observations = 0

    # --------------------------------------------------------- evidence

    def update(self, evidence: Union[Observation, SenseResult]) -> None:
        super().update(evidence)
        if isinstance(evidence, Observation):
            self._weigh(evidence.object_id, evidence.receptacle_id,
                        evidence.t, present=True)
            return
        assert self._context is not None
        present = set(evidence.contents)
        for obj in evidence.contents:
            self._weigh(obj, evidence.receptacle_id, evidence.t, present=True)
        for obj in self._context.object_classes:
            if obj not in present:
                self._weigh(obj, evidence.receptacle_id, evidence.t,
                            present=False)

    def _weigh(self, object_id: str, receptacle_id: str, t: int,
               present: bool) -> None:
        """One observation's factor on every realization's log-weight."""
        codes = self._codes.get(object_id)
        code = self._code_of.get(receptacle_id)
        if codes is None or code is None:
            return                          # an object/receptacle the program lacks
        at = codes[:, self.ensemble.minute_index(t)] == code
        agree = at if present else ~at
        self._logw[~agree] += self._log_eps
        self.n_observations += 1

    # ------------------------------------------------------- weights

    def weights(self) -> NDArray[np.float64]:
        """Normalized realization weights."""
        w: NDArray[np.float64] = np.exp(self._logw - self._logw.max())
        normalized: NDArray[np.float64] = w / w.sum()
        return normalized

    def effective_sample_size(self) -> float:
        """``1 / sum(w_i^2)``: how many realizations still carry weight."""
        w = self.weights()
        return float(1.0 / np.square(w).sum())

    def last_prediction_diagnostics(self) -> Optional[Dict[str, float]]:
        return self._last

    # ---------------------------------------------------------- predict

    def _predict_for_object(self, object_id: str,
                            history: List[Tuple[int, str]],
                            t: int) -> Prediction:
        w = self.weights()
        self._last = {"ess": float(1.0 / np.square(w).sum()),
                      "max_weight": float(w.max())}
        return self._weighted_prediction(object_id, t, w)

    def routine_prediction(self, object_id: str, t: int) -> Prediction:
        """The routine oracle's own answer: uniform weights, no
        observations (the comparison ``OracleBelief`` is measured
        against). Bypasses the pipeline; ties break to the smallest
        receptacle id as in :mod:`baselines.routine_oracle`."""
        n = self.ensemble.n_seeds
        return self._weighted_prediction(object_id, t, np.full(n, 1.0 / n))

    def _weighted_prediction(self, object_id: str, t: int,
                             w: NDArray[np.float64]) -> Prediction:
        assert self._context is not None
        recs = self._context.receptacle_ids
        codes = self._codes[object_id][:, self.ensemble.minute_index(t)]
        mass = np.bincount(codes, weights=w, minlength=len(recs))
        top = mass.max()
        tied = [recs[i] for i in np.flatnonzero(mass >= top - 1e-12)]
        dist = {recs[i]: float(m) for i, m in enumerate(mass) if m > 0.0}
        return Prediction(distribution=dist, argmax=min(tied))
