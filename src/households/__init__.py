"""Attribute-first household dataset pipeline (self-contained).

Successor to src/revamp_v2 for the ~50-household attribute-first set.
Everything version-specific is vendored here (see per-file provenance
headers); the only imports from elsewhere in the repo are the genuinely
shared infrastructure modules dynamic_home_eqa.generation.{llm_client,
cache, hosted_spend}. Nothing here reads the old revamp trees (old_profiles/) — that isolation is enforced by an actual test
(tests/households/test_isolation.py), not a claim.

Data lives in profiles/households/ (YAML and JSON only, never code).
"""
