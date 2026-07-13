"""
llm_prior/pseudo_counts.py — L1 T1: converts an L0-style elicited
categorical distribution into Dirichlet pseudo-counts pluggable directly
into embodied.posterior.shrink_hierarchical_with_llm's `llm`
HierarchicalStat argument. No new elicitation modes and no new model
calls — this module only reads llm_prior.cache.EliciationCache through
llm_prior.scoring.parse_location_distribution_from_cache, the exact same
parse L0's own scoring pass uses.

Dirichlet pseudo-counts, in one line: an elicited distribution p over
states, scaled by a total concentration alpha_0, gives per-state pseudo-
counts alpha_i = alpha_0 * p_i. Interpreting alpha_0 as
HierarchicalStat.weight makes shrink_hierarchical_with_llm's backoff
arithmetic exactly the Dirichlet-multinomial posterior update it already
resembles (_shrink is a weighted average of two already-normalized
distributions, which is exactly what pseudo-count blending reduces to
when both sides are proper probabilities) — no new smoothing math is
introduced here, only the L0-to-D1 plumbing.
"""
from __future__ import annotations

from dataclasses import dataclass

from dynamic_home_eqa.embodied.posterior import HierarchicalStat
from dynamic_home_eqa.llm_prior.cache import EliciationCache
from dynamic_home_eqa.llm_prior.scoring import parse_location_distribution_from_cache


@dataclass(frozen=True)
class LLMPseudoCounts:
    """Recorded verbatim into T2's belief-construction manifest — same
    "record exact model identifiers, prompt hash, sampling params" rule
    L0's own elicitation manifests already follow, so a T2 result can be
    traced back to exactly which cached elicitation backed it."""
    key: str                      # category, or "category::variable" for state
    states: tuple[str, ...]
    pseudo_counts: dict[str, float]  # alpha_i = concentration * p_i; sums to concentration
    concentration: float
    model_id: str
    mode: str
    prompt_hash: str


def elicited_distribution_to_pseudo_counts(
    distribution: dict[str, float], concentration: float, *,
    key: str, model_id: str, mode: str, prompt_hash: str,
) -> LLMPseudoCounts:
    """concentration is the Dirichlet prior's total pseudo-count (alpha_0)
    — this is the SAME number as shrink_hierarchical_with_llm's llm.weight
    and controls how many real observations it takes to override the LLM
    prior (see that function's own docstring for the exact do-no-harm and
    zero-data-limit properties this number produces). concentration=0 is
    legal (produces an all-zero pseudo_counts dict) — the do-no-harm
    floor — and is not treated as an error here; only downstream
    HierarchicalStat construction needs to special-case it (see
    to_hierarchical_stat)."""
    if concentration < 0:
        raise ValueError(f"concentration must be >= 0, got {concentration}")
    total = sum(distribution.values())
    if total <= 0:
        raise ValueError(f"distribution sums to <= 0: {distribution}")
    normalized = {s: p / total for s, p in distribution.items()}
    pseudo_counts = {s: concentration * p for s, p in normalized.items()}
    return LLMPseudoCounts(
        key=key, states=tuple(distribution.keys()), pseudo_counts=pseudo_counts,
        concentration=concentration, model_id=model_id, mode=mode, prompt_hash=prompt_hash,
    )


def to_hierarchical_stat(pseudo_counts: LLMPseudoCounts, state: str) -> HierarchicalStat:
    """value is irrelevant when concentration=0 (shrink_hierarchical_with_
    llm's own documented convention — see its do-no-harm floor test) so
    dividing by zero there is avoided rather than propagated; any state
    not in pseudo_counts.states raises rather than silently returning 0,
    since that would misrepresent "this state was never elicited" as
    "this state has zero probability", a real difference for a caller
    deciding whether to trust this stat at all."""
    if state not in pseudo_counts.pseudo_counts:
        raise KeyError(f"state {state!r} not in elicited states {pseudo_counts.states}")
    if pseudo_counts.concentration == 0:
        return HierarchicalStat(value=0.0, weight=0.0)
    return HierarchicalStat(
        value=pseudo_counts.pseudo_counts[state] / pseudo_counts.concentration,
        weight=pseudo_counts.concentration,
    )


def elicited_pseudo_counts_from_cache(
    cache: EliciationCache, model_id: str, mode: str, prompt_hash: str,
    support: tuple[str, ...], option_letters: tuple[str, ...], concentration: float, key: str,
) -> LLMPseudoCounts:
    """End-to-end: read the committed L0 cache for one (model, mode,
    target), parse it through the identical path L0's own scoring pass
    uses (llm_prior.scoring.parse_location_distribution_from_cache — no
    duplicated parsing logic), and scale to pseudo-counts. Raises
    llm_prior.scoring.ParseFailure under the same conditions L0's own
    scoring does (cache miss, malformed model output) — a caller building
    a belief must decide how to handle a missing/failed elicitation the
    same deliberate way L0's report does (record it, do not silently
    default), not have that decision hidden inside this function."""
    distribution = parse_location_distribution_from_cache(cache, model_id, mode, prompt_hash, support, option_letters)
    return elicited_distribution_to_pseudo_counts(
        distribution, concentration, key=key, model_id=model_id, mode=mode, prompt_hash=prompt_hash,
    )
