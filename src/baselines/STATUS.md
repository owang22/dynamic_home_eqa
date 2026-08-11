# STATUS — basic baselines for the sense-or-answer study

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
