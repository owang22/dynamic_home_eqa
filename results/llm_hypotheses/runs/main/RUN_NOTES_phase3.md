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

## Results

(filled in when the run finishes — see the household README and `figures/tables.md`,
`figures/tree_report.md`)
