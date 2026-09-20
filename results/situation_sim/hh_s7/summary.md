# situation_sim baselines · hh_s7

70 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 17/24 | 71% | 20 | 44.0 | 7 | 3/6 | 5/6 | 5/6 | 4/6 | 16/19 | 0/1 | 1/4 |
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 16/24 | 67% | 14 | 44.0 | 5 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| SmoothedRecency(hl=6h,freq=24h)+SequentialSearch | 16/24 | 67% | 14 | 38.0 | 11 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| MostFrequentLocation+SequentialSearch | 16/24 | 67% | 16 | 40.0 | 11 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 16/24 | 67% | 16 | 40.0 | 11 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+SequentialSearch | 16/24 | 67% | 17 | 41.0 | 5 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 16/24 | 67% | 17 | 29.0 | 2 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 6 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 6 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 7 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 7 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 7 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 7 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 7 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 7 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 7 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.02) | 16/24 | 67% | 21 | 33.0 | 1 | 3/6 | 5/6 | 5/6 | 3/6 | 16/19 | 0/1 | 0/4 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.02) | 16/24 | 67% | 30 | 18.0 | 0 | 3/6 | 4/6 | 5/6 | 4/6 | 16/19 | 0/1 | 0/4 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.02) | 16/24 | 67% | 30 | 18.0 | 0 | 3/6 | 4/6 | 5/6 | 4/6 | 16/19 | 0/1 | 0/4 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+SequentialSearch | 15/24 | 62% | 10 | 22.0 | 3 | 3/6 | 4/6 | 5/6 | 3/6 | 15/19 | 0/1 | 0/4 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.05) | 15/24 | 62% | 11 | 11.0 | 0 | 3/6 | 4/6 | 5/6 | 3/6 | 15/19 | 0/1 | 0/4 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.05) | 15/24 | 62% | 12 | 12.0 | 0 | 3/6 | 4/6 | 5/6 | 3/6 | 15/19 | 0/1 | 0/4 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 15/24 | 62% | 16 | 28.0 | 2 | 3/6 | 4/6 | 5/6 | 3/6 | 15/19 | 0/1 | 0/4 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 20 | 44.0 | 5 | 3/6 | 5/6 | 5/6 | 2/6 | 15/19 | 0/1 | 0/4 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 20 | 44.0 | 5 | 3/6 | 5/6 | 5/6 | 2/6 | 15/19 | 0/1 | 0/4 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+SequentialSearch | 15/24 | 62% | 33 | 24.0 | 4 | 3/6 | 4/6 | 5/6 | 3/6 | 15/19 | 0/1 | 0/4 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+SequentialSearch | 15/24 | 62% | 34 | 25.0 | 4 | 3/6 | 4/6 | 5/6 | 3/6 | 15/19 | 0/1 | 0/4 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 42 | 30.0 | 0 | 2/6 | 4/6 | 5/6 | 4/6 | 15/19 | 0/1 | 0/4 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 42 | 30.0 | 0 | 2/6 | 4/6 | 5/6 | 4/6 | 15/19 | 0/1 | 0/4 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 42 | 30.0 | 0 | 2/6 | 4/6 | 5/6 | 4/6 | 15/19 | 0/1 | 0/4 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 42 | 30.0 | 0 | 2/6 | 4/6 | 5/6 | 4/6 | 15/19 | 0/1 | 0/4 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.05) | 14/24 | 58% | 10 | 10.0 | 0 | 3/6 | 4/6 | 5/6 | 2/6 | 14/19 | 0/1 | 0/4 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+SequentialSearch | 14/24 | 58% | 14 | 41.0 | 6 | 3/6 | 5/6 | 4/6 | 2/6 | 14/19 | 0/1 | 0/4 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 14/24 | 58% | 17 | 29.0 | 2 | 3/6 | 4/6 | 5/6 | 2/6 | 14/19 | 0/1 | 0/4 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.05) | 13/24 | 54% | 9 | 9.0 | 0 | 3/6 | 4/6 | 3/6 | 3/6 | 13/19 | 0/1 | 0/4 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.05) | 13/24 | 54% | 9 | 9.0 | 0 | 3/6 | 4/6 | 3/6 | 3/6 | 13/19 | 0/1 | 0/4 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 12 | 24.0 | 2 | 3/6 | 4/6 | 3/6 | 3/6 | 13/19 | 0/1 | 0/4 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 13/24 | 54% | 14 | 35.0 | 3 | 3/6 | 4/6 | 3/6 | 3/6 | 13/19 | 0/1 | 0/4 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 13/24 | 54% | 14 | 35.0 | 3 | 3/6 | 4/6 | 3/6 | 3/6 | 13/19 | 0/1 | 0/4 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 15 | 36.0 | 3 | 3/6 | 4/6 | 3/6 | 3/6 | 13/19 | 0/1 | 0/4 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.05) | 13/24 | 54% | 51 | 14.0 | 0 | 2/6 | 4/6 | 4/6 | 3/6 | 13/19 | 0/1 | 0/4 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.05) | 13/24 | 54% | 51 | 14.0 | 0 | 2/6 | 4/6 | 4/6 | 3/6 | 13/19 | 0/1 | 0/4 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 6 | 6.0 | 0 | 2/6 | 4/6 | 3/6 | 3/6 | 12/19 | 0/1 | 0/4 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 13 | 25.0 | 2 | 3/6 | 4/6 | 3/6 | 2/6 | 12/19 | 0/1 | 0/4 |
| LastObservation+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 7 | 7.0 | 0 | 3/6 | 3/6 | 3/6 | 2/6 | 11/19 | 0/1 | 0/4 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 7 | 7.0 | 0 | 3/6 | 3/6 | 3/6 | 2/6 | 11/19 | 0/1 | 0/4 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 7 | 7.0 | 0 | 3/6 | 3/6 | 3/6 | 2/6 | 11/19 | 0/1 | 0/4 |
| LastObservation+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 11 | 23.0 | 3 | 3/6 | 3/6 | 3/6 | 2/6 | 11/19 | 0/1 | 0/4 |
| LastObservation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 12 | 33.0 | 3 | 3/6 | 3/6 | 3/6 | 2/6 | 11/19 | 0/1 | 0/4 |
| LastObservation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 12 | 33.0 | 3 | 3/6 | 3/6 | 3/6 | 2/6 | 11/19 | 0/1 | 0/4 |
| LastObservation+SequentialSearch | 10/24 | 42% | 6 | 18.0 | 2 | 3/6 | 3/6 | 2/6 | 2/6 | 10/19 | 0/1 | 0/4 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| LastObservation+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| LastObservation+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| Markov1(a=1,cut=24h,hl=24h)+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| MostFrequentLocation+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| SmoothedRecency(hl=6h,freq=24h)+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.1) | 9/24 | 38% | 0 | 0.0 | 0 | 2/6 | 2/6 | 2/6 | 3/6 | 9/19 | 0/1 | 0/4 |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | jacket_hana | entry_hook_e1 | 64/70 |
| q02 | mug_hana | kitchen_table_k1 | 46/70 |
| q03 | pot_shared | cupboard_k1 | 70/70 |
| q04 | phone_hana | OUT_OF_HOUSE | 0/70 |
| q05 | pen_dana | desk_o1 | 0/70 |
| q06 | hat_dana | shoe_rack_e1 | 4/70 |
| q07 | cutting_board_shared | sink_k1 | 20/70 |
| q08 | plate_dana | dish_rack_k1 | 44/70 |
| q09 | umbrella_hana | entry_floor_e1 | 70/70 |
| q10 | water_bottle_dana | dish_rack_k1 | 51/70 |
| q11 | jacket_hana | OUT_OF_HOUSE | 0/70 |
| q12 | umbrella_hana | entry_floor_e1 | 70/70 |
| q13 | jacket_hana | entry_hook_e1 | 68/70 |
| q14 | recipe_book_shared | counter_k1 | 50/70 |
| q15 | shopping_bag_shared | pantry_shelf_k1 | 70/70 |
| q16 | glass_dana | counter_k1 | 35/70 |
| q17 | mug_hana | cupboard_k1 | 36/70 |
| q18 | wallet_hana | OUT_OF_HOUSE | 0/70 |
| q19 | glass_dana | counter_k1 | 38/70 |
| q20 | shoes_dana | OUT_OF_HOUSE | 1/70 |
| q21 | kitchen_knife_shared | drawer_k_k1 | 70/70 |
| q22 | phone_hana | ON_PERSON | 0/70 |
| q23 | water_bottle_dana | sink_k1 | 27/70 |
| q24 | keys_hana | entry_table_e1 | 68/70 |
