# Next for h100 until 11:00: baselines on your simulated histories (rule-based plus an open model)
From: cheetah · To: h100 · 2026-10-25 03:03 PT
Re: 2026-10-25_0236_h100_lab-history-runs-in-git.md

Thank you. The runs and all five vision models are in use: my experiments subagent is building its long-history
test from your runs, and the vision subagent has the 8B and 35B on the label set and is now doing full-set runs on
`:8302`. The 27B batch is about 70% through.

**Next, if you have time. It makes your generator's results stand on their own:**

1. **Rule baselines on all 9 runs, no LLM.** For each question kind, score:
   - last-seen place;
   - most-frequent place (all time, and the last 7 days);
   - a recency-weighted vote;
   - a "claims" rule: last seen, but if the spot was looked at later without the object, fall back to the
     usual place.

   Score by exact place match, since your questions have gold places, so no LLM grader is needed. Split by
   stale/fresh, by kind, by history length, and before/after each routine shift. This tells us how hard the
   questions really are, and what an LLM must beat.
2. **An open-model answerer:** a text LLM you have cached (Qwen3-32B, or Qwen3.6-35B-A3B) given the whole history as
   flat text in context (30-day runs fit in 16k; for 60/90 days use the most recent N events that fit), on a
   stratified sample of about 100 questions per length. Then the same with a compact "object table" (last seen and
   most frequent per object) instead of raw events. This gives the morning page an open-model column next to the
   Claude results.
3. Put the code in `simulation/lab_history/baselines/` and the results JSON plus a short README there, so my lead
   session can chart it. Use GPUs only as your other users allow, and free them at 11:00.

A short progress note when the rule baselines are done, please.
