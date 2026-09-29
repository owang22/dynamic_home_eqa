# Does the 40-sighting cap cost accuracy?

Written 2026-09-28, after finding that the cap bites 5% of questions at four a day and 86% at 24
a day on the 50-day run, and worrying out loud that it might be what closes our arm's advantage
over last seen at high budgets. **It is not.** No new runs; everything below is on the same
households, from cells already on disk.

Scripts: `scripts/does_the_log_cap_cost_anything.py` and
`scripts/the_budget_trend_on_uncut_questions.py`. Raw output in
`does_the_log_cap_cost_anything.txt`.

## Why the obvious comparisons do not work

**Comparing budgets** does not isolate the cap: at four questions a day the cap bites 5% of
questions *and* the robot has seen little; at 24 it bites 75% *and* the robot has seen a lot.

**Comparing cut against uncut questions** does not either: a question is cut when the robot already
holds more than 40 sightings of that object, which happens to the objects it sees constantly — the
easy ones. Cut questions score better whatever the cap does (90.9% against 80.7% on the ten-home
run).

So both tests below use **last seen as the ruler**. It never reads the log, so its accuracy on the
same question measures how hard that question is, and the quantity of interest is our arm's *lead*
over it.

## Test 1: is our lead smaller where the cap bit?

Difference in differences, paired within household. A positive number means lead lost to the cap.

| run | first room right | found within 3 |
|---|---|---|
| ten homes, 8 a day | +1.1 (2 SE 4.1), 6 of 10 | +0.5 (2 SE 3.0), 6 of 10 |
| five wider homes, 24 a day | **−1.6 (2 SE 0.5), 0 of 5** | +0.1 (2 SE 3.6), 3 of 5 |
| five wider homes, 8 a day | −1.8 (2 SE 4.4), 1 of 5 | +3.0 (2 SE 3.1), 3 of 5 |
| three homes, 50 days, 24 a day | −1.3 (2 SE 11.1), 1 of 3 | +1.9 (2 SE 9.7), 2 of 3 |
| five wider homes, 4 a day | 14 cut questions in one home — cannot be tested |

Nothing clears 2 SE and the noise floor in the direction of a cost. The tightest estimate — the run
where the cap bites 75% of questions — points the other way: our lead is **1.6 points larger** on
the cut questions, in all five homes.

## Test 2: the step at exactly 40

The cap is a step. Questions holding 25 to 39 sightings against 41 to 60 holds familiarity roughly
fixed; last seen over the same two bands is the placebo, because it has no cap.

| run | our arm, first room right | last seen over the same bands |
|---|---|---|
| ten homes, 8 a day | +1.5 (2 SE 4.9) | +1.1 (2 SE 6.3) |
| five wider homes, 24 a day | +0.6 (2 SE 0.8) | −1.5 (2 SE 3.1) |
| five wider homes, 8 a day | +5.1 (2 SE 4.7) | +2.9 (2 SE 7.0) |
| three homes, 50 days | +4.1 (2 SE 12.0) | −0.7 (2 SE 16.1) |

Our arm is the same or slightly **better** above the cap in every run. Accuracy does not step down
where the dated lines stop.

## The test that settles it: the budget trend on questions the cap never touched

Our arm minus last seen, five wider homes, paired within household.

| questions a day | every question | only where nothing was cut |
|---|---|---|
| 4 | +4.4 / +5.0 | **+4.4 (2 SE 1.6, 5 of 5) / +5.3 (2 SE 2.6, 5 of 5)** |
| 8 | +3.5 / +2.6 | +2.8 (2 SE 3.1, 3 of 5) / +3.7 (2 SE 2.2, 4 of 5) |
| 24 | +1.2 / +0.1 | **+0.0 (2 SE 2.6, 2 of 5) / +0.1 (2 SE 3.9, 3 of 5)** |

**On questions where our arm saw its whole record, the advantage still collapses from +4.4 to +0.0
as the looking budget rises.** The cap is not the explanation for the budget result.

And the bias in this comparison runs the safe way. At 24 a day the uncut questions are the 914 about
objects seen at most 40 times — the *less* familiar ones, where a memory ought to help most. Our
arm is dead level there.

## What this test can and cannot see

Stated because a null from a comparison with no power says nothing. Feeding the same machinery two
splits whose answer is known, on the same five homes at 24 a day: our arm's lead over last seen does
not differ measurably between moved objects and the rest (+0.9, 2 SE 3.3), nor between illness days
and settled days on first room right (−0.9, 2 SE 3.2).

That is not the machinery failing — it is the finding. **At 24 questions a day our arm and last seen
are level on every subset tried**: cut and uncut, movers and not, inside the illness and outside it.
There is no lead left for any split to eat. Which is why the argument above rests on the
across-budget comparison of uncut questions rather than on a within-run split.

**What is still untested:** whether a *larger* window would help. Everything here says the cap costs
nothing given the 40 sightings that are shown — the newest 40 already cover the last 4 to 10 days
densely at high budgets, and the summary line still names the rooms and counts of everything older.
It cannot say that a 200-sighting window would not do better. That needs a run.
