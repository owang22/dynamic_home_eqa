"""
generation/ — LLM-driven offline dataset generation for Dynamic Home EQA.

Three stages, each a separate LLM call:
  1. Persona       — who lives here, schedule tendencies, tidiness scalar.
  2. Activity trace — realized activities with continuous start/end times.
  3. Displacement  — which objects move and to what spatial relationship.

Grounding: every displacement is validated by PARTNR's simulation before
acceptance. Ungroundable proposals are rejected by the simulator, not the LLM.

All calls are seeded from (household_id, day, stage, occupant_index) for
exact reproducibility. Raw LLM responses are cached to disk keyed by seed.
"""
