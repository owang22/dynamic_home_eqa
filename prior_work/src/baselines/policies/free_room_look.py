"""The patrol protocol's look policy for belief models: take the one free
look at the room with the largest one-step value of information (or the
room holding the belief's argmax, ``mode="top"``), then answer. No price,
no threshold; the harness expands the sense into a look at the whole room
(:class:`~baselines.harness.RoomLook`) and caps it at one per question.

Room value of information under the base pipeline's semantics: a look at
room R finds the object with probability p(R) = sum of p over R's spots,
otherwise every spot in R is zeroed and the best remaining guess is worth
max over spots outside R, so voi(R) = p(R) + max_{s not in R} p(s) - max(p).
"""
from __future__ import annotations

from typing import Dict, List, Mapping, Optional

from baselines.policies.base import DecisionPolicy
from baselines.types import (ON_PERSON, OUT_OF_HOUSE, Action, AnswerNow,
                             EpisodeContext, Prediction, Question, Sense,
                             SenseResult)


def room_voi(p: Mapping[str, float], rooms: Mapping[str, List[str]]) -> Dict[str, float]:
    best = max(p.values())
    out = {}
    for room in sorted(rooms):
        inside = set(rooms[room])
        p_room = sum(p.get(r, 0.0) for r in inside)
        outside = max((v for s, v in p.items() if s not in inside), default=0.0)
        out[room] = p_room + outside - best
    return out


def choose_room(p: Mapping[str, float], rooms: Mapping[str, List[str]], mode: str) -> str:
    if mode == "voi":
        score = room_voi(p, rooms)
    elif mode == "top":
        best = max(p, key=lambda r: (p[r], r))
        score = {room: (1.0 if best in recs else sum(p.get(r, 0.0) for r in recs))
                 for room, recs in rooms.items()}
    else:
        raise ValueError(f"FreeRoomLook: unknown mode {mode!r}")
    top = max(score.values())
    return sorted(r for r, v in score.items() if v == top)[0]


class FreeRoomLook(DecisionPolicy):
    """One free look per question at the VoI-argmax (or top) room."""

    def __init__(self, mode: str = "voi") -> None:
        if mode not in ("voi", "top"):
            raise ValueError(f"FreeRoomLook: mode must be voi or top, got {mode!r}")
        self._mode = mode
        self._rooms: Dict[str, List[str]] = {}
        self._question_id: Optional[str] = None
        self._looked = False

    @property
    def name(self) -> str:
        return f"FreeRoomLook({self._mode})"

    def reset(self, context: EpisodeContext) -> None:
        rooms: Dict[str, List[str]] = {}
        for rec in context.sensable_receptacle_ids:
            room = context.receptacle_rooms.get(rec)
            if room is not None and rec not in (ON_PERSON, OUT_OF_HOUSE):
                rooms.setdefault(room, []).append(rec)
        self._rooms = {r: sorted(v) for r, v in sorted(rooms.items())}
        self._question_id = None
        self._looked = False

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        if question.question_id != self._question_id:
            self._question_id = question.question_id
            self._looked = False
        if self._looked or not self._rooms:
            return AnswerNow()
        self._looked = True
        room = choose_room(dict(prediction.distribution), self._rooms, self._mode)
        return Sense(receptacle_id=self._rooms[room][0])
