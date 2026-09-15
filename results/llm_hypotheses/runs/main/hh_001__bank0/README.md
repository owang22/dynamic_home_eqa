# hh_001 · timeline seed 0 · bank seed 0 — Phase 3 (hypothesis tree), 2026-09-14

World: owner-room drift + per-resident forgetfulness. Bank re-exported today with ON_PERSON
unsensable (question list unchanged from the Phase 2 bank). Prompts show only objects the
robot has sighted. Model: Qwen3.8-27B, served locally. **Scoring is exact** (ON_PERSON and
OUT_OF_HOUSE are different answers); the older merged number is in brackets in every table.
2472 questions per arm, 28 days, 24 looks a day in the active protocol. Standard error
≈ 0.009 overall, 0.018 on the tour-absent stratum (765 questions about the 11 objects the
tour never saw). Design choices and deviations: `../RUN_NOTES_phase3.md`.

## Active protocol (the numbers that matter)

| arm | top-1 exact (merged) | tour-absent | what it is |
|---|---|---|---|
| routine posterior | **0.809** (0.810) | **0.731** | ceiling on routine knowledge: posterior over 800 re-realizations of the program; eps 0.7 / half-life 6 h, re-selected on hh_002 under exact scoring |
| flat LLM, fixed set (anonymized) | 0.767 (0.780) | 0.498 | 5 hypotheses, never revised |
| tree LLM, fixed roots | 0.766 (0.780) | 0.495 | 4 root hypotheses with labels, no revision |
| tree LLM, fixed roots, β 0.5 | 0.766 (0.782) | 0.505 | same, label-targeted sensing bonus |
| tree LLM, re-asking | 0.766 (0.779) | 0.498 | tree refined by add_child on day 3 and on an anomaly (day 14) |
| flat LLM, re-asking | 0.762 (0.783) | 0.497 | flat set revised 4 times (3 of them on days 0–2) |
| graph LLM, fixed set | 0.764 (0.778) | 0.499 | Phase 2 assumption graph, no revision |
| most-frequent 72 h | 0.755 (**0.801**) | 0.493 (0.622) | no LLM; the mixture's own statistical particle |
| log reader | 0.773 (0.773) | 0.525 | no belief model: one LLM call per decision over the whole log; 2,783 calls, 48.6 M prompt tokens, 4.1 h |

Reading:

- Every LLM arm sits 0.75–0.77 (the log reader too, at 0.773 and ~400× the cost), inside
  about one standard error of each other and of the no-LLM baseline; tree re-asking and tree fixed are identical to three decimals. The tree
  is not buying accuracy at this horizon. Its structure behaves as designed (below), which
  is the thing Phase 3 was built to test before a tree could be blamed or credited.
- **The merged score was flattering most-frequent** by 4.6 points overall and 13 points on
  tour-absent objects: it answers OUT_OF_HOUSE for carried objects, which merged scoring
  called correct whenever the truth was ON_PERSON. Under exact scoring the LLM arms lead
  most-frequent by +0.007 [−0.002, +0.016] (paired, active); passive most-frequent still
  leads by 0.017.
- Routine posterior is the only arm that handles tour-absent objects (0.73 vs ~0.50).

## What the tree did (from `figures/tree_report.md`)

- Elicitation gave 4 roots in both conditions (24 tour-seen objects). Named: every root
  carries `single_resident_mara` (the model read the owner suffix), roots differ on work
  pattern. Anonymized: roots split single vs two adults × commute pattern.
- Re-asking arms made 1–2 calls (scheduled day 3; anomaly bucket on day 14 in the active
  arms; the quality trigger never fired). Every call was `add_child`; no `add_root`. Two
  responses were rejected whole because the rationale text quoted receptacle ids; the
  repair round fixed both. No other rejections.
- Of 7 children added, 3 gained weight over the next 5 days (one to 0.62 of the node
  weight, one to 0.50, one to 0.35), 2 lost, 2 were pruned within a week (born at
  ≤ 0.015). One starved root subtree was pruned per arm (days 5–11). Max depth 1.
- Children were mostly `rest_overrides` restating rests for 11–16 objects plus one
  activity; the anomaly-triggered children added kitchen activities.
- Label recovery (name-matched): composition matched in every arm (`single_resident_mara`
  at 1.00 named; `single_adult` at 0.26–0.45 anonymized, where the two-adult roots hold
  most weight — the anonymized tree is wrong about composition and the sightings did not
  correct it). Work pattern: `commutes_weekday` 0.65–0.93 named; anonymized
  `both_commute` 0.39–0.74.
- Statistical particle weight 0.000–0.003 in every tree arm: the roots explain the
  sightings better than most-frequent yet answer no better — the gap is in what a rest map
  plus a few moves can say, not in the weighting.

Passive protocol (no sensing): all LLM arms 0.704–0.714, most-frequent 0.721, routine
posterior 0.758 (`figures/tables.md`).

## What is where

- `figures/tables.md` — every arm, both strata, exact and merged, paired CIs, re-ask
  events, tree table, graph table. `figures/tree_report.md` — node count/depth per day,
  add_child vs add_root by trigger, tour-absent objects, per-revision weight gain,
  prunes, label recovery. `figures/tree_nodes_depth.png`, `arms_and_strata.png`,
  `baselines_daily.png`, `per_object_heatmap.png`, …
- `arms/active/`, `arms/passive/`, `arms/anonymized/` — per arm `per_question.jsonl.gz`,
  `diagnostics.json` (tree trace, edit/prune/reparent/rejected logs, check outcomes,
  bucket trace, label recovery), `provenance.json`, `revisions/*.json` (full prompts and
  thinking traces).
- Elicitation inputs: `../../hypotheses/<condition>/tl0_bank0_p3/hh_001.json`
  (`tree_named`, `tree_anonymized`, `graph_*`, `tour_*`), exchanges in
  `../../logs/<condition>/tl0_bank0_p3/`.
- Phase 2 run (old bank header, merged scoring): `../../archive/phase2_2026-09-14/`.

## Caveats

- One household, one seed. Passive gaps are all inside the CIs; active gaps between LLM
  arms are too.
- The named tree settles composition at 1.00 on day 0 because every root shares the label —
  "settled" there means "never in question", not "learned".
- Flat re-asking still spends 3 of 4 calls on days 0–2 (uncovered-bank trigger); the tree
  arm has no such trigger by design.
