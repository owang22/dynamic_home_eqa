# situation_sim baselines · hh_s11

70 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.05) | 15/24 | 62% | 12 | 15.0 | 0 | 5/6 | 2/6 | 4/6 | 4/6 | 15/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 15/24 | 62% | 12 | 48.0 | 0 | 3/6 | 3/6 | 5/6 | 4/6 | 13/20 | 2/4 | - |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 15/24 | 62% | 14 | 47.0 | 1 | 6/6 | 2/6 | 4/6 | 3/6 | 15/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 17 | 41.0 | 16 | 6/6 | 2/6 | 4/6 | 3/6 | 15/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 17 | 41.0 | 16 | 6/6 | 2/6 | 4/6 | 3/6 | 15/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 15/24 | 62% | 18 | 24.0 | 1 | 5/6 | 2/6 | 4/6 | 4/6 | 15/20 | 0/4 | - |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 18 | 42.0 | 15 | 5/6 | 2/6 | 5/6 | 3/6 | 15/20 | 0/4 | - |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 18 | 42.0 | 15 | 5/6 | 2/6 | 5/6 | 3/6 | 15/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.02) | 14/24 | 58% | 13 | 13.0 | 0 | 4/6 | 2/6 | 4/6 | 4/6 | 14/20 | 0/4 | - |
| MostFrequentLocation+SequentialSearch | 14/24 | 58% | 14 | 47.0 | 1 | 6/6 | 2/6 | 3/6 | 3/6 | 14/20 | 0/4 | - |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 14/24 | 58% | 18 | 42.0 | 15 | 5/6 | 2/6 | 4/6 | 3/6 | 14/20 | 0/4 | - |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 18 | 42.0 | 15 | 5/6 | 2/6 | 4/6 | 3/6 | 14/20 | 0/4 | - |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 14/24 | 58% | 18 | 42.0 | 13 | 5/6 | 2/6 | 4/6 | 3/6 | 14/20 | 0/4 | - |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 18 | 42.0 | 13 | 5/6 | 2/6 | 4/6 | 3/6 | 14/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 14/24 | 58% | 20 | 44.0 | 13 | 5/6 | 2/6 | 4/6 | 3/6 | 14/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 20 | 44.0 | 13 | 5/6 | 2/6 | 4/6 | 3/6 | 14/20 | 0/4 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 10 | 10.0 | 0 | 4/6 | 2/6 | 3/6 | 4/6 | 13/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+SequentialSearch | 13/24 | 54% | 13 | 46.0 | 1 | 6/6 | 2/6 | 2/6 | 3/6 | 13/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+SequentialSearch | 13/24 | 54% | 14 | 47.0 | 1 | 6/6 | 2/6 | 2/6 | 3/6 | 13/20 | 0/4 | - |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+SequentialSearch | 13/24 | 54% | 14 | 47.0 | 1 | 6/6 | 2/6 | 2/6 | 3/6 | 13/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 13/24 | 54% | 15 | 39.0 | 20 | 3/6 | 2/6 | 4/6 | 4/6 | 12/20 | 1/4 | - |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+SequentialSearch | 13/24 | 54% | 15 | 37.0 | 1 | 5/6 | 2/6 | 3/6 | 3/6 | 13/20 | 0/4 | - |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+SequentialSearch | 13/24 | 54% | 15 | 37.0 | 1 | 5/6 | 2/6 | 3/6 | 3/6 | 13/20 | 0/4 | - |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 29 | 33.0 | 6 | 5/6 | 2/6 | 3/6 | 3/6 | 13/20 | 0/4 | - |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 29 | 33.0 | 6 | 5/6 | 2/6 | 3/6 | 3/6 | 13/20 | 0/4 | - |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 13/24 | 54% | 38 | 32.0 | 4 | 5/6 | 2/6 | 3/6 | 3/6 | 13/20 | 0/4 | - |
| DaytypeMixture(K=3,bin=2h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| LastObservation+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| LastObservation+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| MostFrequentLocation+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| TimetableLookup(bin=1h,days=all)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| DaytypeMixture(K=3,bin=2h,hl=24h)+SequentialSearch | 12/24 | 50% | 9 | 36.0 | 0 | 5/6 | 2/6 | 2/6 | 3/6 | 12/20 | 0/4 | - |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 9 | 9.0 | 0 | 5/6 | 2/6 | 2/6 | 3/6 | 12/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 9 | 9.0 | 0 | 4/6 | 2/6 | 2/6 | 4/6 | 12/20 | 0/4 | - |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 9 | 9.0 | 0 | 4/6 | 2/6 | 3/6 | 3/6 | 12/20 | 0/4 | - |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 12/24 | 50% | 11 | 32.0 | 3 | 5/6 | 2/6 | 2/6 | 3/6 | 12/20 | 0/4 | - |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 12/24 | 50% | 11 | 32.0 | 3 | 5/6 | 2/6 | 2/6 | 3/6 | 12/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 12/24 | 50% | 16 | 40.0 | 21 | 3/6 | 2/6 | 4/6 | 3/6 | 12/20 | 0/4 | - |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 30 | 10.0 | 0 | 4/6 | 2/6 | 2/6 | 4/6 | 12/20 | 0/4 | - |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 12/24 | 50% | 38 | 35.0 | 3 | 5/6 | 2/6 | 2/6 | 3/6 | 12/20 | 0/4 | - |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 12/24 | 50% | 39 | 36.0 | 2 | 5/6 | 2/6 | 2/6 | 3/6 | 12/20 | 0/4 | - |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 12/24 | 50% | 39 | 36.0 | 2 | 5/6 | 2/6 | 2/6 | 3/6 | 12/20 | 0/4 | - |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 5 | 5.0 | 0 | 4/6 | 2/6 | 2/6 | 3/6 | 11/20 | 0/4 | - |
| MostFrequentLocation+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 6 | 6.0 | 0 | 4/6 | 2/6 | 2/6 | 3/6 | 11/20 | 0/4 | - |
| LastObservation+SequentialSearch | 11/24 | 46% | 7 | 28.0 | 0 | 5/6 | 2/6 | 1/6 | 3/6 | 11/20 | 0/4 | - |
| LastObservation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 9 | 24.0 | 3 | 5/6 | 2/6 | 1/6 | 3/6 | 11/20 | 0/4 | - |
| LastObservation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 9 | 24.0 | 3 | 5/6 | 2/6 | 1/6 | 3/6 | 11/20 | 0/4 | - |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 30 | 10.0 | 0 | 4/6 | 2/6 | 2/6 | 3/6 | 11/20 | 0/4 | - |
| LastObservation+VoIThresholdSense(lambda=0.02) | 10/24 | 42% | 5 | 5.0 | 0 | 4/6 | 1/6 | 2/6 | 3/6 | 10/20 | 0/4 | - |
| LastObservation+VoIThresholdSense(lambda=0.05) | 10/24 | 42% | 5 | 5.0 | 0 | 4/6 | 1/6 | 2/6 | 3/6 | 10/20 | 0/4 | - |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.02) | 10/24 | 42% | 6 | 6.0 | 0 | 4/6 | 1/6 | 2/6 | 3/6 | 10/20 | 0/4 | - |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.05) | 10/24 | 42% | 6 | 6.0 | 0 | 4/6 | 1/6 | 2/6 | 3/6 | 10/20 | 0/4 | - |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.05) | 10/24 | 42% | 6 | 6.0 | 0 | 4/6 | 1/6 | 2/6 | 3/6 | 10/20 | 0/4 | - |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.05) | 10/24 | 42% | 6 | 6.0 | 0 | 4/6 | 1/6 | 2/6 | 3/6 | 10/20 | 0/4 | - |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.05) | 6/24 | 25% | 5 | 5.0 | 0 | 3/6 | 1/6 | 1/6 | 1/6 | 6/20 | 0/4 | - |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | spatula_shared | sink_k1 | 11/70 |
| q02 | vacuum_cleaner_shared | storage_floor_s1 | 70/70 |
| q03 | shoes_hana | entry_floor_e1 | 29/70 |
| q04 | wallet_priya | entry_table_e1 | 70/70 |
| q05 | glass_hana | sink_k1 | 65/70 |
| q06 | dog_leash_shared | entry_hook_e1 | 70/70 |
| q07 | phone_hana | ON_PERSON | 0/70 |
| q08 | remote_shared | armchair_l1 | 1/70 |
| q09 | bowl_hana | cupboard_k1 | 32/70 |
| q10 | book_priya | nightstand_b2 | 70/70 |
| q11 | phone_hana | ON_PERSON | 0/70 |
| q12 | jacket_priya | entry_hook_e1 | 31/70 |
| q13 | toiletry_bag_hana | bathroom_shelf_ba1 | 18/70 |
| q14 | phone_priya | ON_PERSON | 1/70 |
| q15 | glass_hana | counter_k1 | 15/70 |
| q16 | bowl_hana | cupboard_k1 | 63/70 |
| q17 | spatula_shared | drawer_k_k1 | 36/70 |
| q18 | shoes_hana | shoe_rack_e1 | 68/70 |
| q19 | phone_hana | ON_PERSON | 2/70 |
| q20 | blanket_shared | bed_b1 | 3/70 |
| q21 | serving_dish_shared | cupboard_k1 | 65/70 |
| q22 | recipe_book_shared | pantry_shelf_k1 | 69/70 |
| q23 | wallet_priya | entry_table_e1 | 70/70 |
| q24 | snack_bowl_shared | sink_k1 | 7/70 |
