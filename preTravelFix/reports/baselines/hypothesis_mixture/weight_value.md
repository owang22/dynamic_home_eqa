# What do the mixture weights actually buy?

Passive diet, no sensing. `learned` minus `uniform` is the value of knowing which hypothesis is right, and therefore the ceiling on what disambiguation sensing could buy. Particle rows show the spread of skill the weights have to work with.

## hh_001

| belief | passive accuracy |
|---|---|
| mixture (learned weights) | 0.6317 |
| mixture (uniform weights) | 0.6365 |
| last_observation | 0.6349 |
| most_frequent | 0.6317 |
| timetable | 0.6095 |
| markov1 | 0.6048 |
| periodic_persistence | 0.6381 |
| hierarchy_backoff | 0.6222 |
| smoothed_recency | 0.6381 |

learned - uniform: **-0.0048**
learned - best single particle: **-0.0063**

## hh_002

| belief | passive accuracy |
|---|---|
| mixture (learned weights) | 0.5714 |
| mixture (uniform weights) | 0.5730 |
| last_observation | 0.5730 |
| most_frequent | 0.5714 |
| timetable | 0.5540 |
| markov1 | 0.5333 |
| periodic_persistence | 0.5714 |
| hierarchy_backoff | 0.5651 |
| smoothed_recency | 0.5746 |

learned - uniform: **-0.0016**
learned - best single particle: **-0.0032**

