# STATUS — basic baselines for the sense-or-answer study

## Update (2026-08-10, baseline repair + data-health gates)

This update makes the baselines trustworthy as a data-health instrument:
beliefs consume negative evidence, the incoherent AlwaysSense policy is
gone, full-state scoring is first-class, and `healthcheck` is the
acceptance gate the data workstream runs on every candidate bank.

### What changed

1. **Negative evidence (belief base class).** A sense result is now
   evidence about every known object: contents become positive sightings
   (as before), and each known object absent from them is *excluded*
   from the sensed receptacle at that time. All bookkeeping —
   per-object exclusion sets with timestamps, the recency rule, uniform
   redistribution of excluded mass, the all-excluded fallback (warning
   with object id and query time) — lives in `beliefs/base.py`; the
   three concrete models are untouched by it. Two documented design
   points:
   - *Redistribution is uniform over all non-excluded receptacles*, not
     a renormalization of the surviving support. Renormalizing support
     alone fabricates certainty (base mass on two receptacles + one
     exclusion => probability 1.0 on a receptacle nobody checked) and
     breaks the search invariant. The brief's "uniform over non-excluded"
     edge case falls out of this rule as the all-support-excluded
     special case.
   - *A positive sighting at exactly the prediction instant wins
     outright* (one-hot). Without this, a frequency belief that just
     watched the search FIND the object would outvote the sighting with
     its own history and answer somewhere else — the exclusions that
     forced the find are invalidated by that same (strictly later)
     sighting, so exclusions alone cannot save it.
2. **TimetableLookup restored.** The previous update had dropped it; the
   healthcheck's fixed panel and the discriminative gate are defined
   over the three belief models, so the roster is back to
   last_observation / most_frequent / timetable — and now frozen.
3. **AlwaysSense and SearchUntilFound are gone; SequentialSearch is the
   one search policy.** It senses receptacles in belief order (exclusions
   yield the next-best receptacle automatically), answers on a find, and
   supports a confidence-threshold early stop (default 1.0). At the
   default threshold the *only* early stop is a sense this question that
   returned the object: belief confidence of 1.0 alone is never trusted,
   because one-hot recency beliefs claim certainty for arbitrarily old
   sightings and exclusion renormalization can concentrate mass on
   unchecked receptacles. Sub-1.0 thresholds trust the belief and are
   only sound for calibrated models (documented in the module). The
   unlimited-budget invariant (task accuracy 1.0 for every belief on
   every well-formed bank) is enforced across all four fixture banks x
   three beliefs in `tests/test_baselines_search.py`.
4. **Full-state scoring is now named `task_accuracy` vs
   `belief_accuracy`** everywhere (aggregate.csv column renamed from
   `accuracy`). Both are recomputable offline from the run log alone via
   `metrics.load_run_log` (asserted by a round-trip test). The queried
   object's snapshot entry now reuses the answer prediction instead of
   re-predicting (an exclusion tie re-broken differently could desync
   snapshot from answer); `replay.py` mirrors the live loop's
   generator-consumption pattern exactly, so the diagonal identity holds
   under the new tie-break-heavy distributions.
5. **`healthcheck` subcommand** (`python -m baselines.cli healthcheck
   BANK [--config Y] [--out-dir D]`): fixed panel (NeverSense x 3
   beliefs, SequentialSearch x 3 @ unlimited, SequentialSearch best
   belief @ real budget), five gates (solvable / not_trivial /
   not_impossible / discriminative / powered — thresholds are config
   values), JSON + stdout reports with full provenance, exit 0 only on
   overall PASS, and a hard refusal to mark overall PASS from a dirty
   git tree. `validate_bank.py` is retired — the healthcheck subsumes
   it (its budget-sensitivity sweep lives on in `sweep.py`, now running
   sequential_search instead of always_sense).
6. **Bank metadata**: episode headers may carry optional
   `household_type`; the loader, `Episode`, and the exporter
   (`export_bank`, when the schedule spec provides it) pass it through
   for the stratified discriminative gate. Absent metadata => the
   stratified check reports SKIPPED and only the global spread counts.
7. **New fixtures** (`bank.py`): `write_negative_evidence_bank` (all
   beliefs favor a receptacle the object silently left; a non-empty
   decoy receptacle proves exclusion comes from absence, not emptiness;
   post-fix search finds the object in 2-4 senses — asserted),
   `write_gate_pass_bank` (310 questions, four dynamics families,
   passes all five gates), `write_gate_fail_static_bank` (static world,
   fails not_trivial/not_impossible/discriminative). Golden snapshot
   regenerated (behaviour legitimately changed with negative evidence +
   the new policy); pinned run is last_observation+SequentialSearch.

### Deviations / judgment calls

- The brief's step-2 reading of the confidence threshold ("meets 1.0 =>
  answer") is implemented as *grounded* certainty only (see point 3):
  the literal reading makes SequentialSearch+LastObservation degenerate
  to NeverSense (its confidence is always 1.0) and violates the
  invariant the same brief makes primary.
- "Log the belief's full per-object predictions" was implemented as the
  existing per-object argmax snapshot (`belief_state`), not full
  distributions: argmax is sufficient for the accuracy metric, and full
  distributions would multiply the snapshot by ~n_receptacles.
- No blanket "search >= never_sense" identity is asserted: at tight
  budgets, morning senses leave exclusions that are stale by evening on
  periodic objects (observed on hh_001: LastObservation+SequentialSearch
  0.688 vs NeverSense 0.724 at budget 2). The asserted identity is
  "found => answered correctly".
- `cli.py` became subcommand-based: `run` (old behaviour) and
  `healthcheck`. Update any scripts calling `python -m baselines.cli
  <config>` to `python -m baselines.cli run <config>`.

### Task-3 log-size impact

The full-state snapshot (`belief_state` + `belief_accuracy`) accounts
for ~54% of run-log bytes on the 17-object hh_001 banks (4.3 MiB vs
2.0 MiB without, 2 772 records) and ~23% on the 3-object smoke bank.
Logging full distributions instead would have multiplied the snapshot
by ~n_receptacles (17x here) — hence argmax-only.

### Healthcheck output, synthetic gate-test banks

`write_gate_pass_bank` (panel: NeverSense last_observation 0.539,
most_frequent 0.323, timetable 0.452; search@unlimited 1.000 for all
three; search@24 with last_observation 0.848):

    [PASS] solvable         measured   1.000  need == 1.000
    [PASS] not_trivial      measured   0.539  need <= 0.650
    [PASS] not_impossible   measured   0.848  need >= 0.689
    [PASS] discriminative   measured   0.216  need > 0.030
    [PASS] powered          measured 310.000  need >= 300.000
    stratified spreads by household_type: synthetic_mixed=0.216
    OVERALL on a dirty dev tree: FAIL ("REFUSED: all gates passed but
    the git tree is dirty") — the refusal path working as intended;
    from a clean tree this bank is overall PASS.

`write_gate_fail_static_bank` (all NeverSense accuracies 1.000):

    [PASS] solvable         measured   1.000  need == 1.000
    [FAIL] not_trivial      measured   1.000  need <= 0.650
    [FAIL] not_impossible   measured   1.000  need >= 1.150
    [FAIL] discriminative   measured   0.000  need > 0.030
    [PASS] powered          measured 300.000  need >= 300.000
    stratified check: SKIPPED (no household_type in bank metadata)
    OVERALL: FAIL — gates failed: not_trivial, not_impossible,
    discriminative

### hh_001 under the new instrument

The committed `smoke_results/healthcheck_hh_001_seed0/` report (run
from a clean tree) is the expected FAILING result for the current
44-question pilot bank — powered fails outright and the belief
separation is weak (see the report for exact numbers). That failure is
the healthcheck doing its job on a bank we already knew was too small,
not a defect to fix here. The 14-day banks fare better on scale but
still show the known nightly-tidy homogenization (NeverSense 0.724 for
all three beliefs on the uniform bank — the open bank-design issue
below, unchanged by this update).

### Carried-over findings (from the earlier confound-fix rounds)

- Off-policy replay on hh_001 (uniform, 308 questions) showed
  LastObservation is genuinely the best belief there (wins every replay
  column) and FixedSchedule genuinely collects the best data (its stream
  tops every column). Basic policies sense indiscriminately (attention
  gaps within noise) — query-aware sensing remains open headroom.
- KNOWN OPEN BANK-DESIGN ISSUE (unchanged): the 14-day headline banks
  (3 sightings/day, tour on, nightly gradual tidy instead of the weekly
  reset) homogenize the beliefs — NeverSense scores 0.724 for all three
  on the uniform bank, so the healthcheck's discriminative gate FAILS
  there. Known lever from the sighting-rate sweep: gaps open at higher
  sighting rates (0.089 at 16/day pre-change). Bank design decision
  still pending with the data workstream.

## Built (original tier)

Everything in the original brief's scope: the frozen core types
(`types.py`), the `EpisodeBank` protocol + strict JSONL loader + synthetic
fixture builders (`bank.py`), three belief models (last-observation,
most-frequent, timetable with configurable bins/day-scheme), three
policies (now never / sequential-search / fixed-schedule), the
belief×policy `Agent` composition, the rule-enforcing harness, metrics
(tidy + aggregate CSVs, the two plots), a YAML-config CLI with full
provenance, the test suite (units, harness invariants, integration grid
with hand-derived exact scores, search invariant, healthcheck
integration, golden-file snapshot — 67 tests), and the smoke-run
outputs. `pytest` green; `mypy --strict` clean over the package.

## Deviations from the brief (all follow existing repo conventions)

1. **Package location**: `src/baselines/` rather than top-level
   `baselines/` — the repo is src-layout (`[tool.setuptools.packages.find]
   where = ["src"]`). Registered via the existing editable install.
2. **Test layout**: flat `tests/test_baselines_*.py` files rather than a
   mirrored `tests/baselines/` tree — the repo keeps a flat pytest dir.
   The golden snapshot lives in `tests/fixtures/`.
3. **`Action` type**: the policy returns `AnswerNow | Sense`, not
   `Answer | Sense`. `Answer` carries `budget_spent`, which policies must
   not account by rule 3; the harness assembles the final `Answer` from
   the standing prediction. Same semantics, cleaner ownership.
4. **Smoke outputs** are written (not git-committed) to
   `smoke_results/baselines_smoke/` — the repo has substantial uncommitted
   work in flight and commits here are the owner's call.
5. **mypy config**: added a minimal `[[tool.mypy.overrides]]` block to the
   shared `pyproject.toml` for untyped third-party imports
   (matplotlib/yaml) only.
6. **Plot palette provenance**: hues come from a colorblind-validated
   reference palette in its documented fixed order. The palette's own
   validator script needs Node ≥ 15 and this box has v12, so validation
   rests on the palette doc's published pass results rather than a local
   run.

## JSONL schemas as implemented

See `bank.py`'s module docstring (bank input) and `harness.QuestionRecord`
(run log); summarized in `README.md`. All times are integer seconds since
episode start; `day_index = t // 86400`.

## Open questions for the data workstream

1. **Scripted observations**: the schema supports an in-episode observation
   stream (source `"scripted"`), delivered to agents in time order before
   each question. Real banks should say what sightings these represent
   (e.g. drive-by camera hits during the day) and their volume; if real
   banks have *only* the initial tour, the field stays but sits empty.
2. **Observation timing convention**: the harness delivers scripted
   observations with `t <= t_query` before asking each question. If a
   bank intends observations to arrive with latency (seen at t, known
   only later), that needs a `t_delivered` field — schema change.
3. **Truth encoding**: piecewise-constant change-points, one row per
   move, mandatory t=0 row per object. Fine for the current simulator's
   event streams (events.jsonl maps 1:1); confirm carried objects
   (`person:*` locations) will be projected to receptacles (or an
   `OUT_OF_HOUSE` pseudo-receptacle) before bank export — the baseline
   scorer does exact receptacle match only.
4. **Budget semantics**: budget is per-day and non-carryover here.
   Confirm.
5. **Aliases**: the loader assumes receptacle ids are already normalized
   (scoring is exact match by rule 4). The revamp_v1 profile pipeline
   already enforces canonical ids, so this should hold; flagging it
   anyway.

## Known limitations (in-scope simplifications)

- Exclusions expire only via a strictly later positive sighting, so a
  morning miss still zeroes a receptacle the object re-entered by
  evening (periodic objects); the all-excluded fallback plus the
  search's tried-set keep this from ever costing correctness at
  unlimited budget, but at tight budgets stale exclusions can cost the
  recency belief the occasional blind answer (numbers in the update
  above).
- `FixedSchedule` senses at most once per question even if more than one
  cadence period elapsed since the last patrol.
- The accuracy-vs-budget "curve" currently has one point per run (the
  bank's single budget level); sweeping budgets is a config-per-level
  affair by design.
