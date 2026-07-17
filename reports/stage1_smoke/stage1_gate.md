# Stage 1 gate report

question validation: n=64 index_counts=[24, 15, 14, 11] max_skew=0.203

| tier | qtype | mean_acc | mean_p_true | n | delta_t_R2 |
|---|---|---|---|---|---|
| b0_lastseen | location_now | 0.7088 | 0.6731 | 364 | 0.4781 |
| b0_lastseen | room_now | 0.6978 | 0.6978 | 364 | 0.6168 |
| b3_perpetua_star(fremen) | location_now | 0.6429 | 0.3996 | 364 | 0.0761 |
| b3_perpetua_star(fremen) | room_now | 0.6319 | 0.4824 | 364 | 0.1182 |
| b3_perpetua_star(schedule_prior) | location_now | 0.6099 | 0.3760 | 364 | 0.2685 |
| b3_perpetua_star(schedule_prior) | room_now | 0.6126 | 0.4607 | 364 | 0.2147 |

## Δt-symmetry check
delta_t_R2 near 1.0 would mean the surface collapses to Δt (no time-of-day structure) — values well below 1 confirm the pair (t_seen, t_query) carries information Δt alone does not.
