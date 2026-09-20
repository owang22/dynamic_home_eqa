# situation_sim baselines · hh_s9

20 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MostFrequentLocation+Reserve(1)[SequentialSearch] | 19/24 | 79% | 13 | 37.0 | 0 | 6/6 | 4/6 | 5/6 | 4/6 | 19/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[SequentialSearch] | 18/24 | 75% | 12 | 39.0 | 0 | 6/6 | 4/6 | 4/6 | 4/6 | 18/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[SequentialSearch] | 18/24 | 75% | 13 | 37.0 | 0 | 6/6 | 4/6 | 4/6 | 4/6 | 18/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[SequentialSearch] | 18/24 | 75% | 13 | 37.0 | 0 | 6/6 | 4/6 | 5/6 | 3/6 | 18/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 18/24 | 75% | 17 | 41.0 | 0 | 6/6 | 4/6 | 4/6 | 4/6 | 18/21 | 0/2 | 0/1 |
| MostFrequentLocation+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 17/24 | 71% | 16 | 40.0 | 0 | 5/6 | 4/6 | 4/6 | 4/6 | 17/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 17/24 | 71% | 17 | 38.0 | 0 | 6/6 | 3/6 | 5/6 | 3/6 | 17/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 17/24 | 71% | 18 | 42.0 | 0 | 5/6 | 4/6 | 4/6 | 4/6 | 17/21 | 0/2 | 0/1 |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 8 | 23.0 | 0 | 4/6 | 3/6 | 5/6 | 4/6 | 16/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 8 | 23.0 | 0 | 4/6 | 3/6 | 5/6 | 4/6 | 16/21 | 0/2 | 0/1 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 12 | 30.0 | 0 | 6/6 | 3/6 | 4/6 | 3/6 | 16/21 | 0/2 | 0/1 |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 16/24 | 67% | 16 | 31.0 | 0 | 4/6 | 4/6 | 5/6 | 3/6 | 16/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 16/24 | 67% | 16 | 40.0 | 0 | 5/6 | 4/6 | 4/6 | 3/6 | 16/21 | 0/2 | 0/1 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 16/24 | 67% | 16 | 31.0 | 0 | 4/6 | 4/6 | 5/6 | 3/6 | 16/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 15/24 | 62% | 11 | 26.0 | 0 | 4/6 | 3/6 | 5/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[SequentialSearch] | 15/24 | 62% | 13 | 40.0 | 0 | 4/6 | 4/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 15/24 | 62% | 14 | 26.0 | 0 | 4/6 | 3/6 | 5/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 15/24 | 62% | 15 | 24.0 | 0 | 4/6 | 4/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 15/24 | 62% | 15 | 24.0 | 0 | 4/6 | 4/6 | 4/6 | 3/6 | 15/21 | 0/2 | 0/1 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 14/24 | 58% | 13 | 37.0 | 0 | 4/6 | 3/6 | 4/6 | 3/6 | 14/21 | 0/2 | 0/1 |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | headphones_ines | desk_b1 | 20/20 |
| q02 | sunglasses_ines | entry_table_e1 | 20/20 |
| q03 | shoes_ines | shoe_rack_e1 | 10/20 |
| q04 | razor_hana | sink_ba_ba1 | 20/20 |
| q05 | glasses_yuki | nightstand_b1 | 7/20 |
| q06 | tablet_yuki | nightstand_b1 | 20/20 |
| q07 | kitchen_knife_shared | drawer_k_k1 | 20/20 |
| q08 | keys_ines | OUT_OF_HOUSE | 0/20 |
| q09 | plate_ines | kitchen_table_k1 | 14/20 |
| q10 | remote_shared | coffee_table_l1 | 0/20 |
| q11 | shoes_yuki | entry_floor_e1 | 19/20 |
| q12 | razor_hana | sink_ba_ba1 | 20/20 |
| q13 | phone_hana | nightstand_b2 | 0/20 |
| q14 | keys_ines | entry_table_e1 | 20/20 |
| q15 | sunglasses_yuki | entry_table_e1 | 20/20 |
| q16 | shoes_yuki | entry_floor_e1 | 19/20 |
| q17 | towel_hana | towel_rack_ba1 | 20/20 |
| q18 | glass_yuki | cupboard_k1 | 10/20 |
| q19 | sunglasses_hana | entry_table_e1 | 20/20 |
| q20 | phone_yuki | nightstand_b1 | 13/20 |
| q21 | phone_ines | ON_PERSON | 0/20 |
| q22 | jacket_hana | shoe_rack_e1 | 17/20 |
| q23 | phone_hana | ON_PERSON | 0/20 |
| q24 | plate_ines | cupboard_k1 | 18/20 |
