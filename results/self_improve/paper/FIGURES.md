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
| LastSeen | 79.3 | **20.5** | 58.8 | 84.8 | **53.4** | 31.4 |
| log and notes | 84.6 | 27.4 | 57.3 | 84.9 | 55.7 | 29.2 |
| claim store | 57.6 | 6.4 | 51.3 | 60.6 | 12.8 | 47.8 |
| ACE-style | 61.7 | 8.6 | 53.1 | 67.7 | 12.8 | 54.9 |

Per household, LastSeen: day 14 10 / 33 / 18, day 32 56 / 50 / 55.

**Figure A1, the first illness** — `figureA1_first_illness.pdf`. Ten-household run, moved objects,
days 1 to 31.

| method | days 10-13 | day 14 | day 24 |
|---|---|---|---|
| LastSeen | 81.6 | 33.5 | 42.2 |
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

## Still to build

Figure 1 (the schematic), Figure 3 (the three-panel comic strip) and Figure A2 (the night-31 notes
and the sliding threshold). Figure 3's two blocking questions are in
`FIGURE_CHECKS_BEFORE_DRAWING.md` and are still open: which denominator the "86% predicted" panel
means, and whether Table 2's day-32 value of 54 or the measured 53.4 is right.

## The palette, as validated

`#0072B2` LastSeen, `#D55E00` log and notes, `#009E73` claim store, `#785EF0` ACE-style and reduced
ACE, `#882255` MemGPT-style and tight working memory, `#BBBBBB` notes hidden. Grey-green and brown,
which the specification suggests, both fail the colour-blindness checker — see
`FIGURE_CHECKS_BEFORE_DRAWING.md`.
