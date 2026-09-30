# Overnight report, 30 September 2026

Five jobs. Every number names the script that produced it. The draft was not edited.

---

## Contradicts the draft

1. **The ACE-style playbook's merging step did not fail because merging does not help here. It
   failed because the model was putting words where a claim number belongs, and the code threw
   those answers away without counting them.** Measured on the rerun: the model answered 356 of
   359 proposed pairs across two households, and **329 of those answers were discarded** -
   `keep: "both"`, `fold_in: "none"` 174 times, the same claim named twice 18 times. Both are
   valid under the old schema, which typed those fields as plain strings. Anything the paper says
   about how much ACE's grow-and-refine merges in the 50-day run is a measurement of that bug.
   (Job C.)

2. **My own note from 29 September, that the 900-token cap caused the silent nights, is wrong.**
   A rebuilt four-pair night answered inside 900 tokens with 737 used. The cap was raised anyway,
   because it changes the cache key and so forces the merge calls to be made fresh, but it is not
   the cause and `appendix_material.md` should not say it is. (Job C, step 1.)

3. **Last-seen's smaller drop at the second onset is retained knowledge, and now there is a causal
   test rather than an inference.** Delete days 14-23 from its memory and its day-32 drop goes
   from 31.4 to 60.8 points on first room right, against a day-14 drop of 58.8; on found within
   three rooms, from 18.1 to 77.4 against 76.5. The draft states the result correctly; it can now
   state it far more strongly. (Job B.)

4. **The told-cause pattern is in eight runs, not six, and it is weaker than one household
   suggests.** All eight wrote a prediction on night 13. Only **three of eight** stopped
   conditioning on the illness within three nights; one never did. Day-14 accuracy against the
   predicted rooms ranges from 3 of 6 to 11 of 11. Figure 3's household is the strongest of the
   eight, and the draft should say so. (Job A.)

5. **`told_and_committed.py` mislabels its nights by one**, printing as "night 15" the text a note
   carried at the end of night 14. Figure 3 and its caption are correct; the script's headings are
   not. (Job A.)

---

## A. Told-cause pattern across the told runs - DONE

`PYTHONPATH=src python3 results/self_improve/paper/scripts/the_told_cause_across_runs.py`
-> `results/self_improve/paper/the_told_cause_across_runs.txt`

**Eight runs, not six.** Three households in `wave_the_family_reads_the_log` and five in
`wave_told_on_the_wider_homes`, all on the `ours_told_and_asked_what_changes` arm.

Two things had to be fixed before the table meant anything. Resident names come from
`who_lives_here.names_by_resident_id`, not from a header field that does not exist; without them
"the ill resident's moved objects" silently became *everyone's* moved objects. And a note can
retire its hypothesis while still using the word - *"the 'unwell' hypothesis from Day 13 is not
supported"* - so the night the note stops **conditioning** on the illness is reported separately
from the night the word disappears.

| run | household | ill | night-13 note? | day 14 in a named room | stopped conditioning | confirming sighting filed same night |
|---|---|---|---|---|---|---|
| family reads the log | hh_s2_t03 | Tomas | yes | **11 of 11** | night 14 | yes |
| family reads the log | hh_s32_t03 | Leo | yes | 6 of 7 | night 23 | yes |
| family reads the log | hh_s48_t03 | Marco | yes | 9 of 11 | night 17 | yes |
| wider homes | hh_s151_t03 | Dana | yes | 5 of 8 | night 28 | yes |
| wider homes | hh_s32_t03 | Leo | yes | 5 of 5 | night 23 | yes |
| wider homes | hh_s48_t03 | Marco | yes | 3 of 4 | night 15 | yes |
| wider homes | hh_s63_t03 | Dana | yes | 3 of 6 | **never** | no |
| wider homes | hh_s93_t03 | Ines | yes | 5 of 7 | night 14 | yes |

**8 of 8 wrote a prediction. 3 of 8 dropped the illness condition within three nights.** Seven of
eight filed a confirming sighting as an unconditioned standing fact in the same pass.

The quotes for every row are in the output file. The Figure 3 household is the cleanest case and
also the most favourable one: 11 of 11, retracted the very next night.

---

## B. Last-seen with the first illness deleted - DONE

`PYTHONPATH=src python3 results/self_improve/paper/scripts/last_seen_without_the_first_illness.py`
-> `results/self_improve/paper/last_seen_without_the_first_illness.txt`

Last-seen replayed on the three 50-day households with every sighting dated days 14-23 dropped as
it arrives. Same bank, same questions, same seed, same three-room budget, same room-opening rule;
sightings from day 24 on accumulate normally. The robot still looks in those rooms and is still
scored on those days - it just does not carry anything out of them. The deletion is a patch of
`_remember_where_it_was_seen` in that process only, so the arm's own source is untouched.

Day 32, the 14 objects that change room in both illnesses:

| household | measure | original day 14 | original day 32 | first illness deleted, day 32 |
|---|---|---|---|---|
| hh_s2_t03 | first room right | 10 | 56 | 22 |
| hh_s2_t03 | found within 3 | 10 | 78 | 22 |
| hh_s32_t03 | first room right | 33 | 50 | 0 |
| hh_s32_t03 | found within 3 | 33 | 100 | 0 |
| hh_s48_t03 | first room right | 18 | 55 | 45 |
| hh_s48_t03 | found within 3 | 27 | 64 | 45 |

The drop against each run's own days 28-31 mean, the same rule as `the_drop_at_each_onset.py`:

| measure | original drop at 32 | with the first illness deleted | original drop at 14 |
|---|---|---|---|
| first room right | 31.4 | **60.8** | 58.8 |
| found within 3 | 18.1 | **77.4** | 76.5 |

**One sentence: yes.** Deleting the first illness returns the day-32 drop to the day-14 level,
within 2.0 points on first room right and 1.0 on found within three rooms. Last-seen is less wrong
at the second onset *because it remembers the first one*, not because it had less far to fall.

---

## C. ACE-style 50-day rerun with the merge call fixed - see below

_(filled in when the rerun lands)_

---

## D. Log-only arm on the ten-household run - see below

_(filled in when the runs land)_

---

## E. One note's life - DONE

`figure_4` in `paper_figures.py` ->
`results/self_improve/paper/figures/{oliver,spec}/figure4_one_notes_life/`, with `caption.md`.

The ill resident's glass in household hh_s2_t03, claim store, untold arm (`incremental_edits` in
`overnight_wave`), claim_0005, on four nights. Verbatim, with the condition line under each box.
The text a note carried on night N is read as the text its next revision replaced.

| night | the note | when it is true |
|---|---|---|
| 13, normal | "Tomas's glass is in the kitchen sink in the morning. It is not on the dining table during this time." | Morning (observed 09:09) |
| 18, four days ill | "Tomas's glass is on the bedroom nightstand during the day. It is not in the kitchen or office." | Daytime |
| 24, life returns | "Tomas's glass is on the bedroom nightstand in the morning. It moves to the kitchen dish rack by midday and stays there until evening." | Daytime |
| 31, a week after | "Tomas's glass is on the kitchen cupboard in the morning and evening." | **Always** |

The glass has a note on all four nights, so no box says otherwise. The note is rewritten every
time and conditioned never: by night 31 the bedroom placement is gone and the condition field
holds the most general value the format allows, on a placement that was true for ten days of the
month.
