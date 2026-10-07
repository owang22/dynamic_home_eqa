# Planning metric — sick10_owner, matched ask rate 25% on lead days (ask costs [2.0, 4.0])

tau/k chosen per agent so lead-day ask rate = 25%; same threshold then applied to sick/return.

| agent | threshold | lead ask% | sick ask% | return ask% | lead cost(c=2.0) | lead cost(c=4.0) | sick cost(c=2.0) | sick cost(c=4.0) | return cost(c=2.0) | return cost(c=4.0) |
|---|---|---|---|---|---|---|---|---|---|---|
| none_tt | 0.370 | 24% | 17% | 6% | 2.88 | 3.37 | 3.66 | 4.01 | 2.08 | 2.20 |
| none_tt72 | 0.309 | 25% | 27% | 27% | 2.90 | 3.40 | 3.08 | 3.63 | 1.92 | 2.47 |
| none_lastseen | 0.981 | 23% | 30% | 22% | 8.76 | 9.21 | 8.54 | 9.14 | 8.33 | 8.76 |
| mart_tt72 | 0.303 | 25% | 32% | 31% | 2.92 | 3.42 | 2.48 | 3.11 | 1.83 | 2.45 |
| bma_tt | 0.362 | 25% | 26% | 7% | 2.88 | 3.38 | 3.14 | 3.67 | 2.08 | 2.22 |
| ocp_tt | 4 | 22% | 18% | 1% | 2.83 | 3.27 | 3.65 | 4.01 | 2.17 | 2.20 |
