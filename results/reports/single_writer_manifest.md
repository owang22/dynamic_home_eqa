# Single-writer manifest enforcement

**Question:** Can a new gate script silently bypass the fingerprint/code-hash
guards by writing its own result manifest, the way two existing scripts
already had?

**Setup:** Consolidate all manifest writing into one function
(`embodied.attribution.write_result_manifest`) and add a test that scans
every `.py` file in the repo for the manifest-construction shape outside
that one function.

## Headline numbers

| check | before | after |
|---|---|---|
| Scripts constructing their own manifest dict | 2 (`embodied_m2_gate.py`, `embodied_m3_gate.py`) | 0 |
| Enforcement | none (relied on code review) | 3 automated tests, one of which greps the whole repo |

## What this means

The code-hash guard added during the coverage-repair phase was itself
bypassed by two scripts that merged several `rerun_frozen_e0` calls' rows
into a final manifest through their own separate `json.dumps` — omitting
`code_hash` entirely, the exact hole the guard was built to close. Both
scripts now route through the single writer. A new script that reintroduces
this pattern fails `tests/test_single_writer_manifest.py` immediately, not
at the next contamination audit.

## What is NOT yet supported by these numbers

- The scan is a text-pattern match (both `"milestone":` and `"fingerprint":`
  appearing as literal dict keys in the same file), not a static analyzer —
  a sufficiently obfuscated bypass (e.g. building the dict via
  `dict(milestone=..., fingerprint=...)` instead of literal braces) would
  not be caught. This is a deliberate, documented trade-off for a fast,
  dependency-free check, not a claim of completeness.

**Traceability:** fingerprint `25e52eee014c3c72`, code_hash
`05102535c7dbb01b`. Tests: `tests/test_single_writer_manifest.py`.
