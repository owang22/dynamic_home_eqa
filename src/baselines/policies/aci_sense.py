"""Policy: conformal-triggered sensing with an adaptively updated alpha.

Static split-conformal calibration promises coverage on exchangeable
data; a household drifts. Adaptive conformal inference (ACI) keeps the
miscoverage level itself online:

    alpha_{t+1} = alpha_t + gamma * (alpha_target - err_t)

where ``err_t = 1`` if the truth was outside the prediction set. The
policy below is :class:`~baselines.policies.conformal_sense.ConformalSense`
with ``qhat`` recomputed from the calibration scores at the current
``alpha_t`` (one global quantile; ``alpha_0 = alpha_target``, so the
first question uses the static calibration exactly), and a
:meth:`feedback` hook the driver calls after each question.

Which set ``err_t`` refers to: the set formed at the question's FIRST
decision, from memory, before any sense. That is the set the calibration
promises coverage for; a set formed after a sense that returned the
object contains it trivially and carries no information. The driver
learns the truth two ways, and each is a feedback mode:

* ``oracle`` -- the harness's ground truth, every question. Diagnostic
  only: no deployed robot has it. Labeled as such in every output.
* ``sensed`` -- only questions whose own senses revealed the truth: a
  sense found the object, or every sensable receptacle was sensed
  empty this question (which confirms OUT_OF_HOUSE under noiseless
  sensing). Deployable; updates less often.

The policy never sees the truth; the driver computes ``err_t`` from the
record and the policy's :attr:`first_set` and calls :meth:`feedback`.
``alpha_t`` is not clipped in the recursion (as in Gibbs & Candes 2021)
but is clipped to ``[0, 1)`` when the quantile is looked up: at or above
1 the set is empty (sense the argmax), at or below 0 it is vacuous.
All times are seconds since episode start.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from baselines.conformal.calibration import (AgeFn, conformal_qhat,
                                             prediction_set)
from baselines.policies.base import DecisionPolicy
from baselines.types import (Action, AnswerNow, EpisodeContext, Prediction,
                             Question, Sense, SenseResult)

FEEDBACK_MODES = ("oracle", "sensed")


class ACISense(DecisionPolicy):
    """ConformalSense whose alpha follows the ACI recursion."""

    def __init__(self, rng: random.Random, scores: Sequence[float],
                 alpha_target: float, gamma: float, age_fn: AgeFn,
                 feedback_mode: str) -> None:
        if not 0.0 < alpha_target < 1.0:
            raise ValueError(f"ACISense: alpha_target {alpha_target} outside (0, 1)")
        if gamma < 0.0:
            raise ValueError(f"ACISense: gamma {gamma} must be non-negative "
                             f"(0 = the static reference)")
        if feedback_mode not in FEEDBACK_MODES:
            raise ValueError(f"ACISense: feedback_mode {feedback_mode!r} "
                             f"not in {FEEDBACK_MODES}")
        self._rng = rng
        self._scores = sorted(float(s) for s in scores)
        self._alpha_target = float(alpha_target)
        self._gamma = float(gamma)
        self._age_fn = age_fn
        self._feedback_mode = feedback_mode
        self.alpha = float(alpha_target)
        self.n_updates = 0
        self.first_set: Set[str] = set()
        self.first_qhat = 1.0
        self.first_alpha = float(alpha_target)
        self._receptacles: Tuple[str, ...] = ()
        self._all_receptacles: Tuple[str, ...] = ()
        self._question_id: Optional[str] = None
        self._tried: Set[str] = set()

    @property
    def name(self) -> str:
        return (f"ACISense(alpha={self._alpha_target:g},gamma={self._gamma:g},"
                f"{self._feedback_mode})")

    @property
    def feedback_mode(self) -> str:
        return self._feedback_mode

    @property
    def alpha_target(self) -> float:
        return self._alpha_target

    @property
    def gamma(self) -> float:
        return self._gamma

    def qhat(self) -> float:
        """The quantile at the current alpha, clipped: at or above 1 the
        set is empty (qhat 0), at or below 0 it is vacuous (qhat 1)."""
        if self.alpha >= 1.0:
            return 0.0
        if self.alpha <= 0.0:
            return 1.0
        return conformal_qhat(self._scores, self.alpha)

    def reset(self, context: EpisodeContext) -> None:
        self._receptacles = context.sensable_receptacle_ids
        self._all_receptacles = context.receptacle_ids
        self._question_id = None
        self._tried = set()
        self.alpha = self._alpha_target
        self.n_updates = 0

    def feedback(self, err: bool) -> None:
        """One ACI step; the driver calls it after a question resolves,
        only when its feedback mode allows."""
        self.alpha += self._gamma * (self._alpha_target - float(err))
        self.n_updates += 1

    def decide(self, question: Question, prediction: Prediction,
               budget_remaining: float, t: int,
               last_sense: Optional[SenseResult] = None) -> Action:
        qhat = self.qhat()
        members = prediction_set(prediction.distribution, qhat,
                                 self._all_receptacles)
        if self._question_id != question.question_id:
            self._question_id = question.question_id
            self._tried = set()
            self.first_set = set(members)
            self.first_qhat = qhat
            self.first_alpha = self.alpha
        if last_sense is not None and question.object_id in last_sense.contents:
            return AnswerNow()
        if len(members) == 1:
            return AnswerNow()
        if budget_remaining <= 0:
            return AnswerNow()
        untried = [r for r in self._receptacles if r not in self._tried]
        if not untried:
            return AnswerNow()
        if not members:
            if prediction.argmax not in untried:
                return AnswerNow()
            self._tried.add(prediction.argmax)
            return Sense(receptacle_id=prediction.argmax)
        choice = self._best_untried(prediction, untried)
        self._tried.add(choice)
        return Sense(receptacle_id=choice)

    def _best_untried(self, prediction: Prediction,
                      untried: List[str]) -> str:
        top = max(prediction.distribution.get(r, 0.0) for r in untried)
        tied = [r for r in untried
                if prediction.distribution.get(r, 0.0) == top]
        return tied[0] if len(tied) == 1 else self._rng.choice(tied)


def truth_revealed(actions: Sequence[Dict[str, Any]], object_id: str,
                   sensable: Sequence[str]) -> bool:
    """Whether a question's own senses revealed the truth: the object
    turned up in a sense, or every sensable receptacle was sensed empty
    of it (noiseless sensing: it is out of the house)."""
    sensed_empty: Set[str] = set()
    for action in actions:
        if action.get("type") != "sense":
            continue
        contents = action.get("contents", ())
        if object_id in contents:
            return True
        sensed_empty.add(str(action["receptacle_id"]))
    return bool(sensable) and sensed_empty >= set(sensable)


