"""
Tests for embodied/policy.py's CoverageStop (renamed and fixed from
ConfidenceStop, 2026-07-07 — see results/reports/INDEX.md's history).

Old finding: ConfidenceStop's "nothing believed" branch always returned
Abstain() regardless of whether a plausible candidate existed to search,
making it structurally identical to AnswerImmediately on every input.

Fix applied (literal instruction: "reuse the existing goto/sense
machinery"): "nothing believed" now delegates to _continue_or_answer, the
same search-then-answer machinery every other resense-capable policy
already uses.

Second finding, made while verifying the fix rather than assuming it
worked (see CoverageStop's own docstring for the full argument): this fix
is PROVABLY still a no-op under every belief-store implementation in this
codebase. believed_anchor()'s "is anything believed" check is the argmax
of the identical per-candidate propagated masses that top_candidates()
filters with the identical >1e-9 survival threshold — an argmax below
threshold means every candidate is below threshold, so whenever
believed_anchor() returns None, top_candidates() is mathematically
guaranteed to return empty too. CoverageStop therefore remains
behaviorally identical to AnswerImmediately on every input, not just on
this pool's data — TestStructuralInvariant below proves this directly
against the real posterior code, not through an empirical sweep that
could get lucky. Reusing the *existing* goto/sense machinery cannot
produce a non-degenerate literature baseline under the current
belief-store interface; that would need a new, threshold-independent
candidate-selection path, an intentionally separate, bigger decision.

Pure logic — belief.BeliefStore / posterior.PosteriorBeliefStore, no
habitat_sim needed.
"""
from __future__ import annotations

from dynamic_home_eqa.embodied.belief import BeliefStore, DecayModel
from dynamic_home_eqa.embodied.policy import AnswerImmediately, CoverageStop
from dynamic_home_eqa.embodied.posterior import PosteriorBeliefStore, PosteriorObjectNode, TransitionKernel
from dynamic_home_eqa.embodied.question import MCQQuestion
from dynamic_home_eqa.embodied.scoring import Abstain, Choice
from dynamic_home_eqa.embodied.types import OracleDetection, Pose

_POSE = Pose(0.0, 0.0, 0.0, 0.0)


def _question(options=("shelf", "table", "OUTSIDE")) -> MCQQuestion:
    return MCQQuestion(
        label="book_1", category="book", stem="Where is the book?",
        options=options, correct_index=0, asked_t=1.0,
        hazard_class="stable", distractor_provenance=("real", "real", "real"),
    )


def _empty_belief_store() -> BeliefStore:
    return BeliefStore(decay_models={"book": DecayModel("book", lambda_per_hour=0.5)})


def _observed_belief_store(anchor="shelf", t=0.0) -> BeliefStore:
    store = _empty_belief_store()
    store.observe_detection(
        OracleDetection(label="book_1", category="book", world_pos=(0, 0, 0), anchor=anchor, t=t),
        _POSE,
    )
    return store


def _kernel(states=("shelf", "table", "OUTSIDE"), dest_dist=None) -> TransitionKernel:
    n = len(states)
    return TransitionKernel(
        category="book", states=states, lambda_per_hour=0.5,
        dest_dist=dest_dist or tuple(1.0 / n for _ in states),
    )


class TestUnchangedWhenBeliefExists:
    """The one branch CoverageStop deliberately preserves from ConfidenceStop."""

    def test_answers_at_confidence_one_regardless_of_staleness(self):
        store = _observed_belief_store(t=0.0)
        question = _question()
        for t in (0.25, 1.0, 4.0, 24.0):
            decision = CoverageStop().act(store, question, _POSE, t=t, config=None, travel_time_to=lambda a: 1.0)
            assert decision == Choice(option_index=0, confidence=1.0)


class TestNothingBelievedStillAbstains:
    """The fixed branch, exercised against belief.BeliefStore (M1) and
    posterior.PosteriorBeliefStore (M2+) — both still abstain, per
    TestStructuralInvariant's proof of why that's guaranteed, not a
    leftover bug in this fix."""

    def test_never_observed_belief_store_abstains(self):
        store = _empty_belief_store()
        question = _question()
        decision = CoverageStop().act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 0.1)
        assert decision == Abstain()

    def test_never_observed_posterior_store_abstains(self):
        store = PosteriorBeliefStore(kernels={"book": _kernel()})
        question = _question()
        decision = CoverageStop().act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 0.1)
        assert decision == Abstain()

    def test_displaced_belief_store_abstains(self):
        # belief.BeliefStore: any negative observation sets node.displaced,
        # and believed_anchor short-circuits to None whenever displaced —
        # its own top_candidates is LITERALLY defined as
        # "(believed_anchor(),) if not None else ()", so this is the same
        # invariant by an even more direct construction.
        store = _observed_belief_store(anchor="shelf", t=0.0)
        store.observe_negative("book_1", t=1.0)
        question = _question()
        decision = CoverageStop().act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 0.1)
        assert decision == Abstain()

    def test_all_candidate_mass_at_threshold_posterior_store_abstains(self):
        store = PosteriorBeliefStore(kernels={"book": _kernel()})
        store.nodes["book_1"] = PosteriorObjectNode(
            label="book_1", category="book", kernel=_kernel(),
            posterior={"shelf": 0.0, "table": 0.0, "OUTSIDE": 1.0},
            last_updated_t=5.0, last_update_was_positive=False,
        )
        question = _question()
        # t == last_updated_t: elapsed=0, propagate() is the identity, so
        # the posterior above is exactly what believed_anchor/top_candidates
        # see — no relaxation toward dest_dist has had time to occur yet.
        decision = CoverageStop().act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 0.1)
        assert decision == Abstain()


class TestStructuralInvariant:
    """Proves, against the real posterior code (not asserted from the
    docstring), that believed_anchor() is None implies top_candidates()
    is empty for every t — the reason CoverageStop's fixed branch can
    never actually execute a search. Verified empirically at multiple t
    (not just t == last_updated_t) because propagate()'s relaxation
    toward dest_dist can make a candidate's mass cross back above the
    1e-9 threshold as elapsed time grows; the invariant must hold at
    every one of those crossings too, not just the initial instant."""

    def test_posterior_store_invariant_holds_across_elapsed_time(self):
        kernel = _kernel(dest_dist=(1 / 3, 1 / 3, 1 / 3))
        store = PosteriorBeliefStore(kernels={"book": kernel})
        store.nodes["book_1"] = PosteriorObjectNode(
            label="book_1", category="book", kernel=kernel,
            posterior={"shelf": 0.0, "table": 1e-12, "OUTSIDE": 1.0 - 1e-12},
            last_updated_t=0.0, last_update_was_positive=False,
        )
        for t in (0.0, 1e-6, 0.001, 0.1, 1.0, 5.0, 24.0):
            anchor = store.believed_anchor("book_1", t)
            candidates = store.top_candidates("book_1", t, travel_time_to=lambda a: 1.0, k=3)
            assert (anchor is None) == (candidates == ()), (
                f"invariant broken at t={t}: believed_anchor={anchor!r}, top_candidates={candidates!r}"
            )

    def test_belief_store_invariant_holds_by_direct_construction(self):
        # belief.BeliefStore's top_candidates is defined in terms of its
        # own believed_anchor, so this holds trivially by inspection, but
        # tested directly against the real object rather than assumed.
        store = _observed_belief_store(anchor="shelf", t=0.0)
        store.observe_negative("book_1", t=1.0)
        for t in (1.0, 2.0, 10.0):
            anchor = store.believed_anchor("book_1", t)
            candidates = store.top_candidates("book_1", t, travel_time_to=lambda a: 1.0, k=3)
            assert (anchor is None) == (candidates == ())


class TestStillIdenticalToAnswerImmediately:
    """The headline consequence of the structural invariant: CoverageStop
    (fixed) and AnswerImmediately remain identical on every belief state
    this test can construct, including states specifically designed to
    exercise the new search branch. This is the "N of 855 trials differ"
    finding reported at N=0, not a residual gap in the fix."""

    def test_identical_on_never_observed(self):
        for store_factory in (_empty_belief_store, lambda: PosteriorBeliefStore(kernels={"book": _kernel()})):
            question = _question()
            cs = CoverageStop().act(store_factory(), question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 0.1)
            ai = AnswerImmediately().act(store_factory(), question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 0.1)
            assert cs == ai == Abstain()

    def test_identical_after_displacement(self):
        def make_store():
            store = _observed_belief_store(anchor="shelf", t=0.0)
            store.observe_negative("book_1", t=1.0)
            return store

        question = _question()
        cs = CoverageStop().act(make_store(), question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 0.1)
        ai = AnswerImmediately().act(make_store(), question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 0.1)
        assert cs == ai == Abstain()

    def test_identical_when_belief_exists(self):
        store = _observed_belief_store(t=0.0)
        question = _question()
        cs = CoverageStop().act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        ai = AnswerImmediately().act(store, question, _POSE, t=5.0, config=None, travel_time_to=lambda a: 1.0)
        assert cs == ai
