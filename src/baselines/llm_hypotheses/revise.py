"""The revision elicitor: the LLM call behind the mixture's re-asking.

:class:`RevisionElicitor` is the ``elicitor`` callable an
:class:`~baselines.beliefs.llm_hypothesis_mixture.LLMHypothesisMixture`
invokes when its trigger fires. It turns the belief's revision report
into the revision prompt (:func:`~baselines.llm_hypotheses.prompt.
revision_prompt`), makes one cached thinking call, validates strictly
in the vocabulary the model saw, repairs once on invalid ids, salvages
through guided JSON when no object arrived, translates back to real ids
in the anonymized condition, and writes a full log of the exchange.

Failure is never silent and never fuzzy: a call that yields nothing
usable returns the previous hypotheses unchanged (the mixture records
``changed: False``), and every dropped hypothesis is logged with the
exact offending strings.

The call happens mid-episode, inside the belief's ``update``. Because
every call is cached by request hash, a rerun of the same episode is
byte-identical and free; the log records live calls and timing.
"""

from __future__ import annotations

import json
import pathlib
import time
from typing import Any, Dict, List, Mapping, Optional

from baselines.llm_hypotheses.elicit import (DEFAULT_MAX_TOKENS,
                                             DEFAULT_REASONING_EFFORT,
                                             DEFAULT_TEMPERATURE,
                                             CachedThinkingClient,
                                             extract_json, repair_prompt,
                                             salvage_prompt,
                                             validate_hypotheses)
from baselines.llm_hypotheses.prompt import (HYPOTHESES_SCHEMA,
                                             SYSTEM_PROMPT,
                                             anonymize_hypothesis,
                                             build_anonymization_maps,
                                             deanonymize_hypothesis,
                                             revision_prompt,
                                             vocabulary_tables)


class RevisionElicitor:
    """``(report, previous_hypotheses, context) -> revised hypotheses``.

    ``episode`` supplies the vocabulary tables and, for the anonymized
    condition, the token maps; ``log_dir`` receives one JSON per call.
    ``llm_seed`` is offset by the call index so two revisions in one
    episode never share a cache key by accident.
    """

    def __init__(self, client: CachedThinkingClient, episode,
                 anonymized: bool, log_dir: pathlib.Path,
                 temperature: float = DEFAULT_TEMPERATURE,
                 max_tokens: int = DEFAULT_MAX_TOKENS,
                 reasoning_effort: str = DEFAULT_REASONING_EFFORT,
                 llm_seed: int = 101) -> None:
        self._client = client
        self._episode = episode
        self._anonymized = anonymized
        self._log_dir = pathlib.Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._effort = reasoning_effort
        self._seed = llm_seed
        self.calls: List[Dict[str, Any]] = []
        if anonymized:
            self._omap, self._rmap, self._cmap = build_anonymization_maps(
                episode)
        else:
            self._omap, self._rmap, self._cmap = {}, {}, {}
        self._tables = vocabulary_tables(episode, self._omap, self._rmap,
                                         self._cmap)
        if anonymized:
            self._seen_classes = {self._omap[o]: self._cmap[c]
                                  for o, c in episode.object_classes.items()}
            self._seen_receptacles = tuple(self._rmap[r]
                                           for r in episode.receptacle_ids)
        else:
            self._seen_classes = dict(episode.object_classes)
            self._seen_receptacles = tuple(episode.receptacle_ids)

    def __call__(self, report: Mapping[str, Any], previous: List[dict],
                 context) -> List[dict]:
        index = len(self.calls) + 1
        shown = ([anonymize_hypothesis(h, self._omap, self._rmap, self._cmap)
                  for h in previous] if self._anonymized else previous)
        previous_json = json.dumps({"hypotheses": shown}, indent=1)
        user = revision_prompt(report, self._tables, previous_json,
                               self._omap, self._rmap)
        log: Dict[str, Any] = {"household": self._episode.household_id,
                               "anonymized": self._anonymized,
                               "call_index": index, "day": report["day"],
                               "prompt": user, "rounds": []}
        seed = self._seed + 10 * index
        started = time.monotonic()
        row = self._client.generate(SYSTEM_PROMPT, user, seed=seed,
                                    temperature=self._temperature,
                                    max_tokens=self._max_tokens,
                                    reasoning_effort=self._effort)
        payload, think = row["payload"], row["think"]
        hypotheses: List[dict] = []
        try:
            hypotheses = list(extract_json(payload).get("hypotheses", []))
            log["rounds"].append({"kind": "revision", "think": think,
                                  "payload": payload,
                                  "n_hypotheses": len(hypotheses),
                                  **_stats(row)})
        except json.JSONDecodeError as err:
            log["rounds"].append({"kind": "shape_failure", "error": str(err),
                                  "payload": payload, "think": think,
                                  **_stats(row)})
            raw = self._client.generate(
                SYSTEM_PROMPT, salvage_prompt(user, payload), seed=seed + 1,
                temperature=self._temperature, max_tokens=self._max_tokens,
                schema=HYPOTHESES_SCHEMA)
            try:
                hypotheses = list(extract_json(raw["payload"]).get(
                    "hypotheses", []))
                log["rounds"].append({"kind": "salvage",
                                      "payload": raw["payload"],
                                      "n_hypotheses": len(hypotheses),
                                      **_stats(raw)})
            except json.JSONDecodeError as err2:
                log["rounds"].append({"kind": "salvage_failed",
                                      "error": str(err2), **_stats(raw)})
        valid, failed = validate_hypotheses(hypotheses, self._seen_classes,
                                            self._seen_receptacles)
        if failed:
            user2 = repair_prompt(failed, self._tables, payload)
            raw2 = self._client.generate(
                SYSTEM_PROMPT, user2, seed=seed + 2,
                temperature=self._temperature, max_tokens=self._max_tokens,
                reasoning_effort=self._effort)
            entry: Dict[str, Any] = {"kind": "repair", "prompt": user2,
                                     "think": raw2["think"],
                                     "payload": raw2["payload"],
                                     **_stats(raw2)}
            try:
                reparsed = list(extract_json(raw2["payload"]).get(
                    "hypotheses", []))
                valid, failed = validate_hypotheses(
                    reparsed, self._seen_classes, self._seen_receptacles)
                entry["n_valid"] = len(valid)
            except json.JSONDecodeError as err:
                entry["error"] = str(err)
            log["rounds"].append(entry)
        if self._anonymized:
            translated = [deanonymize_hypothesis(h, self._omap, self._rmap,
                                                 self._cmap) for h in valid]
            valid, real_failed = validate_hypotheses(
                translated, self._episode.object_classes,
                self._episode.receptacle_ids)
            failed = failed + real_failed
        log["dropped"] = failed
        log["generation_seconds"] = round(time.monotonic() - started, 2)
        log["n_valid"] = len(valid)
        log["outcome"] = "revised" if valid else "kept_previous"
        self.calls.append({k: log[k] for k in ("call_index", "day", "n_valid",
                                               "generation_seconds", "outcome")})
        (self._log_dir / f"{self._episode.household_id}_revision_"
                         f"{index}.json").write_text(json.dumps(log, indent=1))
        return valid if valid else list(previous)


def _stats(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {"generation_seconds": row.get("generation_seconds"),
            "completion_tokens": row.get("completion_tokens"),
            "prompt_tokens": row.get("prompt_tokens"),
            "finish_reason": row.get("finish_reason"),
            "think_closed": row.get("think_closed"),
            "cached": row.get("cached")}
