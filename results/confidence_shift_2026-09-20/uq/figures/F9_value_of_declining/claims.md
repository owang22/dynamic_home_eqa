# What F9 does and does not support

## The claim

> At the shift, being allowed to decline is worth almost nothing to the timetables (+0.3 and +0.4) and a great deal to the survival-time model (+2.8). the survival-time model scores BELOW both timetables while the world is stable: it is not the better model, it is the only one whose uncertainty is worth acting on.

## What in the figure demonstrates it

The first-sick-days group. the survival-time model gains 2.8 points from being allowed to decline, against 0.3 for the timetable that never forgets, 0.4 for the timetable with a three-day memory and 0.8 for the whole-log-in-the-prompt memory. On the first days back the pattern repeats: the survival-time model 1.4, everything else at or below 1.4.

## Why this happens

WHY declining is worth so much to one method and so little to the others. A rule that declines when confidence is low can only help if confidence still predicts correctness. In the settled weeks all three are about equally good at that: the correlation between what a method claims and whether it is right runs +0.28 to +0.37. At the shift both timetables stop predicting — the timetable that never forgets falls -0.47 and the three-day one -0.28, both clearing the bar, and what is left of either cannot be told from zero. The survival-time model's does not move (+0.07, not distinguishable from no change) and stays at +0.43, which DOES differ from zero. That one fact explains the inversion, the value of declining, and why a confidence signal that barely moves can still be worth acting on.

It also predicts what the return should do, and the prediction holds. The timetable that never forgets, which does not break when the old routine comes back, regains its footing immediately (+0.39); the three-day timetable, which does break there, is still not predicting (+0.11, not distinguishable from zero) until a week later. The survival-time model's accuracy breaks at both boundaries as much as anyone's and its confidence keeps tracking anyway — which is the point: knowing you are wrong is separable from being right.

## What it does NOT show

This is not a claim that the survival-time model is the better model — F8's settled-week numbers show it scoring 4.6 against the timetables' 7.7 and 7.6. The claim is narrower and stranger: it is the worst forecaster of the four and the only one whose uncertainty is worth acting on. The thresholds are also chosen with hindsight, which strengthens the negative half — even given the answers in advance, declining buys the counters almost nothing exactly when it would matter.

## A hypothesis that was tested and failed

A hypothesis worth recording because a reader will arrive with it, as we did. The coordinator proposed that the survival-time model's confidence is a function of how long its evidence has stood, so that at a shift the objects whose placement had just changed would be the ones with the oldest supporting evidence, and its confidence would fall on precisely the questions it was about to get wrong; and that a timetable, whose confidence reflects how regular the past was, would do the opposite and be MOST confident on the objects that moved. Both halves were tested on the ten households and both failed. Its confidence is not lower on the objects that moved but 4.5 points higher, which is not distinguishable from no difference, and its accuracy on those objects is 16.3 points HIGHER — a model of displacement doing its job rather than a defect. Its confidence RISES with the age of its evidence (+0.13 ± 0.03) rather than falling, which is also correct for it: its hazard is lognormal and therefore decreasing, so the longer a thing has sat undisturbed the longer it expects it to stay. And the timetable is not most confident on the objects that moved (−2.4, not distinguishable). The mechanism is not about WHICH objects; it is the one above.

## The numbers

Measured on the DAILY values, not read off the plotted line.

| series | settled week 9-13 | first sick days 14-16 | rest of the spell 17-23 | first days back 24-26 | a week later 27-31 |
|---|---|---|---|---|---|
| timetable that never forgets | 0.04 | 0.333 | 0.186 | 0.167 | 0.44 |
| timetable with a three-day memory | 0.1 | 0.4 | 0.057 | 0.033 | 0.18 |
| survival-time model | 0.32 | 2.833 | 0.343 | 1.433 | 1.5 |
| whole-log-in-the-prompt memory | 0.3 | 0.767 | 0.3 | 0.433 | 0.6 |
