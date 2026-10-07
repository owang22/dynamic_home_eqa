# situation_sim baselines · hh_s8

70 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.1) | 14/24 | 58% | 18 | 8.0 | 0 | 3/6 | 3/6 | 3/6 | 5/6 | 14/19 | 0/3 | 0/2 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.1) | 14/24 | 58% | 18 | 8.0 | 0 | 3/6 | 3/6 | 3/6 | 5/6 | 14/19 | 0/3 | 0/2 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.05) | 14/24 | 58% | 31 | 9.0 | 0 | 3/6 | 3/6 | 3/6 | 5/6 | 14/19 | 0/3 | 0/2 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.05) | 14/24 | 58% | 34 | 9.0 | 0 | 3/6 | 3/6 | 3/6 | 5/6 | 14/19 | 0/3 | 0/2 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.02) | 14/24 | 58% | 38 | 10.0 | 0 | 3/6 | 3/6 | 3/6 | 5/6 | 14/19 | 0/3 | 0/2 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.02) | 14/24 | 58% | 41 | 10.0 | 0 | 3/6 | 3/6 | 3/6 | 5/6 | 14/19 | 0/3 | 0/2 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 17 | 41.0 | 5 | 2/6 | 3/6 | 4/6 | 4/6 | 13/19 | 0/3 | 0/2 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 5 | 5.0 | 0 | 2/6 | 2/6 | 3/6 | 5/6 | 12/19 | 0/3 | 0/2 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 5 | 5.0 | 0 | 2/6 | 2/6 | 3/6 | 5/6 | 12/19 | 0/3 | 0/2 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 2/6 | 2/6 | 3/6 | 5/6 | 12/19 | 0/3 | 0/2 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 2/6 | 2/6 | 3/6 | 5/6 | 12/19 | 0/3 | 0/2 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+SequentialSearch | 12/24 | 50% | 12 | 48.0 | 0 | 2/6 | 2/6 | 4/6 | 4/6 | 12/19 | 0/3 | 0/2 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 16 | 40.0 | 4 | 2/6 | 2/6 | 4/6 | 4/6 | 12/19 | 0/3 | 0/2 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 12/24 | 50% | 39 | 19.0 | 3 | 2/6 | 3/6 | 3/6 | 4/6 | 12/19 | 0/3 | 0/2 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 12/24 | 50% | 39 | 19.0 | 1 | 2/6 | 3/6 | 3/6 | 4/6 | 12/19 | 0/3 | 0/2 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 12/24 | 50% | 39 | 19.0 | 3 | 2/6 | 3/6 | 3/6 | 4/6 | 12/19 | 0/3 | 0/2 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 12/24 | 50% | 39 | 19.0 | 1 | 2/6 | 3/6 | 3/6 | 4/6 | 12/19 | 0/3 | 0/2 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| LastObservation+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| Markov1(a=1,cut=24h,hl=24h)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| MostFrequentLocation+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| SmoothedRecency(hl=6h,freq=24h)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 11/24 | 46% | 0 | 0.0 | 0 | 2/6 | 3/6 | 2/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 4 | 4.0 | 0 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 4 | 4.0 | 0 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| LastObservation+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 4 | 4.0 | 0 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 4 | 4.0 | 0 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 4 | 4.0 | 0 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 4 | 4.0 | 0 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 4 | 4.0 | 0 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 5 | 5.0 | 0 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 11 | 20.0 | 0 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+SequentialSearch | 11/24 | 46% | 12 | 45.0 | 1 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 12 | 36.0 | 4 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 12 | 36.0 | 4 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 12 | 36.0 | 4 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| LastObservation+SequentialSearch | 11/24 | 46% | 12 | 45.0 | 1 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| LastObservation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 12 | 36.0 | 4 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| LastObservation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 12 | 36.0 | 4 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| LastObservation+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 12 | 36.0 | 4 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 13 | 37.0 | 4 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 13 | 37.0 | 6 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 13 | 37.0 | 4 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 13 | 37.0 | 6 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 16 | 40.0 | 20 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 17 | 41.0 | 17 | 2/6 | 1/6 | 4/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 17 | 41.0 | 17 | 2/6 | 1/6 | 4/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 17 | 41.0 | 15 | 2/6 | 1/6 | 4/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 17 | 41.0 | 15 | 2/6 | 1/6 | 4/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 18 | 42.0 | 17 | 2/6 | 1/6 | 4/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 18 | 42.0 | 17 | 2/6 | 1/6 | 4/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 18 | 42.0 | 18 | 2/6 | 1/6 | 4/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 19 | 43.0 | 14 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 19 | 43.0 | 14 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+SequentialSearch | 11/24 | 46% | 63 | 39.0 | 6 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+SequentialSearch | 11/24 | 46% | 63 | 39.0 | 6 | 2/6 | 2/6 | 3/6 | 4/6 | 11/19 | 0/3 | 0/2 |
| LastObservation+VoIThresholdSense(lambda=0.1) | 10/24 | 42% | 2 | 2.0 | 0 | 2/6 | 2/6 | 2/6 | 4/6 | 10/19 | 0/3 | 0/2 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.1) | 10/24 | 42% | 2 | 2.0 | 0 | 2/6 | 2/6 | 2/6 | 4/6 | 10/19 | 0/3 | 0/2 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.1) | 10/24 | 42% | 2 | 2.0 | 0 | 2/6 | 2/6 | 2/6 | 4/6 | 10/19 | 0/3 | 0/2 |
| MostFrequentLocation+SequentialSearch | 10/24 | 42% | 12 | 48.0 | 0 | 2/6 | 2/6 | 2/6 | 4/6 | 10/19 | 0/3 | 0/2 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+SequentialSearch | 10/24 | 42% | 12 | 48.0 | 0 | 2/6 | 2/6 | 2/6 | 4/6 | 10/19 | 0/3 | 0/2 |
| SmoothedRecency(hl=6h,freq=24h)+SequentialSearch | 10/24 | 42% | 12 | 48.0 | 0 | 2/6 | 2/6 | 2/6 | 4/6 | 10/19 | 0/3 | 0/2 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 10/24 | 42% | 12 | 48.0 | 0 | 2/6 | 2/6 | 2/6 | 4/6 | 10/19 | 0/3 | 0/2 |
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 10/24 | 42% | 14 | 47.0 | 5 | 2/6 | 1/6 | 3/6 | 4/6 | 10/19 | 0/3 | 0/2 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 17 | 41.0 | 17 | 2/6 | 1/6 | 4/6 | 3/6 | 10/19 | 0/3 | 0/2 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 10/24 | 42% | 17 | 41.0 | 17 | 2/6 | 1/6 | 4/6 | 3/6 | 10/19 | 0/3 | 0/2 |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | pen_felix | OUT_OF_HOUSE | 0/70 |
| q02 | jacket_aisha | entry_hook_e1 | 70/70 |
| q03 | towel_felix | towel_rack_ba1 | 70/70 |
| q04 | phone_aisha | ON_PERSON | 0/70 |
| q05 | hat_aisha | OUT_OF_HOUSE | 0/70 |
| q06 | glass_aisha | cupboard_k1 | 6/70 |
| q07 | vacuum_cleaner_shared | storage_floor_s1 | 70/70 |
| q08 | phone_aisha | ON_PERSON | 0/70 |
| q09 | skincare_felix | bathroom_shelf_ba1 | 56/70 |
| q10 | glass_aisha | couch_l1 | 0/70 |
| q11 | kitchen_knife_shared | counter_k1 | 24/70 |
| q12 | tablet_felix | bedroom_floor_b1 | 1/70 |
| q13 | phone_aisha | nightstand_b1 | 2/70 |
| q14 | bowl_aisha | cupboard_k1 | 53/70 |
| q15 | towel_felix | towel_rack_ba1 | 70/70 |
| q16 | hat_aisha | entry_hook_e1 | 70/70 |
| q17 | vacuum_cleaner_shared | floor_l_l1 | 1/70 |
| q18 | skincare_felix | sink_ba_ba1 | 9/70 |
| q19 | keys_felix | entry_table_e1 | 70/70 |
| q20 | phone_aisha | ON_PERSON | 0/70 |
| q21 | glass_felix | pantry_shelf_k1 | 52/70 |
| q22 | mug_felix | sink_k1 | 26/70 |
| q23 | shopping_bag_shared | pantry_shelf_k1 | 70/70 |
| q24 | keys_aisha | entry_table_e1 | 70/70 |
