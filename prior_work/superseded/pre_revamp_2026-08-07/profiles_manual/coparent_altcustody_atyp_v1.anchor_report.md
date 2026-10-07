# Anchor validation report -- coparent_altcustody_atyp_v1

- profile: `profiles/manual/coparent_altcustody_atyp_v1.yaml`
- status: **DRAFT**  (loader refuses DRAFT in bank builds unless --allow-draft)
- overall: **WARN**  (0 FAIL, 1 WARN, 3 NEEDS_DATA)

| check | status | detail |
|---|---|---|
| V1 no-double-placement | PASS | ok |
| V2 referential | PASS | ok |
| V3 block-overlap | WARN | [V3 WARN] R1: 'morning_prep' and 'breakfast' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'breakfast' and 'leave_work' can overlap under jitter (generator clamps sampled starts); [V3 WARN] R1: 'away_at_work' ... |
| V4 probabilities | PASS | ok |
| V5 alias-normalize | PASS | ok |
| V6a ATUS timing | NEEDS_DATA | 14 [ATUS] schedule block(s) to check; place ATUS zips in data/anchors/atus/raw (bls.gov unreachable); then compile percentile bands per atus_code_map.yaml |
| V6b HOMER jitter | NEEDS_DATA | 3 [HOMER] jitter value(s) to check; parsed 195 routines but no clean per-activity start alignment; HOMER routine schema needs a bespoke parser |
| V6c emergent hazard | NEEDS_DATA | emergent per-class daily change rates computed (top: phone=4.286, plate=4.214, bowl=3.571, fork=3.214, knife=2.643, water_glass=2.143, pan=2.071, cup=2.071); HOMER band NEEDS_DATA, literature tier NEEDS_HUMAN_TRANSCRIPTION -> band non-ga... |
| V6d BDDL bindings | PASS | 4 [BEHAV] object(s) matched their activity's BDDL synset union |
| V6e Housekeep placement | PASS | 9 [HKEEP] placement(s) plausible per Housekeep |

NEEDS_DATA checks are non-gating (anchor not yet present). Only FAIL blocks a VERIFIED flip.
