# STATUS — basic baselines for the sense-or-answer study

## Built

Everything in the brief's scope: the frozen core types
(`types.py`), the `EpisodeBank` protocol + strict JSONL loader + synthetic
fixture builder (`bank.py`), three belief models (last-observation,
most-frequent, timetable with configurable bins/day-scheme), three
policies (never/always/fixed-schedule), the belief×policy `Agent`
composition, the rule-enforcing harness, metrics (tidy + aggregate CSVs,
the two plots), a YAML-config CLI with full provenance, 27 tests
(units, harness invariants, integration grid with hand-derived exact
scores, golden-file snapshot), and the smoke-run outputs. `pytest` green;
`mypy --strict` clean over the package.

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

- Basic beliefs ignore the negative information in `SenseResult.contents`
  (documented contract keeps it available for later model families).
- `FixedSchedule` senses at most once per question even if more than one
  cadence period elapsed since the last patrol.
- The accuracy-vs-budget "curve" currently has one point per run (the
  bank's single budget level); sweeping budgets is a config-per-level
  affair by design.
