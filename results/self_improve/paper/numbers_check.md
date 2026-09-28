# Numbers in the draft, recomputed

Written 2026-09-28. Draft value, recomputed value, 2 SE where relevant, and the script. The draft
is not edited. Arm directories are the mapping in `questions_answered.md`.

**Read §0 first: two of these tables come from a different room chooser than the rest.**

## 0. What "first room right" and "found within 3 rooms" are computed over

Both are defined on every row: `found_at_step == 1` and `found_it`. In the ten-household run that
is **2,480 rows per method** (10 homes x 31 question-days x 8), every home exactly 248, so pooling
and averaging over households give the same number to one decimal. Exact-place accuracy has a
smaller and arm-dependent denominator (2,443 to 2,480) because an unparsed answer or LastSeen never
having seen the object leaves no place to score — see `scored_counts.py`.

Script for §1 to §4: `python3 results/self_improve/paper/scripts/table1_ten_homes.py` and
`day14_and_recovery.py`. For §5: `budget_sweep.py`.

## 1. Table 1, ten-household run, 8 questions a day

| method | draft | recomputed | difference |
|---|---|---|---|
| log and notes | 85.5 / 96.6 | **85.6 / 96.6** | +0.1 / 0 |
| LastSeen | 82.0 / 95.0 | **82.1 / 95.0** | +0.1 / 0 |
| claim store | 76.8 / 86.8 | **77.0 / 86.9** | +0.2 / +0.1 |
| reduced ACE | 75.9 / 85.3 | **76.0 / 85.3** | +0.1 / 0 |
| small working memory | 70.9 / 82.0 | **71.0 / 82.1** | +0.1 / +0.1 |
| notes hidden | 53.4 / 65.8 | **53.5 / 65.8** | +0.1 / 0 |

Every recomputed value is 0.0 to 0.2 points **above** the draft, and the ordering and the gaps are
unchanged. I could not identify the draft's estimator: pooling all 2,480 rows and averaging the ten
household rates agree with each other and not with the draft, and restricting to place-scored rows
moves the values up by about a point, further away. The difference is too small to matter for any
claim and too systematic to be rounding, so name the estimator in the caption.

## 2. Paired differences, ten households

| comparison | draft | recomputed | 2 SE | same sign in |
|---|---|---|---|---|
| LastSeen − claim store | +5.1 / +8.2 | **+5.1 / +8.2** | 5.7 / 4.3 | 7 of 10 / **10 of 10** |
| LastSeen − reduced ACE | +6.1 / +9.7 | **+6.0 / +9.7** | 6.1 / 6.1 | 7 of 10 / 9 of 10 |
| LastSeen − small working memory | +11.1 / +12.9 | **+11.1 / +12.9** | 7.1 / 6.9 | 8 of 10 / 10 of 10 |
| log and notes − LastSeen | +3.5 / +1.5 | **+3.5 / +1.5** | 4.2 / 2.0 | 9 of 10 / 8 of 10 |

The point estimates reproduce exactly. **The significance does not.** On first room right, only
LastSeen − small working memory clears 2 SE and the noise floor; LastSeen − claim store (+5.1
against 2 SE 5.7) and LastSeen − reduced ACE (+6.0 against 6.1) do not, and neither does log and
notes − LastSeen (+3.5 against 4.2). On found within 3 rooms all three LastSeen differences clear
and log and notes − LastSeen does not (+1.5, under the 2.2 floor as the draft already says).

So the sentence that all three LastSeen-beats-a-memory differences clear is true for
found-within-3 and not for first-room-right. Cluster is household, ten of them, 2 SE = 2 x sd/√10.

## 3. Day 14 on spell-1 movers, first room right

Draft: a range of **31.5 to 36.8** for every method. Recomputed, 35 mover questions on day 14
across the ten homes:

| method | day 14 | its own days 8-13 |
|---|---|---|
| claim store | **37.2** | 70.9 |
| small working memory | 36.8 | 60.4 |
| log and notes | 34.0 | 81.1 |
| LastSeen | 33.5 | 77.5 |
| reduced ACE | 31.5 | 64.9 |
| notes hidden | **28.8** | 45.3 |

The draft's range is the middle four. Two methods sit outside it: claim store at 37.2 above, notes
hidden at 28.8 below. The range for all six is **28.8 to 37.2**. The point the draft is making —
every design falls to about a third on the first changed day, whatever it scored before — survives
and is stronger with the full range, because notes hidden starts at 45.3 and falls to 28.8 while
log and notes starts at 81.1 and falls to 34.0.

## 4. Recovery by day 17 — **not reproducible, and the measure has no power**

Draft: 91% for log and notes, 58% for LastSeen, each against its own days 8 to 13 level.

Recomputed at day 17: **log and notes 100% (2 SE 23), LastSeen 80% (2 SE 31)**. The 20-point gap is
well inside either interval. The reason is the denominator: **day 17 carries 2 to 5 mover questions
per household** (2, 3, 3, 2, 5, 3, 4, 4, 3, 4), far below the eight-per-window minimum this project
set. Widening the window does not rescue it:

| window | log and notes | LastSeen | claim store | reduced ACE | small working memory | notes hidden |
|---|---|---|---|---|---|---|
| day 17 | 100% (2 SE 23) | 80% (31) | 98% (36) | 135% (52) | 116% (69) | 105% (47) |
| days 17-19 | 111% (13) | 100% (24) | 119% (37) | 142% (49) | 128% (94) | 149% (92) |
| days 17-23 | 110% (12) | 112% (20) | 132% (50) | 153% (52) | 127% (78) | 138% (86) |

Two things to notice before this goes in the paper. Every method exceeds 100% over the wider
windows, so the ratio is not measuring "how much of its old accuracy has it got back": the
days 8-to-13 baseline **on movers** is not the right reference, because the mover set is defined by
where the illness puts things, and mid-illness questions concentrate on fewer rooms. And no pair of
methods is separable at this precision. If the paper wants "our memory adapts within three days and
the trail does not", it needs a measure with a denominator — the day-by-day curve in
`first_illness_adaptation.pdf` is the honest version, and the numbers above should be dropped.

## 5. Budget sweep, five wider homes

`python3 results/self_improve/paper/scripts/budget_sweep.py`. Log and notes minus LastSeen, paired
within household, whole month, first room right / found within 3 rooms:

| questions a day | draft | recomputed | 2 SE | same sign in |
|---|---|---|---|---|
| 4 | +4.4 / +5.0 | **+4.4 / +5.0** | 1.9 / 2.4 | **5 of 5 / 5 of 5** |
| 8 | not quoted | **+3.5 / +2.6** | 3.0 / 2.3 | 5 of 5 / 4 of 5 |
| 24 | +1.2 / +0.1 | **+1.2 / +0.1** | 2.4 / 1.3 | 3 of 5 / 3 of 5 |

Reproduces exactly. At four a day both measures clear 2 SE and the noise floor with every household
agreeing; at 24 a day neither clears. The settled fortnight at four a day is +6.9 on both measures
(2 SE 2.0 and 2.6, 5 of 5). All three budgets ran under the same chooser, the same banks and the
same five households, so the trend is internal to one wave.

The note limit does not explain the trend: at 24 a day the flat sixteen binds on 117 of 160 nights
and lifting it to the counted allowance moves first room right by −0.8 (2 SE 2.3) and
found-within-3 by −0.9 (2 SE 2.6) on three homes — see
`archive/stopped_the_counted_allowance_was_already_a_null_2026-09-27/WHY_THESE_WERE_STOPPED.md`.

## Still to do

§6 to §15 of the list (the 50-day tables, the night-31 audits, the told-arm shares, the MemGPT and
ACE diagnostics), the four new analyses, the four figures, `appendix_material.md` and the
bibliography. The three told-arm and ACE diagnostics that are already settled are in
`questions_left_open.md` §1 and §4 rather than repeated here.
