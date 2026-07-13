# Prompting Infrastructure — Phase 0 (hygiene) report

Four wiring-review bugs fixed, one deeper judge-robustness bug surfaced and
fixed as a consequence, verified on a one-scene rerun (102343992,
family_with_kids). **STOP for review before Phase 1.**

## What changed

1. **Judge scores persisted on every candidate.** `score_realism_batch` now
   returns `(scores, judge_meta)`; the pipeline stamps every grounded
   candidate — selected AND rejected — with `_judge_score`,
   `_judge_stage_tag`, `_judge_seed`, `_selected`, and (thinking mode only)
   `_judge_think`. Selected records are the same dicts, so `displacements`
   carries the exact score selection sampled against. Written to
   `generation_result.json["candidates"]` and mirrored one-per-line to a new
   `choices.jsonl`.
2. **Silent 0.5 default killed.** `_normalize_judge_scores` now warns and
   raises `PartialJudgeScores` whenever the judge covers fewer candidates
   than the batch (including the degenerate `{"scores": []}`). This is a
   retryable failure, same path as a JSON parse error. On retry exhaustion,
   missing scores default to **0.0 under `judge_style="strict"`** and 0.5
   otherwise — logged at ERROR either way, and marked per-candidate with
   `_judge_score_fallback` so a default is never mistaken for a real score.
3. **Temperature singleton fixed.** `_LLMClient` no longer holds a
   `temperature` (the first caller's value used to leak to every later
   stage). It is now a per-call `SamplingParams` argument on both the guided
   and thinking paths; every stage threads its own `temperature` through
   `generate_json`.
4. **Schema grammar cache re-keyed.** `_structured_cache` keys on
   `sha256(json.dumps(schema, sort_keys=True))` instead of `id(schema)` —
   structurally identical schemas built at different call sites now share
   one compiled grammar, and a recycled `id()` can no longer serve the wrong
   grammar.

### Fifth fix, surfaced by the above

The one-scene rerun crashed the *entire scene* when a single judge batch hit
the 2048-token guided cap and truncated mid-JSON: the malformed response
failed all 3 retries and the `JSONDecodeError` propagated out, discarding
the persona, traces, and every other activity's work. Per Phase 0.2's stated
intent ("if retries exhaust, default missing scores … log loudly either
way"), a judge call that exhausts retries with *any* failure — partial,
empty, or unparseable/truncated — now degrades to the same loud
style-dependent fallback. One bad batch can no longer kill a scene.

## Checkpoint P0 verification

**Partial-coverage path (provoked, CPU-only stub — no GPU):** all three
judge failure modes retry 3× then fall back without raising —
partial → per-index default, empty `{"scores": []}` → all default,
truncated JSON → all default; each records `_judge_score_fallback`. Warnings
fire on every attempt, an ERROR on exhaustion.

**One-scene rerun (real, Qwen3-32B, `judge_style=asis`):**
`survival=18.2% (88/483), realism=0.57, 20 changes`, all four files written
including `choices.jsonl`. In `generation_result.json`:

- 88 candidates, **0 missing** any of `_judge_score` / `_judge_stage_tag` /
  `_judge_seed` / `_selected`; 25 selected, **0 missing** `_judge_score`.
- Score histogram (rounded 0.1): `{0.3:2, 0.4:4, 0.5:49, 0.6:6, 0.7:8,
  0.8:11, 0.9:7, 1.0:1}` — real scores span 0.3–1.0, not a flat 0.5.
- `choices.jsonl`: 88 valid-JSON lines, one per candidate.

**Headline finding the fix exposed: 44 of 88 candidates (50%) carry
`_judge_score_fallback`** — the `asis` judge returned empty score arrays for
entire activity batches, which the old code silently scored 0.5 with no
marker. The frequently-cited `mean_realism_score ≈ 0.667` was therefore
heavily contaminated by silent 0.5 defaults. This is exactly the measurement
gap Phase 1's harness and Phase 2's judge work are meant to close; naming it
here so it is not re-discovered later.

Note: this degenerate emptiness is specific to the `asis` prompt; the strict
prompt is what Phase 1/2 build on and has not yet been measured this way.

## Tests

- `test_integration_fake_client`, `test_determinism`, `test_run_batch_days`:
  35 passed (fake-client `generate` signature updated for the new
  `temperature` kwarg; `score_realism_batch` tuple return exercised
  end-to-end).
- Full suite: 694 passed; the 7 failures are pre-existing working-tree
  failures unrelated to generation (3 `test_llm_prior_report`, 3
  `TestEvaluateObjectMask`, 1 `test_kernel_reliability_diagram`) — identical
  before and after this change.

## Artifacts

- Rerun output: `generation_out_p0_check/102343992_family_with_kids/`
  (verification artifact, disposable — not part of the frozen pool).
- Rerun log: showed the graceful judge fallbacks firing (ERROR lines) with
  no scene crash.

## Addendum — does strict have the same empty-array error? (one-scene check)

Re-ran the same scene under `--judge-style strict` (fresh strict judge calls,
everything else from cache). **Yes — strict has the identical pathology, at
essentially the same rate:**

| | asis | strict |
|---|---|---|
| candidates scored | 88 | 217 |
| fallback (empty/truncated judge output) | 44 (50%) | 99 (46%) |
| real judge scores | 44 (50%) | 118 (54%) |

Worse, of the 118 real strict scores, **0 used the 0.0–0.1 "absurd" band** —
every strict 0.0 in the output is a fallback default, not a real verdict.
When strict *does* respond, it clusters high (0.8→39, 0.9→22, 1.0→14), i.e.
it is not actually scoring strictly. So strict is not "the version that works
well": it fails to answer for ~half the pool and, when it answers, doesn't
behave like a strict judge. This is the strongest evidence yet that judge
quality must be *measured* (Phase 1b) before being relied on, and is exactly
what Phase 2's context + exemplars are meant to fix.

## Two root-cause fixes (post-checkpoint, at owner request)

### Reproducibility — the conflict-verification pass

Root cause: `generation/verification.py` made three `force=True` LLM calls
(regenerate conflicting trace, re-check conflicts, final conflict check).
`force=True` bypasses the cache and regenerates fresh, and vLLM is not
bit-reproducible across processes — so every run of a multi-occupant
household detected different conflicts and spliced different traces (and
line 112 also *overwrote* the base activity cache entry, which is why occ3's
cache showed 15 while the run recorded a spliced 23). `family_with_kids` has
4 occupants, so this fired every run.

Fix: replace `force=True` with content-derived, deterministic seeds.
`detect_occupant_conflicts` now folds a sha256 of the trace text into its
seed, so each round's distinct traces get their own cacheable entry;
`generate_activity_trace` gained a `variant_tag` that the resolver uses
(`conflictfix_r{round}`) to resample a conflicting occupant under a distinct
but deterministic seed, leaving the original cache entry intact. **Verified:
two independent runs now produce byte-identical traces, candidates, and
displacements** (25.2% survival, 121/480, realism 0.70, 30 changes; occupant
activity counts identical).

### Empty scores — the judge grammar

Root cause: `REALISM_SCHEMA`'s `scores` array had **no `minItems`**, so
`{"scores": []}` was grammar-legal and the model took that path ~half the
time; and each entry required a free-text `reason`, whose length pushed large
batches past the 2048-token cap and truncated the JSON.

Fix: `build_realism_schema(n)` pins the array to exactly `n` entries
(`minItems == maxItems == n`) so the grammar cannot emit an empty or partial
array, and drops the unused `reason` field so output stays compact. The
judge prompt also states the required count explicitly. **Verified: judge
fallback rate 50%/46% → 0%** on the one-scene run; all 121 candidates scored,
spread 0.1–1.0, no 0.5 pile-up. The robustness fallback from P0.2 remains as
the safety net for any residual mis-indexing.

Both fixes verified together on the same two-run experiment; the
graceful-fallback and score-persistence plumbing from P0 is unchanged.

## Open for Phase 1

- The `asis` judge's empty-array behavior is a real quality signal, not
  noise — the harness should quantify it per judge variant.
- Judge guided `max_tokens` is 2048; verbose batches truncate. Left as-is
  (judge tuning is Phase 2), but flagged.
