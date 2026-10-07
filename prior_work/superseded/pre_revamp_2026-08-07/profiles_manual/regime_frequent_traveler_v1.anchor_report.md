# Anchor validation report -- regime_frequent_traveler_v1

- profile: `profiles/manual/regime_frequent_traveler_v1.yaml`
- status: **VERIFIED**  (loader refuses DRAFT in bank builds unless --allow-draft)
- overall: **WARN**  (0 FAIL, 1 WARN, 2 NEEDS_DATA)

| check | status | detail |
|---|---|---|
| V1 no-double-placement | PASS | ok |
| V2 referential | PASS | ok |
| V3 block-overlap | WARN | [V3 WARN] R1: 'sleep' and 'morning_prep' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'morning_prep' and 'breakfast' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'breakfast' and '... |
| V4 probabilities | PASS | ok |
| V5 alias-normalize | PASS | ok |
| V6a ATUS timing | NEEDS_DATA | 5 [ATUS] schedule block(s) to check; place ATUS zips in data/anchors/atus/raw (bls.gov unreachable); then compile percentile bands per atus_code_map.yaml |
| V6b HOMER jitter | SKIP | no [HOMER]-tagged jitter values |
| V6c emergent hazard | NEEDS_DATA | emergent per-class daily change rates computed (top: phone=2.0, coffee_mug=1.5, plate=1.286, bowl=1.143, fork=1.071, packing_cubes=0.643, toiletry_bag=0.571, passport=0.571); HOMER band NEEDS_DATA, literature tier NEEDS_HUMAN_TRANSCRIPTI... |
| V6d BDDL bindings | SKIP | no [BEHAV]-tagged activity objects |
| V6e Housekeep placement | SKIP | no [HKEEP]-tagged placements |

NEEDS_DATA checks are non-gating (anchor not yet present). Only FAIL blocks a VERIFIED flip.
