# Checks on DRAFT_CorlMemoryWorkshop_1.pdf

Eighteen items from the editor's list, worked against the analysis outputs and the run data rather
than against any summary of them. Every number below names the script that produced it. Where a
number in the draft does not reproduce, it is reported here and not edited.

**The folder holds only the PDF.** There is no `.tex` and no `.bib` anywhere on this machine, so
items 13, 17 and 18 could not be carried out as edits. What could be prepared for them is at the
end.

---

## Summary: what needs changing in the draft

Six things. Two are wrong, four are imprecise.

1. **Table 1's caption is wrong.** "Each margin clears two standard errors across households and
   the noise floor" does not hold on first room right: last-seen over the claim store is +5.1
   against a 2 SE of 5.7, and over the ACE-style playbook +6.0 against 6.1. Neither clears. On
   found within three rooms all three do clear. (Item 1.)
2. **Table 1's caption names the wrong failing criterion.** "+3.5 / +1.5 points, which does not
   clear the floor" - +3.5 *does* clear the 1.9 floor. What it fails is 2 SE (4.2) and the
   all-household sign (9 of 10). +1.5 fails all three. (Item 1.)
3. **"Hiding the notes at search time costs about 30 points"** - it costs 23.5 on first room right
   and 21.1 on found within three rooms, comparing the claim store with notes hidden, which are
   the two arms that differ only in that. 30 is the gap to log and notes, a different comparison.
4. **Two different arms are both called "ACE-style playbook".** Table 1 and Figure 4 are
   `claim_store_told_if_it_was_right`; Table 2 and Figure 2 are `ACE_as_published`. They are
   separate implementations with three named differences (`memory_notes.py:102-108`). Appendix D
   half-says this. It should say it outright. The same applies to "MemGPT-style working memory",
   which in Table 1 is the 1,200-character variant.
5. **"Roughly 80 to 100 objects"** - measured, 76 to 104.
6. **The observation-budget range does not reproduce.** The draft says 9.0-10.7 rooms a day at 8
   questions and 25.6-30.5 at 24. Counting looks per day per household: 8.9 to 10.9 at 8 a day and
   26.5 to 31.0 at 24 for the methods the paper reports, and up to 16.9 and 34.2 for arms that
   search worse. Say which arms the range covers.

Everything else in the list checks out. Details below.

---

## Numbers to reproduce (items 1-5)

### 1. Table 1, and the per-household sign

`python3 results/self_improve/paper/scripts/table1_ten_homes.py` ->
`results/self_improve/paper/table1_ten_homes.txt`

Every value in Table 1 reproduces exactly: log and notes 85.6 / 96.6, last-seen 82.1 / 95.0, claim
store 77.0 / 86.9, ACE-style playbook 76.0 / 85.3, MemGPT-style 71.0 / 82.1, notes hidden 53.5 /
65.8, 2,480 questions per method (10 households x 31 days x 8, every household exactly 248).

The paired within-household differences, with 2 SE across the ten households and the floor:

| difference | first room right | clears? | found within 3 | clears? |
|---|---|---|---|---|
| last-seen - claim store | +5.1, 2 SE 5.7, sign 7 of 10 | **no** | +8.2, 2 SE 4.3, sign 10 of 10 | yes |
| last-seen - ACE-style playbook | +6.0, 2 SE 6.1, sign 7 of 10 | **no** | +9.7, 2 SE 6.1, sign 9 of 10 | yes |
| last-seen - MemGPT-style | +11.1, 2 SE 7.1, sign 8 of 10 | yes | +12.9, 2 SE 6.9, sign 10 of 10 | yes |
| log and notes - last-seen | +3.5, 2 SE 4.2, sign 9 of 10 | no | +1.5, 2 SE 2.0, sign 8 of 10 | no |

So the caption's claim holds on found within three rooms and fails on first room right for two of
the three summary-only memories. The body sentence built on the found-within-3 column - "The
last-seen lead ranges from 8 to 13 points on found within three rooms and holds in 10 of 10
households against the claim store" - is right (8.2 to 12.9; 10 of 10 against the claim store).

On the second point: the draft says log and notes' +3.5 / +1.5 "does not clear the floor". +3.5
clears the 1.9 floor and fails 2 SE and the sign test. +1.5 is under the 2.2 floor and fails all
three. The conclusion stands; the stated reason is wrong for one of the two numbers.

`results/self_improve/THE_MAIN_POINTS.md` carried the same error - "LastSeen - plain claim store
+5.1 / +8.2 both clear". **Fixed there on 2026-09-29**, with the 2 SE and the household sign
printed on every line so it cannot come back as a bare "clears".

### 2. The 8.6 / 9.7 gap, the 15.9% match, 57 vs 24, 95 vs 59, 96 seen / 62 found

`PYTHONPATH=src python3 results/self_improve/paper/scripts/why_it_adapts_faster.py`

- 8.6 / 9.7: 85.6 - 77.0 = 8.6 and 96.6 - 86.9 = 9.7. Both are unpaired table differences, which
  is what the sentence claims, so this is right.
- **15.9% level match**: confirmed, and identical to one decimal - last-seen 15.9%, log and notes
  15.9%, on the questions where neither had ever seen the object where it now is. **It is 20
  questions.** The draft says "on questions where neither has yet seen the object in its new
  place, log and notes and last-seen are level", which is fair, but 20 questions is worth a clause.
- **Day 14, 57% vs 24%**: confirmed. Found within three rooms, log and notes 57%, last-seen 24%.
  First room right that day is 27% and 21%, which is what "about equally often" refers to.
- **Days 15-17, 95% vs 59%**: confirmed, on "had already seen it there".
- **Claim store 96% seen, 62% found**: confirmed - but 62% is the **first-room-right** rate, not
  found within three rooms. Appendix C says "finds them only 62% of the time", and "finds" is the
  word the paper uses for found-within-three elsewhere. Change it to "gets the first room right
  only 62% of the time". The same applies to the 88% quoted for log and notes in that comparison.

### 3. The onset drops of Section 3.2

New: `PYTHONPATH=src python3 results/self_improve/paper/scripts/the_drop_at_each_onset.py` ->
`results/self_improve/paper/the_drop_at_each_onset.txt`

All four pairs reproduce, on the 14 objects that change room in both illnesses, three households,
each method against its own mean over the four days before that onset:

| method | draft | measured, day 14 | measured, day 32 |
|---|---|---|---|
| last-seen | 59 / 31 | 58.8 | 31.4 |
| log and notes | 57 / 29 | 57.3 | 29.2 |
| claim store | 51 / 48 | 51.3 | 47.8 |
| ACE-style playbook | 53 / 55 | 53.1 | 54.9 |

**The baseline window is days 10-13 and days 28-31**, four days each, the same four for every
method, and the object subset is the 14 both-illness room-changers. Both confirmed.

**What the draft does not say, and should.** The two-standard-error band on these drops, across
the three households, is 13.0 to 33.7 points at day 14 and 5.5 to 56.2 at day 32. The claim store's
day-32 drop of 47.8 carries a band of 56.2. Section 3.2 quotes eight numbers with no uncertainty
at all, and the sentence that saves it - "we read this as the direction of the effect rather than
its size" - is in Section 3.2's last paragraph and refers to Table 2. It should refer to these
numbers as well.

### 4. The 426 notes and the 170 / 142 / 114 breakdown

`PYTHONPATH=src python3 results/self_improve/paper/scripts/night31_audit.py` ->
`results/self_improve/paper/night31_audit.txt`

Confirmed. Claim store 170, log and notes 142, ACE-style playbook 114, total 426, over the ten
households on night 31. Within those: always 133, a time of day 238, a person home or away 12,
other 43. The MemGPT-style arm adds 27 more (453 across four arms) and is excluded from the figure
because it held 101 live notes against the claim store's 595.

### 5. The noise floor

`results/self_improve/three_prompts/the_rerun_noise_floor.json`

Confirmed, and the draft's description of it is accurate. Two arms - `control` and `told_unwell` -
have byte-identical prompts on **days 0-13**, so their difference over that window is rerun noise.
Mean absolute difference: 0.0190 on share-first-room-right (1.9 points) and 0.0219 on
share-found-within-budget (2.2). **Measured on 7 households.**

Two things to state if the floor is doing work in a caption: it is a **mean**, and the largest
per-household difference over that same window is 6.3 and 7.3 points; and it was measured on a
different run from the one it is applied to.

---

## Facts about the setup (items 6-9)

### 6. Seed, world trajectory and question schedule

Read from the cells, not the README. In both the ten-household wave and the 50-day wave, for every
arm of a given household: one bank file, `seed = 0`, and byte-identical question schedules and
ground truth. Hashing `(question_id, object_id, day, time)` over every arm of `hh_s2_t03` in
`overnight_wave` gives one hash for all seven arms; hashing `(question_id, true_place)` likewise.

The world cannot differ by arm: it is frozen in the household's question bank before any arm runs,
and the arm only chooses which rooms to open. Safe to assert in the paper.

### 7. What a room opening records about residents

A look records residents **by name**: `LookRecord.residents_seen`, filled at `looking.py:235` by
mapping resident ids through the household's display names, and rendered at `looking.py:459-460` as
`People there: Tomas.`

Where that reaches:

- **The nightly note-writing prompt of every note-writing arm.** One renderer,
  `describe_look_for_the_model`, feeds both note formats, so all of them see it. Confirmed in a
  rendered prompt: `results/self_improve/paper/appendix_material.md`, Section 3.
- **Not the search-time log.** `the_log_the_robot_reads.py` has no resident field.
- **Not the room-choice prompt.** `choose_where_to_look.py` never mentions people.
- Last-seen has no model call at all.

So the told-cause case does rest on something the arm genuinely saw. Verified end to end for the
household in Figure 3: the night-14 text of `claim_0022` is *"Tomas works from the office during
the day (seen 14:08)... The 'unwell' hypothesis from Day 13 is not supported by Day 14 activity."*

**Figure 3's nights are right.** `revision_history` stores, under `was`, the text a revision
replaced, so the text written on night N is the `was` of the revision dated N+1. Under that rule
the night-13 sentence, the office retraction and the glass note are nights 13, 14 and 14 - the
retraction and the glass note in the same pass, exactly as the caption says. (`told_and_committed.py`
prints these under the headings "night 15/16/17", which is off by one in the *script's labels*; the
figure and the caption are correct.)

### 8. Which object subset each figure and table uses

| where | subset | level |
|---|---|---|
| Table 1 | **all questions**, no subset at all - 2,480 per method | n/a |
| Figure 2 | the 14 objects whose commonest daytime room differs from settled in **both** illnesses | room |
| Figure 4 (first illness, ten households) | `the_movers` - objects whose commonest daytime **spot** differs during the first illness | spot |
| Table 2 | the same 14 as Figure 2 | room |
| Table 3 | all 22 objects that moved in the first illness | spot |
| Figure 5 | not an accuracy figure; notes naming an object and one of its illness-time rooms | room |

The editor's premise that Table 1 is a moved-spot table is not right - Table 1 pools every
question. Figure 2's caption does say "the 14 objects that change room in both illnesses" and
Table 2's does too. **Figure 4's caption says "the objects the illness moves", which does not say
spot-level**, and Table 3's says "all 22 objects that moved in the first illness", which also does
not. Those two are the captions to fix.

### 9. Does every method recover within the first illness in the 50-day run?

Measured as: days after the onset until the method is back within ten points of its own mean over
the four preceding days, same window as item 3.

At the first onset, first room right, per household: last-seen 1, 4, **13**; log and notes 1, 1, 1;
claim store 2, 3, 1; ACE-style playbook 1, 2, 1. On found within three rooms: last-seen 1, 5,
**10**; log and notes 1, 1, 1; claim store 2, 2, 1; playbook 1, 3, 1.

The illness runs days 14-23, so recovery inside it means nine days or fewer. **Every method in
every household recovers inside the illness except last-seen in the third household**, which takes
13 days on first room right and 10 on found within three. The Discussion's "every method adapted
within the first illness" is true of the ten-household run and needs a one-clause exception for the
50-day run, or a statement that it is said of Figure 4.

One caveat on the measure: a method with a low pre-onset mean has a low bar. The claim store's
baseline over days 10-13 is 57.6 against last-seen's 79.3, so "within ten points" is easier for it.

---

## The two extra analyses (items 10-12)

### 10. The first question about each object at each onset

New: `PYTHONPATH=src python3 results/self_improve/paper/scripts/the_first_question_of_the_day.py`
-> `results/self_improve/paper/the_first_question_of_the_day.txt`

**The strict version asked for has no power.** Requiring that no look earlier that day had already
seen the object leaves 2 to 5 object-days per method across the three households, and two of the
three households contribute nothing. The reason is structural: every room opening records every
object in the room, so answering a question about one object usually reveals several others.

The unfiltered version - the first question about each object on that day, whether or not it had
been seen - keeps 13 object-days at day 14 and 11 at day 32, and says something:

| method | day 14 first room right | day 32 | day 14 found within 3 | day 32 |
|---|---|---|---|---|
| last-seen | 23.3 | 36.7 | 23.3 | 85.0 |
| log and notes | 23.3 | 50.0 | 60.0 | 91.7 |
| claim store | 15.0 | 28.3 | 51.7 | 53.3 |
| ACE-style playbook | 8.3 | 21.7 | 60.0 | 61.7 |

On found within three rooms the two memories that keep the raw record gain +61.7 and +31.7 from
the first onset to the second, while the two summary-only memories gain **+1.6 and +1.7**. That is
the paper's Section 3.2 claim, on the first question of the day only, and it is if anything
sharper. It is 11 to 13 object-days, so it belongs in an appendix sentence, not a table.

### 11. The notes conditioned on a person being home

From the night-31 audit. **Twelve notes of the 426, and every one of them comes from a single
household (`hh_s151_t03`) and a single arm (the ACE-style playbook).** Their conditions, in full:
"Dana and Felix are at home" (x3), "Dana is at home" (x5), "Felix is at home" (x2), "Dana is at
home and Felix is working", "Felix is at home in the evening".

**The narrowed claim does not need a caveat; it needs strengthening.** None of those conditions
separates an ill day from a well one - the residents are at home on well days too, and the resident
who falls ill is not the one named in most of them. Together with "always" (133) and "a time of
day" (238), that is 383 of 426, **90%**, whose condition is true again the next day whatever the
resident's state. The editor's proposed subtitle, "most conditions hold on ill and well days
alike", is the right claim and is now on the figure.

### 12. Recovery speed, and whether "adapts faster the second time" can go in

**It cannot, on this measure.** Days until back within ten points of the pre-onset mean, first room
right:

| method | first onset | second onset |
|---|---|---|
| last-seen | 1, 4, 13 | 1, 1, 13 |
| log and notes | 1, 1, 1 | 2, 1, 1 |
| claim store | 2, 3, 1 | 3, 2, 1 |
| ACE-style playbook | 1, 2, 1 | 4, 2, 1 |

Almost everything is back inside one to four days at both onsets, so there is no room for a second
illness to be faster. The measure is too coarse: on 11 questions a day the day-to-day swing is
large enough to clear a ten-point bar by itself, and the methods with the lowest baselines have the
lowest bars. The paper's existing framing - the *depth* of the drop, not the speed of the recovery
- is the one the data supports. Leave "adapts faster the second time" out.

---

## Figures (items 13-16)

All figure sources are at `results/self_improve/paper/scripts/paper_figures.py`; the PDFs are under
`results/self_improve/paper/figures/oliver/`, each beside its caption.

- **13. Figure 1** - not ours. It is an illustration, not a generated figure, and no source file for
  it exists in this repository. Not done.
- **14. Figure 2, drop annotations** - **not done, deliberately, and it needs your call.** Those
  annotations were on the figure and you had them removed two days ago: *"for oliver fig2, you
  should not have text boxes that talk about the accuracy numbers. thats clutter"*. Putting them
  back reverses that. If you want them, say so and it is a two-line change; the numbers are in
  item 3 above.
- **14b / 16. Legend names** - done. A display-label layer now sits over the arm keys, so the
  legends read **last-seen**, **log and notes**, **claim store**, **ACE-style playbook** and
  **MemGPT-style working memory**, matching the draft's text. The two different ACE arms keep
  separate keys internally and share one label, which is what the draft does; see point 4 of the
  summary for why that needs saying in Appendix D.
- **15. Figure 5** - done. The red line above the axes now reads "most conditions hold on ill and
  well days alike", and the third bar is labelled "ACE-Style Playbook". The 426 count moves to the
  caption, which has been rewritten to match.

---

## Bibliography and compile (items 17-18)

No `.bib` and no `.tex` exist on this machine, so nothing could be filled in or compiled. The three
entries, fetched from the sources:

- **RoboMME-Interference**, arXiv:2606.22338, *RoboMME-Interference: Benchmarking Robot Memory
  Under Interference*. The arXiv page lists **one** author, **Soumil Rathi**. Submitted 21 June
  2026, v3 revised 26 August 2026. One author on a benchmark paper is unusual enough that it is
  worth a second look before it goes in.
- **MEM**, arXiv:2603.03596, *MEM: Multi-Scale Embodied Memory for Vision Language Action Models*.
  Authors in order: Marcel Torne, Karl Pertsch, Homer Walke, Kyle Vedder, Suraj Nair, Brian Ichter,
  Allen Z. Ren, Haohuan Wang, Jiaming Tang, Kyle Stachowicz, Karan Dhabalia, Michael Equi, Quan
  Vuong, Jost Tobias Springenberg, Sergey Levine, Chelsea Finn, Danny Driess. The draft currently
  credits it to "Physical Intelligence and VERIFY authors".
- **DynaMem**, *DynaMem: Online Dynamic Spatio-Semantic Memory for Open World Mobile Manipulations*,
  arXiv:2411.04999, 2024. Authors: Peiqi Liu, Zhanqiu Guo, Mohit Warke, Soumith Chintala, Chris
  Paxton, Nur Muhammad "Mahi" Shafiullah, Lerrel Pinto. Note the year is **2024**, not 2026.

Send the `.tex` and `.bib` and both remaining items can be finished.

---

## Found afterwards, and it affects Section 3.2 and Table 2

**In the 50-day run, ACE's grow-and-refine step returned almost nothing.** Over 150 nights and
three households, the embedding proposed 529 pairs and the model sent back a verdict on **33** of
them, merging **7** notes. On **126 of the 137** nights that proposed a pair, the reply produced no
verdict at all. The same code, on the same three households at 24 questions a day, run the day
before, was silent on 3 of 88 nights and merged 67 notes.

A likely cause, not confirmed: commit `b4207b7b3` (2026-09-26 20:49) raised that call's schema from
four merges to twelve and its `why` field from 200 characters to 600 and left `max_tokens=900`
where it was; a reply carrying several 600-character explanations does not fit, is cut off, and the
handler silently sets `merges = []`. The timing fits two of the three cells - the one that finished
before the commit answered on 9 of its 43 asked nights, the two that finished after it answered on
one night each - but it does not explain the first cell's own 9 of 43.

**What this means for the draft.** The arm Table 2, Figure 2 and Section 3.2 call the ACE-style
playbook had its merging step effectively switched off in that run. Its numbers are still a correct
measurement of the arm as it ran; what cannot be said is that they measure ACE's grow-and-refine.
Appendix D should say the step returned a verdict on 11 of 137 nights, or the run should be redone
with the cap raised. Full counts and the per-cell timing are in
`results/self_improve/paper/appendix_material.md`, Section 1.

**The "Differences from ACE" paragraph mixes the two ACE arms.** "Ours ranks pairs by embedding,
hands at most four pairs a night to the model, which decides whether they say one thing, and merges
by deterministic concatenation" - the embedding ranking and the model verdict are the 50-day arm;
the deterministic merge is the ten-household arm. No single arm does both. The ten-household arm
never proposed a pair at all in 320 nights: its merge sits behind a line budget that was never
reached, and the only joining it did was 22 uses of the deterministic backstop. Section 1 of
`appendix_material.md` now sets the two arms side by side and gives replacement wording.

## Smaller things found along the way

- Appendix A, "eleven kinds of object, including books, mugs, glasses, water bottles, chargers and
  tablets" - confirmed for the ten-household and 50-day runs. The eleven are book, charger, glass,
  glasses, medication, mug, notebook, razor, tablet, towel, water_bottle, and all six named are
  among them. **The five wider households use a different list of 21 kinds**, which is what makes
  them wider; if the sentence is meant to cover the whole study it needs a clause.
- **The simulator-dynamics paragraph** the draft leaves as a TODO is now written, from the
  generator and the two scenario files rather than from the README:
  `results/self_improve/paper/appendix_material.md`, Section 4.
- Appendix A, "Day 0 is a night with no questions" - confirmed; question days start at 1.
- Setting, "two or three residents, eight or nine rooms with about forty places between them" -
  confirmed: 2 to 3 residents, 8 or 9 rooms, 39 to 46 places.
  `PYTHONPATH=src python3 results/self_improve/paper/scripts/what_a_household_is_made_of.py`
- Figure 3's three quotations are **hard-coded constants** in `paper_figures.py` rather than read
  from the notes at draw time. They are correct - re-derived from `claim_0022` and `claim_0024`
  above - but they will not follow the data if anything is re-run.
