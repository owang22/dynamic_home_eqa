# Search-driven sensing: what a finished run must contain

Written **before** the run, so a run can be checked against this list rather than
against a clean exit. The dominant failure mode in this project is a run that looks
complete because everything it did do succeeded.

Harness: `src/self_improve/search_driven.py`. Outputs:
`results/self_improve/search_driven/<household>/<sensing_arm>/<how_memory_is_written>/`.

## The design, stated so the output can be checked against it

- **No patrol and no day-0 walkthrough.** Every observation comes from a search the
  robot made because it was asked a question. `cell.json` carries
  `there_was_no_patrol_and_no_warm_start: true`, and no look record may have
  `chosen_by` containing "the fixed schedule" or "walkthrough".
- **k = 3 rooms per question**, one at a time, stopping early on a find.
- **Answer**: the true place if found, otherwise the model's guess from an 8-line
  window of its notes (`LOCKED.read_budget_lines`, unchanged) **plus the rooms the
  failed search just ruled out**. A robot that has opened three rooms and not found
  the towel knows it is not in those three rooms. It does not favour an arm: all
  three rule out the same *number* of rooms, k = 3, they just rule out different
  ones, and that the memory-guided arm rules out better-chosen rooms is the
  hypothesis, not a confound. `ablation_the_notes_alone/` runs the identical thing
  with that list withheld, to price what the immediate search evidence adds.
- **Every search step is described to the note-writer in full**, by
  `describe_look_for_the_model(look, only_these_objects=None)` — every sighting,
  every resident, every absence, for all three sensing arms. One compaction that
  keeps a fact rather than a repetition: an absence is keyed on (object, room),
  stated once, and **carries how many times the day confirmed it** — "towel_nora
  was not anywhere in the kitchen (checked 4 times today)" — because one failed
  check and four failed checks are different grounds for concluding the towel has
  moved. Measured: 0.36–0.51 of the verbatim size, no fact lost. Both sizes are
  logged per night (`n_characters_of_look_description` and
  `n_characters_if_every_look_were_restated`).
- **The three sensing arms differ only in how the room is chosen.** Same budget,
  same stopping rule, same rendering, same answering prompt.

## Per cell, the file must contain

1. `cell.json` with `searches` of length ≈ 8 × 31 = **248** rows (fewer only where
   the bank has no answerable question that day), each carrying:
   `rooms_opened`, `n_rooms_opened`, `found_it`, `found_at_step`, `answered_from`,
   `answer_place`, `correct_place`, `correct_room`, `is_a_mover`,
   `times_seen_there_before`, `error_kind`.
2. `per_day.jsonl` with one row per day 0–31 (**32 rows**), each carrying
   `household, day, sensing_arm, how_memory_is_written, n_questions, n_scored,
   n_correct_place, n_correct_room, n_found, rooms_opened, room_visits,
   distinct_rooms, distinct_objects_observed,
   distinct_asked_about_objects_observed, distinct_residents_seen`.
3. `looks.jsonl` — one `look` row per room opened, with sightings and absences.
   Count must equal `sum(rooms_opened)` over `per_day.jsonl`, + 1 header row.
4. `notes.json` — non-empty. For **incremental edits**: at least one claim by the
   end of day 2, and `total_revised > 0` over the month. For **wholesale rewrite**:
   a non-empty newest summary.
5. `sanity_assay.json` with an empty `concerns` list, or a concern that is explained
   before any accuracy number is quoted.
6. `nightly` in `cell.json`: 32 rows. `model_call_failed` false on all but a handful.
   `n_characters_of_look_description` > 0 for every day that had a question.

## Checks that must pass before any number is believed

- **The day renderer landed.** `run_one_cell` raises if the note-writing prompt did
  not go through `the_day_in_words`. A cell that finished at all has passed this.
- **Night 1 produced edits** in the incremental arm. Measured 2026-09-24: with the
  explanation before the imperative this model replies `{"edits": []}` to a night
  with fresh sightings, which is a silently empty arm no accuracy number exposes.
- **`sanity_assay`** on the first cell, on the answers that came *from the notes*
  (found answers excluded — they are the world's answers, not the model's).
- **The arms got the same questions.** The question id lists must be identical
  across all six cells of a household; the sample depends on the bank alone.
- **Rooms opened ≤ 3 per question** and all distinct within a search.
- **`found_it` implies `correct_place`** — the robot saw the object where it was.
- **Days 1–13 must CLIMB.** With no day-0 walkthrough the settled fortnight is
  learned from scratch, so the settled period should show a rising slope. Flat and
  low means the robot never learned the ordinary routine, the disruption has
  nothing to break, and every later number is about noise — the failure the
  night-shift control was built to detect. `did_it_learn_the_settled_fortnight`
  reports the slope in accuracy points per day and the days 1–4 to 10–13 climb.
- **Two differences from the patrol runs, not one.** The search runs differ from
  `results/self_improve/memory_factor_v1/` in TWO ways at once — no priors and
  search-driven looking — so no one may compare the two sets naively. That sentence
  is in every `cell.json` under `how_this_differs_from_the_patrol_runs`.

## The numbers to report

Paired within household, clustered on **household, never on question**
(per-question error bars come out about four times too narrow).

- accuracy at **the right room** (primary) and **the exact shelf** (strict);
- **search cost**: mean rooms opened per question, and share of questions where the
  object was found within the budget;
- **accuracy by day, 0–31**, mover / non-mover slice, not one number for the run;
- **the three-way error split** from structured sighting records: never saw it
  there / saw once and did not record / saw repeatedly and did not record. Under
  the patrol this was 75% never-saw; the point of search is that it should fall.
- **the observation confound**, per household per day: room-visits, distinct rooms,
  distinct objects, distinct asked-about objects — for the search arms **and** for
  the patrol run at `results/self_improve/memory_factor_v1/`, so the ratio is one
  line rather than a late discovery. A patrol gives 1 room-visit a day; search at
  3 rooms × 8 questions gives up to 24.
- **accuracy against observation count**, not only against arm. The three arms
  share a budget, so: differ on accuracy but not on distinct rooms visited →
  choosing. Differ on both → the budget is doing the work, and we say so.

## The prediction, stated so it can be refuted

Memory-guided search should beat the fixed rotation on **search cost** more clearly
than on accuracy, because finding the object makes the answer correct whatever the
notes said. If accuracy differences vanish while search cost separates cleanly,
that is the finding. And the never-saw share should fall sharply; if it does not,
the sensing bottleneck is deeper than the patrol.
