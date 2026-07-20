"""Profile-driven symbolic household system (profile_schema_v1).

The v2 revamp's world engine: a provenance-tagged YAML profile (who lives
here, their weekly schedule, activity->object bindings, placement homes)
deterministically generates receptacle-level movement logs in the exact
episode format ReplayWorld consumes — no Habitat, no LLM in the loop.

  schema.py      loader + structural validator V1-V5 (alias normalization at load)
  transforms.py  the four REGISTERED atypicality transformations (pure functions;
                 the only sanctioned way to produce atypical profiles)
  generator.py   profile -> N-day event/snapshot logs (jitter, during/after
                 branches, misplacement noise, dish-cycle)

Profiles live in profiles/manual/*.yaml at the repo root. Typical profiles
may be model-drafted but count only once a human verifies provenance tags
and flips status to VERIFIED; atypical profiles are NEVER hand- or
model-authored — transforms.py only.
"""
from dynbelief.profiles.schema import (  # noqa: F401
    Profile, Finding, load_profile, profile_from_dict, validate_structural,
)
