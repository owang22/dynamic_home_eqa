"""Two-Capacities Section 2 arms.

R1  llm_selfconf — LLM answers + the LLM's OWN verbalized-confidence ranking,
    thresholded at tau. tau is chosen on dev so the realized resense rate MATCHES
    the arm's error rate (recalibrate the LEVEL, keep the ranking). This is the
    arm P4 should have been; replaces the confounded llm_thresh.

R2  evidence-integration prompt variants (attack Capacity B directly). Change
    ONLY how self-gathered observations are presented:
      v1_recency  — most-recent-first, each line tagged "you observed this
                    yourself on day d"; never summarized away.
      v1_pinned   — a protected EVIDENCE block holding all self-gathered
                    observations verbatim (tests context-curation loss).
      v1_explicit — adds "your own past observations override general
                    expectations about where objects usually are".
"""
from __future__ import annotations

import json

from dynbelief.classical.filter import uniform_belief
from dynbelief.answer_or_resense.arms import LLMArm, AOR_SCHEMA, PROMPTS


class LLMSelfConf(LLMArm):
    """R1: decision = (verbalized confidence < tau) -> resense. The LLM's own
    ranking (AUROC 0.75-0.81) with a recalibrated operating point."""
    name = "llm_selfconf"

    def __init__(self, client, tau, prompt_key="v1"):
        super().__init__(client, prompt_key)
        self.tau = tau

    def decide(self, q, st, r_resense, wrong):
        _action, top, bel, vconf = self._ask(q, st, r_resense, wrong)
        if top not in set(self.cands):
            top = max(bel, key=bel.get)
        v = vconf if 0 <= vconf <= 1 else 0.5          # off-scale -> neutral
        action = "resense" if (v < self.tau and st.budget_left > 0) else "answer"
        return {"action": action, "pred": top, "conf": max(bel.values()),
                "verbal_conf": vconf}


# ── R2 prompt variants: presentation of self-gathered evidence ───────────────

_EXPLICIT_SUFFIX = (" IMPORTANT: your own past observations of THIS home override "
                    "general expectations about where objects usually are — if you "
                    "have seen an object somewhere in this home, trust that over "
                    "your prior.")


class LLMVariant(LLMArm):
    """R2: same decision logic as the llm arm; only the observation presentation
    (and for v1_explicit, one system-prompt sentence) changes."""

    def __init__(self, client, variant):
        super().__init__(client, "v1")
        self.variant = variant
        self.name = f"llm_{variant}"

    def _obs_text(self, st):
        if not st.history:
            return "(you have made no observations of this home yet)"
        ev = sorted(st.history)
        if self.variant == "v1_recency":
            lines = [f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — "
                     f"{o} seen at {rec} (you observed this yourself on day {t//1440})"
                     for (t, o, rec) in reversed(ev)]
            return ("Your own observations, MOST RECENT FIRST (never forget these):\n"
                    + "\n".join(lines))
        if self.variant == "v1_pinned":
            lines = [f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — "
                     f"{o} was at {rec}" for (t, o, rec) in ev]
            return ("=== PROTECTED EVIDENCE (verbatim log of every observation you "
                    "have made in this home; treat as ground truth) ===\n"
                    + "\n".join(lines) + "\n=== END EVIDENCE ===")
        # v1_explicit: same listing as v1
        lines = [f"  Day {t//1440}, {(t%1440)//60:02d}:{(t%1440)%60:02d} — {o} seen at {rec}"
                 for (t, o, rec) in ev[-60:]]
        return "Your observations so far (from your own resensing):\n" + "\n".join(lines)

    def _ask(self, q, st, r_resense, wrong):
        sys = PROMPTS["v1"].format(one=1, wrong=wrong, r=r_resense, b=st.budget_left)
        if self.variant == "v1_explicit":
            sys += _EXPLICIT_SUFFIX
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
