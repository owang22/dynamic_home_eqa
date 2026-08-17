# Anchor validation report -- regime_pet_heavy_v1

- profile: `profiles/manual/regime_pet_heavy_v1.yaml`
- status: **VERIFIED**  (loader refuses DRAFT in bank builds unless --allow-draft)
- overall: **WARN**  (0 FAIL, 1 WARN, 2 NEEDS_DATA)

| check | status | detail |
|---|---|---|
| V1 no-double-placement | PASS | ok |
| V2 referential | PASS | ok |
| V3 block-overlap | WARN | [V3 WARN] R1: 'morning_walk' and 'feed_pets' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'feed_pets' and 'breakfast' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'breakfast' and ... |
| V4 probabilities | PASS | ok |
| V5 alias-normalize | PASS | ok |
| V6a ATUS timing | NEEDS_DATA | 5 [ATUS] schedule block(s) to check; place ATUS zips in data/anchors/atus/raw (bls.gov unreachable); then compile percentile bands per atus_code_map.yaml |
| V6b HOMER jitter | SKIP | no [HOMER]-tagged jitter values |
| V6c emergent hazard | NEEDS_DATA | emergent per-class daily change rates computed (top: phone=5.214, fork=4.286, plate=3.143, coffee_mug=2.786, chew_toy=2.571, bowl=2.357, blanket=2.071, cushion=1.286); HOMER band NEEDS_DATA, literature tier NEEDS_HUMAN_TRANSCRIPTION -> b... |
| V6d BDDL bindings | SKIP | no [BEHAV]-tagged activity objects |
| V6e Housekeep placement | SKIP | no [HKEEP]-tagged placements |

NEEDS_DATA checks are non-gating (anchor not yet present). Only FAIL blocks a VERIFIED flip.
