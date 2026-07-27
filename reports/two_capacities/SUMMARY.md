# Two Capacities — (a) knowing what it doesn't know vs (b) learning from what it gathers

> ## ⚠️ SUPERSEDED (2026-07-26): the multi-model section below is WRONG
>
> The three-model table and the "fusion inherits LLM overconfidence" conclusion
> used a SINGLE frozen τ=0.45 and α=6.07, both derived from DeepSeek. Per-model
> dev sweeps show τ=0.45 sat **below the entire fused-confidence distribution**
> of Qwen and GLM (their p10 ≈ 0.50), so their resense gate could never fire —
> they answered ~96% of queries and starved themselves. That was **my
> hyperparameter choice, not a model property.**
>
> **Corrected confirmatory (per-model τ\*, α\*; classical baseline 5.04):**
>
> | model | τ* | α* | OLD (frozen) | **NEW (per-model)** | Δ |
> |---|---|---|---|---|---|
> | DeepSeek | 0.45 | 2.72 | 5.73 | **5.26 [5.10,5.43]** | **−0.47** |
> | Qwen3.6 | 0.70 | 2.75 | 3.34 | **5.42 [5.23,5.59]** | **+2.08** |
> | GLM-4.5-Air | 0.70 | 0.65 | 3.14 | **5.19 [4.98,5.39]** | **+2.05** |
>
> **Both "weak" models now BEAT classical (5.04)**, and all three land in a tight
> 5.19–5.42 band with healthy resense rates (0.19–0.27). The claim that the
> scaffold only works on a well-calibrated model does NOT survive.
>
> Note the honest cost: **DeepSeek LOSES 0.47** from the α correction. Its τ was
> already right, so the only change was α 6.07 → 2.72 — trusting its genuinely
> good prior less lost real reward. Per-model calibration is therefore *not* a
> free win: it helps models whose priors were over-credited and hurts the one
> whose prior deserved the credit.
>
> Figures: `reports/corrected/C2_per_model_calibration.png`,
> `C3_P1_accuracy_by_day.png`, `C1_anonymization_corrected.png`.
>
> Also superseded here: the object-level typical/atypical split. P1 is now tested
> at the HOUSEHOLD level against a purpose-built typical bank
> (`version22_typ`, 6 households); the object-level split additionally suffered a
> query-ordering confound (atypical queries systematically got first claim on the
> daily budget), fixed in `env.household_queries`.


> **HEADLINE CORRECTION (final).** The "LLM fails to integrate self-gathered
> evidence" claim was an artifact of a SCAFFOLDING difference between experiments,
> not a property of the model. When the reflect-style nightly reflection +
> persona memory is restored inside the resense loop (`llm_scaffold`), the LLM
> becomes the **best arm overall (5.78 [5.60,5.96] reward/hh-day)**, beating
> classical (5.04), the fusion hybrid (5.38), and the raw-log LLM (4.76) — and it
> beats classical on BOTH splits including atypical (3.02 vs 2.82). See
> "The scaffold control" below. Sections written before that control are retained
> for provenance, with their claims narrowed accordingly.


Confirmatory pool: 24 households (v22+v22b), staggered start offsets, frozen
answer-or-resense protocol (Q=10, B=5, r=0.4, wrong=0). All accuracies use the
counterfactual answer correctness (logged for every query), immune to
action-selection bias. Figures F1–F5 in this folder.

## Headline: a DOUBLE DISSOCIATION

**Capacity A (confidence) splits into ranking vs level — the ranking works:**
- RANKING: verbalized-confidence AUROC 0.75–0.79 (internal 0.77–0.79); resense
  targeting P(would-be-wrong | resensed) = 0.79–0.89. It KNOWS what it doesn't know.
- LEVEL: stated confidence 0.68 vs realized accuracy 0.53 (ECE 0.18); resense
  volume ratio (rate/error) 0.49–0.59 — it under-looks by ~half. (F3.)
- **Deployable (R1, the corrected P4):** thresholding the LLM's OWN confidence at a
  dev-matched τ=0.8 (`llm_selfconf`) lifts atypical reward 2.36 → **2.74**
  [2.65,2.83], statistically at classical's 2.82 [2.70,2.94]; overall 5.19 vs the
  self-deciding llm's 4.76. The decision failure was the operating point, not the
  ranking. Caveat: realized rr 0.48 sits at the B/Q=0.50 ceiling — the corrected
  level is partly budget-clamped, and reward improves via selective prediction
  (converting wrongs to resense credit), NOT via learning (see Capacity B).

**Capacity B (evidence integration) — CORRECTED after a prompt audit. It does
integrate, but with DECAYING FIDELITY (D4, F6):**

The first pass reported "gathers but does not learn" from the before/after delta
(llm −0.00 vs classical +0.60). **That metric was confounded** and the claim was
too strong. Classical's "before" is 0.000 *by construction* — with no
observations it is uniform over ~14 candidates — while the LLM's "before" is
0.420 because it has a conventional prior. So classical's +0.60 mostly measures
"went from nothing to something", not superior integration. The unconfounded
test is whether an arm ANSWERS WITH its own most-recent observation:

| arm | follows own last obs | acc when following | acc when overriding |
|---|---|---|---|
| classical | 0.999 | 0.616 | — |
| hybrid | 0.985 | 0.602 | — |
| llm_selfconf | 0.898 | 0.679 | 0.28 |
| **llm** | **0.809** | **0.591** | **0.245** |
| llm_v1_pinned | 0.814 | 0.627 | 0.265 |

- The LLM **does** use self-gathered evidence — it echoes its own last sighting
  81% of the time and reaches **91% of its echo-ceiling** after ≥3 observations
  (0.531 realized vs 0.586 available; classical realizes 100% of 0.617).
- **The real mechanism: following fidelity DECAYS as evidence accumulates** —
  0.94 (1 obs) → 0.88 (2) → 0.71 (3) → 0.70 (4+). With a single observation it
  is nearly a perfect counting model; the more data it holds, the more it
  second-guesses its own record.
- **Overrides cost 2.4×**: 0.245 accuracy when it departs from its own last
  observation vs 0.591 when it follows. Notably the override is often *timed*
  correctly — the object had genuinely moved in 53% of overrides — but it
  predicts the wrong destination. It knows *that* things move, not *where to*.
- **Query-level deltas, unconfounded by the zero-baseline** (both splits):
  llm +0.002, **llm_v1_pinned +0.133**, hybrid +0.226, classical +0.594. The
  protected-evidence variant does help more than the noisier dev slope metric
  suggested — pinning evidence is a real, partial mitigation.

Revised claim: *the statistical channel's advantage is not that it learns while
the LLM doesn't — it is that it never stops trusting its own data.*

**Paper framing this supports:** frontier LLMs can identify what they don't know
and act to acquire it (ranking usable, thresholdable), and they DO integrate
self-gathered evidence — but with fidelity that decays as evidence accumulates,
and their departures from their own record are 2.4x worse than following it.
That decay is the gap the statistical channel fills. Hybrid remains
best overall (5.38) because the statistical side does the learning while the LLM
side supplies cold-start answers and usable uncertainty ranking.

## Arm-5 correction (mandatory)

`llm_thresh` (LLM answers + CLASSICAL confidence decisions) did NOT test P4:
C3g's posterior confidence ranks the LLM's answer correctness at **AUROC 0.46 ≈
chance** (the LLM's own ignored verbal confidence: 0.81). Its resense rate
collapses to ~0.01–0.03 by day 8 (typical) as C3g's posterior sharpens while the
LLM's answers haven't improved — a mismatched-confidence artifact. Do not cite
arm 5 as evidence about LLM decision quality; `llm_selfconf` is the correct test
and it PASSES.

## R3 — the KARL/prompt-sensitivity finding (first-class)

| prompt (dev) | framing | resense rate | ceiling | answered acc | reward/hh |
|---|---|---|---|---|---|
| v1 (frozen) | "if confident, answer; if not, resense" | 0.30 | 0.50 | 0.55 | 70.9 |
| v2 | expected-value ("choose higher long-run value") | 0.49 | 0.50 | 0.15 | 37.8 |
| v3 | "only answer when confidence beats resense value" | 0.46 | 0.50 | 0.17 | 38.8 |

The two MORE principled decision-theoretic framings pinned the LLM at the budget
ceiling with collapsed accuracy — the KARL abstention trap triggered by wording
alone, caught by the pre-registered interiority check. (F4 marks these points.)

## Plot hygiene applied (D3)
- Oracle dropped from risk–coverage panels (no meaningful sweepable confidence;
  its earlier "backwards" curve was an artifact of sweeping a confidence it never
  uses).
- Resense-rate figures state denominators: rates are per-split, budget is global;
  the global B/Q ceiling is drawn as labeled reference.
- 1.7% of verbalized confidences were off-scale (>1: rating-scale/percent
  leakage, e.g. "3", "85"); excluded from ECE/AUROC and logged.

## Files
- F1 gathers-but-does-not-learn (accuracy/day + cumulative-obs inset)
- F2 within-object before/after forest (the mechanism)
- F3 ranking vs level (risk–coverage + reliability with operating points)
- F4 resense-vs-error scatter (diagonal = volume-calibrated; KARL points marked)
- F5 reward decomposition (why the hybrid wins)
- Section-1 diagnostics: `python -m dynbelief.two_capacities.diagnostics`

## Prompt / implementation audit (added after a skeptical review)

The negative result was re-examined for self-inflicted causes by reconstructing
the EXACT prompts sent (replaying logged actions; `scratchpad/dump_prompt.py`).
Findings:

1. **Prompt content is clean.** Late-day prompts contain every self-gathered
   observation of the queried object, correctly timestamped, with the candidate
   list and budget. Verified case: 8 prior observations of `bowl`, all reading
   `desk_o1`, all present in the prompt.
2. **Uniform-fallback artifact (minor, 0.1–0.4% of answers).** When the model
   returns receptacle names outside the candidate list (or the JSON fails),
   `_ask` falls back to a uniform belief and `decide` takes `max()` of it, which
   returns the alphabetically-first candidate (`bathroom_c1`). Accuracy among
   these is 0.000 by construction. Immaterial at this rate, but it should be
   logged as an explicit `parse_failed` action rather than silently answered.
3. **Observation truncation (`[-60:]`) — tested and RESOLVED, no effect.**
   Households exceeding the 60-line cap: llm 1/24, llm_v1_pinned 4/24 (that
   variant shows all by design), **llm_selfconf 22/24**, hybrid 0/24.
   `llm_selfconf` was rerun with the cap raised to 200 (above the 70 max
   achievable): reward/hh-day 5.19 -> 5.18, resense rate 0.48 -> 0.48,
   answered-accuracy 0.628 -> 0.625, follow-rate curve 0.97/0.94/0.85/0.86 ->
   0.95/0.93/0.90/0.86. The cap retained the MOST RECENT observations, so
   nothing material was lost. **Caveat withdrawn.**
4. **The metric confound above (D1 baseline asymmetry) was the material issue**
   and is corrected in this document.

## Mechanism jobs J1-J4 (free re-analysis of the confirmatory logs)

### J1 — the decay is driven mainly by CONTEXT LENGTH, not per-object count
Observation count, day, and total context length are collinear by construction, so
both a matched comparison and a regression were run (`fidelity.py`).

Logistic regression of follow on standardized predictors (log-odds per 1 SD):

| predictor | coefficient |
|---|---|
| n_hist (total observations in the prompt = context length) | **-0.492** |
| n_obs (per-object evidence) | -0.158 |
| day | -0.071 |

Matched cells confirm BOTH effects exist but context dominates: holding day at
10-15, follow falls 0.96 → 0.68 as per-object count rises; holding count at 3,
follow falls 0.80 → 0.63 as the day band rises. **Claim: primarily general
long-context degradation, with a secondary per-object dilution term** — not a
pure evidence-dilution story.

### J2 — overrides revert toward the model's own PRIOR (prior gravity), at a constant rate
Prior = the arm's own first prediction for that object *before* it had any
observation of it (its revealed prior).

- llm: **28.4% of overrides land exactly on the revealed prior** vs ~5.9% chance
  (**4.8x enrichment**); pinned 27.9%; hybrid 57% (of only 7 overrides).
- But prior gravity does **not intensify**: among overrides it is 0.08 (1 obs) →
  ~0.28-0.38 (2+ obs) and then flat; by context-length tercile 0.22 / 0.34 / 0.29.
  **What grows is the override RATE (0.084 → 0.398), not the prior's share of them.**
  So the correct statement is "the model departs from its evidence more often as
  context grows, and when it departs it falls back toward its prior" — not "prior
  gravity grows."

**The H1 connection (the unifying result).** Prior-reversion is adaptive exactly
where the prior is right and destructive where it is not:

| split | override rate | of overrides → prior | acc of those reversions | acc had it followed |
|---|---|---|---|---|
| typical | 0.215 | 0.271 | **0.457** | 0.343 (**+0.11, helps**) |
| atypical | 0.250 | 0.306 | **0.227** | 0.545 (**−0.32, hurts**) |

This is the same prior-over-evidence failure as the H1 atypical-household story,
now observed *within* a single run as a function of accumulated context.

### J3 — Ns and object-clustered CIs on every bin (the ≥5 bin is well populated)

llm follow-rate: 1 obs **0.942 [0.917,0.965]** (n=566, 140 objects) → 2 obs 0.883
[0.825,0.932] → 3 obs 0.709 [0.590,0.820] → 4 obs 0.678 [0.573,0.780] → **≥5 obs
0.718 [0.646,0.787]** (n=510, 97 objects). The 1-vs-≥5 decay is **CI-separated**.
The tail bin is not thin (97 objects), so no merging is required.

Override rate AND accuracy together (both needed for the claim):

| arm | override rate | acc when following | acc when overriding |
|---|---|---|---|
| classical | **0.001** (3/2151) | 0.616 [0.571,0.659] | 0.667 (n=3) |
| hybrid | 0.015 | 0.604 | 0.361 |
| llm_selfconf | 0.102 | 0.700 | 0.231 |
| **llm** | **0.191** (392/2051) | 0.591 [0.547,0.636] | **0.245 [0.191,0.301]** |

"Classical rarely-but-well vs the LLM often-and-badly" is quantified.

### J4 — the environment's echo-ceiling, and why overriding is *principled but unskilled*
P(most-recent observation still correct at query time) = **0.569-0.616** — so
**perfect following is NOT optimal**: ~43% of queries genuinely require predicting
movement, and classical's fidelity-1.0 leaves that headroom on the table.
Freshness decays fast: lag 0d 0.83 → 1d 0.66 → 2d 0.57.

Counterfactual decomposition of the LLM's 392 overrides:

- staleness base rate 0.431; staleness among overridden queries 0.526 →
  **targeting enrichment only 1.22x (barely better than chance)**
- override on a genuinely STALE observation (n=206): **0.466 correct** vs 0.000
  had it followed → real gain
- override on a still-FRESH observation (n=186): **0.000 correct** vs 1.000 had it
  followed → total loss
- **NET: overriding scored 0.245 where following would have scored 0.474 (−0.230
  per override)**

**The precise, defensible claim:** the LLM's impulse to override is right in
principle — 43% of its evidence really is stale, and when it correctly suspects
staleness it recovers the right location 47% of the time — but it discriminates
stale from fresh at only 1.22x chance, so overriding is net-harmful. The failure
is not "ignores evidence"; it is *unskilled staleness detection combined with
prior gravity*, and it worsens with context length.

## THE SCAFFOLD CONTROL (decisive; resolves the cross-experiment discrepancy)

**Why it was run.** The reflect experiments (LLM 0.43 vs classical 0.30) and
answer-or-resense (LLM below classical) appeared to contradict each other even
though observations reach the context the same way. Three explanations were
tested and FALSIFIED: recency/staleness (the LLM loses at every lag), classical
data density (3.9 vs 4.5 observations per queried object; 85% vs 89% below C3g's
fitting threshold), and query-hour alignment (the LLM is *worse* near the
regime-revealing hour). The surviving difference was scaffolding: reflect gave
the model a **curated memory — persona hypotheses with probabilities + selected
evidence — built by a nightly reflection call, plus a routine-aware prompt**;
answer-or-resense gave it a **raw observation log** and a budget-focused prompt
with no persona step. `llm_scaffold` restores the reflect scaffold inside the
resense loop, so the two experiments differ ONLY in sensing protocol.

| arm | reward/hh-day | typical | atypical | resense rate | answered acc |
|---|---|---|---|---|---|
| llm (raw log) | 4.76 [4.57,4.93] | 2.40 | 2.36 | 0.32 | 0.512 |
| classical | 5.04 [4.84,5.26] | 2.23 | 2.82 | 0.28 | 0.544 |
| hybrid | 5.38 [5.21,5.55] | 2.60 | 2.78 | 0.27 | 0.589 |
| **llm_scaffold** | **5.78 [5.60,5.96]** | **2.76** | **3.02** | **0.18** | **0.616** |

The scaffolded LLM is CI-separated above every other arm, wins on **both** splits,
and needs to **look less** (resense rate 0.32 -> 0.18) because it knows more.

### The mechanism: the scaffold does not stop overriding — it makes overriding SKILLED

Override *rate* is essentially unchanged (0.191 -> 0.200). What changes is quality:

| arm | staleness targeting | acc when overriding | acc when following | net per override |
|---|---|---|---|---|
| llm (raw log) | 1.22x chance | 0.245 | 0.591 | **-0.230** |
| hybrid | 1.32x | — | 0.604 | -0.111 |
| **llm_scaffold** | **1.69x chance** | **0.544** | 0.651 | **+0.254** |

With a persona hypothesis, departing from a stale observation is a *grounded
inference* ("the night nurse sleeps at midday, so the phone is on the
nightstand"): staleness detection improves 1.22x -> 1.69x above chance, and when
the evidence really is stale the model names the right new location **76.6%** of
the time (vs 46.6% raw). Overriding flips from costing -0.230 to **gaining
+0.254** per override. Prior-reversion also rises (0.284 -> 0.460) but is now
*adaptive*, because the persona-informed prior is usually right.

### Revised conclusions

- **Capacity A (knows what it doesn't know): intact.** Ranking is usable
  (AUROC 0.75-0.79); level is miscalibrated but correctable by thresholding its
  own confidence (`llm_selfconf`, R1).
- **Capacity B (integrates self-gathered evidence): INTACT, conditional on
  scaffolding.** The raw-log arm's ungrounded second-guessing is a
  prompt/architecture artifact, not a model limitation. The nightly
  reflection + persona memory is **load-bearing**: it converts second-guessing
  into skilled inference and is worth **+1.02 reward/hh-day** over the raw log.
- **The paper's claim becomes stronger and simpler:** the reflection scaffold is
  what makes an LLM able to learn from its own sensing; strip it and the model
  falls below a counting baseline; keep it and it beats both the counting
  baseline and the fusion hybrid.
- **Open item:** `llm_scaffold` (5.78) beats the fusion `hybrid` (5.38), which
  fuses the RAW-log LLM. A scaffold+fusion arm is the obvious next combination
  and is untested.
- **Do not cite** the pre-scaffold "gathers but does not learn" framing.


## MULTI-MODEL REPLICATION (three models, frozen protocol) — the scaffold is a
## CALIBRATION MULTIPLIER, not a universal fix

24 households, staggered starts, τ=0.45 frozen from the DeepSeek dev sweep and
applied unchanged to every model (so cross-model differences are the model, not
per-model tuning). `classical` is model-independent and shared.

| model / arm | reward/hh-day | early d0-4 | late d5-13 | resense rate | err | **rr/err** | obs/hh |
|---|---|---|---|---|---|---|---|
| classical (shared) | 5.04 [4.84,5.26] | 3.72 | 5.78 | 0.28 | 0.49 | 0.56 | 38 |
| **DeepSeek** llm_scaffold | **5.78 [5.60,5.96]** | 5.25 | 6.08 | 0.18 | 0.47 | **0.38** | 25 |
| DeepSeek scaffold_fusion | 5.73 [5.55,5.91] | 5.35 | 5.94 | 0.20 | 0.42 | 0.48 | 28 |
| **GLM-4.5-Air** llm_scaffold | 4.88 [4.67,5.10] | 4.56 | 5.06 | 0.05 | 0.53 | **0.09** | 7 |
| GLM-4.5-Air scaffold_fusion | 3.14 [2.95,3.32] | 2.43 | 3.53 | 0.03 | 0.69 | 0.05 | 5 |
| **Qwen3.6-35B** llm_scaffold | 3.70 [3.51,3.90] | 2.92 | 4.13 | 0.04 | 0.64 | **0.06** | 6 |
| Qwen3.6-35B scaffold_fusion | 3.34 [3.14,3.53] | 2.64 | 3.72 | 0.03 | 0.67 | 0.04 | 4 |

### Finding 1 — the scaffold advantage does NOT generalize; it tracks calibration

- DeepSeek: scaffold **beats** classical (5.78 vs 5.04, CI-separated).
- GLM-4.5-Air: scaffold **ties** classical (4.88 vs 5.04, CIs overlap).
- Qwen3.6: scaffold is **worse** than classical (3.70 vs 5.04, CI-separated).

Reward rank-orders perfectly with the volume-calibration ratio rr/err
(**0.38 → 0.09 → 0.06** giving **5.78 → 4.88 → 3.70**) and with observations
gathered (25 → 7 → 6 per household). The weak models never spend the sensing
budget: Qwen answers 96% of queries and ends with **6 observations/household vs
DeepSeek's 25**, so it spends the whole run guessing from its prior. The scaffold
is a **multiplier on a model's existing calibration**, not a substitute for it.

### Finding 2 — fusion INHERITS LLM overconfidence (a pre-registered prediction that FAILED)

We predicted fusion would rescue the weak models, since the resense decision is
made by the fused statistical confidence rather than the LLM's own choice. **It
did the opposite**: Qwen 3.70 → 3.34, GLM 4.88 → 3.14. Mechanism:

| model | mean fused conf | frac below τ=0.45 | realized acc | conf − acc |
|---|---|---|---|---|
| DeepSeek | 0.592 | 0.239 | 0.577 | **+0.015** |
| Qwen3.6 | 0.677 | 0.029 | 0.326 | **+0.351** |
| GLM-4.5-Air | 0.626 | 0.033 | 0.305 | **+0.321** |

The fused belief is `w·LLM + (1−w)·stat` with `w = α/(α+n) ≈ 0.86` at n=1, so while
evidence is scarce the fused confidence is *mostly the LLM's*. A confidently-wrong
LLM therefore produces a HIGH fused confidence, the τ gate never fires (only
~3% of queries fall below τ), and the arm answers instead of looking — a
self-reinforcing starvation loop. DeepSeek's fused confidence is nearly calibrated
(+0.015 gap) so the same gate works; Qwen/GLM are +0.32-0.35 overconfident.

**Honest caveat:** τ=0.45 was frozen from DeepSeek's dev bank by design (for
cross-model comparability), so part of this is a mis-set threshold rather than a
pure architectural fact. The two readings are separable with a per-model τ sweep
on dev — untested. What IS established regardless: a single frozen fusion
threshold does not transfer across models with different confidence scales, and
precision-weighting cannot repair a prior whose *confidence* is itself wrong.

### Revised framing for the writeup
1. The reflection scaffold is load-bearing **and model-dependent**: it converts
   ungrounded second-guessing into skilled inference *only if the base model's
   confidence ranks its errors usably*.
2. Precision-weighted fusion buys **sample efficiency** on a calibrated model
   (day-2 vs day-5 to competence on DeepSeek) but **amplifies miscalibration** on
   an uncalibrated one. It is not a safety net for a weak LLM.
3. The single best predictor of whether any of this machinery helps is the cheap,
   model-agnostic statistic **rr/err** — how often a model looks relative to how
   often it is wrong.
