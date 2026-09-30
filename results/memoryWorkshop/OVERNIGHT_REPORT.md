# Overnight report, 30 September 2026

Five jobs. Every number names the script that produced it. The draft was not edited.

---

## Contradicts the draft

1. **Every number the draft gives for the ACE-style playbook on the 50-day run was produced with
   its merging step silently broken.** The model was putting words where a claim number belongs -
   `keep: "both"`, `fold_in: "none"` - in fields typed as plain strings, and the handler dropped
   those answers without counting them: **329 of 356 answers discarded** across two households.
   Fixed with an enum of the real claim ids and rerun: **0 discarded**. The draft's
   **first-room-right** numbers for that arm come out identical, so Table 2's first-room-right
   block is safe; **found within three rooms** moves 11 points in Table 2 and 23 in Table 3, both
   towards zero, and the onset drops become 66 and 63 rather than 53 and 55. (Job C.)

   **The paper's conclusion about ACE survives, and improves.** With the fix the model returns
   396 rejections against 26 merges: asked in a currency it can answer in, it says the pairs are
   *different notes*. So ACE's grow-and-refine does little here for a defensible reason rather
   than because of a bug - which is a better sentence for the paper than the one it has.

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

5. **Writing notes on top of the raw record buys nothing measurable.** A new log-only arm - the
   control's search-time prompt, the object's raw log, an empty notes block, no nightly write -
   scores 85.2 / 95.9 against log-and-notes' 85.6 / 96.6 over all ten households. The difference
   is -0.4 and -0.7, both inside their noise floors, both under two standard errors, sign 5 of 10.
   The draft's second finding survives but its mechanism changes: the record is the whole of it.
   (Job D.)

6. **`told_and_committed.py` mislabels its nights by one**, printing as "night 15" the text a note
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

**hh_s93_t03 is the same story, independently, and would make a second panel if one is wanted.**
Night 13: *"Ines is unwell and staying home. Expect her to be in bedroom_1 or living room during
the day, not the office."* Day 14: 5 of 7. Night 14, the note becomes *"Ines is working in the
office during the day... Day 14: office (11:48)"* - one sighting, and the hypothesis is gone. In
the same pass it files *"Ines's water bottle moves between kitchen dish rack (morning) and
bedroom_1 nightstand (day/evening). Day 14: dish rack (08:22), nightstand (09:33-16:31)"* - the
bedroom nightstand through the working day is the illness, recorded as a rule about ordinary life.
That is Figure 3's mechanism in a different household with a different resident and a different
object.

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

## C. ACE-style 50-day rerun with the merge call fixed - DONE

### Step 1: the cap is not the cause

`scratchpad/cap_test.py` rebuilt a four-pair night from the household that was silent from night 1
(`hh_s32_t03`, night 20, 48 live claims) and sent it to the server. It answered inside
`max_tokens=900`, using **737 completion tokens**, parsed, four verdicts. So the cap never bound
and the value recorded on 29 September as the likely cause is wrong.

The cap was raised to **3,000** anyway, for one reason: `max_tokens` is part of the response
cache key, so raising it is what forces a rerun to make the merge calls fresh instead of replaying
them.

### Step 2: no other arm shares this call

`merge_what_says_the_same_thing` is called from one place, under `as_published=True`. The claim
store and log-and-notes have **no merge step at all** - not a silent one, none - so there are no
silent nights to count for them.

### Step 3: the real cause, found by counting what the handler threw away

The handler had a bare `continue` for any returned merge whose `keep`/`fold_in` was not a claim in
the store. Nothing was recorded, so "the model answered and we discarded it" and "the model never
answered" looked identical from outside. I added `n_returned_by_the_model`, `n_unusable` and the
reason for each discard, and reran.

| household | nights | pairs proposed | answered by the model | merged | rejected | **discarded** | nights with no verdict |
|---|---|---|---|---|---|---|---|
| hh_s2_t03 | 50 | 163 | 160 | 5 | 18 | **137** | 35 of 43 |
| hh_s32_t03 | 50 | 196 | 196 | 2 | 2 | **192** | 48 of 49 |

**The model answered 356 of the 359 pairs it was shown. 329 of those answers were thrown away.**
The reasons, counted: **174** named a claim that is not in the store, **18** named the same claim
twice. The values it actually returned were `keep: "both"`, `fold_in: "none"` - it answered the
question in words, in a field typed as a plain string, which makes that schema-valid.

The fix is the one every other schema in this project already uses for a field that must name
something real: `merge_schema()` now builds an **enum of the claim ids in the prompt**, so a word
cannot be returned at all, and the prompt says the two must differ. A head-to-head test on one
reconstructed prompt returned usable ids under both schemas, so the failure is prompt-dependent;
the enum's value is that it makes the bad answer unrepresentable rather than merely unlikely.

### Step 4: two reruns

Both on the same three households, 24 questions a day, same banks and seed, otherwise identical.

- `wave_the_second_illness_ACE_rerun` - raised cap, old schema. Two households finished and are
  the table above. The third was stopped after 17 of 49 days: it was running at about ten minutes
  a day under contention and would not have finished, and its value was diagnostic only, which the
  first two already gave.
- `wave_the_second_illness_ACE_fixed` - the enum. Launched 00:59.

### Step 5: the tables

`WAVE_50=<wave>/cells PYTHONPATH=src python3 results/self_improve/paper/scripts/the_rerun_tables.py`
produces Table 2, Table 3 and the merge audit for any wave; it reproduces the draft's published
values exactly on the original wave, including the never-found counts, which is the check that it
can be trusted on a rerun. The drops, the first-question numbers and the recovery days come from
`the_drop_at_each_onset.py` and `the_first_question_of_the_day.py`, which now honour `WAVE_50` too.

### What the fix changed

`wave_the_second_illness_ACE_fixed`, all three households, finished 05:21. Old beside new for
every number. **The other three arms are not in the rerun wave and come from the original one**,
which makes these mixed comparisons; `paper_data.rows` falls back for them and every table marks
the rows it fell back on.

**The merging step.** The enum did exactly what it was for: nothing is discarded any more.

| | old schema (2 households) | fixed (3 households) |
|---|---|---|
| pairs proposed | 359 | 517 |
| answered by the model | 356 | 424 |
| **merged** | **7** | **26** |
| **rejected** | **20** | **396** |
| **discarded** | **329** | **0** |
| nights asked with no verdict | 83 of 92 | 24 of 136 |

**But the conclusion about ACE survives the fix, and for a better reason.** Merges per household
go 5 and 2 under the old schema, 6, 1 and 19 under the fixed one. What the fix mostly revealed was
**rejections**: the model, asked in a currency it can answer in, says these pairs are *different
notes* 396 times out of 422. ACE's grow-and-refine really does almost nothing on this task - not
because the call was broken, but because the pairs an embedding ranks as most alike are, in this
household, notes about different objects. The old numbers were produced by a bug; the new ones say
the same thing honestly.

**Table 2, the ACE-style playbook row** (14 objects, day 14 to 32):

| measure | draft | fixed |
|---|---|---|
| found within 3 | 10->44, 83->25, 91->45, mean **-23.1**, 2 SE 58.0 | 10->33, 83->25, 55->55, mean **-11.7**, 2 SE 48.6 |
| first room right | 0->11, 17->0, 9->27, mean +4.2, 2 SE 21.3 | 0->11, 17->0, 9->27, mean +4.2, 2 SE 21.3 - **identical** |
| objects never found | 11 -> 14 | 15 -> 14 |

**Table 3, the ACE-style playbook row** (22 objects, found within 3): draft 25->62, 91->17,
91->50, mean **-26.2**, 2 SE 65.6; fixed 25->54, 91->50, 55->58, mean **-2.8**, 2 SE 40.8.

**The four onset drops** (first room right, against each method's own four preceding days):

| | draft | fixed |
|---|---|---|
| day 14 | 53.1, 2 SE 20.3 | **65.9**, 2 SE **8.2** |
| day 32 | 54.9, 2 SE 46.0 | **62.9**, 2 SE **18.8** |
| pre-onset baselines | 61.7 and 67.7 | **74.4 and 75.7** |

The arm is better *between* illnesses after the fix and falls further at each onset. Section 3.2's
sentence - the summary-only memories drop as far the second time as the first - holds: 65.9 then
62.9, and the two-standard-error bands are less than half what they were.

**First question of the day, before that day's looking can help** (unfiltered form, 13 and 11
object-days): day 14 first room right 8.3 -> **15.0**, found within 3 60.0 -> **53.3**; day 32
21.7 -> **20.0** and 61.7 -> **60.0**.

**Recovery inside the first illness** (days until back within ten points of the pre-onset mean,
per household): 1, 2, 1 -> 1, 2, 2. Inside the illness in every household, both ways.

**Figure 2 regenerated with the new arm, no drop annotations**:
`results/self_improve/paper/figures/{oliver,spec}/figure2_both_illnesses_ACE_fixed/`. The legend
reads "ACE-style playbook", matching the text. The old figure is untouched beside it.

### What this means for the draft

The ACE row's **first-room-right** numbers do not move at all, so Table 2's first-room-right block
and Section 3.2's "53 and 55" for the playbook are the only places that need touching - and they
become 66 and 63. The **found-within-three** numbers do move, by 11 points in Table 2 and 23 in
Table 3, both towards zero. Neither reverses a claim. What has to change is the appendix's account
of the merging step, which currently describes a mechanism that was being thrown away.

---

## D. Log-only arm on the ten-household run - DONE, all ten

`PYTHONPATH=src python3 results/self_improve/paper/scripts/log_only_row.py`
-> `results/self_improve/paper/log_only_row.txt`

A new arm, `log only, no notes`: the model chooses rooms from the control's search-time prompt,
with the object's raw sighting log present and the notes block empty, and **never writes a note**.
Ten households, 31 days, 8 questions a day, same banks and seed as Table 1. Implementation: a new
way of writing in `memory_notes`, membership of `THE_LOG_AND_THE_ROUTINE_FAMILY` so it reads the
log, and a night that returns without calling anything. The guard that every night goes through the
search-driven day renderer is exempted for this arm by name rather than weakened.

**All ten households finished.** The Table 1 row, 2,480 questions per method:

| method | first room right | found within 3 |
|---|---|---|
| log and notes | 85.6 | 96.6 |
| **log only, no notes** | **85.2** | **95.9** |
| last-seen | 82.1 | 95.0 |
| claim store | 77.0 | 86.9 |

Paired within household, 2 SE across the ten, floors 1.9 and 2.2:

| difference | first room right | found within 3 |
|---|---|---|
| log only - log and notes | -0.4, 2 SE 1.9, sign **5 of 10** | -0.7, 2 SE 2.0, sign **5 of 10** |
| log only - last-seen | +3.1, 2 SE 3.4, sign 8 of 10 | +0.8, 2 SE 2.0, sign 7 of 10 |
| log only - claim store | **+8.2, 2 SE 3.9, sign 9 of 10, CLEARS** | **+9.0, 2 SE 3.7, sign 10 of 10, CLEARS** |

**Plainly: log-only is inside the noise floor of log-and-notes on both measures.** The difference
is 0.4 and 0.7 points, both under their floors (1.9 and 2.2), both under two standard errors, and
the sign is 5 of 10 - a coin flip. Writing a note every night, on top of the record the model can
already read, buys nothing measurable here.

Two consequences worth stating carefully:

- The paper's second finding - *"Giving the same summaries the raw sighting record closes the
  gap"* - survives, but its mechanism changes. On this evidence the record is the whole of it. An
  arm that keeps the record and writes nothing does as well as the arm that keeps both, and both
  beat the claim store by 8 to 9 points.
- Log-only against last-seen is +3.1 and +0.8, neither clearing - the same shape as
  log-and-notes against last-seen (+3.5 / +1.5). So the model reading the record is not reliably
  better than the rule walking back through it either.

This is the arm the Limitations section says was wanted and not run: *"An arm that reads the log
without notes would separate the value of the summaries from the model's use of the log; we did
not run it."* It is run now, on all ten households.

**The Figure A1 line.** Added, from `results/self_improve/wave_log_only/cells`; everything else
about it is that figure's wave. Days 10-13 **81.0**, day 14 **35.2**, day 24 **49.6**, against
log-and-notes 85.3 / 34.0 / 63.5 and last-seen 81.6 / 33.5 / 42.2. On the figure the log-only line
tracks log-and-notes through the whole illness and both climb back faster than last-seen. The
`oliver` three-line version now shows the three arms the ablation is about - last-seen, log only,
log and notes - and drops the reduced-ACE line; the `spec` version shows all six.

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
