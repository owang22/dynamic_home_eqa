"""Naive LLM belief: hand the object's evidence to a language model and
ask where it is.

A floor measurement, not a design. The model receives, per question, the
current time with its weekday, the object, the home's receptacles grouped
by room, the object's sighting history and the negative evidence gathered
since its last sighting, and answers with a JSON ranking. No chain of
thought, no examples, no routine summary: those are the variants to test
against this floor later.

The two things every classical model on these banks lacks come for free:
OUT_OF_HOUSE and ON_PERSON are offered as first-class answers, and the
weekday and time of day are in the prompt.

Interface. This is an ordinary :class:`BeliefModel`; the evidence
bookkeeping is the base class's. Negative evidence goes into the prompt,
so the base class's hard exclusion is bypassed exactly as the Perpetua
models bypass it (:meth:`LLMBelief._apply_exclusions` is the identity).
Generation is offline and batched, so the model does not call the LLM
itself: it asks a :class:`PromptCache` for the answer to a prompt key.
In *collect* mode the cache records the prompt and answers None (the
model falls back to LastObs and counts the question as pending); after a
batch run the same cache answers from its completions. Two replays of
one bank with the same cache therefore give byte-identical prompts, and
the key makes identical situations reuse one completion.

Cache key: (episode, object, last sighting, newest active exclusion,
hour bucket of the query). Two questions with the same key differ only
by minutes inside the hour and see the same evidence.

Output handling: the ranking becomes a distribution by fixed geometric
weights (0.5, 0.25, ...) renormalized over the ranked names, so log-loss
is defined; ``p_top`` is logged, never used. A completion that does not
parse, ranks nothing, or names a receptacle outside the offered list
falls back to the LastObs answer (one-hot last sighting with the base
class's exclusions) and is counted.
"""

from __future__ import annotations

import dataclasses
import json
import random
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from baselines.beliefs.base import BeliefModel
from baselines.types import DAY_SECONDS, Prediction

DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday")
"""Day 0 is a Monday, the convention of the timetable and day-type
beliefs (``weekday = day_index % 7``)."""

OUT_OF_HOUSE = "OUT_OF_HOUSE"
ON_PERSON = "ON_PERSON"
SPECIAL_ANSWERS = (ON_PERSON, OUT_OF_HOUSE)
"""Pseudo-receptacles the banks use for 'carried by a resident' and
'taken out of the home'. They are receptacle ids in every bank, so the
harness scores them like any other answer."""

ROOM_OF_SUFFIX = {"b": "bedroom", "l": "living room", "k": "kitchen",
                  "ba": "bathroom", "e": "entry"}
"""Fallback room grouping when no receptacle -> room map is supplied:
receptacle ids end in a room code plus an index. The index is NOT
reliable as a room number (``chair_k2`` is the second chair of the one
kitchen), so the fallback groups by code only; the driver passes the
map read from the bank's room-visit rows, which is exact."""
ROOM_LABEL = {"living": "living room"}

_SUFFIX = re.compile(r"^(.*)_([a-z]+)(\d+)$")

SYSTEM_PROMPT = (
    "You track where household objects are from a robot's observations. "
    "Given the current time, the home's receptacles, the object's sighting "
    "history and the places checked since it was last seen, predict where "
    "the object is right now. Reply with JSON only, in the form "
    '{"ranking": [<receptacle names, most likely first>], "p_top": '
    "<probability that the first name is right, 0 to 1>}; every name must "
    "be copied exactly from the receptacle list, or be OUT_OF_HOUSE or "
    "ON_PERSON.")

JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "ranking": {"type": "array", "items": {"type": "string"},
                    "minItems": 1, "maxItems": 5},
        "p_top": {"type": "number"},
    },
    "required": ["ranking", "p_top"],
    "additionalProperties": False,
}
"""Shape enforced by guided decoding when the generator runs with it.
Names are deliberately NOT an enum: an off-list name is a counted
failure, not something the grammar hides."""


@dataclasses.dataclass(frozen=True)
class LLMBeliefConfig:
    """Fixed knobs of the naive prompt (v1)."""

    model: str = "Qwen/Qwen3.8-27B"
    max_history: int = 60          # newest sightings shown
    max_ranking: int = 5           # names asked for, and kept, per answer
    geometric_ratio: float = 0.5   # rank weights 0.5, 0.25, ...
    hour_bucket_s: int = 3600      # cache-key time resolution

    def __post_init__(self) -> None:
        if self.max_history < 1 or self.max_ranking < 1:
            raise ValueError("LLMBeliefConfig: max_history and max_ranking "
                             "must be positive")
        if not 0.0 < self.geometric_ratio < 1.0:
            raise ValueError("LLMBeliefConfig: geometric_ratio in (0, 1)")
        if self.hour_bucket_s < 1:
            raise ValueError("LLMBeliefConfig: hour_bucket_s must be positive")


# ---------------------------------------------------------------- prompt --

def format_time(t: int) -> str:
    """``day 12 (Saturday) 14:32`` for a time in seconds since day 0."""
    day, rem = divmod(int(t), DAY_SECONDS)
    hh, mm = divmod(rem // 60, 60)
    return f"day {day} ({DAY_NAMES[day % 7]}) {hh:02d}:{mm:02d}"


def room_label(room: str) -> str:
    """``bedroom_2`` -> ``bedroom 2``, ``living`` -> ``living room``."""
    return ROOM_LABEL.get(room, room.replace("_", " "))


def room_groups(receptacle_ids: Sequence[str],
                rooms: Optional[Mapping[str, str]] = None
                ) -> List[Tuple[str, List[str]]]:
    """Receptacles grouped by room in first-seen order; the special
    answers are left out (they get their own line). ``rooms`` maps
    receptacle id -> room name (from the bank); without it the room comes
    from the id's suffix code, and an id with no known code lands in
    ``other``."""
    groups: Dict[str, List[str]] = {}
    for rec in receptacle_ids:
        if rec in SPECIAL_ANSWERS:
            continue
        if rooms and rec in rooms:
            label = room_label(rooms[rec])
        else:
            m = _SUFFIX.match(rec)
            label = (ROOM_OF_SUFFIX[m.group(2)]
                     if m and m.group(2) in ROOM_OF_SUFFIX else "other")
        groups.setdefault(label, []).append(rec)
    return list(groups.items())


def build_messages(*, t: int, object_id: str, object_class: str,
                   receptacle_ids: Sequence[str],
                   history: Sequence[Tuple[int, str]],
                   exclusions: Sequence[Tuple[int, str]],
                   config: LLMBeliefConfig,
                   rooms: Optional[Mapping[str, str]] = None
                   ) -> List[Dict[str, str]]:
    """The chat messages for one question (pure; the whole prompt)."""
    seen = {rec for _, rec in history}
    lines = [f"Current time: {format_time(t)}. Day 0 was a Monday.",
             f"Object: {object_id} (class: {object_class}).", "",
             "Receptacles in the home, by room (* marks ones this object "
             "has been seen at):"]
    for room, recs in room_groups(receptacle_ids, rooms):
        lines.append(f"- {room}: " + ", ".join(
            rec + ("*" if rec in seen else "") for rec in recs))
    lines.append(f"- not at any receptacle: {ON_PERSON} (carried by a "
                 f"resident), {OUT_OF_HOUSE} (taken out of the home)")
    shown = list(history)[-config.max_history:]
    header = "Sighting history (oldest first, newest last"
    if len(history) > len(shown):
        header += f"; newest {len(shown)} of {len(history)}"
    lines += ["", header + "):"]
    if shown:
        lines += [f"- {format_time(ot)}: {rec}" for ot, rec in shown]
    else:
        lines.append("- none")
    lines += ["", "Receptacles inspected since the last sighting where the "
                  "object was NOT found:"]
    if exclusions:
        lines += [f"- {format_time(et)}: {rec}"
                  for et, rec in sorted(exclusions)]
    else:
        lines.append("- none")
    lines += ["", f"Answer with JSON only: {{\"ranking\": [up to "
                  f"{config.max_ranking} receptacle names, most likely "
                  f"first], \"p_top\": number}}. Names must come from the "
                  f"list above or be {OUT_OF_HOUSE} or {ON_PERSON}."]
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(lines)}]


def cache_key(episode_id: str, object_id: str,
              last_sighting: Optional[Tuple[int, str]],
              newest_exclusion: Optional[Tuple[int, str]], t: int,
              config: LLMBeliefConfig) -> str:
    """(episode, object, last sighting, newest exclusion, hour bucket)."""
    ls = "none" if last_sighting is None else f"{last_sighting[0]}@{last_sighting[1]}"
    ne = ("none" if newest_exclusion is None
          else f"{newest_exclusion[0]}@{newest_exclusion[1]}")
    return f"{episode_id}|{object_id}|{ls}|{ne}|{t // config.hour_bucket_s}"


# ---------------------------------------------------------------- output --

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def parse_completion(text: Optional[str], allowed: Sequence[str],
                     max_ranking: int
                     ) -> Tuple[Optional[List[str]], Optional[float], str]:
    """(ranking, p_top, status). ``status`` is ``ok`` or the failure
    kind: ``no_json``, ``bad_shape``, ``empty``, ``off_list``. Duplicate
    names are dropped, keeping the first; the ranking is cut to
    ``max_ranking``."""
    if not text:
        return None, None, "no_json"
    try:
        obj = json.loads(text)
    except ValueError:
        m = _JSON_BLOCK.search(text)
        if not m:
            return None, None, "no_json"
        try:
            obj = json.loads(m.group(0))
        except ValueError:
            return None, None, "no_json"
    if not isinstance(obj, dict) or not isinstance(obj.get("ranking"), list):
        return None, None, "bad_shape"
    p_top = obj.get("p_top")
    p_top = float(p_top) if isinstance(p_top, (int, float)) else None
    names: List[str] = []
    for name in obj["ranking"]:
        if not isinstance(name, str):
            return None, p_top, "bad_shape"
        name = name.strip().rstrip("*")
        if name not in names:
            names.append(name)
    if not names:
        return None, p_top, "empty"
    allowed_set = set(allowed)
    if any(name not in allowed_set for name in names):
        return None, p_top, "off_list"
    return names[:max_ranking], p_top, "ok"


def ranking_distribution(ranking: Sequence[str],
                         ratio: float) -> Dict[str, float]:
    """Geometric weights ratio, ratio^2, ... over the ranked names,
    renormalized."""
    weights = [ratio ** (i + 1) for i in range(len(ranking))]
    total = sum(weights)
    return {name: w / total for name, w in zip(ranking, weights)}


# ---------------------------------------------------------------- cache --

class PromptCache:
    """Prompt key -> completion text, with a collect mode.

    ``answers`` maps key -> completion text (None for keys the generator
    did not answer). In collect mode :meth:`lookup` records every prompt
    it is asked for in ``prompts`` (key -> messages) and returns None.
    """

    def __init__(self, answers: Optional[Mapping[str, Optional[str]]] = None,
                 collect: bool = False) -> None:
        self.answers: Dict[str, Optional[str]] = dict(answers or {})
        self.collect = collect
        self.prompts: Dict[str, List[Dict[str, str]]] = {}

    def lookup(self, key: str, messages: List[Dict[str, str]]
               ) -> Optional[str]:
        if self.collect:
            self.prompts.setdefault(key, messages)
        return self.answers.get(key)


# ---------------------------------------------------------------- model --

class LLMBelief(BeliefModel):
    """Where the object is, according to a language model shown its
    evidence. See the module docstring."""

    def __init__(self, rng: random.Random, config: LLMBeliefConfig,
                 cache: PromptCache,
                 rooms: Optional[Mapping[str, str]] = None) -> None:
        super().__init__(rng)
        self.config = config
        self.cache = cache
        self.rooms = dict(rooms) if rooms else None
        self.counts: Dict[str, int] = {}
        self._last: Optional[Dict[str, float]] = None
        self.last_key: Optional[str] = None
        self.last_messages: Optional[List[Dict[str, str]]] = None

    @property
    def name(self) -> str:
        return "LLMBelief"

    def last_prediction_diagnostics(self) -> Optional[Dict[str, float]]:
        return self._last

    def _apply_exclusions(self, object_id: str, t: int,
                          base: Prediction) -> Prediction:
        # Negative evidence is in the prompt; the LLM's answer stands.
        return base

    def _count(self, what: str) -> None:
        self.counts[what] = self.counts.get(what, 0) + 1

    def _fallback(self, object_id: str, history: List[Tuple[int, str]],
                  t: int) -> Prediction:
        """The LastObs answer: one-hot last sighting, base exclusions."""
        last = history[-1][1]
        base = Prediction(distribution={last: 1.0}, argmax=last)
        return BeliefModel._apply_exclusions(self, object_id, t, base)

    def _predict_for_object(self, object_id: str,
                            history: List[Tuple[int, str]],
                            t: int) -> Prediction:
        if not history:
            self._last = None
            return self._uniform()
        assert self._context is not None
        recs = self._context.receptacle_ids
        newest_positive = max(ot for ot, _ in history)
        exclusions = sorted(
            (t_ex, rec) for rec, t_ex in
            self._exclusions.get(object_id, {}).items()
            if t_ex >= newest_positive)
        newest_exclusion = exclusions[-1] if exclusions else None
        key = cache_key(self._context.episode_id, object_id, history[-1],
                        newest_exclusion, t, self.config)
        messages = build_messages(
            t=t, object_id=object_id,
            object_class=self._context.object_classes[object_id],
            receptacle_ids=recs, history=history, exclusions=exclusions,
            config=self.config, rooms=self.rooms)
        self.last_key, self.last_messages = key, messages
        text = self.cache.lookup(key, messages)
        self._count("predictions")
        if text is None:
            self._count("pending")
            self._last = {"p_top": float("nan"), "fallback": 1.0,
                          "pending": 1.0, "n_ranked": 0.0}
            return self._fallback(object_id, history, t)
        ranking, p_top, status = parse_completion(
            text, recs, self.config.max_ranking)
        if ranking is None:
            self._count("fallback")
            self._count(f"fallback_{status}")
            self._last = {"p_top": float("nan") if p_top is None else p_top,
                          "fallback": 1.0, "pending": 0.0, "n_ranked": 0.0}
            return self._fallback(object_id, history, t)
        self._count("answered")
        self._last = {"p_top": float("nan") if p_top is None else p_top,
                      "fallback": 0.0, "pending": 0.0,
                      "n_ranked": float(len(ranking))}
        dist = ranking_distribution(ranking, self.config.geometric_ratio)
        return Prediction(distribution=dist, argmax=ranking[0])
