# Planning metric — sick10_all, matched ask rate 50% on lead days (ask costs [2.0, 4.0])

tau/k chosen per agent so lead-day ask rate = 50%; same threshold then applied to sick/return.

| agent | threshold | lead ask% | sick ask% | return ask% | lead cost(c=2.0) | lead cost(c=4.0) | sick cost(c=2.0) | sick cost(c=4.0) | return cost(c=2.0) | return cost(c=4.0) |
|---|---|---|---|---|---|---|---|---|---|---|
| none_tt | 0.516 | 50% | 46% | 25% | 2.42 | 3.42 | 3.67 | 4.60 | 2.06 | 2.56 |
| none_tt72 | 0.402 | 50% | 66% | 56% | 2.67 | 3.67 | 2.78 | 4.10 | 2.04 | 3.16 |
| none_lastseen | 0.982 | 41% | 40% | 41% | 7.56 | 8.38 | 8.36 | 9.16 | 7.29 | 8.10 |
| mart_tt72 | 0.402 | 50% | 71% | 62% | 2.67 | 3.67 | 2.25 | 3.67 | 2.00 | 3.24 |
| bma_tt | 0.495 | 50% | 63% | 26% | 2.39 | 3.39 | 2.82 | 4.08 | 2.03 | 2.54 |
| ocp_tt | 2 | 38% | 41% | 23% | 2.74 | 3.50 | 3.42 | 4.24 | 2.13 | 2.59 |
