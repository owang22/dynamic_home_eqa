"""Anchor data acquisition + automated profile checks (anchor_checks_brief).

Compiles five external anchor datasets into machine-checkable validation
bounds for profile_schema_v1 YAMLs.

  fetch_all.py         idempotent clone/download of Anchors 1-4 into
                       third_party/ + data/anchors/ (gitignored); ATUS
                       (bls.gov, unreachable here) prints NEEDS_DATA.
  compile_envelope.py  raw anchors -> envelope.yaml (committed, provenance
                       per bound, band-multiplier config block at the top).
  validate_profile.py  V1-V5 (structural, from profiles.schema) + V6a-V6e
                       (anchor checks); writes anchor_report.md; nonzero exit
                       on any FAIL. The bank builder calls this and refuses
                       profiles not fully PASS/WARN with status VERIFIED.

Committed config/mapping tables (this directory):
  envelope.yaml            compiled bounds + band config  (compile_envelope output)
  homer_class_map.yaml     our object class -> HOMER+ classes   [draft, low-conf rows]
  bddl_activity_map.yaml   our activity -> BDDL activities       [draft]
  atus_code_map.yaml       our activity -> ATUS activity codes   [draft]
  literature_constants.yaml  Anchor 5 (human transcribes numbers; TODO placeholders)

Hard rules honored: no LLM fills numeric constants/bounds (they come from
parsed data or human transcription); name-to-name hand mappings are drafted
here with confidence tags for human review; raw data stays out of git.
"""
import pathlib

ANCHORS_DIR = pathlib.Path(__file__).resolve().parent
ENVELOPE_PATH = ANCHORS_DIR / "envelope.yaml"
