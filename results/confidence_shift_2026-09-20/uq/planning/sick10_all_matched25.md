# Planning metric — sick10_all, matched ask rate 25% on lead days (ask costs [2.0, 4.0])

tau/k chosen per agent so lead-day ask rate = 25%; same threshold then applied to sick/return.

| agent | threshold | lead ask% | sick ask% | return ask% | lead cost(c=2.0) | lead cost(c=4.0) | sick cost(c=2.0) | sick cost(c=4.0) | return cost(c=2.0) | return cost(c=4.0) |
|---|---|---|---|---|---|---|---|---|---|---|
| none_tt | 0.356 | 23% | 19% | 5% | 3.26 | 3.72 | 4.27 | 4.66 | 2.26 | 2.36 |
| none_tt72 | 0.292 | 25% | 35% | 30% | 3.31 | 3.81 | 3.38 | 4.08 | 2.12 | 2.71 |
| none_lastseen | 0.981 | 20% | 20% | 20% | 9.81 | 10.21 | 11.04 | 11.44 | 9.51 | 9.91 |
| mart_tt72 | 0.292 | 25% | 45% | 38% | 3.31 | 3.81 | 2.55 | 3.46 | 2.04 | 2.81 |
| bma_tt | 0.349 | 25% | 32% | 7% | 3.15 | 3.65 | 3.55 | 4.20 | 2.21 | 2.34 |
| ocp_tt | 5 | 24% | 21% | 1% | 3.13 | 3.62 | 4.00 | 4.43 | 2.44 | 2.45 |
