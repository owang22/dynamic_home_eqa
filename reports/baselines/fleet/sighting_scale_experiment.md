# Does scaling the observation budget with household size fix the fleet?

Test of the Cause-1 hypothesis in `failures.md`: the discriminative
collapse on 11 of 12 banks is the fixed 10 sightings/day meeting
inventories 2-3x larger than the one that rate was calibrated on, not a
defect in the households. Prediction: make sightings proportional to
inventory and the belief spread should open.

**Verdict: the diagnosis is confirmed, the first proposed dosage was
wrong, and fixing this gate exposes the next one.** Discriminative
failures fall from 11/12 to 1/12. Passing banks go from 1 to 2. The
residual blocker is `not_impossible`, and it is now partly *caused* by
the fix.

## The dosage probe

Four households exported at several per-object sighting rates, measuring
only the NeverSense panel accuracies the discriminative gate reads
(spread must exceed 0.03):

| bank | objects | r=0.5 | r=1.0 | r=2.0 | r=4.0 |
|---|---|---|---|---|---|
| revamp_v1 hh1 | 17 | 0.027 | **0.049** | 0.112 | 0.162 |
| storyfirst hh10 | 28 | 0.017 | **0.054** | 0.117 | 0.184 |
| storyfirst hh9 | 51 | 0.029 | **0.051** | 0.130 | 0.146 |
| storyfirst hh4 | 53 | 0.011 | **0.034** | 0.070 | 0.165 |

Spread rises monotonically with evidence on every bank, so this was a
**dosage** problem, not a structural one: the three panel beliefs are not
inherently indistinguishable on these worlds, they were merely being
starved into agreement. But `failures.md` proposed 0.5 sightings per
object per day, and the table shows 0.5 is **below** the gate on all four
— it roughly doubles the spread and still lands at 0.01-0.03. The rate
that works is **1.0/object/day**. (0.5 was derived from hh1's passing
10/day over 17 objects; that arithmetic ignored that ~15% of sightings
are dropped as unobservable when the object is out of the house, so hh1's
effective rate was never 0.59.)

Confirmation that 0.5 was too low: at r=0.5 the calibration bank hh1
itself REGRESSED from passing to failing discriminative (0.052 -> 0.027),
because the rule handed it less evidence than the 10/day it passed with.

## Fleet at the corrected rate

Variant C — sightings 1.0/object/day, budget 1.6/sensable receptacle
(hh1's 24 senses over 15 sensable receptacles), everything else the
shared config unchanged:

| bank | spread base → C | passive best base → C | not_impossible margin base → C | gates at C |
|---|---|---|---|---|
| revamp_v1 hh1 | 0.052 → 0.049 | 0.580 → 0.588 | +0.174 → +0.185 | **PASS** |
| revamp_v1 hh3 | 0.006 → 0.012 | 0.619 → 0.656 | +0.012 → +0.020 | stationarity, not_trivial, not_impossible, discriminative |
| storyfirst hh1 | 0.022 → 0.069 | 0.517 → 0.644 | +0.136 → +0.099 | stationarity, not_impossible |
| storyfirst hh10 | 0.001 → 0.054 | 0.479 → 0.577 | +0.215 → +0.170 | **PASS** |
| storyfirst hh2 | 0.006 → 0.051 | 0.486 → 0.541 | +0.079 → +0.063 | not_impossible |
| storyfirst hh3 | 0.012 → 0.048 | 0.507 → 0.584 | +0.081 → +0.093 | stationarity, not_impossible |
| storyfirst hh4 | 0.003 → 0.034 | 0.452 → 0.499 | +0.053 → +0.121 | not_impossible |
| storyfirst hh5 | 0.006 → 0.062 | 0.401 → 0.540 | +0.096 → +0.061 | not_impossible |
| storyfirst hh6 | 0.004 → 0.030 | 0.423 → 0.478 | +0.033 → +0.076 | not_impossible |
| storyfirst hh7 | 0.015 → 0.075 | 0.594 → 0.674 | +0.123 → +0.115 | stationarity, not_trivial, not_impossible |
| storyfirst hh8 | 0.010 → 0.062 | 0.541 → 0.617 | +0.138 → +0.125 | stationarity, not_impossible |
| storyfirst hh9 | 0.004 → 0.051 | 0.567 → 0.679 | +0.093 → +0.065 | stationarity, not_trivial, not_impossible |

Failure counts across the fleet:

| gate | base | variant C |
|---|---|---|
| stationarity | 6 | 6 |
| not_trivial | 0 | **3** |
| not_impossible | 10 | 10 |
| discriminative | **11** | **1** |
| banks passing all six | 1 | 2 |

## What the residual failures mean

**The gates pull against each other, and stationarity is upstream of
both survivors.** More evidence per object raises passive accuracy
(every bank's "passive best" column rises, by up to +0.14 on hh5 and
hh1). That is fine on a bank whose world genuinely moves, but on a
stationary bank passive accuracy runs straight at the `not_trivial`
ceiling of 0.65 — and the three banks that newly fail not_trivial
(revamp_v1 hh3 0.656, hh7 0.674, hh9 0.679) are all banks that were
ALREADY failing stationarity. They are not victims of the sighting rate;
they are stationary worlds where enough evidence lets memory solve them,
which is exactly what `not_trivial` exists to catch.

The same rise is why `not_impossible` did not improve in count: the gate
asks search to beat the best passive belief by 0.15, so lifting passive
lifts the bar. Budget scaling did buy real margin where the house is
genuinely churny (hh4 +0.053 → +0.121, hh6 +0.033 → +0.076), and lost
ground where passive rose faster than search could (hh5, hh1, hh10).

## Recommended sequence for the generation workstream

1. **Fix stationarity first** (the content problem in `failures.md`
   Cause 3: chore/utility objects with movement rules that never fire).
   It is upstream of both remaining gates — it inflates passive accuracy,
   which eats the not_trivial headroom and the not_impossible margin.
2. **Then adopt sightings = 1.0/object/day** as the shared rule. It is
   the measured feasible point: it clears discriminative everywhere while
   leaving passive accuracy under the not_trivial ceiling on every bank
   whose world actually moves.
3. **Then re-tune budget** against the repaired banks. 1.6/sensable
   receptacle is a reasonable starting rule but its effect is entangled
   with stationarity and should not be fixed until step 1 lands.

Not adopted into `src/baselines/configs/fleet.yaml` yet: changing the
shared config changes what every previously recorded gate reading means,
and step 1 will move these numbers again. The scaling rules themselves
ARE implemented (`sightings_per_object_day`,
`budget_per_sensable_receptacle` in `baselines.export_bank.export` and
the fleet config), so adopting it is a two-line config edit once the
content fixes land.

Reproduce: the variant configs and their fleet outputs are regenerable
with `python -m baselines.cli fleet --config <variant>.yaml`; the dosage
probe measures NeverSense only and takes about a minute.
