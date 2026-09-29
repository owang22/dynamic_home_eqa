# The figures, in two versions, and every number drawn

Built 2026-09-28. Two complete sets, because the written specification and the guidance given
verbally disagree on four points and neither is a subset of the other:

| | `figures/spec/` | `figures/oliver/` |
|---|---|---|
| lines on one axis | four or five | two, at most three |
| uncertainty | ±1 SE band behind each line | none |
| text | regular weight, no title | bold throughout, with a title |
| legend | inside the plot | below it, one entry a row |

They agree on the rest: first-room-right on y labelled in words, day on x, the illness shaded with
"sick" over the band, one fixed colour per method, 396 pt canvas, vector PDF.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/paper_figures.py

Every number below is printed by that script into `figures/NUMBERS_DRAWN.txt` as it draws.

## Done

**Figure 2, both illnesses** — `figure2_both_illnesses.pdf`. 50-day run, three households, first
room right on the 14 both-illness movers, averaged over households, by day, with a strip of
questions-per-day underneath (12 to 29 a day).

| method | days 10-13 | day 14 | fall | days 28-31 | day 32 | fall |
|---|---|---|---|---|---|---|
| last seen | 79.3 | **20.5** | 58.8 | 84.8 | **53.4** | 31.4 |
| log and notes | 84.6 | 27.4 | 57.3 | 84.9 | 55.7 | 29.2 |
| claim store | 57.6 | 6.4 | 51.3 | 60.6 | 12.8 | 47.8 |
| ACE-style | 61.7 | 8.6 | 53.1 | 67.7 | 12.8 | 54.9 |

Per household, last seen: day 14 10 / 33 / 18, day 32 56 / 50 / 55.

**Figure A1, the first illness** — `figureA1_first_illness.pdf`. Ten-household run, moved objects,
days 1 to 31.

| method | days 10-13 | day 14 | day 24 |
|---|---|---|---|
| last seen | 81.6 | 33.5 | 42.2 |
| log and notes | 85.3 | 34.0 | 63.5 |
| claim store | 68.2 | 36.0 | 31.3 |
| reduced ACE | 69.1 | 31.5 | 24.4 |
| tight working memory | 63.8 | 36.8 | 39.1 |

## Three places the specification and the data disagree

**1. The day-32 annotation was not true as written.** It asked for "second illness: only
summary-only memories drop". Measured against each line's own days-28-to-31 level, the trail falls
31.4 points on day 32 and our notes 29.2 — not "barely". What is true is that they fall about half
as far as the summary-only memories (47.8 and 54.9), whereas on day 14 all four fell within eight
points of each other. The figures carry the true version, computed from the lines actually drawn so
the three-line and four-line versions cannot disagree with each other.

**2. Figure A1 cannot show ACE-style or MemGPT-style, because the ten-household run has neither.**
Its ACE-shaped arm is `claim_store_told_if_it_was_right`, the constrained version, and its
MemGPT-shaped arm is `a_small_working_memory_and_an_archive`, which ran on a **1,200-character**
block — a sixteenth of MemGPT's own smallest, which `memory_notes.py:196-200` says must be called
the tight variant and never MemGPT. They are drawn under the names **reduced ACE** and **tight
working memory**, keeping the published methods' colours because they are those methods' cousins.
The published pair exist only at 24 questions a day on three households.

**3. The expected day-14 range was 29-37%; it is 31.5-36.8%.** Close, and the claim is unaffected.

**Figure 3, told the cause** — `figure3_told_the_cause.pdf`. Three panels joined by arrows.
Night 13 carries all three sentences, as decided. Day 14 prints the denominator on the bar:
**11 of 11, 100%** — bedroom_1 7, living 4, office 0. Night 14 puts the retraction beside the glass
note under the bracket "written the same night", with the glass card marked "revised the same
night" because it is a night-13 claim revised, not a new one.

**Figure A2, what the notes held on night 31** — `figureA2_what_the_notes_held.pdf`. Left, live
notes naming an object and one of its illness-time places, split by the condition attached; right,
the hour the ACE-style playbook says "evening" begins.

| method | total | "always" | a time of day | a person home or away | other |
|---|---|---|---|---|---|
| claim store | 170 | 65 | 77 | 0 | 28 |
| log and notes | 142 | 19 | 115 | 0 | 8 |
| reduced ACE | 114 | 49 | 46 | 12 | 7 |
| tight working memory | 27 | 4 | 10 | 3 | 10 |
| **total** | **453** | 137 | 248 | 15 | 53 |

**Mentioning the illness: 0, in all four methods.** Out of 1,501 live notes, 453 describe a place
an object went to *because* someone was ill, and not one of them says so.

The threshold, `overnight_wave_24_questions/ACE_as_published/hh_s2_t03`, claim_0006:

| night | "evening" begins at |
|---|---|
| 13 | 20:00 |
| 14 | 13:00 |
| 15 to 18 | **11:47** |
| 19 to 22 | 11:00 |
| 23 | no time stated |

Behind it, the hours the ill resident was actually in the house on days 14 to 23: **every hour from
06:00 to 23:00, on 10 days out of 10** (one hour, 20:00, on 9 of 10). That is the point of the
panel — he is home all day, so "evening" has stopped distinguishing anything, and the playbook's
threshold slides to late morning chasing a distinction that no longer exists.

## Two recomputed numbers that differ from earlier notes

**The night-31 count is 453, not 428**, and per method 170 / 142 / 114 / 27 against the earlier
156 / 131 / 103 / 38. The rule used here is stated so it can be checked: a note counts when the
structural matcher `write_the_notes.where_an_object_is_named` finds the object AND the note's text
contains one of the plain-word places or rooms that object occupied during daytime hours on days 14
to 23, taken from the bank rather than from text. The "0 mention the illness" agrees exactly.

**The "always" count is 137, not 74**, under the condition rule stated in `night31_audit.py`: a
condition counts as "always" when it is empty or one of always / any time / all day / current /
general; as "a person home or away" when it names someone being at home, out or away; as "a time of
day" when it names a part of the day or a clock time; otherwise "other".

**And the threshold nights are one earlier than previously reported**: 20:00 on night 13, 13:00 on
night 14, 11:47 from night 15. My earlier report said 14, 15, 16 because that check had not been
given the fix for reading a claim's history - `revision_history` stores the text a revision
REPLACED, so the wording on night N is the `was` of the first revision after it.

## Still to build

Figure 1, the schematic. It needs no data decisions.

## The palette, as validated

`#0072B2` last seen, `#D55E00` log and notes, `#009E73` claim store, `#785EF0` ACE-style and reduced
ACE, `#882255` MemGPT-style and tight working memory, `#BBBBBB` notes hidden. Grey-green and brown,
which the specification suggests, both fail the colour-blindness checker — see
`FIGURE_CHECKS_BEFORE_DRAWING.md`.
