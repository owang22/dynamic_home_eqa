# What F10 does and does not support

## The claim

> Refitting the threshold every single day — the most generous reading there is — does not rescue the timetables at the shift. The timetable that never forgets has a confidence signal that beats hindsight-on-shuffled-labels in every window of the run except one: 0.20 against a bar of 0.10 in the settled week, 0.35 against 0.21 on the first days back — and at the first sick days 0.07 against a bar of 0.33, which is nothing. The three-day timetable is clears at neither boundary (0.18 against 0.39 at the shift, 0.29 against 0.35 on the return). The survival-time model moves the other way, from 0.51 settled to 2.25 at the shift, the largest value it reaches all run. So the never-forgets timetable does not have a weak signal that the shift weakens further: it has a working signal that stops working on the day the routine changes and works again a week later.

## What in the figure demonstrates it

The first dotted rule. The never-forgets timetable dips to and below the zero line there, at the same moment the survival-time model rises to its highest point of the run. The three-day timetable is near zero at both rules, which is why the claim above treats the two timetables differently rather than as one story.

## Why this happens

The floor itself moves, and that is the point. In the settled week hindsight on shuffled labels buys almost nothing, because a method that is right four times in five leaves little for a threshold to find. At the shift the timetables are right about half the time, and hindsight on pure noise then buys a great deal. Their observed gain rises at the shift too — which is why the raw number looks like a result — but it rises no faster than the floor beneath it.

## What it does NOT show

It does not show the total value of declining, most of which comes from the level term and not from the ordering — that split is F9's. It is not a deployable policy: the threshold is chosen knowing the day it is scored on, which is why a noise floor has to be subtracted at all. Days 1 to 8 are drawn for completeness and nothing is claimed from them: the methods' memories are still filling, and the settled comparison in every window table starts at day 9.

## The numbers

Measured on the DAILY values, not read off the plotted line.

| series | settled week 9-13 | settled week 9-13 (bar to clear) | first sick days 14-16 | first sick days 14-16 (bar to clear) | rest of the spell 17-23 | rest of the spell 17-23 (bar to clear) | first days back 24-26 | first days back 24-26 (bar to clear) | a week later 27-31 | a week later 27-31 (bar to clear) |
|---|---|---|---|---|---|---|---|---|---|---|
| timetable that never forgets | 0.2 | 0.1 | 0.07 | 0.33 | 0.22 | 0.2 | 0.35 | 0.21 | 0.53 | 0.16 |
| timetable with a three-day memory | 0.1 | 0.12 | 0.18 | 0.39 | 0.13 | 0.07 | 0.29 | 0.35 | 0.33 | 0.12 |
| survival-time model | 0.51 | 0.23 | 2.25 | 0.5 | 0.59 | 0.16 | 1.05 | 0.51 | 1.55 | 0.33 |
| whole-log-in-the-prompt memory | 0.28 | 0.17 | 0.75 | 0.26 | 0.37 | 0.14 | 0.38 | 0.21 | 0.65 | 0.22 |
