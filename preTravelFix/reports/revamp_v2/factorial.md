# revamp_v2 factorial report (2x2: calendar x movement)

| arm | model | household | n_events | events_per_day | moves_per_object_day | hour_entropy | daily_fano | fano_all | carry_frac | top2 | dead_days | unbound_story_activities | fallback_days |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rule_based | claude-fable-5 | hh1 | 191 | 9.1 | 0.51 | 0.763 | 0.71 | 1.94 | 0.621 | 0.356 | 1 | - | - |
| rule_based | deepseek-v4-flash | hh1 | 169 | 8.05 | 1.01 | 0.586 | 0.7 | 0.72 | 0.302 | 0.586 | 0 | - | - |
| rule_based | deepseek-v4-flash | hh2 | 1624 | 77.33 | 1.93 | 0.845 | 5.01 | 4.49 | 0.284 | 0.24 | 0 | - | - |
| rule_based | deepseek-v4-flash | hh3 | 676 | 32.19 | 1.46 | 0.782 | 4.15 | 6.35 | 0.464 | 0.299 | 0 | - | - |
| rule_based | qwen3.6-35b-a3b-fp8 | hh1 | 294 | 14.0 | 1.56 | 0.724 | 0.76 | 0.88 | 0.265 | 0.32 | 0 | - | - |
| rule_based | qwen3.6-35b-a3b-fp8 | hh3 | 562 | 26.76 | 1.12 | 0.727 | 1.05 | 1.37 | 0.111 | 0.395 | 0 | - | - |
| rule_based | qwen3.8-27b | hh1 | 428 | 20.38 | 2.55 | 0.661 | 1.61 | 1.61 | 0.0 | 0.414 | 0 | - | - |
| rule_based | qwen3.8-27b | hh2 | 2094 | 99.71 | 3.84 | 0.858 | 3.78 | 3.67 | 0.015 | 0.212 | 0 | - | - |
| rule_based | qwen3.8-27b | hh3 | 2331 | 111.0 | 8.54 | 0.815 | 17.7 | 17.7 | 0.0 | 0.243 | 0 | - | - |
| rule_based | qwen3.8-27b | hh4 | 1047 | 49.86 | 1.25 | 0.864 | 7.59 | 10.74 | 0.289 | 0.266 | 0 | - | - |
| rule_based | qwen3.8-27b | hh5 | 769 | 36.62 | 3.05 | 0.858 | 10.98 | 11.24 | 0.036 | 0.696 | 0 | - | - |
| rule_based | qwen3.8-27b | hh6 | 1568 | 74.67 | 2.41 | 0.734 | 9.96 | 9.99 | 0.001 | 0.145 | 0 | - | - |
| rule_based | qwen3.8-27b | hh7 | 3846 | 183.14 | 4.58 | 0.828 | 6.55 | 6.59 | 0.104 | 0.199 | 0 | - | - |
| rule_based | qwen3.8-27b | hh8 | 622 | 29.62 | 1.85 | 0.78 | 4.13 | 4.13 | 0.0 | 0.387 | 0 | - | - |
| rule_based | qwen3.8-27b | hh10 | 8663 | 412.52 | 17.19 | 0.924 | 35.75 | 40.86 | 0.106 | 0.417 | 0 | - | - |
| freeform | deepseek-v4-flash | hh1 | 443 | 21.1 | 2.64 | 0.622 | 1.65 | 1.65 | 0.0 | 0.467 | 0 | - | - |
| story_driven | deepseek-v4-flash | hh1 | 509 | 24.24 | 3.03 | 0.831 | 2.03 | 2.03 | 0.0 | 0.54 | 1 | - | 0 |
| story_driven | deepseek-v4-flash | hh2 (NOT story-driven) | 455 | 21.67 | 0.54 | 0.728 | 22.18 | 22.18 | 0.0 | 0.136 | 0 | - | 21 |
| story_driven | deepseek-v4-flash | hh3 (NOT story-driven) | 733 | 34.9 | 1.59 | 0.768 | 10.54 | 10.54 | 0.0 | 0.256 | 1 | - | 7 |
| story_rules | deepseek-v4-flash | hh1 | 83 | 3.95 | 0.49 | 0.768 | 1.22 | 0.78 | 0.352 | 0.627 | 2 | 15 | 0 |
| story_rules | deepseek-v4-flash | hh3 | 425 | 20.24 | 0.92 | 0.593 | 1.47 | 2.48 | 0.425 | 0.445 | 0 | 19 | 0 |
| story_rules | qwen3.8-27b | hh1 | 107 | 5.1 | 0.64 | 0.386 | 0.78 | 0.78 | 0.0 | 0.673 | 2 | 18 | 0 |
| story_rules | qwen3.8-27b | hh2 | 1121 | 53.38 | 2.05 | 0.791 | 6.75 | 6.17 | 0.051 | 0.269 | 0 | 19 | 0 |
| story_rules | qwen3.8-27b | hh3 | 1555 | 74.05 | 5.7 | 0.795 | 5.92 | 5.92 | 0.0 | 0.25 | 0 | 14 | 0 |
| comparator | - | casas_aruba (real ADLs, invented objects) | 1027 | 48.9 | 3.26 | 0.884 | 5.09 | 5.09 | 0.0 | 0.309 | 0 | - | - |

Legend (all event statistics on the NON-CARRY basis — departure-carry
pickups/putdowns excluded; `carry_frac` is their share of all events and
`fano_all` the all-events Fano, so the basis is visible):
- n_events / events_per_day / moves_per_object_day: non-carry move counts.
- hour_entropy: hour-of-day entropy of move times, normalized by log 24.
- daily_fano: var/mean of daily non-carry move counts.
- top2: share of non-carry events owed to the two most-moved objects.
- dead_days: days with < 3 non-carry events while a resident was home
  awake >= 6 h.
- unbound_story_activities: story activities no object rule or reset_all
  names ("-" for arms with no story stage).
- fallback_days: days the story stage failed to author ("-" likewise).
  A household with > 30% fallback days is marked NOT story-driven.
- casas_aruba (casas/aruba/timeline_21d): its ACTIVITY stream is real
  CASAS free-living data; its OBJECT layer (inventory + activity->object
  binding) is INVENTED, with the per-bout probabilities that set move
  volume "tuned by feel" (casas/README.md). Treat it as a comparator for
  TIMING SCATTER only — hour_entropy and daily_fano inherit their
  character from the real intervals (that README's deterministic-rules
  run reproduces them: 0.74/1.92 -> 0.76/2.03). Its volume columns
  (n_events, events_per_day, moves_per_object_day) and object-identity
  columns (top2, twin_pairs, never_move) come from the invented layer and
  are NOT ground truth: read that row as one authored household, not a
  target.
