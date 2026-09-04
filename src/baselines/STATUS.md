# STATUS — basic baselines for the sense-or-answer study

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
