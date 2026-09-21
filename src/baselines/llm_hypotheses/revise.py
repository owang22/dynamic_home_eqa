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
                                             extract_json, output_budget,
                                             repair_prompt, salvage_prompt,
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
        self._tables = ""          # built per call from the known objects
        self._seen_classes: Dict[str, str] = {}
        if anonymized:
            self._seen_receptacles = tuple(self._rmap[r]
                                           for r in episode.receptacle_ids)
        else:
            self._seen_receptacles = tuple(episode.receptacle_ids)

    def _set_vocabulary(self, known: Mapping[str, str]) -> None:
        """Per call: the tables and the validation vocabulary are the
        objects the mixture has been shown so far, in the vocabulary the
        model speaks. Never the bank's inventory."""
        self._known = dict(known)
        if self._anonymized:
            self._seen_classes = {self._omap[o]: self._cmap[c]
                                  for o, c in known.items()}
        else:
            self._seen_classes = dict(known)
        self._tables = vocabulary_tables(self._episode, self._omap, self._rmap,
                                         self._cmap, objects=known)

    def __call__(self, report: Mapping[str, Any], previous: List[dict],
                 context) -> List[dict]:
        index = len(self.calls) + 1
        self._set_vocabulary(report.get("known_objects")
                             or self._episode.object_classes)
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
                translated, self._known, self._episode.receptacle_ids)
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


# ================================================================== graph

from baselines.llm_hypotheses.assumption_graph import (  # noqa: E402
    ALL_OPS, AWAY_TOKENS, DIVERSIFY_OPS, REPAIR_OPS, AssumptionGraph,
    OperationResult, apply_operations)
from baselines.llm_hypotheses.prompt import (  # noqa: E402
    OPERATIONS_SCHEMA, anonymize_graph, deanonymize_operations,
    graph_repair_prompt, graph_revision_prompt)


class GraphRevisionElicitor(RevisionElicitor):
    """``(report, graph, context) -> OperationResult`` for the graph arm.

    Same call discipline as the flat elicitor (one cached thinking call,
    grammar salvage, one repair round, full log), but the model returns
    OPERATIONS which are applied with :func:`~baselines.llm_hypotheses.
    assumption_graph.apply_operations` in real-id space. Leaves the model
    does not mention stay byte-identical. If the applied set fails
    whole-graph validation the repair prompt runs once with the exact
    problems; if that fails too, the result carries ``graph=None`` and
    the mixture logs ``changed: False``.

    The report must carry ``leaf_weights`` (real leaf ids -> mixture
    weight) — the birth rule reads them.
    """

    def __call__(self, report: Mapping[str, Any],  # type: ignore[override]
                 graph: AssumptionGraph, context) -> OperationResult:
        index = len(self.calls) + 1
        self._set_vocabulary(report.get("known_objects")
                             or self._episode.object_classes)
        shown = graph.to_json()
        if self._anonymized:
            shown = anonymize_graph(shown, self._omap, self._rmap, self._cmap)
        graph_json = json.dumps(shown, indent=1)
        call_type = report.get("call_type") if self.call_types else None
        user = graph_revision_prompt(report, self._tables, graph_json,
                                     self._omap, self._rmap,
                                     call_type=call_type)
        log: Dict[str, Any] = {"household": self._episode.household_id,
                               "anonymized": self._anonymized, "graph": True,
                               "call_index": index, "day": report["day"],
                               "trigger": report.get("trigger"),
                               "call_type": call_type,
                               "settled": dict(report.get("settled", {})),
                               "prompt": user, "rounds": []}
        seed = self._seed + 10 * index
        started = time.monotonic()
        row = self._client.generate(SYSTEM_PROMPT, user, seed=seed,
                                    temperature=self._temperature,
                                    max_tokens=self._max_tokens,
                                    reasoning_effort=self._effort)
        payload, think = row["payload"], row["think"]
        operations: List[dict] = []
        try:
            operations = list(extract_json(payload).get("operations", []))
            log["rounds"].append({"kind": "revision", "think": think,
                                  "payload": payload,
                                  "n_operations": len(operations),
                                  **_stats(row)})
        except json.JSONDecodeError as err:
            log["rounds"].append({"kind": "shape_failure", "error": str(err),
                                  "payload": payload, "think": think,
                                  **_stats(row)})
            raw = self._client.generate(
                SYSTEM_PROMPT, salvage_prompt(user, payload), seed=seed + 1,
                temperature=self._temperature, max_tokens=self._max_tokens,
                schema=OPERATIONS_SCHEMA)
            try:
                operations = list(extract_json(raw["payload"]).get(
                    "operations", []))
                payload = raw["payload"]
                log["rounds"].append({"kind": "salvage",
                                      "payload": raw["payload"],
                                      "n_operations": len(operations),
                                      **_stats(raw)})
            except json.JSONDecodeError as err2:
                log["rounds"].append({"kind": "salvage_failed",
                                      "error": str(err2), **_stats(raw)})
        result = self._apply(graph, operations, report, context)
        if result.graph is None and operations:
            user2 = graph_repair_prompt(result.problems, self._tables,
                                        payload, kind="operations")
            raw2 = self._client.generate(
                SYSTEM_PROMPT, user2, seed=seed + 2,
                temperature=self._temperature, max_tokens=self._max_tokens,
                reasoning_effort=self._effort)
            entry: Dict[str, Any] = {"kind": "repair", "prompt": user2,
                                     "think": raw2["think"],
                                     "payload": raw2["payload"],
                                     "problems_before": list(result.problems),
                                     **_stats(raw2)}
            try:
                operations2 = list(extract_json(raw2["payload"]).get(
                    "operations", []))
                result2 = self._apply(graph, operations2, report, context)
                entry["problems_after"] = list(result2.problems)
                result = result2
            except json.JSONDecodeError as err:
                entry["error"] = str(err)
            log["rounds"].append(entry)
        log["operations"] = list(result.operations)
        log["applied"] = list(result.applied)
        log["rejected"] = list(result.rejected)
        log["births"] = list(result.births)
        log["skipped_births"] = list(result.skipped_births)
        log["problems"] = list(result.problems)
        log["generation_seconds"] = round(time.monotonic() - started, 2)
        log["outcome"] = "revised" if result.graph is not None else "kept_previous"
        log["n_valid"] = len(result.graph.leaves) if result.graph else None
        self.calls.append({k: log[k] for k in ("call_index", "day", "n_valid",
                                               "generation_seconds", "outcome")})
        (self._log_dir / f"{self._episode.household_id}_revision_"
                         f"{index}.json").write_text(json.dumps(log, indent=1))
        return result

    call_types: bool = True
    """Honour the report's ``call_type`` (repair / diversify) by limiting
    the allowed operations and switching the prompt lead. False runs the
    phase-1 protocol: one call type, every operation but deletion."""

    def _apply(self, graph: AssumptionGraph, operations: List[dict],
               report: Mapping[str, Any], context) -> OperationResult:
        real_ops = (deanonymize_operations(operations, self._omap, self._rmap,
                                           self._cmap)
                    if self._anonymized else [dict(op) for op in operations])
        object_classes = dict(report.get("known_objects") or self._known)
        call_type = report.get("call_type") if self.call_types else None
        allowed = (REPAIR_OPS if call_type == "repair" else
                   DIVERSIFY_OPS if call_type == "diversify" else ALL_OPS)
        result = apply_operations(graph, real_ops,
                                  dict(report.get("leaf_weights", {})),
                                  object_classes, self._episode.receptacle_ids,
                                  allowed_ops=allowed,
                                  settled=report.get("settled"),
                                  unsensable=AWAY_TOKENS)
        result.operations = real_ops
        return result


# =================================================================== tree

from baselines.llm_hypotheses.hypothesis_tree import (  # noqa: E402
    HypothesisTree, TreeOperationResult)
from baselines.llm_hypotheses.hypothesis_tree import (  # noqa: E402
    apply_operations as apply_tree_operations)
from baselines.llm_hypotheses.tree_prompt import (  # noqa: E402
    TREE_OPERATIONS_SCHEMA, anonymize_tree, deanonymize_tree_operations,
    tree_repair_prompt, tree_revision_prompt)


class TreeRevisionElicitor(RevisionElicitor):
    """``(report, tree, context) -> TreeOperationResult`` for the tree
    arm: one cached thinking call, grammar salvage when no JSON arrived,
    the operations applied in real-id space
    (:func:`~baselines.llm_hypotheses.hypothesis_tree.apply_operations`
    — add_child / add_root only, rejected whole otherwise), one repair
    round naming the exact problems, full log. One call type: the
    report's trigger is shown, the operations are the same."""

    def __call__(self, report: Mapping[str, Any],  # type: ignore[override]
                 tree: HypothesisTree, context) -> TreeOperationResult:
        index = len(self.calls) + 1
        self._set_vocabulary(report.get("known_objects")
                             or self._episode.object_classes)
        shown = tree.to_json()
        if self._anonymized:
            shown = anonymize_tree(shown, self._omap, self._rmap, self._cmap)
        tree_json = json.dumps(shown, indent=1)
        user = tree_revision_prompt(report, self._tables, tree_json,
                                    self._omap, self._rmap)
        log: Dict[str, Any] = {"household": self._episode.household_id,
                               "anonymized": self._anonymized, "tree": True,
                               "call_index": index, "day": report["day"],
                               "trigger": report.get("trigger"),
                               "settled_labels": dict(
                                   report.get("settled_labels", {})),
                               "prompt": user, "rounds": []}
        seed = self._seed + 10 * index
        started = time.monotonic()
        row = self._client.generate(SYSTEM_PROMPT, user, seed=seed,
                                    temperature=self._temperature,
                                    max_tokens=self._max_tokens,
                                    reasoning_effort=self._effort)
        payload, think = row["payload"], row["think"]
        operations: List[dict] = []
        try:
            operations = list(extract_json(payload).get("operations", []))
            log["rounds"].append({"kind": "revision", "think": think,
                                  "payload": payload,
                                  "n_operations": len(operations),
                                  **_stats(row)})
        except json.JSONDecodeError as err:
            log["rounds"].append({"kind": "shape_failure", "error": str(err),
                                  "payload": payload, "think": think,
                                  **_stats(row)})
            # The model fixes its own reply first (thinking on, the exact
            # parser message); the grammar salvage is the last resort.
            user_fix = tree_repair_prompt(
                [f"the JSON at the end of your reply failed to parse: {err}"],
                self._tables, payload, kind="operations")
            raw = self._client.generate(
                SYSTEM_PROMPT, user_fix, seed=seed + 1,
                temperature=self._temperature, max_tokens=self._max_tokens,
                reasoning_effort=self._effort)
            try:
                operations = list(extract_json(raw["payload"]).get(
                    "operations", []))
                payload = raw["payload"]
                log["rounds"].append({"kind": "self_repair", "prompt": user_fix,
                                      "think": raw["think"],
                                      "payload": raw["payload"],
                                      "n_operations": len(operations),
                                      **_stats(raw)})
            except json.JSONDecodeError as err2:
                log["rounds"].append({"kind": "self_repair_failed",
                                      "error": str(err2), "think": raw["think"],
                                      "payload": raw["payload"], **_stats(raw)})
                raw = self._client.generate(
                    SYSTEM_PROMPT, salvage_prompt(user, payload), seed=seed + 3,
                    temperature=self._temperature, max_tokens=self._max_tokens,
                    schema=TREE_OPERATIONS_SCHEMA)
                try:
                    operations = list(extract_json(raw["payload"]).get(
                        "operations", []))
                    payload = raw["payload"]
                    log["rounds"].append({"kind": "salvage",
                                          "payload": raw["payload"],
                                          "n_operations": len(operations),
                                          **_stats(raw)})
                except json.JSONDecodeError as err3:
                    log["rounds"].append({"kind": "salvage_failed",
                                          "error": str(err3), **_stats(raw)})
        result = self._apply_tree(tree, operations, report)
        if result.tree is None and operations:
            user2 = tree_repair_prompt(result.problems, self._tables, payload,
                                       kind="operations")
            raw2 = self._client.generate(
                SYSTEM_PROMPT, user2, seed=seed + 2,
                temperature=self._temperature, max_tokens=self._max_tokens,
                reasoning_effort=self._effort)
            entry: Dict[str, Any] = {"kind": "repair", "prompt": user2,
                                     "think": raw2["think"],
                                     "payload": raw2["payload"],
                                     "problems_before": list(result.problems),
                                     **_stats(raw2)}
            try:
                operations2 = list(extract_json(raw2["payload"]).get(
                    "operations", []))
                result2 = self._apply_tree(tree, operations2, report)
                entry["problems_after"] = list(result2.problems)
                # Keep the first round's rejections in the log too.
                result2.rejected = list(result.rejected) + list(result2.rejected)
                result = result2
            except json.JSONDecodeError as err:
                entry["error"] = str(err)
            log["rounds"].append(entry)
        log["operations"] = list(result.operations)
        log["applied"] = list(result.applied)
        log["rejected"] = list(result.rejected)
        log["problems"] = list(result.problems)
        log["generation_seconds"] = round(time.monotonic() - started, 2)
        log["outcome"] = "revised" if result.tree is not None else "kept_previous"
        log["n_valid"] = len(result.tree.nodes) if result.tree else None
        self.calls.append({k: log[k] for k in ("call_index", "day", "n_valid",
                                               "generation_seconds", "outcome")})
        (self._log_dir / f"{self._episode.household_id}_revision_"
                         f"{index}.json").write_text(json.dumps(log, indent=1))
        return result

    def _apply_tree(self, tree: HypothesisTree, operations: List[dict],
                    report: Mapping[str, Any]) -> TreeOperationResult:
        real_ops = (deanonymize_tree_operations(operations, self._omap,
                                                self._rmap, self._cmap)
                    if self._anonymized else [dict(op) for op in operations])
        object_classes = dict(report.get("known_objects") or self._known)
        result = apply_tree_operations(tree, real_ops, object_classes,
                                       self._episode.receptacle_ids,
                                       unsensable=AWAY_TOKENS)
        result.operations = real_ops
        return result


# =============================================================== longleaf

from baselines.llm_hypotheses.longleaf import (  # noqa: E402
    MAX_LIBRARY, accept_literal_away_tokens, anonymize_document,
    deanonymize_document, parse_documents, read_ids, revive_ids)
from baselines.llm_hypotheses import protocol_text as _PT
from baselines.llm_hypotheses.longleaf_prompt import (  # noqa: E402
    longleaf_repair_prompt, longleaf_revision_prompt)


class LongLeafRevisionElicitor(RevisionElicitor):
    """``(report, live_raws, context) -> {"new": [raw...], "revive":
    [ids], "dropped": [...], "problems": [...]}``. One thinking call; the
    documents are parsed in the vocabulary the model saw; one repair
    round reprints only the failed ones; anonymized documents are
    translated to real ids in their structured fields (prose stays as
    written). Never a replacement set: only additions and revivals."""

    def __call__(self, report: Mapping[str, Any],  # type: ignore[override]
                 previous: List[dict], context) -> Dict[str, Any]:
        index = len(self.calls) + 1
        self._set_vocabulary(report.get("known_objects")
                             or self._episode.object_classes)
        proto = getattr(self._episode, "protocol", None)
        notes = _PT.household_notes(proto, int(report["day"]))
        asked = _PT.questions_sentence(proto)
        if asked:
            notes = (notes + "\n\n" if notes else "") + asked
        user = longleaf_revision_prompt(report, self._tables, self._omap,
                                        self._rmap, notes=notes)
        log: Dict[str, Any] = {"household": self._episode.household_id,
                               "anonymized": self._anonymized,
                               "longleaf": True, "call_index": index,
                               "day": report["day"],
                               "trigger": report.get("trigger"),
                               "prompt": user, "rounds": []}
        seed = self._seed + 10 * index
        started = time.monotonic()
        budget = output_budget(user, self._max_tokens, SYSTEM_PROMPT)
        log_budget = budget
        row = self._client.generate(SYSTEM_PROMPT, user, seed=seed,
                                    temperature=self._temperature,
                                    max_tokens=budget,
                                    reasoning_effort=self._effort,
                                    keep_content=True)
        payload, think = row.get("content", row["payload"]), row["think"]
        if self._anonymized:
            payload = accept_literal_away_tokens(payload, self._rmap)
        taken = [str(r.get("hypothesis_id")) for r in previous] + [
            d["hypothesis_id"] for d in report.get("library", [])]
        seen_away = (tuple(self._rmap[r] for r in AWAY_TOKENS if r in self._rmap)
                     if self._anonymized else AWAY_TOKENS)
        # Parents for forks, in the vocabulary the model writes in.
        parents = {d["hypothesis_id"]: (anonymize_document(d, self._omap, self._rmap, self._cmap)
                                        if self._anonymized else d)
                   for d in report.get("library_raws", [])}
        valid, dropped = parse_documents(payload, self._seen_classes,
                                         self._seen_receptacles, taken=taken,
                                         unsensable=seen_away, parents=parents)
        wanted = read_ids(payload)
        log["rounds"].append({"kind": "revision" if valid else "read_request",
                              "think": think, "payload": payload,
                              "n_valid": len(valid), "n_dropped": len(dropped),
                              "read": wanted, **_stats(row)})
        if not valid and wanted:
            # Phase two: the same prompt with the requested documents.
            by_id = {d["hypothesis_id"]: d for d in report.get("library", [])}
            fetched = [by_id[i] for i in wanted if i in by_id]
            user2 = longleaf_revision_prompt(report, self._tables, self._omap,
                                             self._rmap, fetched=fetched, notes=notes)
            budget2 = output_budget(user2, self._max_tokens, SYSTEM_PROMPT)
            row2 = self._client.generate(SYSTEM_PROMPT, user2, seed=seed + 1,
                                         temperature=self._temperature,
                                         max_tokens=budget2,
                                         reasoning_effort=self._effort,
                                         keep_content=True)
            payload, think = row2.get("content", row2["payload"]), row2["think"]
            if self._anonymized:
                payload = accept_literal_away_tokens(payload, self._rmap)
            valid, dropped = parse_documents(payload, self._seen_classes,
                                             self._seen_receptacles, taken=taken,
                                             unsensable=seen_away, parents=parents)
            log["rounds"].append({"kind": "revision", "prompt": user2,
                                  "fetched": [d["hypothesis_id"] for d in fetched],
                                  "think": think, "payload": payload,
                                  "n_valid": len(valid), "n_dropped": len(dropped),
                                  **_stats(row2)})
        if dropped:
            log["dropped_before_repair"] = list(dropped)
            problems = [f"document {d['index']}: {d['error']}" for d in dropped]
            user2 = longleaf_repair_prompt(
                problems, self._tables,
                "\n\n".join(d["document"] for d in dropped))
            raw2 = self._client.generate(
                SYSTEM_PROMPT, user2, seed=seed + 2,
                temperature=self._temperature,
                max_tokens=output_budget(user2, self._max_tokens, SYSTEM_PROMPT),
                reasoning_effort=self._effort, keep_content=True)
            text2 = raw2.get("content", raw2["payload"])
            if self._anonymized:
                text2 = accept_literal_away_tokens(text2, self._rmap)
            fixed, still = parse_documents(
                text2, self._seen_classes, self._seen_receptacles,
                taken=taken + [v["hypothesis_id"] for v in valid],
                unsensable=seen_away, parents=parents)
            log["rounds"].append({"kind": "repair", "prompt": user2,
                                  "think": raw2["think"],
                                  "payload": raw2.get("content", raw2["payload"]),
                                  "n_valid": len(fixed), "n_dropped": len(still),
                                  **_stats(raw2)})
            valid += fixed
            dropped = still
        if self._anonymized:
            translated = [deanonymize_document(v, self._omap, self._rmap,
                                               self._cmap) for v in valid]
            real_valid = []
            for raw in translated:
                try:
                    from baselines.beliefs.timetable_hypothesis import parse_timetable
                    parse_timetable(raw, self._known, self._episode.receptacle_ids,
                                    unsensable=AWAY_TOKENS)
                    real_valid.append(raw)
                except Exception as err:      # noqa: BLE001 - logged, never guessed
                    dropped.append({"index": -1, "error": f"real-id check: {err}",
                                    "bad_strings": [], "document": raw.get("markdown", "")[:2000]})
            valid = real_valid
        revive = revive_ids(payload)
        problems: List[str] = []
        live = sum(1 for d in report.get("library", []) if d.get("status") == "live")
        room = max(0, MAX_LIBRARY - live - len(revive))
        if len(valid) > room:
            problems.append(f"{live} live documents plus {len(revive)} revived: "
                            f"room for {room} of the {len(valid)} written; the "
                            f"rest are logged and left out")
            log["left_out"] = [v["hypothesis_id"] for v in valid[room:]]
            valid = valid[:room]
        log.update({"n_valid": len(valid), "dropped": dropped,
                    "revive": revive, "problems": problems,
                    "output_budget": log_budget,
                    "generation_seconds": round(time.monotonic() - started, 2),
                    "outcome": "revised" if (valid or revive) else "kept_previous"})
        self.calls.append({k: log[k] for k in ("call_index", "day", "n_valid",
                                               "generation_seconds", "outcome")})
        (self._log_dir / f"{self._episode.household_id}_revision_"
                         f"{index}.json").write_text(json.dumps(log, indent=1))
        return {"new": valid, "revive": revive, "dropped": dropped,
                "problems": problems}
