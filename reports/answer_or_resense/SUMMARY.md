# Answer-or-Resense — calibration under a scarce-sensing loop (results)

> **UPDATES (2026-07-26).** (1) P1/P2 were originally tested with an OBJECT-level
> typical/atypical split because the 24-household pool is atypical by
> construction; a TYPICAL household bank (`version22_typ`, 6 hh) now exists and
> P1 is tested at the household level — the scaffolded LLM beats classical in
> BOTH classes, and its edge is LARGER on atypical households (+0.74) than
> typical (+0.30), contradicting P2's direction. (2) The object-level split
> suffered a query-ordering confound (atypical queries always drew the earliest
> hours and so got first claim on the daily budget) — fixed in
> `env.household_queries`; cross-arm comparisons were unaffected. (3) τ and α are
> now PER-MODEL (see `frozen_dev_params.json` → `per_model`). See
> `reports/two_capacities/SUMMARY.md` for the corrected multi-model table.


Confirmatory: 24 households (v22 + v22b expanded pool), **staggered start offsets**
(phase lesson applied — offset (i·3)%7 per household, day-of-week balanced; no
Monday artifact possible). Scarce mode: zero initial observations; resense is the
only data source. Typical/atypical is WITHIN-household at the object level
(conventional objects vs the regime-flipped idiosyncratic targets). Day-clustered
bootstrap CIs. Model: DeepSeek-V4-Flash local.

## Frozen on dev (before any confirmatory call)

| param | value | how chosen |
|---|---|---|
| queries/day Q | 10 | oracle-interior sensing cell |
| resense budget B | 5 | scarcest interior cell (B=2 was degenerate: even the ORACLE pinned at ceiling — KARL check applied at selection) |
| resense reward r | 0.4 | mid grid; oracle interior (rr 0.37 < 0.9·ceiling 0.50) |
| wrong penalty | 0 | primary (−1 variant swept on dev only) |
| τ_c classical | 0.75 | dev reward max |
| τ_c hybrid | 0.45 | dev reward max |
| LLM prompt | v1 | 70.9/hh vs v2 37.8 / v3 38.8 — **the EV-framed prompts v2/v3 drove the LLM to near-ceiling resensing (rr≈0.49 vs ceiling 0.5) with acc 0.15–0.17: the KARL abstention trap, triggered by prompt wording alone.** Reported, not hidden. |
| α* (fusion) | 6.07 | reused from reflect_dag dev calibration; not re-tuned |

## Headline: cumulative reward per household-day (95% CI)

| arm | typical | atypical | ALL |
|---|---|---|---|
| classical (τ) | 2.23 [2.08,2.37] | **2.82 [2.70,2.93]** | 5.04 |
| llm (decides itself) | **2.40 [2.29,2.51]** | 2.36 [2.24,2.48] | 4.76 |
| **hybrid (fusion+τ)** | **2.60 [2.49,2.71]** | 2.78 [2.65,2.89] | **5.38 [5.21,5.54]** |
| llm_thresh (arm 5) | 1.88 | 2.26 | 4.14 |
| oracle (bound) | 3.25 | 3.84 | 7.09 |

## Pre-registered verdicts

- **P1 (typical: llm ≥ classical) — SUPPORTED.** 2.40 [2.29,2.51] vs 2.23
  [2.08,2.37]; the LLM's conventional prior pays where placements are conventional.
- **P2 (atypical: classical > llm by late days) — SUPPORTED, CI-separated**, with a
  twist on the mechanism. Classical 2.82 [2.70,2.93] vs llm 2.36 [2.24,2.48];
  answered-accuracy 0.65 vs 0.51. Mechanism evidence: the LLM's resense rate per
  unit error is 0.35/0.49 = 0.71 vs classical 0.34/0.35 = 0.97 — the LLM
  **under-resenses relative to its error rate** and its learning curve stays flat
  while classical's rises. The twist: the idiosyncratic objects are actually EASY
  for an evidence-based learner (a mug that lives at the craft desk is stable once
  observed) and HARD only for a prior-driven guesser — so honest ignorance +
  looking beats confident knowledge, which is precisely the thesis.
- **P3 (hybrid ≥ max(llm, classical) in BOTH splits) — SUPPORTED (as ≥).** Typical
  2.60 > both (separated); atypical 2.78 ≈ classical 2.82 (indistinguishable);
  pooled 5.38 [5.21,5.54] beats both (separated). Robust in both splits, best overall.
- **P4 (llm_thresh closes the atypical gap) — FAILS, informatively.** Arm 5 is the
  WORST arm (4.14). Giving the LLM's answers a statistical resense-decision does
  not rescue it — because the LLM's resense *targeting* was actually its strong
  suit (P(wrong|resensed,cf) = 0.79–0.89: when it chose to look, it was right to)
  while its ANSWERS are the weak link in scarce mode. The attribution flips: the
  failure lives in the answers (prior + weak integration of self-gathered
  evidence), not the decisions. Forcing it to answer where it wanted to look
  (coverage 0.79 vs 0.70) converts good abstentions into wrong answers.

## Calibration

- **Verbalized confidence is overconfident** (the literature's signature): mean
  stated 0.68 vs realized 0.53 (llm arm), ECE = 0.18. (2.9% of confidences came
  back off-scale >1 and were excluded; logged.)
- **Behavioral calibration is better than verbal but still short**: the LLM's
  resense choices track would-be errors well (cf-wrong 0.79–0.89 among its
  resenses vs oracle's 1.00 by construction), yet it under-resenses in volume
  relative to its error rate — it "knows what it doesn't know" locally but
  over-answers globally.
- **KARL-trap check on the frozen run: clean.** All arms interior (rr 0.21–0.39 vs
  ceiling 0.50); no arm pinned at ceiling or floor. The trap DID appear at dev
  time in prompt variants v2/v3 (see table) — evidence the failure mode is real
  and prompt-sensitive, caught by the pre-registered check.
- Figures: `resense_rate_conf.png` (with ceiling), `risk_coverage_conf.png`,
  `learning_curve_conf.png`.

## Notes and lineage

- Scoring order correct > resense > wrong follows the evaluation-reform argument
  (Kalai et al., "Why Language Models Hallucinate"): partial credit for
  admitting uncertainty makes calibrated behavior rational; resense = IDK-plus-look.
- This line deliberately RE-COUPLES learning and sensing (the earlier ambient
  stream decoupled them); the coupling is the object of study.
- Oracle sanity: P(wrong|resensed,cf) = 1.00 by construction — machinery verified.
- Not run this round (noted variants): resense-then-answer; wrong=−1 confirmatory;
  warm-start control for LLM arms (classical warm control is cheap to add).
- Old-bank (v22-only) vs expanded split available from the row files (`hh` field);
  headline numbers above are the expanded pool.
