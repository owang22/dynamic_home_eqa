# The two mandated checks, run before drawing. Both fail.

Written 2026-09-28. The figure specification says to stop and report if Figure 2's values do not
match Table 2, and to print the exact text and stop if Figure 3's quotes are not verbatim. Both
triggered. Nothing has been drawn from these numbers.

Scripts: everything below is reproducible from
`results/self_improve/paper/scripts/paper_data.py` and `told_and_committed.py`; the exact commands
are in the sections.

## Check 1 — Figure 2 against Table 2: off by 0.6 of a point on day 32

Specification: "the day-14 and day-32 values drawn must match Table 2 (last seen 20→54 first room,
averaged)". Measured, last seen first room right on the 14 both-illness movers, per household and
then averaged over households:

| | hh_s2 | hh_s32 | hh_s48 | average | Table 2 says |
|---|---|---|---|---|---|
| day 14 | 10.0% (10 q) | 33.3% (6 q) | 18.2% (11 q) | **20.51** | 20 |
| day 32 | 55.6% (9 q) | 50.0% (4 q) | 54.5% (11 q) | **53.37** | 54 |

Day 14 agrees. **Day 32 is 53.4, not 54.** The gap is 0.6 of a point and almost certainly an
estimator difference rather than an error: 53.37 is the mean of the three household rates, and 54
would come out of pooling the questions instead — 15 of 24 pooled is 62.5%, which is not it either,
so the likeliest source is a rounding step somewhere in the table's own pipeline.

It is 0.6 of a point on a figure whose day-32 column rests on 4 to 11 questions a household. It
changes nothing about the claim. But the specification said to stop rather than draw a number that
disagrees with the table, so: **which is right, the table or the mean of household rates?** Say
which and the figure follows in minutes.

## Check 2 — Figure 3's "86% predicted": not reproducible under any object set

Specification: a stacked bar of "the resident's moved objects on day 14 by room", printing "86%
predicted, 0% office".

**The 0% office is right, in every reading.** The 86% is not. On hh_s2, day 14, told-and-committed,
counting the share whose true room is bedroom_1 or living:

| object set | in a predicted room | share | in the office |
|---|---|---|---|
| **Tomas's moved objects** (what the panel describes) | 11 of 11 | **100.0%** | 0 |
| Tomas's asked objects, moved or not | 11 of 18 | 61.1% | 0 |
| every moved object, any resident | 11 of 12 | 91.7% | 0 |
| every asked object that day | 11 of 24 | 45.8% | 0 |

Nothing gives 86%. The panel as written — "the resident's moved objects" — is **100%**: all eleven
questions about Tomas's six moved objects had their answer in bedroom_1 (7) or the living room (4),
and none in the office, the room the note had ruled out.

100% is a stronger result than 86% and I am not going to quietly draw the stronger number. Tell me
which denominator the paper means and I will draw that one.

## Check 3 — Figure 3's quotes: verbatim, with one truncation to resolve

All three exist in the run. Read from the claim's own history at the night in question, not from
its current text.

**Night 13, the prediction** — the specification quotes two sentences; the note has three:

> Tomas is unwell and staying home. Expect him in bedroom_1 or living room during day/evening, not
> office. His laptop/mug/charger likely in bedroom_1 or living, not office desk.

The spec's version stops after "not office." Either is defensible on a card — the third sentence is
the part that names the objects — but it should be marked with an ellipsis if it is cut.

**Night 14, the retraction** — verbatim, and the spec's ellipsis marks the omission correctly:

> Tomas works from the office during the day (seen 14:08). He moves to the living room in the
> evening (seen 19:48-20:50). The 'unwell' hypothesis from Day 13 is not supported by Day 14
> activity.

**The glass note** — verbatim, with one correction: it was not *written* that night, it was a
night-13 claim **revised** that night, which is a sharper fact for the panel.

> Tomas's glass is on the bedroom nightstand during the day (seen 08:07-15:12).

Worth the caption: those last two were written on the same night. One says Tomas was in the office
during the day; the other says his glass sat on the bedroom nightstand from 08:07 to 15:12.

## Palette, settled and checked

The suggested roles mostly survive the colour-blindness check; two do not.

| method | colour | note |
|---|---|---|
| last seen | `#0072B2` dark blue | as suggested |
| log and notes | `#D55E00` orange | as suggested |
| claim store | `#009E73` green | **not grey-green**: every grey-green tried fails the chroma floor, i.e. it reads as grey |
| ACE-style | `#785EF0` purple | as suggested |
| MemGPT-style | `#882255` wine | **not brown**: brown is dark orange, and every brown tried fails against `#D55E00` on the same axis in Figure A1 (worst ΔE 3.2 protan, 6.8 normal vision) |
| notes hidden | `#BBBBBB` light grey | as suggested; it shares an axis with nothing in this spec |

The four on one axis in Figure 2 pass on all pairs with no warning; adding `#882255` for Figure A1
keeps that.
