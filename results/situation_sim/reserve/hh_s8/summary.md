# situation_sim baselines · hh_s8

20 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 18/24 | 75% | 20 | 44.0 | 0 | 4/6 | 5/6 | 4/6 | 5/6 | 18/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[SequentialSearch] | 17/24 | 71% | 14 | 38.0 | 0 | 4/6 | 4/6 | 4/6 | 5/6 | 17/21 | 0/3 | - |
| MostFrequentLocation+Reserve(1)[SequentialSearch] | 17/24 | 71% | 14 | 38.0 | 0 | 4/6 | 4/6 | 4/6 | 5/6 | 17/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[SequentialSearch] | 17/24 | 71% | 14 | 41.0 | 0 | 4/6 | 4/6 | 4/6 | 5/6 | 17/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[SequentialSearch] | 17/24 | 71% | 14 | 38.0 | 0 | 4/6 | 4/6 | 4/6 | 5/6 | 17/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 17/24 | 71% | 14 | 35.0 | 0 | 4/6 | 5/6 | 3/6 | 5/6 | 17/21 | 0/3 | - |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 17/24 | 71% | 15 | 39.0 | 0 | 4/6 | 5/6 | 3/6 | 5/6 | 17/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 17/24 | 71% | 17 | 38.0 | 0 | 4/6 | 4/6 | 4/6 | 5/6 | 17/21 | 0/3 | - |
| MostFrequentLocation+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 17/24 | 71% | 18 | 42.0 | 0 | 3/6 | 5/6 | 4/6 | 5/6 | 17/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 17/24 | 71% | 21 | 45.0 | 0 | 3/6 | 5/6 | 4/6 | 5/6 | 17/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 13 | 37.0 | 0 | 4/6 | 4/6 | 3/6 | 5/6 | 16/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 13 | 31.0 | 0 | 4/6 | 4/6 | 3/6 | 5/6 | 16/21 | 0/3 | - |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 14 | 38.0 | 0 | 4/6 | 4/6 | 3/6 | 5/6 | 16/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 18 | 39.0 | 0 | 4/6 | 5/6 | 2/6 | 5/6 | 16/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 16/24 | 67% | 21 | 42.0 | 0 | 4/6 | 5/6 | 2/6 | 5/6 | 16/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[SequentialSearch] | 15/24 | 62% | 12 | 42.0 | 0 | 3/6 | 4/6 | 4/6 | 4/6 | 15/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 15/24 | 62% | 14 | 38.0 | 0 | 5/6 | 5/6 | 3/6 | 2/6 | 13/21 | 2/3 | - |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 15/24 | 62% | 18 | 42.0 | 0 | 3/6 | 5/6 | 3/6 | 4/6 | 15/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 13/24 | 54% | 16 | 34.0 | 0 | 4/6 | 5/6 | 2/6 | 2/6 | 13/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 12/24 | 50% | 17 | 41.0 | 0 | 3/6 | 4/6 | 3/6 | 2/6 | 12/21 | 0/3 | - |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | pan_shared | cupboard_k1 | 15/20 |
| q02 | helmet_felix | entry_hook_e1 | 20/20 |
| q03 | towel_felix | towel_rack_ba1 | 20/20 |
| q04 | phone_aisha | ON_PERSON | 1/20 |
| q05 | glasses_felix | nightstand_b1 | 20/20 |
| q06 | dog_leash_shared | entry_hook_e1 | 0/20 |
| q07 | wallet_aisha | entry_table_e1 | 20/20 |
| q08 | phone_aisha | ON_PERSON | 1/20 |
| q09 | shopping_bag_shared | pantry_shelf_k1 | 20/20 |
| q10 | dog_leash_shared | entry_hook_e1 | 20/20 |
| q11 | keys_felix | entry_floor_e1 | 9/20 |
| q12 | tablet_felix | nightstand_b1 | 20/20 |
| q13 | phone_aisha | bedroom_floor_b1 | 6/20 |
| q14 | bowl_aisha | cupboard_k1 | 20/20 |
| q15 | toiletry_bag_felix | bathroom_shelf_ba1 | 12/20 |
| q16 | hat_aisha | entry_hook_e1 | 18/20 |
| q17 | vacuum_cleaner_shared | coffee_table_l1 | 0/20 |
| q18 | skincare_felix | sink_ba_ba1 | 10/20 |
| q19 | keys_felix | entry_table_e1 | 17/20 |
| q20 | phone_aisha | ON_PERSON | 0/20 |
| q21 | glass_felix | sink_k1 | 15/20 |
| q22 | mug_felix | sink_k1 | 18/20 |
| q23 | shoes_felix | shoe_rack_e1 | 19/20 |
| q24 | keys_aisha | entry_table_e1 | 20/20 |
