# D1 kernel generalization (core)

**Question:** Can belief kernels be pooled across scenes sharing a
household profile, instead of each scene fitting its transition kernels
from its own data alone?

**Setup:** Build the three prerequisites — a cross-scene-portable slot key
(category + room, not a literal per-scene anchor string), a qualification-time
check that a scene's anchors all map to a known room, and a 3-level
count-weighted backoff (scene → profile → global) — as generic, tested
building blocks, without yet wiring them to real multi-scene data (the pool
was still landing new profiles as this work was done).

## Headline numbers

| piece | status | test evidence |
|---|---|---|
| `rooms.slot_type_for` (category, room) key | built | 3 unit tests |
| `rooms.unmapped_slots` / qualification-time check | built, wired into `qualify_labels` | 6 unit tests (`test_label_qualification.py`) + 6 (`test_rooms.py`) |
| `posterior.shrink_hierarchical` (scene→profile→global) | built | 4 unit tests confirm exact zero-weight fallback at each level |
| Real multi-scene aggregation (`fit_transition_kernels_hierarchical`) | **not built** | — |

## What this means

The generalizable, testable core is complete: a category with zero events
in one scene now has a well-defined, exactly-verified path to fall back to
profile-level statistics, and then to global statistics, using the same
shrinkage math M2 already relies on. An anchor a scene's own vocabulary
can't place in a known room now fails at qualification time, not silently at
belief-fitting time.

## What is NOT yet supported by these numbers

- No real profile-level or global-level kernel has ever been fit from
  multi-scene data — the backoff math is verified against synthetic
  `HierarchicalStat` inputs only. The data-aggregation layer that reads
  `category_location_change_stats` across every scene sharing a profile
  does not exist yet.
- Nothing in the current M2/M3 gates or E1 sweep uses this hierarchy; every
  result to date still fits kernels from a single scene's own data.

**Traceability:** fingerprint `25e52eee014c3c72`, code_hash
`05102535c7dbb01b` (this work does not change the fitted kernels any
existing result uses). Full write-up: `../../D1_KERNEL_GENERALIZATION_NOTE.md`.
