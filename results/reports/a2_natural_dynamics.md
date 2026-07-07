# Phase A, A2: FM dynamics reasoning in its native modality — quick check

**VERDICT: does not beat the kernel; consistent with L0, not a new
finding, and not a rigorous study.** This is exactly what the task list
asked for: a fast look, drawn from a genuinely different elicitation
modality (free-form reasoning ending in a stated number, not L0's
bucketed-simplex formats), reported at the scale it was run — one model,
one scene, single pass, no species-level claim either direction.

## What was asked

The FM (Llama-3.3-70B-AWQ, A1's clean cross-family pick) reasons in
prose about a household's routine and a specific object category's
likely behavior, then concludes with a single stated number
(`STAY_PROBABILITY: <x>`) — the model's own native modality, not forced
into L0's JSON-simplex-per-state format from the first token. 36
location-axis targets (every category with a fitted kernel and at least
one real train-split event in that time bucket — same target
enumeration L0 used), scored against the fitted kernel on the identical
dwell/reliability machinery T0 and L0 both used
(`scripts/kernel_reliability_diagram.py`'s `reliability_points`/
`bin_reliability`, `llm_prior/synthetic_kernel.build_synthetic_kernel`).
0 parse failures — the free-form-then-extract format worked cleanly
every time.

## Headline numbers

| wait_hours | fitted kernel Brier | A2 natural-reasoning Brier |
|---|---|---|
| 0.25 | 0.228 | 0.237 |
| 0.50 | 0.321 | 0.379 |
| 1.00 | 0.266 | 0.366 |
| 2.00 | 0.239 | 0.406 |
| 4.00 | **0.118** | **0.365** |

The fitted kernel wins at every horizon, and the gap widens rather than
narrows at longer waits (roughly 3x at 4h) — the same shape T0 already
found for the fitted kernel's OWN advantage over a trivial predictor: the
horizons where real dwell-time fitting matters most are exactly where an
elicited prior (bucketed or natural-language, same conclusion either
way) falls furthest behind.

## What this means

A genuinely different elicitation modality — reasoning in prose rather
than filling a forced simplex — does not change L0's conclusion. This
is not a new, independent finding; it is the same finding surviving a
format change, which is itself worth having on record precisely because
it rules out "L0's result was a format artifact" as an explanation. Per
the task's own instruction, since this did NOT surprise in the kernel's
favor, there is nothing to flag for a later real study — proceed to B.

## What is NOT yet supported by these numbers

- One model (Llama only — A2 explicitly skipped the same-family
  contaminated-reference and the multi-mode comparison L0 ran; this is a
  quick check, not L0-scale replication).
- One scene, one pass, no repeated sampling or confidence intervals.
- State axis not covered.
- No claim that natural-language reasoning is categorically worse than
  structured elicitation in general — only that it did not do better
  here, on this scene, this once.

**Traceability:** `scripts/a2_quick_dynamics_check.py`; raw numbers
`results/reports/a2_quick_dynamics_check.json`; plot
`a2_natural_dynamics_reliability.png`. No habitat_sim needed (pure
elicitation + scoring, in-process vLLM client — this script doesn't run
inside a live episode, so A1's HTTP decoupling doesn't apply here).
