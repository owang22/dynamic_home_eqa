# Contamination audit ledger — Suite Buildout Phase A

Root cause: 102344022 and 102344049's day0 folders were generated July 4
(pre-dating this session's manifest.py trace-integrity fixes) and were
reused as-is by the scene-pool orchestrator, which checked file existence
only, not `trace_validate.validate()`. Both fail badly: 102344022 day0 =
39 chain_breaks/57 re_inserts/47 no_ops/53 unattended of 169 events;
102344049 day0 = 4/26/31/26 of 92 events. Neither has been regenerated as
of this ledger (confirmed by direct `trace_validate.validate()` re-run:
both still FAIL). Every other scene-pool folder checked (27 folders across
102343992, 102816216, 102816615, 102344022 days 1/3/4, 102344049 days
1-4, 102344457, 102816627) passes clean — the corruption is exactly and
only these two day0 folders, confirmed independently by the scene-pool
agent's own sweep.

## Per-artifact status

| Artifact | Consumed 102344022/102344049 day0? | Status | Action |
|---|---|---|---|
| `scripts/e2_headline_comparison.py` (E2 rehearsal) | No — reads only `embodied_results/m3_result.json`, built exclusively from `experiment_config.FROZEN`'s own 102343992 folders | **CLEAN** | None needed. Fingerprint mechanism extended with validation hashes anyway (see "closing the hole" below), rehearsal re-run to confirm — numbers unchanged (864ff40f29873a7f). |
| `scripts/embodied_m1_gate.py` / `_m2_gate.py` / `_m3_gate.py` (kernel fits, all milestone rows) | No — all exclusively use `FROZEN.train_folders`/`FROZEN.eval_folder` (102343992) | **CLEAN** | None needed. |
| `scripts/compute_frozen_labels.py` (`FROZEN_LABELS`/`FROZEN_STATE_LABELS`) | No — 102343992 only | **CLEAN** | None needed. |
| `scripts/generate_state_stratum.py` runs (102343992, 102816216, 102816615) | No — different scene IDs entirely; also structurally immune (refuses to write output unless the merged trace itself passes `trace_validate`) | **CLEAN** | None needed. |
| `scripts/yield_projector.py` (my run reported to the user in the Pre-Suite Window status) | **Yes** — read `_expand_scene_pool_state.json`'s `qualified_labels` for 102344049 (12 labels, populated from the corrupted day0 at read time) and fit decay models from its train folders including the corrupted day0; 102344022's exact contribution at that read is not reconstructable (its `qualified_labels` has since been reset to `None` by the scene-pool agent's self-healing fix, which landed after my read) but was almost certainly also contaminated given the identical root cause | **CONTAMINATED** | **Regenerated.** Script now validates every consumed folder before counting a scene, excludes (with a logged reason) any scene with a failing folder — 102344049 is now correctly excluded. See delta below. |
| `expand_scene_pool.py`'s own `qualified_labels`/`n_candidates` state for 102344022/102344049 | Yes (source of the contamination) | **CONTAMINATED, being fixed by its owner** | Not mine to fix directly — the scene-pool agent already landed the root-cause fix (`_folder_ready()` now requires `trace_validate.validate().ok`, and the main loop re-checks disk instead of trusting a cached `generated=True`) and will regenerate both day0 folders in its next consolidated pass. |

## Delta: yield_projector, contaminated vs. corrected

The contaminated run (reported earlier as "location clears the bar
comfortably") used a raw-label-count methodology that Phase B3 separately
identified as wrong regardless of contamination — the two issues compound,
so the delta below reflects **both** fixes together, not corruption alone:

| Stratum | Old (contaminated, raw-count) | New (clean, effective-N = n_clusters) |
|---|---|---|
| location/stable | 12 raw labels — reported "OK" | **4 qualifying scenes** — SHORT (needs 96 more) |
| location/volatile | 28 raw labels — reported "OK" | **4 qualifying scenes** — SHORT (needs 96 more) |
| state/stable | 1 raw label — reported SHORT | **3 qualifying scenes** — SHORT (needs 97 more) |
| state/volatile | 1 raw label — reported SHORT | **2 qualifying scenes** — SHORT (needs 98 more) |

**Correction to the Pre-Suite Window status report**: "location clears the
≥100 bar comfortably" was wrong. Under the corrected effective-N
(scene-day-cluster count, not raw question count — see Phase B3),
**location is also short**, at 4 of the required 100 qualifying scenes.
This was not solely a contamination artifact — the raw-count methodology
itself overstated readiness even before contamination is considered; the
two effects compound in the same direction. Reported here per the standing
rule that gate results contradicting stated expectations are escalated
with logs, not softened.

## Closing the hole (permanent fix)

- `trace_validate.Report.validation_hash()` (new): deterministic hash of a
  report's hard-invariant outcome. Any artifact that consumes a scene-day
  now records this per folder.
- `scripts/scene_validation.py` (new): shared `validate_folder`/
  `validate_folders` helper — one implementation, not N reimplementations
  of the same read+validate glue, so every consumer computes the hash
  identically.
- `scripts/yield_projector.py`: validates every folder before counting a
  scene; excludes (with a logged, visible reason) any scene with a
  failing folder, rather than trusting `entry.generated`/
  `entry.qualified_labels` at face value.
- `scripts/e2_headline_comparison.py`'s `SceneDescriptor` gained
  `validation_hashes` (one per consumed folder, sorted), incorporated into
  `PoolManifest.fingerprint()` — a folder that later fails validation (or
  a corrupted folder that gets fixed) changes the pool fingerprint and
  forces the "any config-affecting change re-fingerprints and rebuilds
  the attribution table" rule to fire mechanically, not by memory.

Test coverage: `tests/test_trace_validate.py` (validation_hash),
`tests/test_scene_validation.py` (validate_folder/validate_folders),
`tests/test_yield_projector.py` (n_clusters tracking),
`tests/test_e2_headline_comparison.py` (fingerprint sensitivity — already
covered `navmesh`/`start_island`/labels; validation_hashes uses the same
mechanism). 292 tests passing (habitat_sim env: see full suite run).
