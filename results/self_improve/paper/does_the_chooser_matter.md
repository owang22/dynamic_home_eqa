# Does reasoning before choosing the room change the result? No.

Written 2026-09-28. **This corrects what I wrote in `questions_left_open.md` section 2 and said
twice in reports.** The fact there was right; the conclusion drawn from it was not.

Scripts: `scripts/does_the_chooser_matter.py` (the paired table) and `scripts/plot_the_chooser.py`
(the figure, `figures/the_chooser_by_day.pdf`).

## What I got wrong

I established that the ten-household run and `overnight_wave_24_questions` name the room *before*
the reason, with 36% and 42% of explanations cut off at exactly 240 characters, and that every
later wave reasons first. That much is measured and stands.

From it I concluded that "Table 1 and the recurrence figures are not the same system", that
comparing across them is comparing across a change in the chooser, and that Table 1 should perhaps
be rebuilt. **I never measured the chooser's effect before saying that.** I inferred it from a
mechanism - no thinking channel, so the field order is the reasoning order - and from the fact that
the two groups of waves disagree about whether a written memory beats last seen.

## The test I should have run first

`overnight_wave_24_questions` and `wave_reasons_first` are **the same three households, the same
banks, the same 24 questions a day, and the same arms**. They differ in the room-choice schema and
nothing else. That is a paired test of the chooser; comparing either with the ten-household run is
not, because that also changes the households, the question budget and the object list.

**The control passes.** last seen makes no model call, so its rows must be identical across the two
waves, and they are: 744 of 744 rows in each of the three homes, matching on the rooms opened, the
step it was found at and the place answered. So the chooser is the only thing that moved.

## What the chooser actually does

`figures/the_chooser_by_day.pdf` plots first room right by day under both choosers, pooled over the
three homes, for every question and for moved objects, with the illness shaded and days 14 and 24
marked. **The two curves track each other.** Both dip on day 14, both dip again on day 24, both
recover on the same schedule, and the gaps between them are day-to-day wobble of a few questions.

At the days that matter - the first after each transition - on moved objects, room-first → reason-first:

| arm | day 14 | day 15 | day 16 | day 24 | day 25 |
|---|---|---|---|---|---|
| log and notes | 26 → 38 | 87 → 90 | 97 → 97 | 82 → 72 | 67 → 79 |
| claim store | 18 → 15 | 41 → 51 | 70 → 78 | 26 → 18 | 69 → 69 |
| ACE | 21 → 18 | 54 → 77 | 78 → 84 | 41 → 23 | 69 → 67 |
| counted allowance | 24 → 18 | 56 → 72 | 81 → 70 | 31 → 18 | 59 → 49 |

A single day here carries about 33 moved-object questions across the three homes, so one question
is three points. Paired across households, every window difference sits inside its own 2 SE: the
largest, ACE on day 24 at −24.5, has a 2 SE of 28, and the log-and-notes day-14 gain of +11.9 has a
2 SE of 6 in one direction while its day-24 loss of −10.3 has a 2 SE of 10 in the other.

**There is no systematic effect, and no consistent direction across arms.** Reason-first is better
for log and notes on day 14 and worse on day 24; worse for the claim store nearly everywhere;
better for ACE in the middle of the illness and worse at both ends.

## What stands, and what to write instead

Stands: the ten-household run and the 24-a-day wave chose the room with no deliberation and with a
third of their explanations truncated. That is a real limitation of those two waves and belongs in
the paper as one.

Does not stand: that Table 1 measures a different system, that its numbers cannot sit beside the
recurrence figures, or that it should be rebuilt. The chooser does not move the day curves.

And the thing I attributed to it - that a written memory beats last seen on the 50-day homes while
last seen leads in Table 1 - has to be explained by what else differs between those runs: different
households, 24 questions a day against 8, and the wide object list against the narrow one. Not the
chooser.
