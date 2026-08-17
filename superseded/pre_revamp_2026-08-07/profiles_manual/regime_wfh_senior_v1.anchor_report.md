# Anchor validation report -- regime_wfh_senior_v1

- profile: `profiles/manual/regime_wfh_senior_v1.yaml`
- status: **VERIFIED**  (loader refuses DRAFT in bank builds unless --allow-draft)
- overall: **WARN**  (0 FAIL, 1 WARN, 2 NEEDS_DATA)

| check | status | detail |
|---|---|---|
| V1 no-double-placement | PASS | ok |
| V2 referential | PASS | ok |
| V3 block-overlap | WARN | [V3 WARN] R1: 'sleep' and 'morning_meds' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'morning_meds' and 'breakfast' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'desk_setup' and ... |
| V4 probabilities | PASS | ok |
| V5 alias-normalize | PASS | ok |
| V6a ATUS timing | NEEDS_DATA | 5 [ATUS] schedule block(s) to check; place ATUS zips in data/anchors/atus/raw (bls.gov unreachable); then compile percentile bands per atus_code_map.yaml |
| V6b HOMER jitter | SKIP | no [HOMER]-tagged jitter values |
| V6c emergent hazard | NEEDS_DATA | emergent per-class daily change rates computed (top: coffee_mug=3.429, plate=3.286, fork=3.0, bowl=2.929, reading_glasses=2.5, phone=2.5, pill_organizer=1.714, remote=1.643); HOMER band NEEDS_DATA, literature tier NEEDS_HUMAN_TRANSCRIPTI... |
| V6d BDDL bindings | SKIP | no [BEHAV]-tagged activity objects |
| V6e Housekeep placement | SKIP | no [HKEEP]-tagged placements |

NEEDS_DATA checks are non-gating (anchor not yet present). Only FAIL blocks a VERIFIED flip.
