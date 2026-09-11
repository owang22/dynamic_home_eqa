# Oracle lookahead headroom check — STOP: no gap found

Question: can sensing beyond the current query help at all? Answer from
this diagnostic: **no — the gap is inside noise at c = 2 and negative
at c = 0.** Per the brief, the lookahead line stops here.

## Setup

`OracleLookaheadSense` (handed the true query schedule; values a sense
as current-question VoI plus discounted VoI over every scheduled
question within 2 days; greedy; a future-only sense must leave half the
day's remaining pro-rata budget) vs the best myopic policy from the
room-change study (`VoIThresholdSense`, lambda = 0.05), same
`periodic_persistence` belief, routine-driven banks hh_001 / hh_003 /
hh_009 at their own budget (24/day), c in {0, 2}. Paired day-clustered
bootstrap, 95% CI.

## Result (oracle − myopic accuracy)

| household | c = 0 | c = 2 |
|---|---|---|
| hh_001 | −0.029 [−0.058, +0.001] | +0.004 [−0.027, +0.036] |
| hh_003 | −0.030 [−0.053, −0.009] | −0.000 [−0.015, +0.015] |
| hh_009 | −0.050 [−0.076, −0.026] | −0.017 [−0.045, +0.009] |

The oracle senses roughly twice as much as the myopic policy
(`oracle_budget_split.png`: most of its spend is future-only) and buys
nothing with it; at c = 0 the extra spend is actively harmful. An
unreserved first pass was worse still (−5 to −10 points): morning
lookahead exhausted the day's budget and starved the evening questions
— that failure is what the reserve guard in the policy now prevents,
and it is itself informative: on these banks, budget spent early on
anticipated queries is worth less than the same budget at the query.

## Why lookahead buys nothing here

One line each, not investigated further:

- The ambient patrol (6 room visits/day) plus the myopic policy's own
  senses already keep the belief fresh at the rate information decays;
  a pre-query sense is mostly a duplicate that is staler at query time.
- The one-step VoI formula cannot value refuting a confidently WRONG
  belief (sensing the believed receptacle has ~0 VoI), so the oracle
  never buys the senses that would fix the routine-displacement misses
  (the `towel_marisol` class of error).

## Caveat, stated plainly

Greedy over the window is a lower bound; a planner that reasoned about
refutation or timed senses just before the query could in principle
find gains this diagnostic cannot. But as measured — the measurement
the brief asked for — there is no headroom, and the lookahead policies
(`sense_room_on_arrival`, `stale_room_refresh`,
`anticipated_query_voi`) should not be built without a new reason.
