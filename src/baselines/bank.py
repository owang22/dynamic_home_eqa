"""Episode banks: the JSONL interchange format, its loader, and a synthetic
fixture builder used until real banks exist.

JSONL schema (one JSON object per line; lines of one episode are contiguous
and start with its header; a file may hold many episodes):

    {"kind": "episode_header", "episode_id": str, "household_id": str,
     "receptacle_ids": [str, ...], "object_classes": {object_id: class},
     "budget_per_day": int, "n_days": int}

    {"kind": "truth", "episode_id": str, "object_id": str, "t": int,
     "receptacle_id": str}
        Piecewise-constant ground truth: object is at receptacle from t
        until its next truth row. Every object needs a t=0 row. Times are
        seconds since episode start (as everywhere in this package).

    {"kind": "observation", "episode_id": str, "object_id": str,
     "receptacle_id": str, "t": int, "source": "initial_tour"|"scripted"}
        The fixed observation stream. Rows with source "initial_tour" are
        delivered before day 0; "scripted" rows are delivered in time order
        interleaved with questions. "sense" never appears in a bank — sense
        observations exist only inside a run.

    {"kind": "question", "episode_id": str, "question_id": str,
     "object_id": str, "t_query": int, "day_index": int}

The loader is strict: unknown kinds, out-of-order episode_ids, references
to undeclared receptacles/objects, missing t=0 truth, or day_index
disagreeing with t_query all raise ``BankFormatError`` with the offending
line number. Real-bank producers conform to this schema or negotiate
changes against it.
"""

from __future__ import annotations

import hashlib
import json
import logging
import pathlib
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Protocol, Tuple

from baselines.types import DAY_SECONDS, Episode, Observation, Question

logger = logging.getLogger(__name__)

_BANK_SOURCES = ("initial_tour", "scripted")


class BankFormatError(ValueError):
    """A malformed bank row; message carries file, line number, and context."""


class EpisodeBank(Protocol):
    """What the harness and CLI need from any bank implementation."""

    @property
    def path(self) -> pathlib.Path:
        """Where the bank lives on disk (for provenance)."""

    @property
    def manifest_hash(self) -> str:
        """Stable content hash of the bank file (for provenance)."""

    def episodes(self) -> Iterator[Episode]:
        """Yield episodes in file order."""


@dataclass(frozen=True)
class JsonlBank:
    """Loader for the JSONL schema documented in this module's docstring."""

    path: pathlib.Path

    @property
    def manifest_hash(self) -> str:
        """SHA-256 of the bank file bytes."""
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def episodes(self) -> Iterator[Episode]:
        """Parse and yield each episode, validating as documented."""
        current: _EpisodeAccumulator | None = None
        with open(self.path) as f:
            for lineno, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as err:
                    raise BankFormatError(
                        f"{self.path}:{lineno}: invalid JSON: {err}") from err
                kind = row.get("kind")
                if kind == "episode_header":
                    if current is not None:
                        yield current.finish()
                    current = _EpisodeAccumulator(row, self.path, lineno)
                elif current is None:
                    raise BankFormatError(
                        f"{self.path}:{lineno}: {kind!r} row before any "
                        f"episode_header")
                elif kind in ("truth", "observation", "question"):
                    current.add(kind, row, lineno)
                else:
                    raise BankFormatError(
                        f"{self.path}:{lineno}: unknown kind {kind!r}")
        if current is not None:
            yield current.finish()


class _EpisodeAccumulator:
    """Builds one Episode from its header + body rows, validating eagerly."""

    def __init__(self, header: Dict[str, Any], path: pathlib.Path,
                 lineno: int) -> None:
        self._path = path
        try:
            self.episode_id = str(header["episode_id"])
            self.household_id = str(header["household_id"])
            self.receptacles = tuple(str(r) for r in header["receptacle_ids"])
            self.object_classes = {
                str(k): str(v)
                for k, v in header["object_classes"].items()}
            self.budget_per_day = int(header["budget_per_day"])
            self.n_days = int(header["n_days"])
        except (KeyError, TypeError, AttributeError) as err:
            raise BankFormatError(
                f"{path}:{lineno}: bad episode_header: {err}") from err
        self._truth: Dict[str, List[Tuple[int, str]]] = {}
        self._observations: List[Observation] = []
        self._questions: List[Question] = []

    def _check(self, cond: bool, lineno: int, msg: str) -> None:
        if not cond:
            raise BankFormatError(
                f"{self._path}:{lineno} (episode {self.episode_id}): {msg}")

    def add(self, kind: str, row: Dict[str, Any], lineno: int) -> None:
        self._check(row.get("episode_id") == self.episode_id, lineno,
                    f"episode_id {row.get('episode_id')!r} does not match header")
        if kind == "truth":
            obj, rec, t = str(row["object_id"]), str(row["receptacle_id"]), int(row["t"])
            self._check(obj in self.object_classes, lineno, f"unknown object {obj!r}")
            self._check(rec in self.receptacles, lineno, f"unknown receptacle {rec!r}")
            self._truth.setdefault(obj, []).append((t, rec))
        elif kind == "observation":
            source = str(row["source"])
            self._check(source in _BANK_SOURCES, lineno,
                        f"bank observation source must be one of {_BANK_SOURCES}, "
                        f"got {source!r}")
            obj = str(row["object_id"])
            self._check(obj in self.object_classes, lineno, f"unknown object {obj!r}")
            rec = str(row["receptacle_id"])
            self._check(rec in self.receptacles, lineno, f"unknown receptacle {rec!r}")
            self._observations.append(Observation(
                object_id=obj, object_class=self.object_classes[obj],
                receptacle_id=rec, t=int(row["t"]), source=source))
        else:  # question
            obj = str(row["object_id"])
            self._check(obj in self.object_classes, lineno, f"unknown object {obj!r}")
            try:
                q = Question(
                    question_id=str(row["question_id"]), object_id=obj,
                    t_query=int(row["t_query"]), day_index=int(row["day_index"]))
            except ValueError as err:
                raise BankFormatError(
                    f"{self._path}:{lineno} (episode {self.episode_id}): {err}"
                ) from err
            self._check(q.day_index < self.n_days, lineno,
                        f"question day_index {q.day_index} >= n_days {self.n_days}")
            self._questions.append(q)

    def finish(self) -> Episode:
        for obj in self.object_classes:
            traj = sorted(self._truth.get(obj, []))
            if not traj or traj[0][0] != 0:
                raise BankFormatError(
                    f"{self._path} (episode {self.episode_id}): object {obj!r} "
                    f"has no t=0 truth row")
        by_day: List[List[Question]] = [[] for _ in range(self.n_days)]
        for q in self._questions:
            by_day[q.day_index].append(q)
        initial = tuple(o for o in self._observations if o.source == "initial_tour")
        scripted = tuple(sorted(
            (o for o in self._observations if o.source == "scripted"),
            key=lambda o: o.t))
        episode = Episode(
            episode_id=self.episode_id, household_id=self.household_id,
            receptacle_ids=self.receptacles, object_classes=self.object_classes,
            initial_observations=initial, scripted_observations=scripted,
            questions_by_day=tuple(
                tuple(sorted(day, key=lambda q: q.t_query)) for day in by_day),
            budget_per_day=self.budget_per_day,
            trajectories={obj: tuple(sorted(self._truth[obj]))
                          for obj in self.object_classes})
        logger.debug("loaded episode %s: %d objects, %d questions",
                     episode.episode_id, len(episode.object_classes),
                     sum(len(d) for d in episode.questions_by_day))
        return episode


# --------------------------------------------------------------------------
# Synthetic fixture bank
# --------------------------------------------------------------------------

_H = 3600
_FIXTURE_RECEPTACLES = ("counter_k", "desk_o", "entry_e", "shelf_l")
_TRAIN_DAYS = range(0, 4)
_QUESTION_DAYS = range(4, 7)
_FIXTURE_N_DAYS = 7
_FIXTURE_BUDGET = 2


def write_synthetic_bank(path: pathlib.Path) -> JsonlBank:
    """Write the deterministic three-object fixture bank and return its loader.

    Construction (all times seconds since episode start; days 0-3 provide
    scripted sightings, days 4-6 carry the questions):

    * ``mug_static`` never leaves ``counter_k``; observed only on the
      initial tour. Every belief should localize it perfectly.
    * ``keys_periodic`` follows a strict daily schedule — ``entry_e``
      overnight, ``desk_o`` 09:00-18:00 — with scripted sightings at 10:00
      (desk) and 20:00 (entry) on each train day. Question times alternate
      10:05 / 20:05, so a timetable belief is exactly right while
      frequency and recency beliefs are right only at 20:05.
    * ``laptop_mover`` sits on ``desk_o`` until noon of day 3, then moves
      permanently to ``shelf_l``; sightings at 09:00 on days 0-1 (desk) and
      14:00 on day 3 (shelf). Last-observation localizes it after the
      move; most-frequent stays wrong (2 desk sightings + tour vs 1 shelf).

    The file round-trips through :class:`JsonlBank` so loader and schema
    are exercised by every test that touches the fixture.
    """
    rows: List[Dict[str, Any]] = [{
        "kind": "episode_header", "episode_id": "synthetic_ep0",
        "household_id": "synthetic_hh", "receptacle_ids": list(_FIXTURE_RECEPTACLES),
        "object_classes": {"mug_static": "mug", "keys_periodic": "keys",
                           "laptop_mover": "laptop"},
        "budget_per_day": _FIXTURE_BUDGET, "n_days": _FIXTURE_N_DAYS,
    }]

    def truth(obj: str, t: int, rec: str) -> None:
        rows.append({"kind": "truth", "episode_id": "synthetic_ep0",
                     "object_id": obj, "t": t, "receptacle_id": rec})

    def obs(obj: str, t: int, rec: str, source: str) -> None:
        rows.append({"kind": "observation", "episode_id": "synthetic_ep0",
                     "object_id": obj, "t": t, "receptacle_id": rec,
                     "source": source})

    truth("mug_static", 0, "counter_k")
    truth("laptop_mover", 0, "desk_o")
    truth("laptop_mover", 3 * DAY_SECONDS + 12 * _H, "shelf_l")
    for d in range(_FIXTURE_N_DAYS):
        base = d * DAY_SECONDS
        truth("keys_periodic", base, "entry_e")
        truth("keys_periodic", base + 9 * _H, "desk_o")
        truth("keys_periodic", base + 18 * _H, "entry_e")

    obs("mug_static", 0, "counter_k", "initial_tour")
    obs("keys_periodic", 0, "entry_e", "initial_tour")
    obs("laptop_mover", 0, "desk_o", "initial_tour")
    for d in _TRAIN_DAYS:
        base = d * DAY_SECONDS
        obs("keys_periodic", base + 10 * _H, "desk_o", "scripted")
        obs("keys_periodic", base + 20 * _H, "entry_e", "scripted")
    obs("laptop_mover", 0 * DAY_SECONDS + 9 * _H, "desk_o", "scripted")
    obs("laptop_mover", 1 * DAY_SECONDS + 9 * _H, "desk_o", "scripted")
    obs("laptop_mover", 3 * DAY_SECONDS + 14 * _H, "shelf_l", "scripted")

    qn = 0
    for d in _QUESTION_DAYS:
        base = d * DAY_SECONDS
        for obj, t in (("keys_periodic", base + 10 * _H + 300),
                       ("mug_static", base + 11 * _H),
                       ("laptop_mover", base + 12 * _H + 300),
                       ("keys_periodic", base + 20 * _H + 300)):
            rows.append({"kind": "question", "episode_id": "synthetic_ep0",
                         "question_id": f"q{qn:03d}", "object_id": obj,
                         "t_query": t, "day_index": d})
            qn += 1

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    logger.info("wrote synthetic bank: %d rows -> %s", len(rows), path)
    return JsonlBank(path=path)
