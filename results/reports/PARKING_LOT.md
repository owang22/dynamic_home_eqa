# Parking lot

Ideas raised during review that are not must-fixes (don't block a headline
number) and are not queued. One line each. Revisit if a future headline
number is demonstrably wrong for a related reason — otherwise leave parked.

- `env/inventory.py`'s `load_scene_state`/`inventory_for_generation` are
  `@lru_cache`'d by bare `scene_id`, process-wide, with no per-test reset.
  Found while writing `tests/test_llm_prior_targets.py`: running the full
  suite gives scene 102343992 a different (clutter-inclusive) furniture
  census than calling the same function fresh — some other test
  observably populates the cache differently before that test runs.
  Worked around locally (test now uses a synthetic category name instead
  of a real one), not investigated further — no headline number depends
  on `inventory_for_generation`'s cache being test-order-independent
  today, but a future consumer that does would hit this.
