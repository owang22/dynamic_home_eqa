# Anchor validation report -- regime_wfh_hybrid_v1

- profile: `profiles/manual/regime_wfh_hybrid_v1.yaml`
- status: **VERIFIED**  (loader refuses DRAFT in bank builds unless --allow-draft)
- overall: **WARN**  (0 FAIL, 2 WARN, 3 NEEDS_DATA)

| check | status | detail |
|---|---|---|
| V1 no-double-placement | PASS | ok |
| V2 referential | PASS | ok |
| V3 block-overlap | WARN | [V3 WARN] R1: 'morning_prep' and 'breakfast' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'wfh_setup' and 'wfh_work_am' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'wfh_work_am' ... |
| V4 probabilities | PASS | ok |
| V5 alias-normalize | PASS | ok |
| V6a ATUS timing | NEEDS_DATA | 8 [ATUS] schedule block(s) to check; place ATUS zips in data/anchors/atus/raw (bls.gov unreachable); then compile percentile bands per atus_code_map.yaml |
| V6b HOMER jitter | NEEDS_DATA | 2 [HOMER] jitter value(s) to check; parsed 195 routines but no clean per-activity start alignment; HOMER routine schema needs a bespoke parser |
| V6c emergent hazard | NEEDS_DATA | emergent per-class daily change rates computed (top: phone=3.214, fork=3.0, coffee_mug=2.857, plate=2.643, bowl=1.643, remote=0.643, keys=0.643, laptop=0.571); HOMER band NEEDS_DATA, literature tier NEEDS_HUMAN_TRANSCRIPTION -> band non-... |
| V6d BDDL bindings | SKIP | no [BEHAV]-tagged activity objects |
| V6e Housekeep placement | WARN | 0 [HKEEP] placement(s) plausible per Housekeep; not in Housekeep vocab (uncheckable): ['keys'] |

NEEDS_DATA checks are non-gating (anchor not yet present). Only FAIL blocks a VERIFIED flip.
