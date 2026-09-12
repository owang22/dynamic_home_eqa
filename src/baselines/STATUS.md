# STATUS — basic baselines for the sense-or-answer study

## Update (2026-09-11, later: questions from day 0; hypothesis mixture + disambiguation sensing, trial run)

Continues past the disagreement STOP at the user's direction (the family
panel had passed the gate).

### Questions now start the day of the tour

`configs/fleet.yaml` had `first_question_day: 3` — a three-day warmup
with observations and no questions. Besides delaying examination, it
meant no question ever saw a single-sighting object fresh: the tour was
the only sighting and always days stale by the first query. Now
`first_question_day: 0`. Trial re-export of hh_001/hh_002 to
`banks/baselines/fleet_day0/` (90 questions on every day, day 0
included). The 20-bank fleet under `banks/baselines/fleet/` is NOT
re-exported — that is a full sweep and the frozen instrument's banks
should not silently change under it; re-export deliberately when wanted.

### `hypothesis_mixture` belief

`beliefs/hypothesis_mixture.py`, registered as candidate. Particles are
registry beliefs (default: 7 cheap family representatives;
`daytype_mixture`/`perpetua_star` cut for speed, addable via the
`particles` spec). One log weight per particle, uniform at reset. At
sighting time — BEFORE the sighting is applied — each particle is asked
for its distribution over the object's location and gains
`log(p_particle(observed receptacle))`, tempered by
`log_w = decay * log_w + log p`. Deviation from the brief's letter: the
predict-before-update hook lives inside `update()` rather than the
harness — every consumer delivers evidence through `update`, so this
covers harness, passive eval, replay and traces without widening any
shared contract. Empty looks update particle evidence but not weights.
Prediction = weight-normalized average of particle predictions; the
mixture adds NO second floor and NO second suppression (particles
already did both; single-particle mixture equals the particle exactly,
tested). ESS `1/sum w^2` tracked per weight update.

`decay` default 0.95, measured not guessed: the steady-state log-weight
gap scales as `1/(1-decay)`, and on the gate-pass fixture 1.0 and 0.98
both collapse (ESS 1.00/1.03) while 0.95 holds ESS 2.4 with a 0.57
leader. The brief's tests all pass: weights normalized+finite over an
episode; a badly predicting particle loses weight; decay 1 collapses
while the default keeps ESS above 1; one-particle equivalence.

### `hypothesis_disambiguation_sense` policy

`policies/hypothesis_disambiguation.py`. Extends `VoIThresholdSense`
via a new `_sense_values` hook (base class refactor; base behaviour
byte-identical): sense while `(voi(r) + beta * weight_entropy_reduction(r))
/ cost(r) >= lambda`. The bonus is the expected Shannon-entropy drop of
the weight vector over the binary found/not-found outcome for the
CURRENT question's object (`p_mix(r) = sum w_i p_i(r)`; posterior
weights one multiply per particle per outcome). At `beta = 0` the bonus
is never computed and the policy reproduces the myopic VoI policy
decision-for-decision and draw-for-draw (tested on full episode runs).
Each issued sense is classified needed-vs-disambiguation by whether raw
voi alone cleared the price (`sense_split`).

**Coherence gap, noted not fixed:** the bonus values BOTH outcomes of a
sense, but the mixture only updates weights on positive sightings — a
disambiguating sense that comes back empty for the queried object never
actually moves the weights. The policy is paying for information the
belief then discards half the time. Extending weighting to empty looks
(likelihood `1 - p_i(r)`) is the obvious follow-up.

### Trial run (2 households, first 7 days, lambdas {0.02, 0.08, 0.2} x betas {0, 0.5, 2})

`hypothesis_mixture_study.py` -> `results/hypothesis_mixture_trial/`
(frontier.png, ess_over_time.png, sense_split.png, trial_results.json).
~3 min total.

- **Frontier:** beta=0.5 sits above the myopic line over the whole
  swept range (e.g. 0.641 vs 0.633 at the low end, 0.660 vs 0.653 at
  24 senses/day); beta=2 at lambda=0.2 reaches 0.660 at 20.5 senses/day
  vs myopic 0.646 at 20.9. Direction is positive at matched budget, but
  the gaps are 0.005-0.015 on ~1 260 questions per config — binomial
  noise is ~0.013, so the trial shows a consistent trend, NOT a
  significant win. That is what a trial can show; a fleet run decides.
- **ESS:** disambiguation sharpens where there is room (hh_001,
  lambda=0.2: final ESS 1.05 at beta=2 vs 1.52 myopic). hh_002's
  weights sit near-collapsed (ESS ~1) for every policy — one particle
  dominates that household outright; not investigated (one line, moved
  on).
- **Split:** at beta=0.5 the bonus buys 6-14% of senses; at beta=2,
  lambda=0.2 over half the senses are disambiguation-only — beta=2
  spends most of its budget on the weights, and its accuracy at that
  configuration is the trial's best.
- Budget saturates at 24 senses/day for lambda <= 0.08, so the low-
  lambda frontier points bunch at the cap.

### Fat cut (trial-run pass)

- 2 households, 7 of 28 days, one seed, no intervals.
- Default particle list drops `daytype_mixture` and `perpetua_star`
  (cost); the two most-distinct families per the disagreement matrix
  are therefore underrepresented.
- Entropy bonus computed for the current question's object only; no
  scan for the most-disambiguating object.
- Empty-look weighting (the coherence gap above) not implemented.
- Fleet banks not re-exported at first_question_day 0.
- Pre-existing unrelated failure unchanged:
  `test_baselines_llm_belief.py::test_prompt_and_key_match_the_committed_fixture`.


## Update (2026-09-11: Dirichlet prior on the frequency path; belief disagreement measured — GATE PASSES on families, FAILS on parameter variants)

Two sections of the hypothesis-mixture brief. The second ends at a STOP;
nothing past it (the `hypothesis_mixture` belief, disambiguation sensing)
is built.

### Dirichlet prior on the frequency fallback

The frequency path turned an object's decayed placement counts into a
distribution by plain normalization, so ONE sighting gave a one-hot
histogram that the 0.02 floor mix turned into 0.98 confidence. It now
goes through `BeliefModel.dirichlet_normalized` — the posterior mean of a
symmetric Dirichlet over every location, `(count_r + alpha) / (total +
alpha * n_locations)`. `frequency_alpha` is configurable per belief spec
(`DEFAULT_FREQUENCY_ALPHA = 0.06`, set so one fresh sighting leaves ~0.40
on the observed receptacle in a median 27-location fleet household; 0.31
at a 39-location one). `alpha = 0` restores the empirical histogram
exactly, which is how the pre-migration smoothed-recency golden fixture
still runs.

**Which beliefs changed.** `most_frequent`, `timetable`, `markov1`
(stationary backoff only), `periodic_persistence` (the below-`min_departures`
degradation path only, as scoped), `smoothed_recency` (its frequency
component), `daytype_mixture` (its no-day-types fallback only). Models
already carrying a pseudo-count on counts keep theirs and do NOT stack a
second prior: the Markov transition row's Laplace alpha,
`hierarchy_backoff`'s shrinkage toward class and household pools,
Perpetua's switching prior, and `cold_start_distribution`.

**One reversal, measured.** Smoothing each day-type's timetable in
`daytype_mixture` took `test_two_regime_daytype_beats_most_frequent` from
a perfect score to 0.0: a type's weight comes from the day-type
posterior, so smoothing its timetable by its own sample size mutes
exactly the rare regime the model exists to detect. Per-type timetables
were reverted to empirical normalization. Consequence to note:
`daytype_mixture` is still one-hot off a single observation, because any
sighting at all creates a day feature and its no-day-types fallback is
then unreachable.

**Short run** (2 households, first 3 question-bearing days, passive diet,
769 single-observation (object, question) pairs):

| belief | mean conf. alpha=0 | >0.9 | mean conf. alpha=0.06 | >0.9 |
|---|---|---|---|---|
| most_frequent | 0.960 | 93.1% | 0.308 | 0.0% |
| timetable | 0.960 | 93.1% | 0.308 | 0.0% |
| markov1 | 0.960 | 93.1% | 0.073 | 0.0% |
| periodic_persistence | 0.960 | 93.1% | 0.073 | 0.0% |
| smoothed_recency | 0.969 | 96.9% | 0.058 | 0.0% |

Gate met — nothing sits near 1.0 any more. One line on something odd:
every single-observation case in these banks is >24 h stale (the initial
tour is the only sighting and questions start days later), so the "~0.4"
target is never actually exercised in the fleet. For the beliefs that
decay counts at 24 h the aged count falls well below `alpha *
n_locations` and those objects land near uniform (0.058-0.073 vs a 1/40
floor). Directionally right — stale single evidence IS weak — but it is a
larger calibration move than "0.98 -> 0.4", and the accuracy cost has not
been measured.

### Disagreement measurement — the gate

`src/baselines/disagreement.py`, `reports/baselines/disagreement/`. No
run logs exist on disk, so this is the short run only: passive diet
(initial tour + scripted evidence, no sensing), every belief predicting
every bank question, 2 households x full length = 4 500 questions. Per
question: whether all beliefs share an argmax, and the mean pairwise
Jensen-Shannon divergence (bits) across their distributions; broken out
by object volatility tercile (true moves per day, split within household)
and by hour of day. Plus a per-pair argmax-agreement matrix.

Two panels, because "a hypothesis about household dynamics" means two
things:

| panel | beliefs | unanimous argmax | mean pairwise JSD |
|---|---|---|---|
| family (one per model family) | 9 | **0.482** | **0.304** |
| parameter (`smoothed_recency` at 1/3/6/12/24/48 h) | 6 | 0.923 | 0.085 |

**Family panel: the gate passes.** Beliefs disagree on the argmax for
more than half of all questions and the divergence histogram is a broad
mode centred on 0.30 with essentially no mass below 0.10 — not
concentrated near zero. There is something for a mixture to operate on
and something for a sense to resolve. Disagreement tracks volatility the
way it should: unanimity 0.579 / 0.502 / 0.363 across calm / middle /
volatile terciles, JSD 0.279 / 0.304 / 0.328. Hour of day is much weaker
and mostly noise, with the expected quiet-hours effect at the edges
(23:00 unanimity 0.691 on n=110; 00:00 0.318 on n=22). The pair matrix
puts `perpetua_star` and `timetable` furthest from everything (0.61
agreement with each other) and the recency-flavoured group —
`last_observation`, `smoothed_recency`, `hierarchy_backoff`,
`periodic_persistence` — tight at 0.93-0.96.

**Parameter panel: the gate fails.** Varying only the smoothing
half-life over a factor of 48 moves the argmax on 7.7% of questions and
the divergence mass sits under 0.18 with a mean of 0.085. Terciles are
flat (0.955 / 0.910 / 0.903). A mixture whose particles are one family at
different rates has almost nothing to weight, and a disambiguating sense
would have almost nothing to sharpen. If the mixture is built, its
particles must differ in the SHAPE of the dynamics, not the rate.

**Figures.** `{family,parameter}_jsd_histogram.png` (figure 1) and
`{family,parameter}_argmax_agreement.png` (figure 2).

**STOP.** Handing back here as the brief requires.

### Where the fat was cut (this was a "will it work" pass)

- 2 households, as the brief's debugging-run rule says. For a gate this
  is thin; the family/parameter contrast is 3.6x in JSD, far larger than
  any plausible between-household wobble, but the absolute numbers are
  not fleet estimates.
- One parameter axis only (smoothing half-life). Varying the frequency
  half-life, or crossing the two, was not tried.
- `most_frequent`'s undecayed variant, the LLM belief (needs a filled
  prompt cache) and `oracle_program_posterior` (privileged) are out of
  both panels.
- No per-household bootstrap or any interval on these numbers.
- The Dirichlet's accuracy and log-loss cost was not measured anywhere;
  only confidence was checked, which is what the brief asked for.
- Pre-existing unrelated failure, untouched:
  `test_baselines_llm_belief.py::test_prompt_and_key_match_the_committed_fixture`
  (missing committed fixture; fails on a clean tree too).


## Update (2026-09-10: room-change travel cost — a sense outside the robot's room costs 1 + c)

Until now an active sense cost one budget unit wherever the robot stood.
It now costs 1.0 for a receptacle in the room the robot is already in and
`1 + c` for one anywhere else — one parameter, distance-free, and at
`c = 0` exactly the model the package had before. What a sense REVEALS is
unchanged (`Sense(receptacle_id)` still returns that receptacle's full
contents), and the passive patrol is unchanged.

**Where it lives.** Bank headers gained `receptacle_rooms` (receptacle ->
room, every in-house receptacle; OUT_OF_HOUSE is in no room and absent)
and `home_base_room` (the room with the most receptacles, ties by room id
sort order); both are optional and the loader rejects one without the
other. `Episode` and `EpisodeContext` carry them, plus
`EpisodeContext.sense_cost(receptacle_id)` and a live `RobotPosition` the
harness owns and mutates — so policies price their options without the
`decide` signature widening. `harness.run_episode(agent, episode,
room_change_cost=0.0)` tracks the position (home base at each day start,
the room of every ambient room visit delivered up to `t_query`, the room
of every receptacle actively sensed), charges `cost(r)`, and refuses a
sense whose cost exceeds the remaining budget. Budgets are floats
throughout (`budget_before/spent/after` and the loop variable);
`budget_per_day` stays an int in the header. `QuestionRecord` gained
`n_senses`, `same_room_senses` and `robot_room_at_query`, and sense
actions log their room, cost and same-room flag. Only
`VoIThresholdSense` and `VoIBudgetPriceSense` can see the price: they
sense while `voi(r) >= lambda * cost(r)` and pick the receptacle
maximizing `voi(r) / cost(r)`. Every other policy is untouched. New:
`bank.write_room_cost_bank` (fixture), `room_change_cost_study.py`
(driver), `tests/test_baselines_room_cost.py` (29 tests). `mypy --strict`
clean on every new and touched file.

**Banks.** All 20 re-exported to `banks/baselines/fleet_room_cost/`,
leaving `banks/baselines/fleet/` in place. `--stage verify_banks`
confirms each rebuilt bank is byte identical to its predecessor except
for the two new header fields (`bank_verification.md`); the fleet
healthcheck flags are unchanged from the committed summary.

**Run** (`results/room_change_cost/`, 1 500 cells: 3 beliefs x 5 policies
x 2 budgets x 5 costs x 10 test households, 22 500 questions per grid
row, ~2 h on 20 workers).

*The c = 0 regression against `results/voi_policies/grid.csv` FAILED, and
the failure is pre-existing.* 20 of 30 cells match to six decimals —
every cost-blind cell on all three beliefs, and every LastObservation
cell. The 10 VoI cells on PeriodicPersistence and PerpetuaStar differ by
0.0003-0.008. Re-running those cells under the CURRENT COMMITTED CODE,
unmodified, on the ORIGINAL banks reproduces THIS study's numbers
exactly (7/7 cells tested, recorded in `head_baseline.json` and rendered
into `regression.md`) and not the reference csv's. Cause:
`results/voi_policies/provenance.json` records commit `eb731bcd` with
`git_dirty: true` at 2026-09-08T20:33, while the Part B commit
`230a2701` landed 3.6 h later with a different `voi_sense.py`; the
reference csv was produced by code that was never committed. **Follow-up
for the owner, outside this brief: `results/voi_policies/`'s VoI rows are
stale by up to 0.008 and its `findings.md` headline carries the same
caveat; regenerating that study under committed code would fix both.**
Owner decision on 2026-09-10 was to interpret the c > 0 results with this
documented, since the check's purpose — "did this brief change c = 0
behaviour?" — is answered NO by the stronger HEAD comparison.

*Status of these conclusions (owner, 2026-09-10): PROVISIONAL.* The
question set is being redrawn to reflect how people actually ask, rather
than the present uniform draw over objects and awake instants. Findings 4
and 5 are conditioned on it — finding 4 (where the robot stands when a
question arrives) is a property of the patrol crossed with the query
distribution and nothing else, and it is the ceiling on the whole effect
— so their magnitudes should not be quoted until the queries settle. The
mechanism findings (2 and 3) are arithmetic on the policies and are not
at risk. A high-cost arm (c in {0,2,4,6,8,10} with budget scaled by
1 + c, isolating the price RATIO from starvation) is implemented behind
`--costs/--compensate-budget` and was deliberately NOT run for the same
reason; the command is in `results/room_change_cost/findings.md`.

*Headline.* Every policy loses accuracy as c rises (travel eats budget);
the cost-aware pair loses less. The gap between the best cost-aware and
best cost-blind policy moves toward cost-awareness in 5 of 6 cells,
monotonically in 4. The brief's target question — does the advantage
appear on LastObservation, where VoI lost in Part B — is YES at 90/day
and it is the largest effect in the study: the gap closes from -0.100 to
-0.014 across c in [0, 2]. But it is a recovery, not a win (-0.014 is
still a loss at the 0.01 resolution the sample supports), and the
mechanism is not the expected one: the gap closes because
ResolvableMassSense FALLS (-0.109) while VoI barely moves (-0.023).
The gate spends on the stale-but-confident questions one-step voi will
not touch, so its accuracy is elastic in how many senses it can afford;
VoI's was already insensitive to its own sense count because it was
mis-allocating. The cost-aware advantage is robustness to the price more
than exploitation of the discount — and much of that robustness is
inherited from under-spending, which was Part B's weakness. Cost-aware
policies do take the discount: their same-room sense share roughly
doubles at the FIRST non-zero price (LastObs@90 VoIThreshold 0.369 ->
0.713 at c = 0.25) and then plateaus. Cost-blind policies are NOT flat
across c as predicted — they drift +0.05 to +0.11 — but for a benign
reason: their choice sequence is identical at every c, and a higher price
merely truncates it earlier, leaving the prefix where the robot has not
yet wandered from where the patrol left it. The two signals are
distinguishable (gradual monotone drift vs a step at the first price).
The robot's own room contains the queried object's most likely receptacle
on only 0.183-0.200 of questions — against an INDEPENDENCE baseline of
0.182-0.184 (per household, the inner product of the robot-room marginal
with the argmax-room marginal; `1/n_rooms` is the wrong reference because
rooms are far from equally likely). So position carries essentially no
information about the answer: LastObs +0.018 above independence, Periodic
+0.007, PerpetuaStar -0.001, exactly on it. That is the ceiling on the
whole effect and no policy can move it.

*OracleBelief joined the grid* (4 beliefs), at the eps 0.4 /
half-life 12 h weighting the v2 sweep SELECTED — not the module defaults,
which are still the whole-episode setting that collapsed at the ESS gate,
so `belief_spec()` reads `results/oracle_program_posterior/selected.json`
and refuses if it is missing. Part B never ran the oracle, so its policy
configuration is the consensus one (the convention `voi_study` already
used for PerpetuaStar), marked `consensus: true` in `configs.json`. It is
the strongest confirmation of Part B's thesis in the study: at 90/day the
cost-aware advantage is +0.115 at c = 0, the largest anywhere here, and
it DECAYS to +0.038 as c rises — the opposite direction to the other
three beliefs. On the one genuinely calibrated belief VoI wins outright,
and the travel cost erodes that win rather than creating it. The
resolvable-mass gate sits nearly flat at ~0.785 because a calibrated
belief usually yields a singleton conformal set, so it barely senses.
Its median ESS is 23.4 under NeverSense (healthy; the gate is defined on
the passive diet) but ~1.4 under SequentialSearch — see the note on the
ensemble's evidence appetite below.

One clear practical caveat found by the run: a lambda tuned at c = 0 does
not survive a change of price scale. VoIThresholdSense at Part B's best
lambda = 0.2 on PerpetuaStar@24 needs `voi >= 0.6` at c = 2, which almost
nothing clears; it senses only in its own room (same-room share 1.000),
leaves three quarters of its budget unspent (cost/q 0.064 against a 0.267
allowance) and drops to 0.562, below SequentialSearch. Scaling lambda by
cost makes the rule cost-correct but leaves its calibration
cost-dependent.

Deviations and design decisions:

1. **The passive patrol does not react to the policy.** A scheduled
   visit sets the robot's position to its own room regardless of where a
   sense has just sent it. This is deliberate: the banks must stay frozen
   and identical across every policy under test, which is impossible if
   policy actions alter the observation stream. The consequence is that
   the robot can teleport between a sense and the next ambient visit; the
   cost model prices the sense, not the patrol.
2. **The day-start reset is an event at the day boundary.** The harness
   delivers all evidence with `t < day_start` BEFORE resetting position,
   so a late visit from yesterday cannot outlive the reset, and a visit
   at exactly `t = day_start` belongs to the new day. Delivery order to
   the beliefs is unchanged, so no belief sees anything different.
3. **The loop bound is the sensable-receptacle count.** The old
   `budget_remaining + 1` bound does not terminate under fractional
   costs. A receptacle may not be sensed twice within a question, so that
   count is already an upper bound for every policy in the roster; the
   cap logs a warning and forces an answer if it ever fires (it does not
   for any policy here).
4. **`VoIBudgetPriceSense`'s controller still counts SENSES, not cost.**
   The brief specified exactly two changes to the VoI policies and
   "nothing else changes", so `spend_rate` remains senses per question
   while `budget_rate` is budget units per question. At `c > 0` these are
   no longer commensurable and the controller under-measures its own
   spend by roughly the average cost multiplier. Measured effect: it
   stops modulating and just runs into the cap — at budget 90 its cost
   per question is 0.85-1.00 at every c (against VoIThresholdSense's
   0.55-0.94) and it carries the higher forced-answer rate of the pair
   (0.10-0.17 vs 0.001-0.066). Its rows are a capped policy's, not a
   budget-tracking one's. The one-line fix (book `cost` in `_on_sense`)
   is deliberately NOT made here — it is a change to the experiment, not
   to its plumbing — but it is the first thing to change if this arm is
   rerun.
4b. **Forced-answer rates at c > 0 are largely an artefact** and are
   non-monotone in c (SequentialSearch@24: 0.000, 0.652, 0.410, 0.038,
   0.079). Policies guard with `budget_remaining <= 0`, which no longer
   catches "positive but unaffordable", so the flag measures leftover
   budget granularity: at c = 0.25 the day ends on leftovers of
   0.25/0.5/0.75 that buy nothing, while at c = 1 a leftover of exactly 1
   still buys a same-room look. Accuracy is unaffected. Teaching the
   cost-blind policies to check affordability would remove the noise but
   would also give them a form of cost-awareness, so it was not done.
5. **ON_PERSON sits in the `person_check` pseudo-room** (the existing
   `RoomMap` convention), and the fleet's `round_robin_patrol` never
   visits it, so on these banks sensing ON_PERSON always pays the
   surcharge. Noted rather than special-cased: it is one receptacle of
   22-38.
6. **Policy slugs in the study are Part B's own**, hyperparameters and
   all, because every generator derives from `(seed, belief, policy slug,
   budget, episode)` — relabelling `..._best` would reseed the
   tie-breaks and the `c = 0` regression against `results/voi_policies/`
   would fail for reasons having nothing to do with cost.
   `VoIBudgetPriceSense` likewise keeps Part B's fixed `lam0 = 0.05`.
7. **`representative_grid` cells gained a fourth coordinate** (the
   room-change cost) and the grid csv three columns
   (`room_change_cost`, `cost_per_question`/`cost_per_day`,
   `same_room_sense_fraction`). `senses_per_question` now counts SENSES
   where it used to sum spend; the two coincide at `c = 0`, which is what
   keeps the regression exact. Part-file names are unchanged at `c = 0`,
   so the earlier studies' `questions/*.jsonl.gz` paths still resolve.
8. **OracleBelief's ESS depends on the POLICY, and that is not a bug.**
   `OracleProgramPosterior` is not the routine oracle: the routine oracle
   (`routine_oracle.py`) takes no observations, but this belief keeps the
   same 800-realization ensemble alive and weights each realization by
   agreement with everything the agent has seen. A paid sense is a full
   receptacle readout, i.e. one check per KNOWN OBJECT (35 on hh_001),
   so a sensing policy injects far more evidence per question than the
   passive diet does, weights concentrate, and ESS falls — 23.4 under
   NeverSense against ~1.4 under SequentialSearch. The gate is defined on
   the passive diet, where it passes; the sensing figure is a property of
   the belief's evidence appetite, and it is worth remembering that under
   an active policy the oracle is close to a point estimate again.

   A hard "keep every realization NOT INVALIDATED" rule was considered as
   the alternative to the soft eps weighting and MEASURED on hh_001
   (24 850 object-level observations x 800 realizations): over the whole
   episode it leaves ZERO survivors at every one of the 2 250 question
   times, because the best realization already disagrees with 676
   observations. Restricted to a trailing window it is bimodal rather
   than graded — survivors (mean, % of questions with none): 0.5 h 675,
   5.7%; 1 h 552, 11.0%; 3 h 178, 27.9%; 6 h 95, 54.4%; 12 h 9.7, 89.1%;
   24 h and beyond 0, 100%. The p10/p90 at 1 h are 0 and 800: the rule
   almost always returns either the entire prior (uninformative) or
   nothing (undefined). That bimodality is exactly what the soft
   multiplier exists to avoid, and it is why the module says "soft, never
   a hard filter". If the idea is wanted in a well-defined form, the
   robust variants are rank-based (keep the k least-disagreeing in the
   window, never empty and never all) or tolerance-based (allow up to m
   disagreements in window H) — both are two-knob hard filters that
   interpolate where the pure rule cannot. Not implemented; it is a
   model change and therefore the owner's call.

9. **Two pre-existing failures, neither touched by this work.** The
   golden run-log fixture did not reproduce at HEAD on this machine (one
   ULP in a `LastObservation` distribution) before any change here; it
   was regenerated along with the schema change this brief does make.
   `tests/test_baselines_llm_belief.py::test_prompt_and_key_match_the_committed_fixture`
   fails because `banks/baselines/sweep/visits6/` is gitignored and
   absent. `mypy --strict` reports one error in `passive_eval.py` from an
   uncommitted edit that predates this work.

## Update (2026-09-09: STAR-style indexed memory + LLM decision loop — code landed, runs pending banks)

An exploration per the STAR brief (Chen et al., arXiv:2511.14004): does
an LLM reasoning over retrieved memory beat a script that mimics it?
New files only — `memory/indexed_observation_log.py` (exact-match
spatial/semantic/temporal record store over the agent's own stream),
`memory/recall_tools.py` (the three free recall actions as ~15-line
prompt blocks), `policies/star_memory_loop.py` (one loop, pluggable
selector: `ScriptedRecallThenVerify` control and `QwenSelector`),
`memory/serving.py` (served-vLLM HTTP glue + full-request-hash prompt
cache), `star_study.py` (subset/offline/llm/report stages, outputs
`results/star_memory_loop/`), `tests/test_baselines_star_memory.py`
(19 tests). Registry entry: `star_memory_loop` in `cli.build_policy`
(scripted selector only; the LLM selector needs a served endpoint and
is wired by the study driver). All new files `mypy --strict` clean.

Deviations and design decisions:

1. **Study-local runner, not the harness.** Two harness contracts make
   the STAR arms impossible under `run_episode` as-is: policies never
   receive the ambient observation stream (only beliefs do), and the
   final `Answer` is always assembled from the standing prediction's
   argmax, so a policy cannot commit a location of its own. Editing the
   harness is out of scope for this brief, so `star_study.run_star_episode`
   mirrors it exactly (delivery order, per-day budget accounting,
   forced-answer flag, unsensable check, exact-match scoring) plus the
   two additions: every piece of evidence also feeds the policy's
   memory index, and the selector's `answer_override` is committed when
   present. Baseline arms run through the real harness unchanged.
2. **Sampled questions, full-episode replay.** Every arm replays FULL
   episodes (identical diet, real shared budget); records are kept for
   the 400 sampled questions only. In the LLM cells the LLM selector
   engages only on sampled questions; elsewhere the scripted control
   acts (and spends) in its place, so a sampled question sees a
   realistic budget state without ~22k LLM calls per cell. The two STAR
   arms therefore face identical non-sampled spending by construction.
3. **Subset stratification uses ground truth.** Regime labels
   (`stale_in_house`/`came_back`/`truly_out`) come from
   `exclusion_migration_replay.question_facts`, which reads truth.
   Legitimate: the sampler is evaluation design, not an agent. 400 =
   200 per budget x ~67 per regime; ids in
   `results/star_memory_loop/subset.json`. Household split read from
   `results/voi_policies/provenance.json` and cross-checked against the
   re-derived reference split (drift is a hard error).
4. **Found-at-query-instant auto-answers.** In both STAR arms a sense
   that returns the queried object ends the question (a hit at the
   query instant is ground truth; the belief one-hots on it anyway).
   Saves one LLM call per hit and keeps the two selectors comparable.
5. **`answered_from_memory` accounting.** A selector `AnswerCall` that
   merely copies the fallback argmax (`from_fallback=True`) is NOT
   counted as answering from memory; only genuine memory-grounded
   answers with zero senses are.
6. **mypy**: `requests` added to the existing untyped-third-party
   override block in `pyproject.toml` (`memory/serving.py` imports it
   for the provenance probe). Package-wide `--strict` is NOT currently
   clean (pre-existing drift in `household_report.py`,
   `household_analysis.py`, `multiseed_report.py`, `perpetua_filters.py`
   — untouched here); the brief's requirement is enforced per new file.
7. **Banks**: `banks/baselines/fleet/` was absent on this machine
   (gitignored). Regeneration was prepared but the owner is supplying
   the generated banks instead; the hash check against
   `reports/baselines/fleet/fleet_summary.json` (`bank_manifest_hash`
   per bank) decides comparability before any run. Note the committed
   fleet summary already flags every bank (`not_impossible` at the
   24-budget default everywhere, plus `stationarity`/`not_trivial` on
   hh_003/011/013/014/016); those flags predate this study and did not
   stop the VoI runs, so they are treated as data-source properties,
   not stop conditions — the hash match is the gate.

Runs pending: subset -> offline arms -> LLM arm (served model; default
flag `Qwen/Qwen3.8-27B` per `llm_generate.py`, actual serving model on
this box to be recorded in `llm_run.json`) -> findings.

## Update (2026-09-08, later: OracleBelief stopped at the ESS gate; value-of-information policies; delayed-label conformal feedback)

Three parts of one brief, committed separately in order. Shared
machinery: `representative_grid.py` (the representative grid every part
runs: beliefs LastObservation, PeriodicPersistence, PerpetuaStar,
LLMBelief, OracleBelief; policies NeverSense, SequentialSearch plus the
part's own; budgets 24 and 90; the 20 fleet banks and the
calibration/test split of `results/conformal_sweep_v2/`, re-derived and
checked against its `calibration.json`; per-day accuracy written for
every cell). LLMBelief cells are skipped in every part: the only
completions that exist (`reports/baselines/llm_floor/`) cover a
stratified sample of the passive questions, so a passive replay already
leaves most queried predictions unanswered and any sensing changes the
prompts further; each part's findings carry the measured unanswered
fraction.

**Part B — value-of-information policies (`policies/voi_sense.py`,
driver `voi_study.py`, results `results/voi_policies/`).** At a decision
point the value of answering now is `max(p)`; sensing a sensable untried
receptacle r is worth `p(r) + (1 - p(r)) * max(p') - max(p)`, where p'
is p with r zeroed and renormalised (a fresh empty look suppresses fully
in the base pipeline). Exact one-step lookahead, arithmetic on the
belief's own distribution, no cloning and no mutation; the greedy form
of the classical search-and-stop rule (Ross 1969; Weitzman 1979), valid
because senses within a question are at the query instant.
`VoIThresholdSense` senses the argmax-voi receptacle while max voi >=
lambda; `VoIBudgetPriceSense` moves lambda by
`gamma * (spend_rate - budget_rate)` after each question, clipped to
[0.001, 0.5]. Run at lambda in {0.01, 0.02, 0.05, 0.1, 0.2, 0.3} under
the caps and with the cap removed (the price-based frontier), gamma in
{0.01, 0.05, 0.1}, against ResolvableMassSense and conformal-global at
the v2 sweep's best configuration per (belief, budget). The refit global
quantiles reproduce the v2 sweep's stored values exactly on every shared
(belief, alpha), which pins the two studies to the same calibration.

*Headline.* Each cell is 22 500 questions (95% Wilson interval about
+/-0.006), so the read-out uses a 0.01 resolution. VoI is AHEAD in one
cell: PerpetuaStar at 90/day, VoIThresholdSense(lambda=0.05) 0.719 at
0.84 senses/q against the resolvable-mass gate's 0.681 at 0.99 (+0.038,
and cheaper). It is BEHIND in two: LastObservation at 90/day 0.705 vs
0.806 (-0.100) and PeriodicPersistence at 90/day 0.776 vs 0.853
(-0.076). The other three cells are within noise (all |delta| <= 0.009).
The mechanism is visible in `budget_reallocation.png`: the two classical
beliefs are 0.95+ confident on 73-93% of questions, so one-step voi is
below every lambda there and the policy under-spends on exactly the
stale-but-confident questions the conformal gate catches. VoI is only as
good as the calibration of the belief it reads, and it wins on the one
graded belief in the panel.

*Reallocation (question 2) held.* VoIBudgetPriceSense spends 9-39 times
more on the least-confident bin than on the most-confident one, against
4-15 for SequentialSearch, and accuracy in the hard bins rises with it
(LastObservation at 90/day: 0.64 -> 0.72 in [0, 0.5), 0.49 -> 0.76 in
[0.5, 0.8)). It tracks any cap without tuning (0.25-0.26 senses/q
against a 0.27 allowance, 0.81-0.99 against 1.00). Gamma made no
difference anywhere (0.01/0.05/0.1 within 0.002), so this run says
nothing about the right adaptation speed. Question 3 (does VoI reach the
oracle ceiling with fewer senses) is unanswerable: OracleBelief is not
in the grid, per Part A's gate.

*Soft-budget arm.* With the cap removed the frontier keeps climbing:
PeriodicPersistence reaches 0.929 at 2.56 senses/q (lambda 0.01) and
0.872 at 1.36 (lambda 0.02), both far above anything the capped runs
reach. The ceiling is high and the price rule finds it; the caps, not
the rule, are what bind at 24 and 90.

Deviations (Part B): (1) the reference sweep never ran PerpetuaStar, so
its comparators use the configuration most v2 beliefs preferred at that
budget ("consensus" in `comparators.json` and in the findings tables);
its +0.038 is against those settings, not against a gate tuned for it.
(2) The soft-budget arm runs the threshold policy only: the price
controller needs a budget to track, and with the cap removed there is
none. (3) `frontier.png` carries Wilson intervals and the cap-removed
frontier in one figure per (belief, budget) rather than the v2 sweep's
one-panel-per-belief layout, and `budget_reallocation.png` is new.

**Part A — OracleProgramPosterior (`beliefs/oracle_program_posterior.py`,
registry `oracle_program_posterior`, display name OracleBelief).** The
routine oracle's 800 re-realizations (seeds 1001-1800; seed 0, the
bank's world, never included) kept alive for the episode as a
minute-resolution location grid per object (change points from the
same truth loader the bank export uses; cached under
`banks/baselines/oracle_realizations/`, regenerable, ~30 s per
household), each realization log-weighted by consistency with every
observation (positive sighting or empty look: log(1) on agreement,
log(0.05) on disagreement, incremental, never a hard filter);
`predict` is the weighted location distribution; opts out of the base
negative-evidence step; floor mix and the query-instant sighting
short-circuit as for every model; `effective_sample_size()` and
`last_prediction_diagnostics()["ess"]` expose the degeneracy
diagnostic. Driver `oracle_posterior_study.py` (stages realize,
ess_gate, grid, report). **The ESS gate stopped the study**: under the
passive diet the fleet median ESS is 1.00 on every bank (maximum 3.41
over 45 000 questions), so the grid was not run, per the brief. A
diagnostic run explains it (`results/oracle_program_posterior/findings.md`):
the seed-0 control realization agrees with every observation on 18 of
20 banks (11-12 disagreements on hh_004/hh_005), so matching is right;
but the BEST of 800 realizations disagrees with 480-846 of the 18-47
thousand object-level observations per bank and the second-best is
1-15 disagreements behind, each worth a factor 0.05 — ESS 1 by
arithmetic. No eps gives a middle ground on whole-episode
realizations; windowed matching or re-realizing from the observed state
are the candidate fixes, and that choice is the owner's. Parts B and C
run their grids without OracleBelief and say so.

Deviations (Part A): (1) "routine_oracle's default seed count, excluding
seed 0" is satisfied by construction — the routine oracle's seed range
starts at 1001 (per-bank offset as `llm_floor`/`household_analysis`);
no seed was removed. (2) The per-question ESS is read after the
question resolves (post-sense for sensing policies) and, for the gate,
under NeverSense, where the two coincide. (3) The realization cache
lives under the gitignored `banks/` tree rather than in the results
directory, because it is 5 MB per household and regenerable.

## Update (2026-09-08: the exclusion veto is gone; negative evidence is a soft, decaying observation over the full location space)

Owner decision, implemented in `beliefs/base.py` and documented at the
top of that module: every model now outputs one distribution over all
receptacles plus OUT_OF_HOUSE with a uniform floor (`floor_mass` 0.02),
an empty look at a sensable receptacle multiplies that receptacle by
`1 - 2^(-age / half_life)` using its newest look not superseded by a
strictly later sighting (`negative_half_life_h`: the model's own
half-life where it has one, else 24 h), and the result is renormalised.
No veto, no uniform redistribution, no all-excluded fallback, no
elimination logic in any policy: OUT_OF_HOUSE never receives a factor,
so after a full sensable sweep at the query instant its floor mass is
all that survives and the belief's own argmax answers it (the solvable
invariant still holds everywhere without the policy naming anything).
`negative_observations(object_id, t)` is the public readout of the
recorded looks. Perpetua opts out of the suppression step (its filters
already ingest the looks); the LLM belief's own answers opt out too (the
looks are in its prompt) while its LastObs fallback does not.
`exclusion_floor`, `MAX_EXCLUSION_FLOOR`, SmoothedRecency's histogram
backoff and `ExpiringExclusionLastObservation` are gone (the pipeline
now IS expiring soft exclusion; its scenarios moved to the base
pipeline tests); the LLM-floor report lost its expiring-comparator
section. The paired replay (`exclusion_migration_replay.py`, report
under `reports/baselines/exclusion_migration/`) runs the frozen panel
and PerpetuaStar under NeverSense and SequentialSearch on the 20 seed-0
fleet banks at the bank budget with the old rule (the replay-only
`legacy_exclusion_veto` flag, which reproduces the pre-migration golden
log byte for byte) and the new pipeline.

**Headline (45 000 questions, old -> new).** Passive: LastObs 0.592 ->
0.618, MostFreq 0.586 -> 0.622, Timetable 0.531 -> 0.560. With
SequentialSearch at 24 senses/day: 0.651 -> 0.671, 0.636 -> 0.673,
0.578 -> 0.598. PerpetuaStar is identical under both (control). Every
gain is at ages of a day and more (+0.11 to +0.19 passive), and all of
it comes from one regime: `came_back` (truth equals the last-seen
receptacle and an ambient visit had found it empty since; 2 633
questions) goes from 0.00 to 0.95-1.00 passive, because the look
decays and the last sighting wins back the argmax. The price is the
other regime: `truly_out` (6 195 questions, 14% of the set) passive
accuracy falls from 0.205 to 0.000, and with SequentialSearch from
0.26 to 0.02. Passive OUT_OF_HOUSE answers all but vanish: 4 395 fired
(1 270 right) -> 8 fired (4 right) for LastObs, and the same for the
other two. `stale_in_house` moves by at most +0.01 passive and +0.03
to +0.04 with search.

**Which parts of the expected signature held.** came_back rises for the
graded models: held. truly_out passive accuracy dips: it did, to zero.
Search accuracy holds or rises: held. OUT_OF_HOUSE over-firing "shrinks
toward the truth rate": did NOT hold; it shrank past it to nothing.
This is arithmetic, flagged before the run and confirmed by it: OUT's
share of the floor is 0.02/N (about 0.0009 on a 23-receptacle bank)
while the last-seen receptacle keeps about 0.98 * (1 - w); with a 24 h
half-life OUT can only win when the last-seen receptacle was looked at
empty within about two minutes of the query, and only the newest look
counts, so negatives do not accumulate. Passive out-of-house answering
is therefore not reachable under this design; within-question
elimination by a sweep is exact. If passive reachability is wanted, the
knob is a separate OUT_OF_HOUSE prior share, not the uniform floor;
that is a design decision, not made here.

**Reports regenerated under the new semantics (A5).** Fleet
healthchecks (`reports/baselines/fleet/`, banks re-exported byte
identical): NeverSense accuracy rises on every home, mean +0.026 LastObs,
+0.036 MostFreq, +0.030 Timetable (smallest +0.004, largest +0.064);
search at the bank budget mean +0.024 (range -0.034 to +0.060);
`solvable` passes everywhere; three advisory flags moved (hh_003 now
also flags not_trivial, hh_017 no longer flags discriminative, hh_018
now does). Household analysis (`reports/baselines/household_analysis/`,
100 banks, 11 models): at a day and older the classical models now sit
above the survival models where they sat below them (all homes pooled,
1-2d: LastObs 0.287 -> 0.371, MostFreq 0.284 -> 0.415, Timetable 0.284
-> 0.400, PerpetuaStar 0.352 unchanged; 3d+: LastObs 0.168 -> 0.339,
MostFreq 0.195 -> 0.357); the two time-of-day models lose a little at
short ages (DaytypeMix 3-6 h 0.709 -> 0.670, 1-3 h 0.782 -> 0.752;
Timetable about -0.01) because a strong time-of-day prior on a
receptacle that was looked at empty an hour ago is now suppressed by a
factor of a few percent rather than vetoed. The `perpetua_cases` split
is kept as a diagnostic of the same situations; its "stayed, EXCLUDED"
row is now 1.00 for LastObs. LLM floor (`reports/baselines/llm_floor/`,
score and report stages rerun on the cached completions; every prompt
key hit): the classical comparators answer OUT_OF_HOUSE on 0.0-0.1% of
questions (LastObs 0.001 recall on the 5 729 true out-of-house
questions in the sample; the LLM stays at 0.370 recall, 0.620 at a day
and older), and at a day and older LastObs is now above the LLM (0.352
vs 0.325 at 1-2d, 0.356 vs 0.282 at 3d+). The report's comparator
columns key on bare class names; the loader now strips the parameter
suffix, which the previous report had not done. rate_sweep and the
bake-offs were not rerun; their findings and summary files carry a
one-line notice that they predate this migration.

**Deviations from the brief, logged here per the repo convention (no
PR workflow on this repo):**

1. The LLM belief's own answers skip the suppression step like
   Perpetua (the negatives are in its prompt); only its LastObs
   fallback runs the full pipeline. The brief listed only Perpetua.
2. `llm_floor`'s expiring-exclusion comparator rows and report section
   are dropped with the retired model rather than re-expressed.
3. SmoothedRecency's negative half-life is its smoothing half-life
   (6 h), the knob that already says how fast its evidence ages; the
   brief said "the model's own half-life parameter" and it has two.
4. The supersession rule keeps the existing equal-time convention: a
   look at exactly the instant of a sighting elsewhere still counts
   (the brief's sentence 2 says "strictly later sighting", its step 3
   "look strictly later than the sighting"; the code and its tests
   follow sentence 2, unchanged from before).
5. The decay-aware room-visit test needs "fresh" to mean one minute
   after the last look (the arithmetic above); it asserts the stale
   case three days later.
6. The pre-migration golden log was kept as
   `tests/fixtures/baselines_golden_run_log_legacy.jsonl` with a test
   asserting the legacy flag reproduced it byte for byte; both were
   deleted with the flag in the cleanup below, as planned.
7. Three pre-existing `mypy --strict` errors in `llm_floor.py` were
   fixed in passing (touched file).

**Conformal program on the new semantics.** `results/conformal_sweep_v2/`
reruns v1's alpha range (0.02-0.5) at budgets {24, 45, 90} and adds two
policies: `ResolvableMassSense` (sense only while the conformal set has
more than one member AND its mass on sensable untried members is at
least tau) and `ACISense` (alpha updated online by
`alpha += gamma * (target - err)`, the error judged on the set formed at
the question's first decision, fed either by ground truth every question
or only when the question's own senses revealed the truth). Four
findings, with numbers in `findings.md`: (1) the achievable alpha floor
barely moves (0.4 old -> 0.4 new for three of five beliefs, 0.4 -> 0.3
for two) — OUT_OF_HOUSE's floor share is too small to shift calibration
until alpha is already near 0.4-0.5, the same arithmetic as the replay's
caveat; (2) the mechanism table's expectations hold except truly_out
passive reachability, which a second independent measurement confirms
does NOT hold (memory-answer accuracy on truly_out 0.21 old -> 0.000
new for every belief); (3) ResolvableMassSense beats conformal-global's
own best frontier point for three of five beliefs at budget 90
(LastObs +0.020, Timetable +0.067, Periodic +0.002), loses at budget 45,
ties at 24 — no uniform winner; (4) ACI with oracle feedback holds the
target coverage tighter than static calibration everywhere (day-to-day
sd 0.012-0.017 vs 0.030-0.065) and corrects a real 0.03-0.05 static
miscalibration for two beliefs, but with sensed-only feedback — the
deployable mode — it undercovers badly (0.54-0.63 against a 0.70
target) because only 1-4% of questions ever produce feedback and those
are the ones that got swept.

**Cleanup.** `legacy_exclusion_veto`, its old-semantics branch, the
`_legacy_apply_veto` method and the all-excluded warning state are gone
from the base class and from all eleven concrete constructors and the
registry; the two tests and the fixture that exercised the flag are
deleted with it. `exclusion_migration_replay.py` stays as the readable
record of how the paired comparison was produced and now refuses its
`old` arm loudly rather than silently filing new-semantics numbers under
the old label (`--render-only` still rebuilds the report from the
committed csvs). Stale exclusion-application prose fixed in
`README.md`, `bank.py`, `passive_eval.py`, `perpetua_cases.py`,
`llm_floor.py` and `beliefsim/beliefs.py`. `mypy --strict` is clean on
all 26 touched files; the 92 remaining errors in the package are
pre-existing in three untouched report modules (`household_report.py`,
`household_analysis.py`, `multiseed_report.py`) and predate this work
(96 errors in five files at the base commit).

## Update (2026-09-04: observation-rate sweep — more sensing helps the classical models and cannot help Perpetua)

`baselines.rate_sweep` re-exports every household at 0.5x / 1x / 2x / 4x
of the fleet's passive patrol density (`visits_per_day` 3 / 6 / 12 / 24;
the 1x export is byte-identical to the fleet bank) and re-runs the
household analysis (now parametrised by `--bank-dir`) with LastObs,
Periodic, DaytypeMix, SmoothedRec, the three survival models and the
oracle, 20 homes x seeds {0, 1}, 28 days. A 56-day arm was NOT run:
these programs have no weekly routine (`weekly_blocks` empty, every day
an authored arc event), so extending needs a program transform; owner
deferred. Under `reports/baselines/rate_sweep/`: a full household report
per rate, `summary.md` and `explainer.md` (generated) and `findings.md`
(authored). `--stage explain` builds the glossary, the per-home mix and
per-situation accuracy figures, and a Oaxaca decomposition of the
headline difference with a household bootstrap.

**The result, and a correction.** The first pass claimed "per-case
accuracies do not move with the rate; only the case mix does". The
decomposition refutes it: at 12-24 h the move from 1x to 4x (-0.223) is
-0.231 from accuracy changing WITHIN situations and only +0.009 from the
mix. The corrected mechanism is sharper. Whenever a later visit has found
the last-seen receptacle empty, elimination has ruled out every sensable
receptacle and LastObs answers OUT_OF_HOUSE — in 100% of such questions,
at every rate — and is right exactly as often as the object really is
out: 0.41 / 0.56 / 0.69 at 1x / 2x / 4x. Perpetua has no OUT_OF_HOUSE
edge (unsensable, never sighted, so no edge is ever created) and falls
0.21 / 0.14 / 0.09 in the same situation as it swells to 69% of the
band. So the PerpetuaStar minus LastObs difference at 12-24 h widens:
-0.092, -0.089, -0.137, -0.311, with separating household bootstrap
intervals. At 1-2d and 2d+ the move IS mostly the mix (2d+ at 4x: -0.284
of a -0.246 move), because the in-house share of those bands falls 0.87 /
0.76 / 0.64 / 0.29.

Two situations are genuinely rate-invariant and bracket the model class:
object still at its last-seen spot with no re-check, PerpetuaStar
0.68-0.76 against LastObs's structural 1.00 (the survival prior decays an
edge nobody contradicted); object left, seen gone, came back,
PerpetuaStar 0.35-0.61 against every classical model's structural 0.00.
Learning is not the bottleneck on either count: fallback share never
reaches 0.25 at any rate (day 27: 0.61 / 0.54 / 0.53 / 0.52), edges never
completing two persistence segments 0.48 / 0.42 / 0.41 / 0.39, and
in-house-only accuracy is flat at 0.45-0.58 in every band at every rate.
The blocking gap is the missing absence hypothesis — the paper's
threshold δ on the belief, which our measured absence signal does not
currently support — and that is a model change, so it is a decision.
160 banks, 71 min wall on four 40-worker pools; per-rate figure copies
gitignored.

## Update (2026-09-03: Perpetua and Perpetua* ported as candidates, run on the full 20x5 fleet; the exclusion rule audited)

Two survival-analysis belief models from the Montreal robotics group,
registered as candidates `perpetua`, `perpetua_star`, and the
`perpetua_star` flat-switching-prior ablation (display names Perpetua,
PerpetuaStar, PerpetuaStarFlat), all appended to the bake-off slate. Each
(object, receptacle) pair an object has ever been sighted at is one
binary feature tracked by a mixture of persistence filters (present
until a survival time elapses) and a mixture of emergence filters (absent
until it reappears); the prediction is the normalised vector of per-edge
presence beliefs over the object's support. OUT_OF_HOUSE is never sighted,
so it never enters any support: both models are structurally wrong there
(14-31% of the truth at ages of a day and more).

**Faithfulness.** `beliefs/perpetua_filters.py` is a numpy port of
montrealrobotics/perpetua-code (JAX) with its numerical conventions
mirrored (clip bounds, the `logdiff` floor, the two-level interpolation
of the switching simulation, EM E/M steps for exponential and lognormal
families, AIC model selection). `tests/test_perpetua_filters.py` checks
it against outputs captured from the JAX code on 12 deterministic cases
(`tests/fixtures/perpetua_reference_targets.json`, driver and patched
clone under `third_party/perpetua_reference/`, gitignored): single and
mixture filters, the state machine at num_steps 1 and 10 including a
3000 s forecast tail, and 30-iteration EM traces all agree to float32
precision. Perpetua* (arXiv 2605.00121) has no public code; equations
2-15 are ported from the paper.

**Deviations, each documented in the module docstrings:**

- Perpetua* resets. The paper never says whether the mixtures are ever
  re-initialised; run literally from a fixed origin, hour-scale survival
  priors lose all mass within days and the posterior collapses. Default
  `reset_mode="belief"`: after each observation, when the eq. 13 presence
  belief crosses 0.5 against the current phase, BOTH mixtures restart at
  that time with eq. 18's eps-mixed weights and are seeded with the
  observation (both restart so the eq. 12 evidences cover the same
  window). The first proposal, `model_posterior` (restart the newly
  dominant mixture when the eq. 12 posterior flips), ping-pongs on our
  sparse streams because the model posterior names the story that
  explains the window that just ended, not the phase that begins; it is
  kept as a diagnostic, as is `none` (literal). Every reset is logged.
- Time-of-day switching prior with Laplace pseudo-count 1: without it a
  freshly created edge's prior is exactly 1 (its only sighting created
  it) and the prior alone flips the edge.
- Segments cut at observed flips (no PELT; the stream is noise-free);
  persistence segment = presence run plus the following absence run,
  origin at the head's first observation time.
- EM: deterministic starts (the reference's grid quantiles, a
  data-driven quantile start, and the previous day's fit as a warm start)
  instead of random perturbation restarts; stopping tolerance 1e-4 on the
  float64 log-evidence, the float32 resolution the reference's 1e-6
  effectively is. Edges without new observations since their last fit
  are not refit.
- Exclusions: `_apply_exclusions` is the identity in the Perpetua base
  (negative evidence enters the filters as y=0, so the base rule would
  count it twice); base sighting bookkeeping and the sighting-at-instant
  short circuit stay.

**Hyperparameters** (signed off): P_M = P_F = 0.01, lognormal family
(exponential via config), K in {1, 2, 3} by AIC, delta 0.05/0.95, eps 0.1,
num_steps 10, gamma 0.99, alpha0 0.01 per hour, refit at the first update
after each day boundary, fallback single-component prior (median 12 h)
below 2 completed segments per filter kind.

**Instrumentation.** `BeliefModel.last_prediction_diagnostics()` (None by
default) rides on `ScoredQuestion.diagnostics`; the household analysis
writes `absence_signal.csv.gz` (largest per-edge belief per question,
with where the object really was), `perpetua_resets.csv.gz`,
`perpetua_edges.csv.gz` (completed segments, fitted K, fallback flags per
edge) and `perpetua_fallback.csv.gz` (fallback share per query day);
`household_report.py` renders them in a new section.

**Full run (20 homes x 5 seeds, 11 models + oracle, 100 workers):**
23 min 49 s wall, 31 CPU-hours; the three survival models are 24 of the
~35 CPU-minutes a bank costs. The report gained two per-home figures
(`perpetua_by_home.png`, `perpetua_long_age_delta.png`) with Wilson 95%
bands, per-bin question counts on the ticks, and a MIN_N = 30 rule: no
cell under 30 questions is drawn or quoted (hh_016's "1.000 at 3d+" was 3
questions). Never pool homes; the per-home rows are the result.

**Group-level figures (2026-09-05).** `age_by_group.png` now carries only
the three basic models (MostFreq, Periodic, Perpetua) plus the oracle,
with Wilson bands and per-bin counts. Two figures were added:
`learning_by_group.png` (accuracy by query day, weekend query days
shaded because every bank starts on a Monday) and `learning_vs_age.png`,
which crosses history window (days 3-6, then whole weeks) with a
six-bin age of last sighting, all homes pooled, so learning and
staleness can be read separately. At fixed age, MostFreq and Periodic
are flat across the four weeks; Perpetua drifts down at ages of a day
or more.

**What the survival models do, per home.** At a day and older every
home shows the same shape: LastObs and MostFreq coincide (the exclusion
rule dominates both) and Perpetua* sits above them by 0.05 to 0.30
except in hh_012 and hh_019, where it loses. `perpetua_cases.py`
explains it with a four-case split of each long-age question by (object
MOVED since its last sighting) x (a later visit EXCLUDED the last-seen
receptacle). Fleet totals for orientation, per-home tables in
`perpetua_cases.md`:

    case                      n      LastObs  MostFreq  PerpetuaStar
    stayed, not excluded    5874     1.00     1.00      0.69
    stayed, EXCLUDED       12272     0.00     0.00      0.64
    moved, not excluded     3904     0.00     0.00      0.23
    moved, EXCLUDED        28738     0.42     0.42      0.14

The whole gain is the second row: the object left, a patrol found the
spot empty, the object came back unobserved. The base class's exclusion
is permanent until the next sighting, so no classical model can ever
re-answer that receptacle; the Perpetua models feed the same negative
evidence into their filters and the emergence filter re-admits the
receptacle after the expected absence. hh_016 (single senior) is the
extreme: 100% of its long-age questions have the last-seen receptacle
excluded (a sparse home where the patrol always catches the absence),
93% of them are still in the house, and 35% are "came back" cases, so
LastObs/MostFreq score 0.03 and Perpetua* 0.36. The survival models pay
for it in the other rows: 0.69 where the object simply stayed put, and
at 12-24 h they lose 0.24 on the 46 629 stayed-and-not-excluded
questions (0.76 vs 1.00) because the fallback prior (median 12 h, still
in use for 54% of edge beliefs on day 27) decays the last-seen edge too
fast. 97% of hh_016's long-age predictions used the fallback prior: the
learned mixtures barely act; the structure does the work.

**Audit of the exclusion rule itself, prompted by the above.** The rule
(`BeliefModel._active_exclusions`) drops an exclusion only when a later
positive sighting of that object arrives. At long ages there is by
definition no later sighting, so exclusions accumulate and never age.
Replaying LastObs on all 100 banks with and without the rule (the
counterfactual is simply "answer the last sighting"):

    age of last sighting      n     LastObs now  rule removed   delta   last-seen excluded
    3-6h                   24504      0.767        0.767       +0.000        0.00
    12-24h                 78956      0.603        0.595       +0.008        0.04
    1 day and older        50788      0.353        0.357       -0.004        0.81

So the rule is not buggy and it is not free money: it is worth +0.008 at
12-24 h and -0.004 at a day and older. What it buys is the only route any
model has to OUT_OF_HOUSE, which is unsensable and therefore never
sighted and never excluded — at long ages LastObs answers OUT_OF_HOUSE
41 010 times and is right 12 045 of them, catching 94% of the 12 777 true
out-of-house questions. What it costs is that by then 81% of questions
have their last-seen receptacle ruled out and 24.2% have the object
sitting at a receptacle the rule has ruled out (it left, was seen gone,
and came back unobserved). Elimination has effectively collapsed into
"answer OUT_OF_HOUSE", firing 3.2x more often than the truth warrants.

The real asymmetry is that positive evidence decays in the models that
model decay, while negative evidence never decays and is enforced in the
base class ABOVE every model, so no model can opt out of it — which is
exactly what the Perpetua models had to bypass to get their long-age
gain. An exclusion with an expiry (or a decay to the model's own prior)
would be the principled fix and the cheap comparator at once; it changes
the frozen panel's numbers, so it is the owner's call, not a silent edit.

The obvious cheap comparator this implies -- LastObs or MostFreq with an
exclusion that expires -- is not implemented and not on the slate; it is
a decision for the owner. The absence signal separates a little at long
ages fleet-wide (mean max edge belief 0.51 in-house vs 0.37 out-of-house
at 1-2d for Perpetua*) but is not thresholdable. Frozen-forecast
(D=7, h=1) headline: Perpetua* is best on 4 of 20 homes. 58 new tests
pass; mypy --strict clean on the new and touched code.

## Update (2026-08-27, later: patrol volume reported, routine oracle, recency strata, smoothed recency)

Four additions closing out the classical-baseline side. Three are
evaluation infrastructure reused by everything downstream; the fourth is
one belief model, and it did not win.

**Patrol comparison now reports observation volume.** `build_patrol_section`
attached each schedule's realized `stream_stats` (visits and sightings per
day among them). This was needed because the section claimed to hold
everything but the route fixed while `morning_evening_sweep` and
`stationed_observer` ignore `visits_per_day` and generate their own visit
counts — so route and volume moved together and no difference was
attributable. On hh4 at a nominal 6 visits/day the realized counts are
`random_room_walk` 6.0, `round_robin_patrol` 6.0, `follow_the_person` 9.5,
`stationed_observer` 13.3, `morning_evening_sweep` 14.0 — a 2.3x spread.
The viewer plots mean accuracy against realized visits/day, so
same-x comparisons isolate the route and different-x ones do not.
Plotting rather than subsampling: thinning a full sweep or a stationed
observer destroys the structure those schedules exist to model, so the
compared objects would stop being the named schedules.

**Monte-Carlo routine oracle** (`routine_oracle.py`). The storyfirst
pipeline separates authorship from realization — an LLM writes the story
days and probabilistic movement rules into `program.yaml` once, and a
seeded local simulator turns them into a timeline. All the object-position
randomness (misplace draws, rule destination draws, tidy races, activity
skips, jitter, bout fragmentation) is realization randomness. The oracle
re-realizes the same program at seeds 1..N (seed 0 excluded: it is the
bank's own world) and answers each question with the modal receptacle
across realizations. That is perfect routine knowledge with zero
observations, and it needed no simulator reimplementation. Verified the
seed-0 re-realization reproduces the shipped `hourly.csv` byte-for-byte
and every event field the truth loader reads.

Fleet mean 0.718. Headroom (oracle minus best model) per visits/day:

    1      2      3      4      6      8     12     24
    +0.254 +0.201 +0.164 +0.142 +0.083 +0.052 -0.000 -0.096

The oracle is a diagnostic, not a competitor, and NOT a hard ceiling: it
sees no observations, so a model with a fresh sighting can beat it, which
is what the negative values from 12 visits/day up are. Positive headroom
is residual error explainable by routine knowledge alone; negative
headroom means recency is carrying the load instead. It renders as a
dashed gray reference line, never in the model palette.

**Seed count is 800, set from a measurement.** Eight INDEPENDENT 200-seed
blocks per household put the per-household sd of oracle accuracy at
0.003-0.008 (worst hh7 0.0080, hh2 0.0076). Since sd falls as
1/sqrt(seeds), 800 seeds put every household at sd <= 0.004 — 2 sd of
0.008, inside the 0.02 this fleet treats as noise. Realized disjoint-half
deltas at 800 seeds: worst 0.0105 (hh10), median 0.0031. A realization
costs ~0.02 s, so 800 seeds is ~16 s per household.

Two corrections recorded because both changed conclusions mid-run. (1)
The first stability check compared the full estimate against its own
first half — a subset of itself at half the sample — so it reported the
prefix's noise, not the estimate's. It flagged hh7 as unstable at 50 AND
at 100 seeds when the 50-seed value was the outlier and the 100-seed one
sat within 0.005 of its plateau. The check is now two DISJOINT halves
(`accuracy_halves`, `half_split_delta`), which are independent. (2) A
cumulative accuracy-vs-seed-count curve cannot establish convergence:
successive points share most of their samples, so a monotone run over
several checkpoints is ordinary correlated noise. hh9 and hh10 looked
like they were drifting upward through 400 seeds and were flat by 1600;
hh7 and hh8 then moved instead. Only disjoint blocks answer the question.
A hypothesis that did NOT survive: near-ties in the modal estimator do
not explain which households are noisy (correlation between near-tie
share and sd is -0.06; hh1 has the most near-ties at 8.1% and one of the
smallest spreads). The mechanism is unexplained and left that way.

**Recency stratification in the budget sweep.** `passive_eval`'s existing
bins were reusable as-is, so `belief_trace` imports `PassiveProtocolConfig`
rather than duplicating the binning; the sweep, the bake-off, and any
passive-eval table now stratify time-since-last-sighting identically.
Every cell carries its question count. Pooled over the ten households at
6 visits/day the bins are very uneven — 897 questions in [0h,1h) against
8 539 in [6h,24h) and 590 in [72h,inf) — which is exactly why the counts
travel with the accuracies. The stratification is where the models
actually differ:

    model              [0h,1h)    [1h,6h)   [6h,24h)  [24h,72h)  [72h,inf)
    last_observation     0.940      0.790      0.632      0.284      0.297
    most_frequent        0.915      0.772      0.631      0.272      0.153
    smoothed_recency     0.940      0.790      0.638      0.306      0.214
    n                      897       3427       8539       2747        590

**Smoothed recency** (`beliefs/smoothed_recency.py`, registered
`candidate`). Weight 2^(-elapsed/half_life) on the last-seen receptacle,
the rest on the object's decayed frequency histogram: last-observation
when fresh, most-frequent when stale, a proper distribution throughout so
log loss and calibration are finite. Smoothing half-life 6 h, chosen once
on a three-household dev split (hh1/hh2/hh3, candidates {2, 6, 12, 24, 48}
h) and frozen. One pass, no variants, no per-bank tuning.

The exclusion collapse it was also meant to fix is fixed without touching
the shared rule: `BeliefModel._exclusion_backoff` is a new hook returning
None by default (uniform redistribution, so no existing model changed
behavior), and smoothed recency returns its frequency histogram, so
"not where I last saw it" means "probably at one of its usual spots"
rather than "anywhere in the house".

**It did not beat the naive rows, and the honest sentence is that the
difference is noise.** Fleet mean over ten households, smoothed recency
minus last_observation, is +0.004 to +0.009 at every budget — all under
the 0.02 threshold. On the seven households outside the dev split it is
BELOW last_observation at every budget (0.605 vs 0.613 at 6 visits/day;
0.768 vs 0.783 at 24). It does beat most_frequent by more than noise from
8 visits/day up (+0.028, +0.036, +0.054 at 8/12/24). So it succeeds at
being a proper-distribution comparator nobody can call a strawman, and
fails to be a better predictor than naive recency. Per the scope limit it
was not tuned further; last_observation and most_frequent stay the
comparators.

**Reporting convention** (applies wherever these numbers are used):
last_observation stays in accuracy tables and is excluded from any
calibration, log-loss, confidence, or regret analysis, where a one-hot
belief is meaningless. That exclusion is noted at every site rather than
applied silently.

All ten storyfirst traces regenerated (~2 min each). 144 tests pass
(9 new in `tests/test_baselines_smoothed_recency.py`); mypy --strict
clean; viewer JS syntax-checked.

## Update (2026-08-27: negative evidence flows passively; patrol + budget-sweep viewer tabs)

**Negative evidence, implemented with no new belief code.** Room-visit
banks now write each visit as one ``room_visit`` row whose ``contents``
map EVERY inspected receptacle (empty ones included) to the objects
found there. The loader replays a visit as one ``SenseResult`` per
receptacle — the evidence type the belief base class already consumes
for paid senses — so positive sightings and exclusions arrive through
the existing machinery. ``Episode`` gained ``scripted_evidence`` and a
single ``evidence_stream()`` accessor; the harness, passive evaluation,
belief traces, and off-policy replay all deliver through it, so
positive-only and visit-based banks cannot diverge in delivery.
``scripted_observations`` still exposes the positive half for recency
readouts and the viewer. Tests cover the two payoff cases: a visit
finding a receptacle empty rules it out, and visits covering every
sensable receptacle drive a passive belief to answer OUT_OF_HOUSE —
an answer no positive-only diet could ever reach.

**Negative evidence reorders the models.** On the budget sweep (below),
frequency-style models now benefit most: an excluded receptacle costs a
recency model its whole belief (uniform fallback) but costs a frequency
model only its top choice (mass moves to the next-most-frequent spot).
On hh1 at 24 visits/day: most_frequent/hierarchy_backoff 0.860 vs
last_observation 0.748.

**Viewer: two new tabs** on the belief-vs-truth page, fed by two new
sections `belief_trace.py` computes when given ``--timeline/--spec``:
``active (patrols)`` — every patrol schedule at one shared visit budget,
with the visit timeline and house-wide accuracy series per panel model —
and ``budget sweep`` — question-set accuracy per registered model per
observation budget (1..24 room visits/day), the
floor/separation/saturation picture. Traces regenerated for all ten
storyfirst households (~45 s, 300-600 KB each).

**Candidate slate verdict on this setup** (mean question-set accuracy
over the ten households, negative evidence on): last_observation and
hierarchy_backoff are effectively tied at every budget (hierarchy
+0.005 at 6 visits/day, -0.019 at 24; it wins at most 3/10 households);
every other candidate trails at every budget, timetable badly (-0.07 to
-0.16). markov1 remains indistinguishable-or-worse vs most_frequent.
The pragmatic roster for now: last_observation as the common-sense
baseline, most_frequent as the frequency representative — the other
candidates stay registered but out of headline tables until some
household regime rewards them.

Fleet re-exported with the new rows (flags shift slightly: hh2 now also
flags discriminative at 6 visits/day; hh9 no longer flags not_trivial).
135 tests pass; mypy --strict clean.


## Update (2026-08-26, later: nothing disqualifies — the healthcheck is a diagnostic report; fleet re-run on room visits)

Direction set explicitly by the owner: dataset acceptance happens once,
at generation time (`src/revamp_v2/validate.py`); anything the
instrument computes afterwards is about the EXPERIMENT built on the
dataset (observation stream, question sample, budget), which is iterated
on freely. So the healthcheck no longer gates anything. All six checks
are now DIAGNOSTICS — measured, compared to a reference threshold, and
reported as flags for a human to look at. The one exception is
`solvable`, kept as a hard bug check (unlimited-budget search failing to
find a queried object means the bank or harness is broken, and every
other number in the report is suspect); the CLI exits nonzero only on
it. Gone with the gating: the `overall PASS/FAIL` verdict, the
dirty-git-tree refusal (tree state is still recorded in provenance), the
two-tier advisory scheme from earlier today, and the bake-off's
passing-banks filter (it now runs every completed bank). The earlier
note that the healthcheck "must refuse room-visit banks until its gates
are re-derived" is withdrawn — it came from a draft integration note and
was never implemented; nothing refuses any observation model.
`HealthcheckReport` now carries `diagnostics` / `flags` / `solvable_ok`;
`fleet_summary` rows carry the same.

The shared fleet config now uses the room-visit observation model
(round-robin patrol, 6 visits/day — roughly 0.7-1.2 sightings per object
per day across the set). Fleet re-run on the ten storyfirst households
under the new semantics: discriminative is flagged NOWHERE (it was
flagged on all ten under the glimpse stream); `not_impossible` is
flagged everywhere (24 receptacle-senses/day next to a room-bundled
ambient stream buys little — the sense budget's granularity is now the
odd one out, a known open question for the active-side work);
`not_trivial` flags the five stickiest households, as the stationarity
diagnostic predicts.

With adequate observations the passive models finally separate for real:
against the best-possible "always guess each object's usual spot"
strategy (computed from ground truth), most_frequent lands about +0.06
above it on average — it IS that strategy, learned from observations —
while last_observation adds another +0.03 on top by tracking recent
moves (household means 0.567 usual-spot / 0.622 most_frequent / 0.655
last_observation / 0.565 timetable at 8 visits/day).


## Update (2026-08-26: room-visit observations; two gates demoted to advisory)

**Two gates no longer disqualify** (`ADVISORY_GATES` in healthcheck.py;
both still measured and printed). `stationarity` averages each object's
dwell-weighted modal share over ALL objects, so a permanently-parked
object contributes exactly 1.0 and the statistic charges a household for
owning realistic furniture — the worst storyfirst household still has 18
of 32 objects below 0.7 modal share, so it cannot detect degeneracy on
its own. `not_impossible` presumes the configured sense budget is near
the ceiling of what sensing can buy, which 24/day over 22-35 receptacles
is not, and it rejects precisely the banks where sensing is hard — the
interesting ones for an active-sensing study.

**The observation model is now room visits.** New
`baselines/room_observations.py` replaces the random-glimpse process (one
random object at one random instant, no spatial structure) with a room
visit: at time t the contents of every receptacle in one room are
revealed at once. Five deterministic patrol schedules —
`morning_evening_sweep`, `round_robin_patrol`, `random_room_walk`,
`stationed_observer`, `follow_the_person` — after the STRANDS
long-term-autonomy line (Santos et al. RA-L 2016; Krajnik et al. ECMR
2015); adaptive/information-driven scheduling is deliberately absent
because in this codebase that is an ACTIVE policy, not a scripted stream.
`export_bank` takes `--observation-model room_visit --patrol P
--visits-per-day N`; the header records all three. Only the POSITIVE half
is written so far, as ordinary `observation` rows, so every belief model
and the harness consume it unchanged.

The efficiency is the point: **8 visits/day yields 0.87-1.53 sightings
per object per day, where 10 glimpses/day yielded 0.15-0.32** — fewer
events, ~10x the evidence, because one visit reports a whole room. Median
gap between sightings of one object drops from 2-3 DAYS to 6-16 h.
Passive panel spread on the storyfirst set goes from **0/10 banks
clearing the discriminative gate to 10/10**.

**The binding constraint moved, and stationarity turns out to predict
it.** With adequate evidence, passive accuracy rises until `not_trivial`
(<= 0.65) binds: at 6 visits/day 10/10 clear discriminative but 5/10
exceed the passive ceiling. Which 5 is almost perfectly predicted by
stationarity (Spearman rho = 0.96, Pearson r = 0.94 against passive
accuracy at 6 visits/day: hh7 0.668 -> 0.756, hh9 0.653 -> 0.686, hh8
0.623 -> 0.694, hh1 0.622 -> 0.679, hh10 0.582 -> 0.671). So the
stationarity statistic was measuring something real; its error was the
consequence it drew. A sticky world does not need disqualifying on its
own arithmetic — once the observation stream is adequate, `not_trivial`
catches the same banks directly and for the right reason.

No single global visit budget satisfies both gates on all ten households
(hh7 exceeds the passive ceiling by 3 visits/day; hh4 and hh6 need 6 to
open any spread), and per-bank tuning stays prohibited — so the choice of
budget is a deliberate global trade, not a fit.

Three bugs in the proposed module were fixed rather than reproduced, each
noted at its site: `follow_the_person` merged every resident's blocks and
picked whichever sorted first, making the followed person depend on file
order (now follows one named resident); a person-check was dropped
whenever nothing was carried, conflating "the person is out, cannot be
inspected" with "the person is home carrying nothing", which is valid
negative evidence (now uses away intervals); and `stationed_observer`
defaulted its home base to the spec's first room, typically a bedroom
(now the busiest room by resident presence). `draw_time` was made public
in export_bank for reuse. 11 new tests
(`tests/test_baselines_room_observations.py`) cover schedule determinism
and seed sensitivity, the round-robin revisit bound, that realization
never invents evidence, and that a visit reports EVERY object in the
room. 132 tests pass; mypy --strict clean.

NOT yet done, in order: the `room_visit` row kind and header `rooms`
mapping (the negative-evidence half — a bank schema change, with the
healthcheck refusing room-visit banks until its gates are re-derived);
belief-side consumption of that negative evidence; and the whole active
policy roster.

## Update (2026-08-25, later: sighting-scale experiment + viewer belief traces)

**The Cause-1 diagnosis was tested and holds, with a corrected dosage.**
`export_bank.export` gained two size-scaling rules —
`sightings_per_object_day` and `budget_per_sensable_receptacle` — which
replace the absolute per-day settings with rules proportional to the
household (fleet config passes them through). A rate probe over four
banks shows belief spread rising monotonically with evidence
(hh4: 0.011 -> 0.034 -> 0.070 -> 0.165 at 0.5/1/2/4 per object per day),
so the panel beliefs were being STARVED into agreement, not inherently
alike. Full fleet at 1.0/object/day + 1.6 senses/sensable receptacle:
**discriminative failures 11/12 -> 1/12, passing banks 1 -> 2**
(revamp_v1 hh1 restored, storyfirst hh10 newly passing). Two corrections
to the earlier write-up, both recorded in
`reports/baselines/fleet/sighting_scale_experiment.md`: the originally
proposed 0.5/object/day is BELOW the gate on every probed bank (and
regresses hh1 from PASS to FAIL — the 0.51 arithmetic ignored the ~15%
of sightings dropped as unobservable while an object is out), and the
fix is not free — more evidence raises passive accuracy, which pushes
three already-stationary banks (revamp_v1 hh3, hh7, hh9) past the
`not_trivial` ceiling and raises the bar `not_impossible` must clear
(10/12 still fail it). Stationarity is upstream of both survivors, so
the recommended order is: repair the dead-inventory content first, then
adopt 1.0/object/day, then re-tune budget. `configs/fleet.yaml` is
deliberately NOT changed yet — switching the shared config rewrites what
every recorded gate reading means, and the content fixes will move these
numbers again; adopting it is then a two-line edit.

**Belief traces for the viewer.** New `baselines/belief_trace.py` writes
`belief_trace.json` beside a household's `trace.json`: per belief model
and per object, run-length-encoded segments of the model's argmax under
the PASSIVE diet (tour + scripted sightings, no sensing), plus the
bank's own truth segments. Predictions are sampled on a 15-minute grid
because a belief's argmax moves with time even without new evidence
(decayed counts re-weight, timetable bins roll over, hazards decay);
RLE keeps a 7-model, 53-object household at ~270 KB. Built for all 12
fleet households (~2 s each). `visualization/serve.py` DISCOVERS these
files and publishes them in `traces.json`, which is what brings the
belief-vs-truth page back — it had gone dark because its `runs` entries
pointed at archived run logs from the retired dataset. The page
(`viewer/beliefs.html`) is rebuilt around three tabs: the focus object
on the map (belief ring vs truth disc, joined when they disagree, now
resolvable at ANY slider moment rather than only at question times), a
table of every object right now sorted wrong-first, and the same instant
scored across all seven models. Ten tests
(`tests/test_baselines_belief_trace.py`) assert the traced argmax equals
the live model's prediction at every grid point for every model, that
truth matches the bank exactly, byte-determinism, and refusal of
multi-episode banks; the page's own segment-lookup logic was exercised
against real data under node (13 260 lookups, 0 outside their segment).

Follow-up in the same session, from viewer feedback: the trace now also
carries the EVIDENCE (`sightings`: every observation the passive diet
delivered, per object), which the page reads for a "last seen — where,
how long ago, has it moved since" row, a dashed marker on the map at the
last-seen receptacle, and gold ticks on the strip. This closed a real
gap — the panel had a last-sighting row wired to a field the generator
never emitted, so it always read "–". Rounding matters here and is
tested: sighting seconds round UP to the minute, because a belief
sampled at grid minute m has consumed exactly the observations with
t <= m*60, and flooring advertised a sighting one grid step before the
models could act on it (4 disagreements per household between
LastObservation's belief and its own last-seen row; now 270 144/270 144
agree across hh1/hh4/hh9). The synthetic fixtures all sight on whole
minutes and so cannot see the rounding direction — a dedicated test
pins it with a 12 345 s sighting. The strip also gained a caption: it
plots two unrelated series (share-of-objects-correct, and this object's
sightings) and was unreadable without one.

Second round of viewer feedback found the real layout bug: ALL of the
tab/sheet CSS had been written to `visualization/style.css`, a file no
page loads (the pages link `viewer/style.css`, and the short-URL route
injects a `<base>` to the same place) — so the table views rendered as
unstyled always-visible blocks that flowed over the timeline slider and
could not be dismissed. The styles now live in `viewer/style.css` (the
stray file is deleted) with the sheet inset inside the map area on all
four sides, where it structurally cannot reach the footer's slider.
Dismissal has three paths — a ✕ button in the sheet, Esc, and clicking
the open tab again toggles it closed — and the tabs are renamed
("◀ map" / "all objects now" / "model comparison") with title tooltips
saying what each shows.

## Update (2026-08-25, fleet health run + horizon-controlled passive protocol + candidate bake-off)

Three additions, all passive-side; the frozen instrument panel, gate
thresholds, and 24 h half-life are untouched.

**Fleet (Task 1).** New `python -m baselines.cli fleet`: exports every
realized household under one shared config
(`configs/fleet.yaml` = the hh1 gate-passing recipe: 90 q/day from day
3, 10 sightings/day, budget 24, uniform, tour on, seed 0) and runs
healthcheck + bankstats on each. Results
(`reports/baselines/fleet/`): **12 banks, 1 passes all six gates**
(revamp_v1 hh1 — the calibration bank). Both precedent failure classes
were checked explicitly and are clean (zero duplicate YAML mapping keys
fleet-wide; 0.000 of question times inside whole-household sleep on
every bank). The three real causes, diagnosed in `fleet/failures.md`:
(1) discriminative collapse on 11/12 banks — the fixed 10 sightings/day
starves per-object evidence on 26-53-object inventories (spread tracks
sightings/object/day; hh1 passes at 0.51, everything under ~0.3
collapses) — an instrument-scale mismatch needing one deliberate global
config revision (e.g. sightings ~ 0.5 x n_objects), not per-bank
tuning; (2) not_impossible on 10/12 — budget 24 vs 22-35 sensable
receptacles and 100-210 moves/day, plus 11-19% OUT_OF_HOUSE questions
that cost a full sweep to prove; (3) stationarity on 6/12 — inventory
objects whose movement rules never fire (laundry baskets, vacuum
cleaners, yoga mats, watering cans at modal share ~1.0), flagged as
generator CONTENT per bank in failures.md; no household YAML edited.
No exporter/simulator defect surfaced (solvable 1.000 everywhere).

**Horizon-controlled passive protocol (Task 2).**
`baselines/passive_eval.py`: per checkpoint day D the belief consumes
tour + sightings with t < D*86 400 only, then answers bank questions at
horizons h past D, scored per (D, h) cell (never pooled across h), with
per-question time-since-last-sighting recency bins, top-1 AND epsilon-
floored natural-log loss, household-unit aggregation (unweighted mean,
seeded bootstrap over households, sample sizes everywhere). The old
per-day curve is retained and now labeled DESCRIPTIVE ONLY in
`metrics.plot_accuracy_by_day` and the report header.

**Candidates + bake-off (Task 3).** New registry
(`baselines/registry.py`) tags every belief `frozen|candidate`;
`cli.build_belief` delegates to it and the healthcheck asserts its panel
is all-frozen (a candidate in the panel raises — tested). Four
candidates under `beliefs/`: `markov1`, `periodic_persistence` (hazard
estimator unit-tested on hand-computed censored dwells),
`daytype_mixture` (seeded k-means day-types + naive-Bayes type
inference + per-type timetables), `hierarchy_backoff` (object -> class
-> global). `python -m baselines.bakeoff` runs panel + candidates under
the Task-2 protocol on gate-passing banks
(`reports/baselines/bakeoff/`; an `exploratory_all_banks/` run covers
all 12 since only one bank passes). Findings (`recommendation.md`):
promote periodic_persistence (strongest classical per-object
comparator) and hierarchy_backoff (wins log-loss on 10/12 households —
top-1 and calibration genuinely dissociate); keep daytype_mixture as a
regime probe only — **it separates on no bank** (its wins are within
noise), while it is perfect on the synthetic two-regime fixture, so the
finding is that current banks do not reward cross-object regime
inference and generation must couple routines before LLM comparisons
are worth running; drop markov1 (indistinguishable from most_frequent
at realistic sighting rates).

**Tests (Task 4).** 21 new tests (111 total, all passing; mypy --strict
clean): hazard hand-computations, markov1 row arithmetic, backoff
pooling, registry tags, healthcheck panel refusal, the three analytic
fixture banks (strict-periodic -> timetable & periodic_persistence 1.0
at h <= 1; two-regime -> daytype 1.0 vs frequency 0.0; fast churn ->
every model within 0.2 of the frequency floor in the stalest bin), the
poisoned post-checkpoint sighting barrier (whole scored output
byte-equal), and bake-off JSON byte-determinism across runs.

Deviations / judgment calls this round:

1. *Fleet roots*: the brief's `profiles/revamp_v1/*/hh*` glob predates
   the dataset reorganization; only hh1/hh3 are realized there. The
   fleet default scans revamp_v1 AND `profiles/revamp_v2/storyfirst`
   (the current 10-household set); `--roots` overrides.
2. *Belief base hook*: cross-object candidates needed the shared
   evidence store, so `BeliefModel` gained an overridable
   `_predict_for_object` (default = old behavior); exclusions,
   renormalization, and the at-instant override remain base-only.
   `_predict_from_history` is no longer abstract (cross-object models
   never reach it).
3. *Log-loss floor*: the brief says "the belief's configured floor",
   but the panel runs exclusion_floor = 0 (hard exclusions + one-hot
   recency), where one confident miss makes the mean infinite. The
   protocol floors every model at the same configured epsilon
   (default 1e-3) instead — same floor for every model, so the
   comparison stays fair.
4. *daytype_mixture type inference* adds a day-of-week term to the
   brief's "sightings seen so far today" naive Bayes: under the frozen
   checkpoint there are never same-day sightings, so day-of-week is
   the regime evidence the model always has.
5. *Horizon cells are bins*: questions come from the bank, so each is
   assigned the smallest configured h covering its lag past D (0.25 ->
   (0, 6 h], 1 -> (6 h, 1 d], ...), rather than being generated at
   exact horizons.
6. *Bake-off household unit is the bank* (filename-stem label):
   household_ids collide across profile sets (both hh1s are
   `hh_001`).
7. *hierarchy_backoff global fix* (recorded per the "clearly broken
   default" rule): backoff WEIGHTS now use raw sighting counts, not
   24 h-decayed counts — decay-gated weights abandoned old-but-
   plentiful own evidence for the global histogram (stale-bin accuracy
   0.105 -> 0.432). Level distributions still use the frozen decay.
8. *Exploratory bake-off*: only one bank passes gates, so the official
   run has n_households = 1; a clearly-labeled
   `exploratory_all_banks/` run over all 12 provides the
   multi-resident evidence the daytype question needs. Official
   conclusions cite the official run; the daytype non-separation holds
   in both.
9. *Dirty-tree runs*: fleet/bake-off reports were produced from the
   working tree of this change; healthchecks record gates_pass with
   `overall_pass` correctly REFUSED-dirty. Committing (owner's call)
   and re-running `cli fleet` + `bakeoff` reproduces them with clean
   provenance.

## Update (2026-08-11, dated-activity pipeline: hh1 is the new headline bank)

The household authoring chain is now three reviewable stages per
household folder (profiles/revamp_v1/claude-fable-5/hh1..hh10):
persona.yaml -> detailed_activities.yaml (a DATED 21-day calendar with a
story arc — a covered double, a dentist-split sleep, a manic reset that
happens/skips/gets abandoned) -> object_motions.yaml (per-activity object
rules citing charter habits). simulate_activities.py realizes the
calendar into the standard timeline artifacts; export_bank and the whole
instrument run unchanged. The old weekly-pattern schedule specs,
simulate_schedule.py timelines, and the 28d banks/reports are retired
(git history keeps them).

Two exporter-level findings from bringing hh1 through the gates:

- **Duplicate YAML keys silently drop rules**: two `after` rules for one
  (activity, object) key left the cereal bowl stranded at modal share
  0.911. The simulator now rejects duplicate mapping keys loudly; each
  dish's put-away lives on an activity that cannot also dirty it.
  Stationarity 0.616 FAIL -> 0.573 PASS from this alone.
- **The fixed 08:00-22:00 question window was not household-agnostic**:
  for a night-shifter it is mostly blackout sleep, so half the questions
  probed a frozen world — inflating passive memory (0.651), collapsing
  belief spread (0.023), and starving not_impossible. Questions and
  sightings now draw from the household's own awake time
  (non-sleep resident blocks): query-time modal share 0.601 -> 0.525,
  NeverSense 0.651 -> 0.580, spread 0.023 -> 0.052. Budget 24/day chosen
  from a {16, 24} probe (16 clears not_impossible by only 0.003).

hh1 21-day bank: all six gates PASS from a clean tree (stationarity
0.573, solvable 1.000, not_trivial 0.580, not_impossible 0.754 vs
0.730, discriminative 0.052, powered 1620). Grid orders cleanly (search
> patrol > passive; recency > decayed-frequency > decayed-timetable).
Sweep re-targeted to the hh1 pipeline with ramp {0, 1, 4, 24}.


## Update (2026-08-11, decayed frequency beliefs + review-flag resolutions)

**Count decay (the fairness fix).** MostFrequentLocation and
TimetableLookup take an optional `half_life_h`: sighting counts decay as
2^(-age/half_life) at prediction time. An infinite-memory histogram is a
known-broken estimator in a drifting world; the healthcheck panel, sweep,
and headline grid now run the honest-strong versions at a **frozen 24 h
half-life** — the domain's natural cycle, chosen a priori. Tuning the
half-life per bank is instrument-gaming and invalidates cross-bank gate
comparisons (12 h would score higher here and collapse the discriminative
spread to the gate edge: fair estimators converge toward recency as the
half-life shrinks — freq@12h is 0.628 vs last_observation's 0.630).
Measured decayed-vs-undecayed gap on the 28-day bank — itself the drift
measurement: most_frequent +0.040 (0.585 -> 0.625), timetable +0.027
(0.569 -> 0.596). Panel readings: 0.630 / 0.625 / 0.596, spread 0.034
(discriminative passes, thinly; undecayed spread 0.061 was partly the
naive estimator's handicap). The gate-pass fixture was re-tuned for the
stronger instrument (question mix shifted from the timetable-perfect
periodic pair toward the drifters) and passes all six gates again.
Incidental fix surfaced by decayed weights: exclusion redistribution now
renormalizes exactly (float error could push a lone survivor a few ulp
past probability 1.0, which the strict Answer contract rejects).

**Review flags resolved with receipts:**

1. *Solvability on the repaired bank*: verified everywhere it matters —
   the clean-tree healthchecks ran SequentialSearch@unlimited = 1.0000
   for all three beliefs on the headline bank, and the same holds on the
   sweep's blind no-tour bank (task 1.0000 x3; full-state at unlimited
   0.959/0.858/0.848). Multi-stage journeys and person-coupled absences
   did not break findability: OUT_OF_HOUSE answers are proven by
   elimination (single unsensable receptacle — keep it single).
2. *Day 22*: intended dynamics, not an artifact. Day 20 (Sunday) rolled
   every probabilistic block cold — tidy, wash, outing all skipped
   (8 events vs ~21 typical) — displacement compounded, Monday's 4-item
   tidy barely dented it, and by Tuesday 35/90 question answers sat on
   coffee_table/couch: query-time modal share collapsed to 0.34 (vs
   0.5-0.7 neighbors). Compounding neglect is the mechanism the
   persistence repair exists to create; agents that sense recently
   handle it best (budget 16 dips least).
3. *FixedSchedule dropped from the sweep*: its 6 h/4-stop rotation
   spends at most 4 senses/day, so budgets >= 4 produced byte-identical
   columns. The policy class remains in the roster and grid.
4. *The ~0.77 ceiling at budget 16 is churn, not unfindability* (see 1);
   the missing points are the world outrunning finite sensing, which is
   the task. Bank-intrinsic stats on the repaired bank: dwell-weighted
   modal share 0.571 (was 0.701 pre-repair; the 0.75 figure was the
   query-time share), displaced 43% of the time, median stint 12.1 h.


## Update (2026-08-11, unsensable OUT_OF_HOUSE)

Reverses the earlier "robot can sense OUT_OF_HOUSE" placeholder: banks
may now declare `unsensable_receptacles` (header field; loader, Episode,
EpisodeContext.sensable_receptacle_ids). They stay legal ANSWERS but a
Sense targeting one is a policy contract violation and the harness
raises loudly. SequentialSearch sweeps sensable receptacles only; an
unsensable location is reached by ELIMINATION — sweep everything, miss
everywhere, and the exclusion redistribution concentrates the remaining
mass on it. With exactly ONE unsensable receptacle this is exact, so
solvable stays 1.0 (verified: 1.0000 on the 28-day bank); keep it at
one unless the invariant is deliberately renegotiated.

Consequences implemented with it:

- The exporter projects person-carried objects time-dependently: while
  the carrier is away (residents.jsonl ELSEWHERE blocks), person:X ->
  OUT_OF_HOUSE, not ON_PERSON — the phone in her pocket at work is out
  of the house. ON_PERSON stays sensable (looking at what a HOME
  resident carries), and sensing it while she is away leaks nothing
  because nothing is ON_PERSON then.
- Neither the tour nor drive-by sightings ever report an object whose
  true location is unsensable (you cannot see what is not there);
  dropped sightings are counted and logged.
- The OUT_OF_HOUSE full-contents information leak is closed: one sense
  used to reveal every absent object at once.

Instrument on the re-exported 28-day bank: unchanged NeverSense floors
(0.630/0.585/0.569), stationarity 0.571, search@16 0.821 (up from
0.811 — the leak was not actually helping the searcher), all six gates
PASS. At real budgets an out-of-house answer now costs a full sensable
sweep (15 senses) or a guess — "guess it and hope" is literal.


## Update (2026-08-11, latest): sweep ramp recalibrated; all-excluded warning deduped

- The blind-start sweep's budget ramp is now {0, 1, 4, 16}: full-contents
  senses are so informative (~2-4 sightings each; OUT_OF_HOUSE aggregates
  every absent carried item) that 16/day assembles a home-base map in ~2
  days — the visible learning arc lives at 1-4 senses/day (budget 1 is
  still climbing at day 27). Unlimited dropped from the ramp as a known
  flat reference (task pinned at 1.0 by the invariant; healthcheck
  documents it). Day-to-day wiggle at fixed budget is ~60% shared world
  difficulty (cross-belief day correlation 0.54-0.62; sd 0.114 vs
  binomial 0.044 at n=90), not sampling noise.
- Timetable's flat curve is a measurement, not a bug: search-generated
  evidence gives each (object, hour-bin) only ~2-4 observations a month,
  so it runs its most-frequent fallback almost always (mean daily gap to
  most_frequent: 0.065), and the world's strongest periodicity — the
  22:25-07:05 shift absences — lies almost entirely OUTSIDE the
  08:00-22:00 question window. Time-conditioning has little purchase on
  what the bank asks; noted for the QA-design discussion.
- The "every receptacle excluded" warning (the brief-mandated signal that
  stale negative evidence covered all receptacles and was ignored) now
  fires once per (object, episode); repeats log at DEBUG. It stays a
  warning: on healthy runs it is rare, and a run that triggers it
  constantly is telling you searches exhaust the house without finding
  the object.

## Update (2026-08-11, later): displacement persistence + scale — first passing bank

Steps 2-3 of the agreed sequence, iterated against `bankstats` exactly as
intended: dwell-weighted modal share 0.701 -> 0.639 (sparse tidy + dish
stages + outings) -> 0.615 (statics softened, errands) -> **0.571 PASS**
(phone set-down misplacement, keys/wallet arrival drift). The result is
`banks/baselines/hh_001_28d_uniform.jsonl` (28 days, 90 questions/day =
2 250, 10 sightings/day, budget 16/day) — the first bank expected to pass
all six health gates.

Generator changes (simulator + hh_001 schedule spec):

- `simulate_schedule.py` blocks may carry `p:` — the block fires each
  listed day only with that probability (seeded). Existing specs are
  bit-identical without it.
- Tidying is now unreliable and partial: planned Mo/We/Fr/Su only, skipped
  outright 15% of those (block p 0.85), each item handled w.p. 0.45, and
  dishes are OUT of tidy scope — a dirty plate is never teleported clean
  into the cupboard.
- Multi-stage dish journey with dwell per stage: use -> sink (hours-days)
  -> wash night (Tu/Th/Su, p 0.75) -> drying rack (overnight+) -> put-away
  on a later evening wake (p 0.55/evening).
- Weekend outings that are fun, not work: Sa 19:00-23:30 (p 0.55) and the
  odd Su evening (p 0.25), taking keys/wallet/jacket; plus Tu/Th errand
  runs (p 0.4). Spec comments record the multi-resident convention: who
  leaves depends on household_type (family = parent+kids subsets,
  roommates = independent per-resident outing blocks).
- Longer-lived displacement everywhere: book home-base drift (bedtime
  retrieval p 0.75, some evenings it migrates to the couch), phone set
  down astray on 40% of days (retrieved on evening wake), umbrella joins
  35% of commutes ("rain nights" — the stand-in for a weather model),
  charger makes couch-side charging trips, blanket homing weakened.
  `bowl_1` and `medication_bottle_1` remain the only statics.

Exporter: uniform mode now draws objects WITHOUT replacement from a
per-day shuffled pool — repeats capped at ceil(questions/objects) (= 6
here), killing the single-object day lotteries diagnosed earlier. The
naturalistic mode is unchanged and stays the robustness condition;
uniform is the headline per the standing decision.

Instrument readings on the new bank: NeverSense last_observation 0.630 >
most_frequent 0.585 > timetable 0.569 (spread 0.061 — discriminative
finally passes, and recency winning is what a persistence world SHOULD
reward); SequentialSearch@16 with last_observation 0.811; grid ordering
is clean (search > fixed patrol > never within every belief). Budget 16
chosen from a {8, 12, 16} probe: 8 fails not_impossible, 12 is marginal
(+0.009), 16 comfortable (+0.031). Sighting rate 10/day chosen from a
{6, 10, 16} probe: 6 leaves the spread at 0.034 (thin), 16 pushes
last_observation to 0.669 past the not_trivial ceiling.

Standing decisions this round: OUT_OF_HOUSE stays a sensable receptacle
(explicitly confirmed "for now — may change"); start-weekday staggering
across households is DEFERRED until multi-household generation (it needs
a bank-header start_weekday field and a weekday-aware timetable
convention — noted so the schema change is deliberate, not accidental).


## Update (2026-08-11): bank-intrinsic stats + stationarity gate

Diagnosis that motivated it (sweep on the hh_001 no-tour bank): the
world's dwell-weighted modal share is **0.701** (0.750 at query times) —
a model knowing nothing but home bases is right ~3/4 of the time at a
random moment, which is why most_frequent's full-state accuracy catches
its (low) ceiling within days. Day-to-day wiggles (the day-6 spike /
day-13 dip, both Sundays) are quiet-weekend dynamics x uniform-draw
repeat concentration at n=28/day, not schedule events.

- New `python -m baselines.cli bankstats BANK` — ground-truth-only stats
  (modal share time-weighted and at query times, moves/day, displacement
  stint median/p90, displaced-time share, worst per-day repeat draw) and
  a **stationarity** gate: dwell-weighted modal share <= 0.60 (config
  `stationarity_max_modal_share`). Runs in < 1 s with no agents: the
  generation workstream's fast loop. The same stats + gate are embedded
  in the healthcheck (now six gates), so the full instrument enforces it.
- Current readings: hh_001 banks 0.701 FAIL; synthetic fixture 0.708
  (hand-derived (1 + 0.625 + 0.5)/3); gate-pass fixture 0.452 PASS;
  static fixture 1.000 FAIL.
- **Standing schema decision for the persistence work**: the exporter's
  `OUT_OF_HOUSE` / `ON_PERSON` pseudo-receptacles remain first-class
  answer categories (predictable and sensable), so an object is always
  in *some* receptacle and the `solvable` gate stays meaningful under
  longer displacements and person-coupled absences. Any new dynamics
  must still re-run `solvable` before results are trusted.
- Agreed sequence for the workstream (this update is step 1):
  (2) generator changes for displacement *persistence* — unreliable /
  partial tidying, multi-stage journeys with dwell per stage, overnight
  and multi-day displacements, person-coupled absences — iterated
  against `bankstats`; (3) scale: ~75-100 questions/day, 28 days,
  staggered start weekdays across households, and a per-object repeat
  cap (sample without replacement) in the uniform draw; (4) full panel;
  only then mass generation. Uniform query times stay the headline
  condition; naturalistic remains the robustness stress test.

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
44-question pilot bank: powered FAILS (44 < 300), discriminative FAILS
(all three NeverSense accuracies 0.545, spread 0.000), not_impossible
FAILS (search@2 0.614 < 0.545 + 0.15); solvable and not_trivial pass.
That failure is the healthcheck doing its job on a bank we already knew
was too small, not a defect to fix here. Reports for the two 14-day
banks live in `reports/baselines/healthcheck_hh_001_{uniform,
naturalistic}/`: both PASS solvable and powered and FAIL discriminative
(spreads 0.000 / 0.003) and not_impossible at budget 2; the uniform
bank also fails not_trivial (NeverSense 0.724). The 14-day banks fare better on scale but
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
