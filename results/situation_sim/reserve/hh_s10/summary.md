# situation_sim baselines · hh_s10

20 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MostFrequentLocation+Reserve(1)[SequentialSearch] | 17/24 | 71% | 17 | 41.0 | 0 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[SequentialSearch] | 17/24 | 71% | 17 | 41.0 | 0 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 17/24 | 71% | 20 | 44.0 | 0 | 2/6 | 6/6 | 4/6 | 5/6 | 17/18 | - | 0/6 |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 13 | 25.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 13 | 25.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[SequentialSearch] | 16/24 | 67% | 14 | 41.0 | 0 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 16/24 | 67% | 14 | 26.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 14 | 26.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 15 | 27.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[SequentialSearch] | 16/24 | 67% | 15 | 39.0 | 0 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 16/24 | 67% | 15 | 27.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 16/24 | 67% | 16 | 28.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 16/24 | 67% | 17 | 29.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 16/24 | 67% | 18 | 30.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 16/24 | 67% | 18 | 42.0 | 0 | 2/6 | 6/6 | 3/6 | 5/6 | 16/18 | - | 0/6 |
| MostFrequentLocation+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 16/24 | 67% | 19 | 43.0 | 0 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 16/24 | 67% | 19 | 43.0 | 0 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 16/24 | 67% | 21 | 42.0 | 0 | 2/6 | 6/6 | 4/6 | 4/6 | 16/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[SequentialSearch] | 15/24 | 62% | 16 | 40.0 | 0 | 2/6 | 6/6 | 4/6 | 3/6 | 15/18 | - | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 15/24 | 62% | 18 | 42.0 | 0 | 2/6 | 6/6 | 4/6 | 3/6 | 15/18 | - | 0/6 |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | vitamins_omar | kitchen_table_k1 | 20/20 |
| q02 | skincare_omar | bathroom_shelf_ba1 | 20/20 |
| q03 | shoes_yuki | OUT_OF_HOUSE | 0/20 |
| q04 | handbag_omar | OUT_OF_HOUSE | 0/20 |
| q05 | scarf_omar | OUT_OF_HOUSE | 0/20 |
| q06 | shoes_omar | OUT_OF_HOUSE | 0/20 |
| q07 | plate_omar | cupboard_k1 | 20/20 |
| q08 | controller_omar | tv_stand_l1 | 20/20 |
| q09 | glass_yuki | sink_k1 | 20/20 |
| q10 | remote_shared | tv_stand_l1 | 20/20 |
| q11 | glasses_omar | nightstand_b1 | 20/20 |
| q12 | pot_shared | cupboard_k1 | 20/20 |
| q13 | pen_omar | entry_hook_e1 | 10/20 |
| q14 | bike_lock_omar | entry_table_e1 | 20/20 |
| q15 | laptop_yuki | entry_hook_e1 | 20/20 |
| q16 | bowl_omar | cupboard_k1 | 20/20 |
| q17 | phone_yuki | OUT_OF_HOUSE | 0/20 |
| q18 | jacket_yuki | OUT_OF_HOUSE | 0/20 |
| q19 | wallet_yuki | entry_floor_e1 | 8/20 |
| q20 | scarf_omar | wardrobe_b1 | 10/20 |
| q21 | remote_shared | tv_stand_l1 | 20/20 |
| q22 | plate_omar | cupboard_k1 | 20/20 |
| q23 | glass_yuki | sink_k1 | 20/20 |
| q24 | wallet_yuki | entry_table_e1 | 13/20 |
