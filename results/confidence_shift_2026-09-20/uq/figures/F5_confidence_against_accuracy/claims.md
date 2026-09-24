# What F5 does and does not support

## Its job in the argument

States the paper's claim in its simplest form: accuracy and uncertainty are separate axes, and a regime shift moves one and not the other. Everything after this figure is about why, and what it costs.

## The claim

> Accuracy and the confidence a method states in its own answer are separate quantities, and a change in the household's routine moves one of them and not the other. At the shift the timetables' accuracy collapses while the confidence they state in their own answers barely moves, so the gap between what they claim and what they deliver opens by 10 points in a single day for the timetable that never forgets. The survival-time model is the one whose stated confidence moves with its own accuracy through the change, its gap at day 14 being +24.8 points against that timetable's +10.3. It is also the least accurate method on this chart while the household is stable, which is the point rather than an inconsistency: whatever makes a method accurate in a settled world is not what makes its uncertainty survive a change to that world.

## What in the figure demonstrates it

The first dotted rule, and each method's two lines at it. The timetable that never forgets loses 47 points of accuracy between day 13 and day 14 while the confidence it states moves 14. The survival-time model's two lines move together. That contrast, on one pair of panels, is the paper.

## What it does NOT show

It does not show WHY the two behave differently — that is the next figure, and it is a property of how each one computes a confidence number rather than of how good each one is. The right-hand panel is each method's own number on its own scale, so heights are not comparable between methods; only each line against its own left-hand partner is.

## The numbers

Measured on the DAILY values, not read off the plotted line.

| series | accuracy day 13 | confidence day 13 | accuracy day 14 | confidence day 14 | gap at day 14 |
|---|---|---|---|---|---|
| timetable that never forgets | 87.3 | 63.9 | 40.0 | 50.3 | 10.3 |
| timetable with a three-day memory | 83.3 | 47.5 | 42.5 | 38.9 | -3.6 |
| survival-time model | 69.3 | 71.1 | 44.4 | 69.1 | 24.8 |
| LLM | 78.5 | 88.8 | 59.4 | 90.9 | 31.5 |
