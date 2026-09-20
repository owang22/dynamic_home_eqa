# situation_sim baselines · hh_s8

48 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 18/24 | 75% | 16 | 43.0 | 5 | 4/6 | 5/6 | 5/6 | 4/6 | 18/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 17/24 | 71% | 12 | 48.0 | 0 | 4/6 | 5/6 | 3/6 | 5/6 | 14/21 | 3/3 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.01) | 17/24 | 71% | 16 | 40.0 | 6 | 4/6 | 5/6 | 3/6 | 5/6 | 17/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.01) | 17/24 | 71% | 17 | 38.0 | 4 | 4/6 | 4/6 | 4/6 | 5/6 | 17/21 | 0/3 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.005) | 16/24 | 67% | 15 | 42.0 | 9 | 4/6 | 4/6 | 4/6 | 4/6 | 16/21 | 0/3 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 16/24 | 67% | 15 | 39.0 | 4 | 4/6 | 4/6 | 3/6 | 5/6 | 16/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 16/24 | 67% | 15 | 39.0 | 4 | 4/6 | 4/6 | 3/6 | 5/6 | 16/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 16/24 | 67% | 16 | 40.0 | 15 | 4/6 | 5/6 | 3/6 | 4/6 | 13/21 | 3/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.005) | 16/24 | 67% | 17 | 44.0 | 10 | 4/6 | 4/6 | 4/6 | 4/6 | 16/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.01) | 16/24 | 67% | 17 | 38.0 | 5 | 4/6 | 5/6 | 3/6 | 4/6 | 16/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 16/24 | 67% | 18 | 45.0 | 12 | 4/6 | 4/6 | 4/6 | 4/6 | 16/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.25,lambda0=0.05) | 16/24 | 67% | 18 | 45.0 | 12 | 4/6 | 4/6 | 4/6 | 4/6 | 16/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+SequentialSearch | 15/24 | 62% | 12 | 45.0 | 3 | 4/6 | 4/6 | 3/6 | 4/6 | 15/21 | 0/3 | - |
| MostFrequentLocation+SequentialSearch | 15/24 | 62% | 12 | 45.0 | 3 | 4/6 | 4/6 | 3/6 | 4/6 | 15/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 15/24 | 62% | 12 | 45.0 | 3 | 4/6 | 4/6 | 3/6 | 4/6 | 15/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+SequentialSearch | 15/24 | 62% | 13 | 43.0 | 6 | 4/6 | 4/6 | 3/6 | 4/6 | 15/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.005) | 15/24 | 62% | 16 | 43.0 | 12 | 4/6 | 4/6 | 4/6 | 3/6 | 15/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.01) | 15/24 | 62% | 16 | 40.0 | 11 | 5/6 | 5/6 | 3/6 | 2/6 | 12/21 | 3/3 | - |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 15/24 | 62% | 16 | 43.0 | 12 | 3/6 | 4/6 | 4/6 | 4/6 | 15/21 | 0/3 | - |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.25,lambda0=0.05) | 15/24 | 62% | 16 | 43.0 | 12 | 3/6 | 4/6 | 4/6 | 4/6 | 15/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.01) | 15/24 | 62% | 18 | 45.0 | 5 | 4/6 | 4/6 | 3/6 | 4/6 | 15/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.03) | 14/24 | 58% | 15 | 18.0 | 0 | 4/6 | 3/6 | 2/6 | 5/6 | 14/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.005) | 14/24 | 58% | 17 | 41.0 | 12 | 4/6 | 4/6 | 3/6 | 3/6 | 14/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.005) | 14/24 | 58% | 19 | 43.0 | 10 | 4/6 | 3/6 | 4/6 | 3/6 | 14/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.03) | 13/24 | 54% | 11 | 11.0 | 0 | 4/6 | 3/6 | 2/6 | 4/6 | 13/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 14 | 38.0 | 7 | 4/6 | 3/6 | 3/6 | 3/6 | 13/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.25,lambda0=0.05) | 13/24 | 54% | 16 | 43.0 | 12 | 3/6 | 4/6 | 3/6 | 3/6 | 13/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 13/24 | 54% | 18 | 42.0 | 17 | 3/6 | 4/6 | 3/6 | 3/6 | 13/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.25,lambda0=0.05) | 13/24 | 54% | 18 | 42.0 | 17 | 3/6 | 4/6 | 3/6 | 3/6 | 13/21 | 0/3 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.03) | 12/24 | 50% | 7 | 7.0 | 0 | 3/6 | 3/6 | 2/6 | 4/6 | 12/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.03) | 12/24 | 50% | 7 | 7.0 | 0 | 3/6 | 3/6 | 2/6 | 4/6 | 12/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 13 | 40.0 | 4 | 4/6 | 4/6 | 2/6 | 2/6 | 12/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 12/24 | 50% | 19 | 43.0 | 15 | 3/6 | 3/6 | 3/6 | 3/6 | 12/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.25,lambda0=0.05) | 12/24 | 50% | 19 | 43.0 | 15 | 3/6 | 3/6 | 3/6 | 3/6 | 12/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 3/6 | 3/6 | 1/6 | 4/6 | 11/21 | 0/3 | - |
| LastObservation+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 3/6 | 3/6 | 1/6 | 4/6 | 11/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 3/6 | 3/6 | 1/6 | 4/6 | 11/21 | 0/3 | - |
| MostFrequentLocation+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 3/6 | 3/6 | 1/6 | 4/6 | 11/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 3/6 | 3/6 | 1/6 | 4/6 | 11/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 3/6 | 3/6 | 1/6 | 4/6 | 11/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.03) | 11/24 | 46% | 6 | 6.0 | 0 | 3/6 | 3/6 | 2/6 | 3/6 | 11/21 | 0/3 | - |
| LastObservation+SequentialSearch | 11/24 | 46% | 7 | 25.0 | 1 | 3/6 | 4/6 | 2/6 | 2/6 | 11/21 | 0/3 | - |
| LastObservation+VoIBudgetPriceSense(gamma=0.1,lambda0=0.05) | 11/24 | 46% | 8 | 23.0 | 2 | 3/6 | 4/6 | 2/6 | 2/6 | 11/21 | 0/3 | - |
| LastObservation+VoIBudgetPriceSense(gamma=0.25,lambda0=0.05) | 11/24 | 46% | 8 | 23.0 | 2 | 3/6 | 4/6 | 2/6 | 2/6 | 11/21 | 0/3 | - |
| LastObservation+VoIThresholdSense(lambda=0.005) | 11/24 | 46% | 8 | 23.0 | 2 | 3/6 | 4/6 | 2/6 | 2/6 | 11/21 | 0/3 | - |
| LastObservation+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 8 | 23.0 | 2 | 3/6 | 4/6 | 2/6 | 2/6 | 11/21 | 0/3 | - |
| LastObservation+VoIThresholdSense(lambda=0.01) | 11/24 | 46% | 12 | 36.0 | 4 | 3/6 | 3/6 | 2/6 | 3/6 | 11/21 | 0/3 | - |
| LastObservation+VoIThresholdSense(lambda=0.03) | 10/24 | 42% | 5 | 5.0 | 0 | 3/6 | 2/6 | 2/6 | 3/6 | 10/21 | 0/3 | - |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | pan_shared | cupboard_k1 | 23/48 |
| q02 | helmet_felix | entry_hook_e1 | 48/48 |
| q03 | towel_felix | towel_rack_ba1 | 48/48 |
| q04 | phone_aisha | ON_PERSON | 3/48 |
| q05 | glasses_felix | nightstand_b1 | 48/48 |
| q06 | dog_leash_shared | entry_hook_e1 | 0/48 |
| q07 | wallet_aisha | entry_table_e1 | 48/48 |
| q08 | phone_aisha | ON_PERSON | 3/48 |
| q09 | shopping_bag_shared | pantry_shelf_k1 | 48/48 |
| q10 | dog_leash_shared | entry_hook_e1 | 36/48 |
| q11 | keys_felix | entry_floor_e1 | 3/48 |
| q12 | tablet_felix | nightstand_b1 | 42/48 |
| q13 | phone_aisha | bedroom_floor_b1 | 13/48 |
| q14 | bowl_aisha | cupboard_k1 | 42/48 |
| q15 | toiletry_bag_felix | bathroom_shelf_ba1 | 23/48 |
| q16 | hat_aisha | entry_hook_e1 | 37/48 |
| q17 | vacuum_cleaner_shared | coffee_table_l1 | 1/48 |
| q18 | skincare_felix | sink_ba_ba1 | 14/48 |
| q19 | keys_felix | entry_table_e1 | 45/48 |
| q20 | phone_aisha | ON_PERSON | 3/48 |
| q21 | glass_felix | sink_k1 | 31/48 |
| q22 | mug_felix | sink_k1 | 15/48 |
| q23 | shoes_felix | shoe_rack_e1 | 30/48 |
| q24 | keys_aisha | entry_table_e1 | 48/48 |
