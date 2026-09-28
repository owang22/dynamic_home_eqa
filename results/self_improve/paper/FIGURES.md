# The four figures: what each one draws, and what to write under it

`PYTHONPATH=src python3 results/self_improve/paper/scripts/make_figures.py`, which prints every
number it drew. Style, colours and the text width are in `scripts/figure_style.py`.

## Before these go in the document

**The width is a guess.** `corl_2026.sty` is not in this repository and not anywhere under the
home directory, so the text width could not be read from it. Every figure is drawn on a canvas
**5.5 in (396 pt) wide** and is **not cropped to its content**, so all four are exactly the same
width and the type is exactly 8 to 9 pt — but only if 5.5 in is right. Put `\showthe\textwidth` in
the draft and re-run:

    CORL_TEXTWIDTH_IN=<inches> PYTHONPATH=src python3 results/self_improve/paper/scripts/make_figures.py

Include them with `\includegraphics{...}` and **no width argument**. A `width=\textwidth` would
rescale and change the type size.

**The colours were checked, not chosen by eye**, with the dataviz validator: the four methods that
share an axis (LastSeen `#0072B2`, log and notes `#D55E00`, claim store `#009E73`, ACE `#785EF0`)
pass every check including the strict all-pairs test with no warning. The full seven-method set
passes as an ordered legend. Every line is also labelled directly, so nothing is told apart by hue
alone.

## Figure 1, `overview.pdf` — the schematic

The calendar with both illnesses shaded alike; one mug's share of the day per room under normal
life and under the illness, showing the weight moving rather than the object teleporting; and the
five-step loop, with the return leg drawn below the row and labelled "every day for a month". The
illness is marked as hidden from the robot in the line above the calendar. No data.

## Figure 2, `recurrence_first_day.pdf` — main text

Found within 3 rooms on the 14 **both-spell movers**, day 14 against day 32, one panel per method,
one line per household, the question count printed at each end.

| method | hh_s2 | hh_s32 | hh_s48 | mean change | 2 SE |
|---|---|---|---|---|---|
| LastSeen | 10 → 78 | 33 → 100 | 27 → 64 | **+56.9** | 20.6 |
| log and notes | 40 → 78 | 50 → 100 | 82 → 82 | +29.3 | 30.1 |
| claim store | 20 → 33 | 50 → 25 | 73 → 36 | −16.0 | 30.1 |
| ACE | 10 → 44 | 83 → 25 | 91 → 45 | −23.1 | 58.0 |

Two things the caption has to say. **The day-32 column rests on 4 to 11 questions per household**
(hh_s32 has 4, below this project's own eight-per-window minimum), which is why the 2 SE runs from
21 to 58 points. And these are the objects that move in **both** illnesses — the spell-1 mover set
would put 8 objects in here that the second illness leaves where they normally are, and flatter
every method's day-32 column.

The draft's Table 2 quotes LastSeen +45.1 (2 SE 14.6) and log and notes +21.1 (2 SE 20.1) on the
spell-1 set; on the both-spell set they are +56.9 (20.6) and +29.3 (30.1). Report whichever set the
paper defines, and say which.

## Figure 3, `recurrence_timeline.pdf` — appendix

The same measure every day, averaged over the three households with a ±1 SE band, both spells
shaded, days 14 and 32 marked, and a strip underneath with the number of both-spell-mover questions
each day (12 to 29 across the three homes).

| method | settled | day 14 | spell 1 | day 32 | spell 2 |
|---|---|---|---|---|---|
| LastSeen | 98 | **24** | 71 | **80** | 83 |
| log and notes | 95 | 57 | 95 | 87 | 99 |
| claim store | 77 | 48 | 87 | **32** | 90 |
| ACE | 76 | 61 | 94 | **38** | 90 |

The shape worth pointing at: LastSeen falls furthest on day 14 (98 → 24) and barely falls the
second time (80), while the two written memories fall **further** on day 32 than on day 14. A trail
gets the repeat for free; a memory that has been rewritten across the recovery does not.

## Figure 4, `first_illness_adaptation.pdf` — appendix

First room right on spell-1 movers, ten-household run, days 1 to 31, one panel per method with the
other five behind it in grey, ±1 SE across households, days 14 to 23 shaded.

Six lines on one axis would not have been legible: seven method colours cannot all clear the
validator's normal-vision floor at once, and the rule for that case is to facet rather than cycle
hues. Identity here is colour **and** position.

| method | days 8-13 | day 14 | day 17 | day 24 |
|---|---|---|---|---|
| log and notes | 83 | 34 | 78 | 64 |
| LastSeen | 79 | 34 | 60 | 42 |
| claim store | 64 | 36 | 69 | 31 |
| reduced ACE | 65 | 32 | 73 | 24 |
| small working memory | 63 | 37 | 53 | 39 |
| notes hidden | 31 | 31 | 33 | 21 |

Caption material: every method that writes anything falls to about a third on day 14 and climbs
back inside the spell; the arm with no notes at search time is flat at about 31 throughout, which
is what the fall is measured against; and the second dip at day 24 — the day ordinary life returns —
is deepest for the memories that had adapted most.

**This figure is the honest version of the "recovery by day 17" numbers**, which cannot be quoted:
day 17 carries 2 to 5 mover questions per household, and the draft's 91% against 58% recomputes as
100% (2 SE 23) against 80% (2 SE 31). See `numbers_check.md` §4.
