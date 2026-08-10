# baselines — sense-or-answer baseline study

Agents hold a memory of timestamped object sightings and answer
object-localization questions ("where is mug_2 right now?") under a
per-day sensing budget: for each question they either answer from belief
or spend one budget unit sensing a receptacle (learning its full true
contents) before answering.

All times in this package are **seconds since episode start**; a day is
86 400 s and `day_index = t // 86400`.

## Architecture: beliefs × policies

An `Agent` is exactly one `BeliefModel` plus one `DecisionPolicy`
(`agent.py`); the harness (`harness.py`) is generic over both.

- **BeliefModel** (`beliefs/base.py`): consumes the observation stream and
  sense results, answers `predict(object_id, t)` with a distribution over
  receptacles plus its argmax. Shared history bookkeeping lives in the
  base class; a concrete model implements one method,
  `_predict_from_history`.
- **DecisionPolicy** (`policies/base.py`): given a question, the current
  prediction, and the (read-only) remaining budget, returns `AnswerNow`
  or `Sense(receptacle_id)`. After a sense the harness updates the belief
  and asks again, so policies bound their senses per question.

**Adding a belief model**: subclass `BeliefModel` in a new file under
`beliefs/`, implement `_predict_from_history` (and `update` only if you
need more than positive-sighting bookkeeping — e.g. to exploit the
negative information in `SenseResult.contents`), register it in
`cli.build_belief`. **Adding a policy**: subclass `DecisionPolicy` under
`policies/`, guarantee termination, register in `cli.build_policy`.
Nothing else changes — the harness, metrics, and logs are agnostic.

Hard rules the harness enforces (see `harness.py` docstring): identical
observation diet for every agent, budget accounting outside policies,
ground-truth isolation by construction (`Episode.agent_view()` has no
truth accessor), exact-match scoring, full-run JSONL logging.

## Running

```bash
# tests (from the repo root)
python -m pytest tests/test_baselines_*.py

# type check
python -m mypy --strict src/baselines

# smoke run: full 3x3 grid on the synthetic fixture bank
python -m baselines.cli src/baselines/configs/smoke.yaml
```

The smoke config writes `smoke_results/baselines_smoke/`: `run_log.jsonl`,
`questions.csv`, `aggregate.csv`, the two plots, and `provenance.json`
(config hash, bank manifest hash, git commit, seed, timestamp).

## JSONL schemas

**Bank input** (full spec in `bank.py`'s docstring): line kinds
`episode_header` (ids, receptacles, object classes, budget, n_days),
`truth` (piecewise-constant ground truth; every object needs a t=0 row),
`observation` (source `initial_tour` or `scripted` — the fixed stream),
and `question`. The synthetic fixture builder emits exactly this format,
so tests exercise the real loader.

**Run log** (one line per question; field-by-field in
`harness.QuestionRecord`): episode/agent/question ids, the full predicted
distribution, every action in order (senses embed returned contents),
the answer + confidence, truth, correctness, and budget
before/spent/after plus a `forced_answer` flag.

**Results**: `questions.csv` is the scalar projection of the run log (one
row per question); `aggregate.csv` has one row per (agent, stratum) with
accuracy and budget means, stratified `overall` / per `object_class` /
per `day_index`, each row carrying `budget_per_day` so runs at different
budgets concatenate into accuracy-vs-budget curves.

## Synthetic fixture

`bank.write_synthetic_bank` builds a 7-day, 3-object episode whose exact
accuracies are hand-derivable (derivation in
`tests/test_baselines_integration.py`): a static mug (everyone scores 1.0),
strictly periodic keys (timetable 1.0 vs most-frequent 0.5), and a
move-once laptop (last-observation 1.0 vs most-frequent 0.0).
