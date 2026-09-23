# What F8 does and does not support

## The claim

> Scored the way a user would feel it — +1 for a right answer, −1 for a wrong one, 0 for declining — the ranking inverts at the moment of change: the methods that are most accurate in the settled world are the ones that collapse, and one goes NEGATIVE. On day 14 the timetable that never forgets scores below zero, meaning it would have done better answering nothing at all. Accuracy in a stable world does not predict value when the world moves.

## What in the figure demonstrates it

The first dotted rule. The timetable that never forgets falls from 7.7 in the settled week to 0.7 on the first sick days and the timetable with a three-day memory from 7.5 to 2.9, while the survival-time model goes 4.4 to 4.0 and the whole-log-in-the-prompt memory 5.4 to 4.1. Note also that the survival-time model sits BELOW both timetables while the world is stable. And on day 14 the timetable that never forgets's daily score is -3.0 — below zero, meaning it would have scored better answering nothing at all that day. That single day is the sharpest form of this figure's point and the window averages above do not show it.

## What it does NOT show

The threshold here is ONE number per method for the whole run, chosen knowing the whole run — not refitted per window, which is F9, and not per day, which is F10. That makes it an upper bound, though the tightest of the three, and not a policy anyone could have run in advance. Each method uses a different threshold, so the lines are not a like-for-like confidence comparison — that is deliberate, since the confidence scales differ wildly, but it means a reader cannot infer anything about the thresholds themselves from this figure.

## The numbers

Measured on the DAILY values, not read off the plotted line.

| series | its own best threshold | % of questions declined at it | settled week 9-13 | first sick days 14-16 | rest of the spell 17-23 | first days back 24-26 | a week later 27-31 | worst single day |
|---|---|---|---|---|---|---|---|---|
| timetable that never forgets | 0.272 | 3.6 | 7.7 | 0.7 | 6.6 | 6.5 | 7.4 | -3.0 |
| timetable with a three-day memory | 0.092 | 1.7 | 7.5 | 2.9 | 11.5 | 2.4 | 6.6 | -2.1 |
| survival-time model | 0.542 | 28.4 | 4.4 | 4.0 | 7.6 | 2.0 | 4.1 | -0.6 |
| whole-log-in-the-prompt memory | 0.65 | 9.5 | 5.4 | 4.1 | 7.1 | 4.5 | 5.7 | 0.9 |
