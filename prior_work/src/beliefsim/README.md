# Budgeted whole-house belief tracking on HOMER+

## Problem statement

A robot in an unfamiliar home may observe only a limited number of objects
per day. At every timestep it must maintain a belief over the location of
EVERY object in the house. It chooses where to spend its sensing budget.
Evaluation is the accuracy of the whole-house belief across all timesteps.

There is no per-object query. Held-out objects are not imposed; under a
tight budget some objects simply never get sensed.

## Why this replaced the E1/E2 pilot

The superseded pilot (`superseded/homer_pilot_2026_08/`) granted every model
65 days of complete state and then asked it to localize. In that regime 91%
of query instants are inertia, counting is near-optimal, and world knowledge
has nothing to contribute — the top five methods landed within 0.02 of each
other and five of them produced bit-identical held-out numbers. The
constraint added here is the **sensing channel**, which is the realistic one:
a robot cannot observe a whole house at once. Nothing about HOMER+'s dynamics
was changed to make the task harder.

## Setup

| | |
|---|---|
| data | `data/homer_traces/` (canonical traces, `src/homer/loader.py`) |
| households | A, B, C — 39-50 objects, 25-29 receptacles |
| timeline | 65 learning days then 10 scored days, one continuous index |
| timesteps | hourly, 07:00-23:00 (17 per day) |
| prior knowledge | **none** — the agent arrives knowing nothing |

The agent walks every day of the timeline, spends at most `B` observations
per day, and its belief is scored on every object at every hour of the 10
scored days. The learning days are not "training data" handed to a model;
they are simply days over which the agent spends budget before scoring
begins. There is no initial tour: everything the agent knows, it paid for.

### Observation model

**Object-level**: observe object *o*, learn its receptacle at that instant.
Nothing is learned about any other object, so there is no negative evidence
and the exclusion machinery in `baselines.beliefs.base` stays inert.

A receptacle-level model (visit receptacle *r*, learn everything in it) is
closer to a real robot and is the intended next step; the `Belief` seam and
the `SensingPolicy` interface are both shaped to accept it without touching
the loop. The active model is recorded in `results/provenance.json`.

### Three load-bearing choices

**Budget is per DAY; scoring is per TIMESTEP.** With ~50 objects and 17
timesteps, a budget of 5 freshly observes at most 5 of 850 object-instants
per day, so nearly every scored instant is far in time from any observation.
A per-timestep budget would silently measure observation freshness instead of
inference.

**Sensing at hour h precedes scoring at hour h**, so a just-looked-at object
is trivially correct. The inflation is bounded and it is not hidden: the CSV
carries `n_just_sensed` and `n_displaced_not_sensed`, so the strict reading
(displaced AND not currently observed) is available for every cell, and it is
a column in the diagnostics table.

**The harness spreads the day's budget evenly, at a phase drawn fresh each
day.** The factorial varies *what* to look at, not *when*. The phase must be
random: displacement on HOMER+ is concentrated in the evening (19:00-23:00
runs 12-15% displaced against 4-6% at midday), and with a fixed schedule a
budget of 2 that happened to land on 19:00 outscored a budget of 5 that
missed it. *When* to look is a real second axis on this data — worth more at
low budget than the choice of belief model — and it is left for future work
rather than folded in silently.

## Metrics

All emitted per timestep as sums and counts, so every reported average is a
weighted one computed by `beliefsim.scoring.aggregate_ratio`.

| metric | definition |
|---|---|
| **all-instant accuracy** | top-1 over every object, every scored timestep |
| **displaced-instant accuracy** | *primary.* Top-1 restricted to instants where the object is NOT at its learning-period modal receptacle |
| **displaced, not-sensed** | strictest reading: displaced and not observed at that instant |
| Brier | multiclass, over the full receptacle set, range [0, 2] |
| log loss | nats, floored at 1e-6 (max penalty 13.8) |
| just-sensed / not-sensed | accuracy split by whether the object was observed at the scored instant |
| staleness | mean hours since last observation, over objects ever observed |
| value per sense | (accuracy − never-sense accuracy) / budget |

The displaced slice is the primary metric because the all-instant number is
dominated by inertia: a predictor that always guesses each object's habitual
receptacle scores ~0.92. Its size is reported before any conclusion is drawn
from it — 560-663 displaced instants per household, 7.5-8.4% of instants,
38-100 per household-day. That supports household-level comparison, which is
the unit of analysis; it does not support reading a single household-day.

Argmax ties are broken by a seeded RNG and every cell is run over five seeds.
This is not cosmetic: the pilot's stable-sort tie-break turned its uniform
control into a measurement of one arbitrary receptacle's occupancy and
produced a published-sounding conclusion that was pure artifact. The
`uniform` belief is kept live as an end-to-end check — it must score 1/|R|,
and it does (0.035-0.043 against 0.034-0.040 expected).

## Factorial

Every cell of belief × policy × budget × household × seed.

| axis | levels |
|---|---|
| belief | uniform, last-observation, most-frequent, timetable, fremen, pooled-class |
| policy | never-sense, random, round-robin, staleness-first, entropy-first |
| budget | 0, 1, 2, 5, 10, 25, 50, all |
| household | A, B, C |
| seed | 0-4 |

2970 cells. Two combinations are dropped as exact duplicates, not as
omissions: budget 0 is run once (every policy at zero budget *is*
never-sense), and never-sense is not rerun per budget.

### Belief models

`last-observation`, `most-frequent` and `timetable` are the unmodified
classes from `src/baselines/beliefs/`, wired through `BaselineBelief`.
Decay is off, diverging from that panel's frozen 24 h half-life: that
half-life exists because our generated banks drift, and HOMER+ does not
(each day is an independent sample from one fixed schedule distribution).
Under a budget, evidence is the scarce resource, and a half-life would
collapse most-frequent onto last-observation.

`fremen` is `src/homer/fremen.py` refit from the agent's own observations,
at most once per simulated day. This is closer to the paper's setting than
the pilot was: FreMEn exists to extrapolate from sparse irregular visits, and
here the sampling times *are* the agent's sense times.

`pooled-class` is the cross-object competitor, backing off object-hour →
object-any-hour → class-hour → house-hour. It replaces the pilot's `Pooled`,
which keyed on the initial placement — there is no initial placement in this
setting. Both smoothing constants were chosen to maximise **this model's own**
accuracy, so the competitor gets its best shot:

| M_OBJECT | M_CLASS | mean accuracy (HH-A,B × B∈{1,5,25,all}) |
|---|---|---|
| **1** | **1** | **0.9312** |
| 1 | 2 | 0.9312 |
| 2 | 1 | 0.9311 |
| 2 | 2 | 0.9310 |
| 5 | 1 | 0.9302 |
| 12 | 2 | 0.9301 |
| 1 | 5 | 0.8594 |
| 12 | 5 | 0.8583 |

Selecting on reported data is mild overfitting, in the competitor's favour,
which can only make a later claim against it more conservative. Two earlier
versions of these competitors were strawmen and were fixed before any number
was reported: pooled without the object-any-hour level scored 0.44 against
0.92 at budget 1, and FreMEn falling through to uniform instead of to its own
sighting histogram scored 0.37 against 0.92.

All beliefs share the same-instant sighting short-circuit
(`_ExactSighting`), which `baselines.beliefs.base` already implements. Without
it the adapted models would win every just-sensed object outright while the
batch-fit models inferred their way back to a location they had just been
told — worth the entire gap between 1.000 and 0.956 at unlimited budget.

### Sensing policies

`SensingPolicy` is a **new interface**, not `baselines.policies.base.DecisionPolicy`.
That one is `decide(question, prediction, budget_remaining, t, last_sense) ->
AnswerNow | Sense`: driven by a question, choosing a *receptacle* to open in
service of one named object, terminating by committing an answer. This loop
has no questions, chooses *objects*, and never answers. There is nothing to
adapt. The sense-or-answer interface is correct for its own study and is
untouched; the belief interface *is* reused as-is.

`AgentView` holds no reference to `World`. A policy can read its own belief
and its own observation history and nothing else, which
`tests/test_beliefsim_loop.py` asserts structurally alongside budget
accounting (spend never exceeds B, violations raise rather than truncate) and
held-out unreachability.

### Forced held-out ablation

A small controlled condition: *k*=2 objects (`data/homer_traces/heldout_masks.json`,
5 draws) are unobservable to every method, so cross-method comparison is not
confounded by different policies leaving different objects unseen.

## Reproduction

```bash
PYTHONPATH=src python -m beliefsim.run    --out results --workers 32   # ~20 s
PYTHONPATH=src python -m beliefsim.report --out results                # ~10 s
PYTHONPATH=src python -m pytest tests/test_beliefsim_loop.py tests/test_scoring.py
```

`results/raw_results.csv` (63 MB, 566k rows) is the single source of truth and
is gitignored as regenerable; `results/raw_results.csv.gz` is committed beside
it. Every table and figure derives from it through one function, and micro vs
macro is a required argument that each table's header states.

## Limitations

* **n = 3 households.** Per-household columns are the result; aggregates are
  descriptive. No confidence intervals are quoted, because three households
  cannot support them. Seed spread is reported separately and is not a
  substitute for household count. The budget effect is clear in HH-C, present
  in HH-B, and essentially absent in HH-A — a one-household-of-three split
  that the macro average would otherwise hide.
* **HOMER+ has no weekly structure.** Day-of-week is not a generator
  variable (`reports/homer_spectra/`), so timetable runs with
  `day_scheme="all"` and FreMEn's weekly harmonics carry ~no amplitude. Any
  result about periodicity here is about *daily* periodicity only.
* **Days are self-contained.** Each HOMER+ day is an independent VirtualHome
  rollout opening with a full-state snapshot. Objects do not physically
  persist across midnight; what makes yesterday informative is schedule
  regularity, not continuity.
* **Budget 0 and budget "all" are degenerate by construction** — at 0 no
  method has observed anything and all sit at 1/|R|; at "all" every object is
  observed at every scored instant and all sit at 1.000. The discriminating
  range is 1-50.
* **Look timing is fixed by the harness**, so a policy cannot choose to spend
  its whole budget in the evening. On this data that choice would be worth
  more than the belief model at low budget.
* **The LLM arm is not wired.** `ours` and `llm_raw` are absent; the belief
  seam and policy interface are in place for them.
