# Stage 0 gate report

episode: logs/dynbelief_ep049w (7 days, 42 objects, 42 receptacles)

| schedule | tier | map_err | moved | placed | elsewhere | log_loss | brier |
|---|---|---|---|---|---|---|---|
| round_robin | b0_lastseen | 0.5318 | 0.536 | 0.422 | 0.721 | 10.081 | 0.949 |
| round_robin | b1_longmem | 0.5499 | 0.569 | 0.451 | 0.721 | 2.697 | 0.719 |
| round_robin | b2_classdecay | 0.6119 | 0.639 | 0.422 | 0.940 | 7.118 | 0.911 |
| round_robin | b3_perpetua_star | 0.5334 | 0.539 | 0.425 | 0.721 | 8.635 | 0.797 |
| random_uniform | b0_lastseen | 0.5369 | 0.545 | 0.430 | 0.721 | 10.212 | 0.959 |
| random_uniform | b1_longmem | 0.5509 | 0.571 | 0.453 | 0.721 | 2.696 | 0.717 |
| random_uniform | b2_classdecay | 0.6173 | 0.648 | 0.431 | 0.940 | 6.235 | 0.892 |
| random_uniform | b3_perpetua_star | 0.5373 | 0.546 | 0.431 | 0.721 | 8.567 | 0.807 |

## Sanity ordering (b3 <= b2 <= b1 <= b0 map error)
DEVIATION on: ['random_uniform', 'round_robin'] — recorded, see metrics.
