# situation_sim baselines · hh_s10

70 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 15/24 | 62% | 13 | 46.0 | 2 | 2/6 | 4/6 | 4/6 | 5/6 | 15/17 | 0/1 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 23 | 47.0 | 8 | 1/6 | 6/6 | 4/6 | 3/6 | 14/17 | 0/1 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.02) | 14/24 | 58% | 41 | 18.0 | 0 | 2/6 | 5/6 | 4/6 | 3/6 | 14/17 | 0/1 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.02) | 14/24 | 58% | 41 | 18.0 | 0 | 2/6 | 5/6 | 4/6 | 3/6 | 14/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 14 | 41.0 | 3 | 2/6 | 3/6 | 5/6 | 3/6 | 12/17 | 0/1 | 1/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 13/24 | 54% | 23 | 47.0 | 9 | 1/6 | 6/6 | 4/6 | 2/6 | 13/17 | 0/1 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+SequentialSearch | 13/24 | 54% | 45 | 36.0 | 8 | 2/6 | 4/6 | 4/6 | 3/6 | 13/17 | 0/1 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+SequentialSearch | 13/24 | 54% | 45 | 36.0 | 8 | 2/6 | 4/6 | 4/6 | 3/6 | 13/17 | 0/1 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 9 | 9.0 | 0 | 1/6 | 5/6 | 3/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 10 | 10.0 | 0 | 1/6 | 5/6 | 3/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 11 | 11.0 | 0 | 1/6 | 5/6 | 3/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+SequentialSearch | 12/24 | 50% | 12 | 42.0 | 4 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 13 | 37.0 | 4 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 13 | 40.0 | 5 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 13 | 13.0 | 0 | 1/6 | 5/6 | 3/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+SequentialSearch | 12/24 | 50% | 13 | 40.0 | 12 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 13 | 37.0 | 6 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+SequentialSearch | 12/24 | 50% | 14 | 44.0 | 7 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| MostFrequentLocation+SequentialSearch | 12/24 | 50% | 14 | 41.0 | 12 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+SequentialSearch | 12/24 | 50% | 14 | 41.0 | 10 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 12/24 | 50% | 14 | 41.0 | 12 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 16 | 40.0 | 7 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 16 | 16.0 | 0 | 1/6 | 5/6 | 3/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 17 | 41.0 | 3 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 12/24 | 50% | 19 | 43.0 | 16 | 1/6 | 4/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 12/24 | 50% | 19 | 43.0 | 15 | 2/6 | 4/6 | 4/6 | 2/6 | 11/17 | 0/1 | 1/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 30 | 12.0 | 0 | 1/6 | 5/6 | 3/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 30 | 12.0 | 0 | 1/6 | 5/6 | 3/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 42 | 13.0 | 0 | 1/6 | 5/6 | 3/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 42 | 13.0 | 0 | 1/6 | 5/6 | 3/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 9 | 9.0 | 0 | 1/6 | 4/6 | 3/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 9 | 9.0 | 0 | 1/6 | 4/6 | 3/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 9 | 9.0 | 0 | 1/6 | 4/6 | 3/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 11 | 11.0 | 0 | 1/6 | 4/6 | 3/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| LastObservation+SequentialSearch | 11/24 | 46% | 12 | 45.0 | 2 | 2/6 | 3/6 | 3/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 12 | 12.0 | 0 | 1/6 | 4/6 | 3/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| LastObservation+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 13 | 37.0 | 4 | 2/6 | 3/6 | 3/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.02) | 11/24 | 46% | 15 | 39.0 | 6 | 2/6 | 3/6 | 3/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 18 | 42.0 | 16 | 1/6 | 3/6 | 4/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 18 | 42.0 | 16 | 1/6 | 3/6 | 4/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 19 | 43.0 | 15 | 1/6 | 4/6 | 4/6 | 2/6 | 11/17 | 0/1 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 19 | 43.0 | 15 | 1/6 | 4/6 | 4/6 | 2/6 | 11/17 | 0/1 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 19 | 43.0 | 15 | 1/6 | 4/6 | 4/6 | 2/6 | 11/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 11/24 | 46% | 21 | 45.0 | 11 | 1/6 | 3/6 | 4/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 11/24 | 46% | 21 | 45.0 | 11 | 1/6 | 3/6 | 4/6 | 3/6 | 11/17 | 0/1 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.1) | 10/24 | 42% | 8 | 8.0 | 0 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| LastObservation+VoIThresholdSense(lambda=0.1) | 10/24 | 42% | 8 | 8.0 | 0 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.1) | 10/24 | 42% | 8 | 8.0 | 0 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.05) | 10/24 | 42% | 9 | 9.0 | 0 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| LastObservation+VoIThresholdSense(lambda=0.05) | 10/24 | 42% | 9 | 9.0 | 0 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.05) | 10/24 | 42% | 9 | 9.0 | 0 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 16 | 40.0 | 6 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 10/24 | 42% | 16 | 40.0 | 6 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| LastObservation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 16 | 40.0 | 6 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| LastObservation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 10/24 | 42% | 16 | 40.0 | 6 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 18 | 42.0 | 17 | 1/6 | 3/6 | 4/6 | 2/6 | 10/17 | 0/1 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 39 | 22.0 | 1 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 10/24 | 42% | 39 | 22.0 | 1 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 10/24 | 42% | 39 | 22.0 | 1 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 10/24 | 42% | 39 | 22.0 | 1 | 1/6 | 3/6 | 3/6 | 3/6 | 10/17 | 0/1 | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |
| LastObservation+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |
| MostFrequentLocation+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 8/24 | 33% | 0 | 0.0 | 0 | 1/6 | 3/6 | 2/6 | 2/6 | 8/17 | 0/1 | 0/6 |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | wallet_omar | entry_floor_e1 | 20/70 |
| q02 | snack_bowl_shared | counter_k1 | 70/70 |
| q03 | shoes_yuki | OUT_OF_HOUSE | 1/70 |
| q04 | handbag_omar | OUT_OF_HOUSE | 0/70 |
| q05 | scarf_omar | OUT_OF_HOUSE | 0/70 |
| q06 | shoes_omar | OUT_OF_HOUSE | 0/70 |
| q07 | phone_yuki | coffee_table_l1 | 8/70 |
| q08 | controller_omar | tv_stand_l1 | 70/70 |
| q09 | glass_omar | sink_k1 | 56/70 |
| q10 | razor_yuki | sink_ba_ba1 | 70/70 |
| q11 | glass_yuki | cupboard_k1 | 15/70 |
| q12 | pot_shared | cupboard_k1 | 32/70 |
| q13 | pen_omar | entry_hook_e1 | 29/70 |
| q14 | bike_lock_omar | entry_table_e1 | 70/70 |
| q15 | laptop_yuki | entry_hook_e1 | 70/70 |
| q16 | bowl_omar | cupboard_k1 | 60/70 |
| q17 | phone_yuki | OUT_OF_HOUSE | 0/70 |
| q18 | jacket_yuki | OUT_OF_HOUSE | 1/70 |
| q19 | wallet_yuki | entry_table_e1 | 70/70 |
| q20 | scarf_omar | wardrobe_b1 | 5/70 |
| q21 | razor_yuki | bathroom_shelf_ba1 | 4/70 |
| q22 | phone_yuki | ON_PERSON | 0/70 |
| q23 | glass_yuki | sink_k1 | 47/70 |
| q24 | wallet_yuki | entry_table_e1 | 70/70 |
