# What F9 does and does not support

## Its job in the argument

SUPPORTING, and technical. Establishes that the timetables' apparent gain from being allowed to decline is not coming from their confidence at all. It is the rigour behind F10 rather than a figure a reader needs to see.

## The claim

> Being allowed to decline is worth something to every method at the shift, but for the timetables that is not because their confidence knows anything. The value splits in two: what the best all-or-nothing choice gives, which needs no signal at all and pays whenever a method is wrong more often than right, and what the ORDER of the confidences adds on top. At the shift the timetable that never forgets is right 51.3% of the time, so declining is worth 2.07 to it on the level alone — and its ordering adds 0.37 against a hindsight-on-noise floor of 0.29, which is nothing. The three-day timetable is the same story (0.43 against 0.36). The survival-time model's ordering adds 2.70 against a floor of 0.52, and the LLM's 1.33 against 0.30. The honest contrast is not a big effect against a small one. It is a real effect against no measurable effect.

## What in the figure demonstrates it

The first-sick-days group. Both timetables' bars sit on their own floors; the survival-time model's stands well clear of it and the LLM's clears too.

## Why this happens

The same result by a second route, which is why it is stated as a finding rather than as one test. Correlating each method's stated confidence with whether it was actually right, inside each household, both timetables fall at the shift to something indistinguishable from zero while the survival-time model's is unchanged. One statistic subtracts a shuffled-label floor and the other measures association directly; they agree on which methods have a real ordering and on the timetables having none.

## What it does NOT show

It does not show the level part, which is real and is where the timetables' apparent gain comes from; those numbers are in the claim. It is not a deployable policy — the threshold is fitted after the fact on the very window being scored, which is why a floor is drawn at all. And a floor is not an error bar: it says what noise would give, not how uncertain this estimate is.

## The same quantity measured a stricter way

A stricter estimator gives the same ranking. Choosing ONE threshold for all ten households instead of one each, the totals are 0.33 for the timetable that never forgets, 0.40 for the three-day one, 2.83 for the survival-time model and 0.77 for the LLM. Its noise floor sits near 0.01, because a single policy applied to every household has far less freedom to chase noise, so on that estimator every bar clears its floor. The two agree on the ranking and disagree on the floor: that is a fact about the estimators rather than about the methods, and a reviewer who recomputes one of them should expect a different-looking number.

## The numbers

Measured on the DAILY values, not read off the plotted line.

| series | settled week 9-13 | first sick days 14-16 | rest of the spell 17-23 | first days back 24-26 | a week later 27-31 |
|---|---|---|---|---|---|
| timetable that never forgets — what the ordering adds | 0.14 | 0.37 | 0.33 | 0.54 | 0.92 |
| timetable that never forgets — noise floor for that | 0.04 | 0.29 | 0.08 | 0.12 | 0.1 |
| timetable that never forgets — the level part | 0.0 | 2.07 | 0.71 | 0.0 | 0.0 |
| timetable that never forgets — % right | 81.6 | 51.3 | 70.2 | 77.2 | 79.3 |
| timetable with a three-day memory — what the ordering adds | 0.3 | 0.43 | 0.14 | 0.29 | 0.62 |
| timetable with a three-day memory — noise floor for that | 0.05 | 0.36 | 0.03 | 0.32 | 0.08 |
| timetable with a three-day memory — the level part | 0.0 | 1.0 | 0.0 | 0.83 | 0.0 |
| timetable with a three-day memory — % right | 80.4 | 57.9 | 85.8 | 61.4 | 76.6 |
| survival-time model — what the ordering adds | 0.9 | 2.7 | 0.71 | 1.96 | 1.84 |
| survival-time model — noise floor for that | 0.15 | 0.52 | 0.07 | 0.52 | 0.25 |
| survival-time model — the level part | 0.06 | 0.67 | 0.0 | 0.42 | 0.26 |
| survival-time model — % right | 66.3 | 55.4 | 73.7 | 56.8 | 59.1 |
| LLM — what the ordering adds | 0.38 | 1.33 | 0.37 | 0.83 | 0.84 |
| LLM — noise floor for that | 0.08 | 0.3 | 0.06 | 0.16 | 0.1 |
| LLM — the level part | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| LLM — % right | 69.6 | 61.7 | 71.3 | 67.4 | 69.5 |
