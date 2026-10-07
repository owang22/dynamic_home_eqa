# LLM-agent memory / reasoning / planning shortlist — 2026-09-21 20:40

Citations checked against arXiv/venue just now (WebSearch), not from memory alone. All runnable as "where is X" agents
on our banks against the local Qwen3.8-27B (:8300 only); "what it needs from the log" = the extra machinery beyond the
sighting stream every classical/LLM agent already gets.

## Memory constructions

1. **Rolling buffer** (baseline) — the object's raw sighting history in the prompt, newest N. No paper, the null
   hypothesis every memory method is measured against. Needs: nothing extra (already `naive`/`recent` in llm.py).
2. **Retrieval memory** — Mem0 (Chhikara et al., *Mem0: Building production-ready AI agents with scalable long-term
   memory*, arXiv:2504.19413, ECAI 2025) and A-Mem (Xu et al., *A-Mem: Agentic Memory for LLM Agents*,
   arXiv:2502.12110, NeurIPS 2025): store observations as retrievable units, pull the relevant ones at query time
   instead of dumping everything. Here, "relevant" = this object's own sightings AND sightings from the SAME
   time-of-day bin across other days AND the most recent days — the structured analogue of semantic retrieval since
   our observations are (time, receptacle) tuples, not free text. Needs: a retrieval query built from (object, query
   time) at question time; no new nightly step.
3. **Reflection memory** — Generative Agents (Park et al., *Generative Agents: Interactive Simulacra of Human
   Behavior*, UIST 2023, arXiv:2304.03442: periodic reflections synthesized from raw observations) and Reflexion
   (Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning*, NeurIPS 2023, arXiv:2303.11366:
   verbal self-critique from task feedback, kept as episodic memory). Distinct from the workshop session's `routine7`
   (a nightly table rewritten from the raw sighting timeline) only if it is driven by ERRORS specifically: nightly,
   show the model which of today's found-it feedback corrected a WRONG answer, and have it write a short note on
   what it got wrong and why — Reflexion's actual mechanism, not Generative Agents' periodic summarization (which
   `routine7` already covers). Needs: the previous day's per-question correctness, already in `records` inside
   `run_arm` — no new evidence, just a new nightly prompt.
4. **Long context** — no single canonical paper (this is "does scale substitute for a memory architecture", tested
   informally across long-context papers, e.g. Liu et al. *Lost in the Middle*, TACL 2024, arXiv:2307.03172, on
   whether models actually use everything in a long prompt); the natural control nobody on this project has run.
   Whole per-object sighting history unclipped, plus the full household movement log (every object's moves), in one
   prompt. Needs: a token-count check against Qwen3.8-27B's context (we quoted ~98k earlier) — measured below.
5. *(not shortlisted, noted for completeness)* MemGPT (Packer et al., *MemGPT: Towards LLMs as Operating Systems*,
   arXiv:2310.08560, Oct 2023) — OS-style paging between a fixed "main context" and unlimited "external context" with
   the model issuing its own memory-management function calls. Close in spirit to the rolling buffer + retrieval
   combination above, but the self-paging control loop is a large build for tonight; skipped in favor of a fourth
   slot on the uncertainty side.

## Planning / uncertainty (layered on top of a memory construction, not a memory construction itself)

6. **KnowNo** (Ren et al., *Robots That Ask For Help: Uncertainty Alignment for Large Language Model Planners*, CoRL
   2023, arXiv:2307.01928) and **Explore until Confident** (Ren et al., arXiv:2403.15941, 2024 — already used
   in-house today for the classical honest-sets agents): conformal prediction over an LLM's own answer distribution,
   building a calibrated ANSWER SET (not one point guess) with a coverage guarantee, asking a human when the set is
   large. Needs: the multiple-choice-with-logprobs call already built for today's confidence-channel test
   (`uq_llm.py`), reused to build a set instead of reading one letter's probability.
7. **Confidence channels** (verbalized — Tian et al. 2023; first-token logprob — Kadavath et al. 2022 / the KnowNo
   multiple-choice form; 5-sample agreement / semantic-entropy-style — Farquhar et al., *Detecting hallucinations in
   large language models using semantic entropy*, Nature 2024, and Lyu et al. 2024 sample-consistency calibration):
   three cheap, already-implemented (in `uq_llm.py`, run once today on the naive buffer) confidence signals to put on
   whichever memory construction gets the calibration study.

## The four to run tonight

**Retrieval, long context, KnowNo-conformal + confidence channels (layered on retrieval), and reflection (Reflexion-
style, error-driven)** — reflection is kept conditional: if its nightly notes end up functionally indistinguishable
from `routine7`'s once running (both are "the model's own summary of the day"), the budget moves to widening the
long-context run instead, per the workshop session's steer (it already owns the `routine7` table and confirmed the
overlap risk). Buffer (naive/recent) and the sighting-table reflection (`routine7`) are the workshop session's; not
duplicated here.

## Split with the workshop session (dynamic-home-eqa-5a), agreed 20:36
- They run: `naive` (buffer) and `routine7` (nightly per-object table), told + not-told, on sick10_partial hh_s0-s2.
  Told arms are pre-armed to auto-start at each not-told arm's day 14 (bank `hint_messages`).
- I run: retrieval, long-context, reflection (conditional), KnowNo/conformal + confidence channels, told + not-told,
  same households, plus sick10_all per the coordinator's original scope.
- Code: copied `dynamic_home_eqa_fm/src/baselines/patrol/llm.py` wholesale (confirmed importable, confirmed today's
  earlier `uq_llm.py` calls it with an unchanged, compatible signature — zero regression). Leak check unchanged
  (`baselines/patrol/leak_check.py`, called on every prompt inside `run_arm`'s `ask()`).
- Server: 64 sequence slots; workshop holds ~35-40 until ~23:30; I stay under 20 streams until then; no server
  restart before 23:30 without messaging them first.
- Cold/warm split: mirroring the workshop's finding that day-level accuracy hides recency (right on later
  questions about an object each day by flattery, wrong on the first) — every table below will report the COLD
  split (first question about an object that day, before that day's feedback) alongside the plain day mean.

## Plan for the next 45 minutes
1. Implement `retrieval`, `longcontext`, `reflect` as new `mem_kind` values in `llm.py` (new `MEMORIES` entries);
   write the expectation for each before running.
2. 20-question smoke test on hh_s0 (sick10_all), not-told, all three memory kinds + the existing `naive` as a
   same-household yardstick; check the per-day/per-question table against the expectation by hand.
3. 3-5 households on sick10_all/banks and sick10_partial/banks, told and not-told, within the 20-stream budget
   (~744 q/household x up to 4 memory kinds x 2 told-arms — sizing the household count to the budget, reported
   honestly if it has to be fewer than 5).
4. KnowNo/conformal + the three confidence channels layered on `retrieval`'s answers, one household, small (matches
   today's earlier local-only, small-test discipline).
5. Wide runs (more households) after 23:30, per the server-budget agreement.

## Expectation, before the smoke test — 20:48
`retrieval`, `longcontext`, `reflect` on hh_s0 (sick10_all), not-told, `fmt=conf`, `--max-days 2` (~48 questions, day
1-2, both lead-up days, no shift yet): every arm should run without a leak-check abort or a parse fallback rate above
~10% (the schema and prompt format are unchanged from the naive/summary arms already proven today), and land within
a few points of the naive/summary arms' day-1/2 accuracy already seen in this study (naive ~90%+, summary similar) —
these are easy early days, not a place where a NEW memory construction should differ much yet. `longcontext`'s prompt
token count is the thing being measured, not accuracy: expect prompt_tokens per call in the low thousands on day 1-2
(household has ~20 objects with a handful of sightings each) rising day over day; the question is whether it still
fits well under 98k by day 28-32, checked once the smoke test's token counts are in. `noticing` (every arm) should
answer "changed: false" on essentially every lead-up day (nothing has changed yet) — any "changed: true" this early
is a false alarm, logged as such once the wide run reaches the shift day.

## Smoke test result — 20:49 (corrected expectation, logged honestly)
retrieval/longcontext/reflect on hh_s0, not-told, days 1-2 (48 q each): 58-60% overall, day1 50-54%, day2 62-67%.
My WRITTEN expectation ("within a few points of naive/summary's ~90%+") was wrong, not the code: that 90%+ recollection
was from day 13 of a DIFFERENT regime (sick_owner), 13 days into the lead-up with history built up; days 1-2 are the
hardest days for every method, memory or classical, because almost nothing has been seen yet. Checked against the
actual same-household classical yardsticks: frozen timetable day1/2 = 50%/79%, last seen = 50%/42% (hh_s0, sick10_all).
All three new strategies sit in that same range on day 1 (54-60%) and between last-seen and the timetable on day 2
(62-67% vs 42%/79%) — a normal early-days shape, not a bug. Fallback rate 0% and status all "ok" in every arm (no
parse failures, no leak-check aborts). `noticing` answered "changed: false" on both lead-up days in every arm (0 false
alarms) — correct, matches the expectation exactly. Cold/warm split (new, per the workshop session's finding) shows
the expected direction in all three: warm (61-68%) > cold (41-53%) — a method that has not actually learned anything
yet would show cold ≈ warm; this gap is itself a first, cheap signal that these strategies use SOME memory, not none.
Prompt tokens (day 1-2 only): longcontext mean 1993 (max 2721), reflect mean 1205, retrieval mean 992 — all far under
98k; the real test (does longcontext still fit by day 28-31) needs a full-length run, planned next.
Server reality: 151 calls took 2288s at --workers 6 under the shared load (~15s/call effective) — a full 744-question
household at that rate is ~2 hours per arm. Scaling to the agreed 20-stream ceiling should help but is not linear if
the bottleneck is server-side queueing, not my own concurrency. Revised plan below.
