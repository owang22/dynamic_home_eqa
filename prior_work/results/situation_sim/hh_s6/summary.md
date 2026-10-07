# situation_sim baselines · hh_s6

70 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 15 | 39.0 | 16 | 1/6 | 4/6 | 5/6 | 5/6 | 15/16 | 0/2 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+SequentialSearch | 14/24 | 58% | 12 | 45.0 | 1 | 1/6 | 3/6 | 5/6 | 5/6 | 13/16 | 1/2 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 14/24 | 58% | 13 | 31.0 | 2 | 0/6 | 4/6 | 6/6 | 4/6 | 14/16 | 0/2 | 0/6 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 17 | 41.0 | 15 | 1/6 | 4/6 | 5/6 | 4/6 | 13/16 | 1/2 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 14/24 | 58% | 20 | 44.0 | 16 | 1/6 | 3/6 | 5/6 | 5/6 | 14/16 | 0/2 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 14/24 | 58% | 21 | 45.0 | 14 | 1/6 | 4/6 | 5/6 | 4/6 | 14/16 | 0/2 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 21 | 45.0 | 14 | 1/6 | 4/6 | 5/6 | 4/6 | 14/16 | 0/2 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 21 | 45.0 | 15 | 1/6 | 4/6 | 5/6 | 4/6 | 14/16 | 0/2 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.1) | 13/24 | 54% | 9 | 9.0 | 0 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 10 | 10.0 | 0 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.05) | 13/24 | 54% | 11 | 11.0 | 0 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 12 | 36.0 | 2 | 0/6 | 4/6 | 6/6 | 3/6 | 13/16 | 0/2 | 0/6 |
| MostFrequentLocation+SequentialSearch | 13/24 | 54% | 12 | 45.0 | 5 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+SequentialSearch | 13/24 | 54% | 12 | 45.0 | 5 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 12 | 12.0 | 0 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+SequentialSearch | 13/24 | 54% | 13 | 46.0 | 4 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 13 | 13.0 | 0 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 13/24 | 54% | 14 | 38.0 | 19 | 1/6 | 2/6 | 5/6 | 5/6 | 13/16 | 0/2 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 16 | 16.0 | 0 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 13/24 | 54% | 16 | 40.0 | 18 | 1/6 | 3/6 | 5/6 | 4/6 | 13/16 | 0/2 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 13/24 | 54% | 17 | 41.0 | 17 | 1/6 | 2/6 | 5/6 | 5/6 | 13/16 | 0/2 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 13/24 | 54% | 17 | 41.0 | 15 | 1/6 | 3/6 | 5/6 | 4/6 | 12/16 | 1/2 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 8 | 8.0 | 0 | 1/6 | 3/6 | 5/6 | 3/6 | 12/16 | 0/2 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 12/24 | 50% | 12 | 45.0 | 4 | 0/6 | 2/6 | 5/6 | 5/6 | 11/16 | 1/2 | 0/6 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 12/24 | 50% | 12 | 45.0 | 5 | 1/6 | 2/6 | 5/6 | 4/6 | 12/16 | 0/2 | 0/6 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 12/24 | 50% | 16 | 40.0 | 18 | 1/6 | 3/6 | 5/6 | 3/6 | 12/16 | 0/2 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 29 | 9.0 | 0 | 0/6 | 3/6 | 5/6 | 4/6 | 12/16 | 0/2 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 29 | 9.0 | 0 | 0/6 | 3/6 | 5/6 | 4/6 | 12/16 | 0/2 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 36 | 27.0 | 2 | 0/6 | 3/6 | 5/6 | 4/6 | 12/16 | 0/2 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 5 | 5.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 6 | 6.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 6 | 6.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 6 | 6.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 6 | 6.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 6 | 6.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 6 | 6.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 6 | 6.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 6 | 6.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 13 | 7.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 13 | 7.0 | 0 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 16 | 40.0 | 18 | 1/6 | 2/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 35 | 23.0 | 2 | 0/6 | 3/6 | 5/6 | 3/6 | 11/16 | 0/2 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.05) | 10/24 | 42% | 5 | 5.0 | 0 | 0/6 | 3/6 | 5/6 | 2/6 | 10/16 | 0/2 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+SequentialSearch | 10/24 | 42% | 8 | 26.0 | 0 | 0/6 | 3/6 | 5/6 | 2/6 | 10/16 | 0/2 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 10 | 22.0 | 5 | 0/6 | 3/6 | 5/6 | 2/6 | 10/16 | 0/2 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 10/24 | 42% | 10 | 22.0 | 5 | 0/6 | 3/6 | 5/6 | 2/6 | 10/16 | 0/2 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 21 | 15.0 | 1 | 0/6 | 2/6 | 5/6 | 3/6 | 10/16 | 0/2 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 10/24 | 42% | 21 | 15.0 | 1 | 0/6 | 2/6 | 5/6 | 3/6 | 10/16 | 0/2 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 21 | 15.0 | 1 | 0/6 | 2/6 | 5/6 | 3/6 | 10/16 | 0/2 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 10/24 | 42% | 21 | 15.0 | 1 | 0/6 | 2/6 | 5/6 | 3/6 | 10/16 | 0/2 | 0/6 |
| LastObservation+VoIThresholdSense(lambda=0.05) | 9/24 | 38% | 4 | 4.0 | 0 | 0/6 | 3/6 | 4/6 | 2/6 | 9/16 | 0/2 | 0/6 |
| LastObservation+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 4 | 4.0 | 0 | 0/6 | 3/6 | 4/6 | 2/6 | 9/16 | 0/2 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.05) | 9/24 | 38% | 5 | 5.0 | 0 | 0/6 | 2/6 | 4/6 | 3/6 | 9/16 | 0/2 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 5 | 5.0 | 0 | 0/6 | 2/6 | 4/6 | 3/6 | 9/16 | 0/2 | 0/6 |
| LastObservation+SequentialSearch | 9/24 | 38% | 6 | 24.0 | 0 | 0/6 | 3/6 | 4/6 | 2/6 | 9/16 | 0/2 | 0/6 |
| LastObservation+VoIThresholdSense(lambda=0.02) | 9/24 | 38% | 7 | 19.0 | 2 | 0/6 | 4/6 | 4/6 | 1/6 | 9/16 | 0/2 | 0/6 |
| LastObservation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 9/24 | 38% | 8 | 20.0 | 5 | 0/6 | 3/6 | 4/6 | 2/6 | 9/16 | 0/2 | 0/6 |
| LastObservation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 9/24 | 38% | 8 | 20.0 | 5 | 0/6 | 3/6 | 4/6 | 2/6 | 9/16 | 0/2 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+SequentialSearch | 9/24 | 38% | 25 | 26.0 | 0 | 0/6 | 2/6 | 5/6 | 2/6 | 9/16 | 0/2 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+SequentialSearch | 9/24 | 38% | 25 | 26.0 | 0 | 0/6 | 2/6 | 5/6 | 2/6 | 9/16 | 0/2 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |
| LastObservation+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |
| MostFrequentLocation+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 0/6 | 2/6 | 4/6 | 2/6 | 8/16 | 0/2 | 0/6 |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | charger_omar | OUT_OF_HOUSE | 0/70 |
| q02 | bowl_omar | kitchen_table_k1 | 24/70 |
| q03 | phone_omar | OUT_OF_HOUSE | 0/70 |
| q04 | keys_leo | OUT_OF_HOUSE | 0/70 |
| q05 | shoes_omar | OUT_OF_HOUSE | 0/70 |
| q06 | phone_leo | ON_PERSON | 0/70 |
| q07 | laptop_leo | desk_b1 | 9/70 |
| q08 | jacket_omar | OUT_OF_HOUSE | 0/70 |
| q09 | phone_leo | OUT_OF_HOUSE | 0/70 |
| q10 | water_bottle_omar | dish_rack_k1 | 51/70 |
| q11 | snack_bowl_shared | cupboard_k1 | 66/70 |
| q12 | razor_omar | bathroom_shelf_ba1 | 69/70 |
| q13 | shoes_omar | shoe_rack_e1 | 70/70 |
| q14 | mug_omar | kitchen_table_k1 | 51/70 |
| q15 | charger_omar | nightstand_b1 | 3/70 |
| q16 | umbrella_omar | entry_floor_e1 | 70/70 |
| q17 | sunglasses_omar | entry_table_e1 | 70/70 |
| q18 | shopping_bag_shared | pantry_shelf_k1 | 70/70 |
| q19 | kitchen_knife_shared | drawer_k_k1 | 70/70 |
| q20 | phone_omar | ON_PERSON | 4/70 |
| q21 | spatula_shared | kitchen_table_k1 | 25/70 |
| q22 | vitamins_omar | kitchen_table_k1 | 53/70 |
| q23 | towel_leo | bathroom_shelf_ba1 | 4/70 |
| q24 | dog_leash_shared | entry_hook_e1 | 63/70 |
