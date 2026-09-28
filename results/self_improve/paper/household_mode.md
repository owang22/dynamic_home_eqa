# A non-language-model latent-state searcher: "household mode"

Written 2026-09-28. No language model, no GPU: a count table and a Chinese restaurant process.
Measured cost, `run_household_mode.py` timed directly — **0.4 s** for a 31-day cell at 8 questions
a day, **1.5 s** for a 50-day cell at 24, zero model calls. The whole 28-cell run is about 20
seconds; the nine-setting grid took 3 minutes 16 seconds.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/run_household_mode.py --check
    PYTHONPATH=src python3 results/self_improve/paper/scripts/run_household_mode.py --run --alpha 1 --stay 0.9
    PYTHONPATH=src python3 results/self_improve/paper/scripts/score_household_mode.py
    PYTHONPATH=src python3 results/self_improve/paper/scripts/why_one_mode.py

The model is `src/self_improve/household_mode.py`, built exactly to the specification: modes
holding object → room counts under a Dirichlet prior of 0.5, hard CRP assignment of each whole day,
a within-day posterior started from yesterday's mode, rooms ranked by P(room | object) summed over
modes, LastSeen's rule as the fallback for an object no mode has seen, and the answer taken from
the most recent sighting in the room where it is found.

## The loop was checked before the arm was trusted

LastSeen rerun through the runner's own `run_one_search`, in the environment this driver builds,
reproduces **every recorded row of all 28 cells** — question by question, on the rooms opened, the
step it was found at, the place answered and both correctness flags. So the environment is the one
the results came from, and any difference below belongs to the arm.

## It never finds a second mode — at any setting asked for

| alpha | stay 0.8 | stay 0.9 | stay 0.95 |
|---|---|---|---|
| 0.5 | 1 mode | 1 mode | 1 mode |
| 1 | 1 mode | 1 mode | 1 mode |
| 2 | 1 mode | 1 mode | 1 mode |

One mode in every one of the 28 households, at all nine settings. The mode-by-day table is one
line: **every day of every run is assigned to mode 0.** Nothing was tuned to change that.

## Why, in the arithmetic of one day

`why_one_mode.py` prints the two numbers the CRP compares on day 14, the first day of the illness
and the day with the best chance of splitting:

| household | sightings that day | of them, objects the illness moves | existing mode | a new empty mode |
|---|---|---|---|---|
| hh_s2 | 78 | 14 (18%) | −33.7 | −171.4 |
| hh_s32 | 126 | 13 (10%) | −26.1 | −262.0 |
| hh_s48 | 187 | 12 (6%) | −88.3 | −388.9 |

The established mode wins by 138 to 301 in log units. A new mode would have to be e^138 times
better to be chosen.

**The reason is not that the shift is invisible — it is that the day is mostly not about it.** A
look into a room records everything in that room, so a day's sightings are dominated by the objects
that did not move, each of them exactly where the established mode expects. The objects that did
move are there and are properly surprising — in hh_s2, `water_bottle_tomas` in bedroom_1 at p=0.009,
`glass_tomas` at 0.043, `charger_tomas` at 0.065 — but they are 6% to 18% of the evidence, and a
whole-day likelihood drowns them in the 82% to 94% that is business as usual.

**This is a result about the design, not about this household.** Hard assignment of a whole day
cannot detect a regime change that touches a minority of objects, however surprising those objects
are individually. A model that could would have to assign per object, or weight by surprise, or
score the day against what it predicted rather than against everything it saw.

## What it scores, given one mode

With one mode the memory is a per-object room-frequency table averaged over the whole month. That
is strictly worse than a recency trail, and the numbers say so — first room right, against LastSeen,
paired within household:

| run | log and notes | household mode |
|---|---|---|
| ten homes, 8 a day, every question | +3.5 (2 SE 4.2), 9 of 10 | **−14.9 (2 SE 10.6), 1 of 10** |
| ten homes, moved objects | +3.7 (2 SE 7.2), 8 of 10 | **−26.2 (2 SE 16.6), 1 of 10** |
| 50 days, 24 a day, every question | +4.3 (2 SE 5.2), 3 of 3 | **−10.1 (2 SE 6.5), 0 of 3** |
| 50 days, moved objects | +8.8 (2 SE 10.2), 3 of 3 | **−16.3 (2 SE 10.2), 0 of 3** |

Found within 3 rooms tells the same story: −18.4 and −31.2 on the ten homes, −3.7 and −6.7 on the
50-day run. Full tables, including the two budget-sweep runs, in `household_mode_scores.txt`.

Day 14 against day 32 on the objects that move in both illnesses, first room right:

| method | hh_s2 | hh_s32 | hh_s48 | mean change | 2 SE |
|---|---|---|---|---|---|
| LastSeen | 10 → 56 | 33 → 50 | 18 → 55 | +32.9 | 17.0 |
| log and notes | 20 → 44 | 17 → 50 | 45 → 73 | +28.4 | 5.2 |
| household mode | 10 → 33 | 17 → 0 | 0 → 18 | +8.3 | 25.1 |

It absorbs the second illness least of the three, which follows from the same fact: a month-long
average has no way to notice that this week is like a fortnight ago.

## What this is worth to the paper

A negative result with a mechanism, and it closes a hole a reviewer would otherwise open. The
obvious objection to the whole study is that a language model is unnecessary — that a small latent
state model would find the regime for free. Built to a reasonable specification and given its own
searches, it finds one mode and scores 15 to 26 points below a rule that just walks back through
where the thing was last seen.

It is one specification, not the family. What it licenses is: *hard whole-day assignment under a
CRP does not find this shift, because the shift is a minority of the evidence on the day it starts.*
It does not license "no latent-state model can". The per-object and surprise-weighted variants are
the obvious next ones, and neither needs a GPU.
