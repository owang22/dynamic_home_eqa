# Confirmatory run — PRE-REGISTRATION (written before any confirmatory LLM call)

Frozen from the E5 design study: the regime prompt (`e5_regime._SYS`), the schema
(`REGIME_SCHEMA`), and the digest format ("Day D, HH:MM — obj seen at rec"). Three
NEW confusable pairs, unseen during design. Query design uniform (regime-dependent
TARGETS + matched CONVENTIONAL held-out objects × a fixed weekday grid), clustered
bootstrap CIs by household. Run on DeepSeek-V4-Flash, Qwen3.6-35B-A3B, GLM-4.5-Air.

## Human-predictability precheck (all pass)
Each persona's routine is inferable by a human from the diagnostic sightings:
gardening gloves + watering can at 09:00 ⇒ retiree gardener; headset/webcam/laptop
persisting at a desk ⇒ remote worker; sippy cup + board book ⇒ toddler; dog leash +
food bowl ⇒ pets; badge + hi-vis vest leaving pre-dawn ⇒ shift worker; suitcase +
passport then a multi-day gap ⇒ traveler. Confirmed in simulation that each regime
FLIPS the shared object (retiree mug→patio vs wfh→desk; toddler cushion→play_mat vs
pet→pet_bed; rotator laptop→desk-evening vs traveler→away).

## Pre-registered per-household predictions (named vs anon on TARGETS)

| household | class | prediction |
|---|---|---|
| retiree_gardener | **semantics-necessary** | named >> anon (must know "gardening gloves"⇒garden) |
| wfh_senior | **structure-sufficient** | named ≈ anon (objects visibly persist at the desk) |
| toddler_home | **semantics-necessary** | named >> anon (sippy_cup⇒toddler⇒play mat) |
| pet_heavy | **semantics-necessary** | named >> anon (dog_leash⇒pets⇒pet bed) |
| shift_rotator | **semantics-necessary** | named >> anon (badge/vest⇒shift⇒shifted presence) |
| frequent_traveler | **structure-sufficient** | named ≈ anon (multi-day absence is visible) |

"named >> anon" scored as named−anon > 0.10; "named ≈ anon" as |named−anon| ≤ 0.10.

## Pre-registered aggregate predictions
1. **Targets (regime-flipped):** llm_named > class_freq > classical(=0). If
   llm_named ≤ class_freq on targets, the claim does NOT survive the strong baseline.
2. **Conventional objects:** class_freq ≥ llm_named (the table is reliable on
   typical placements); classical still ~0 (per-edge, held-out).
3. **E4 hybrid:** ≈ llm_named on targets AND ≈ class_freq on conventional →
   dominates both single-arm endpoints across the mixed set.
4. **Mechanism:** the aggregate named−anon gap on targets is positive and driven by
   the semantics-necessary households, near-zero on the structure-sufficient ones.
5. **Cross-model:** the qualitative ordering (named > class_freq > classical on
   targets; named−anon gap on semantics households) holds for all three models;
   magnitudes may differ with capability.

A result is a WIN if predictions 1, 2, and 4 hold with non-overlapping-ish CIs on
the aggregate; per-household (5-way) hits are secondary evidence.

---

# Addendum — E7 v2 (events-observed learning curves) + evidence-routed hybrid

Written when reworking E7 after the reviewer notes on aggregation, the C3 crash,
and the frozen classical.

## Frozen classical: C3g (gated periodic GLM)
The single named "vs classical" opponent for ALL remaining claims (curves, hybrid).
Rule: persistence/constant everywhere by default; the per-object periodic GLM is
enabled ONLY when it beats the constant model on that object's own held-out
observation likelihood by ≥ 0.7 nats/point (MDL gate). This removes the ungated-C3
anti-learning crashes (pet cushion 0.86→0.29, sparse shift laptop) — where the
sparse periodic fit underperformed persistence — while preserving the genuine
weekly cycle (retiree coffee_mug → 1.0). C1 (pure persistence) is a strawman in one
direction; ungated C3 is a strawman in the other. C3g is the strongest honest
classical. Implemented in `dynbelief/classical/rates/c3g_gated.py`, arm "C3g".

## E7 v2 methodology (frozen)
x-axis = EVENTS-OBSERVED k of the target object (0,1,2,4,8,16), NOT days (days
confound rarity). Pooled over all 18 regime-conditioned target objects × 6
confirmatory households, stratified into rarity terciles (rare ≤47, medium ≤78,
frequent >78 events/30d), clustered bootstrap CIs (cluster = household×object).
Observations from days [0,21); true forward test on days [21,28) at the regime
hour. LLM gets persona diagnostic digest + first-k target events (k=0 = persona
only); classical (per-edge) gets first-k target events only.

Stated predictions (E7 v2):
- **P1 (cold start):** at k=0, LLM > 0 and classical = 0 in every stratum (per-edge
  classical has nothing without target events; the LLM transfers from the persona).
- **P2 (frequent crossover):** in the FREQUENT tercile, C3g overtakes the LLM by
  k=16 (dense events let it learn the cycle); C1 does not (no periodic term).
- Middle-k differences are NOT predicted significant (n=6/tercile, wide CIs); a
  single recent observation of a stable regime object is expected to let classical
  catch up — so the LLM's edge is concentrated at cold-start, not sustained.

## Evidence-routed hybrid (E4 v2) — stated claim
Routing rule (frozen from DEV bank atyp_regime_v1 only): per object, route to the
LLM's regime prediction when observed events < τ*, else to frozen C3g. τ* = the
smallest k at which pooled C3g ≥ pooled LLM on the DEV bank. Frozen, then applied
unchanged to the confirmatory bank.
- **Claim:** within EVERY rarity stratum, hybrid accuracy ≥ max(LLM, C3g). It
  inherits the LLM cold-start edge (few events → LLM) and the classical ceiling
  (many events → C3g). Evaluated on the confirmatory-bank E7 rows.

---

# Addendum — Reflective memory (written before the confirmatory reflective run)

New architecture (`src/dynbelief/reflect/`): an online LLM agent lives through days
0-13 of the FULL event stream (diagnostics + targets + conventional distractors —
every object movement), reflecting nightly into a memory file: up to 15 curated
evidence lines + top-3 persona hypotheses with probabilities (add/sharpen/REMOVE as
evidence arrives). Hypothesis entropy H is the agent's own uncertainty signal.

FROZEN before the confirmatory run: the reflection prompt/schema and query prompt
(`reflect/memory.py`), checkpoint grid [1,2,3,5,7,10,14] days, fixed future test
week (days 14-20), the entropy mapping w = 1 − H/log2(3), and kappa_max* = 1
(dev sweep over {1,2,3,5,8}: acc .543/.514/.495/.452/.462 — light prior wins).

Arms (ALL fit/answer from the identical stream): classical C3g/C1 (statistical
updating); llm_direct (semantic only, curated memory ONLY); llm_nomem (semantic
only, raw uncurated digest); fusion (both: per-query memory-conditioned LLM belief
injected as kappa_eff = round(1·w) days of pseudo-obs into the target's edge, base
model real-data); fusion_flat (kappa_eff = kappa_max always — isolates the entropy
gate).

Stated predictions:
- P1: fusion ≥ both llm_direct and classical_C3g pooled (dev showed .543 vs .429/.424;
  predicted to transfer).
- P2: llm_direct ≈ llm_nomem despite ~15 lines vs ~hundreds — curation retains the
  regime signal (if direct > nomem, curation actively helps reasoning).
- P3: entropy declines over days as evidence accumulates; households whose personas
  are semantically obvious converge fastest.
- P4: fusion ≥ fusion_flat where memory is uncertain early (the gate defers to
  statistics exactly when the LLM doesn't know yet).
