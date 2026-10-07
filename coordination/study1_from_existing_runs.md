# Study 1 from the runs already on disk: first guess right after each return to normal

Written 2026-10-02. Nothing here ran a model or touched the GPU. Every number below is produced by
`coordination/study1_from_existing_runs.py` (run as `PYTHONPATH=src python3
coordination/study1_from_existing_runs.py`), which reads the answer files listed under "What was
read" and writes the raw tables to `coordination/study1_from_existing_runs.raw.md`. The tables in
this file are that output, pasted whole.

## What was read, and how it is scored

- The run: `results/self_improve/wave_the_second_illness/cells/<method>/<household>/searches.jsonl`,
  one JSON row per question (`kind == "search"`), 24 questions a day, days 1-49, three households:
  `hh_s2_t03`, `hh_s32_t03`, `hh_s48_t03` (questions_answered.md section 1, "The 50-day
  second-illness run"). Bank: `results/self_improve/varied_homes/all_generated_v2_twice/banks`.
  Resident 1 is sick on days 14-23 and 32-41; days 24-31 and 42-49 are the returns
  (questions_answered.md section 4).
- The method is the cell directory name, not the `how_memory_is_written` field (section 1).
- "First guess right" = the row's `found_at_step == 1`. That is the same rule as
  `results/self_improve/paper/scripts/paper_data.py` `share(rows, "first")`, and it is room level
  because a search only ever opens whole rooms (`src/self_improve/search_driven.py:550`, section 6).
  `found_at_step` is filled on every row, so the denominator is every question in the window
  (section 13). `src/self_improve/score_at_both_levels.py` and `accuracy_by_day.py` score a
  different file format (the frozen-memory `held_out_answers.json`); they were read, and only their
  convention (room level primary, paired per-household differences, mean and standard error with
  n = households, two standard errors as the bar) is reused here.
- Windows: days 24-28 (five days after the first return) and 42-46 (five after the second), and
  the two pooled. 24 questions a day gives 120 questions per window per household, 240 pooled,
  and every arm asks the identical question list (checked row for row in the script, as section
  12 says it should be).
- Standard error: for each method the per-household difference against the reference arm is
  taken in points, and SE = standard deviation of the three differences / sqrt(3). "Separated"
  means |mean| > 2 SE. **With three households, any difference under two standard errors is not
  separated**, and the 2 SE column is also "the smallest gap this setup could detect" for that
  pair.

## Which methods are in the 50-day run

Present (one cell per household, all complete, 1,176 questions each):

| cell directory | what it is | notes |
|---|---|---|
| `last_seen_no_model` | the mechanical baseline: open the room the object was last seen in, no model call | deterministic, reproduces exactly |
| `the_log_and_notes_about_the_routine` | the sighting log plus nightly notes, model-guided | hh_s2's cell ran before the 26 Sep schema change, hh_s32 and hh_s48 after (`results/memoryWorkshop/CHECKS_ON_THE_DRAFT.md`, "the 50-day wave straddles a schema change"); same for the next two rows |
| `incremental_edits` | the plain claim store (the paper's "claim store") | |
| `ACE_as_published` | the ACE-style playbook, original wave | its merge call discarded most verdicts (overnight report, job C) |
| `ACE_as_published [ACE_fixed]` | the same arm rerun with the merge schema fixed: `results/self_improve/wave_the_second_illness_ACE_fixed/cells` | this is "the fixed rerun"; it is a rerun of ACE, not of `incremental_edits` |
| `ours_told_the_night_before` | the told arm: log and notes, told the night before the sickness starts | the only told arm in this run; it had the log at search time (section 10) |
| `last_seen_no_model [first illness deleted]` | last-seen with every day 14-23 sighting dropped from its trail: `results/self_improve/wave_last_seen_no_first_illness/cells` | a separate wave on the same bank and questions, no model; included because it is a 50-day baseline variant on disk |

Not in the 50-day run, so no number can be given: `prior_only_no_notes` (notes hidden),
`claim_store_told_if_it_was_right` (reduced ACE), `a_small_working_memory_and_an_archive`
(the 1,200-character working memory), log-only (`wave_log_only` has `log_only_no_notes` cells but
they are 31-day cells on the ten-home bank), and every other told variant. questions_answered.md
section 2 says the same for MemGPT and reduced ACE.

`results/self_improve/wave_the_second_illness_ACE_rerun/` is **not a second observation**: its
hh_s2 and hh_s32 cells match the original ACE cell on all 1,176 rows (rooms opened and
`found_at_step`), because it changed only a token cap and replayed the response cache; its hh_s48
cell was stopped on day 18 and has no `cell.json`. It is left out of the tables.

## The short version

- In the first return window (days 24-28) nothing beats last-seen. Log and notes ties it
  (-0.3 points, 2 SE 1.5); the told arm is -2.8 (2 SE 6.5, not separated); the claim store is
  -20.8 and ACE -13.3 (fixed: -13.1), both separated and below.
- In the second return window (days 42-46) log and notes is +7.5 over last-seen (2 SE 1.9,
  separated, same sign in all three homes) and the told arm +5.6 (2 SE 5.3, just separated).
  The claim store is still below (-7.8, 2 SE 4.8); ACE is -2.8 (original, 2 SE 2.4) and -1.4
  (fixed, 2 SE 2.8, not separated).
- Pooled over both windows: log and notes +3.6 (2 SE 1.5), told +1.4 (2 SE 2.4, not separated),
  ACE -8.1 / fixed -7.2, claim store -14.3.
- Against the best arm (log and notes, 91.8 pooled), last-seen is -3.6 (2 SE 1.5) and the told
  arm -2.2 (2 SE 1.7); everything else is 11 to 18 points below it (pooled).
- On moved objects the gaps are larger and the standard errors much larger (2 SE of 2 to 26
  points on the both-spell slice), because the slice has 29 to 43 questions per window per home.
  Log and notes over last-seen on days 42-46 is +12.4 on spell-1 movers (2 SE 2.4) and +16.5 on
  both-spell movers (2 SE 11.3).
- A caveat the 2 SE rule does not cover: rerun noise. The same model arm rerun against itself
  moves about 1.9 points in a settled window and 2.5 to 6.2 points in a change window
  (`results/self_improve/three_prompts/the_rerun_noise_floor.json`;
  `results/memoryWorkshop/CHECKS_ON_THE_DRAFT.md`, "1 Oct: a 31-day rerun floor"). Last-seen
  makes no model calls and has no such noise. A model-arm difference of a few points that clears
  2 SE is still inside that floor.
- Deleting the first illness from last-seen's trail changes days 42-46 not at all (0.0 in every
  home) and days 24-28 by -1.9 (2 SE 2.9): by the second return the trail no longer holds anything
  from the first sickness.

## "Moved objects only": what the code exposes

The scoring code does not expose "moved since the method last saw it" as a per-question flag.
What it exposes is two fixed object sets per household:

- `is_a_mover` on every row: `search_driven.the_movers`, an object whose commonest daytime spot on
  days 14-23 differs from days 0-13. Fixed once per run from the first sickness only, at spot level
  (sections 4 and 14). 8, 8 and 6 objects.
- `paper_data.both_spell_movers`: the subset whose commonest daytime room differs from settled in
  both sicknesses. 4, 5 and 5 objects (14 in all, the list is printed below).

Both slices are reported. A true "moved since last seen" slice could be built offline from each
cell's `looks.jsonl` (the last sighting of the object before the question) against the bank's
true place at the question time, but that would be a new definition and is not done here.

# The tables (script output, unedited)

## Question counts per window per household (every arm asks the same questions)

| household | slice | days 24-28 | days 42-46 | pooled |
|---|---|---|---|---|
| hh_s2_t03 | all | 120 | 120 | 240 |
| hh_s2_t03 | spell-1 mover | 85 | 74 | 159 |
| hh_s2_t03 | both-spell | 43 | 31 | 74 |
| hh_s32_t03 | all | 120 | 120 | 240 |
| hh_s32_t03 | spell-1 mover | 58 | 58 | 116 |
| hh_s32_t03 | both-spell | 31 | 29 | 60 |
| hh_s48_t03 | all | 120 | 120 | 240 |
| hh_s48_t03 | spell-1 mover | 48 | 40 | 88 |
| hh_s48_t03 | both-spell | 40 | 33 | 73 |

Both-spell movers per home: hh_s2_t03: 4 (book_tomas, glass_tomas, mug_tomas, water_bottle_tomas); hh_s32_t03: 5 (book_leo, glass_leo, mug_leo, tablet_leo, water_bottle_leo); hh_s48_t03: 5 (book_marco, charger_marco, glass_marco, mug_marco, water_bottle_marco)
Spell-1 movers per home (row field is_a_mover): hh_s2_t03: 8; hh_s32_t03: 8; hh_s48_t03: 6

## First guess right, percent (right/asked) - all

| method | window | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | pooled over homes |
|---|---|---|---|---|---|
| last_seen_no_model | days 24-28 | 88.3 (106/120) | 92.5 (111/120) | 88.3 (106/120) | 89.7 (323/360) |
| last_seen_no_model | days 42-46 | 85.8 (103/120) | 90.0 (108/120) | 84.2 (101/120) | 86.7 (312/360) |
| last_seen_no_model | pooled | 87.1 (209/240) | 91.2 (219/240) | 86.2 (207/240) | 88.2 (635/720) |
| ACE_as_published | days 24-28 | 75.8 (91/120) | 85.0 (102/120) | 68.3 (82/120) | 76.4 (275/360) |
| ACE_as_published | days 42-46 | 85.0 (102/120) | 87.5 (105/120) | 79.2 (95/120) | 83.9 (302/360) |
| ACE_as_published | pooled | 80.4 (193/240) | 86.2 (207/240) | 73.8 (177/240) | 80.1 (577/720) |
| ACE_as_published [ACE_fixed] | days 24-28 | 72.5 (87/120) | 85.0 (102/120) | 72.5 (87/120) | 76.7 (276/360) |
| ACE_as_published [ACE_fixed] | days 42-46 | 85.8 (103/120) | 85.8 (103/120) | 84.2 (101/120) | 85.3 (307/360) |
| ACE_as_published [ACE_fixed] | pooled | 79.2 (190/240) | 85.4 (205/240) | 78.3 (188/240) | 81.0 (583/720) |
| incremental_edits | days 24-28 | 70.8 (85/120) | 71.7 (86/120) | 64.2 (77/120) | 68.9 (248/360) |
| incremental_edits | days 42-46 | 77.5 (93/120) | 78.3 (94/120) | 80.8 (97/120) | 78.9 (284/360) |
| incremental_edits | pooled | 74.2 (178/240) | 75.0 (180/240) | 72.5 (174/240) | 73.9 (532/720) |
| last_seen_no_model [first illness deleted] | days 24-28 | 89.2 (107/120) | 88.3 (106/120) | 85.8 (103/120) | 87.8 (316/360) |
| last_seen_no_model [first illness deleted] | days 42-46 | 85.8 (103/120) | 90.0 (108/120) | 84.2 (101/120) | 86.7 (312/360) |
| last_seen_no_model [first illness deleted] | pooled | 87.5 (210/240) | 89.2 (214/240) | 85.0 (204/240) | 87.2 (628/720) |
| ours_told_the_night_before | days 24-28 | 90.0 (108/120) | 91.7 (110/120) | 79.2 (95/120) | 86.9 (313/360) |
| ours_told_the_night_before | days 42-46 | 91.7 (110/120) | 90.8 (109/120) | 94.2 (113/120) | 92.2 (332/360) |
| ours_told_the_night_before | pooled | 90.8 (218/240) | 91.2 (219/240) | 86.7 (208/240) | 89.6 (645/720) |
| the_log_and_notes_about_the_routine | days 24-28 | 88.3 (106/120) | 90.8 (109/120) | 89.2 (107/120) | 89.4 (322/360) |
| the_log_and_notes_about_the_routine | days 42-46 | 95.0 (114/120) | 95.8 (115/120) | 91.7 (110/120) | 94.2 (339/360) |
| the_log_and_notes_about_the_routine | pooled | 91.7 (220/240) | 93.3 (224/240) | 90.4 (217/240) | 91.8 (661/720) |

## First guess right, percent (right/asked) - spell-1 mover

| method | window | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | pooled over homes |
|---|---|---|---|---|---|
| last_seen_no_model | days 24-28 | 84.7 (72/85) | 86.2 (50/58) | 75.0 (36/48) | 82.7 (158/191) |
| last_seen_no_model | days 42-46 | 78.4 (58/74) | 79.3 (46/58) | 65.0 (26/40) | 75.6 (130/172) |
| last_seen_no_model | pooled | 81.8 (130/159) | 82.8 (96/116) | 70.5 (62/88) | 79.3 (288/363) |
| ACE_as_published | days 24-28 | 68.2 (58/85) | 70.7 (41/58) | 39.6 (19/48) | 61.8 (118/191) |
| ACE_as_published | days 42-46 | 77.0 (57/74) | 75.9 (44/58) | 40.0 (16/40) | 68.0 (117/172) |
| ACE_as_published | pooled | 72.3 (115/159) | 73.3 (85/116) | 39.8 (35/88) | 64.7 (235/363) |
| ACE_as_published [ACE_fixed] | days 24-28 | 63.5 (54/85) | 70.7 (41/58) | 56.2 (27/48) | 63.9 (122/191) |
| ACE_as_published [ACE_fixed] | days 42-46 | 79.7 (59/74) | 74.1 (43/58) | 60.0 (24/40) | 73.3 (126/172) |
| ACE_as_published [ACE_fixed] | pooled | 71.1 (113/159) | 72.4 (84/116) | 58.0 (51/88) | 68.3 (248/363) |
| incremental_edits | days 24-28 | 62.4 (53/85) | 69.0 (40/58) | 33.3 (16/48) | 57.1 (109/191) |
| incremental_edits | days 42-46 | 66.2 (49/74) | 79.3 (46/58) | 52.5 (21/40) | 67.4 (116/172) |
| incremental_edits | pooled | 64.2 (102/159) | 74.1 (86/116) | 42.0 (37/88) | 62.0 (225/363) |
| last_seen_no_model [first illness deleted] | days 24-28 | 87.1 (74/85) | 86.2 (50/58) | 72.9 (35/48) | 83.2 (159/191) |
| last_seen_no_model [first illness deleted] | days 42-46 | 78.4 (58/74) | 79.3 (46/58) | 65.0 (26/40) | 75.6 (130/172) |
| last_seen_no_model [first illness deleted] | pooled | 83.0 (132/159) | 82.8 (96/116) | 69.3 (61/88) | 79.6 (289/363) |
| ours_told_the_night_before | days 24-28 | 85.9 (73/85) | 86.2 (50/58) | 52.1 (25/48) | 77.5 (148/191) |
| ours_told_the_night_before | days 42-46 | 86.5 (64/74) | 84.5 (49/58) | 82.5 (33/40) | 84.9 (146/172) |
| ours_told_the_night_before | pooled | 86.2 (137/159) | 85.3 (99/116) | 65.9 (58/88) | 81.0 (294/363) |
| the_log_and_notes_about_the_routine | days 24-28 | 85.9 (73/85) | 86.2 (50/58) | 75.0 (36/48) | 83.2 (159/191) |
| the_log_and_notes_about_the_routine | days 42-46 | 91.9 (68/74) | 93.1 (54/58) | 75.0 (30/40) | 88.4 (152/172) |
| the_log_and_notes_about_the_routine | pooled | 88.7 (141/159) | 89.7 (104/116) | 75.0 (66/88) | 85.7 (311/363) |

## First guess right, percent (right/asked) - both-spell

| method | window | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | pooled over homes |
|---|---|---|---|---|---|
| last_seen_no_model | days 24-28 | 81.4 (35/43) | 77.4 (24/31) | 75.0 (30/40) | 78.1 (89/114) |
| last_seen_no_model | days 42-46 | 71.0 (22/31) | 58.6 (17/29) | 60.6 (20/33) | 63.4 (59/93) |
| last_seen_no_model | pooled | 77.0 (57/74) | 68.3 (41/60) | 68.5 (50/73) | 71.5 (148/207) |
| ACE_as_published | days 24-28 | 53.5 (23/43) | 58.1 (18/31) | 27.5 (11/40) | 45.6 (52/114) |
| ACE_as_published | days 42-46 | 64.5 (20/31) | 69.0 (20/29) | 33.3 (11/33) | 54.8 (51/93) |
| ACE_as_published | pooled | 58.1 (43/74) | 63.3 (38/60) | 30.1 (22/73) | 49.8 (103/207) |
| ACE_as_published [ACE_fixed] | days 24-28 | 55.8 (24/43) | 54.8 (17/31) | 52.5 (21/40) | 54.4 (62/114) |
| ACE_as_published [ACE_fixed] | days 42-46 | 64.5 (20/31) | 62.1 (18/29) | 51.5 (17/33) | 59.1 (55/93) |
| ACE_as_published [ACE_fixed] | pooled | 59.5 (44/74) | 58.3 (35/60) | 52.1 (38/73) | 56.5 (117/207) |
| incremental_edits | days 24-28 | 51.2 (22/43) | 51.6 (16/31) | 30.0 (12/40) | 43.9 (50/114) |
| incremental_edits | days 42-46 | 41.9 (13/31) | 72.4 (21/29) | 42.4 (14/33) | 51.6 (48/93) |
| incremental_edits | pooled | 47.3 (35/74) | 61.7 (37/60) | 35.6 (26/73) | 47.3 (98/207) |
| last_seen_no_model [first illness deleted] | days 24-28 | 88.4 (38/43) | 77.4 (24/31) | 72.5 (29/40) | 79.8 (91/114) |
| last_seen_no_model [first illness deleted] | days 42-46 | 71.0 (22/31) | 58.6 (17/29) | 60.6 (20/33) | 63.4 (59/93) |
| last_seen_no_model [first illness deleted] | pooled | 81.1 (60/74) | 68.3 (41/60) | 67.1 (49/73) | 72.5 (150/207) |
| ours_told_the_night_before | days 24-28 | 79.1 (34/43) | 74.2 (23/31) | 50.0 (20/40) | 67.5 (77/114) |
| ours_told_the_night_before | days 42-46 | 74.2 (23/31) | 69.0 (20/29) | 78.8 (26/33) | 74.2 (69/93) |
| ours_told_the_night_before | pooled | 77.0 (57/74) | 71.7 (43/60) | 63.0 (46/73) | 70.5 (146/207) |
| the_log_and_notes_about_the_routine | days 24-28 | 81.4 (35/43) | 80.6 (25/31) | 77.5 (31/40) | 79.8 (91/114) |
| the_log_and_notes_about_the_routine | days 42-46 | 83.9 (26/31) | 86.2 (25/29) | 69.7 (23/33) | 79.6 (74/93) |
| the_log_and_notes_about_the_routine | pooled | 82.4 (61/74) | 83.3 (50/60) | 74.0 (54/73) | 79.7 (165/207) |

## Paired per-household difference against last_seen_no_model, points of first guess right - all

| method | window | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | mean | SE (n homes) | 2 SE | separated? |
|---|---|---|---|---|---|---|---|---|
| ACE_as_published | days 24-28 | -12.5 | -7.5 | -20.0 | -13.3 | 3.6 (n=3) | 7.3 | yes |
| ACE_as_published | days 42-46 | -0.8 | -2.5 | -5.0 | -2.8 | 1.2 (n=3) | 2.4 | yes |
| ACE_as_published | pooled | -6.7 | -5.0 | -12.5 | -8.1 | 2.3 (n=3) | 4.5 | yes |
| ACE_as_published [ACE_fixed] | days 24-28 | -15.8 | -7.5 | -15.8 | -13.1 | 2.8 (n=3) | 5.6 | yes |
| ACE_as_published [ACE_fixed] | days 42-46 | +0.0 | -4.2 | +0.0 | -1.4 | 1.4 (n=3) | 2.8 | no |
| ACE_as_published [ACE_fixed] | pooled | -7.9 | -5.8 | -7.9 | -7.2 | 0.7 (n=3) | 1.4 | yes |
| incremental_edits | days 24-28 | -17.5 | -20.8 | -24.2 | -20.8 | 1.9 (n=3) | 3.8 | yes |
| incremental_edits | days 42-46 | -8.3 | -11.7 | -3.3 | -7.8 | 2.4 (n=3) | 4.8 | yes |
| incremental_edits | pooled | -12.9 | -16.2 | -13.8 | -14.3 | 1.0 (n=3) | 2.0 | yes |
| last_seen_no_model [first illness deleted] | days 24-28 | +0.8 | -4.2 | -2.5 | -1.9 | 1.5 (n=3) | 2.9 | no |
| last_seen_no_model [first illness deleted] | days 42-46 | +0.0 | +0.0 | +0.0 | +0.0 | 0.0 (n=3) | 0.0 | no |
| last_seen_no_model [first illness deleted] | pooled | +0.4 | -2.1 | -1.3 | -1.0 | 0.7 (n=3) | 1.5 | no |
| ours_told_the_night_before | days 24-28 | +1.7 | -0.8 | -9.2 | -2.8 | 3.3 (n=3) | 6.5 | no |
| ours_told_the_night_before | days 42-46 | +5.8 | +0.8 | +10.0 | +5.6 | 2.6 (n=3) | 5.3 | yes |
| ours_told_the_night_before | pooled | +3.7 | +0.0 | +0.4 | +1.4 | 1.2 (n=3) | 2.4 | no |
| the_log_and_notes_about_the_routine | days 24-28 | +0.0 | -1.7 | +0.8 | -0.3 | 0.7 (n=3) | 1.5 | no |
| the_log_and_notes_about_the_routine | days 42-46 | +9.2 | +5.8 | +7.5 | +7.5 | 1.0 (n=3) | 1.9 | yes |
| the_log_and_notes_about_the_routine | pooled | +4.6 | +2.1 | +4.2 | +3.6 | 0.8 (n=3) | 1.5 | yes |

## Paired per-household difference against last_seen_no_model, points of first guess right - spell-1 mover

| method | window | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | mean | SE (n homes) | 2 SE | separated? |
|---|---|---|---|---|---|---|---|---|
| ACE_as_published | days 24-28 | -16.5 | -15.5 | -35.4 | -22.5 | 6.5 (n=3) | 13.0 | yes |
| ACE_as_published | days 42-46 | -1.4 | -3.4 | -25.0 | -9.9 | 7.6 (n=3) | 15.1 | no |
| ACE_as_published | pooled | -9.4 | -9.5 | -30.7 | -16.5 | 7.1 (n=3) | 14.1 | yes |
| ACE_as_published [ACE_fixed] | days 24-28 | -21.2 | -15.5 | -18.8 | -18.5 | 1.6 (n=3) | 3.3 | yes |
| ACE_as_published [ACE_fixed] | days 42-46 | +1.4 | -5.2 | -5.0 | -2.9 | 2.1 (n=3) | 4.3 | no |
| ACE_as_published [ACE_fixed] | pooled | -10.7 | -10.3 | -12.5 | -11.2 | 0.7 (n=3) | 1.3 | yes |
| incremental_edits | days 24-28 | -22.4 | -17.2 | -41.7 | -27.1 | 7.4 (n=3) | 14.9 | yes |
| incremental_edits | days 42-46 | -12.2 | +0.0 | -12.5 | -8.2 | 4.1 (n=3) | 8.2 | no |
| incremental_edits | pooled | -17.6 | -8.6 | -28.4 | -18.2 | 5.7 (n=3) | 11.4 | yes |
| last_seen_no_model [first illness deleted] | days 24-28 | +2.4 | +0.0 | -2.1 | +0.1 | 1.3 (n=3) | 2.6 | no |
| last_seen_no_model [first illness deleted] | days 42-46 | +0.0 | +0.0 | +0.0 | +0.0 | 0.0 (n=3) | 0.0 | no |
| last_seen_no_model [first illness deleted] | pooled | +1.3 | +0.0 | -1.1 | +0.0 | 0.7 (n=3) | 1.4 | no |
| ours_told_the_night_before | days 24-28 | +1.2 | +0.0 | -22.9 | -7.2 | 7.8 (n=3) | 15.7 | no |
| ours_told_the_night_before | days 42-46 | +8.1 | +5.2 | +17.5 | +10.3 | 3.7 (n=3) | 7.4 | yes |
| ours_told_the_night_before | pooled | +4.4 | +2.6 | -4.5 | +0.8 | 2.7 (n=3) | 5.5 | no |
| the_log_and_notes_about_the_routine | days 24-28 | +1.2 | +0.0 | +0.0 | +0.4 | 0.4 (n=3) | 0.8 | no |
| the_log_and_notes_about_the_routine | days 42-46 | +13.5 | +13.8 | +10.0 | +12.4 | 1.2 (n=3) | 2.4 | yes |
| the_log_and_notes_about_the_routine | pooled | +6.9 | +6.9 | +4.5 | +6.1 | 0.8 (n=3) | 1.6 | yes |

## Paired per-household difference against last_seen_no_model, points of first guess right - both-spell

| method | window | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | mean | SE (n homes) | 2 SE | separated? |
|---|---|---|---|---|---|---|---|---|
| ACE_as_published | days 24-28 | -27.9 | -19.4 | -47.5 | -31.6 | 8.3 (n=3) | 16.7 | yes |
| ACE_as_published | days 42-46 | -6.5 | +10.3 | -27.3 | -7.8 | 10.9 (n=3) | 21.8 | no |
| ACE_as_published | pooled | -18.9 | -5.0 | -38.4 | -20.8 | 9.7 (n=3) | 19.3 | yes |
| ACE_as_published [ACE_fixed] | days 24-28 | -25.6 | -22.6 | -22.5 | -23.6 | 1.0 (n=3) | 2.0 | yes |
| ACE_as_published [ACE_fixed] | days 42-46 | -6.5 | +3.4 | -9.1 | -4.0 | 3.8 (n=3) | 7.6 | no |
| ACE_as_published [ACE_fixed] | pooled | -17.6 | -10.0 | -16.4 | -14.7 | 2.4 (n=3) | 4.7 | yes |
| incremental_edits | days 24-28 | -30.2 | -25.8 | -45.0 | -33.7 | 5.8 (n=3) | 11.6 | yes |
| incremental_edits | days 42-46 | -29.0 | +13.8 | -18.2 | -11.1 | 12.9 (n=3) | 25.7 | no |
| incremental_edits | pooled | -29.7 | -6.7 | -32.9 | -23.1 | 8.3 (n=3) | 16.5 | yes |
| last_seen_no_model [first illness deleted] | days 24-28 | +7.0 | +0.0 | -2.5 | +1.5 | 2.8 (n=3) | 5.7 | no |
| last_seen_no_model [first illness deleted] | days 42-46 | +0.0 | +0.0 | +0.0 | +0.0 | 0.0 (n=3) | 0.0 | no |
| last_seen_no_model [first illness deleted] | pooled | +4.1 | +0.0 | -1.4 | +0.9 | 1.6 (n=3) | 3.3 | no |
| ours_told_the_night_before | days 24-28 | -2.3 | -3.2 | -25.0 | -10.2 | 7.4 (n=3) | 14.8 | no |
| ours_told_the_night_before | days 42-46 | +3.2 | +10.3 | +18.2 | +10.6 | 4.3 (n=3) | 8.6 | yes |
| ours_told_the_night_before | pooled | +0.0 | +3.3 | -5.5 | -0.7 | 2.6 (n=3) | 5.1 | no |
| the_log_and_notes_about_the_routine | days 24-28 | +0.0 | +3.2 | +2.5 | +1.9 | 1.0 (n=3) | 2.0 | no |
| the_log_and_notes_about_the_routine | days 42-46 | +12.9 | +27.6 | +9.1 | +16.5 | 5.6 (n=3) | 11.3 | yes |
| the_log_and_notes_about_the_routine | pooled | +5.4 | +15.0 | +5.5 | +8.6 | 3.2 (n=3) | 6.4 | yes |

## Paired per-household difference against the best arm on pooled first guess, the_log_and_notes_about_the_routine, points of first guess right - all

| method | window | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | mean | SE (n homes) | 2 SE | separated? |
|---|---|---|---|---|---|---|---|---|
| last_seen_no_model | days 24-28 | +0.0 | +1.7 | -0.8 | +0.3 | 0.7 (n=3) | 1.5 | no |
| last_seen_no_model | days 42-46 | -9.2 | -5.8 | -7.5 | -7.5 | 1.0 (n=3) | 1.9 | yes |
| last_seen_no_model | pooled | -4.6 | -2.1 | -4.2 | -3.6 | 0.8 (n=3) | 1.5 | yes |
| ACE_as_published | days 24-28 | -12.5 | -5.8 | -20.8 | -13.1 | 4.3 (n=3) | 8.7 | yes |
| ACE_as_published | days 42-46 | -10.0 | -8.3 | -12.5 | -10.3 | 1.2 (n=3) | 2.4 | yes |
| ACE_as_published | pooled | -11.2 | -7.1 | -16.7 | -11.7 | 2.8 (n=3) | 5.5 | yes |
| ACE_as_published [ACE_fixed] | days 24-28 | -15.8 | -5.8 | -16.7 | -12.8 | 3.5 (n=3) | 7.0 | yes |
| ACE_as_published [ACE_fixed] | days 42-46 | -9.2 | -10.0 | -7.5 | -8.9 | 0.7 (n=3) | 1.5 | yes |
| ACE_as_published [ACE_fixed] | pooled | -12.5 | -7.9 | -12.1 | -10.8 | 1.5 (n=3) | 2.9 | yes |
| incremental_edits | days 24-28 | -17.5 | -19.2 | -25.0 | -20.6 | 2.3 (n=3) | 4.5 | yes |
| incremental_edits | days 42-46 | -17.5 | -17.5 | -10.8 | -15.3 | 2.2 (n=3) | 4.4 | yes |
| incremental_edits | pooled | -17.5 | -18.3 | -17.9 | -17.9 | 0.2 (n=3) | 0.5 | yes |
| last_seen_no_model [first illness deleted] | days 24-28 | +0.8 | -2.5 | -3.3 | -1.7 | 1.3 (n=3) | 2.5 | no |
| last_seen_no_model [first illness deleted] | days 42-46 | -9.2 | -5.8 | -7.5 | -7.5 | 1.0 (n=3) | 1.9 | yes |
| last_seen_no_model [first illness deleted] | pooled | -4.2 | -4.2 | -5.4 | -4.6 | 0.4 (n=3) | 0.8 | yes |
| ours_told_the_night_before | days 24-28 | +1.7 | +0.8 | -10.0 | -2.5 | 3.8 (n=3) | 7.5 | no |
| ours_told_the_night_before | days 42-46 | -3.3 | -5.0 | +2.5 | -1.9 | 2.3 (n=3) | 4.5 | no |
| ours_told_the_night_before | pooled | -0.8 | -2.1 | -3.7 | -2.2 | 0.8 (n=3) | 1.7 | yes |

## Paired per-household difference against the best arm on pooled first guess, the_log_and_notes_about_the_routine, points of first guess right - spell-1 mover

| method | window | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | mean | SE (n homes) | 2 SE | separated? |
|---|---|---|---|---|---|---|---|---|
| last_seen_no_model | days 24-28 | -1.2 | +0.0 | +0.0 | -0.4 | 0.4 (n=3) | 0.8 | no |
| last_seen_no_model | days 42-46 | -13.5 | -13.8 | -10.0 | -12.4 | 1.2 (n=3) | 2.4 | yes |
| last_seen_no_model | pooled | -6.9 | -6.9 | -4.5 | -6.1 | 0.8 (n=3) | 1.6 | yes |
| ACE_as_published | days 24-28 | -17.6 | -15.5 | -35.4 | -22.9 | 6.3 (n=3) | 12.6 | yes |
| ACE_as_published | days 42-46 | -14.9 | -17.2 | -35.0 | -22.4 | 6.4 (n=3) | 12.7 | yes |
| ACE_as_published | pooled | -16.4 | -16.4 | -35.2 | -22.7 | 6.3 (n=3) | 12.6 | yes |
| ACE_as_published [ACE_fixed] | days 24-28 | -22.4 | -15.5 | -18.8 | -18.9 | 2.0 (n=3) | 3.9 | yes |
| ACE_as_published [ACE_fixed] | days 42-46 | -12.2 | -19.0 | -15.0 | -15.4 | 2.0 (n=3) | 3.9 | yes |
| ACE_as_published [ACE_fixed] | pooled | -17.6 | -17.2 | -17.0 | -17.3 | 0.2 (n=3) | 0.3 | yes |
| incremental_edits | days 24-28 | -23.5 | -17.2 | -41.7 | -27.5 | 7.3 (n=3) | 14.6 | yes |
| incremental_edits | days 42-46 | -25.7 | -13.8 | -22.5 | -20.7 | 3.6 (n=3) | 7.1 | yes |
| incremental_edits | pooled | -24.5 | -15.5 | -33.0 | -24.3 | 5.0 (n=3) | 10.1 | yes |
| last_seen_no_model [first illness deleted] | days 24-28 | +1.2 | +0.0 | -2.1 | -0.3 | 1.0 (n=3) | 1.9 | no |
| last_seen_no_model [first illness deleted] | days 42-46 | -13.5 | -13.8 | -10.0 | -12.4 | 1.2 (n=3) | 2.4 | yes |
| last_seen_no_model [first illness deleted] | pooled | -5.7 | -6.9 | -5.7 | -6.1 | 0.4 (n=3) | 0.8 | yes |
| ours_told_the_night_before | days 24-28 | +0.0 | +0.0 | -22.9 | -7.6 | 7.6 (n=3) | 15.3 | no |
| ours_told_the_night_before | days 42-46 | -5.4 | -8.6 | +7.5 | -2.2 | 4.9 (n=3) | 9.9 | no |
| ours_told_the_night_before | pooled | -2.5 | -4.3 | -9.1 | -5.3 | 2.0 (n=3) | 3.9 | yes |

## Paired per-household difference against the best arm on pooled first guess, the_log_and_notes_about_the_routine, points of first guess right - both-spell

| method | window | hh_s2_t03 | hh_s32_t03 | hh_s48_t03 | mean | SE (n homes) | 2 SE | separated? |
|---|---|---|---|---|---|---|---|---|
| last_seen_no_model | days 24-28 | +0.0 | -3.2 | -2.5 | -1.9 | 1.0 (n=3) | 2.0 | no |
| last_seen_no_model | days 42-46 | -12.9 | -27.6 | -9.1 | -16.5 | 5.6 (n=3) | 11.3 | yes |
| last_seen_no_model | pooled | -5.4 | -15.0 | -5.5 | -8.6 | 3.2 (n=3) | 6.4 | yes |
| ACE_as_published | days 24-28 | -27.9 | -22.6 | -50.0 | -33.5 | 8.4 (n=3) | 16.8 | yes |
| ACE_as_published | days 42-46 | -19.4 | -17.2 | -36.4 | -24.3 | 6.1 (n=3) | 12.1 | yes |
| ACE_as_published | pooled | -24.3 | -20.0 | -43.8 | -29.4 | 7.3 (n=3) | 14.7 | yes |
| ACE_as_published [ACE_fixed] | days 24-28 | -25.6 | -25.8 | -25.0 | -25.5 | 0.2 (n=3) | 0.5 | yes |
| ACE_as_published [ACE_fixed] | days 42-46 | -19.4 | -24.1 | -18.2 | -20.6 | 1.8 (n=3) | 3.6 | yes |
| ACE_as_published [ACE_fixed] | pooled | -23.0 | -25.0 | -21.9 | -23.3 | 0.9 (n=3) | 1.8 | yes |
| incremental_edits | days 24-28 | -30.2 | -29.0 | -47.5 | -35.6 | 6.0 (n=3) | 11.9 | yes |
| incremental_edits | days 42-46 | -41.9 | -13.8 | -27.3 | -27.7 | 8.1 (n=3) | 16.3 | yes |
| incremental_edits | pooled | -35.1 | -21.7 | -38.4 | -31.7 | 5.1 (n=3) | 10.2 | yes |
| last_seen_no_model [first illness deleted] | days 24-28 | +7.0 | -3.2 | -5.0 | -0.4 | 3.7 (n=3) | 7.5 | no |
| last_seen_no_model [first illness deleted] | days 42-46 | -12.9 | -27.6 | -9.1 | -16.5 | 5.6 (n=3) | 11.3 | yes |
| last_seen_no_model [first illness deleted] | pooled | -1.4 | -15.0 | -6.8 | -7.7 | 4.0 (n=3) | 7.9 | no |
| ours_told_the_night_before | days 24-28 | -2.3 | -6.5 | -27.5 | -12.1 | 7.8 (n=3) | 15.6 | no |
| ours_told_the_night_before | days 42-46 | -9.7 | -17.2 | +9.1 | -5.9 | 7.8 (n=3) | 15.7 | no |
| ours_told_the_night_before | pooled | -5.4 | -11.7 | -11.0 | -9.3 | 2.0 (n=3) | 4.0 | yes |

## Smallest gap this setup separates (two standard errors of the paired difference, observed spread)

| method vs last_seen_no_model | slice | 2 SE days 24-28 | 2 SE days 42-46 | 2 SE pooled |
|---|---|---|---|---|
| ACE_as_published | all | 7.3 | 2.4 | 4.5 |
| ACE_as_published | spell-1 mover | 13.0 | 15.1 | 14.1 |
| ACE_as_published | both-spell | 16.7 | 21.8 | 19.3 |
| ACE_as_published [ACE_fixed] | all | 5.6 | 2.8 | 1.4 |
| ACE_as_published [ACE_fixed] | spell-1 mover | 3.3 | 4.3 | 1.3 |
| ACE_as_published [ACE_fixed] | both-spell | 2.0 | 7.6 | 4.7 |
| incremental_edits | all | 3.8 | 4.8 | 2.0 |
| incremental_edits | spell-1 mover | 14.9 | 8.2 | 11.4 |
| incremental_edits | both-spell | 11.6 | 25.7 | 16.5 |
| last_seen_no_model [first illness deleted] | all | 2.9 | 0.0 | 1.5 |
| last_seen_no_model [first illness deleted] | spell-1 mover | 2.6 | 0.0 | 1.4 |
| last_seen_no_model [first illness deleted] | both-spell | 5.7 | 0.0 | 3.3 |
| ours_told_the_night_before | all | 6.5 | 5.3 | 2.4 |
| ours_told_the_night_before | spell-1 mover | 15.7 | 7.4 | 5.5 |
| ours_told_the_night_before | both-spell | 14.8 | 8.6 | 5.1 |
| the_log_and_notes_about_the_routine | all | 1.5 | 1.9 | 1.5 |
| the_log_and_notes_about_the_routine | spell-1 mover | 0.8 | 2.4 | 1.6 |
| the_log_and_notes_about_the_routine | both-spell | 2.0 | 11.3 | 6.4 |

## Notes from the loader
- prior_only_no_notes: not in the 50-day run (no cell directory)
- claim_store_told_if_it_was_right: not in the 50-day run (no cell directory)
- a_small_working_memory_and_an_archive: not in the 50-day run (no cell directory)
- log_only: not in the 50-day run (no cell directory)
- the_log_only: not in the 50-day run (no cell directory)
- ACE_as_published [ACE_rerun] hh_s2_t03: identical to the original ACE_as_published cell on all 1176 rows (rooms opened and found_at_step), a cache replay; left out of the tables
- ACE_as_published [ACE_rerun] hh_s32_t03: identical to the original ACE_as_published cell on all 1176 rows (rooms opened and found_at_step), a cache replay; left out of the tables
- ACE_as_published [ACE_rerun] hh_s48_t03: incomplete, days 1-18 only (430 questions); it does not reach the return windows and is left out

## A recency-weighted last-seen baseline: not in the run, and what it would take

No cell in any wave implements a recency-weighted last-seen. `last_seen_no_model` keeps one entry
per room, newest first, and dedupes before picking its second and third rooms
(`src/self_improve/search_driven.py:635-694`, questions_answered.md section 15). A weighted
version would score each room by, for example, the sum over past sightings of the object in that
room of a decay in the time since the sighting, and open rooms in score order.

What it needs as input, per question: every sighting of the asked object before the question
time, each with its room and its time. That is exactly the stream the methods see
(`eyes.sightings_of(object_id)`, section 7), and it IS stored in every cell directory:

- `<cell>/looks.jsonl`: one `kind == "look"` row per room opened, with `day`, `time`, the room
  opened, and a `sightings` list whose entries carry `observation_id`, `object_id`, `object_class`,
  `place_id`, `room`, `day`, `time`. Present for all 15 cells of the original wave, the 3 ACE_fixed
  cells and the 3 first-illness-deleted cells (55 to 134 MB each).
- `<cell>/searches.jsonl`: per question, `question_id`, `object_id`, `day`, `time`, `true_place`,
  `true_room`, and the rooms the arm opened. The bank
  (`results/self_improve/varied_homes/all_generated_v2_twice/banks/<household>.jsonl`) has the
  true place of every object at any time.

So the first guess of a weighted baseline can be computed offline, with no model, from the
stored logs: take an arm's `looks.jsonl`, keep sightings with time before each question's time,
score rooms, compare the top room with the row's `true_room`. The caveat is that this is an
off-policy estimate. The sighting stream is produced by the arm's own room choices (a room
opened for one object records every object in it, section 5), so after the first question on
which the weighted rule opens a different room from last-seen, its own log would diverge from the
one being replayed. On the first-guess measure this is a second-order effect for a rule close to
last-seen, but it is not the number a real cell would give.

The exact number needs no model either, only the simulator: `last_seen_no_model` is a few lines
of Python in `search_driven.py`, and
`results/self_improve/paper/scripts/last_seen_without_the_first_illness.py` already shows the
pattern (it patches `_remember_where_it_was_seen` in-process and reruns the arm on the 50-day bank
with no model call anywhere; its `arm.json` records 0 model calls and 2.7 to 4.1 seconds per
household for all 49 days). A weighted chooser would patch `_the_next_room_it_was_seen_in` the same way. Either
route is a CPU job; the on-disk logs are enough for the approximate one, and the bank plus
simulator for the exact one.

## Files

- Script: `/home/oliver/robot/dynamic_home_eqa/coordination/study1_from_existing_runs.py`
- Raw output: `/home/oliver/robot/dynamic_home_eqa/coordination/study1_from_existing_runs.raw.md`
- Inputs: listed in the script's docstring and in "What was read" above.
