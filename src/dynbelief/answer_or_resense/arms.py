"""Answer-or-Resense arms. All face the identical query stream, budget, reward.

Confidence sources (the point of the experiment):
  classical  — max posterior of the Dirichlet-smoothed C3g belief fit on the arm's
               OWN resense history. Zero events -> near-uniform -> honestly low
               confidence -> resenses. That honesty is the showcased mechanism.
  llm        — DeepSeek is TOLD the reward structure and remaining budget and
               DECIDES answer-vs-resense itself (behavioral calibration test);
               also emits a verbalized confidence (logged, never used mechanically).
  hybrid     — Tier-3 precision fusion of the classical belief with the LLM's
               per-query belief distribution; SAME threshold family as classical
               (tau swept separately on dev).
  llm_thresh — LLM's ANSWER, but the RESENSE decision made by the classical
               statistical confidence (attribution cell: is it the LLM's answers
               or its decisions that fail?).
  oracle     — replay-cheap upper bound: resenses iff its (classical) answer would
               be wrong, subject to budget.
"""
from __future__ import annotations

import json

import numpy as np

from dynbelief.classical.run import make_arm, _belief
from dynbelief.classical.filter import uniform_belief
from dynbelief.answer_or_resense.env import true_loc

_GAMMA = 1.0          # Dirichlet smoothing pseudo-count
# Cap on observation lines shown in the prompt (most-recent-first retention).
# The original frozen `llm`/`hybrid` runs used 60; the audit found it binds for
# high-resense arms (llm_selfconf: 22/24 households exceeded it), so reruns use
# 200 (above the 70 max achievable at B=5 x 14 days). Rows record the cap used.
OBS_CAP = 200


def _hist_rows(history):
    return [{"day": t // 1440, "t_min": t, "parents": {o: rec}}
            for (t, o, rec) in sorted(history)]


class _Classical:
    """Shared classical belief machinery: refit C3g each day on the arm's own
    history; per-query belief conditions on the object's last self-observation."""

    def reset(self, hh, h, st):
        self.h, self.cands = h, h["cand_set"]
        self.rm = None

    def new_day(self, day, st):
        rows = _hist_rows(st.history)
        self.rm = make_arm("C3g", self.cands, rows)[0] if rows else None

    def observe(self, q, truth, st):
        pass                                    # refit is daily (cheap + stable)

    def belief(self, q, st):
        if self.rm is None:
            return uniform_belief(self.cands)
        ev = [(t, rec) for (t, o, rec) in st.history if o == q.obj and t < q.t]
        lo = (ev[-1][1], ev[-1][0]) if ev else (None, None)
        ep = {"object": q.obj, "t_query": q.t, "last_obs": lo[0], "last_obs_t": lo[1]}
        bel = _belief(self.rm, self.cands, q.obj, q.t, ep, "categorical")
        # Dirichlet shrink toward uniform by the object's OWN evidence count —
        # 0 events => uniform however peaked the class fallback is.
        n_o = len(ev)
        w = n_o / (n_o + _GAMMA)
        K = len(self.cands)
        return {c: w * p + (1 - w) / K for c, p in bel.items()}

    @staticmethod
    def top(bel):
        p = max(bel, key=bel.get)
        return p, bel[p]


class ClassicalThreshold(_Classical):
    """RESENSE when max-posterior confidence < tau_c."""
    name = "classical"

    def __init__(self, tau):
        self.tau = tau

    def decide(self, q, st, r_resense, wrong):
        bel = self.belief(q, st)
        pred, conf = self.top(bel)
        action = "resense" if (conf < self.tau and st.budget_left > 0) else "answer"
        return {"action": action, "pred": pred, "conf": conf}


class Oracle(_Classical):
    """Upper bound: resense iff the answer would be wrong (replay knowledge)."""
    name = "oracle"

    def decide(self, q, st, r_resense, wrong):
        bel = self.belief(q, st)
        pred, conf = self.top(bel)
        would_be_wrong = pred != true_loc(self.h, q.obj, q.t)
        action = "resense" if (would_be_wrong and st.budget_left > 0) else "answer"
        return {"action": action, "pred": pred, "conf": conf}


AOR_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["answer", "resense"]},
        "predictions": {"type": "array", "items": {"type": "object", "properties": {
            "receptacle": {"type": "string"}, "p": {"type": "number"}},
            "required": ["receptacle", "p"]}},
        "confidence": {"type": "number"}},
    "required": ["action", "predictions", "confidence"]}

# ≤3 dev prompt variants; frozen after dev. All state the rewards + budget (an
# informed decision is the fair test).
PROMPTS = {
    "v1": ("You are an embodied home agent answering object-location queries under a "
           "sensing budget. Rewards: a correct answer scores +{one}, a wrong answer "
           "scores {wrong}, choosing RESENSE scores {r} and reveals the object's true "
           "location (added to your observations — your ONLY way to learn this home). "
           "You have {b} resenses left today. Decide: if you are confident, ANSWER; if "
           "not, RESENSE. Give up to 3 candidate receptacles with probabilities from "
           "the provided list (or 'elsewhere'), and your confidence 0-1 that your top "
           "answer is correct."),
    "v2": ("Same task, expected-value framing: answer scores +{one} with probability "
           "equal to your true accuracy, {wrong} otherwise; resense guarantees {r} now "
           "AND buys information that raises future accuracy. {b} resenses left today. "
           "Choose the action with higher long-run value. Give up to 3 candidates with "
           "probabilities and your confidence 0-1."),
    "v3": ("You answer object-location queries; admitting uncertainty is rewarded. "
           "Correct +{one}; wrong {wrong}; RESENSE {r} plus the true location is added "
           "to your observations. {b} resenses left today. Only answer when your "
           "confidence beats the resense value; otherwise resense. Up to 3 candidates "
           "with probabilities, plus confidence 0-1."),
}


class LLMArm:
    """DeepSeek decides answer-vs-resense itself, informed of rewards + budget."""
    name = "llm"

    def __init__(self, client, prompt_key="v1"):
        self.client, self.pk = client, prompt_key

    def reset(self, hh, h, st):
        self.h, self.cands = h, h["cand_set"]

    def new_day(self, day, st):
        pass

    def observe(self, q, truth, st):
        pass

    def _obs_text(self, st):
        if not st.history:
            return "(you have made no observations of this home yet)"
        lines = [f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — {o} seen at {rec}"
                 for (t, o, rec) in sorted(st.history)[-OBS_CAP:]]
        return "Your observations so far (from your own resensing):\n" + "\n".join(lines)

    def _ask(self, q, st, r_resense, wrong):
        sys = PROMPTS[self.pk].format(one=1, wrong=wrong, r=r_resense, b=st.budget_left)
        clk = f"{(q.t % 1440)//60:02d}:{(q.t % 1440) % 60:02d}"
        user = (f"{self._obs_text(st)}\n\nCandidate receptacles: "
                f"{', '.join(self.h['cands'])}, elsewhere.\n\n"
                f"Query: on day {q.t//1440} at {clk}, where is the {q.obj}?"
                + ("" if st.budget_left > 0 else "\n(No resenses left — you must answer.)"))
        try:
            out = json.loads(self.client.generate(sys, user, AOR_SCHEMA, seed=7,
                                                  temperature=0.0, max_tokens=512))
            preds = [p for p in out.get("predictions", []) if p.get("receptacle")]
            top = preds[0]["receptacle"] if preds else "elsewhere"
            bel = {c: 0.0 for c in self.cands}
            for p in preds:
                if p["receptacle"] in bel:
                    bel[p["receptacle"]] += max(0.0, float(p.get("p", 0)))
            z = sum(bel.values())
            bel = ({c: v / z for c, v in bel.items()} if z > 0
                   else uniform_belief(self.cands))
            return (out.get("action", "answer"), top, bel,
                    float(out.get("confidence", 0.5)))
        except Exception:
            return "answer", "elsewhere", uniform_belief(self.cands), 0.0

    def decide(self, q, st, r_resense, wrong):
        action, top, bel, vconf = self._ask(q, st, r_resense, wrong)
        if top not in set(self.cands):
            top = max(bel, key=bel.get)
        return {"action": action if st.budget_left > 0 else "answer",
                "pred": top, "conf": max(bel.values()), "verbal_conf": vconf,
                "llm_belief": bel}


class HybridArm(_Classical):
    """Tier-3 precision fusion of classical belief with the LLM's per-query
    belief; threshold decision on the FUSED confidence. kappa = alpha* (6.07,
    dev-calibrated); n = the object's own resense count."""
    name = "hybrid"

    def __init__(self, client, tau, alpha_star=6.07, prompt_key="v1"):
        self.llm = LLMArm(client, prompt_key)
        self.tau, self.alpha = tau, alpha_star

    def reset(self, hh, h, st):
        super().reset(hh, h, st)
        self.llm.reset(hh, h, st)

    def decide(self, q, st, r_resense, wrong):
        stat = self.belief(q, st)
        _, _, lbel, vconf = self.llm._ask(q, st, r_resense, wrong)
        n_o = len([1 for (t, o, _rec) in st.history if o == q.obj and t < q.t])
        w = self.alpha / (self.alpha + n_o)          # prior weight fades with data
        fused = {c: w * lbel.get(c, 0.0) + (1 - w) * stat[c] for c in stat}
        z = sum(fused.values())
        fused = {c: v / z for c, v in fused.items()}
        pred, conf = self.top(fused)
        action = "resense" if (conf < self.tau and st.budget_left > 0) else "answer"
        return {"action": action, "pred": pred, "conf": conf, "verbal_conf": vconf}


class LLMThreshold(_Classical):
    """Attribution cell (arm 5): the LLM's ANSWER, the classical confidence's
    DECISION. Separates bad answers from bad decisions."""
    name = "llm_thresh"

    def __init__(self, client, tau, prompt_key="v1"):
        self.llm = LLMArm(client, prompt_key)
        self.tau = tau

    def reset(self, hh, h, st):
        super().reset(hh, h, st)
        self.llm.reset(hh, h, st)

    def decide(self, q, st, r_resense, wrong):
        stat = self.belief(q, st)
        _, sconf = self.top(stat)                    # statistical confidence
        _, top, lbel, vconf = self.llm._ask(q, st, r_resense, wrong)
        if top not in set(self.cands):
            top = max(lbel, key=lbel.get)
        action = "resense" if (sconf < self.tau and st.budget_left > 0) else "answer"
        return {"action": action, "pred": top, "conf": sconf, "verbal_conf": vconf}
