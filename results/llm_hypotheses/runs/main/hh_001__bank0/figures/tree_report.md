# Tree arms — hh_001, main

Every number is from one episode (one household, one bank seed); a change over a few nodes is anecdote, and the tables say which.

## Node count and depth per day

- active · tree · tree_named · f0: nodes by day d0:4 d3:5 d6:5 d9:4 d12:4 d15:5 d18:5 d21:5 d24:5 d27:5; max depth reached 1
- active · tree_fixed · tree_named · f0: nodes by day d0:4 d3:4 d6:4 d9:4 d12:4 d15:4 d18:4 d21:4 d24:4 d27:4; max depth reached 0
- active · tree_fixed · tree_named · f0 · b0.5: nodes by day d0:4 d3:4 d6:4 d9:4 d12:4 d15:4 d18:4 d21:4 d24:4 d27:4; max depth reached 0
- active · tree · tree_anonymized · f0: nodes by day d0:4 d3:5 d6:4 d9:4 d12:4 d15:5 d18:5 d21:5 d24:5 d27:5; max depth reached 1
- active · tree_fixed · tree_anonymized · f0: nodes by day d0:4 d3:4 d6:4 d9:4 d12:4 d15:4 d18:4 d21:4 d24:4 d27:4; max depth reached 0
- passive · tree · tree_anonymized: nodes by day d0:4 d3:6 d6:6 d9:6 d12:5 d15:5 d18:5 d21:5 d24:5 d27:5; max depth reached 1
- passive · tree_fixed · tree_anonymized: nodes by day d0:4 d3:4 d6:4 d9:4 d12:4 d15:4 d18:4 d21:4 d24:4 d27:4; max depth reached 0
- passive · tree · tree_named: nodes by day d0:4 d3:5 d6:4 d9:4 d12:4 d15:4 d18:4 d21:4 d24:4 d27:4; max depth reached 1
- passive · tree_fixed · tree_named: nodes by day d0:4 d3:4 d6:3 d9:3 d12:3 d15:3 d18:3 d21:3 d24:3 d27:3; max depth reached 0

## Revisions: add_child versus add_root, by trigger

| arm | call (day, trigger) | ops returned | add_child applied | add_root applied | rejected | outcome |
|---|---|---|---|---|---|---|
| active · tree · tree_named · f0 | d3, scheduled | 1 | 1 | 0 | 0 | revised |
| active · tree · tree_named · f0 | d14, anomaly | 1 | 1 | 0 | 1 | revised |
| active · tree_fixed · tree_named · f0 | (no revision calls) | | | | | |
| active · tree_fixed · tree_named · f0 · b0.5 | (no revision calls) | | | | | |
| active · tree · tree_anonymized · f0 | d3, scheduled | 1 | 1 | 0 | 0 | revised |
| active · tree · tree_anonymized · f0 | d14, anomaly | 1 | 1 | 0 | 0 | revised |
| active · tree_fixed · tree_anonymized · f0 | (no revision calls) | | | | | |
| passive · tree · tree_anonymized | d3, scheduled | 2 | 2 | 0 | 0 | revised |
| passive · tree_fixed · tree_anonymized | (no revision calls) | | | | | |
| passive · tree · tree_named | d3, scheduled | 1 | 1 | 0 | 1 | revised |
| passive · tree_fixed · tree_named | (no revision calls) | | | | | |

## Tour-absent objects (11): first sighting, and whether the FINAL tree gives them a rest or a move

| object | class | first sighted (day) | active · tree · tree_named · f0 | active · tree_fixed · tree_named · f0 | active · tree_fixed · tree_named · f0 · b0.5 | active · tree · tree_anonymized · f0 | active · tree_fixed · tree_anonymized · f0 | passive · tree · tree_anonymized | passive · tree_fixed · tree_anonymized | passive · tree · tree_named | passive · tree_fixed · tree_named |
|---|---|---|---|---|---|---|---|---|---|---|---|
| backpack_mara | backpack | 3.4 | rest 1/5, move 0/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/3, move 0/3 |
| charger_mara | charger | 2.2 | rest 1/5, move 1/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |
| glasses_mara | glasses | 2.2 | rest 1/5, move 1/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |
| headphones_mara | headphones | 2.2 | rest 1/5, move 1/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |
| jacket_mara | jacket | 2.2 | rest 1/5, move 0/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |
| keys_mara | keys | 0.8 | rest 1/5, move 0/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 1/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |
| laptop_mara | laptop | 2.2 | rest 1/5, move 1/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |
| notebook_mara | notebook | 1.4 | rest 1/5, move 1/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 1/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |
| phone_mara | phone | 1.8 | rest 1/5, move 0/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |
| wallet_mara | wallet | 2.2 | rest 1/5, move 0/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |
| water_bottle_mara | water_bottle | 1.9 | rest 1/5, move 1/5 | rest 0/4, move 0/4 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 0/5, move 0/5 | rest 0/4, move 0/4 | rest 1/4, move 0/4 | rest 0/3, move 0/3 |

## Per revision: did the new node gain weight over the next 5 days?

| arm | day | trigger | op | node | labels | weight at creation → +5 d | subtree at creation → +5 d | gained |
|---|---|---|---|---|---|---|---|---|
| active · tree · tree_named · f0 | 3 | scheduled | add_child | p_3bd7 | single_resident_mara, student, weekend_getaways, kitchen_table_workspace, laptop_study | 0.015 → - | 0.015 → - | pruned/ended |
| active · tree · tree_named · f0 | 14 | anomaly | add_child | p_8b0f | single_resident_mara, commutes_weekday, home_empty_middays, kitchen_table_workspace, home_active_middays | 0.020 → 0.350 | 0.020 → 0.350 | yes |
| active · tree · tree_anonymized · f0 | 3 | scheduled | add_child | p_9223 | two_adults, both_commute, empty_weekday_daytime, kitchen_table_cluster, entry_table_items, couch_living_items | 0.009 → - | 0.009 → - | pruned/ended |
| active · tree · tree_anonymized · f0 | 14 | anomaly | add_child | p_7666 | two_adults, both_commute, empty_weekday_daytime, morning_kitchen_prep | 0.327 → 0.505 | 0.327 → 0.505 | yes |
| passive · tree · tree_anonymized | 3 | scheduled | add_child | p_a857 | two_adults, both_commute, empty_weekday_daytime, morning_staging | 0.171 → 0.624 | 0.171 → 0.624 | yes |
| passive · tree · tree_anonymized | 3 | scheduled | add_child | p_cdbd | two_adults, both_commute, empty_weekday_daytime, late_evening_gathering | 0.214 → 0.127 | 0.214 → 0.127 | no |
| passive · tree · tree_named | 3 | scheduled | add_child | p_81d0 | single_resident_mara, commutes_weekday, home_empty_middays, pen_at_drying_rack, no_umbrella_commute | 0.250 → 0.248 | 0.250 → 0.248 | no |

## Prunes and rejected responses

| arm | node prunes | subtree prunes | re-parented children | rejected ops (whole-response rejections) | reasons |
|---|---|---|---|---|---|
| active · tree · tree_named · f0 | 0 | 1 | 0 | 1 | node p_8b0f ×1 |
| active · tree_fixed · tree_named · f0 | 0 | 0 | 0 | 0 |  |
| active · tree_fixed · tree_named · f0 · b0.5 | 0 | 0 | 0 | 0 |  |
| active · tree · tree_anonymized · f0 | 0 | 1 | 0 | 0 |  |
| active · tree_fixed · tree_anonymized · f0 | 0 | 0 | 0 | 0 |  |
| passive · tree · tree_anonymized | 0 | 1 | 0 | 0 |  |
| passive · tree_fixed · tree_anonymized | 0 | 0 | 0 | 0 |  |
| passive · tree · tree_named | 0 | 1 | 0 | 1 | node p_dda3 ×1 |
| passive · tree_fixed · tree_named | 0 | 1 | 0 | 0 |  |

## Labels: final weights, settled, and name-matched recovery of the bank's premises

- active · tree · tree_named · f0: single_resident_mara 1.00, commutes_weekday 0.65, home_empty_middays 0.65, frequent_business_trips 0.23, home_sparse_weekdays 0.23, work_from_home 0.10, morning_yoga 0.10, kitchen_table_workspace 0.05. Settled: single_resident_mara. Recovery ({'composition': 'solo', 'work_pattern': 'works_away'}): composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.65)
- active · tree_fixed · tree_named · f0: single_resident_mara 1.00, commutes_weekday 0.67, home_empty_middays 0.67, frequent_business_trips 0.22, home_sparse_weekdays 0.22, work_from_home 0.09, morning_yoga 0.09, student 0.02. Settled: single_resident_mara. Recovery ({'composition': 'solo', 'work_pattern': 'works_away'}): composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.67)
- active · tree_fixed · tree_named · f0 · b0.5: single_resident_mara 1.00, commutes_weekday 0.65, home_empty_middays 0.65, frequent_business_trips 0.23, home_sparse_weekdays 0.23, work_from_home 0.10, morning_yoga 0.10, student 0.03. Settled: single_resident_mara. Recovery ({'composition': 'solo', 'work_pattern': 'works_away'}): composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.65)
- active · tree · tree_anonymized · f0: two_adults 0.64, both_commute 0.55, empty_weekday_daytime 0.55, single_adult 0.36, morning_kitchen_prep 0.30, works_from_home 0.20, weekday_desk_hours 0.20, commutes 0.16. Settled: none. Recovery ({'composition': 'solo', 'work_pattern': 'works_away'}): composition=single_adult (0.36); work_pattern=both_commute (0.55)
- active · tree_fixed · tree_anonymized · f0: two_adults 0.55, single_adult 0.45, both_commute 0.39, empty_weekday_daytime 0.39, works_from_home 0.28, weekday_desk_hours 0.28, commutes 0.17, evening_cooker 0.17. Settled: none. Recovery ({'composition': 'solo', 'work_pattern': 'works_away'}): composition=single_adult (0.45); work_pattern=both_commute (0.39)
- passive · tree · tree_anonymized: two_adults 0.74, both_commute 0.74, empty_weekday_daytime 0.74, late_evening_gathering 0.46, single_adult 0.26, works_from_home 0.15, weekday_desk_hours 0.15, commutes 0.11. Settled: none. Recovery ({'composition': 'solo', 'work_pattern': 'works_away'}): composition=single_adult (0.26); work_pattern=both_commute (0.74)
- passive · tree_fixed · tree_anonymized: two_adults 0.55, both_commute 0.45, empty_weekday_daytime 0.45, single_adult 0.45, works_from_home 0.27, weekday_desk_hours 0.27, commutes 0.18, evening_cooker 0.18. Settled: none. Recovery ({'composition': 'solo', 'work_pattern': 'works_away'}): composition=single_adult (0.45); work_pattern=both_commute (0.45)
- passive · tree · tree_named: single_resident_mara 1.00, commutes_weekday 0.93, home_empty_middays 0.93, pen_at_drying_rack 0.71, no_umbrella_commute 0.71, frequent_business_trips 0.05, home_sparse_weekdays 0.05, student 0.01. Settled: single_resident_mara, commutes_weekday, home_empty_middays. Recovery ({'composition': 'solo', 'work_pattern': 'works_away'}): composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.93)
- passive · tree_fixed · tree_named: single_resident_mara 1.00, commutes_weekday 0.76, home_empty_middays 0.76, frequent_business_trips 0.19, home_sparse_weekdays 0.19, student 0.05, weekend_getaways 0.05. Settled: single_resident_mara. Recovery ({'composition': 'solo', 'work_pattern': 'works_away'}): composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.76)
