# baselines — sense-or-answer baseline study

Package map beyond the core (see sections below): `fleet.py` (fleet
health run over every realized household), `passive_eval.py` (the
horizon-controlled passive protocol), `bakeoff.py` (candidate belief
bake-off), `registry.py` (belief registry with `frozen|candidate`
panel tags).

Agents hold a memory of timestamped object sightings and answer
object-localization questions ("where is mug_2 right now?") under a
per-day sensing budget: for each question they either answer from belief
or spend one budget unit sensing a receptacle (learning its full true
contents) before answering.

All times in this package are **seconds since episode start**; a day is
86 400 s and `day_index = t // 86400`.

These baselines are deliberately basic: they are the **instrument** the
data-generation workstream uses to judge whether a candidate bank is
healthy (see the healthcheck below). The roster is intentionally small
and frozen.

## Architecture: beliefs × policies

An `Agent` is exactly one `BeliefModel` plus one `DecisionPolicy`
(`agent.py`); the harness (`harness.py`) is generic over both.

- **BeliefModel** (`beliefs/base.py`): consumes the observation stream and
  sense results, answers `predict(object_id, t)` with a distribution over
  receptacles plus its argmax. Shared bookkeeping lives in the base class;
  a concrete model implements one method, `_predict_from_history`. The
  base class also owns **negative evidence**: a sense whose contents omit
  a known object excludes that object from the sensed receptacle, the
  exclusion is invalidated by any strictly later positive sighting, and a
  positive sighting at exactly the prediction instant outranks every
  model prior. Concrete models never reimplement any of this.
- **DecisionPolicy** (`policies/base.py`): given a question, the current
  prediction, and the (read-only) remaining budget, returns `AnswerNow`
  or `Sense(receptacle_id)`. After a sense the harness updates the belief
  and asks again, so policies bound their senses per question.

### Registry: frozen panel vs candidates

Every buildable belief is registered in `registry.py` with a `panel`
tag. `frozen` members are the three-model instrument panel below;
`candidate` members (currently `markov1`, `periodic_persistence`,
`daytype_mixture`, `hierarchy_backoff` — the bake-off slate, see
`bakeoff.py` and `reports/baselines/bakeoff/recommendation.md`) are
buildable from any config but the healthcheck REFUSES to run a panel
containing one — the instrument stays frozen by construction, not
convention. Candidates that pool evidence across objects override the
base class's `_predict_for_object` hook; exclusion machinery,
renormalization, and the sighting-at-instant override stay base-only
either way. All candidates use the frozen 24 h count half-life where
they use counts; every hyperparameter is fixed a priori (values in each
model's config dataclass).

### Roster (frozen)

Beliefs: `last_observation` (one-hot on the newest sighting),
`most_frequent` (sighting-frequency histogram), `timetable`
(same-time-of-day histogram with a most-frequent fallback). The
frequency-style pair take an optional `half_life_h` (exponential count
decay); the instrument panel runs them at a frozen 24 h half-life — the
honest strong versions — and the decayed-vs-undecayed gap on a bank is
itself a measurement of how much that bank drifts.

Policies: `never_sense` (the zero-cost floor), `fixed_schedule` (blind
patrol on a cadence), `sequential_search` (senses receptacles in belief
order until the object is found, the budget runs out, or a configured
confidence threshold is met; misses become exclusions, so the belief
itself yields the next-best receptacle). **Invariant**: on any bank whose
queried objects are each inside some receptacle at query time,
`sequential_search` at unlimited budget scores task accuracy 1.0 with
every belief model — enforced by tests and by the healthcheck's
`solvable` gate.

**Adding a member**: subclass under `beliefs/` or `policies/`, register in
`cli.build_belief` / `cli.build_policy`. Nothing else changes — but the
instrument panel above stays frozen; additions are for later phases.

Hard rules the harness enforces (see `harness.py` docstring): identical
observation diet for every agent, budget accounting outside policies,
ground-truth isolation by construction (`Episode.agent_view()` has no
truth accessor), exact-match scoring, full-run JSONL logging with a
full-state belief snapshot per question.

## Running

```bash
# tests (from the repo root)
python -m pytest tests/test_baselines_*.py

# type check
python -m mypy --strict src/baselines

# smoke run: full 3x3 grid on the synthetic fixture bank
python -m baselines.cli run src/baselines/configs/smoke.yaml

# data-health gate report for a candidate bank
python -m baselines.cli healthcheck banks/baselines/hh_001_seed0_bank.jsonl \
    --out-dir smoke_results/healthcheck_hh_001_seed0

# intrinsic stats + stationarity gate only (no agents, < 1 s) — the fast
# feedback loop while iterating the generator
python -m baselines.cli bankstats banks/baselines/hh_001_seed0_bank.jsonl

# fleet: export + healthcheck EVERY realized household under the one
# shared config (configs/fleet.yaml — the hh1 recipe; never tuned per
# bank); writes reports/baselines/fleet/fleet_summary.{md,json}
python -m baselines.cli fleet

# candidate bake-off under the horizon-controlled passive protocol,
# on the fleet's gate-passing banks
python -m baselines.bakeoff

# belief trace for the viewer: what every model believes about every
# object at every moment, against truth (see "Belief traces" below)
python -m baselines.belief_trace --candidates \
    --bank banks/baselines/fleet/<household>_bank.jsonl \
    --out profiles/<household>/timeline_seed0/belief_trace.json
```

## Belief traces (the viewer's belief-vs-truth page)

`belief_trace.py` writes `belief_trace.json` beside a household's
`trace.json`: per belief model and per object, run-length-encoded
segments of that model's argmax under the PASSIVE diet (initial tour +
the bank's scripted sightings, no sensing at all), plus the bank's own
truth segments. Because a belief's argmax moves with time even when no
new evidence arrives — decayed counts re-weight continuously, timetable
bins roll over, hazards decay — predictions are sampled on a fixed grid
(15 min) and then RLE'd, which is exact at grid resolution and small on
disk (~100-270 KB for 7 models over 17-53 objects).

`visualization/serve.py` discovers these files and publishes them, so
running the generator is what makes a household appear on
`viewer/beliefs.html`. That page compares belief against truth at ANY
slider moment (not only at question times) with three tabs: the focus
object on the map, every object scored right now, and the same instant
across all models. Correctness there means exactly what it means in the
harness — identical receptacle ids, exact match — because the truth
segments come from the bank, not from the spatialized timeline.

## Horizon-controlled passive evaluation

The per-day passive curves from `run` are DESCRIPTIVE ONLY: a later day
has more history, fresher sightings, and a shorter forecast horizon all
at once. Learning-curve claims use `passive_eval.py`: evidence frozen at
checkpoint day D (tour + sightings with t < D·86 400, no sensing),
questions scored at horizons h past D per (D, h) cell — never pooled
across h — plus recency stratification (accuracy vs
time-since-last-sighting), top-1 AND epsilon-floored log-loss, and
household-unit aggregation (unweighted mean over households, seeded
bootstrap intervals, sample sizes printed). `bakeoff.py` runs the frozen
panel + candidate slate under this protocol and writes the leaderboard,
recency curves, per-household winners, and a byte-deterministic
`bakeoff_results.json`.

The smoke config writes `smoke_results/baselines_smoke/`: `run_log.jsonl`,
`questions.csv`, `aggregate.csv`, the two plots, and `provenance.json`
(config hash, bank manifest hash, git commit, seed, timestamp).

## Healthcheck: the data-health gates

`python -m baselines.cli healthcheck BANK [--config thresholds.yaml]
[--out-dir DIR]` runs the fixed instrument panel — NeverSense with each
of the three beliefs, SequentialSearch with each belief at unlimited
budget, SequentialSearch (best belief) at the real budget — and reports
five gates (thresholds configurable; defaults shown):

| gate | default | rationale |
|---|---|---|
| `stationarity` | dwell-weighted modal share <= 0.60 | above it, a home-base-only model is right that often at a random moment — scale just tightens error bars around an uninteresting bank |
| `solvable` | == 1.0 | unlimited-budget search must find everything; failure = bank/harness bug |
| `not_trivial` | max NeverSense <= 0.65 | if passive memory nearly solves it, the dynamics are too static |
| `not_impossible` | search@budget >= best NeverSense + 0.15 | sensing must buy real accuracy at the allotted budget |
| `discriminative` | NeverSense spread > 0.03 (global or per household_type stratum) | different modeling assumptions must score differently somewhere |
| `powered` | >= 300 questions | fewer and agent differences drown in binomial noise |

`stationarity` is pure ground-truth arithmetic — `cli bankstats` computes
it (plus moves/day, the displacement-stint distribution, modal share at
query times, and the worst per-day question-repeat draw) in well under a
second with no agents; `--figs` renders a four-panel `bank_dynamics.png`
diagnostic (per-object modal share vs the gate, stint-length histogram,
moves/day with weekends marked, per-day query-time modal share). The intended loop: iterate the generator against
`bankstats`, and pay for the full panel only once the intrinsic stats
pass.

Output: a self-explanatory stdout summary plus `healthcheck.json` /
`healthcheck.txt` under `--out-dir`, with all measured values, thresholds,
per-gate verdicts, and provenance. The overall verdict **refuses to be
PASS on a dirty git tree** — instrument results must be reproducible.
Exit status is 0 only on overall PASS.

## Scoring: task vs full-state accuracy

`task_accuracy` scores the queried objects only. Because sensing is
correlated with what gets asked, the run log also snapshots the belief's
argmax for EVERY object after each question (`belief_state`);
`belief_accuracy` scores that probe set, which sensing cannot game.
Both flow through `questions.csv` / `aggregate.csv` with `overall`,
per-`object_class`, and per-`day_index` strata, and both are recomputable
offline from the run log alone (`metrics.load_run_log`). `replay.py`
additionally replays any agent's evidence stream through every belief
(off-policy matrix: columns isolate belief quality, rows isolate
data-collection quality).

## JSONL schemas

**Bank input** (full spec in `bank.py`'s docstring): line kinds
`episode_header` (ids, receptacles, object classes, budget, n_days,
optional `household_type` metadata, optional `unsensable_receptacles` —
legal answers Sense may never target, reachable only by eliminating
every sensable receptacle), `truth` (piecewise-constant ground
truth; every object needs a t=0 row), `observation` (source
`initial_tour` or `scripted` — the fixed stream; never reports an object
at an unsensable location), and `question`. The
synthetic fixture builders emit exactly this format, so tests exercise
the real loader.

**Run log** (one line per question; field-by-field in
`harness.QuestionRecord`): episode/agent/question ids, the full predicted
distribution, every action in order (senses embed returned contents),
the answer + confidence, truth, correctness, budget
before/spent/after plus a `forced_answer` flag, and the full-state
`belief_state` snapshot.

## Synthetic fixtures (`bank.py`)

- `write_synthetic_bank` — the 7-day, 3-object bank with hand-derivable
  accuracies (derivation in `tests/test_baselines_integration.py`).
- `write_negative_evidence_bank` — negative evidence is decisive: every
  belief favors a receptacle the object silently left; only the
  exclusion machinery finds it (`tests/test_baselines_search.py`).
- `write_gate_pass_bank` / `write_gate_fail_static_bank` — engineered to
  PASS all five healthcheck gates / FAIL `not_trivial` (a static world),
  used by `tests/test_baselines_healthcheck.py`.
