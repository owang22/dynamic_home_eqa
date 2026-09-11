# Room-change travel cost: what a same-room discount buys a cost-aware policy

> **READ THIS FIRST — the conclusions here are provisional (owner, 2026-09-10).**
> The question set is about to change: queries will be redrawn to reflect
> how people actually ask, rather than the current uniform draw over
> objects and awake instants. Every number below is conditioned on the
> present query distribution, and two of the five answers are especially
> exposed to it:
>
> * **§4 (where the robot is when a question arrives)** is a property of
>   the patrol crossed with the query distribution and nothing else. Its
>   finding — that the robot's room is no more informative about the
>   answer than independence would give — will move when queries move,
>   and it is the ceiling on the whole effect. Do not build on it.
> * **§5 (the headline gap)** inherits that ceiling. The DIRECTION of
>   each curve should be robust (it follows from the price arithmetic),
>   but the magnitudes should not be quoted until the queries are settled.
>
> The mechanism results (§2 and §3 — that cost-blind policies convert
> their whole allowance into fewer looks, that cost-aware ones re-rank by
> `voi/cost` at the first non-zero price) are arithmetic on the policies
> and are not at risk from the query change.
>
> **Not run: the high-cost, compensated-budget arm.** `c` in
> {0, 2, 4, 6, 8, 10} with `budget = round(base * (1 + c))`, which holds
> the number of affordable cross-room looks constant and isolates the
> price RATIO (a same-room look is up to 11x cheaper) from plain
> starvation. It was specced, launched, and deliberately stopped for the
> same reason — it is not worth ~2 h of compute against a question set
> that is about to be replaced. To run it when the queries are settled:
>
> ```bash
> python -m baselines.room_change_cost_study --stage grid report figures \
>     --out results/room_change_cost_high --costs 0,2,4,6,8,10 \
>     --compensate-budget --workers 20
> ```
>
> The driver supports it directly (`--costs`, `--compensate-budget`, and
> `--beliefs` to add a belief to a finished grid without re-running the
> rest). A timing probe on the worst cell (PerpetuaStar, SequentialSearch,
> hh_001) put it at 90-222 s per episode, and at `c = 10, budget = 990`
> the policy spends 10.98 of its 11.0 per-question allowance, so the arm
> does bind rather than degenerating to NeverSense.

Sensing a receptacle in the room the robot already stands in costs 1;
sensing one anywhere else costs `1 + c`. One parameter, distance-free, and
at `c = 0` exactly the flat model the package had before. What a sense
REVEALS is unchanged, and the passive patrol is unchanged.

Inputs: the 10 test households of the split in
`results/voi_policies/provenance.json` (seed 0), on the 20 banks
re-exported with room maps into `banks/baselines/fleet_room_cost/`
(`bank_verification.md`: every one byte identical to
`banks/baselines/fleet/` except the two new header fields). Beliefs
LastObservation, PeriodicPersistence, PerpetuaStar; policies NeverSense,
SequentialSearch, ResolvableMassSense, VoIThresholdSense and
VoIBudgetPriceSense at their best configurations from
`results/voi_policies/` (`configs.json`); budgets 24 and 90 senses/day;
`c` in {0, 0.25, 0.5, 1, 2}. Every cell is 22 500 questions, so the 95%
Wilson interval on an accuracy is about ±0.006 and differences below
about 0.01 are noise. Produced by
`python -m baselines.room_change_cost_study`; tables in `grid.csv`,
`by_cost.csv`, `head_to_head.csv`, `arrival.csv`, `accuracy_by_day.csv`.

**Figures** (`--stage figures`; every point carries a 95% interval, and
`c` is drawn at equal spacing rather than to scale):

| file | the claim it carries | section |
|---|---|---|
| `accuracy_vs_cost.png` | everyone loses accuracy; the cost-aware policies usually lose least, and the one exception is a threshold that stops firing | 2 |
| `same_room_share.png` | only the cost-aware policies take the discount, and they take it all at the first non-zero price | 3 |
| `arrival.png` | the robot's room is no more informative about the answer than independence would give | 4 |
| `voi_gap_vs_cost.png` | the headline: the cost-aware minus cost-blind gap against `c` | 5 |

Intervals are Wilson on the cell's own denominator (questions for an
accuracy, senses for the same-room share) everywhere except
`voi_gap_vs_cost.png`. That figure compares two policies on the very same
questions, so it uses the PAIRED per-question difference — roughly half
the width an independence assumption would give, and the honest interval
for that comparison. Its numbers are in `gap_paired_ci.csv`.

**Only VoIThresholdSense and VoIBudgetPriceSense can see the price.** They
sense while `voi(r) >= lambda * cost(r)` and pick the receptacle
maximizing `voi(r) / cost(r)`. Every other policy orders candidates by
belief mass and spends until the budget will not cover the next sense,
exactly as before. That asymmetry is the experiment.

---

## 1. Regression at `c = 0`

**20 of 30 cells reproduce `results/voi_policies/grid.csv` exactly. The
other 10 — every VoI cell on PeriodicPersistence and PerpetuaStar — differ
by 0.0003 to 0.008. The difference is NOT this work's, and the c > 0
readings stand.** Full table in `regression.md`.

The evidence, because this is the check everything else rests on:

* Every cost-blind cell matches to all six decimals, on all three
  beliefs. So the beliefs, the banks, the split, the seeding and the
  harness's budget accounting are all reproducing the reference exactly.
* Every LastObservation cell matches, VoI cells included.
* The mismatching cells were re-run under the **current committed code,
  unmodified** (a clean `git archive HEAD` checkout, on the ORIGINAL
  `banks/baselines/fleet/` banks). It reproduces THIS STUDY's numbers
  exactly, to six decimals, on all seven cells tested — and not the
  reference csv's (`head_baseline.json`). For instance
  PerpetuaStar@24 VoIBudgetPriceSense(gamma=0.01), the largest gap: HEAD
  0.623067, this study 0.623067, reference 0.631378.
* Cause: `results/voi_policies/provenance.json` records commit `eb731bcd`
  with `git_dirty: true`, generated 2026-09-08T20:33. The Part B commit
  `230a2701` landed 3.6 h later, and `voi_sense.py` differs between the
  working state that produced the csv and the state that was committed
  (the file is unchanged from `230a2701` to HEAD). So the reference csv
  was produced by code that was never committed, and no commit
  reproduces it.

The check's purpose — "did the room-change cost change behaviour at
`c = 0`?" — is therefore answered NO, by a stronger test than the one
specified: agreement with code that exists, rather than with a file no
commit can regenerate. Two consequences worth acting on separately from
this brief: `results/voi_policies/`'s VoI rows are stale by up to 0.008
and should be regenerated before they are quoted again, and the same
dirty-tree provenance means its `findings.md` headline numbers carry the
same caveat.

---

## 2. As `c` rises: accuracy and senses per question

**Everyone loses accuracy, because travel eats budget that used to buy
looks. The cost-aware policies lose less, and lose it more slowly.** Task
accuracy at `c = 0` -> `c = 2`, with senses per question in parentheses;
`*` marks the two cost-aware policies.

| belief, budget | policy | c=0 | c=0.25 | c=0.5 | c=1 | c=2 | Δacc |
|---|---|---|---|---|---|---|---|
| LastObs 24 | SequentialSearch | 0.642 (0.27) | 0.633 (0.23) | 0.627 (0.20) | 0.620 (0.17) | 0.609 (0.13) | −0.033 |
| | ResolvableMass | 0.655 (0.24) | 0.645 (0.21) | 0.637 (0.19) | 0.632 (0.17) | 0.620 (0.14) | −0.035 |
| | \*VoIThreshold | 0.631 (0.20) | 0.628 (0.19) | 0.624 (0.18) | 0.620 (0.16) | 0.616 (0.13) | **−0.015** |
| | \*VoIBudgetPrice | 0.650 (0.25) | 0.638 (0.22) | 0.638 (0.22) | 0.635 (0.20) | 0.626 (0.16) | −0.024 |
| LastObs 90 | SequentialSearch | 0.706 (1.00) | 0.694 (0.85) | 0.687 (0.74) | 0.676 (0.60) | 0.662 (0.44) | −0.044 |
| | ResolvableMass | 0.806 (0.78) | 0.780 (0.71) | 0.765 (0.65) | 0.733 (0.56) | 0.697 (0.44) | −0.109 |
| | \*VoIThreshold | 0.677 (0.59) | 0.674 (0.54) | 0.674 (0.49) | 0.674 (0.43) | 0.666 (0.36) | **−0.011** |
| | \*VoIBudgetPrice | 0.705 (0.82) | 0.705 (0.78) | 0.702 (0.74) | 0.694 (0.66) | 0.682 (0.55) | −0.023 |
| Periodic 24 | SequentialSearch | 0.654 (0.27) | 0.644 (0.23) | 0.638 (0.20) | 0.629 (0.17) | 0.624 (0.12) | −0.030 |
| | ResolvableMass | 0.690 (0.21) | 0.683 (0.19) | 0.674 (0.18) | 0.663 (0.15) | 0.646 (0.11) | −0.044 |
| | \*VoIThreshold | 0.681 (0.24) | 0.678 (0.21) | 0.677 (0.19) | 0.670 (0.17) | 0.655 (0.13) | −0.026 |
| | \*VoIBudgetPrice | 0.668 (0.26) | 0.670 (0.20) | 0.663 (0.20) | 0.646 (0.19) | 0.642 (0.16) | −0.026 |
| Periodic 90 | SequentialSearch | 0.720 (1.00) | 0.708 (0.84) | 0.702 (0.74) | 0.689 (0.59) | 0.675 (0.44) | −0.045 |
| | ResolvableMass | 0.853 (0.96) | 0.816 (0.83) | 0.790 (0.73) | 0.748 (0.59) | 0.706 (0.44) | −0.147 |
| | \*VoIThreshold | 0.777 (0.85) | 0.768 (0.74) | 0.763 (0.68) | 0.757 (0.58) | 0.734 (0.44) | −0.043 |
| | \*VoIBudgetPrice | 0.750 (0.98) | 0.747 (0.88) | 0.736 (0.84) | 0.724 (0.74) | 0.708 (0.60) | −0.042 |
| Perpetua 24 | SequentialSearch | 0.601 (0.27) | 0.596 (0.22) | 0.590 (0.20) | 0.585 (0.16) | 0.574 (0.12) | −0.027 |
| | ResolvableMass | 0.617 (0.27) | 0.612 (0.23) | 0.606 (0.20) | 0.593 (0.16) | 0.586 (0.12) | −0.031 |
| | \*VoIThreshold | 0.631 (0.26) | 0.630 (0.23) | 0.628 (0.20) | 0.595 (0.13) | 0.562 (0.06) | **−0.069** |
| | \*VoIBudgetPrice | 0.623 (0.26) | 0.621 (0.21) | 0.612 (0.20) | 0.590 (0.19) | 0.582 (0.15) | −0.041 |
| Perpetua 90 | SequentialSearch | 0.644 (1.00) | 0.634 (0.83) | 0.631 (0.72) | 0.624 (0.57) | 0.613 (0.41) | −0.031 |
| | ResolvableMass | 0.681 (0.99) | 0.662 (0.86) | 0.648 (0.76) | 0.628 (0.62) | 0.612 (0.45) | −0.069 |
| | \*VoIThreshold | 0.717 (0.84) | 0.710 (0.78) | 0.709 (0.73) | 0.697 (0.66) | 0.684 (0.56) | −0.033 |
| | \*VoIBudgetPrice | 0.707 (0.99) | 0.695 (0.87) | 0.668 (0.81) | 0.647 (0.70) | 0.627 (0.55) | −0.080 |

NeverSense is 0.587 / 0.592 / 0.532 at every `c`, exactly — it never
senses, so the price cannot reach it. That is the arithmetic control.

Three things to read off this:

**The mechanism is budget, not behaviour.** Senses per question falls
roughly as `1/(1 + c)` for every cost-blind policy — SequentialSearch at
budget 90 goes 1.00, 0.85, 0.74, 0.60, 0.44, which is within a few
percent of `1/(1 + c)` scaled by the same-room share. It spends its full
allowance in COST at every `c` (0.267 and 1.000 per question,
`by_cost.csv`); what it buys with it shrinks.

**The heaviest spenders lose the most.** ResolvableMassSense at budget 90
is the biggest loser everywhere (−0.109, −0.147, −0.069) precisely because
it was converting nearly its whole allowance into senses at `c = 0`; there
is nothing to protect when the price rises. VoIThresholdSense, which was
already spending below the cap (0.59 and 0.85 senses/q against a 1.00
allowance), has slack to absorb the price and loses least.

**One cost-aware policy fails badly, and it is worth naming.**
VoIThresholdSense on PerpetuaStar@24 runs at `lambda = 0.2`, Part B's best
there. The test `voi >= lambda * cost` becomes `voi >= 0.6` at `c = 2`,
which almost nothing clears: senses/q collapses 0.26 -> 0.06, cost/q
0.261 -> 0.064 (it leaves three quarters of its budget unspent), and
accuracy falls to 0.562, below what SequentialSearch manages. A threshold
tuned at `c = 0` is not a threshold at `c = 2` — scaling `lambda` by cost
makes the rule cost-correct but leaves its calibration cost-dependent.
This is the clearest practical caveat in the study.

---

## 3. Fraction of senses taken without a room change

| belief, budget | policy | c=0 | c=0.25 | c=0.5 | c=1 | c=2 |
|---|---|---|---|---|---|---|
| LastObs 90 | SequentialSearch | 0.262 | 0.284 | 0.301 | 0.326 | 0.369 |
| | ResolvableMass | 0.317 | 0.342 | 0.355 | 0.382 | 0.425 |
| | \*VoIThreshold | 0.369 | **0.713** | 0.721 | 0.724 | 0.736 |
| | \*VoIBudgetPrice | 0.328 | **0.698** | 0.703 | 0.709 | 0.727 |
| Periodic 90 | SequentialSearch | 0.254 | 0.269 | 0.285 | 0.310 | 0.354 |
| | ResolvableMass | 0.271 | 0.276 | 0.290 | 0.315 | 0.353 |
| | \*VoIThreshold | 0.307 | **0.591** | 0.601 | 0.614 | 0.634 |
| | \*VoIBudgetPrice | 0.270 | **0.625** | 0.638 | 0.655 | 0.671 |
| Perpetua 90 | SequentialSearch | 0.221 | 0.226 | 0.234 | 0.246 | 0.273 |
| | ResolvableMass | 0.381 | 0.380 | 0.382 | 0.382 | 0.393 |
| | \*VoIThreshold | 0.370 | **0.557** | 0.582 | 0.612 | 0.662 |
| | \*VoIBudgetPrice | 0.387 | **0.551** | 0.554 | 0.562 | 0.586 |

Budget 24 has the same shape (`by_cost.csv`); the extreme is
PerpetuaStar@24 VoIThreshold, which reaches **1.000** at `c = 2` — by then
it senses only in the room it is standing in, which is the collapse
described above seen from the other side.

**The cost-aware policies do exactly what the model gives them room to
do**: a step change at the FIRST non-zero price (`c = 0.25` roughly
doubles their same-room share) and then a plateau. That step is the whole
mechanism — once a trip costs anything at all, `voi/cost` reorders the
candidate list in favour of what is already to hand, and pushing the price
higher barely reorders it further.

**The cost-blind policies are NOT flat, and the drift is real rather than
a bug.** SequentialSearch rises about +0.11 across the range (0.262 ->
0.369 at LastObs@90), ResolvableMassSense +0.05 to +0.11. Their *choice
sequence* per question is identical at every `c` — they cannot see the
price — but how much of that sequence they get to execute is not: a higher
price truncates it earlier, and the surviving prefix is the part where the
robot has not yet wandered away from where the patrol left it. So the
statistic drifts because the sample of senses changes, not because the
policy did. The two signals are easy to tell apart: the cost-blind drift
is gradual and monotone in `c`, the cost-aware jump happens entirely
between `c = 0` and `c = 0.25`. PerpetuaStar/ResolvableMass, which spends
its whole allowance at every price, is nearly flat (0.381 -> 0.393) — the
control that confirms the explanation.

---

## 4. Where the robot is when a question arrives

Read off NeverSense, which never senses: position there is the passive
patrol's alone, so this describes the SITUATION every policy faces rather
than any policy's behaviour. It is identical at every `c` and every
budget, as it must be.

Position at `t_query`, pooled over the 10 test households (room names are
pooled across houses, so this is a mix of same-named rooms, not one
floorplan):

    kitchen 0.233   living 0.160   bathroom 0.156   bedroom_1 0.122
    entry 0.119     bedroom_2 0.113  bedroom_3 0.048  bedroom 0.038
    bedroom_4 0.011

**How often the queried object's most likely receptacle is in that room:
0.200 (LastObservation), 0.189 (PeriodicPersistence), 0.183
(PerpetuaStar).** Out-of-house argmaxes are negligible (≤0.04%), as
expected after the negative-evidence migration. Figure: `arrival.png`.

The right reference for those numbers is not `1/n_rooms` — rooms are not
equally likely, the kitchen being visited twice as often as the entry —
but the **independence baseline**: per household, the inner product of the
marginal over the robot's room with the marginal over the argmax's room,
averaged over households. That is what the hit rate would be if position
and answer were unrelated. It is **0.182 / 0.182 / 0.184**, against the
observed 0.200 / 0.189 / 0.183 (`independence_baseline` in
`arrival.csv`).

**So the robot's position carries essentially no information about where
the answer is.** LastObservation is +0.018 above independence,
PeriodicPersistence +0.007, and PerpetuaStar is −0.001 — exactly on it.
The patrol goes where the routine goes and objects are where the routine
leaves them, but the two are not coupled tightly enough to be worth
anything: being where the patrol left you is as good as being placed at
random with respect to the question. Four questions in five need a trip
before the most likely receptacle can be checked at all, and no policy can
change that number — it is a property of the patrol and the question set.
This is the ceiling on the whole effect, and it is why the cost-aware
policies' gain is a matter of a few points rather than a transformation,
and why their same-room share plateaus around 0.6-0.74 instead of climbing
toward 1.

---

## 5. Does the VoI advantage appear on LastObservation?

This is the question the brief exists to answer. In `results/voi_policies/`
VoI LOST on LastObservation at 90/day by 0.100 — the belief whose
confidence is inflated, where one-step voi is below every lambda on the
73-93% of questions the belief calls near-certain. The room-change
discount is an opportunity that does not depend on those probabilities
being calibrated, so the prediction is that it should help there.

Best cost-aware minus best cost-blind, per cell, and how that gap MOVES
from `c = 0`:

| belief, budget | c=0 | c=0.25 | c=0.5 | c=1 | c=2 | moved |
|---|---|---|---|---|---|---|
| LastObs 24 | −0.005 | −0.007 | +0.000 | +0.002 | +0.006 | +0.011 |
| **LastObs 90** | **−0.100** | −0.075 | −0.063 | −0.040 | **−0.014** | **+0.086** |
| Periodic 24 | −0.009 | −0.005 | +0.003 | +0.007 | +0.009 | +0.018 |
| Periodic 90 | −0.076 | −0.049 | −0.027 | +0.009 | +0.028 | +0.104 |
| Perpetua 24 | +0.014 | +0.018 | +0.023 | +0.002 | −0.003 | −0.017 |
| Perpetua 90 | +0.036 | +0.049 | +0.060 | +0.070 | +0.071 | +0.035 |

**Yes, and it is the largest effect in the study — but it is a recovery,
not a win.** On LastObservation at 90/day the gap closes monotonically
from −0.100 to −0.014: five sixths of Part B's deficit is gone by `c = 2`.
At the 0.01 resolution 22 500 questions support, −0.014 is still a loss,
just barely; VoI does not overtake the resolvable-mass gate on this
belief at any price tested. At 24/day, where the deficit was only −0.005
to begin with, the crossover happens but every number in the row is within
noise.

The mechanism is visible in the same rows of section 2, and it is not the
one the brief anticipated. **The gap closes because the leader falls, not
because VoI climbs.** Across the whole range VoIBudgetPriceSense goes
0.705 -> 0.682 (−0.023) while ResolvableMassSense goes 0.806 -> 0.697
(−0.109); VoI's absolute accuracy at `c = 2` is still below its own value
at `c = 0`. Nobody gains from the price; the gate simply has far more to
lose.

Why the gate is the fragile one is the interesting part, and it is the
flip side of Part B's result. On this belief ResolvableMassSense is the
policy that spends on the *right* questions — the stale-but-confident ones
one-step voi will not touch — so its accuracy is strongly elastic in how
many senses it can afford, and cutting senses/q from 0.78 to 0.44 cuts
deeply. VoI's accuracy was already insensitive to its own sense count,
precisely because it was spending on the wrong questions; taking senses
away from a policy that was mis-allocating them costs little.
VoIThresholdSense is the extreme case: it declines marginal senses on its
own (0.588 cost/q at `c = 0` against a 1.000 allowance, still only 0.547
at `c = 2`) and loses just 0.011 across the whole range — the most
price-robust policy in the study and the least accurate of the four.

The same-room preference is real and immediate (section 3: 0.328 ->
0.698 at the first non-zero price) and it is what keeps VoI's own losses
small. But it is the smaller term. **The cost-aware advantage here is
robustness to the price, not exploitation of the discount — and a good
part of that robustness is inherited from under-spending, which is a
weakness at `c = 0` wearing a different hat.**

The pattern generalises: the gap moves toward the cost-aware policies in
5 of 6 cells, and monotonically in 4. The exception is PerpetuaStar@24
(+0.014 -> −0.003), which is the `lambda = 0.2` collapse of section 2 and
says nothing about cost-awareness in general — it says a fixed threshold
does not survive a change of price scale.

PerpetuaStar@90 is the cell where cost-awareness pays outright: already
ahead by +0.036 at `c = 0`, it reaches +0.071 at `c = 2`, and it is the
only cell where a cost-aware policy is clearly ahead across the whole
range. That remains Part B's finding — VoI is as good as the calibration
of the belief it reads — with the room-change cost widening it rather than
creating it.

---

## Caveats

1. **The passive patrol does not react to the policy.** A scheduled visit
   sets the robot's position to its own room regardless of where a sense
   has just sent it, so the robot effectively teleports between a sense
   and the next ambient visit. This is deliberate and it is the price of
   the study's central control: the banks must be frozen and identical
   across every policy under test, which is impossible if policy actions
   alter the observation stream. The consequence is that this study prices
   the *sense*, never the patrol, and a robot that had to walk its patrol
   route would face a different — and strictly harder — problem.
2. **`VoIBudgetPriceSense`'s controller counts senses, not cost.** Per the
   brief's "nothing else changes", `spend_rate` is senses per question
   while `budget_rate` is budget units per question; at `c > 0` these are
   not commensurable and the controller under-measures its own spend by
   roughly the average cost multiplier. The measured effect is that it
   stops modulating and simply runs into the cap: at budget 90 its cost/q
   is 0.85-1.00 at every `c` (against VoIThresholdSense's 0.55-0.94), and
   it carries the higher forced-answer rate of the two (0.10-0.17 against
   0.001-0.066). Its numbers above are therefore a *capped* policy's, not
   a budget-tracking one's. The one-line fix is to book `cost` rather than
   `1` in `_on_sense`; it was not made here because it changes the
   experiment rather than its plumbing.
3. **Forced-answer rates are non-monotone in `c` and mostly an artefact.**
   SequentialSearch@24 goes 0.000, 0.652, 0.410, 0.038, 0.079. The flag
   fires when a policy asks for a sense it cannot afford, and the policies'
   own guard is `budget_remaining <= 0`, which no longer catches "positive
   but unaffordable". At `c = 0.25` the day's budget ends on leftovers of
   0.25/0.50/0.75 that can buy nothing, so nearly every later question is
   flagged; at `c = 1` costs are 1 or 2 and a leftover of exactly 1 still
   buys a same-room look, so the rate drops tenfold. It measures leftover
   granularity, not a behavioural change, and the accuracy columns are
   unaffected.
4. **ON_PERSON is in the `person_check` pseudo-room** and the fleet's
   `round_robin_patrol` never visits it, so on these banks sensing
   ON_PERSON always pays the surcharge. One receptacle of 22-38.
5. **Configurations are Part B's, not re-tuned per `c`.** That is
   deliberate — the study varies the price, and re-tuning at each price
   would confound the two — but it is why section 2's `lambda = 0.2`
   collapse happens, and it means these numbers are a lower bound on what
   a cost-aware policy tuned at its operating price could do.
