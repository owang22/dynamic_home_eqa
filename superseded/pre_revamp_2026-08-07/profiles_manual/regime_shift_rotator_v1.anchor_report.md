# Anchor validation report -- regime_shift_rotator_v1

- profile: `profiles/manual/regime_shift_rotator_v1.yaml`
- status: **VERIFIED**  (loader refuses DRAFT in bank builds unless --allow-draft)
- overall: **WARN**  (0 FAIL, 1 WARN, 2 NEEDS_DATA)

| check | status | detail |
|---|---|---|
| V1 no-double-placement | PASS | ok |
| V2 referential | PASS | ok |
| V3 block-overlap | WARN | [V3 WARN] R1: 'sleep' and 'shift_prep' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'shift_prep' and 'leave_early' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'leave_early' and '... |
| V4 probabilities | PASS | ok |
| V5 alias-normalize | PASS | ok |
| V6a ATUS timing | NEEDS_DATA | 3 [ATUS] schedule block(s) to check; place ATUS zips in data/anchors/atus/raw (bls.gov unreachable); then compile percentile bands per atus_code_map.yaml |
| V6b HOMER jitter | SKIP | no [HOMER]-tagged jitter values |
| V6c emergent hazard | NEEDS_DATA | emergent per-class daily change rates computed (top: phone=2.857, thermos=2.286, fork=1.643, keys=1.571, work_badge=1.5, plate=1.5, laptop=1.286, hi_vis_vest=1.071); HOMER band NEEDS_DATA, literature tier NEEDS_HUMAN_TRANSCRIPTION -> ban... |
| V6d BDDL bindings | SKIP | no [BEHAV]-tagged activity objects |
| V6e Housekeep placement | SKIP | no [HKEEP]-tagged placements |

NEEDS_DATA checks are non-gating (anchor not yet present). Only FAIL blocks a VERIFIED flip.
