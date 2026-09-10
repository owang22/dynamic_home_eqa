# Regeneration audit — physical-model change

Brief: room-visit sensing with enclosure, travel cost and robot position,
person observations, occupied-age staleness. This file is Part 0: what the
change invalidates, what stays useful, and the rebuild order. Nothing has
been built yet.

Repo state at audit time (2026-09-09, host cheetah,
`/home/oliver/robot/dynamic_home_eqa`): HEAD `230a2701` (VoI policies).
The working tree is dirty with someone else's in-flight STAR-memory brief
(uncommitted edits to `STATUS.md` and `cli.py`, untracked
`memory/`, `policies/star_memory_loop.py`, `star_study.py`,
`tests/test_baselines_star_memory.py`, `results/star_memory_loop/`,
`scratch_runs/`) plus timestamp-only diffs in the fleet healthcheck
reports from today's bank rebuild. This brief's edits to `STATUS.md` and
`cli.py` will be appended around those, never over them.

Two facts anchor everything below:

- The 20 fleet banks under `banks/baselines/fleet/` were regenerated
  today (15:12–15:20) and are **byte-identical** (sha256, 20/20) to the
  banks recorded in `results/conformal_sweep_v2/budget90/provenance.json`,
  which `results/voi_policies/` reused. The bank export is deterministic,
  so "before" numbers and the regression run share one world.
- The bank loader is strict: an unknown row `kind` raises
  `BankFormatError`. New row kinds therefore need the loader before any
  new bank can be read; extra header keys are ignored today and stay
  backward compatible.

## 1. Bank fields, rows and header entries this brief adds or changes

### Header (`episode_header`) — additions

| field | part | content |
|---|---|---|
| `receptacle_rooms` | 1, 2 | `{receptacle_id: room}` for every physical receptacle, plus `ON_PERSON -> "person_check"` (the existing pseudo-room). Today the room of a receptacle exists only in `program.yaml` and is scraped from `room_visit` rows by `llm_floor.bank_rooms` and `representative_grid.llm_rooms`; the harness needs it directly to resolve `Sense(receptacle_id)`. Not named in the brief; required by it. |
| `enclosed_receptacles` | 1 | the per-household enclosed set (keyword match + override), and `enclosure_config_sha256`. |
| `room_distances` | 2 | symmetric matrix in meters over the spec's room ids; `distance_source: "room_distances.yaml" \| "uniform_fallback"`; `d_mean`. |
| `sense_costs` | 2 | `{c_visit: 0.5, c_inspect: 0.25, average_sense_raw: 1.75, normalizer: 1.75, c_visit_normalized, c_inspect_normalized}`. |
| `home_base_room` | 2 | default: the room with the most receptacles (spec order breaks ties). |
| `person_observations` | 3 | `{away_rule, away_activities, asleep_activities, config_sha256}` so a bank says how its occupancy rows were derived. |

`budget_per_day` keeps its name and values (24, 90) but its unit becomes
normalized cost, not sense count. `Episode.budget_per_day`,
`EpisodeContext.budget_per_day`, the harness's `budget` and
`QuestionRecord.budget_*`, `Answer.budget_spent`, and every policy's
`budget_remaining` are `int` today and become `float`. That is a type
change through `types.py`, `harness.py`, `policies/base.py`, every policy,
`metrics.py`, `conformal/sweep.py`, `representative_grid.py`,
`voi_study.py`, and the golden run log test.

### Rows — additions and changes

| row | part | change |
|---|---|---|
| `room_visit` | 3 (tier 2) | gains `residents_present: [resident ids whose anchor receptacle is in this room at t]`. |
| `occupancy` (new kind) | 3 (tier 1) | `{"kind": "occupancy", "episode_id", "t", "home_awake": n, "home_total": m}` at every change point of the home-and-awake count, whole episode, delivered to beliefs by time like any evidence. Loader change required. |
| `room_visit.contents` | 1 | **Proposed deviation, needs the owner's yes:** the bank keeps FULL contents (every receptacle in the room, enclosed included) and the loader drops enclosed receptacles from passive visits when `--enclosure` is on. Writing filtered contents into the bank would make `--enclosure off` need a second bank set, since emptiness of an enclosed receptacle cannot be reconstructed without truth. With load-time filtering one rebuilt bank set serves all five runs, and the applied rule is written to each run's provenance. |

Nothing changes in `truth`, `observation` (initial tour) or `question`
rows; question ids, times and objects stay identical, which is what makes
the per-question before/after pairing possible.

### Consequence: which banks must be rebuilt

**All 20 fleet banks**, because every one needs the new header entries,
the `occupancy` rows and `residents_present` on its ~170 visit rows.
They are rebuilt into `banks/baselines/fleet_room_visit/` and the old
directory is left alone. The other directories under `banks/`
(`typ_v1/`, `atyp_v2/`, `atyp_shift_v1/`) are the older dynbelief format
(`events.jsonl`, `queries.jsonl`, no `episode_header`), have no reader
under `src/baselines`, and are out of scope.

### What the inputs actually support (measured, not assumed)

- **Enclosure.** Against the brief's keyword list plus `pantry`,
  `dresser`, `chest`, `hamper`, `bin`, `box`, `oven`, `dishwasher`,
  `microwave`, `trunk`, `basket`, the fleet's 27 receptacle base names
  match only `cupboard_k1` (all 20 households), `toy_chest_l1` (hh_002,
  hh_009, hh_010) and `medicine_cabinet_ba1` (hh_002, hh_013, hh_016).
  Drawer, cabinet (other than medicine), fridge, freezer, closet and
  wardrobe do not exist in any spec. So the enclosed set is 1–3 of 21–37
  receptacles per household (3–8 %). Enclosure will be a weak lever on
  this fleet; that is a finding to report in Part 5, not something to
  patch by widening keywords to open furniture.
- **Person observations.** `residents.jsonl` activity names carry
  suffixes (`work_away__resident_1`, `night_sleep__bed_b2`,
  `get_ready__entry_table_e1`), so matching against the config sets must
  strip at `__`. With that, every activity in the brief's away set does
  occur at `ELSEWHERE`, and all four asleep activities occur. But the
  brief's away set and the simulator disagree in both directions: 27
  blocks of `gym`/`appointment` are anchored at home receptacles, and
  `groceries`, `laundry`, `take_out_bins`, `socialise_home`, `deep_clean`
  blocks occur at `ELSEWHERE` without being in the set. **Recommendation
  (owner to confirm):** "away" = block anchored at `ELSEWHERE`, which is
  the rule `export_bank._away_intervals` already uses to project
  `ON_PERSON` to `OUT_OF_HOUSE`; the tracked `resident_states.yaml` keeps
  the away set as a documented cross-check and the export logs every
  disagreement. "asleep" = base activity in the asleep set. If the owner
  wants the literal activity-set rule instead, the config carries a
  switch and the header records which rule produced the rows.
- **Room distances.** No `room_distances.yaml` exists anywhere. The
  spatialized `timeline_seed0/trace.json` carries HSSD room polygons per
  household (`rooms[].poly`, plus `scene_id`), which is presumably the
  layout database the owner will export from. Per the brief nothing is
  derived from it here; **all 20 households will run on the uniform
  fallback** unless the files arrive before the rebuild, and the header
  and findings will say so.

## 2. Existing result directories

**Comparable to the new runs for absolute numbers: none.** Every result
under `results/` and every report under `reports/baselines/` was produced
with the flat-cost, whole-room sense primitive and passive visits that
reveal every receptacle. Even the all-flags-off regression run is a new
directory, not a reuse.

**Useful as the "before" side of the before/after comparison:**

| directory | role |
|---|---|
| `results/voi_policies/` (`grid.csv` 96 cells, `accuracy_by_day.csv`, `comparators.json`, `provenance.json`, `findings.md`) | the representative grid this brief reruns; same split (10 calibration / 10 test households, seed 0), same budgets 24 and 90; supplies the ResolvableMassSense best (alpha, tau) per (belief, budget) via `comparators.json` and the VoIBudgetPriceSense best gamma per cell via `grid.csv` (gamma made no difference there; the best-by-accuracy row is taken and its gamma recorded). |
| `results/conformal_sweep_v2/` | source of the household split (`budget90/calibration.json["split"]`, checked by `representative_grid.reference_split`) and of the stored global quantiles. Its `budget24`/`budget90` `sweep_results.csv` are a second before-side reading for the same cells. |
| `reports/baselines/fleet/` (fleet_summary + 20 healthchecks) | per-bank passive panel and search-at-budget numbers under the old primitive; the new fleet run writes to a new directory beside it. |
| `results/oracle_program_posterior/`, `results/conformal_sweep_v1/`, `reports/baselines/{household_analysis, rate_sweep, bakeoff*, fleet_seed1-4, exclusion_migration, sweep_hh1, llm_floor}` | historical; keep, not rerun, not cited as comparators except where the findings need the old passive numbers by regime (household_analysis cells). |
| `results/star_memory_loop/` | another brief's in-flight output on the old banks; untouched. |

Regression check plan (Part 5, question 1): the all-flags-off run must
reproduce `results/voi_policies/grid.csv` for NeverSense, SequentialSearch,
ResolvableMassSense_best and the VoIBudgetPriceSense best rows on the same
(belief, budget) cells. Expected agreement is exact rather than "within
noise": the banks are byte-identical, the export is seeded, the new fields
are additive, and with travel cost off every sense costs exactly 1.0 so
float budget accounting equals the old integer accounting. Any difference
larger than floating-point tie-breaking is a bug and stops the rerun.

## 3. Cached artefacts outside `banks/`

| artefact | depends on old sense primitive? | action |
|---|---|---|
| `results/conformal_sweep_v2/budget{24,45,90}/calibration.json` and `results/conformal_sweep_v1/**/calibration.json` (split conformal quantile tables) | yes: quantiles come from passive walks on the old banks (`1 - p(truth)` per question). The `split` inside them is a salted hash of household ids and is bank-independent. | **keep** (before side, and `reference_split` reads the split from it). The new study refits its own tables per run into `results/physical_model_change/<run>/calibration.json`. `voi_study.check_against_reference` currently raises when refit quantiles differ from the stored ones; in the new driver that check becomes a report line, expected to match only in the all-off run. |
| `reports/baselines/llm_floor/completions.jsonl`, `prompts.jsonl`, `questions.jsonl`, `sample.json` (LLM completion cache) | yes: prompt keys are (episode, object, last sighting, newest exclusion, hour bucket), all functions of the evidence stream. | **nothing to rebuild here**: these files are gitignored and are not present on cheetah at all; only the tracked summaries exist. LLMBelief is already skipped in the representative grid for this reason and stays skipped. |
| `results/star_memory_loop/llm_cache/*.jsonl` (STAR served-LLM prompt cache, keyed on the full request) | yes: prompts embed the memory index built from bank evidence. | **keep untouched**; it belongs to the in-flight STAR brief, whose own STATUS note already says its runs are pending banks. Flag to the owner that STAR must rerun on `fleet_room_visit` banks. |
| `llm_prior_cache/` (607 files, 2.5 MB; `src/dynamic_home_eqa/paths.py`) | no: generation-pipeline LLM priors, upstream of the timelines. | keep. |
| `banks/baselines/oracle_realizations/` (OracleBelief realization grids) | no (built from `program.yaml` re-realizations, not from banks); absent on this machine anyway. | nothing; OracleBelief is not in the grid. |
| `reports/baselines/fleet/healthchecks/*/healthcheck.{json,txt}`, `fleet_summary.{md,json}` | yes: `solvable`, `not_impossible` and `sequential_search_real_budget` are computed by running the harness. | **keep** the old reports. The rebuild writes new banks AND new healthchecks to `reports/baselines/fleet_room_visit/` via `--banks-dir/--out-dir`, so the old fleet report stays the before side. Expect the `solvable` gate (unlimited-budget SequentialSearch = 1.0) to still hold: unlimited budget makes cost irrelevant and enclosed receptacles stay sensable by inspection. |
| `profiles/households/generated/*/hh_*/timeline_seed0/belief_trace.json` (20 tracked viewer traces, from `belief_trace.py` on banks) | yes: passive replay of the bank's evidence. | keep; stale for the new primitive; regeneration is a viewer task outside this brief. |
| `reports/baselines/{household_analysis, rate_sweep, bakeoff*, fleet_seed1-4, exclusion_migration}` | yes, historically. | keep as history; not rerun. |
| per-question dumps (`results/**/questions/`) | yes | gitignored and absent on cheetah; nothing to do. |

## 4. Rebuild and rerun command sequence

Environment: `~/miniconda3/envs/dynamic_eqa/bin/python` is the only
interpreter with the full stack plus mypy and pytest. All commands from the
repo root with `PYTHONPATH=src`. Cheetah has 24 cores.

```bash
cd /home/oliver/robot/dynamic_home_eqa
PY=~/miniconda3/envs/dynamic_eqa/bin/python
export PYTHONPATH=src

# 0. code lands (Parts 1–4), then the gates the brief requires
$PY -m pytest tests/test_baselines_*.py -q
$PY -m mypy --strict src/baselines

# 1. rebuild the 20 banks with the new header, occupancy rows and
#    residents_present; new healthchecks beside them (old ones untouched).
#    ~8 min for 20 banks including healthchecks (today's rebuild took 15:12–15:20).
$PY -m baselines.cli fleet \
    --banks-dir banks/baselines/fleet_room_visit \
    --out-dir  reports/baselines/fleet_room_visit
#    fleet.yaml gains: enclosure_config, resident_states_config,
#    room_distances_filename (per household, optional), sense_costs.

# 2. bank audit before any agent runs: per household the enclosed set and
#    count, distance source, home base, occupancy-row count, static-span
#    fraction; and a field-by-field diff against banks/baselines/fleet/
#    asserting truth, questions and visit instants are unchanged.
$PY -m baselines.physical_model_study --stage bank_report \
    --out results/physical_model_change

# 3. regression run FIRST: all flags off; compare against
#    results/voi_policies/grid.csv; stop on any mismatch.
$PY -m baselines.physical_model_study --stage grid \
    --enclosure off --travel-cost off --occupied-age off \
    --out results/physical_model_change/all_off --workers 20
$PY -m baselines.physical_model_study --stage regression \
    --out results/physical_model_change

# 4. the other four runs (each ~30 cells: 3 beliefs x 5 policies x 2 budgets)
$PY -m baselines.physical_model_study --stage grid --out results/physical_model_change/all_on            --workers 20
$PY -m baselines.physical_model_study --stage grid --enclosure off    --out results/physical_model_change/enclosure_off    --workers 20
$PY -m baselines.physical_model_study --stage grid --travel-cost off  --out results/physical_model_change/travel_cost_off  --workers 20
$PY -m baselines.physical_model_study --stage grid --occupied-age off --out results/physical_model_change/occupied_age_off --workers 20

# 5. authored findings + STATUS entry
$PY -m baselines.physical_model_study --stage report --out results/physical_model_change
```

Wall-clock estimate: the 96-cell VoI grid ran in about an hour at 60
workers; 5 runs x 30 cells on 24 cores is roughly 2–3 hours, plus the
8-minute rebuild.

## Points that need the owner's answer at go-ahead

1. **Load-time enclosure filtering** (section 1, `room_visit.contents`):
   one bank set, full contents in the bank, enclosed receptacles dropped
   from passive visits by the loader when the flag is on. Yes/no.
2. **Away rule**: `at == ELSEWHERE` (recommended) versus the literal
   activity set. The config will carry both lists either way.
3. **Flag count**: the brief defines four flags but reruns "each of the
   three off alone". Reading: the three are `--enclosure`,
   `--travel-cost`, `--occupied-age`; `--person-observations` stays on in
   every run (its rows are inert except through occupied age, and turning
   it off would force occupied age off too). Confirm.
4. **Room distances**: none exist; every household runs on the uniform
   fallback unless `room_distances.yaml` files land in each
   `profiles/households/generated/gpt-5.6-terra/hh_*/` before step 1.
5. **VoIBudgetPriceSense "best config"**: gamma was indistinguishable in
   `results/voi_policies/`; the plan takes the best-accuracy gamma per
   (belief, budget) from `grid.csv` and keeps lambda0 = 0.05. Confirm, or
   name a gamma.
