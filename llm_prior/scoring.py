"""
llm_prior/scoring.py — turns a raw elicitation response (whatever
llm_prior.client.LLMPriorClient returned, read back from the committed
cache — never a live call, per L0's own infrastructure rule) into a
normalized distribution over a target's support, then scores that
distribution the same way scripts/kernel_reliability_diagram.py already
scores the fitted kernel: reliability_points/bin_reliability/write_plot
are imported and reused UNCHANGED, not reimplemented, against a
llm_prior.synthetic_kernel.TransitionKernel built from the parsed
elicitation.

Every parser here is defensive about malformed model output (a verbalized
JSON response that doesn't parse, a sample_count run that never produces
a recognized letter) — a parse failure is recorded and reported as a data
quality number (see ParseFailure), never silently defaulted to a uniform
guess and passed off as a real elicited prior.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import Optional

# SentencePiece's word-boundary marker — vLLM's decoded_token for a
# leading-space token like " A" comes back as "▁A", not " A".
_SENTENCEPIECE_SPACE = "▁"


class ParseFailure(Exception):
    """Raised by a mode parser when the model's raw response can't be
    turned into a valid distribution — callers must catch this and record
    it (see llm_prior/elicit.py's manifest "parse_failures" field), not
    swallow it into a default guess."""


def _clean_token(token: str) -> str:
    return token.replace(_SENTENCEPIECE_SPACE, "").strip().upper()


def parse_mcq_logprob_distribution(top_logprobs: dict[str, float], option_letters: tuple[str, ...]) -> dict[str, float]:
    """Restricts the model's next-token distribution to option_letters and
    renormalizes — the standard KnowNo-style construction. A letter absent
    from the returned top-N logprobs gets a floor probability (one e-fold
    below the lowest logprob actually observed) rather than zero, so an
    option that was merely outside the top-N doesn't vanish outright."""
    if not top_logprobs:
        raise ParseFailure("empty top_logprobs")
    by_letter: dict[str, list[float]] = {letter: [] for letter in option_letters}
    for token, logprob in top_logprobs.items():
        clean = _clean_token(token)
        if clean in by_letter:
            by_letter[clean].append(logprob)
    floor_logprob = min(top_logprobs.values()) - 1.0
    raw = {}
    for letter in option_letters:
        lps = by_letter[letter]
        raw[letter] = sum(math.exp(lp) for lp in lps) if lps else math.exp(floor_logprob)
    total = sum(raw.values())
    return {letter: p / total for letter, p in raw.items()}


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> dict:
    match = _JSON_OBJECT_RE.search(text)
    if not match:
        raise ParseFailure(f"no JSON object found in: {text!r}")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ParseFailure(f"invalid JSON in: {text!r} ({e})") from e


def parse_verbalized_location(raw_text: str, support: tuple[str, ...]) -> dict[str, float]:
    obj = _extract_json(raw_text)
    if not isinstance(obj, dict):
        raise ParseFailure(f"verbalized JSON is not an object: {raw_text!r}")
    missing = [s for s in support if s not in obj]
    if missing:
        raise ParseFailure(f"verbalized JSON missing support states {missing}: {raw_text!r}")
    try:
        values = {s: float(obj[s]) for s in support}
    except (TypeError, ValueError) as e:
        raise ParseFailure(f"non-numeric value in verbalized JSON: {raw_text!r} ({e})") from e
    total = sum(values.values())
    if total <= 0:
        raise ParseFailure(f"verbalized probabilities sum to <= 0: {raw_text!r}")
    return {s: v / total for s, v in values.items()}


def parse_verbalized_stay_probability(raw_text: str) -> float:
    obj = _extract_json(raw_text)
    if "stay_probability" not in obj:
        raise ParseFailure(f"verbalized JSON missing stay_probability: {raw_text!r}")
    try:
        p = float(obj["stay_probability"])
    except (TypeError, ValueError) as e:
        raise ParseFailure(f"non-numeric stay_probability: {raw_text!r} ({e})") from e
    if not (0.0 <= p <= 1.0):
        raise ParseFailure(f"stay_probability out of [0,1]: {p}")
    return p


@dataclass(frozen=True)
class SampleCountResult:
    distribution: dict[str, float]
    unparsed_fraction: float
    n: int


def parse_sample_count_distribution(counts: dict[str, int], option_letters: tuple[str, ...]) -> SampleCountResult:
    n = sum(counts.values())
    if n == 0:
        raise ParseFailure("sample_count returned zero total samples")
    recognized = sum(counts.get(letter, 0) for letter in option_letters)
    unparsed = counts.get("_other", 0)
    if recognized == 0:
        raise ParseFailure(f"sample_count produced no recognized options: {counts}")
    distribution = {letter: counts.get(letter, 0) / recognized for letter in option_letters}
    return SampleCountResult(distribution=distribution, unparsed_fraction=unparsed / n, n=n)


def parse_location_distribution_from_cache(
    cache, model_id: str, mode: str, prompt_hash: str,
    support: tuple[str, ...], option_letters: tuple[str, ...],
) -> dict[str, float]:
    """The one place a (model, mode, prompt_hash) triple is turned into a
    normalized location-prior distribution, reading only from the
    committed cache (llm_prior.cache.EliciationCache — never a live
    call). Shared by llm_prior/report.py's scoring pass and llm_prior/
    pseudo_counts.py's T1 conversion so both read the identical parse for
    the identical cached response, rather than each having its own copy
    that could silently drift apart."""
    entry = cache.get(model_id, prompt_hash, mode, 0)
    if entry is None:
        raise ParseFailure(f"cache miss: {model_id}/{prompt_hash}/{mode}")
    raw = entry["raw_response"]
    if mode == "mcq_logprob":
        by_letter = parse_mcq_logprob_distribution(raw["top_logprobs"], option_letters)
        return {slot: by_letter[letter] for letter, slot in zip(option_letters, support)}
    if mode == "verbalized":
        return parse_verbalized_location(raw, support)
    if mode == "sample_count":
        result = parse_sample_count_distribution(raw, option_letters)
        return {slot: result.distribution[letter] for letter, slot in zip(option_letters, support)}
    raise ValueError(f"unknown mode {mode!r}")


def brier_score(predicted: dict[str, float], true_state: str) -> float:
    """Standard multi-class Brier score: mean squared error between the
    predicted distribution and the one-hot ground truth, over every
    outcome in `predicted` (true_state must be one of its keys)."""
    if true_state not in predicted:
        raise ValueError(f"true_state {true_state!r} not in predicted distribution {list(predicted)}")
    return sum((p - (1.0 if s == true_state else 0.0)) ** 2 for s, p in predicted.items())
