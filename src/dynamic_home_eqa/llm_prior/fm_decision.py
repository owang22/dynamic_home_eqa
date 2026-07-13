"""
llm_prior/fm_decision.py — Phase A, A1: the FM decision backbone.

The FM reads a text rendering of the kernel's own belief state (current
top candidate, elapsed time since last update, the full propagated
posterior distribution) plus the question, and chooses ONE of: answer
with one of the question's options, or resense (re-check before
answering). It never recomputes transition dynamics and never sees
anything the kernel didn't already compute — the posterior numbers in
the prompt come directly from PosteriorObjectNode.propagated(t), not
from any belief the FM forms on its own.

This is deliberately an OPEN comparison against decay_voi (embodied/
policy.py's DecayVoi), not a confinement: nothing here encodes an
assumption that the FM is "only" fit for reading a precomputed posterior
because it can't forecast dynamics itself. That framing is not
established at the scale this project has measured (L0/L1 T0 covered one
scene) and must not leak into this module's prompts, code, or the reports
built from it. This module measures whether the FM's decision QUALITY
(answer-vs-resense, at what confidence) beats decay_voi's VoI arithmetic,
nothing more and nothing less.

Reuses embodied.policy's own search/answer machinery for the mechanics
every other resense-capable policy already shares (_search_targets picks
the next best resense candidate from the SAME posterior the FM was shown;
_answer_from_belief resolves a believed anchor to a question option) —
imported directly rather than duplicated, since re-deriving this logic
here would risk it silently drifting from what decay_voi/decay_threshold
actually do, undermining the head-to-head comparison this module exists
to run cleanly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from dynamic_home_eqa.embodied.belief import BeliefStore
from dynamic_home_eqa.embodied.policy import (
    Decision,
    ResensePlan,
    TravelTimeFn,
    _answer_from_belief,
    _search_targets,
)
from dynamic_home_eqa.embodied.question import MCQQuestion
from dynamic_home_eqa.embodied.scoring import Choice
from dynamic_home_eqa.llm_prior import prompts
from dynamic_home_eqa.llm_prior.cache import EliciationCache
from dynamic_home_eqa.llm_prior.scoring import parse_mcq_logprob_distribution


class MCQLogprobClient(Protocol):
    """Structural type both llm_prior.client.LLMPriorClient (in-process
    vLLM, same env L0's elicitation uses) and llm_prior.http_client.
    HTTPLLMClient (cross-process, for running inside a habitat_sim
    episode under an env with no vllm installed — see that module's own
    docstring for why both exist) satisfy without either needing to
    subclass the other. FMDecisionPolicy only ever calls this one method
    plus reads client.spec.model_id."""
    spec: object  # duck-typed: only .model_id is actually read

    def mcq_logprob(self, system: str, user: str, option_letters: tuple[str, ...], seed: int) -> dict: ...


DECISION_SYSTEM_PROMPT = (
    "You are a household robot answering questions about where objects are "
    "in a specific home. For each question you may either answer now using "
    "your current belief, or first travel to re-check the object's location "
    "before answering. Re-checking costs travel time; answering incorrectly "
    "costs accuracy. Decide which is better for this specific question, "
    "using only the belief information given below — do not invent "
    "information about the object's location beyond what is stated."
)


@dataclass(frozen=True)
class BeliefSummary:
    label: str
    category: str
    believed_anchor: Optional[str]     # current top candidate, belief.believed_anchor(label, t)
    elapsed_hours: Optional[float]     # since last update (positive or negative); None if never observed
    posterior: dict[str, float]        # full propagated distribution, if the belief store exposes one


def build_belief_summary(belief: BeliefStore, question: MCQQuestion, t: float) -> BeliefSummary:
    posterior: dict[str, float] = {}
    nodes = getattr(belief, "nodes", None)
    node = nodes.get(question.label) if nodes is not None else None
    if node is not None and hasattr(node, "propagated"):
        posterior = node.propagated(t)
    return BeliefSummary(
        label=question.label, category=question.category,
        believed_anchor=belief.believed_anchor(question.label, t),
        elapsed_hours=belief.elapsed_since_update(question.label, t),
        posterior=posterior,
    )


def render_belief_summary(summary: BeliefSummary) -> str:
    lines = [f'Object: "{summary.label}" (category: {summary.category})']
    if summary.believed_anchor is None:
        lines.append("Current belief: nothing currently believed about this object's location.")
    else:
        age = f"{summary.elapsed_hours:.2f} hours ago" if summary.elapsed_hours is not None else "unknown"
        lines.append(f'Current belief: most likely at "{summary.believed_anchor}" (last updated {age}).')
    if summary.posterior:
        ranked = sorted(summary.posterior.items(), key=lambda kv: -kv[1])
        dist_text = ", ".join(f"{state}: {p:.2f}" for state, p in ranked)
        lines.append(f"Full probability distribution over possible locations: {dist_text}")
    return "\n".join(lines)


def _option_letters(n: int) -> tuple[str, ...]:
    return tuple(chr(ord("A") + i) for i in range(n))


def decision_prompt(summary: BeliefSummary, question: MCQQuestion) -> tuple[str, str, tuple[str, ...], str]:
    """Returns (system, user, all_letters, resense_letter). all_letters
    has one entry per question option plus one trailing entry for the
    resense action — mirrors llm_prior/prompts.py's own MCQ shape (a
    single-letter answer, scored via logprobs) so llm_prior.scoring.
    parse_mcq_logprob_distribution works unchanged."""
    letters = _option_letters(len(question.options) + 1)
    resense_letter = letters[-1]
    options_lines = [f"{letter}) {opt}" for letter, opt in zip(letters, question.options)]
    options_lines.append(f"{resense_letter}) [Re-check the object's location before answering]")
    user = (
        f"Question: {question.stem}\n\n"
        f"{render_belief_summary(summary)}\n\n"
        f"Options:\n" + "\n".join(options_lines) + "\n\n"
        f"Answer with only the single letter of your chosen action."
    )
    return DECISION_SYSTEM_PROMPT, user, letters, resense_letter


class FMDecisionPolicy:
    """A1's decision backbone. Same DecisionPolicy shape as every policy
    in embodied/policy.py (act(belief, question, pose, t, config,
    travel_time_to) -> Decision) so it runs through the existing
    QuestionEpisodeRunner/rerun_frozen_e0 harness unchanged and is
    directly comparable to decay_voi on identical questions."""

    def __init__(self, client: MCQLogprobClient, cache: EliciationCache, seed: int = 0) -> None:
        self.client = client
        self.cache = cache
        self.seed = seed

    def act(self, belief: BeliefStore, question: MCQQuestion, pose, t: float,
            config, travel_time_to: TravelTimeFn) -> Decision:
        summary = build_belief_summary(belief, question, t)
        system, user, letters, resense_letter = decision_prompt(summary, question)
        prompt_hash = prompts.prompt_hash("fm_decision", system, user)
        model_id = self.client.spec.model_id

        if not self.cache.has(model_id, prompt_hash, "mcq_logprob", self.seed):
            raw = self.client.mcq_logprob(system, user, letters, seed=self.seed)
            self.cache.put(model_id, prompt_hash, "mcq_logprob", self.seed, prompt=user, raw_response=raw)
        entry = self.cache.get(model_id, prompt_hash, "mcq_logprob", self.seed)
        dist = parse_mcq_logprob_distribution(entry["raw_response"]["top_logprobs"], letters)
        chosen_letter = max(dist, key=dist.get)

        if chosen_letter == resense_letter:
            targets = _search_targets(belief, question.label, t, travel_time_to)
            if targets:
                return ResensePlan(targets=targets)
            # Nothing left to search (depth cap hit, or nothing ever
            # believed) — fall through to answering from whatever belief
            # exists, same tail every other search policy uses.
            return _answer_from_belief(belief, question, question.label, t,
                                       confidence=belief.validity(question.label, t) if hasattr(belief, "validity") else 0.0)

        answer_letters = letters[:-1]
        option_index = answer_letters.index(chosen_letter)
        # Confidence renormalized over just the real answer options —
        # the resense option's own probability mass isn't part of "how
        # sure am I about THIS answer" once an answer has been chosen.
        answer_mass = sum(dist[letter] for letter in answer_letters)
        confidence = dist[chosen_letter] / answer_mass if answer_mass > 0 else 0.0
        return Choice(option_index=option_index, confidence=confidence)
