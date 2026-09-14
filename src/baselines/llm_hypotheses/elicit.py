"""Elicit household hypotheses from a served LLM, validate strictly,
repair once, write per-household hypothesis files.

One thinking-mode call per (household, condition) produces all
hypotheses together — reasoning first, one JSON object last (guided
JSON is measured to suppress the think block on this stack, so schema
conformance is enforced caller-side instead: strict ID validation with
exact-string error reporting and ONE repair round; a hypothesis that
fails twice is dropped and logged, never fuzzily fixed).

The two conditions are ``named`` (real ids) and ``anonymized`` (every
object, class, and receptacle replaced by a neutral numbered token —
``object_1``, ``receptacle_1`` — with the mapping written out as a
cross-reference table). Hypotheses elicited under anonymization are
translated back to real ids before anything downstream sees them, so
both conditions produce identical-format files.

Calls are disk-cached by request hash (the ``llm_prior_cache``
discipline), so reruns are free and byte-identical; the summary prints
real calls next to cache hits and reports generation time per call and
per hypothesis, because the report must state call counts and cost next
to accuracy.

Outputs under ``--out-dir`` (default ``results/llm_hypotheses``):

* ``hypotheses/<condition>/<household>.json`` — what the belief loads
  (:class:`~baselines.beliefs.llm_hypothesis_mixture.LLMHypothesisMixture`);
  real IDs in both conditions.
* ``logs/<condition>/<household>.json`` — prompt, think trace, raw
  payload, repair round, dropped hypotheses, per-call token usage and
  generation seconds: what the LLM wrote, kept separate from what the
  converter later fits.
* ``anonymization/<household>.md`` / ``.json`` — the cross-reference
  table for the anonymized condition.
* ``generation_cost.json`` — per (household, condition) generation
  seconds, tokens, and seconds per hypothesis.

Usage:
  python -m baselines.llm_hypotheses.elicit --households hh_001 hh_002 \
      --endpoint http://127.0.0.1:8300 --model Qwen/Qwen3.8-27B
  python -m baselines.llm_hypotheses.elicit --households hh_001 --graph \
      --conditions named            # graph arm: hypotheses/graph_named/

``--graph`` elicits the assumption-graph envelope from the tour
(:func:`elicit_graph_household`) — assumptions with named values and
one leaf per tested combination — validated by
:func:`~baselines.llm_hypotheses.assumption_graph.parse_graph`; the
flat tour-start path is unchanged and the two are compared on the same
episodes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import time
from typing import Any, Dict, List, Mapping, Optional, Tuple

import requests

from baselines.bank import JsonlBank
from baselines.beliefs.hypothesis_program import (HypothesisValidationError,
                                                  parse_hypothesis)
from baselines.household_analysis import REPO_ROOT, bank_path
from baselines.llm_hypotheses.assumption_graph import (parse_graph,
                                                       truncate_to_caps)
from baselines.llm_hypotheses.prompt import (GRAPH_SCHEMA, HYPOTHESES_SCHEMA,
                                             N_HYPOTHESES, SYSTEM_PROMPT,
                                             crossref_table,
                                             deanonymize_graph,
                                             deanonymize_hypothesis,
                                             elicitation_prompt,
                                             graph_repair_prompt,
                                             graph_tour_start_prompt,
                                             tour_start_prompt,
                                             vocabulary_tables)

DEFAULT_OUT_DIR = REPO_ROOT / "results" / "llm_hypotheses"
DEFAULT_WARMUP_DAYS = 7
DEFAULT_MAX_TOKENS = 40000
"""Output budget per call. This task needs a big one and the budget is
what actually governs success; measured on hh_001, both failure modes
were budget exhaustion:

* 16384 at the template's default ``xhigh`` effort: the ``<think>``
  block never closed (40-58k chars of reasoning, no ``</think>``, no
  JSON) — 4 calls, 0 usable hypotheses;
* 24000 at ``medium`` and ``low``: thinking closed (~53k chars either
  way) but the JSON that followed was truncated mid-object.

A full 5-hypothesis answer covering every object costs roughly 6k
output tokens on top of ~18k of reasoning, so 40000 leaves real
headroom. Requires the server's ``--max-model-len`` to exceed this plus
the ~3.5k prompt: this run serves at 65536 (the model supports
262144)."""

DEFAULT_REASONING_EFFORT = "medium"
"""``reasoning_effort`` passed through Qwen3.8's chat template
(``xhigh`` is the template's own default).

Measured, this knob barely moves reasoning LENGTH on this task: medium
and low produced 73.9k and 77.2k characters of output respectively —
low was marginally longer. It is kept at medium because the template's
xhigh instruction ("consider plausible alternatives") is aimed at
single-answer correctness while this prompt wants five DIFFERING
answers, but the honest note is that :data:`DEFAULT_MAX_TOKENS`, not
this, is what made generation succeed."""

DEFAULT_TEMPERATURE = 0.6   # Qwen thinking-mode recommended setting
CONDITIONS = ("named", "anonymized")


class CachedThinkingClient:
    """Thinking-mode chat completion with a content-addressed disk cache.

    Posts its own request body rather than reusing
    ``OpenAIHTTPClient.generate_thinking`` because this task needs
    ``reasoning_effort`` in ``chat_template_kwargs`` (which that method
    does not expose) and needs the response's token usage and wall-clock
    time for the run's cost report. Cached rows carry the timing, so a
    replayed run still reports what generation originally cost.
    """

    def __init__(self, endpoint: str, model: str,
                 cache_dir: pathlib.Path, timeout: float = 2400.0) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._dir = cache_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self.calls = 0
        self.cache_hits = 0
        self.generation_seconds = 0.0
        """Wall-clock seconds spent in LIVE generation this run (cache
        hits cost nothing and are excluded)."""

    def generate(self, system: str, user: str, seed: int,
                 temperature: float, max_tokens: int,
                 reasoning_effort: str = DEFAULT_REASONING_EFFORT,
                 schema: Optional[Mapping[str, Any]] = None
                 ) -> Dict[str, Any]:
        """Return the full record: payload, think, usage, timing.

        With ``schema``, decoding is grammar-constrained and thinking is
        disabled (the two cannot be combined on this stack) — the
        structured-output salvage stage.
        """
        key = hashlib.sha256(json.dumps(
            [self._model, system, user, seed, temperature, max_tokens,
             reasoning_effort, schema], sort_keys=True).encode()).hexdigest()
        path = self._dir / f"{key}.json"
        if path.exists():
            self.cache_hits += 1
            row = json.loads(path.read_text())
            row["cached"] = True
            return row
        body: Dict[str, Any] = {
            "model": self._model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": temperature, "top_p": 0.95,
            "max_tokens": max_tokens,
            "seed": seed & 0x7FFFFFFFFFFFFFFF,
            "chat_template_kwargs": {"enable_thinking": True,
                                     "reasoning_effort": reasoning_effort},
        }
        if schema is not None:
            body["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "hypotheses", "schema": schema}}
            body["chat_template_kwargs"] = {"enable_thinking": False}
        started = time.monotonic()
        response = requests.post(f"{self._endpoint}/v1/chat/completions",
                                 json=body, timeout=self._timeout)
        response.raise_for_status()
        elapsed = time.monotonic() - started
        data = response.json()
        message = data["choices"][0]["message"]
        payload = message.get("content") or ""
        think = message.get("reasoning_content") or ""
        # No reasoning parser configured server-side: the think block
        # arrives inline, opened by the chat template and closed by the
        # model. An unclosed block means the budget ran out mid-thought
        # — the whole payload is reasoning and carries no JSON.
        if not think and "</think>" in payload:
            think, payload = payload.rsplit("</think>", 1)
            think = think.replace("<think>", "").strip()
        fence = re.search(r"```(?:json)?\s*(.*?)```", payload, re.S)
        if fence:
            payload = fence.group(1)
        usage = data.get("usage", {})
        row = {"payload": payload.strip(), "think": think,
               "model": self._model, "seed": seed,
               "temperature": temperature,
               "reasoning_effort": reasoning_effort,
               "generation_seconds": round(elapsed, 2),
               "prompt_tokens": usage.get("prompt_tokens"),
               "completion_tokens": usage.get("completion_tokens"),
               "finish_reason": data["choices"][0].get("finish_reason"),
               "think_closed": bool(think)}
        self.calls += 1
        self.generation_seconds += elapsed
        path.write_text(json.dumps(row))
        row["cached"] = False
        return row


def extract_json(payload: str) -> Any:
    """The one JSON object a reply must end with. First plain loads,
    then the outermost brace span; a reply without one is a call
    failure (retried with the next seed), never silently repaired."""
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        pass
    start, end = payload.find("{"), payload.rfind("}")
    if start >= 0 and end > start:
        return json.loads(payload[start:end + 1])
    raise json.JSONDecodeError("no JSON object in payload", payload, 0)


def validate_hypotheses(
        hypotheses: List[Mapping[str, Any]],
        object_classes: Mapping[str, str],
        receptacle_ids: Tuple[str, ...],
) -> Tuple[List[dict], List[dict]]:
    """Split into (valid, failed); each failed row carries the exact
    offending strings for the repair prompt."""
    valid: List[dict] = []
    failed: List[dict] = []
    for index, hypothesis in enumerate(hypotheses):
        try:
            parse_hypothesis(hypothesis, object_classes, receptacle_ids)
            valid.append(dict(hypothesis))
        except HypothesisValidationError as err:
            failed.append({"index": index, "hypothesis": dict(hypothesis),
                           "bad_strings": list(err.bad_strings),
                           "error": str(err)})
        except (TypeError, ValueError, KeyError) as err:
            failed.append({"index": index, "hypothesis": dict(hypothesis),
                           "bad_strings": [], "error": repr(err)})
    return valid, failed


def salvage_prompt(original_user: str, truncated_reasoning: str) -> str:
    """Ask only for the JSON, given the model's own (unfinished)
    reasoning. Used when a thinking call spent its whole budget
    reasoning and never serialized anything."""
    tail = truncated_reasoning[-12000:]
    return f"""{original_user}

---

You already began working on this task. Here is your own analysis so far (it was cut off before you wrote the JSON):

{tail}

---

Do not continue the analysis. Output ONLY the final JSON object now, using the conclusions above where they are usable and your best judgement where the analysis was cut off. It must contain exactly {N_HYPOTHESES} hypotheses and use only identifiers from the tables above."""


def repair_prompt(failed: List[dict], tables: str, raw_json: str) -> str:
    problems = "\n".join(
        f"- hypothesis {row['index']} "
        f"({row['hypothesis'].get('hypothesis_id', '?')}): {row['error']}"
        + (f"; invalid strings: {row['bad_strings']}"
           if row["bad_strings"] else "")
        for row in failed)
    return f"""Your previous output contained invalid identifiers or fields:

{problems}

The ONLY valid identifiers are these, exactly as printed:

{tables}

Here is your previous JSON:

{raw_json}

Reprint the COMPLETE corrected JSON object (all hypotheses, same shape). Replace every invalid string with a valid identifier from the tables, or remove the entry if nothing valid expresses it. Do not change hypotheses that were already valid. End your reply with the JSON object only."""


def elicit_household(client: CachedThinkingClient, episode,
                     condition: str, warmup_days: int, temperature: float,
                     max_tokens: int, llm_seed: int,
                     reasoning_effort: str = DEFAULT_REASONING_EFFORT,
                     tour_start: bool = False) -> Dict[str, Any]:
    """The full pipeline for one (household, condition). Returns the
    log row; the valid real-ID hypotheses are under ``"hypotheses"``.

    ``tour_start`` sends the walkthrough tour only (no sighting history)
    — the day-zero protocol; otherwise the first ``warmup_days`` of the
    passive stream go in."""
    anonymized = condition.endswith("anonymized")
    if tour_start:
        user, maps = tour_start_prompt(episode, anonymized=anonymized)
    else:
        user, maps = elicitation_prompt(episode, warmup_days,
                                        anonymized=anonymized)
    if anonymized:
        omap, rmap, cmap = (maps["omap"], maps["rmap"], maps["cmap"])
        seen_classes = {omap[o]: cmap[c]
                        for o, c in episode.object_classes.items()}
        seen_receptacles = tuple(rmap[r] for r in episode.receptacle_ids)
    else:
        seen_classes = dict(episode.object_classes)
        seen_receptacles = tuple(episode.receptacle_ids)
    tables = vocabulary_tables(
        episode, maps["omap"], maps["rmap"], maps["cmap"])

    log: Dict[str, Any] = {"household": episode.household_id,
                           "condition": condition, "prompt": user,
                           "rounds": []}
    hypotheses: List[dict] = []
    payload = ""
    total_seconds = 0.0
    # Round 0 (fresh seeds on JSON-shape failure) then one repair round.
    for attempt in range(3):
        row = client.generate(SYSTEM_PROMPT, user, seed=llm_seed + attempt,
                              temperature=temperature,
                              max_tokens=max_tokens,
                              reasoning_effort=reasoning_effort)
        payload, think = row["payload"], row["think"]
        total_seconds += row.get("generation_seconds") or 0.0
        stats = _call_stats(row)
        try:
            parsed = extract_json(payload)
        except json.JSONDecodeError as err:
            log["rounds"].append({"kind": "shape_failure", "error": str(err),
                                  "payload": payload, "think": think,
                                  **stats})
            continue
        hypotheses = list(parsed.get("hypotheses", []))
        log["rounds"].append({"kind": "initial", "think": think,
                              "payload": payload,
                              "n_hypotheses": len(hypotheses), **stats})
        break
    if not hypotheses:
        # The thinking call reasoned past its budget and never emitted
        # the JSON. Salvage rather than discard: hand the model its own
        # reasoning back and ask for the object alone, under a grammar
        # that cannot produce a shape error. Reasoning still came first;
        # only its serialization moves to a second call.
        salvage_user = salvage_prompt(user, payload)
        raw = client.generate(SYSTEM_PROMPT, salvage_user,
                              seed=llm_seed + 21, temperature=temperature,
                              max_tokens=max_tokens,
                              schema=HYPOTHESES_SCHEMA)
        total_seconds += raw.get("generation_seconds") or 0.0
        try:
            hypotheses = list(extract_json(raw["payload"]).get(
                "hypotheses", []))
        except json.JSONDecodeError as err:
            log["rounds"].append({"kind": "salvage_failed", "error": str(err),
                                  "payload": raw["payload"],
                                  **_call_stats(raw)})
        else:
            log["rounds"].append({"kind": "salvage",
                                  "payload": raw["payload"],
                                  "n_hypotheses": len(hypotheses),
                                  **_call_stats(raw)})
    valid, failed = validate_hypotheses(hypotheses, seen_classes,
                                        seen_receptacles)
    if failed:
        user2 = repair_prompt(failed, tables, payload)
        raw2 = client.generate(SYSTEM_PROMPT, user2, seed=llm_seed + 7,
                               temperature=temperature,
                               max_tokens=max_tokens,
                               reasoning_effort=reasoning_effort)
        payload2, think2 = raw2["payload"], raw2["think"]
        total_seconds += raw2.get("generation_seconds") or 0.0
        row: Dict[str, Any] = {"kind": "repair", "prompt": user2,
                               "think": think2, "payload": payload2,
                               **_call_stats(raw2)}
        try:
            reparsed = list(extract_json(payload2).get("hypotheses", []))
            valid2, failed2 = validate_hypotheses(
                reparsed, seen_classes, seen_receptacles)
            valid, failed = valid2, failed2
            row["n_valid"] = len(valid2)
        except json.JSONDecodeError as err:
            row["error"] = str(err)  # keep round-0 valid set
        log["rounds"].append(row)
    log["dropped"] = failed
    if anonymized:
        omap, rmap, cmap = (maps["omap"], maps["rmap"], maps["cmap"])
        translated = [deanonymize_hypothesis(h, omap, rmap, cmap)
                      for h in valid]
        # Belt and braces: everything must also validate in real space.
        real_valid, real_failed = validate_hypotheses(
            translated, episode.object_classes, episode.receptacle_ids)
        log["dropped"] += real_failed
        valid = real_valid
    log["hypotheses"] = valid
    log["generation_seconds"] = round(total_seconds, 2)
    log["seconds_per_hypothesis"] = (round(total_seconds / len(valid), 2)
                                     if valid else None)
    return log


def elicit_graph_household(client: CachedThinkingClient, episode,
                           condition: str, temperature: float,
                           max_tokens: int, llm_seed: int,
                           reasoning_effort: str = DEFAULT_REASONING_EFFORT
                           ) -> Dict[str, Any]:
    """The graph arm's tour-start elicitation for one (household,
    condition): one thinking call for the envelope, salvage through the
    envelope grammar when no JSON arrived, strict parsing
    (:func:`~baselines.llm_hypotheses.assumption_graph.parse_graph`),
    ONE repair round naming every problem and dropped leaf, and a
    deterministic cut if the repair still overshoots the caps. Returns
    the log row; the real-id envelope is under ``"graph"`` (None when
    nothing usable came back)."""
    anonymized = condition.endswith("anonymized")
    user, maps = graph_tour_start_prompt(episode, anonymized=anonymized)
    omap, rmap, cmap = maps["omap"], maps["rmap"], maps["cmap"]
    if anonymized:
        seen_classes = {omap[o]: cmap[c]
                        for o, c in episode.object_classes.items()}
        seen_receptacles = tuple(rmap[r] for r in episode.receptacle_ids)
    else:
        seen_classes = dict(episode.object_classes)
        seen_receptacles = tuple(episode.receptacle_ids)
    tables = vocabulary_tables(episode, omap, rmap, cmap)
    log: Dict[str, Any] = {"household": episode.household_id,
                           "condition": condition, "graph_arm": True,
                           "prompt": user, "rounds": []}
    envelope: Optional[dict] = None
    payload = ""
    total_seconds = 0.0
    for attempt in range(3):
        row = client.generate(SYSTEM_PROMPT, user, seed=llm_seed + attempt,
                              temperature=temperature, max_tokens=max_tokens,
                              reasoning_effort=reasoning_effort)
        payload, think = row["payload"], row["think"]
        total_seconds += row.get("generation_seconds") or 0.0
        try:
            parsed = extract_json(payload)
        except json.JSONDecodeError as err:
            log["rounds"].append({"kind": "shape_failure", "error": str(err),
                                  "payload": payload, "think": think,
                                  **_call_stats(row)})
            continue
        envelope = parsed if isinstance(parsed, dict) else None
        log["rounds"].append({"kind": "initial", "think": think,
                              "payload": payload,
                              "n_leaves": len((envelope or {}).get(
                                  "leaves", [])),
                              **_call_stats(row)})
        break
    if envelope is None:
        raw = client.generate(SYSTEM_PROMPT, salvage_prompt(user, payload),
                              seed=llm_seed + 21, temperature=temperature,
                              max_tokens=max_tokens, schema=GRAPH_SCHEMA)
        total_seconds += raw.get("generation_seconds") or 0.0
        try:
            envelope = extract_json(raw["payload"])
            log["rounds"].append({"kind": "salvage", "payload": raw["payload"],
                                  **_call_stats(raw)})
        except json.JSONDecodeError as err:
            log["rounds"].append({"kind": "salvage_failed", "error": str(err),
                                  "payload": raw["payload"],
                                  **_call_stats(raw)})
            envelope = None

    result = parse_graph(envelope or {}, seen_classes, seen_receptacles)
    log["substitutions"] = list(result.substitutions)
    log["dropped"] = list(result.dropped)
    if result.problems or result.dropped:
        problems = list(result.problems) + [
            f"leaf {d['index']} ({d['leaf'].get('leaf_id', '?')}): "
            f"{d['error']}" + (f"; invalid strings: {d['bad_strings']}"
                               if d["bad_strings"] else "")
            for d in result.dropped]
        user2 = graph_repair_prompt(problems, tables,
                                    json.dumps(envelope, indent=1))
        raw2 = client.generate(SYSTEM_PROMPT, user2, seed=llm_seed + 7,
                               temperature=temperature, max_tokens=max_tokens,
                               reasoning_effort=reasoning_effort)
        total_seconds += raw2.get("generation_seconds") or 0.0
        entry: Dict[str, Any] = {"kind": "repair", "prompt": user2,
                                 "think": raw2["think"],
                                 "payload": raw2["payload"],
                                 **_call_stats(raw2)}
        try:
            envelope2 = extract_json(raw2["payload"])
            result2 = parse_graph(envelope2, seen_classes, seen_receptacles)
            entry["problems"] = list(result2.problems)
            entry["n_dropped"] = len(result2.dropped)
            cap_only = result2.problems and all(
                "exceeds the cap" in p for p in result2.problems)
            if result2.graph is not None or cap_only:
                if result2.graph is None:
                    # Only the caps were violated: cut deterministically
                    # rather than throw away a valid set.
                    relaxed = parse_graph(envelope2, seen_classes,
                                          seen_receptacles, enforce_caps=False)
                    if relaxed.graph is not None:
                        cut, notes = truncate_to_caps(relaxed.graph)
                        entry["truncated"] = notes
                        result2 = parse_graph(cut.to_json(), seen_classes,
                                              seen_receptacles)
                result = result2
                log["substitutions"] += list(result2.substitutions)
                log["dropped"] = list(result2.dropped)
        except json.JSONDecodeError as err:
            entry["error"] = str(err)   # keep the round-0 parse
        log["rounds"].append(entry)

    graph_json: Optional[dict] = None
    if result.graph is not None:
        graph_json = result.graph.to_json()
        if anonymized:
            graph_json = deanonymize_graph(graph_json, omap, rmap, cmap)
            real = parse_graph(graph_json, episode.object_classes,
                               episode.receptacle_ids)
            log["dropped"] += real.dropped
            graph_json = real.graph.to_json() if real.graph else None
        if envelope is not None and "leaf_set_rationale" in envelope \
                and graph_json is not None:
            graph_json["leaf_set_rationale"] = envelope["leaf_set_rationale"]
    log["graph"] = graph_json
    log["problems"] = list(result.problems)
    n_leaves = len(graph_json["leaves"]) if graph_json else 0
    log["generation_seconds"] = round(total_seconds, 2)
    log["seconds_per_hypothesis"] = (round(total_seconds / n_leaves, 2)
                                     if n_leaves else None)
    return log


def _call_stats(row: Mapping[str, Any]) -> Dict[str, Any]:
    """The per-call cost record: how long generation took, how many
    tokens it spent, and whether the reasoning block actually closed
    (an unclosed one means the budget ran out mid-thought)."""
    return {"generation_seconds": row.get("generation_seconds"),
            "completion_tokens": row.get("completion_tokens"),
            "prompt_tokens": row.get("prompt_tokens"),
            "finish_reason": row.get("finish_reason"),
            "think_closed": row.get("think_closed"),
            "cached": row.get("cached")}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--households", nargs="+", required=True)
    ap.add_argument("--seed", type=int, default=0, help="bank seed")
    ap.add_argument("--endpoint", default="http://127.0.0.1:8300")
    ap.add_argument("--model", default="Qwen/Qwen3.8-27B")
    ap.add_argument("--conditions", nargs="+", default=list(CONDITIONS),
                    choices=CONDITIONS)
    ap.add_argument("--tour-start", action="store_true",
                    help="send only the walkthrough tour (no sighting "
                         "history); outputs go under conditions prefixed "
                         "tour_ so they never overwrite the history-fed set")
    ap.add_argument("--graph", action="store_true",
                    help="graph arm: elicit an assumption-graph envelope "
                         "from the tour (implies --tour-start); outputs go "
                         "under conditions prefixed graph_")
    ap.add_argument("--warmup-days", type=int, default=DEFAULT_WARMUP_DAYS)
    ap.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    ap.add_argument("--llm-seed", type=int, default=11)
    ap.add_argument("--reasoning-effort", default=DEFAULT_REASONING_EFFORT,
                    choices=("low", "medium", "xhigh"))
    ap.add_argument("--out-dir", type=pathlib.Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--bank-dir", type=pathlib.Path, default=None,
                    help="bank directory (default: the fleet's)")
    ap.add_argument("--hyp-subdir", default="",
                    help="subdirectory under hypotheses/<condition>/ and "
                         "logs/<condition>/ — one per bank when several "
                         "banks of one household are elicited")
    args = ap.parse_args()

    client = CachedThinkingClient(args.endpoint, args.model,
                                  args.out_dir / "cache")
    cost: List[Dict[str, Any]] = []
    for household in args.households:
        episode = next(JsonlBank(bank_path(household, args.seed,
                                           args.bank_dir)).episodes())
        _write_crossref(episode, args.out_dir)
        for condition in args.conditions:
            if args.graph:
                log = elicit_graph_household(
                    client, episode, condition, args.temperature,
                    args.max_tokens, args.llm_seed, args.reasoning_effort)
                log["hypotheses"] = (log["graph"] or {}).get("leaves", [])
                tag = f"graph_{condition}"
                payload_out: Dict[str, Any] = log["graph"] or {
                    "assumptions": {}, "leaves": []}
            else:
                log = elicit_household(client, episode, condition,
                                       args.warmup_days, args.temperature,
                                       args.max_tokens, args.llm_seed,
                                       args.reasoning_effort,
                                       tour_start=args.tour_start)
                tag = f"tour_{condition}" if args.tour_start else condition
                payload_out = {"hypotheses": log["hypotheses"]}
            hyp_dir = args.out_dir / "hypotheses" / tag / args.hyp_subdir
            log_dir = args.out_dir / "logs" / tag / args.hyp_subdir
            hyp_dir.mkdir(parents=True, exist_ok=True)
            log_dir.mkdir(parents=True, exist_ok=True)
            (hyp_dir / f"{episode.household_id}.json").write_text(
                json.dumps(payload_out, indent=1))
            (log_dir / f"{episode.household_id}.json").write_text(
                json.dumps(log, indent=1))
            tokens = sum(r.get("completion_tokens") or 0
                         for r in log["rounds"])
            cost.append({"household": household, "condition": tag,
                         "n_hypotheses": len(log["hypotheses"]),
                         "n_dropped": len(log["dropped"]),
                         "n_calls": len(log["rounds"]),
                         "completion_tokens": tokens,
                         "generation_seconds": log["generation_seconds"],
                         "seconds_per_hypothesis":
                             log["seconds_per_hypothesis"]})
            print(f"{household} {tag}: {len(log['hypotheses'])} valid "
                  f"hypotheses, {len(log['dropped'])} dropped, "
                  f"{log['generation_seconds']:.0f}s generation "
                  f"({log['seconds_per_hypothesis']}s per hypothesis, "
                  f"{tokens} output tokens)")
    cost_name = ("generation_cost_graph.json" if args.graph else
                 "generation_cost_tour.json" if args.tour_start
                 else "generation_cost.json")
    (args.out_dir / cost_name).write_text(json.dumps(
        {"model": args.model, "reasoning_effort": args.reasoning_effort,
         "max_tokens": args.max_tokens,
         "live_calls": client.calls, "cache_hits": client.cache_hits,
         "live_generation_seconds": round(client.generation_seconds, 1),
         "rows": cost}, indent=1))
    print(f"LLM calls made: {client.calls} "
          f"({client.generation_seconds:.0f}s live generation), "
          f"cache hits: {client.cache_hits}")


def _write_crossref(episode, out_dir: pathlib.Path) -> None:
    """The anonymization cross-reference table, written per household
    whether or not the anonymized condition runs — it is the key for
    reading any anonymized artifact later."""
    from baselines.llm_hypotheses.prompt import build_anonymization_maps
    omap, rmap, cmap = build_anonymization_maps(episode)
    directory = out_dir / "anonymization"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{episode.household_id}.md").write_text(
        crossref_table(episode, omap, rmap, cmap))
    (directory / f"{episode.household_id}.json").write_text(json.dumps(
        {"objects": omap, "receptacles": rmap, "classes": cmap}, indent=1))


if __name__ == "__main__":
    main()
