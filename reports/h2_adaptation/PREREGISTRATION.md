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
