# The 32-day and 50-day ACE runs on hh_s2, checked against each other, 2026-09-26

Oliver read the two ACE lines on the artifact and saw sharp falls in the 50-day run, on day 14 and
again around day 7, and asked three things: was the 50-day run wasteful, did the two runs see the
same questions, and is the project carrying so much run-to-run variability that the results might
be luck.

## The two runs are the same run where they overlap

Checked field by field on the 744 questions of days 1 to 31, matched on question id and object:

| checked | differs on |
|---|---|
| the question set: id, object, time of day, true place | **0 of 744** |
| the rooms opened, in order | **0 of 744** |
| which step the object was found at | **0 of 744** |
| whether it was found at all | **0 of 744** |
| the place it answered | **0 of 744** |
| whether the object counts as a mover | **0 of 744** |
| the set of movers for the household | identical, 8 objects |

So there is no difference to diagnose between them over days 1 to 31. Anything that looks like one
is the same curve drawn twice.

## It was not wasteful either

The 50-day run made 1,772 model calls and **1,214 of them, 69%, were served from the response
cache** - which is days 1 to 31 replayed for nothing. The 558 new calls are days 32 to 49, which no
run had done before. The 32-day cell it is compared against was itself 1,152 calls, 1,152 of them
cached.

That has a consequence worth stating: **this pair cannot measure run-to-run variability at all.**
Both cells are replays of one set of completions, so they agree by construction. The only way to
measure that variability is to defeat the cache deliberately, which is where the 1.9 points on
first room right and 2.2 on found-within-budget came from, measured on a separate same-session
baseline.

## What the falls actually are

ACE on this household, first room right, one point per day, 24 questions a day:

    day  1   2   3   4   5   6   7   8   9  10  11  12  13  | 14 |  15  16 ... 23 | 24 | ...
        54  58  83  58  88  79  58  88  88  79  83  88  88  |  46 |  88  92     92 |  33 |

Day 14 and day 24 are the disruption starting and ending, and they are the largest single-day
effects in the study. **Day 7 is not an event.** It is 58%, and so are days 2 and 4, in a settled
stretch whose average is 80%: the first fortnight is where the memory is thinnest and the daily
points bounce most.

The size of the bounce is what counting alone predicts:

| | spread of the daily points, days 3-13 | predicted by counting alone | one question is worth |
|---|---|---|---|
| all objects, 24 a day | 11.2 points | 8.2 points | 4.2 points |
| only the movers, 11-21 a day | 15.0 points | 11.9 points | 6.5 points |

A single day holds 24 questions, so **one question moves a daily point by 4.2 points and three
questions move it by 13.** Day 7 at 58% against day 8 at 88% is seven questions out of 24. There is
a little more spread than counting alone gives, which is expected because the memory is genuinely
changing from night to night, but nothing that needs another explanation.

## So: is it luck?

Not in the sense feared, and the guard is already in place. No claim in `THE_MAIN_POINTS.md` rests
on a single day of a single household. Every one is a window of at least eight questions per home,
paired inside each home, averaged across homes, and required to clear two standard errors AND the
rerun noise floor AND to point the same way in every home. The artifact's comparison tables print
the number of homes in every cell for the same reason.

**What to distrust is a daily point read on its own** - including a daily point that supports us.
The day-14 and day-24 falls survive because they are 30 to 50 points, four to twelve times the
noise of a single day, and they repeat in every household.
