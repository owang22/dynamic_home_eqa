"""Charter-driven symbolic household system (charter_schema_v1).

The v2 revamp's world engine: a provenance-tagged YAML charter (who lives
here, their weekly schedule, activity->object bindings, placement homes)
deterministically generates receptacle-level movement logs in the exact
episode format ReplayWorld consumes — no Habitat, no LLM in the loop.

  schema.py      loader + structural validator V1-V5 (alias normalization at load)
  transforms.py  the four REGISTERED atypicality transformations (pure functions;
                 the only sanctioned way to produce atypical charters)
  generator.py   charter -> N-day event/snapshot logs (jitter, during/after
                 branches, misplacement noise, dish-cycle)

Charters live in charters/manual/*.yaml at the repo root. Typical charters
may be model-drafted but count only once a human verifies provenance tags
and flips status to VERIFIED; atypical charters are NEVER hand- or
model-authored — transforms.py only.
"""
from dynbelief.charters.schema import (  # noqa: F401
    Charter, Finding, load_charter, charter_from_dict, validate_structural,
)
