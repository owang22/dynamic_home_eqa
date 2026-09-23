# What F11 does and does not support

## Its job in the argument

The paper's positive result and the one a model designer can act on. Every other figure says something is broken; this one says which design choice is not broken, and the mechanism section attaches here.

## The claim

> Whether a method's confidence survives a change in the routine is not a matter of how good the method is. It follows from what its confidence is a function of. In a settled household all four methods' stated confidence predicts being right, and by similar amounts: 0.35 for the timetable that never forgets, 0.28 for the three-day one, 0.37 for the survival-time model and 0.29 for the whole log in the prompt. On the first days of the new routine the two timetables fall to nothing (-0.12 and -0.00; the falls of 0.47 and 0.28 both clear our bar). The survival-time model does not move (0.43, a change of +0.07 that does not clear), and the whole log in the prompt degrades without breaking (0.22).

The reason is in the arithmetic of the two confidence numbers rather than in their quality. A timetable's confidence is the share of its sightings in the matching hour bin that fell at the answer it is giving — a ratio of counts. Scale every count down and the ratio is unchanged, so the number is very nearly blind to how old the evidence is. The survival-time model's confidence is a probability advanced from the last sighting by an exponential decay toward that object's long-run base rate, at a speed fitted per object: it IS a measure of how stale the evidence is, and it is least confident about exactly the objects that move most.

A change in routine is an event that makes old evidence wrong WITHOUT changing the historical frequencies. So it is invisible to one confidence number by construction, and visible to the other by construction. That is a design prescription and not a league table: put the age of the evidence in the state, not only its frequency.

## What in the figure demonstrates it

The shaded column. Four lines arrive at it together, from much the same height, and two of them drop to the zero line while two carry on. Then look to the right of it: the timetables come back. Nothing about these methods is permanently broken — their confidence stops meaning anything for the days the routine is changing, which is when a robot would be relying on it.

## Why this happens

Two independent statistics agree on which methods have a real signal at the shift. This figure measures association directly. F9 and F10 instead ask what the ordering of the confidences is worth once a hindsight-on-shuffled-labels floor is subtracted, and reach the same ranking and the same pair of failures. They are not two readings of one test.

## What it does NOT show

A correlation is not calibration: a method can order its answers correctly and still state numbers that are far too high, which is F5. It does not show the survival-time model is accurate — it is the least accurate method here while the household is stable. And it is measured on this one kind of disruption; the claim that the mechanism generalises rests on the arithmetic above rather than on a second regime.

## The numbers

Measured on the DAILY values, not read off the plotted line.

| series | settled 1–13 | sick 14–16 | spell 17–23 | back 24–26 | later 27–31 | change at the shift | is that change real |
|---|---|---|---|---|---|---|---|
| timetable that never forgets | 0.35 | -0.116 | 0.151 | 0.388 | 0.373 | -0.466 | yes |
| timetable with a three-day memory | 0.281 | -0.001 | 0.267 | 0.113 | 0.381 | -0.283 | yes |
| survival-time model | 0.367 | 0.433 | 0.357 | 0.286 | 0.48 | 0.066 | no |
| whole-log-in-the-prompt memory | 0.293 | 0.218 | 0.253 | 0.256 | 0.322 | -0.075 | no |
