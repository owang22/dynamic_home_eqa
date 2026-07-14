# Prompting Infrastructure — Phase 2 (context + exemplars + self-consistency, measured)

Everything measured against the 48-item EVAL set (human bands) or the
regenerated 3-scene comparison set. EXEMPLAR (12 items) held out of every
judge metric.

## Judge — the harness matrix

| config | ctx | fs | think | k | Spearman ↑ | exact | **over** | mean@band 0/1/2/3 |
|---|---|---|---|---|---|---|---|---|
| strict_ctx_fs_k3 | ✓ | ✓ | ✓ | 3 | **0.83** | 0.62 | 0.23 | 0.18/0.41/0.55/0.80 |
| **strict_ctx_fs (WINNER)** | ✓ | ✓ | · | 1 | 0.79 | **0.67** | **0.15** | **0.11**/0.36/0.50/0.80 |
| strict_thinking | · | · | ✓ | 1 | 0.79 | 0.46 | 0.48 | 0.32/0.55/0.73/0.85 |
| strict (P1b baseline) | · | · | · | 1 | 0.75 | 0.58 | 0.29 | 0.23/0.38/0.55/0.82 |
| strict_fs (exemplars only) | · | ✓ | · | 1 | 0.73 | 0.50 | 0.33 | 0.26/0.43/0.57/0.83 |
| strict_ctx (context only) | ✓ | · | · | 1 | 0.73 | 0.54 | 0.38 | 0.27/0.50/0.65/0.83 |
| asis | · | · | · | 1 | 0.64 | 0.54 | 0.35 | 0.45/0.40/0.60/0.88 |

**Winner: `strict_ctx_fs` (context + few-shot exemplars, k=1)** — the best
operating point for a *selection* judge:
- Spearman 0.75 → **0.79**, exact-band 58% → **67%**.
- **Over-scoring halved: 29% → 15%.** Band-0 mean 0.23 → **0.11** — it finally
  uses the "absurd" band (catches 7/10 vs 4/10 for baseline).
- 1× cost, no thinking.

**Mechanism (the key finding): context-alone and exemplars-alone each slightly
HURT** (0.73 each, and context alone *raised* over-scoring to 38%). They only
help **in combination** — context grounds who/when, exemplars anchor the scale.

**k=3 self-consistency** buys the top Spearman (0.83) but re-inflates scores
(over 23%, worse band-0) — the same thinking-inflation as strict_thinking — and
costs 3×. Use it only if pure ranking matters more than calibration.

## Model comparison — 80B MoE vs Qwen3-32B (both strict + thinking)

| model | Spearman ↑ | exact | over | mean@band 0/1/2/3 |
|---|---|---|---|---|
| Qwen3-32B (dense) | **0.79** | 0.46 | 0.48 | 0.32/0.55/0.73/0.85 |
| Qwen3-Next-80B-A3B (MoE, FP8) | 0.66 | 0.52 | 0.29 | 0.34/0.39/0.58/0.83 |

**The 80B MoE does not beat the 32B as a judge** — clearly worse on rank
correlation (0.66 vs 0.79), barely separates absurd from contrived (band-0
0.34 ≈ band-1 0.39). It over-scores less but ranks worse. No reason to switch;
the 32B is better *and* runs in-process with habitat-sim. Reinforces the
standing "bigger model ≠ better uncertainty estimator" theme.

The MoE needed a separate env (`vllm_q`: vLLM 0.25.0) and clearing four
Blackwell/sm_120 serving walls (NVCC 12.3 → FlashInfer sampler → Mamba cache
bound → unsigned-64 seed). The `vllm_q` env + `generation/http_judge.py` HTTP
client are reusable for any future out-of-process model arm.

## Regenerated comparison set (enriched proposer + winning judge)

Proposer now: per-occupant Tier-3 ownership, bedroom scoping, fixtures
excluded from the movable set, occupant_card + temporal_context +
surface_occupancy in the prompt. Judge: strict + context + exemplars. All 3
scenes regenerated (`generation_out_labelset/`, overwritten), **trace-valid**.

**Per-owner Tier-3 move counts — the shared-laptop bug is fixed.** Each owner
now has their own instance with a realistic count, and children own nothing:

| scene | laptops (per owner) | phones (per owner) | toddler Tier-3 |
|---|---|---|---|
| 102343992 | david:3, emily:2, sophie:1 | david:1, emily:2, sophie:3 | Liam: none |
| 102344022 | michael:3, emily:1 | linda:5, michael:3, emily:1 | Jacob: none |
| 102344049 | james:3, emily:1, olivia:2 | james:4, emily:3, olivia:2 | Liam: none |

(Before: one shared `laptop_1`/`laptop_2` accumulating everyone's moves,
toddlers credited with laptop moves.)

**Bedroom monopoly fixed** — moves spread across bedrooms per occupant:

| scene | bedroom_1 | bedroom_2 | bedroom_3 |
|---|---|---|---|
| 102343992 | 6 | 3 | 1 |
| 102344022 | 12 | 6 | — |
| 102344049 | 15 | 6 | 1 |

**Zero fixtures moved** (fridge/tv/wardrobe/counter/oven) across all 3 scenes —
they remain anchors for near/next_to, never carried objects.

Note: `mean_realism(selected)` dropped to ~0.49 (from ~0.67). Expected — the
well-calibrated strict+exemplar judge uses the low bands, so selected scores
are lower; it's being appropriately selective, not worse.

**On the web server.** Realized-day artifacts + render media were built for
all 3 regenerated scenes from `generation_out_labelset/` (via a new `--gen-dir`
flag on `build_realized_day` / `realism_render_job`, so the frozen experiment
pool in `generation_out/` is untouched). Placement success was near-total —
102343992 41/41 ok, 102344022 48/52 ok, 102344049 69/69 ok (mostly snap_down),
consistent with the enriched proposer emitting well-groundable placements. 32
render items (495 panels) across the 3 scenes → `render_manifest.json`. Serve:

    python -m uvicorn dynamic_home_eqa.webapp.realism_eval.app:app --host 127.0.0.1 --port 8000

## Generalization caveats (from the prompt review)

- **Exemplars are `family_with_kids`-flavored** (rationales reference
  toddlers/teens). The archetypes generalize, the phrasings don't — re-sample
  the EXEMPLAR pool across profiles when the scene pool broadens beyond these 3.
- **The judge is fed the proposer's own `reason`**, which can be a persuasive
  post-hoc rationalization for an implausible move — a possible over-scoring
  lever to A/B (drop/down-weight `reason` in the judge's view) if needed.

## Retired / parked

`llm_prior/` (renamed `llm_OLD/` by owner) — the FM-as-uncertainty-estimator
research line, orthogonal to the prompting pipeline and no longer imported by
generation/judge/qa/env.

## Open — Phase 3 (gated on sign-off)

Sequential state threading: generate→ground→judge→select per chronological
window against a running `{instance: location}` state, so the proposer/judge
reason against authoritative current state instead of the proposer's
`assumed_from` guess. This also makes `surface_occupancy` live (it is
start-of-day today) and enables restorative/tidying events.
