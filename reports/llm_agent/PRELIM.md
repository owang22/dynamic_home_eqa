# LLM World Knowledge + Reasoning Under Information Age — PRELIMINARY RESULTS (v2, post-rigor)

Model: local Qwen3.6-35B-A3B (guided JSON, seeded, temp 0.2). Scenes: 2 new-protocol
episodes (family 102344049, roommates 102344022). Main bank: wake-up snapshot 08:00,
single-decision queries at Δt ∈ {1,4,9,13}h, 18 stratified targets/scene, day 10.
Raw artifacts: `prelim_episodes*.parquet`, `prelim_a2x.parquet`, `prelim_moved_bank.parquet`,
`normative_bank.parquet`, `hazard_probe_raw.json`, `hazard_robustness.json`,
`hazard_clarified.json`.

**Scope:** one model (frontier axis pending — the API upgrade), two scenes, one day,
single-decision episodes. v2 adds the rigor pass: normative reference, positive control,
moved-object enrichment, elicitation robustness, and two artifact fixes.

---

## 1. World knowledge (hazard probe, spec 2.4) — robust, miscalibrated

Elicited P(different room after Δt) per class vs ground-truth displacement hazards:

- **Ordering knowledge is real and stable.** Pooled Spearman across 3 seeds: family
  {+0.48, +0.59, +0.63}, roommates {+0.86, +0.79, +0.80} (RIGOR: multi-seed re-elicitation).
- **The 3–6× scale bias is real miscalibration, not definition slippage.** A clarified
  prompt (at-Δt snapshot, explicitly excluding moved-and-returned) leaves the bias intact
  (family 6.6×, roommates 4.1×) with rank correlation intact (+0.74/+0.72).
- Caveat (R1): bias is measured against *our sim's* activity level; part of it may be the
  sim being calm rather than the LLM being wrong about households.

## 2. The normative reference (RIGOR-1) — what SHOULD an agent do here?

B-ladder + VoI run on the *identical* 144-episode bank (same snapshot info state, one
look max), plus a GT-hazard threshold rule:

| policy | resense rate | acc | looks by stratum (sta/occ/dyn) |
|---|---|---|---|
| GT-hazard-rational (c=0.05 / 0.10) | 0.167 / 0.056 | — | concentrated on dynamic |
| B2+VoI (c=0.05) | 0.340 | 0.924 | **0.00** / 0.56 / 0.46 |
| B3+VoI (c=0.05) | 0.597 | 0.799 | 0.40 / 0.67 / 0.73 |
| LLM A1/A2 | 0.000 | 0.924 | 0 / 0 / 0 |
| LLM A3 | 0.347 | 0.917 | 0.06 / 0.46 / 0.52 |

Three consequences:
- **Zero resensing is *nearly* rational in aggregate on this calm bank** (GT-rational
  6–17%; B2+VoI matches the LLM's 0.924 while sensing 34%). So "the LLM never resenses"
  is NOT by itself a failure — the original Finding 2 headline is retired.
- **What remains a failure is discrimination and confidence**: B2 at any cost puts ALL
  its sensing on occasional/dynamic objects (static = 0.00) and its belief decays with
  staleness; the LLM shows zero discrimination and flat 0.95 confidence at every
  staleness (stated 0.95 vs realized 0.861 at Δt=13h).
- **A3 over-senses ≈2× the GT-rational rate** — the valence of the scaffold result flips:
  it reconnects knowledge to action, but imports the 3–6× inflated priors (31% resense on
  1-hour-fresh memories). And notably **B3+VoI underperforms parroting** (0.799 — its
  return-prediction bias, cf. the day-budget report): the literature centerpiece is not
  the ceiling in snapshot-anchored regimes; B2 is.

## 3. The agent ladder (with controls)

| variant | resense | answer acc | conf | status |
|---|---|---|---|---|
| A0 blind | — | 0.583 (chance 0.10) | 0.82 | prior floor, OpenEQA echo |
| A1 ages hidden | 0.000 | 0.924 | 0.95 | parrots memory 100.0% literally |
| A2 ages visible | 0.000 | 0.924 | 0.95 | ≡ A1 answer-for-answer |
| A2n neutral framing | 0.000 | 0.924* | 0.93 | framing controlled |
| **A2x positive control** | **0.708** | — | — | interface NOT a degenerate attractor |
| A3 scaffolded | 0.347 | 0.917 | 0.60 | knowledge reaches the action head |

\* A2n's originally-reported 0.868 was a **scoring artifact** (RIGOR-6): all 8 changed
answers were one chair whose memory said `dining` while the scene's census carries both
`dining` and `dining_room` as distinct labels; neutral framing made the model normalize
the synonym. Alias-tolerant scoring restores 0.924 — behavior identical. The harness now
dedupes room options and scores through `rooms_match` (fixed for all future runs).

**Positive control (RIGOR-3):** with the target's memory row *omitted* — resensing
trivially correct — the SAME A2 prompt/schema/decoding produces resense = **0.708**
(from 0.000). The zero-resense null is a decision, not a guided-decoding basin. (The
other 29% guessed from priors at 0.417 accuracy — itself a mini-finding: it sometimes
prefers a prior guess over a free look even with no memory.)

**Moved-object bank (RIGOR-4):** the punchline cell fattened from n=8 to n=80/variant by
importance-sampling query times after true transitions (calm bank kept as contrast).
Effective accuracy (resense executes → correct):

| variant | resense | effective acc | conf |
|---|---|---|---|
| A1 | 0.000 | **0.062** | 0.95 |
| A2 | 0.087 | 0.150 | 0.88 |
| A3 | 0.463 | 0.463 | 0.42 |

On objects that actually moved, the spontaneous agent is 94% wrong at 95% confidence;
age-visibility helps marginally; the scaffold recovers half. Confidence finally tracks
reality only in A3 (0.42 stated vs 0.46 realized).

## 4. Revised findings (defensible forms)

1. **Ordering-without-calibration** world knowledge: multi-seed stable, semantics
   controlled; 3–6× hot relative to this sim.
2. **Flat-confidence memory parroting, not "irrational inaction":** the LLM's zero
   sensing is near-rational in aggregate here, but it parrots memory literally (100.0%),
   holds 0.95 confidence regardless of staleness, shows zero volatility discrimination
   (vs B2's perfect static-0.00 allocation), and is 94%-wrong-at-95%-confidence exactly
   where information age bites. A1≡A2 answer-for-answer plus the A2x control make this a
   *decision-level* property, cleanly measured.
3. **Knowledge–behavior dissociation, both directions:** unscaffolded it ignores its own
   (inflated) hazard beliefs; scaffolded it obeys them — including their miscalibration
   (over-sensing fresh memories ≈2× GT-rational). Cross-probe consistency ρ=+0.67 between
   A3's in-context estimates and its own elicited curves.
4. **Class, not time:** scaffolding restores volatility discrimination
   (0.06/0.46/0.52) but elapsed-time sensitivity stays weak (est_p_moved vs Δt ρ=+0.22;
   resense rate non-monotone in Δt). The A3 threshold at est≈0.6 should be described as
   **scaffold-induced**, not an intrinsic decision rule.

## 5. Ready-for-API-model checklist (the frontier axis, reviewer item #2)

- Harness fixes in: room-option dedup + alias-tolerant scoring; positive-control (A2x)
  and moved-bank generators are reusable as-is; episode bank is frozen and seeded.
- `llm_agent/clients.py` has the client interface: local Qwen (tested) + an Anthropic
  stub (untested — needs a key). Protocol differences to report when comparing: no guided
  grammar and no seed on the API side (prompted-JSON + validation, temp 0).
- Run order for the API model: A1/A2 on the main bank (does the null replicate at
  scale?), A2x control, moved bank, hazard probe (3 seeds). ~700 calls total per model.

## 6. Open items

- R1: sim calmness — activity scale-up or multi-day staleness would raise the price of
  age-blindness; day-budget scheduler already supports transition-adjacent querying.
- Normative decision-quality regret (spec Phase 2) vs B2+VoI per episode — computable
  from existing parquets; not yet reported.
- Multi-step ReAct + shared day budget: harness exists (day_loop); LLM policy adapter
  not yet written.
