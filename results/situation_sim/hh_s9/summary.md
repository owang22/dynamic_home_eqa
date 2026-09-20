# situation_sim baselines · hh_s9

70 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 17/24 | 71% | 18 | 42.0 | 13 | 6/6 | 4/6 | 4/6 | 3/6 | 14/21 | 2/2 | 1/1 |
| SmoothedRecency(hl=6h,freq=24h)+SequentialSearch | 16/24 | 67% | 15 | 42.0 | 12 | 6/6 | 3/6 | 4/6 | 3/6 | 16/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 16/24 | 67% | 17 | 32.0 | 2 | 6/6 | 4/6 | 3/6 | 3/6 | 16/21 | 0/2 | 0/1 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 17 | 41.0 | 14 | 5/6 | 3/6 | 5/6 | 3/6 | 16/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 12 | 5/6 | 3/6 | 5/6 | 3/6 | 16/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 16/24 | 67% | 20 | 44.0 | 12 | 5/6 | 3/6 | 5/6 | 3/6 | 16/21 | 0/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 15/24 | 62% | 12 | 42.0 | 10 | 6/6 | 4/6 | 3/6 | 2/6 | 13/21 | 1/2 | 1/1 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+SequentialSearch | 15/24 | 62% | 13 | 40.0 | 11 | 6/6 | 3/6 | 3/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+SequentialSearch | 15/24 | 62% | 14 | 41.0 | 10 | 6/6 | 3/6 | 3/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| MostFrequentLocation+SequentialSearch | 15/24 | 62% | 14 | 41.0 | 11 | 6/6 | 3/6 | 3/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+SequentialSearch | 15/24 | 62% | 14 | 41.0 | 11 | 6/6 | 3/6 | 3/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 18 | 42.0 | 14 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 18 | 42.0 | 14 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 21 | 45.0 | 9 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 21 | 45.0 | 9 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+SequentialSearch | 15/24 | 62% | 22 | 27.0 | 2 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+SequentialSearch | 15/24 | 62% | 22 | 27.0 | 2 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 45 | 26.0 | 2 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 45 | 26.0 | 2 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 15/24 | 62% | 45 | 26.0 | 2 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 15/24 | 62% | 45 | 26.0 | 2 | 5/6 | 3/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+SequentialSearch | 14/24 | 58% | 7 | 25.0 | 2 | 5/6 | 3/6 | 3/6 | 3/6 | 14/21 | 0/2 | 0/1 |
| LastObservation+SequentialSearch | 14/24 | 58% | 7 | 25.0 | 2 | 5/6 | 3/6 | 3/6 | 3/6 | 14/21 | 0/2 | 0/1 |
| LastObservation+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 14/24 | 58% | 10 | 25.0 | 3 | 5/6 | 3/6 | 3/6 | 3/6 | 14/21 | 0/2 | 0/1 |
| LastObservation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 10 | 25.0 | 3 | 5/6 | 3/6 | 3/6 | 3/6 | 14/21 | 0/2 | 0/1 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 14/24 | 58% | 11 | 26.0 | 3 | 5/6 | 3/6 | 3/6 | 3/6 | 14/21 | 0/2 | 0/1 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 11 | 26.0 | 3 | 5/6 | 3/6 | 3/6 | 3/6 | 14/21 | 0/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.02) | 14/24 | 58% | 11 | 11.0 | 0 | 5/6 | 4/6 | 3/6 | 2/6 | 14/21 | 0/2 | 0/1 |
| MostFrequentLocation+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 16 | 40.0 | 16 | 5/6 | 3/6 | 2/6 | 4/6 | 12/21 | 2/2 | 0/1 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIBudgetPriceSense(gamma=0.5,lambda0=0.05) | 14/24 | 58% | 16 | 40.0 | 15 | 5/6 | 3/6 | 3/6 | 3/6 | 14/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 16 | 40.0 | 16 | 5/6 | 3/6 | 2/6 | 4/6 | 12/21 | 2/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 14/24 | 58% | 17 | 41.0 | 15 | 5/6 | 3/6 | 3/6 | 3/6 | 14/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.1) | 13/24 | 54% | 7 | 7.0 | 0 | 5/6 | 4/6 | 2/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 8 | 8.0 | 0 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 8 | 8.0 | 0 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 8 | 8.0 | 0 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.05) | 13/24 | 54% | 9 | 12.0 | 0 | 5/6 | 4/6 | 2/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 9 | 9.0 | 0 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 41 | 11.0 | 0 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.05) | 13/24 | 54% | 41 | 9.0 | 0 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.02) | 13/24 | 54% | 41 | 11.0 | 0 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.05) | 13/24 | 54% | 41 | 9.0 | 0 | 5/6 | 3/6 | 3/6 | 2/6 | 13/21 | 0/2 | 0/1 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| LastObservation+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| LastObservation+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| MostFrequentLocation+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+NeverSense | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.1) | 12/24 | 50% | 0 | 0.0 | 0 | 5/6 | 3/6 | 3/6 | 1/6 | 12/21 | 0/2 | 0/1 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 5/6 | 3/6 | 2/6 | 2/6 | 12/21 | 0/2 | 0/1 |
| LastObservation+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 6 | 6.0 | 0 | 5/6 | 3/6 | 2/6 | 2/6 | 12/21 | 0/2 | 0/1 |
| LastObservation+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 5/6 | 3/6 | 2/6 | 2/6 | 12/21 | 0/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 5/6 | 3/6 | 2/6 | 2/6 | 12/21 | 0/2 | 0/1 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 5/6 | 3/6 | 2/6 | 2/6 | 12/21 | 0/2 | 0/1 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 5/6 | 3/6 | 2/6 | 2/6 | 12/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 5/6 | 3/6 | 2/6 | 2/6 | 12/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.05) | 12/24 | 50% | 6 | 6.0 | 0 | 5/6 | 3/6 | 2/6 | 2/6 | 12/21 | 0/2 | 0/1 |
| DaytypeMixture(K=3,bin=2h,hl=24h)+VoIThresholdSense(lambda=0.02) | 12/24 | 50% | 7 | 7.0 | 0 | 5/6 | 3/6 | 2/6 | 2/6 | 12/21 | 0/2 | 0/1 |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | headphones_ines | dresser_b1 | 70/70 |
| q02 | sunglasses_ines | entry_table_e1 | 70/70 |
| q03 | shoes_ines | shoe_rack_e1 | 70/70 |
| q04 | razor_hana | sink_ba_ba1 | 70/70 |
| q05 | glasses_yuki | nightstand_b1 | 8/70 |
| q06 | tablet_yuki | nightstand_b1 | 70/70 |
| q07 | kitchen_knife_shared | drawer_k_k1 | 70/70 |
| q08 | keys_ines | OUT_OF_HOUSE | 2/70 |
| q09 | plate_yuki | dish_rack_k1 | 4/70 |
| q10 | remote_shared | coffee_table_l1 | 0/70 |
| q11 | shoes_yuki | shoe_rack_e1 | 70/70 |
| q12 | razor_yuki | sink_ba_ba1 | 70/70 |
| q13 | phone_hana | nightstand_b2 | 5/70 |
| q14 | keys_ines | entry_table_e1 | 70/70 |
| q15 | sunglasses_yuki | entry_table_e1 | 70/70 |
| q16 | shoes_yuki | entry_floor_e1 | 27/70 |
| q17 | towel_hana | bathroom_shelf_ba1 | 8/70 |
| q18 | glass_yuki | cupboard_k1 | 35/70 |
| q19 | sunglasses_hana | entry_table_e1 | 70/70 |
| q20 | phone_yuki | entry_floor_e1 | 27/70 |
| q21 | phone_ines | ON_PERSON | 4/70 |
| q22 | headphones_ines | couch_l1 | 0/70 |
| q23 | phone_hana | ON_PERSON | 3/70 |
| q24 | plate_ines | cupboard_k1 | 49/70 |
