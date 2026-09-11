# Oracle lookahead headroom check — no gap (corrected measurement)

**Verdict: no headroom.** With and without the ambient patrol, at
matched spend, the myopic frontier is at or above the lookahead one.
Per the brief the lookahead line stops here.

**This supersedes an earlier version of this file whose measurement was
invalid.** The first pass compared the two policies at a single
`lambda`, which put them at wildly different spend levels; its numbers
should not be quoted. The error and its diagnosis are recorded below
because the same trap applies to any future window-objective policy.

## The threshold bug (why the first pass measured nothing)

The policy values a sense as the current question's VoI plus the
discounted VoI of every scheduled question in the window:

    w(o', t') = 2^(-(t' - t) / 24h)
    value_raw(r) = voi_now(r) + sum over the window of w * voi(p_o', r)

At 90 questions/day over a 2-day window the discounts sum to **97.4
question-equivalents** against the current question's weight of 1.
Measured at real decision points (`periodic_persistence`, routine
banks):

| household | median voi_now | median window term | ratio | window term alone clears lambda=0.05 |
|---|---|---|---|---|
| hh_001 | 0.0009 | 0.480 | 490x | 99% of decisions |
| hh_003 | 0.0006 | 0.657 | 1138x | 99% |
| hh_009 | 0.0007 | 1.268 | 1646x | 100% |

So `value_raw / cost >= lambda` never bound: the policy degenerated
into "sense until the budget guard stops you, at whichever receptacle
covers the most upcoming objects" — a COVERAGE policy. It sensed ~21/day
against the myopic policy's 6-18 and lost 3-10 accuracy points. That
result measured coverage-vs-targeted sensing at mismatched spend, not
lookahead-vs-myopic.

Dividing by the total weight (now the default, `normalize_window`)
makes `value` an expected gain per question in the window, the scale
`lambda` was chosen on. It does not change WHICH receptacle is picked —
the denominator is constant across receptacles — only when to stop. But
it over-corrects in the other direction at `lambda = 0.05`: the mean
over ~97 questions is far below any single question's VoI, so the
oracle then sensed 0.1-1.8/day and lost 5-14 points. **No single
`lambda` can compare these two value scales**; only matched spend can.

## The valid measurement: accuracy vs realized spend

`baselines.oracle_lookahead_frontier` sweeps `lambda` per policy and
plots accuracy against realized senses/day, so the frontiers are
compared where the spend agrees.

**With the ambient patrol** (6 room visits/day) —
`results/oracle_lookahead_frontier_patrol/frontier.png`: the myopic
frontier is above the oracle's in all six panels at every spend level.
At hh_001, c = 0, ~21 senses/day: myopic 0.866 vs oracle 0.783.

**Without the ambient patrol** (banks re-exported with no patrol; only
the t=0 tour, so sensing is the sole source of evidence) —
`results/oracle_lookahead_frontier_nopatrol/frontier.png`. The frontier
collapses to two points: at `lambda <= 0.0005` both policies spend the
whole budget (21.4 senses/day), above it neither senses at all. There is
no intermediate operating point, and the reason turns out to disqualify
this arm of the experiment.

**The no-patrol banks give every belief exactly one observation per
object.** The t=0 initial tour sights all 35-45 objects once; with the
patrol removed nothing else ever arrives. `periodic_persistence` needs
`min_departures` observed departures to estimate a hazard, and with a
single sighting it has zero, so it takes its documented count-floor path
and returns the decayed-frequency distribution over one sighting —
one-hot on the tour location, with no mechanism to decay as time passes.
Measured over all 2250 questions of each household:

| | hh_001 | hh_003 | hh_009 |
|---|---|---|---|
| median confidence | 0.981 | 0.981 | 0.981 |
| share with confidence > 0.9 | 100% | 100% | 100% |
| median confidence WHEN WRONG | 0.981 | 0.981 | 0.981 |
| passive accuracy | 0.491 | 0.417 | 0.412 |
| median best VoI | 0.0009 | 0.0006 | 0.0007 |

0.981 is exactly `1 - floor_mass`: the belief is pinned on the tour
location for all 25 question days and is equally confident when wrong as
when right. Best VoI is constant at the floor probability (p90 equals
the median) — there is no variation for any policy to act on. So the
no-patrol arm did not test "does lookahead help without ambient
evidence"; it tested a belief that cannot represent uncertainty, and
both policies were reading noise. **Its numbers below should be treated
as a null instrument, not as evidence.** Re-running that arm needs a
belief that decays toward a prior with time since last sighting (or a
bank with enough sightings to clear the hazard floor).

At the one matched operating point (c = 0, both 21.4 senses/day, paired
day-clustered bootstrap):

| household | oracle − myopic | 95% CI |
|---|---|---|
| hh_001 | +0.016 | [−0.023, +0.054] |
| hh_003 | +0.006 | [−0.008, +0.020] |
| hh_009 | +0.001 | [−0.027, +0.030] |

All three straddle zero. Removing the patrol moves the gap from clearly
negative to indistinguishable from zero — consistent with lookahead
mattering more when ambient evidence is absent — but not to a gap.

## Is there a good middle setting? Sweeping the window weight

Two different knobs get confused here, and only one of them is a real
policy change:

* **Rescaling the value** (dividing by 97.4, or 3, or 10) is
  mathematically identical to multiplying `lambda` by the same number.
  The denominator does not depend on the receptacle, so it cannot change
  which one is picked — only when to stop. Sweeping it IS the `lambda`
  sweep already in the frontier study; there is nothing extra to find.
* **Truncating the horizon** so the window carries fewer
  question-equivalents DOES change which receptacle is picked, because
  it changes which future questions enter the sum. At 90 questions/day
  and a 24 h half-life the window carries
  `129.8 * (1 - 2^(-H/24))` question-equivalents, so:

  | horizon H | 0.1 h | 0.3 h | 0.81 h | 1.36 h | 2.77 h | 5.8 h | 48 h |
  |---|---|---|---|---|---|---|---|
  | question-equivalents | 0.37 | 1.12 | 3.0 | 5.0 | 10.0 | 20.0 | 97.4 |

Best accuracy over the `lambda` grid at each setting (weight 0 =
myopic), patrol banks:

| cell | 0 | 0.37 | 1.12 | 3.0 | 5.0 | 10.0 | 20.0 | 97.4 |
|---|---|---|---|---|---|---|---|---|
| hh_001 c=0 | **0.869** | 0.825 | 0.822 | 0.810 | 0.796 | 0.805 | 0.808 | 0.813 |
| hh_001 c=2 | **0.796** | 0.792 | 0.774 | 0.768 | 0.777 | 0.764 | 0.772 | 0.767 |
| hh_003 c=0 | **0.728** | 0.712 | 0.694 | 0.698 | 0.706 | 0.715 | 0.696 | 0.693 |
| hh_003 c=2 | **0.703** | 0.695 | 0.680 | 0.692 | 0.680 | 0.683 | 0.682 | 0.675 |
| hh_009 c=0 | **0.635** | 0.628 | 0.628 | 0.610 | 0.621 | 0.620 | 0.598 | 0.608 |
| hh_009 c=2 | 0.602 | 0.616 | **0.618** | 0.600 | 0.591 | 0.585 | 0.596 | 0.590 |

**There is no interior optimum.** Myopic is best in 5 of 6 cells; the
penalty appears at the very first nonzero weight (0.37 — a six-minute
horizon holding less than one upcoming question) and is then flat out to
97. The single exception, hh_009 at c=2, is +0.016 in one cell of six
and is not separable from noise.

That flatness is the mechanism. If the problem were "too much far
future", accuracy would peak at a small positive weight. It does not:
any weight on any future question diverts the sense away from the
receptacle that would resolve the question being scored right now, and
since every question is scored equally that diversion is a direct loss.
Upcoming questions have VoI of the same order as the current one, so the
future term does not add signal — it pulls the choice toward
"generally useful" receptacles and away from "resolves this one".
Lookahead can only pay when a single sense serves several queries better
than it serves one, which needs budget to be the binding constraint. At
these budgets the myopic policy's own optimum sits at 13-21 senses/day
against a 24 budget, so it is not.

## Answering the design question directly

Is a sense worth more for a question 10 minutes out than one 30 hours
out? Under this discount, by a factor of 2.4 (0.995 vs 0.420) — and
that is too flat. Ground-truth persistence on these banks:

| dt | 10 min | 1 h | 6 h | 12 h | 24 h | 30 h | 48 h |
|---|---|---|---|---|---|---|---|
| P(same location), hh_001 | 0.99 | 0.93 | 0.69 | 0.51 | 0.57 | 0.48 | 0.53 |
| discount 2^(−dt/24h) | 1.00 | 0.97 | 0.84 | 0.71 | 0.50 | 0.42 | 0.25 |

Persistence flattens near 0.5 rather than decaying — objects return to
home receptacles. But ~0.5 is also roughly what the belief predicts
unaided, so a sense 30 h ahead conveys almost nothing ABOVE the prior,
while a sense 10 minutes ahead is near-certain information the belief
lacks. The right discount is therefore not persistence but persistence
in excess of the belief's own confidence — much steeper than either
curve above. The brief's `anticipated_query_voi` already specifies the
better form ("discounted by the belief's own decay out to the forecast
time"); the flat 24 h half-life used here is the cruder stand-in, and it
systematically overvalues far-horizon questions.

## Caveat

Greedy over the window is a lower bound, and both failure modes above
(coverage degeneration, flat discount) are properties of this
diagnostic rather than of lookahead as an idea. A planner that valued
refuting a confident belief, or timed senses just before the query,
could still find gains this instrument cannot see. As measured — the
measurement the brief asked for — there is no headroom, so
`sense_room_on_arrival`, `stale_room_refresh` and
`anticipated_query_voi` should not be built without a new reason.
