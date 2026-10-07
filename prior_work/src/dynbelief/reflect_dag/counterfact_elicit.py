"""Change 2 — CounterfactCoT do-contrast elicitation (replaces the entropy gate).

The entropy gate failed its calibration check (P4): LLM self-reported hypothesis
entropy did not predict correctness. FBN's CounterfactCoT (Zhang et al. ICCV 2025,
Eq. 1; Table 1: GPT-4o SR 58.8 vs 56.0 direct vs 50.1 CoT) elicits edge weights
CONTRASTIVELY instead of asking for confidence: for hypothesis H and diagnostic
observation O, prompt separately for
    factual        p_f = P(O expected | H present)
    counterfactual p_c = P(O expected | H absent, same household otherwise)
and derive the weight from the gap. We use the log-odds difference (the do-
contrast), squashed to [0,1]:
    contrast(H, O) = |logit(p_f) - logit(p_c)| / 4     (clipped)
A sharp gap => O discriminates H => the prior asserted on H's back is worth more
pseudo-observations. A flat gap => O is regime-neutral => small alpha.

Budget: 2 prompts per (hypothesis, observation) pair, run ONLY on the sparse
diagnostic digest lines (<= _MAX_OBS of them), never per query. Call counts are
returned for logging (FBN reports 3-8 calls/node as acceptable).

The calibration check that killed the entropy gate is re-run in report_dag.py:
per-household mean contrast vs prediction correctness. If contrast is ALSO
uncalibrated, the honest fallback is the pure alpha/(alpha+n) evidence ratio.
"""
from __future__ import annotations

import json
import math

_PROB_SCHEMA = {
    "type": "object",
    "properties": {"reasoning": {"type": "string"},
                   "p_expected": {"type": "number"}},
    "required": ["reasoning", "p_expected"]}

_SYS_FACT = (
    "You judge how EXPECTED a single household observation is under a stated "
    "hypothesis about the household. Think briefly, then give p_expected in [0,1]: "
    "the probability that an observation like this would occur in a household for "
    "which the hypothesis IS TRUE. Day 0 is Monday; days 5-6 are the weekend.")

_SYS_CF = (
    "You judge how EXPECTED a single household observation is if a stated "
    "hypothesis about the household is FALSE. Think briefly, then give p_expected "
    "in [0,1]: the probability that an observation like this would occur in an "
    "otherwise-ordinary household for which the hypothesis is NOT true. Day 0 is "
    "Monday; days 5-6 are the weekend.")

_MAX_OBS = 8          # cap: contrast only the digest's diagnostic lines


def _logit(p: float) -> float:
    p = min(1 - 1e-3, max(1e-3, float(p)))
    return math.log(p / (1 - p))


def _ask(client, sys, hypothesis, obs_line, seed):
    user = (f"Hypothesis about the household: {hypothesis}\n\n"
            f"Observation: {obs_line.strip()}\n\n"
            f"How expected is this observation? Return p_expected.")
    out = json.loads(client.generate(sys, user, _PROB_SCHEMA, seed=seed,
                                     temperature=0.0, max_tokens=512))
    return float(out["p_expected"])


def do_contrast(client, hypothesis: str, obs_lines: list[str], seed: int = 7):
    """Mean do-contrast of a hypothesis over the diagnostic observations.

    Returns (contrast in [0,1], per-obs details, n_llm_calls). Failed calls are
    skipped (contrast from the rest); all-failed -> contrast 0 (no evidence the
    prior discriminates -> minimal alpha, the conservative direction)."""
    details, calls = [], 0
    for i, line in enumerate(obs_lines[:_MAX_OBS]):
        try:
            pf = _ask(client, _SYS_FACT, hypothesis, line, seed + 2 * i)
            calls += 1
            pc = _ask(client, _SYS_CF, hypothesis, line, seed + 2 * i + 1)
            calls += 1
        except Exception:
            continue
        gap = abs(_logit(pf) - _logit(pc))
        details.append({"obs": line.strip(), "p_fact": round(pf, 3),
                        "p_cf": round(pc, 3), "gap": round(gap, 3)})
    if not details:
        return 0.0, details, calls
    mean_gap = sum(d["gap"] for d in details) / len(details)
    return min(1.0, mean_gap / 4.0), details, calls
