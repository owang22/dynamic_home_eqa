# situation_sim baselines · hh_s10

70 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h)+SequentialSearch | 17/24 | 71% | 8 | 23.0 | 3 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 17/24 | 71% | 11 | 23.0 | 5 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.02) | 17/24 | 71% | 11 | 23.0 | 5 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 17/24 | 71% | 12 | 24.0 | 5 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.02) | 17/24 | 71% | 13 | 25.0 | 3 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 17/24 | 71% | 13 | 25.0 | 5 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.02) | 17/24 | 71% | 13 | 25.0 | 4 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 17/24 | 71% | 13 | 25.0 | 5 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 17/24 | 71% | 14 | 26.0 | 5 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 17/24 | 71% | 18 | 30.0 | 4 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 17/24 | 71% | 19 | 43.0 | 11 | 3/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 1/6 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 17/24 | 71% | 20 | 44.0 | 10 | 3/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 1/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+SequentialSearch | 17/24 | 71% | 27 | 22.0 | 5 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+SequentialSearch | 17/24 | 71% | 27 | 22.0 | 5 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+SequentialSearch | 16/24 | 67% | 15 | 42.0 | 8 | 3/6 | 6/6 | 4/6 | 3/6 | 15/18 | - | 1/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 19 | 43.0 | 11 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 10 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 10 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 10 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 21 | 45.0 | 9 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 21 | 45.0 | 9 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 21 | 45.0 | 10 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 21 | 45.0 | 10 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 30 | 21.0 | 2 | 2/6 | 5/6 | 4/6 | 5/6 | 16/18 | - | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 30 | 21.0 | 1 | 2/6 | 5/6 | 4/6 | 5/6 | 16/18 | - | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 30 | 21.0 | 2 | 2/6 | 5/6 | 4/6 | 5/6 | 16/18 | - | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 30 | 21.0 | 1 | 2/6 | 5/6 | 4/6 | 5/6 | 16/18 | - | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.02) | 16/24 | 67% | 36 | 21.0 | 1 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.02) | 16/24 | 67% | 36 | 21.0 | 1 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| LastObservation+SequentialSearch | 15/24 | 62% | 6 | 21.0 | 3 | 2/6 | 4/6 | 4/6 | 5/6 | 15/18 | - | 0/6 |
| LastObservation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 9 | 21.0 | 5 | 2/6 | 4/6 | 4/6 | 5/6 | 15/18 | - | 0/6 |
| LastObservation+VoIThresholdSense(lambda=0.02) | 15/24 | 62% | 9 | 21.0 | 5 | 2/6 | 4/6 | 4/6 | 5/6 | 15/18 | - | 0/6 |
| LastObservation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 10 | 22.0 | 5 | 2/6 | 4/6 | 4/6 | 5/6 | 15/18 | - | 0/6 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.05) | 15/24 | 62% | 10 | 10.0 | 0 | 2/6 | 6/6 | 3/6 | 4/6 | 15/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.05) | 15/24 | 62% | 14 | 14.0 | 0 | 2/6 | 6/6 | 3/6 | 4/6 | 15/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 15/24 | 62% | 14 | 44.0 | 4 | 2/6 | 6/6 | 4/6 | 3/6 | 15/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+SequentialSearch | 15/24 | 62% | 15 | 42.0 | 8 | 2/6 | 6/6 | 4/6 | 3/6 | 15/18 | - | 0/6 |
| MostFrequentLocation+SequentialSearch | 15/24 | 62% | 16 | 43.0 | 8 | 2/6 | 6/6 | 4/6 | 3/6 | 15/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 15/24 | 62% | 16 | 43.0 | 8 | 2/6 | 6/6 | 4/6 | 3/6 | 15/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 18 | 42.0 | 15 | 2/6 | 6/6 | 3/6 | 4/6 | 15/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 18 | 42.0 | 15 | 2/6 | 6/6 | 3/6 | 4/6 | 15/18 | - | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.1) | 15/24 | 62% | 22 | 11.0 | 0 | 2/6 | 6/6 | 3/6 | 4/6 | 15/18 | - | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.1) | 15/24 | 62% | 22 | 11.0 | 0 | 2/6 | 6/6 | 3/6 | 4/6 | 15/18 | - | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.05) | 15/24 | 62% | 32 | 11.0 | 0 | 2/6 | 6/6 | 3/6 | 4/6 | 15/18 | - | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.05) | 15/24 | 62% | 32 | 11.0 | 0 | 2/6 | 6/6 | 3/6 | 4/6 | 15/18 | - | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.05) | 14/24 | 58% | 7 | 7.0 | 0 | 2/6 | 6/6 | 3/6 | 3/6 | 14/18 | - | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.1) | 14/24 | 58% | 7 | 7.0 | 0 | 2/6 | 6/6 | 3/6 | 3/6 | 14/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.05) | 14/24 | 58% | 9 | 9.0 | 0 | 2/6 | 5/6 | 3/6 | 4/6 | 14/18 | - | 0/6 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.1) | 14/24 | 58% | 10 | 10.0 | 0 | 2/6 | 5/6 | 3/6 | 4/6 | 14/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.05) | 14/24 | 58% | 10 | 10.0 | 0 | 2/6 | 5/6 | 3/6 | 4/6 | 14/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.1) | 14/24 | 58% | 11 | 11.0 | 0 | 2/6 | 5/6 | 3/6 | 4/6 | 14/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+SequentialSearch | 14/24 | 58% | 16 | 43.0 | 7 | 2/6 | 6/6 | 4/6 | 2/6 | 14/18 | - | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.05) | 13/24 | 54% | 8 | 8.0 | 0 | 2/6 | 5/6 | 3/6 | 3/6 | 13/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.1) | 13/24 | 54% | 9 | 9.0 | 0 | 2/6 | 4/6 | 3/6 | 4/6 | 13/18 | - | 0/6 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| LastObservation+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| MostFrequentLocation+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 2/6 | 5/6 | 2/6 | 3/6 | 12/18 | - | 0/6 |
| LastObservation+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 2/6 | 4/6 | 3/6 | 3/6 | 12/18 | - | 0/6 |
| LastObservation+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 6 | 6.0 | 0 | 2/6 | 4/6 | 3/6 | 3/6 | 12/18 | - | 0/6 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 6 | 6.0 | 0 | 2/6 | 4/6 | 3/6 | 3/6 | 12/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 7 | 7.0 | 0 | 2/6 | 4/6 | 3/6 | 3/6 | 12/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.05) | 11/24 | 46% | 6 | 6.0 | 0 | 2/6 | 3/6 | 3/6 | 3/6 | 11/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.1) | 11/24 | 46% | 6 | 6.0 | 0 | 2/6 | 3/6 | 3/6 | 3/6 | 11/18 | - | 0/6 |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | vitamins_omar | kitchen_table_k1 | 70/70 |
| q02 | skincare_omar | bathroom_shelf_ba1 | 70/70 |
| q03 | shoes_yuki | OUT_OF_HOUSE | 2/70 |
| q04 | handbag_omar | OUT_OF_HOUSE | 0/70 |
| q05 | scarf_omar | OUT_OF_HOUSE | 0/70 |
| q06 | shoes_omar | OUT_OF_HOUSE | 1/70 |
| q07 | plate_omar | cupboard_k1 | 55/70 |
| q08 | controller_omar | tv_stand_l1 | 70/70 |
| q09 | glass_yuki | sink_k1 | 54/70 |
| q10 | remote_shared | tv_stand_l1 | 70/70 |
| q11 | glasses_omar | nightstand_b1 | 70/70 |
| q12 | pot_shared | cupboard_k1 | 58/70 |
| q13 | pen_omar | entry_hook_e1 | 36/70 |
| q14 | bike_lock_omar | entry_table_e1 | 70/70 |
| q15 | laptop_yuki | entry_hook_e1 | 70/70 |
| q16 | bowl_omar | cupboard_k1 | 60/70 |
| q17 | phone_yuki | OUT_OF_HOUSE | 0/70 |
| q18 | jacket_yuki | OUT_OF_HOUSE | 0/70 |
| q19 | wallet_yuki | entry_floor_e1 | 17/70 |
| q20 | scarf_omar | wardrobe_b1 | 24/70 |
| q21 | remote_shared | tv_stand_l1 | 70/70 |
| q22 | plate_omar | cupboard_k1 | 70/70 |
| q23 | glass_yuki | sink_k1 | 43/70 |
| q24 | wallet_yuki | entry_table_e1 | 52/70 |
