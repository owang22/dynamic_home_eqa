"""
Tests for llm_prior/fm_decision.py — Phase A, A1's FM decision backbone.
A fake client stands in for LLMPriorClient so these never touch vLLM or
the network, per this project's "no live LLM calls in pytest" rule.
"""
from __future__ import annotations

import tempfile
from dataclasses import dataclass

import pytest

from dynamic_home_eqa.embodied.policy import ResensePlan
from dynamic_home_eqa.embodied.posterior import PosteriorBeliefStore, PosteriorObjectNode, TransitionKernel
from dynamic_home_eqa.embodied.question import MCQQuestion
from dynamic_home_eqa.embodied.scoring import Abstain, Choice
from dynamic_home_eqa.embodied.types import Pose
from dynamic_home_eqa.llm_prior.cache import EliciationCache
from dynamic_home_eqa.llm_prior.client import ModelSpec
from dynamic_home_eqa.llm_prior.fm_decision import (
    FMDecisionPolicy,
    build_belief_summary,
    decision_prompt,
    render_belief_summary,
)

_POSE = Pose(0.0, 0.0, 0.0, 0.0)
_SPEC = ModelSpec(model_id="fake/model", family="fake", provider="test", quantization="none", is_generator_family=False)


def _question(options=("shelf", "table", "OUTSIDE")) -> MCQQuestion:
    return MCQQuestion(
        label="book_1", category="book", stem="Where is the book?",
        options=options, correct_index=0, asked_t=1.0,
        hazard_class="stable", distractor_provenance=("real", "real", "real"),
    )


def _kernel(states=("shelf", "table", "OUTSIDE"), dest_dist=None) -> TransitionKernel:
    n = len(states)
    return TransitionKernel(category="book", states=states, lambda_per_hour=0.5, dest_dist=dest_dist or tuple(1 / n for _ in states))


def _store_with_belief(posterior, last_updated_t=0.0, positive=True) -> PosteriorBeliefStore:
    kernel = _kernel()
    store = PosteriorBeliefStore(kernels={"book": kernel})
    store.nodes["book_1"] = PosteriorObjectNode(
        label="book_1", category="book", kernel=kernel,
        posterior=posterior, last_updated_t=last_updated_t, last_update_was_positive=positive,
    )
    return store


def _empty_store() -> PosteriorBeliefStore:
    return PosteriorBeliefStore(kernels={"book": _kernel()})


@dataclass
class _FakeClient:
    spec: ModelSpec
    chosen_letter: str
    calls: list = None

    def __post_init__(self):
        self.calls = []

    def mcq_logprob(self, system, user, option_letters, seed):
        self.calls.append((system, user))
        # Overwhelmingly confident in self.chosen_letter; a small amount
        # of mass elsewhere so parse_mcq_logprob_distribution has
        # something real to renormalize over.
        logprobs = {letter: (-0.01 if letter == self.chosen_letter else -8.0) for letter in option_letters}
        return {"top_logprobs": logprobs, "greedy_text": self.chosen_letter}


class TestBuildBeliefSummary:
    def test_never_observed_gives_none_anchor_and_empty_posterior(self):
        store = _empty_store()
        summary = build_belief_summary(store, _question(), t=5.0)
        assert summary.believed_anchor is None
        assert summary.elapsed_hours is None
        assert summary.posterior == {}

    def test_observed_belief_gives_real_summary(self):
        store = _store_with_belief({"shelf": 1.0, "table": 0.0, "OUTSIDE": 0.0}, last_updated_t=2.0)
        summary = build_belief_summary(store, _question(), t=5.0)
        assert summary.believed_anchor == "shelf"
        assert summary.elapsed_hours == pytest.approx(3.0)
        assert summary.posterior  # non-empty, real propagated distribution


class TestRenderBeliefSummary:
    def test_nothing_believed_says_so(self):
        store = _empty_store()
        summary = build_belief_summary(store, _question(), t=5.0)
        text = render_belief_summary(summary)
        assert "nothing currently believed" in text

    def test_believed_anchor_and_age_appear(self):
        store = _store_with_belief({"shelf": 1.0, "table": 0.0, "OUTSIDE": 0.0}, last_updated_t=2.0)
        summary = build_belief_summary(store, _question(), t=5.0)
        text = render_belief_summary(summary)
        assert "shelf" in text
        assert "3.00 hours ago" in text

    def test_posterior_distribution_is_rendered(self):
        store = _store_with_belief({"shelf": 0.6, "table": 0.4, "OUTSIDE": 0.0}, last_updated_t=5.0)
        summary = build_belief_summary(store, _question(), t=5.0)  # elapsed=0, no propagation drift
        text = render_belief_summary(summary)
        assert "shelf: 0.60" in text
        assert "table: 0.40" in text


class TestDecisionPrompt:
    def test_letters_cover_options_plus_resense(self):
        question = _question(options=("shelf", "table", "OUTSIDE"))
        summary = build_belief_summary(_empty_store(), question, t=5.0)
        system, user, letters, resense_letter = decision_prompt(summary, question)
        assert len(letters) == 4  # 3 options + resense
        assert resense_letter == letters[-1]
        assert "Re-check" in user

    def test_no_forecasting_framing_in_system_prompt(self):
        # Standing rule: this module must not encode "the LLM can't
        # forecast" anywhere in the prompt — it's an open comparison.
        from dynamic_home_eqa.llm_prior.fm_decision import DECISION_SYSTEM_PROMPT
        assert "forecast" not in DECISION_SYSTEM_PROMPT.lower()
        assert "can't" not in DECISION_SYSTEM_PROMPT.lower()
        assert "cannot" not in DECISION_SYSTEM_PROMPT.lower()


class TestFMDecisionPolicyAct:
    def test_picks_a_real_answer(self):
        store = _store_with_belief({"shelf": 0.7, "table": 0.2, "OUTSIDE": 0.1}, last_updated_t=5.0)
        client = _FakeClient(_SPEC, chosen_letter="A")  # A = "shelf", options[0]
        cache = EliciationCache(tempfile.mkdtemp())
        policy = FMDecisionPolicy(client, cache)
        decision = policy.act(store, _question(), _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        assert isinstance(decision, Choice)
        assert decision.option_index == 0
        assert decision.confidence > 0.9

    def test_picks_resense_when_candidates_exist(self):
        store = _store_with_belief({"shelf": 0.5, "table": 0.5, "OUTSIDE": 0.0}, last_updated_t=0.0)
        question = _question()
        # resense letter is the 4th (index 3, "D") for a 3-option question
        client = _FakeClient(_SPEC, chosen_letter="D")
        cache = EliciationCache(tempfile.mkdtemp())
        policy = FMDecisionPolicy(client, cache)
        decision = policy.act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        assert isinstance(decision, ResensePlan)
        assert decision.targets

    def test_resense_with_nothing_to_search_falls_back_to_answer(self):
        store = _empty_store()  # nothing believed, nothing to search
        question = _question()
        client = _FakeClient(_SPEC, chosen_letter="D")
        cache = EliciationCache(tempfile.mkdtemp())
        policy = FMDecisionPolicy(client, cache)
        decision = policy.act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        assert decision == Abstain()

    def test_second_call_hits_cache_not_model(self):
        store = _store_with_belief({"shelf": 0.7, "table": 0.2, "OUTSIDE": 0.1}, last_updated_t=5.0)
        question = _question()
        client = _FakeClient(_SPEC, chosen_letter="A")
        cache = EliciationCache(tempfile.mkdtemp())
        policy = FMDecisionPolicy(client, cache)
        policy.act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        n_calls_after_first = len(client.calls)
        policy.act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        assert len(client.calls) == n_calls_after_first
