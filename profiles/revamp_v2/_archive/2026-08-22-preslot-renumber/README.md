# Archived 2026-08-22 — pre-renumber household set

Everything generated before control.yaml was rebalanced and RENUMBERED
(typical-first ordering; a plain working solo adult became hh_001 and
night_shift_worker_solo moved to hh_010). These directories are still
internally consistent — each persona.yaml/meta.json carries its own
household_type — but their hhN names no longer match the slot of the same
number, so they must not be mixed with new output.

  hh1  = night_shift_worker_solo   (slot hh_001 is now working_professional_solo)
  hh2  = family_young_children     (type deleted from the set)
  hh4  = college_roommates         (slot hh_004 is now family_teen_and_child)
  hh10 = couple_with_toddler       (slot hh_010 is now night_shift_worker_solo)

Also predates the v3 object contract (after-only dists with NO_OP,
synthesized during legs, staged L2 with judgment blocks), so the object
layer is not comparable to anything generated after it either.

Kept for provenance only. The viewer skips `_archive/` by design.
