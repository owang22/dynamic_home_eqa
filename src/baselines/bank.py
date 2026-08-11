"""Episode banks: the JSONL interchange format, its loader, and a synthetic
fixture builder used until real banks exist.

JSONL schema (one JSON object per line; lines of one episode are contiguous
and start with its header; a file may hold many episodes):

    {"kind": "episode_header", "episode_id": str, "household_id": str,
     "receptacle_ids": [str, ...], "object_classes": {object_id: class},
     "budget_per_day": int, "n_days": int,
     "household_type": str (optional bank metadata; enables the
      healthcheck's stratified discriminative gate),
     "unsensable_receptacles": [str, ...] (optional, default none: legal
      ANSWERS that Sense may never target — e.g. OUT_OF_HOUSE; agents can
      only infer them by eliminating every sensable receptacle)}

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
import random
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
            raw_type = header.get("household_type")
            self.household_type = None if raw_type is None else str(raw_type)
            self.unsensable = tuple(
                str(r) for r in header.get("unsensable_receptacles", []))
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
                          for obj in self.object_classes},
            household_type=self.household_type,
            unsensable_receptacle_ids=self.unsensable)
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
      10:05 / 20:05, so beliefs that ignore time-of-day (frequency and
      recency alike) are right only at 20:05 — the periodic stress case.
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


# --------------------------------------------------------------------------
# Negative-evidence fixture bank
# --------------------------------------------------------------------------

_NEG_RECEPTACLES = ("shelf_a", "shelf_b", "shelf_c", "shelf_d")


def write_negative_evidence_bank(path: pathlib.Path) -> JsonlBank:
    """A fixture where negative evidence is decisive (times in seconds).

    ``wallet_hidden`` is sighted three times at ``shelf_a`` (tour plus two
    scripted sightings on day 0) and then silently moves to ``shelf_c`` on
    day 1 at 22:00. Every basic belief therefore favors ``shelf_a`` at the
    day-2 question — recency and frequency directly, the timetable via its
    empty-bin fallback. A search that ignores negative evidence senses
    ``shelf_a`` (whose contents are non-empty: the static ``coin_decoy``
    is there), learns nothing, and answers ``shelf_a`` — wrong even at
    unlimited budget. With exclusions, the miss zeroes ``shelf_a`` and the
    search sweeps the remaining three receptacles, finding the wallet in
    at most four senses total.

    ``coin_decoy`` stays at ``shelf_a`` forever, so the sensed receptacle
    is never empty — exclusion must come from the wallet's absence, not
    from an empty result.
    """
    rows: List[Dict[str, Any]] = [{
        "kind": "episode_header", "episode_id": "negative_ep0",
        "household_id": "negative_hh",
        "receptacle_ids": list(_NEG_RECEPTACLES),
        "object_classes": {"wallet_hidden": "wallet", "coin_decoy": "coin"},
        "budget_per_day": 8, "n_days": 3,
    }]

    def add(kind: str, **fields: Any) -> None:
        rows.append({"kind": kind, "episode_id": "negative_ep0", **fields})

    add("truth", object_id="coin_decoy", t=0, receptacle_id="shelf_a")
    add("truth", object_id="wallet_hidden", t=0, receptacle_id="shelf_a")
    add("truth", object_id="wallet_hidden", t=DAY_SECONDS + 22 * 3600,
        receptacle_id="shelf_c")
    for obj in ("wallet_hidden", "coin_decoy"):
        add("observation", object_id=obj, t=0, receptacle_id="shelf_a",
            source="initial_tour")
    for t in (10 * 3600, 18 * 3600):
        add("observation", object_id="wallet_hidden", t=t,
            receptacle_id="shelf_a", source="scripted")
    add("question", question_id="q_wallet", object_id="wallet_hidden",
        t_query=2 * DAY_SECONDS + 12 * 3600, day_index=2)
    add("question", question_id="q_coin", object_id="coin_decoy",
        t_query=2 * DAY_SECONDS + 13 * 3600, day_index=2)

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    logger.info("wrote negative-evidence bank: %d rows -> %s", len(rows), path)
    return JsonlBank(path=path)


# --------------------------------------------------------------------------
# Healthcheck gate-test banks
# --------------------------------------------------------------------------

_PASS_RECEPTACLES = ("kitchen_c", "desk_d", "entry_e", "shelf_s",
                     "sofa_f", "drawer_w", "bath_b", "bin_n")
_PASS_N_DAYS = 14
_PASS_TRAIN_DAYS = range(0, 4)
_PASS_QUESTION_DAYS = range(4, 14)
_PASS_BUDGET = 24


def _loc_at(trajectory: List[Tuple[int, str]], t: int) -> str:
    """Receptacle at time ``t`` for a sorted change-point list (t0 == 0)."""
    location = trajectory[0][1]
    for change_t, receptacle in trajectory:
        if change_t > t:
            break
        location = receptacle
    return location


def _pass_bank_trajectories(
        rng: random.Random) -> Dict[str, List[Tuple[int, str]]]:
    """Ground truth for the PASS bank's four dynamics families:
    static / strictly periodic / nightly drifter / fast roamer."""
    h = 3600
    trajectories: Dict[str, List[Tuple[int, str]]] = {
        "mug_anchor": [(0, "kitchen_c")]}
    for obj in ("keys_shift", "badge_shift"):
        traj: List[Tuple[int, str]] = []
        for d in range(_PASS_N_DAYS):
            base = d * DAY_SECONDS
            traj += [(base, "entry_e"), (base + 9 * h, "desk_d"),
                     (base + 18 * h, "entry_e")]
        trajectories[obj] = traj
    for obj in ("drift_a", "drift_b", "drift_c"):
        traj = [(0, rng.choice(_PASS_RECEPTACLES))]
        for d in range(_PASS_N_DAYS):
            traj.append((d * DAY_SECONDS + 21 * h,
                         rng.choice(_PASS_RECEPTACLES)))
        trajectories[obj] = traj
    roam = [(0, rng.choice(_PASS_RECEPTACLES))]
    for d in range(_PASS_N_DAYS):
        for move_hour in (5, 11, 17, 23):
            roam.append((d * DAY_SECONDS + move_hour * h,
                         rng.choice(_PASS_RECEPTACLES)))
    trajectories["roam_fast"] = roam
    return trajectories


def _pass_bank_observations(
        trajectories: Dict[str, List[Tuple[int, str]]]
        ) -> List[Tuple[str, int, str, str]]:
    """(object, t, receptacle, source) rows: tour at t=0 for everything,
    then scripted sightings per family (periodic objects only on train
    days, so recency stays stuck; drifters every even day at noon; the
    roamer daily at 07:00)."""
    h = 3600
    obs: List[Tuple[str, int, str, str]] = [
        (obj, 0, _loc_at(traj, 0), "initial_tour")
        for obj, traj in trajectories.items()]
    for obj in ("keys_shift", "badge_shift"):
        for d in _PASS_TRAIN_DAYS:
            base = d * DAY_SECONDS
            obs.append((obj, base + 10 * h, "desk_d", "scripted"))
            obs.append((obj, base + 20 * h, "entry_e", "scripted"))
    for obj in ("drift_a", "drift_b", "drift_c"):
        for d in range(0, _PASS_N_DAYS, 2):
            t = d * DAY_SECONDS + 12 * h
            obs.append((obj, t, _loc_at(trajectories[obj], t), "scripted"))
    for d in range(_PASS_N_DAYS):
        t = d * DAY_SECONDS + 7 * h
        obs.append(("roam_fast", t, _loc_at(trajectories["roam_fast"], t),
                    "scripted"))
    return obs


_PASS_DAILY_QUESTIONS: Tuple[Tuple[str, int], ...] = (
    # (object, seconds into the day); 31 per day x 10 question days = 310.
    # The mix is weighted toward the drifters so the passive ceiling stays
    # under the not_trivial gate even for the decayed (honest-strong)
    # frequency/timetable beliefs, which nearly solve the periodic pair.
    ("mug_anchor", 11 * 3600), ("mug_anchor", 14 * 3600),
    ("mug_anchor", 16 * 3600),
    ("keys_shift", 10 * 3600 + 900), ("keys_shift", 20 * 3600 + 2700),
    ("badge_shift", 10 * 3600 + 1200), ("badge_shift", 20 * 3600 + 3000),
    ("drift_a", 13 * 3600 + 1800), ("drift_a", 14 * 3600 + 900),
    ("drift_a", 15 * 3600), ("drift_a", 15 * 3600 + 1800),
    ("drift_a", 16 * 3600 + 900), ("drift_a", 16 * 3600 + 1800),
    ("drift_a", 17 * 3600 + 600),
    ("drift_b", 13 * 3600 + 2100), ("drift_b", 14 * 3600 + 1200),
    ("drift_b", 15 * 3600 + 300), ("drift_b", 15 * 3600 + 2100),
    ("drift_b", 16 * 3600 + 1200), ("drift_b", 16 * 3600 + 2100),
    ("drift_b", 17 * 3600 + 900),
    ("drift_c", 13 * 3600 + 2400), ("drift_c", 14 * 3600 + 1500),
    ("drift_c", 15 * 3600 + 600), ("drift_c", 15 * 3600 + 2400),
    ("drift_c", 16 * 3600 + 1500), ("drift_c", 16 * 3600 + 2400),
    ("drift_c", 17 * 3600 + 1200),
    ("roam_fast", 15 * 3600 + 1200), ("roam_fast", 18 * 3600 + 1800),
    ("roam_fast", 19 * 3600 + 600),
)


def write_gate_pass_bank(path: pathlib.Path, seed: int = 0) -> JsonlBank:
    """A bank engineered to PASS all five healthcheck gates.

    Dynamics families and their intended NeverSense profiles (derivation
    mirrors ``write_synthetic_bank``; exact values are seeded-random but
    stable): a static anchor (everyone 1.0), two strictly periodic objects
    whose sightings stop after day 3 (timetable 1.0, recency/frequency
    0.5), three nightly drifters sighted every other noon (recency ~0.55,
    frequency/timetable far worse), and a four-moves-a-day roamer nobody
    tracks. Weighted by the daily question mix this lands every belief
    under the not_trivial ceiling with clear spread (discriminative), 310
    questions (powered), and a budget generous enough that search buys
    accuracy (not_impossible). Solvable holds for any well-formed bank.

    ``household_type`` metadata is present so the stratified
    discriminative path is exercised.
    """
    rng = random.Random(seed)
    trajectories = _pass_bank_trajectories(rng)
    rows: List[Dict[str, Any]] = [{
        "kind": "episode_header", "episode_id": f"gate_pass_ep{seed}",
        "household_id": "gate_pass_hh", "household_type": "synthetic_mixed",
        "receptacle_ids": list(_PASS_RECEPTACLES),
        "object_classes": {
            "mug_anchor": "mug", "keys_shift": "keys",
            "badge_shift": "badge", "drift_a": "tote", "drift_b": "tote",
            "drift_c": "tote", "roam_fast": "toy"},
        "budget_per_day": _PASS_BUDGET, "n_days": _PASS_N_DAYS,
    }]
    episode_id = f"gate_pass_ep{seed}"
    for obj, traj in trajectories.items():
        for t, rec in traj:
            rows.append({"kind": "truth", "episode_id": episode_id,
                         "object_id": obj, "t": t, "receptacle_id": rec})
    for obj, t, rec, source in _pass_bank_observations(trajectories):
        rows.append({"kind": "observation", "episode_id": episode_id,
                     "object_id": obj, "t": t, "receptacle_id": rec,
                     "source": source})
    qn = 0
    for d in _PASS_QUESTION_DAYS:
        for obj, offset in _PASS_DAILY_QUESTIONS:
            rows.append({"kind": "question", "episode_id": episode_id,
                         "question_id": f"q{qn:04d}", "object_id": obj,
                         "t_query": d * DAY_SECONDS + offset,
                         "day_index": d})
            qn += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    logger.info("wrote gate-pass bank: %d rows -> %s", len(rows), path)
    return JsonlBank(path=path)


_FAIL_RECEPTACLES = ("kitchen_c", "desk_d", "entry_e",
                     "shelf_s", "sofa_f", "drawer_w")


def write_gate_fail_static_bank(path: pathlib.Path) -> JsonlBank:
    """A static-world bank engineered to FAIL the not_trivial gate.

    Six objects never move and the initial tour reveals all of them, so
    every belief model answers every question correctly without sensing:
    NeverSense accuracy is 1.0, far above the not_trivial ceiling (and the
    spread is exactly 0, so discriminative fails too — a static world
    cannot rank modeling assumptions). 300 questions keep the powered
    gate out of the way; the failure is about dynamics, not scale. No
    ``household_type`` metadata, so the stratified check reports SKIPPED.
    """
    objects = {f"item_{i}": "widget" for i in range(6)}
    episode_id = "gate_fail_ep0"
    rows: List[Dict[str, Any]] = [{
        "kind": "episode_header", "episode_id": episode_id,
        "household_id": "gate_fail_hh",
        "receptacle_ids": list(_FAIL_RECEPTACLES),
        "object_classes": objects, "budget_per_day": 4, "n_days": 12,
    }]
    for i, obj in enumerate(objects):
        home = _FAIL_RECEPTACLES[i % len(_FAIL_RECEPTACLES)]
        rows.append({"kind": "truth", "episode_id": episode_id,
                     "object_id": obj, "t": 0, "receptacle_id": home})
        rows.append({"kind": "observation", "episode_id": episode_id,
                     "object_id": obj, "t": 0, "receptacle_id": home,
                     "source": "initial_tour"})
    qn = 0
    for d in range(2, 12):
        for k in range(30):
            obj = f"item_{k % len(objects)}"
            rows.append({"kind": "question", "episode_id": episode_id,
                         "question_id": f"q{qn:04d}", "object_id": obj,
                         "t_query": d * DAY_SECONDS + (8 + k // 2) * 1800
                         + 8 * 3600, "day_index": d})
            qn += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    logger.info("wrote gate-fail bank: %d rows -> %s", len(rows), path)
    return JsonlBank(path=path)
