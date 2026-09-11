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
no intermediate operating point because with no ambient evidence the
belief is uniformly confident — VoI is ~0.001 for nearly every question,
so the threshold is either under or over essentially all of them. That
cliff is itself the finding: one-step VoI cannot buy information when
the belief is confidently WRONG, which is exactly the regime a patrol-free
world creates.

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
