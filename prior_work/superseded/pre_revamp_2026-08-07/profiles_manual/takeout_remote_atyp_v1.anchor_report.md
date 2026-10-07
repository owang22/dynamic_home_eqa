# Anchor validation report -- takeout_remote_atyp_v1

- profile: `profiles/manual/takeout_remote_atyp_v1.yaml`
- status: **DRAFT**  (loader refuses DRAFT in bank builds unless --allow-draft)
- overall: **WARN**  (0 FAIL, 1 WARN, 3 NEEDS_DATA)

| check | status | detail |
|---|---|---|
| V1 no-double-placement | PASS | ok |
| V2 referential | PASS | ok |
| V3 block-overlap | WARN | [V3 WARN] R1: 'sleep' and 'morning_prep' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'morning_prep' and 'desk_work_am' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'desk_work_am'... |
| V4 probabilities | PASS | ok |
| V5 alias-normalize | PASS | ok |
| V6a ATUS timing | NEEDS_DATA | 5 [ATUS] schedule block(s) to check; place ATUS zips in data/anchors/atus/raw (bls.gov unreachable); then compile percentile bands per atus_code_map.yaml |
| V6b HOMER jitter | NEEDS_DATA | 1 [HOMER] jitter value(s) to check; parsed 195 routines but no clean per-activity start alignment; HOMER routine schema needs a bespoke parser |
| V6c emergent hazard | NEEDS_DATA | emergent per-class daily change rates computed (top: fork=3.929, phone=3.5, mug=3.214, water_bottle=2.214, takeout_container=2.0, plate=1.857, remote_control=0.571, laptop=0.571); HOMER band NEEDS_DATA, literature tier NEEDS_HUMAN_TRANSC... |
| V6d BDDL bindings | SKIP | no [BEHAV]-tagged activity objects |
| V6e Housekeep placement | SKIP | no [HKEEP]-tagged placements |

NEEDS_DATA checks are non-gating (anchor not yet present). Only FAIL blocks a VERIFIED flip.
