# Stage 1 gate report

question validation: n=192 index_counts=[49, 46, 52, 45] max_skew=0.036

| tier | qtype | mean_acc | acc(moved) | acc(stable) | mean_p_true | delta_t_R2 |
|---|---|---|---|---|---|---|
| b0_lastseen | location_now | 0.7593 | 0.1392 | 1.0000 | 0.7204 | 0.8634 |
| b0_lastseen | room_now | 0.7403 | 0.0713 | 1.0000 | 0.7389 | 0.8868 |
| b1_longmem | location_now | 0.7709 | 0.3982 | 0.9156 | 0.5447 | 0.4081 |
| b1_longmem | room_now | 0.6258 | 0.0917 | 0.8332 | 0.6095 | 0.2421 |
| b2_classdecay | location_now | 0.8252 | 0.3752 | 0.9998 | 0.6983 | 0.828 |
| b2_classdecay | room_now | 0.7417 | 0.0772 | 0.9996 | 0.7205 | 0.8874 |
| b3_perpetua_star(fremen) | location_now | 0.8154 | 0.4329 | 0.9638 | 0.5563 | 0.8451 |
| b3_perpetua_star(fremen) | room_now | 0.7651 | 0.3224 | 0.9369 | 0.5988 | 0.8818 |
| b3_perpetua_star(schedule_prior) | location_now | 0.8106 | 0.4372 | 0.9555 | 0.5599 | 0.8174 |
| b3_perpetua_star(schedule_prior) | room_now | 0.7597 | 0.3394 | 0.9228 | 0.6028 | 0.8405 |

## Δt-symmetry check
delta_t_R2 near 1.0 would mean the surface collapses to Δt (no time-of-day structure) — values well below 1 confirm the pair (t_seen, t_query) carries information Δt alone does not.
