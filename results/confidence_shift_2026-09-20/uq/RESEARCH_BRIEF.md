# Brief for the research agent (uncertainty-aware prediction methods) — 2026-09-21 14:25, from the coordinator

Before you start, reply to the coordinator (session `dynamic-home-eqa-37`, via SendMessage) with: (a) the project goal in
your own words, (b) your first three steps with times, (c) how you will catch bugs mid-run. Oliver expects results by ~16:30.

## The project, in one paragraph
A household simulator; a home robot answers "where is X?" from a stream of sightings (a nightly 03:00 round plus "found-it"
feedback 10 min after every question) over weeks. The deliverable is the TESTBENCH story: methods LEARN the household's
routine (accuracy climbs with a visible slope to ~80%), BREAK sharply when the routine shifts (a sick spell, a vacation at
home, a return to work), re-learn in the new regime, and break again on the return. The coordinator is finding that regime
now with cheap agents (results/regime_search/, page https://claude.ai/artifact/H1q17m8yUpCEac8kAek2pc); current best: questions
asked DURING activities about routine objects (timetable 28 -> 80% in 3 weeks; sick spell / holiday->work dips of 11-14 pts,
one day; personal schedule-timed objects — razor, mug, snack_bowl, book, tablet, recipe_book, glasses, glass — carry the break).
YOUR JOB: a roster of current (2024+) uncertainty-quantification-aware prediction methods, correctly implemented as harness
agents, so that when the regime is frozen we show how well existing UQ-aware methods do (calibrated on plain days, aware
when stale, adapting after a shift). No LLM API spend ever; local vLLM (Qwen3.8-27B on :8300) only, and only small tests.

## What exists already (previous agent, exited 13:50) — read these first
- results/confidence_shift_2026-09-20/uq/METHODS.md: papers, adaptations, knobs, expectations, trivial-case checks.
- src/baselines/patrol/uq_agents.py: (1) online conformal with decaying step sizes (Angelopoulos-Barber-Bates ICML 2024) +
  relevance weighting from Ren et al. "Explore until Confident" 2024, with an optional explore-until-confident look;
  (2) conformal test martingale / e-detector staleness detector (Vovk; Shin-Ramdas-Rinaldo 2024) driving a targeted reset;
  (3) Bayesian model averaging over counters with several half-lives (fixed-share). uq_synth.py: synthetic checks (all
  passed: coverage 0.904 stationary; martingale crosses 100 within 12-43 steps after a synthetic shift). uq_report.py: tables.
  Degenerate check: `--agent none` == classical most_frequent, 0 mismatches.
- results on the OLD regime (uq/fb/report.md): all ~50-52% (no cliff in that regime to detect; martingale never fires);
  conformal coverage 0.91 vs 0.90 target. uq_llm.py + uq/llm_channels/: the LLM confidence-channel test (verbalized vs
  first-token logprob vs 5-sample agreement) was started, not finished.

## Your tasks, in order
1. Read METHODS.md and the code; run uq_synth.py yourself; confirm the degenerate check on one bank. Report what is
   actually working vs claimed (numbers).
2. Add the `stage` field to every agent's run-log row (bank question rows carry `stage` when a calendar is present) so the
   coordinator's per-stage tables work on your logs unchanged.
3. Run the roster on the CURRENT regime banks: results/regime_search/sick_spell/banks and results/regime_search/
   holiday_to_work/banks (10 households each, 28 days, 64 q/day; classical logs alongside for reference), output under
   uq/regime/<regime>/<agent>/. Read them the way a reviewer would: per-day accuracy and confidence with the stage boundary
   marked, coverage/set size per day, reliability, martingale firing days vs the true shift day, 5 hand-checked questions.
   Question to answer with numbers: does the staleness detector fire on the shift day (and not before), does conformal
   coverage hold across the boundary while set size grows, does BMA move weight to short half-lives after the shift?
4. Only then, the LLM channels: ONE household, TWO days (one plain, one shift day), ~100 questions, local Qwen.
5. Add one more 2024+ method if time allows — candidates: conformal prediction under distribution shift with weighted
   quantiles (Barber, Candès, Ramdas, Tibshirani 2023/24 "beyond exchangeability"), or semantic-entropy style agreement for
   the LLM channel (Farquhar et al., Nature 2024). Write its expectation before running it.
Rules (Oliver's): never make mistakes integrating these models; test quickly; write the expectation before the run and
check the stream against it mid-run; a metric moving the wrong way is a bug until explained; log problems in
uq/problems_found.md; move outputs, never delete; report to the coordinator with numbers every ~45 min.
