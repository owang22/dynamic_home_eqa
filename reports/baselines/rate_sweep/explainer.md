# Reading the rate sweep

## What the words mean

**Observation rate.** The robot patrols the home on a fixed passive schedule: a *visit* goes to one room and inspects every receptacle in it. The fleet's standard schedule is 6 visits a day, which this sweep calls **1x**; 0.5x, 2x and 4x are 3, 12 and 24 visits a day. Nothing else about the household changes -- same homes, same object movements, same questions.

**Age of last sighting.** How long before the question was asked the patrol last saw that object anywhere. Every comparison is inside one age band, because a denser patrol makes sightings fresher and would otherwise flatter itself.

**Excluded.** After the object was last seen at a receptacle, a later visit inspected that receptacle and the object was not in it. The belief base class then rules that receptacle out until the object is sighted again, for every classical model.

**The four situations.** Each question is one of:

- **still there,
spot never re-checked** (`stayed, not excluded` in the generated tables)
- **came back:
spot was checked, found empty** (`stayed, EXCLUDED` in the generated tables)
- **moved away,
old spot never re-checked** (`moved, not excluded` in the generated tables)
- **moved away,
old spot checked, empty** (`moved, EXCLUDED` in the generated tables)

The first is where LastObs is right by construction and the survival models lose; the second is where every classical model is wrong by construction and the survival models win.

## The figures

1. `explain_mix_12-24h.png`, `explain_mix_1-2d.png` -- the mix of situations per home per rate. This is what the rate changes.
2. `explain_accuracy_12-24h.png`, `explain_accuracy_1-2d.png` -- accuracy inside each situation, per home and pooled with a Wilson 95% band. This is what the rate mostly does not change.
3. `explain_decomposition.png` -- the headline difference by rate, against what it would be if only the mix had changed and every situation's accuracy had stayed at its 1x value.

## The decomposition, in numbers

`observed` is the question-weighted PerpetuaStar minus LastObs difference in that band; `mix` and `within` sum to the change from 1x; `covered` is the share of questions whose situation had enough data (30+) to measure a within-situation change.

| age band | rate | observed | change vs 1x | from the mix | from within situations | covered |
|---|---|---|---|---|---|---|
| 12-24h | 0.5x | -0.092 [-0.108, -0.074] | -0.003 | +0.006 | -0.009 | 1.00 |
| 12-24h | 1x | -0.089 [-0.101, -0.077] | +0.000 | +0.000 | +0.000 | 1.00 |
| 12-24h | 2x | -0.137 [-0.191, -0.086] | -0.048 | +0.014 | -0.062 | 1.00 |
| 12-24h | 4x | -0.311 [-0.398, -0.189] | -0.223 | +0.009 | -0.231 | 1.00 |
| 1-2d | 0.5x | -0.080 [-0.091, -0.069] | -0.064 | -0.053 | -0.011 | 1.00 |
| 1-2d | 1x | -0.016 [-0.060, +0.041] | +0.000 | +0.000 | +0.000 | 1.00 |
| 1-2d | 2x | +0.059 [-0.007, +0.134] | +0.075 | +0.099 | -0.024 | 0.99 |
| 1-2d | 4x | -0.219 [-0.315, -0.106] | -0.203 | -0.068 | -0.135 | 0.98 |
| 2d+ | 0.5x | +0.049 [+0.017, +0.101] | +0.055 | +0.002 | +0.066 | 0.85 |
| 2d+ | 1x | -0.006 [-0.042, +0.043] | +0.000 | +0.000 | +0.000 | 1.00 |
| 2d+ | 2x | -0.093 [-0.168, +0.012] | -0.088 | -0.148 | +0.060 | 1.00 |
| 2d+ | 4x | -0.252 [-0.346, -0.159] | -0.246 | -0.284 | +0.038 | 0.92 |

