# Planning metric — sick10_owner, matched ask rate 50% on lead days (ask costs [2.0, 4.0])

tau/k chosen per agent so lead-day ask rate = 50%; same threshold then applied to sick/return.

| agent | threshold | lead ask% | sick ask% | return ask% | lead cost(c=2.0) | lead cost(c=4.0) | sick cost(c=2.0) | sick cost(c=4.0) | return cost(c=2.0) | return cost(c=4.0) |
|---|---|---|---|---|---|---|---|---|---|---|
| none_tt | 0.544 | 50% | 45% | 29% | 2.27 | 3.27 | 3.11 | 4.02 | 1.91 | 2.49 |
| none_tt72 | 0.428 | 50% | 59% | 55% | 2.37 | 3.37 | 2.68 | 3.86 | 1.80 | 2.91 |
| none_lastseen | 0.982 | 49% | 50% | 48% | 6.85 | 7.84 | 6.39 | 7.39 | 6.53 | 7.50 |
| mart_tt72 | 0.421 | 50% | 60% | 55% | 2.40 | 3.40 | 2.30 | 3.49 | 1.73 | 2.83 |
| bma_tt | 0.519 | 50% | 59% | 29% | 2.29 | 3.29 | 2.49 | 3.67 | 1.95 | 2.52 |
| ocp_tt | 2 | 35% | 34% | 25% | 2.66 | 3.36 | 3.08 | 3.76 | 2.05 | 2.56 |
