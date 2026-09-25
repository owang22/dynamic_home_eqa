# Telling the note-writer what it saw, and not telling it what it will be asked

2026-09-24. Patrol construction (one room a day at 13:00, fixed fair rotation, day-0
walkthrough, 8-line read budget). Superseded as a *configuration* by the search-driven
job, which carries the same two settings; kept because three of the findings below do
not depend on how the looks were chosen.

**No accuracy was measured in this arm.** The answering pass was released before any
cell finished, so there are zero `held_out_answers.json` files under
`results/self_improve/frozen_memory_rich_looks/`. Every number here is about what the
notes CONTAIN. Anyone who needs accuracy has to run it.

## What was built

Two settings in `src/self_improve/study_settings.py`, each defaulting to the behaviour
every number before today was measured with, threaded through `write_the_notes.py`:

| setting | default | True/False means |
|---|---|---|
| `tell_the_model_everything_it_saw` | `False` | `True` renders every sighting and absence of a look to the note-writer; `False` filters the description to the objects the robot is quizzed on |
| `name_the_objects_it_will_be_quizzed_on` | `True` | `True` puts "The things the robot is asked about: ..." in the nightly prompt, and the count of them in the read-budget sentence; `False` replaces both with "someone will ask the robot where a thing in this home is ... anything in this home may be asked about" |

`--tell-the-model-everything-it-saw` and `--do-not-name-the-quizzed-objects` on
`compare_the_two_memory_formats`. Both defaults are frozen: four other jobs import
these modules, so the arms here pass both explicitly by keyword rather than relying on
them. **The search-driven job is now the consumer of both settings.**

## What is on disk

- `results/self_improve/memory_factor_rich_looks/` — rich looks, quiz list still named.
  10 households x 2 formats, complete: 29 nights each (days 0-28), 80 frozen snapshots
  at days 13/16/23/28, every one with `written_up_to_day` equal to the day in its name,
  0 model-call failures in 580 nights. The look streams are byte-identical to
  `memory_factor_v1`'s, so the sweeps are paired on the same evidence and differ only
  in the words the writer was shown.
- `results/self_improve/memory_factor_rich_looks_no_quiz_list/` — rich looks, quiz list
  NOT named. 3 households (s0, s5, s9), **wholesale rewrite complete** (all four
  snapshots). The incremental arms were killed at days 3-4 and are partial: there is no
  claim-store number for this condition.
- `results/self_improve/what_the_notes_mention_day23.json` and
  `results/self_improve/count_what_the_notes_mention.py` — the measurement below.
- `results/self_improve/frozen_memory_test_v1_full_window/frozen_memory_results_*.json`
  — rebuilt from the 40 cells actually on disk, no model calls. The previous files held
  only the 20 control-point rows while 20 day-23 cells sat beside them, so reading a
  summary as a manifest concluded the day-23 baseline did not exist. Old files renamed
  `*.CONTROL_POINT_ONLY_superseded.json`.

## 1. Richer descriptions barely change what is recorded — n=10 per format

Notes frozen at day 23, paired within household. Objects counted with
`write_the_notes.where_an_object_is_named` (the audited matcher, which knows the rewrite
arm writes "Nora's book" for `book_nora`), plus a looser class-word cross-check
reported separately.

**Wholesale rewrite:**

| | filtered looks | rich looks | paired diff |
|---|---|---|---|
| non-quizzed objects named, of 68.6 seen | **0.0** | **0.0** | 0.00, range [0,0] |
| non-quizzed class words (loose), of 54 | 0.0 | 0.0 | 0.00 |
| quizzed objects named, of 15.3 | 11.1 | 12.4 | +1.30, 2 se 3.89 |
| characters | 666 | 728 | +62, 2 se 91 |

Zero in all 10 households with filtered looks and all 10 with rich looks, and the loose
class-word count is zero in all 20 too, so the zero does not rest on the matcher.

**The claim store is the exception and it is small.** With filtered looks it also names
zero non-quizzed objects in all ten households; with rich looks it moves off zero in
**3 of 10** (s3: 6 objects, s5: 7, s6: 1), mean +1.4 of 68.6, 2 se 1.72 -- which does
**not** clear the two-standard-error bar, so this is a hint and not an effect. The
direction is at least unambiguous, because the filtered side is exactly zero in all ten.
Its quizzed-object count and length do not move (14.3 -> 14.1 named, 3,577 -> 3,428
characters). So the format that is under no length pressure at write time does use a
little of the extra context; the summariser uses none.

Meanwhile the writer was reading 4-5x as much: the day's look
description goes from 936 to 4,476 characters on a typical day and up to 13,944 on the
biggest, and the biggest household's look stream holds 103 distinct objects.

The prompt explains it. It also contained the line "The things the robot is asked
about: <13 ids>", and one rich summary answers in its own words: *"No items from the
asked list were found in the living room or storage during the 13:00 check."*

## 2. The quiz list is the lever — n=3, and the bar is the spread, not 2 se

Same rich looks, enumeration removed. Wholesale rewrite at day 23:

| household | non-quizzed objects named | non-quizzed class words | quizzed objects named | characters |
|---|---|---|---|---|
| s0 | 0 -> 5 of 54 | 0 -> 11 of 49 | 11 -> 4 of 13 | 589 -> 579 |
| s5 | 0 -> 5 of 76 | 0 -> 27 of 60 | 14 -> 1 of 16 | 908 -> 874 |
| s9 | 0 -> 10 of 82 | 0 -> 12 of 58 | 18 -> 1 of 21 | 639 -> 852 |
| mean | 0 -> 6.7 | 0 -> 16.7 | 12.7 -> 2.0 | 712 -> 768 |

Three households is below the six where a two-standard-error bar means anything, so the
bar used here is that the effect is bigger than the spread: the smallest move is +5
non-quizzed objects, against [0,0] across the 20 wholesale cells that had the list (and
against the claim store's 0 to 7 in section 1). Every household moves the same way on all
three measures.

Note length barely moves. **Curation under a fixed read budget is zero-sum: the same
purse, spent on different things.** s0 at day 23, verbatim: *"Bedroom_2 desk holds
Nora's pencil case and sketchbook... Bedroom_1 desk holds Yuki's gym bag, laptop, and
pen... Kitchen cupboard holds Nora's bowl, mug, plate, and shared pan, pot, and snack
bowl."* No summary in either sweep that had the list ever named one of those things --
580 nights of wholesale rewriting, ten households in each of the two sweeps. (The rich
claim store did name a gym bag, in s5; see section 1.)

**What this means for every memory-format number in the study.** The enumeration is not
a prompt detail; it is the study telling the memory what it will be tested on. With the
list, the writer knows the query distribution in advance, which a deployed robot does
not. Numbers measured with it are about two ways of writing notes *when you already
know what you will be asked*. That does not invalidate them, it narrows them.

Predicted, not measured: with 1 to 4 of these households' 13 to 21 quizzed objects
named, accuracy at the day-23 freeze should fall hard. The number worth reporting is not
the fall but how much of it the naming ratio explains -- if accuracy falls by less than
2.0 against 12.7 named implies, the notes are carrying useful room-level structure about
objects they never name.

## 3. Residents are never recorded, in any condition — n=43 cells

No household's notes name a resident by identifier, in any of the three conditions -- 43
cells, every one zero -- and the word "resident" appears at all in 4 of the 43.

**Correction to the figure this arm started from.** The motivating note said residents
appear in only 2 look records. That is s0's number, not the study's: across the ten
households a resident is seen on 1 to 9 of each household's 30 look records, mean 4.8
(s0 2, s1 2, s2 5, s3 9, s4 6, s5 2, s6 1, s7 7, s8 8, s9 6). So there were 48
opportunities, and `describe_look_for_the_model` puts "People there: resident_1." into
the prompt in every condition, filtered or rich, because resident reporting was never
inside the filter. Not one of the 48 was written down.

That makes residents a curation result rather than the observation limit I first called
it, and it is the one result that survives removing the quiz list: s0, s5 and s9 had 2, 2
and 6 resident sightings in the no-list condition and still named none. Sparse evidence
is part of the story -- a resident is in view on about one look in six -- but it is not
the whole of it.

## 4. Repetition: a null, and a retraction — n=10

**Retracted.** I reported that rich looks made the rewriter stop revising, on s0's 0 of
29 nights identical to the night before going to 14 of 29. That was the extreme
household, not the effect. Across ten households the filtered arm already repeats
itself on 9.7 of 29 nights and the rich arm on 7.4, a paired difference of **-2.3
nights, 2 se 5.7** -- and the sign is the wrong way round for the story. Per household,
filtered -> rich: s0 0->14, s1 7->8, s2 13->4, s3 13->17, s4 10->10, s5 9->7, s6 5->8,
s7 19->0, s8 6->1, s9 15->5. s7 moves as far in the opposite direction as s0 does in the
favourable one. s0's 0 was the minimum of a distribution running 0 to 19, not a
baseline.

What survives is an exclusion, and it is wide: rich looks change the rewriter's
self-repetition by **no more than about 6 nights in 29, roughly 20 percentage points,
either way**. That rules out a large effect, not a small one. The claim store is flat on
the same bar: adds 23.3 -> 23.2, revises 67.4 -> 72.6 (2 se 7.6), nights with no edit at
all 11.0 -> 10.7.

## Caveats a reader needs

- The no-list arm moves two sentences, the enumeration and the count of quizzed objects
  in the read-budget sentence. They are one construct -- both hand the writer the test
  -- but it is one construct, not one sentence, and nobody has separated them.
- The claim store's forced-edit rule (`write_the_notes_incrementally`, `minItems: 1`)
  still fires on whether a look saw an **asked-about** object. That is in the schema,
  not the prompt, so even a no-list claim store is nudged to edit on exactly the nights
  that saw quizzed objects. A properly unconfounded claim-store arm has to deal with
  this; the wholesale arm has no such path.
- The strict object count refuses a bare class word on purpose, which is why the loose
  class-word count is reported beside it. Both are zero for all 20 wholesale cells that
  had the list, so that zero does not rest on the matcher. The loose count is zero for the
  three rich claim-store cells that DO name non-quizzed objects, which is expected: the
  claim store writes full identifiers, not class words.
- Another agent added a `wording` parameter to `rewrite_the_notes_wholesale` while these
  runs were in flight. It defaults to the wording used here, and these sweeps predate
  it, but a rerun should pin it explicitly the way the two settings above are pinned.
- Every figure here is at the day-23 freeze point under the 8-line read budget, patrol
  looking, with the day-0 walkthrough included in the stream.
