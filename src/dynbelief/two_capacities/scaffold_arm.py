"""The decisive control for the cross-experiment discrepancy.

The reflect experiments (where the LLM BEAT classical) gave the model a curated
MEMORY built by a nightly reflection call — persona hypotheses with probabilities
plus selected diagnostic evidence — and a routine-aware query prompt ("Day 0 is
Monday ... weigh your hypotheses ... consider the queried weekday and time").
The answer-or-resense `llm` arm gave it a RAW observation log and a
budget-focused prompt with no persona step and no routine guidance.

That is the only surviving explanation for the reversal (recency, classical data
density, and query-hour alignment were each tested and falsified). This arm
restores the reflect scaffold INSIDE the resense loop so the two experiments
differ only in the sensing protocol:

  llm_scaffold — nightly reflection over the arm's OWN self-gathered observations
                 (memory.reflect_day, the frozen reflect prompt), and the query
                 prompt carries the persona memory + routine guidance + the
                 answer/resense decision.

If its override rate falls and its follow-fidelity stops decaying, the finding is
"the reflection scaffold is what makes LLM evidence-integration work", not "LLMs
cannot integrate self-gathered evidence".
"""
from __future__ import annotations

import json

from dynbelief.classical.filter import uniform_belief
from dynbelief.answer_or_resense.arms import LLMArm, AOR_SCHEMA
from dynbelief.reflect import memory as M

_SYS = (
    "You are an embodied home agent answering object-location queries about a household "
    "using your MEMORY file: persona hypotheses with probabilities plus selected evidence. "
    "Day 0 is a Monday; days 5-6 are the weekend; the weekly pattern repeats. Weigh your "
    "hypotheses by their probabilities, consider the queried weekday and time of day, and "
    "predict where the object is.\n"
    "You are also under a SENSING BUDGET. A correct answer scores +{one}; a wrong answer "
    "scores {wrong}; choosing RESENSE scores {r} and reveals the object's true location, "
    "which is added to your observations (your ONLY way to learn this home). You have {b} "
    "resenses left today. If your memory makes you confident, ANSWER; otherwise RESENSE.\n"
    "Give up to 3 candidate receptacles with probabilities, most likely first, using ONLY "
    "receptacles from the provided candidate list (or 'elsewhere'), plus your confidence "
    "0-1 that your top answer is correct."
)


class LLMScaffold(LLMArm):
    """Reflect-style persona memory, rebuilt nightly from self-gathered evidence."""
    name = "llm_scaffold"

    def __init__(self, client, prompt_key="v1"):
        super().__init__(client, prompt_key)
        self.mem = dict(M.EMPTY_MEM)
        self.md = M.render_md(M.EMPTY_MEM, -1)
        self.reflect_calls = 0

    def reset(self, hh, h, st):
        super().reset(hh, h, st)
        self.mem = dict(M.EMPTY_MEM)
        self.md = M.render_md(M.EMPTY_MEM, -1)
        self.reflect_calls = 0

    def new_day(self, day, st):
        """Nightly reflection over YESTERDAY's self-gathered observations (the same
        call the reflect experiments used, on the resense log instead of the
        ambient stream)."""
        if day == 0 or not st.history:
            return
        prev = [(t, o, rec) for (t, o, rec) in st.history if t // 1440 == day - 1]
        if not prev:
            return
        lines = [f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — {o} seen at {rec}"
                 for (t, o, rec) in sorted(prev)]
        new = M.reflect_day(self.client, self.md, day - 1, lines)
        self.reflect_calls += 1
        if new is not None:
            self.mem = new
        self.md = M.render_md(self.mem, day - 1)

    def _obs_text(self, st):
        """Memory file FIRST (the reflect scaffold), then the raw log for grounding."""
        raw = super()._obs_text(st)
        return f"YOUR MEMORY:\n{self.md}\n\n{raw}"

    def _ask(self, q, st, r_resense, wrong):
        sys = _SYS.format(one=1, wrong=wrong, r=r_resense, b=st.budget_left)
        clk = f"{(q.t % 1440)//60:02d}:{(q.t % 1440) % 60:02d}"
        user = (f"{self._obs_text(st)}\n\nCandidate receptacles: "
                f"{', '.join(self.h['cands'])}, elsewhere.\n\n"
                f"Query: on day {q.t//1440} ({M.WEEKDAYS[(q.t//1440) % 7]}) at {clk}, "
                f"where is the {q.obj}?"
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


class ScaffoldFusion:
    """scaffold + Tier-3 precision fusion.

    The best LLM implementation (persona memory rebuilt nightly from its own
    resenses) fused with the classical C3g belief fit on the SAME self-gathered
    observations, weighted by precision: w_prior = alpha*/(alpha* + n_obj), so the
    persona-conditioned belief leads while an object is data-poor and fades as its
    own evidence accumulates. The resense decision thresholds the FUSED confidence.

    alpha* = 6.07 (dev-calibrated in reflect_dag; not re-tuned here); tau swept on
    the dev bank only.
    """
    name = "scaffold_fusion"

    def __init__(self, client, tau, alpha_star=6.07):
        from dynbelief.answer_or_resense.arms import _Classical
        self._c = _Classical()
        self.llm = LLMScaffold(client)
        self.tau, self.alpha = tau, alpha_star

    def reset(self, hh, h, st):
        self._c.reset(hh, h, st)
        self.llm.reset(hh, h, st)
        self.cands = h["cand_set"]

    def new_day(self, day, st):
        self._c.new_day(day, st)        # refit C3g on self-gathered observations
        self.llm.new_day(day, st)       # nightly persona reflection

    def observe(self, q, truth, st):
        pass

    def decide(self, q, st, r_resense, wrong):
        stat = self._c.belief(q, st)
        _a, top, lbel, vconf = self.llm._ask(q, st, r_resense, wrong)
        n_o = len([1 for (t, o, _r) in st.history if o == q.obj and t < q.t])
        w = self.alpha / (self.alpha + n_o)
        fused = {c: w * lbel.get(c, 0.0) + (1 - w) * stat[c] for c in stat}
        z = sum(fused.values())
        fused = {c: v / z for c, v in fused.items()} if z > 0 else stat
        pred = max(fused, key=fused.get)
        conf = fused[pred]
        action = "resense" if (conf < self.tau and st.budget_left > 0) else "answer"
        return {"action": action, "pred": pred, "conf": conf, "verbal_conf": vconf}
