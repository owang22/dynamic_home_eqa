# L0: how calibrated is an LLM's prior over household object dynamics?

> **SUPERSEDED (2026-07-07) by `l0_rerun.md`.** This run had three
> stacked confounds — the room-inventory prompt omitted the categories
> being asked about, the cross-family model (Mistral-7B) was both smaller
> and non-reasoning relative to Qwen, and the same-family model is the
> literal pool generator — that together make its "worse everywhere"
> verdict untrustworthy. Do not cite the verdict or headline numbers
> below. Kept only as the record of the three real infrastructure bugs
> this run found and fixed (Qwen3's thinking-mode budget consumption,
> `verbalized()` bypassing the chat template, location targets missing a
> dynamics elicitation) — those fixes carried forward unchanged into the
> rerun. See `l0_rerun.md` for the current numbers.

**VERDICT (SUPERSEDED — see notice above): Worse everywhere.** No (model, elicitation-mode) combination
tested beats the fitted TransitionKernel on either scored axis. On the
location prior, the fitted kernel's own Brier (0.787) beats every LLM
elicitation, including the best one (Qwen/verbalized, 0.852). On the
state-axis long-horizon cell — the specific cell this phase exists to
check, where the fitted kernel predicts 50% survival against 0% observed
— every LLM (model, mode) combination reproduces the same failure mode
or a substantially worse one: Qwen tracks the fitted kernel's own error
closely (50-65% predicted vs. 0% observed); Mistral's mcq_logprob and
sample_count modes predict essentially certain survival (99.9% vs. 0%
observed), a much larger miscalibration than the artifact L0 was sent to
investigate.

## Setup

Frozen scene (102343992_family_with_kids) only — the same scene D1's
kernels are fit from, matching this project's established precedent for
foundational calibration work (voi_boundary.md, kernel_reliability.md
were both scene-limited the same way). 42 elicitation targets (36
location-axis, 6 state-axis), each a (category-or-variable, time_bin)
pair with at least one real train-split event in that 6-hour bucket. Two
elicitation targets per target: a **location prior** (categorical
P(slot_type), location-axis only) and a **dynamics prior** (stay-
probability / flip-rate, both axes), each run through all three
elicitation modes (mcq_logprob, verbalized, sample_count with k=20).
Persona text and room inventory only — no train-day event was ever shown
to a model (verified directly: `tests/test_llm_prior_targets.py`'s
`test_does_not_reference_train_day_events` checks no change event's
`reason` field text leaks into either rendering).

**Models:**

| | same-family (generator) | cross-family |
|---|---|---|
| model | `Qwen/Qwen3-14B-AWQ` | `mistralai/Mistral-7B-Instruct-v0.3` |
| provider | local vLLM | local vLLM |
| quantization | AWQ | none (fp16) |
| lineage | Qwen (Alibaba) — the exact model `scripts/expand_scene_pool.py` used to generate every pool scene's traces (see Step 0 below) | Mistral AI — different base model, different provider, no relation to Qwen's lineage |

Mistral was chosen because it is ungated on the HF Hub (no token needed
in this environment), exposes token logprobs identically to Qwen through
vLLM, and is a genuinely separate lineage — not a fine-tune or
distillation of anything Qwen-derived.

**Step 0 (generator family):** confirmed via the generation call sites,
not assumed — `generation.llm_client.DEFAULT_MODEL`
("Qwen/Qwen3-14B-Instruct") does not exist on the HF Hub (HF API 401) and
was never actually used; `scripts/expand_scene_pool.py` (which produced
every pool scene) passes `--model Qwen/Qwen3-14B-AWQ` explicitly, matching
`agents/llm_agent.py`'s `MODEL_14B` ("production"). `generation_model` is
now a required field on `scripts/e2_headline_comparison.py`'s
`PoolManifest` (no default — a future generation run on a different model
must set it explicitly, and doing so changes the pool fingerprint like
any other config field).

**Infrastructure:** one cached client (`llm_prior/client.py`), cache keyed
by (model_id, prompt_hash, mode, seed) (`llm_prior/cache.py`), every
response committed under `llm_prior_cache/` (1.9 MB). Prompt templates
are versioned (`llm_prior/prompts.py`'s `PROMPT_VERSION = "l0-v1"`) and
hashed into every elicitation manifest
(`results/reports/l0_manifests/l0_manifest_{qwen,mistral}.json`)
alongside `code_hash` (both models share `code_hash=39266943216ebc03`,
confirming identical elicitation code). `tests/test_llm_prior_report.py`
scores directly off the committed cache — no live model call anywhere in
pytest; `llm_prior/elicit.py` is the only module that touches vLLM or the
network.

**A real infrastructure bug found and fixed during this batch, not
papered over:** Qwen3 is a "thinking" model — without
`chat_template_kwargs={"enable_thinking": False}`, it emits a reasoning
trace before any answer, which broke all three elicitation modes (a
1-token mcq_logprob budget captured the first reasoning token, not the
answer; sample_count's 4-token budget never reached a parseable letter).
A first pass mistakenly scored this reasoning-trace noise as Qwen's
"prior" — caught because the resulting Brier (0.885) turned out to
exactly equal the uniform-guessing baseline computed independently,
which is what pure noise on a first-token distribution over unrelated
filler words should produce. Fixed by disabling thinking mode for every
`.chat()` call (a no-op for Mistral's chat template, verified). A second,
independent bug in the same pass — `verbalized()` called vLLM's raw
`.generate()` on a manually concatenated system+user string, skipping the
chat template's generation-prompt scaffolding entirely — was fixed by
routing verbalized mode through `.chat()` like the other two modes. A
third bug — location-axis targets never received a dynamics-prior
elicitation at all (`run_elicitation` called either the location-prior
or the dynamics-prior builder per target, never both) — was found from
`n_parse_failures=36/42` in the dynamics scoring pass exactly matching
the location-target count, and fixed by eliciting both prior types for
every location target (dynamics prior only, for state targets — state
variables don't have "slot types", per L0's own spec).

## Headline numbers

### Location prior — Brier score against empirical train-split frequency (lower is better)

| model | mode | Brier | n scored | n parse failures |
|---|---|---|---|---|
| **fitted kernel (reference)** | — | **0.787** | 36 | — |
| Qwen (same-family) | verbalized | 0.852 | 36 | 0 |
| uniform guessing (baseline, matched per-target support size) | — | 0.885 | 36 | — |
| Mistral (cross-family) | mcq_logprob | 1.445 | 36 | 0 |
| Mistral (cross-family) | sample_count | 1.488 | 36 | 0 |
| Mistral (cross-family) | verbalized | 1.517 | 30 | 6 |
| Qwen (same-family) | mcq_logprob | 1.506 | 36 | 0 |
| Qwen (same-family) | sample_count | 1.524 | 36 | 0 |

Every LLM (model, mode) pair except Qwen/verbalized scores **worse than
blind uniform guessing** over the same support. Qwen/verbalized is the
only combination in the neighborhood of uniform, and it still trails the
fitted kernel by 0.065 Brier.

### State axis, wait=4h — the cell this phase exists to check (fitted kernel: 50% predicted vs. 0% observed, n=66)

| model | mode | predicted survival | observed survival | n |
|---|---|---|---|---|
| **fitted kernel (reference)** | — | **50.1%** | 0% | 66 |
| Qwen (same-family) | sample_count | 50.5% | 0% | 66 |
| Qwen (same-family) | mcq_logprob | 50.6% | 0% | 66 |
| Qwen (same-family) | verbalized | 64.5% | 0% | 66 |
| Mistral (cross-family) | verbalized | 64.5% | 0% | 66 |
| Mistral (cross-family) | mcq_logprob | 99.9% | 0% | 66 |
| Mistral (cross-family) | sample_count | 100.0% | 0% | 66 |

Nothing closes this gap. Qwen's predictions sit close to the fitted
kernel's own error; Mistral's mcq_logprob and sample_count modes are
dramatically more confident than the fitted kernel while being equally
wrong — the object's state changes within 4 hours in literally every one
of 66 held-out instances, and two of Mistral's three elicitation modes
predict near-certain survival.

## Plots

![Fitted kernel reliability (reference)](kernel_reliability.png)
![Qwen (same-family) dynamics reliability, verbalized mode](l0_dynamics_reliability_qwen.png)
![Mistral (cross-family) dynamics reliability, verbalized mode](l0_dynamics_reliability_mistral.png)

All three reuse `scripts/kernel_reliability_diagram.py`'s
`bin_reliability`/`write_plot` unchanged — the LLM-elicited priors are
scored on these plots via `llm_prior/synthetic_kernel.py`, which turns an
elicited (destination distribution, stay probability) pair into a real
`posterior.TransitionKernel` object and feeds it through the identical
`_posterior_validity_at_dwell` propagation the fitted kernel itself is
scored with — not a parallel reimplementation.

## The circularity table

**Same-family (Qwen) scores materially better than cross-family
(Mistral) on both axes** — location Brier 0.852 vs. 1.445 (best mode
each); state wait=4h predicted survival 50-65% (Qwen) vs. 65-100%
(Mistral), further from the 0% ground truth. Qwen is not merely "the
same lineage" as the generator — it is the *exact model* every pool
scene's traces were generated from
(`scripts/expand_scene_pool.py --model Qwen/Qwen3-14B-AWQ`). Some or all
of Qwen's advantage over Mistral here is plausibly measured
contamination — the same weights that produced the ground truth are
being asked to predict it — not a genuine same-family-reasoning
advantage, and this report makes no claim to separate those two effects.
Reported as a gap, not hidden as a "same-family baseline."

This also means Qwen's numbers above are the MORE favorable case for
"LLM priors help," and they still lose to the fitted kernel on both axes.

## What this means

An LLM prior over object dynamics, elicited the three standard ways on
this scene, does not beat a plain fitted TransitionKernel — on the axis
where the fitted kernel is already known to fail badly (state-axis long
horizon), the LLM prior does not close the gap and in the cross-family
case makes it worse. This is a real, negative, well-measured result: it
sharpens (not undermines) the motivation for L1's actual design — a
Dirichlet pseudo-count *blend* of an LLM prior into the existing D1
backoff hierarchy, not a wholesale substitution of the fitted kernel with
an LLM prior. A blend can only help if it's weighted correctly; today's
raw elicitation, unweighted, would make the state axis worse, not better.

This also connects to `e2_preliminary.md`'s `tod_prior` finding: a
schedule-only prior with zero live sensing already scores far below the
answer-immediately floor on this benchmark (0.133/0.180 vs. 0.476/0.366).
L0 shows the same qualitative pattern one level up the prior-quality
ladder — a frontier LLM's forecast-only prior, still with zero live
observation, also fails to match a simple fitted statistical model.
Priors substituting for observation is the wrong shape of claim on this
benchmark; priors blended with observation (L1's actual design) is the
live hypothesis.

## What is too thin to call

- 42 targets, one scene. The location Brier gap between the fitted
  kernel (0.787) and Qwen/verbalized (0.852) is real but not large — a
  second scene could plausibly flip the ranking on the location axis
  specifically, even though the state-axis long-horizon result (a much
  larger, near-total-certainty miscalibration for Mistral) looks robust
  to that kind of noise.
- Only one persona, one room-inventory rendering was ever shown to
  either model — whether a different household profile changes which
  mode elicits the best prior is not tested here.

## What is NOT yet supported by these numbers

- **Room inventory omits Tier-2b clutter categories** (book, bowl,
  candle, cup, keys, phone, stool, vase — everything
  `env.inventory.inventory_for_generation` doesn't track pre-clutter-pass,
  see that function's own docstring). These are exactly the categories
  most of the 36 location targets ask about. Direct evidence this
  matters: Mistral's verbalized responses for several of these
  categories reasoned explicitly from the (correct) observation that the
  category wasn't mentioned in the inventory it was shown, and returned
  either "100% OUTSIDE" or an all-zero (unparseable) distribution. This
  is not a bug — the room-inventory renderer faithfully reflects what
  `inventory_for_generation` tracks, and any richer inventory would need
  a specific day's clutter-placement result, which is train-day-adjacent
  information L0 is not allowed to show — but it is a real, systematic
  source of location-prior degradation this report does not correct for.
- L1's gate (this report existing + E4's perturbation sweep tolerance
  curve) is not evaluated here — see `results/reports/INDEX.md`.
- No hosted same-family model was used (this environment has no API keys
  for any hosted provider) — "same family may be hosted" was permitted
  by L0's spec but not exercised; Qwen ran locally via the identical
  vLLM path as Mistral.

**Traceability:** `code_hash=39266943216ebc03` (both manifests agree),
`prompt_version=l0-v1`. Reproduce with `llm_prior/elicit.py --model
{qwen,mistral}` then `llm_prior/report.py`. Raw cache:
`llm_prior_cache/` (1.9 MB, committed). Manifests:
`results/reports/l0_manifests/l0_manifest_{qwen,mistral}.json`. Scores:
`results/reports/l0_scores_{qwen,mistral}.json`.
