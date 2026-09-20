# situation_sim baselines · hh_s11

42 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 17/24 | 71% | 14 | 38.0 | 17 | 4/6 | 4/6 | 4/6 | 5/6 | 16/21 | 1/3 | - |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 16/24 | 67% | 13 | 46.0 | 2 | 5/6 | 4/6 | 3/6 | 4/6 | 15/21 | 1/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 14 | 38.0 | 18 | 4/6 | 4/6 | 4/6 | 4/6 | 16/21 | 0/3 | - |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 15 | 39.0 | 16 | 4/6 | 4/6 | 3/6 | 5/6 | 15/21 | 1/3 | - |
| LastObservation+SequentialSearch | 15/24 | 62% | 1 | 4.0 | 0 | 4/6 | 5/6 | 3/6 | 3/6 | 15/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 15/24 | 62% | 16 | 34.0 | 2 | 5/6 | 3/6 | 2/6 | 5/6 | 15/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 19 | 43.0 | 14 | 4/6 | 4/6 | 3/6 | 4/6 | 15/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 19 | 43.0 | 15 | 4/6 | 4/6 | 3/6 | 4/6 | 15/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 14/24 | 58% | 12 | 45.0 | 5 | 4/6 | 3/6 | 3/6 | 4/6 | 13/21 | 1/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+SequentialSearch | 14/24 | 58% | 12 | 45.0 | 2 | 5/6 | 4/6 | 2/6 | 3/6 | 13/21 | 1/3 | - |
| MostFrequentLocation+SequentialSearch | 14/24 | 58% | 13 | 46.0 | 2 | 5/6 | 4/6 | 2/6 | 3/6 | 13/21 | 1/3 | - |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 14/24 | 58% | 14 | 38.0 | 18 | 4/6 | 4/6 | 3/6 | 3/6 | 14/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 11 | 11.0 | 0 | 5/6 | 4/6 | 2/6 | 2/6 | 13/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+SequentialSearch | 13/24 | 54% | 13 | 46.0 | 2 | 5/6 | 3/6 | 2/6 | 3/6 | 13/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 13/24 | 54% | 18 | 48.0 | 5 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 13/24 | 54% | 18 | 48.0 | 5 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| LastObservation+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| LastObservation+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| MostFrequentLocation+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 3 | 3.0 | 0 | 4/6 | 4/6 | 1/6 | 3/6 | 12/21 | 0/3 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 5 | 5.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 5 | 5.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 6 | 6.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 6 | 6.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 7 | 7.0 | 0 | 3/6 | 4/6 | 2/6 | 3/6 | 12/21 | 0/3 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 12 | 21.0 | 0 | 4/6 | 3/6 | 1/6 | 4/6 | 12/21 | 0/3 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 5 | 5.0 | 0 | 3/6 | 4/6 | 2/6 | 2/6 | 11/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 13 | 37.0 | 22 | 3/6 | 3/6 | 3/6 | 2/6 | 11/21 | 0/3 | - |
| LastObservation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 2 | 5.0 | 0 | 4/6 | 3/6 | 1/6 | 2/6 | 10/21 | 0/3 | - |
| LastObservation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 10/24 | 42% | 2 | 5.0 | 0 | 4/6 | 3/6 | 1/6 | 2/6 | 10/21 | 0/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 14 | 41.0 | 15 | 3/6 | 2/6 | 2/6 | 3/6 | 9/21 | 1/3 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.05) | 9/24 | 38% | 3 | 3.0 | 0 | 3/6 | 3/6 | 1/6 | 2/6 | 9/21 | 0/3 | - |
| LastObservation+VoIThresholdSense(lambda=0.02) | 7/24 | 29% | 2 | 2.0 | 0 | 3/6 | 2/6 | 0/6 | 2/6 | 7/21 | 0/3 | - |
| LastObservation+VoIThresholdSense(lambda=0.05) | 7/24 | 29% | 2 | 2.0 | 0 | 3/6 | 2/6 | 0/6 | 2/6 | 7/21 | 0/3 | - |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | snack_bowl_shared | kitchen_table_k1 | 10/42 |
| q02 | vacuum_cleaner_shared | storage_floor_s1 | 42/42 |
| q03 | shoes_hana | entry_floor_e1 | 17/42 |
| q04 | wallet_priya | entry_table_e1 | 40/42 |
| q05 | glass_hana | kitchen_table_k1 | 3/42 |
| q06 | dog_food_bag_shared | pantry_shelf_k1 | 42/42 |
| q07 | phone_hana | ON_PERSON | 0/42 |
| q08 | recipe_book_shared | pantry_shelf_k1 | 30/42 |
| q09 | bowl_hana | cupboard_k1 | 29/42 |
| q10 | book_priya | nightstand_b2 | 42/42 |
| q11 | phone_hana | nightstand_b1 | 37/42 |
| q12 | jacket_priya | entry_hook_e1 | 15/42 |
| q13 | toiletry_bag_hana | bathroom_shelf_ba1 | 15/42 |
| q14 | phone_priya | ON_PERSON | 0/42 |
| q15 | glass_hana | desk_b1 | 1/42 |
| q16 | bowl_hana | cupboard_k1 | 37/42 |
| q17 | spatula_shared | drawer_k_k1 | 23/42 |
| q18 | shoes_hana | entry_floor_e1 | 13/42 |
| q19 | phone_hana | ON_PERSON | 7/42 |
| q20 | blanket_shared | bed_b1 | 14/42 |
| q21 | serving_dish_shared | cupboard_k1 | 37/42 |
| q22 | pot_shared | cupboard_k1 | 27/42 |
| q23 | wallet_priya | entry_table_e1 | 41/42 |
| q24 | skincare_priya | sink_ba_ba1 | 2/42 |
