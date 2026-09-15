# Phase 3 run notes — hypothesis tree (2026-09-14)

Household hh_001, timeline seed 0, bank seed 0 (`banks/baselines/tour_start_day0/tl0`),
re-exported today. Model Qwen3.8-27B served locally (prefix caching on). Previous run
(Phase 2 arms, old bank header) moved to `../../archive/phase2_2026-09-14/`.

## Bugs landed first

- **ON_PERSON is unsensable** beside OUT_OF_HOUSE (`export_bank.UNSENSABLE`). The person
  pseudo-room is gone from `RoomMap.from_spec` and from the follow-person schedule; the
  bank header no longer maps ON_PERSON to a room, so no policy can target it. Tour rows and
  drive-by sightings at ON_PERSON are dropped like OUT_OF_HOUSE ones. Effect on the banks:
  hh_001 — header only (round-robin patrol never visited the pseudo-room; the tour saw
  nothing on a person); hh_002 — 3 tour rows at ON_PERSON dropped. Question lists are
  byte-identical, so the old passive numbers remain comparable; active arms differ because
  the pseudo-room is no longer a look target.
- Both away tokens are now listed in every receptacle table (flat, graph, tree, log
  reader) with the two mandated sentences and nothing else about them.
- **Scoring**: exact match (ON_PERSON ≠ OUT_OF_HOUSE) is the reported number; the merged
  number follows in brackets in every table. `passive_eval.AWAY_EQUIVALENCE` docstring
  corrected: merging existed to stop tie-break artefacts between two statistical models,
  but it marked "gone" correct when the resident was in the house.
- Routine posterior active parameters re-selected on the re-exported hh_002 under exact
  log-loss: eps 0.7 / half-life 6 h (unchanged from the merged selection).
- "late-discovered" renamed **tour-absent** everywhere (`tour_absent_objects`,
  per-question `tour_absent`); analysis reads the old keys too for archived runs.
- Deleted dead code found on the way: `_first_sighting_day` (runner), `_nobody_home`
  (room observations).

## Error-catalogue checks (answers)

- Negations / forbidden words: tree prompts grep clean (test 11) except the mandated
  sentence "OUT_OF_HOUSE means the object is not in the house", exempted explicitly, and
  "carrying" in the mandated ON_PERSON sentence (`carry` is checked as a whole word).
- Belief side reads Observation / SenseResult only (test 10: static grep for `episode.`
  and `truth` over the tree modules, plus a check resolved from a SenseResult alone).
- Ground truth never reaches a prompt: tables come from `known_objects`; the tree report
  is report-side.
- Untested ≠ disconfirmed: a check with no look in its window prints "check untested so
  far"; resolved ones print "came true k/n times".
- Identical edits across nodes cannot happen: there is no edit; a child is one node.
- Unresolvable checks: `check_history` per node comes from `check_resolutions` over the
  look log (a look elsewhere that finds the target counts as empty at `at`).
- Bucket: the prompt shows only keys at the repeat threshold.
- CHANCE_PRIOR_STRENGTH / start-hour prior decay: **not changed**. The rest prior decays
  because a wrong rest competes with a prior-free statistical particle on the same
  clock; a chance prior (2 pseudo-counts) is already outvoted by two sightings and the
  start-hour prior (sd 1.5 h) is a location, not a count. Left as is; revisit only if the
  rule tables show stated chances surviving contrary evidence.
- Enums doing numbers' job: none added; chance labels stay labels by design.
- ON_PERSON moves earn absence credit through `AWAY_DESTINATIONS` (test 12).
- Label recovery is name-matched on label text only (labels carry no question, so the
  graph arm's axis check has nothing to read); the report says so.
- Zero-weight collapse is visible in `tree_trace` (per-node weight per day) before any
  "the tree contributes nothing" reading.

## Tree design choices (where the brief left room)

- `moves_changed` = `[{activity: <inherited name>, moves: [complete new list]}]`,
  applied after the child's own activities are appended, so folding a pruned node's
  delta into its children preserves bodies exactly (test 3).
- A child requires `labels_added` (≥1 new label), a non-empty delta and a
  `distinguishing_check`. A root requires a distinct label set from every node.
- Elicitation is roots only, 3–5; a repaired response with too many roots is cut to 5,
  one with too few is kept as is (logged `cap_relaxed`) rather than discarded.
- Weight floor for pruning is on the mixture weight (as for graph leaves); the subtree
  sum is compared on the same scale. Subtree rule runs before node rule.
- Triggers for `tree`: scheduled day 3, anomaly bucket (3 repeats, p < 0.05), quality;
  max 4 calls; no uncovered-bank trigger; one call type. `tree_fixed` never calls.
- Policy `b0.5` on the tree uses `LabelDisambiguationSense` (with/without split per
  label); `b0` is bit-identical to myopic VoI (test 8).
- Settled labels: share ≥ 0.9 of node weight (same knob as `settled_weight`).

## Arms in this run

Active f0 and passive, named and anonymized: tree (re-asking), tree_fixed, flat LLM
(re-asking), flat fixed, graph fixed, mostfreq72, routine_posterior; plus
tree_fixed named b0.5 (active) and the log reader (named, active), run alongside on the
otherwise idle GPU.

## Deviations noticed during the run

- The parser applies the "no object/receptacle id" rule to `rationale` as well as
  `labels`. Two tree responses were rejected whole for a rationale quoting receptacle ids
  and recovered by the repair round. The rule stays as run (provenance); relaxing it to
  labels only is a one-line change for the next run.
- The anomaly trigger fired once per active tree arm (day 14) and never in passive; the
  quality trigger never fired. Tree arms therefore made 1–2 calls of the 4 allowed.
- The log reader ran alongside on the same server; its numbers land in the README when it
  finishes (~4 h).

## Results

See `hh_001__bank0/README.md` (summary), `hh_001__bank0/figures/tables.md` and
`hh_001__bank0/figures/tree_report.md`. Headline: every LLM arm 0.755–0.767 exact top-1
active, routine posterior 0.809; the merged rule had been flattering most-frequent (0.801
merged vs 0.755 exact) because it answers OUT_OF_HOUSE for carried objects.

## treeLongLeaf (added 2026-09-14 evening, queued behind the log reader)

Motivation from the Phase 3 numbers: the statistical particle ends at weight ~0 in every
tree arm (the programs explain the sightings better than most-frequent) yet answers no
better, and no tree came near the 12-node cap — the family "rest map + a few moves" is the
limit, not the count. So this arm changes the family and the count together.

- **Hypothesis = markdown document** (`hypotheses/longleaf_<cond>/tl0_bank0_p3/hh_001/
  <id>.md`, mirrored into each arm's `library/` with `INDEX.md` carrying weight and
  status). Prose (who lives here, what sets this apart, what would refute it) plus one
  fenced JSON block the converter runs.
- **No rest state.** The JSON is a per-target TIMETABLE: ordered blocks
  `{days, from, to, at, chance}`; later blocks override earlier ones; hours no block covers
  fall to the object's own sighting statistics; `class:` targets apply to later objects.
  Converter `beliefs/timetable_hypothesis.py`: each block's chance is a Beta with the
  label prior, updated by sightings inside the block with credit shared down the priority
  stack; edges soft (0.5 h) and fixed; away blocks earn the absence credit from empty looks
  at the receptacle they override; total claimed mass capped at 0.95.
- **Many of them.** Installation asks for 12–20 documents (retries up to 3 calls until at
  least 8 survive); revisions on days 3, 7, 14 plus anomaly and quality (max 4 calls) ask
  for 3–8 new documents each; library cap 40.
- **Never deleted.** A document under the weight floor (0.02) for 3 days is RETIRED: out of
  the particle set, kept in the library with its last weight and day, shown to the model
  as retired, revivable with a `REVIVE p_xxxx` line. Never below 3 live documents.
- Mixture `beliefs/longleaf_mixture.py` (subclass of the flat mixture; particle factory
  hook added to the parent). Arms `longleaf` / `longleaf_fixed`, conditions
  `longleaf_named` / `longleaf_anonymized`; anonymized documents keep their prose in token
  space and translate only the JSON. Prompts (`longleaf_prompt.py`) pass the same
  no-negation / tour-seen-only checks. Tests: `tests/test_longleaf.py` (8).
- Policy: plain myopic VoI (f0). No label bonus — documents carry no labels.

### treeLongLeaf: what the first run (2026-09-15 03:17–04:13) taught, and the rerun

- Elicitation: named 11 documents (13 written; 2 dropped for the chance label `always`,
  which the repair round repeated), anonymized 16 (no drops). 10 of the 11 named
  documents send objects out on a stated schedule.
- **Bug 1 (fixed):** the shared LLM client kept only the first fenced block of a reply,
  so the multi-document elicitation came back as one JSON block and three attempts were
  wasted. Library calls now ask for the full reply (`keep_content`, part of the cache
  key).
- **Bug 2 (fixed):** the revision prompt carries every document (up to ~25k tokens); with
  a fixed 40k output budget the request exceeded the 65k context and the server refused it
  (HTTP 400) — all four re-asking arms crashed at their day-3 call. Output budgets are
  now fitted to the prompt (`output_budget`).
- **Design flaw (fixed):** with no rest state, a block said only "usually at X"; it could
  learn its chance but not *where*, so on churny kitchen objects every document was a
  worse likelihood model than most-frequent, and the named library's weight went to the
  statistical particle by day 3 with 8 of 11 documents retired by day 6. Each block now
  carries a where-Dirichlet (stated `at` as the decaying pseudo-count, in-window sightings
  as counts): a document is a time-conditioned frequency model, never worse than plain
  counts.
- **Entry rule (deviation from "mean log weight"):** a new document enters at the weight
  its replayed log-likelihood earns relative to a fresh statistical particle, anchored on
  that particle's current weight. The mean of the existing documents is exactly wrong when
  they have already lost — which is when a revision is called.
- First-run fixed-set numbers (superseded by the rerun, kept for the record): active named
  0.756, anonymized 0.763; tour-absent 0.498 both.
- Aided log reader (same out-of-house paragraph + per-object weekday-daytime absence table
  as the library prompts): 0.753 vs 0.773 unaided; tour-absent 0.566 vs 0.525;
  tour-visible 0.837 vs 0.883; 2,850 calls, 153 invalid decisions (vs 119). The help moved
  answers toward OUT_OF_HOUSE: it gained on the objects that do leave and lost more on the
  ones that stay.

### treeLongLeaf as intended (2026-09-15, second rerun of the re-asking arms)

- **Revisions read the library like files.** Phase one sends the index (id, title,
  weight, fork lineage, claim tallies) and the evidence — no document bodies; the model
  replies `READ p_xxxx …` (up to 6) or writes documents straight away. Phase two adds only
  the requested documents. Day-3 named prompt: ~34k tokens before, ~8k now.
- **No scheduled revisions.** Triggers: a live document at weight ≥ 0.1 whose claim went
  against it ≥ 2 times (and more against than for) since the last call; the anomaly
  bucket; prediction quality. Gap 40 sightings; cap 12 calls.
- One per-object evidence table (usual place, share of sighted days, distinct
  receptacles, sightings, weekday 9–17 found/empty looks at the usual place) replaces the
  statistics and absence sections; "objects outside every document" dropped (the index
  shows coverage).
- Log-reader call logs now record cache hits with their original generation time.
- Parser tolerances added after reading the first revisions (all deterministic, all
  logged in the stored block): chance words outside the four labels map onto them
  (`always`→`almost_always`, `mostly`→`usually`, …); a fork inherits every target and
  claim it does not restate from its parent; the literal `OUT_OF_HOUSE`/`ON_PERSON` in an
  anonymized reply map onto their tokens. The repair round now receives the whole failed
  document (it was truncated to 2,000 chars, which is why repairs used to fail), and both
  rounds' drop reasons are kept. The claim trigger waits a full day since the episode
  start or the last call as well as 40 sightings (an active arm met the sighting gap on the
  tour afternoon).
- Library cap: was 40 on live + retired and rejected an overflowing reply whole; the
  first full run hit it from call 7 (anonymized, day 14) and call 9 (named, day 11) and
  wasted the remaining calls. Now 40 LIVE documents, and a reply keeps as many documents
  as there is room for (the rest are logged as `left_out`). Both active arms relaunched
  11:39 with the request cache replaying their earlier calls.

### treeLongLeaf result (2026-09-15 12:50)

Active named 0.790 exact (tour-absent 0.586); fixed library 0.763 (0.495); anonymized
0.759 (0.502); aided log reader 0.753 (0.566). Paired: named library +0.028 [+0.019,
+0.036] over its fixed set, +0.019 [+0.008, +0.030] over most-frequent, −0.019 [−0.038,
0.000] against the routine posterior. The passive re-asking arms were stopped on request
(GPU contention) and sit under `arms/incomplete/_stopped_*`.
