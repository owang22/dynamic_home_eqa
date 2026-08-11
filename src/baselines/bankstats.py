"""Bank-intrinsic statistics: how stationary is the world, before any agent
runs?

Everything here is computed from ground truth (and question placement)
alone — no agents, no baseline panel, fractions of a second per bank. It
exists so the data-generation workstream gets an instant feedback loop:
tweak the generator, run ``python -m baselines.cli bankstats BANK``, and
only run the full healthcheck panel once these numbers look right.

The headline number is **dwell-weighted modal share**: the fraction of
time an object spends at its single most-occupied receptacle, averaged
over objects. A model that knows nothing but each object's home base is
right exactly that often at a uniformly sampled moment, so no amount of
questions, days, or agents makes a high-modal-share bank interesting —
the ``stationarity`` gate fails any bank above the threshold (default
0.60). Also reported: modal share evaluated at the bank's actual question
times (what the examiner samples), moves per day, the distribution of
contiguous away-from-home displacement intervals (short excursions vs
persistent displacement), and the worst per-day question repeat count
(uniform draws over few objects concentrate; repeats amplify single-object
noise).

All times are seconds since episode start; durations are reported in
hours.
"""

from __future__ import annotations

import collections
import dataclasses
import json
import logging
import pathlib
from typing import Dict, List, Tuple

from baselines.bank import JsonlBank
from baselines.types import DAY_SECONDS, Episode

logger = logging.getLogger(__name__)

DEFAULT_MAX_MODAL_SHARE = 0.60
"""Stationarity ceiling: dwell-weighted modal share above this fails."""


@dataclasses.dataclass(frozen=True)
class ObjectDwell:
    """One object's home-base profile within one episode."""

    object_id: str
    modal_receptacle: str
    modal_share: float                  # fraction of the horizon at modal
    displacement_intervals_s: Tuple[int, ...]   # contiguous away-from-modal


@dataclasses.dataclass(frozen=True)
class BankStats:
    """Ground-truth-intrinsic statistics for one bank."""

    n_episodes: int
    n_objects: int
    n_receptacles: int
    n_days: int
    n_questions: int
    modal_share_time: float         # dwell-weighted, mean over objects
    modal_share_questions: float    # evaluated at the bank's (obj, t) pairs
    moves_per_day: float            # true location changes per episode-day
    displacement_median_h: float    # median contiguous away-from-home stint
    displacement_p90_h: float
    displaced_time_share: float     # fraction of object-time away from home
    max_repeats_per_day: int        # worst (episode, day, object) count
    per_object_modal_share: Dict[str, float]


def _object_dwell(episode: Episode, object_id: str) -> ObjectDwell:
    """Home base (max dwell; ties -> earliest first entry) and excursions."""
    horizon = episode.n_days * DAY_SECONDS
    traj = episode.trajectories[object_id]
    dwell: Dict[str, int] = collections.defaultdict(int)
    first_entry: Dict[str, int] = {}
    for i, (t, rec) in enumerate(traj):
        end = traj[i + 1][0] if i + 1 < len(traj) else horizon
        dwell[rec] += max(0, min(end, horizon) - t)
        first_entry.setdefault(rec, t)
    top = max(dwell.values())
    modal = min((r for r, d in dwell.items() if d == top),
                key=lambda r: first_entry[r])
    intervals: List[int] = []
    away_since: int | None = None
    for i, (t, rec) in enumerate(traj):
        if rec != modal and away_since is None:
            away_since = t
        elif rec == modal and away_since is not None:
            intervals.append(t - away_since)
            away_since = None
    if away_since is not None:
        intervals.append(horizon - away_since)
    return ObjectDwell(object_id=object_id, modal_receptacle=modal,
                       modal_share=dwell[modal] / horizon,
                       displacement_intervals_s=tuple(intervals))


def _percentile(sorted_values: List[int], q: float) -> float:
    """Nearest-rank percentile of a pre-sorted list; 0.0 when empty."""
    if not sorted_values:
        return 0.0
    rank = min(len(sorted_values) - 1, int(q * len(sorted_values)))
    return float(sorted_values[rank])


def compute_bank_stats(bank: JsonlBank) -> BankStats:
    """All intrinsic statistics for a bank; pure ground-truth arithmetic."""
    episodes = list(bank.episodes())
    dwells: List[ObjectDwell] = []
    intervals: List[int] = []
    moves = 0
    modal_hits = questions = 0
    repeats: collections.Counter[Tuple[str, int, str]] = collections.Counter()
    for ep in episodes:
        by_object = {obj: _object_dwell(ep, obj) for obj in ep.trajectories}
        dwells += by_object.values()
        for obj, traj in ep.trajectories.items():
            intervals += by_object[obj].displacement_intervals_s
            moves += sum(1 for i in range(1, len(traj))
                         if traj[i][1] != traj[i - 1][1])
        for day in ep.questions_by_day:
            for q in day:
                questions += 1
                truth = ep.true_location(q.object_id, q.t_query)
                modal_hits += truth == by_object[q.object_id].modal_receptacle
                repeats[(ep.episode_id, q.day_index, q.object_id)] += 1
    intervals.sort()
    total_days = sum(ep.n_days for ep in episodes)
    return BankStats(
        n_episodes=len(episodes),
        n_objects=sum(len(ep.trajectories) for ep in episodes),
        n_receptacles=len(episodes[0].receptacle_ids),
        n_days=episodes[0].n_days,
        n_questions=questions,
        modal_share_time=sum(d.modal_share for d in dwells) / len(dwells),
        modal_share_questions=(modal_hits / questions) if questions else 0.0,
        moves_per_day=moves / total_days if total_days else 0.0,
        displacement_median_h=_percentile(intervals, 0.5) / 3600,
        displacement_p90_h=_percentile(intervals, 0.9) / 3600,
        displaced_time_share=1.0 - sum(d.modal_share for d in dwells)
        / len(dwells),
        max_repeats_per_day=max(repeats.values()) if repeats else 0,
        per_object_modal_share={d.object_id: round(d.modal_share, 4)
                                for d in dwells})


def stationarity_passes(stats: BankStats,
                        max_modal_share: float = DEFAULT_MAX_MODAL_SHARE
                        ) -> bool:
    """The generator-side gate: is the world non-trivial by construction?"""
    return stats.modal_share_time <= max_modal_share


def render_text(bank_path: pathlib.Path, stats: BankStats,
                max_modal_share: float) -> str:
    """Self-explanatory stdout summary (no baselines knowledge assumed)."""
    passed = stationarity_passes(stats, max_modal_share)
    return "\n".join([
        f"BANK-INTRINSIC STATS — {bank_path.name}",
        f"  {stats.n_questions} questions over {stats.n_days} days; "
        f"{stats.n_objects} objects, {stats.n_receptacles} receptacles"
        f" ({stats.n_episodes} episode(s))",
        "",
        f"  dwell-weighted modal share   {stats.modal_share_time:.3f}   "
        "(chance a home-base-only model is right at a random moment)",
        f"  modal share at query times   {stats.modal_share_questions:.3f}   "
        "(same, at the moments the bank actually asks)",
        f"  true moves per day           {stats.moves_per_day:.1f}",
        f"  displacement stints          median "
        f"{stats.displacement_median_h:.1f} h, p90 "
        f"{stats.displacement_p90_h:.1f} h "
        f"(displaced {stats.displaced_time_share:.0%} of the time)",
        f"  worst per-day repeat draw    {stats.max_repeats_per_day} "
        "questions on one object in one day",
        "",
        f"  [{'PASS' if passed else 'FAIL'}] stationarity: modal share "
        f"{stats.modal_share_time:.3f} must be <= {max_modal_share:.2f} — "
        "above it, scale only buys tighter error bars around a bank that "
        "passive memory mostly solves",
    ])


def json_dict(bank: JsonlBank, stats: BankStats,
              max_modal_share: float) -> Dict[str, object]:
    """Machine-readable report block (embedded by the healthcheck too)."""
    d: Dict[str, object] = dataclasses.asdict(stats)
    d["stationarity_max_modal_share"] = max_modal_share
    d["stationarity_pass"] = stationarity_passes(stats, max_modal_share)
    d["bank_manifest_hash"] = bank.manifest_hash
    return d


def write_report(bank: JsonlBank, stats: BankStats, max_modal_share: float,
                 out_dir: pathlib.Path) -> None:
    """Write bankstats.json + bankstats.txt under ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "bankstats.json").write_text(
        json.dumps(json_dict(bank, stats, max_modal_share), indent=2) + "\n")
    (out_dir / "bankstats.txt").write_text(
        render_text(bank.path, stats, max_modal_share) + "\n")
    logger.info("wrote %s/bankstats.{json,txt}", out_dir)
