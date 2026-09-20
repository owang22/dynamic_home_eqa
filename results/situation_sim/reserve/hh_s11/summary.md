# situation_sim baselines · hh_s11

20 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TimetableLookup(bin=1h,days=all)+Reserve(1)[SequentialSearch] | 17/24 | 71% | 14 | 44.0 | 0 | 6/6 | 4/6 | 4/6 | 3/6 | 17/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[SequentialSearch] | 16/24 | 67% | 13 | 43.0 | 0 | 6/6 | 4/6 | 3/6 | 3/6 | 16/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[SequentialSearch] | 16/24 | 67% | 14 | 44.0 | 0 | 6/6 | 4/6 | 3/6 | 3/6 | 16/20 | 0/4 | - |
| MostFrequentLocation+Reserve(1)[SequentialSearch] | 16/24 | 67% | 14 | 47.0 | 0 | 6/6 | 4/6 | 3/6 | 3/6 | 16/20 | 0/4 | - |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 16/24 | 67% | 14 | 29.0 | 0 | 6/6 | 3/6 | 4/6 | 3/6 | 16/20 | 0/4 | - |
| MostFrequentLocation+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 16/24 | 67% | 18 | 42.0 | 0 | 5/6 | 3/6 | 4/6 | 4/6 | 16/20 | 0/4 | - |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 16/24 | 67% | 18 | 42.0 | 0 | 5/6 | 3/6 | 4/6 | 4/6 | 16/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 16/24 | 67% | 21 | 45.0 | 0 | 5/6 | 2/6 | 5/6 | 4/6 | 16/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 16/24 | 67% | 22 | 46.0 | 0 | 6/6 | 2/6 | 4/6 | 4/6 | 16/20 | 0/4 | - |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 15/24 | 62% | 13 | 31.0 | 0 | 6/6 | 3/6 | 3/6 | 3/6 | 15/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 15/24 | 62% | 15 | 33.0 | 0 | 6/6 | 2/6 | 4/6 | 3/6 | 15/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 15/24 | 62% | 18 | 24.0 | 0 | 5/6 | 2/6 | 4/6 | 4/6 | 15/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 15/24 | 62% | 19 | 40.0 | 0 | 6/6 | 2/6 | 4/6 | 3/6 | 15/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 14/24 | 58% | 13 | 13.0 | 0 | 4/6 | 2/6 | 4/6 | 4/6 | 14/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 14/24 | 58% | 17 | 32.0 | 0 | 5/6 | 2/6 | 4/6 | 3/6 | 14/20 | 0/4 | - |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 13/24 | 54% | 10 | 10.0 | 0 | 4/6 | 2/6 | 3/6 | 4/6 | 13/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[SequentialSearch] | 13/24 | 54% | 12 | 48.0 | 0 | 3/6 | 4/6 | 3/6 | 3/6 | 13/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 12/24 | 50% | 9 | 9.0 | 0 | 4/6 | 2/6 | 2/6 | 4/6 | 12/20 | 0/4 | - |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 12/24 | 50% | 9 | 9.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 10/24 | 42% | 14 | 38.0 | 0 | 3/6 | 2/6 | 3/6 | 2/6 | 10/20 | 0/4 | - |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | spatula_shared | sink_k1 | 12/20 |
| q02 | vacuum_cleaner_shared | storage_floor_s1 | 20/20 |
| q03 | shoes_hana | entry_floor_e1 | 13/20 |
| q04 | wallet_priya | entry_table_e1 | 20/20 |
| q05 | glass_hana | sink_k1 | 16/20 |
| q06 | dog_leash_shared | entry_hook_e1 | 20/20 |
| q07 | phone_hana | ON_PERSON | 0/20 |
| q08 | remote_shared | armchair_l1 | 5/20 |
| q09 | bowl_hana | cupboard_k1 | 14/20 |
| q10 | book_priya | nightstand_b2 | 20/20 |
| q11 | phone_hana | ON_PERSON | 0/20 |
| q12 | jacket_priya | entry_hook_e1 | 15/20 |
| q13 | toiletry_bag_hana | bathroom_shelf_ba1 | 11/20 |
| q14 | phone_priya | ON_PERSON | 0/20 |
| q15 | glass_hana | counter_k1 | 11/20 |
| q16 | bowl_hana | cupboard_k1 | 20/20 |
| q17 | spatula_shared | drawer_k_k1 | 14/20 |
| q18 | shoes_hana | shoe_rack_e1 | 15/20 |
| q19 | phone_hana | ON_PERSON | 0/20 |
| q20 | blanket_shared | bed_b1 | 0/20 |
| q21 | serving_dish_shared | cupboard_k1 | 19/20 |
| q22 | recipe_book_shared | pantry_shelf_k1 | 15/20 |
| q23 | wallet_priya | entry_table_e1 | 20/20 |
| q24 | snack_bowl_shared | sink_k1 | 13/20 |
