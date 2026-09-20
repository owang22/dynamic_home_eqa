# situation_sim baselines · hh_s10

20 agents (belief x policy), 24 questions, room-level looks (1 + 3 travel), budget 12/day, walkthrough Wed 18:00.

| agent | right | acc | looks | budget | forced | Thu | Fri | Sat | Sun | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[SequentialSearch] | 15/24 | 62% | 14 | 41.0 | 0 | 2/6 | 5/6 | 4/6 | 4/6 | 15/17 | 0/1 | 0/6 |
| MostFrequentLocation+Reserve(1)[SequentialSearch] | 15/24 | 62% | 15 | 42.0 | 0 | 2/6 | 5/6 | 4/6 | 4/6 | 15/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[SequentialSearch] | 15/24 | 62% | 15 | 42.0 | 0 | 2/6 | 5/6 | 4/6 | 4/6 | 15/17 | 0/1 | 0/6 |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 14/24 | 58% | 14 | 41.0 | 0 | 2/6 | 5/6 | 4/6 | 3/6 | 14/17 | 0/1 | 0/6 |
| MostFrequentLocation+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 14/24 | 58% | 15 | 39.0 | 0 | 2/6 | 5/6 | 4/6 | 3/6 | 14/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[SequentialSearch] | 14/24 | 58% | 16 | 43.0 | 0 | 2/6 | 5/6 | 4/6 | 3/6 | 14/17 | 0/1 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 14/24 | 58% | 16 | 40.0 | 0 | 2/6 | 5/6 | 4/6 | 3/6 | 14/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 14/24 | 58% | 19 | 43.0 | 0 | 2/6 | 5/6 | 4/6 | 3/6 | 14/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 14/24 | 58% | 20 | 44.0 | 0 | 2/6 | 5/6 | 4/6 | 3/6 | 14/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 13/24 | 54% | 13 | 34.0 | 0 | 2/6 | 4/6 | 4/6 | 3/6 | 13/17 | 0/1 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 13/24 | 54% | 14 | 38.0 | 0 | 2/6 | 4/6 | 4/6 | 3/6 | 13/17 | 0/1 | 0/6 |
| MostFrequentLocation+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 13/24 | 54% | 21 | 45.0 | 0 | 1/6 | 5/6 | 4/6 | 3/6 | 13/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 13/24 | 54% | 21 | 45.0 | 0 | 1/6 | 5/6 | 4/6 | 3/6 | 13/17 | 0/1 | 0/6 |
| SmoothedRecency(hl=6h,freq=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 13/24 | 54% | 23 | 44.0 | 0 | 1/6 | 5/6 | 4/6 | 3/6 | 13/17 | 0/1 | 0/6 |
| TimetableLookup(bin=1h,days=all)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 12/24 | 50% | 11 | 32.0 | 0 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.02)] | 12/24 | 50% | 14 | 32.0 | 0 | 2/6 | 3/6 | 4/6 | 3/6 | 12/17 | 0/1 | 0/6 |
| HierarchyBackoff(po=5,pc=5,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 12/24 | 50% | 24 | 45.0 | 0 | 1/6 | 5/6 | 4/6 | 2/6 | 12/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[SequentialSearch] | 11/24 | 46% | 13 | 46.0 | 0 | 2/6 | 3/6 | 4/6 | 2/6 | 11/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIThresholdSense(lambda=0.01)] | 11/24 | 46% | 16 | 34.0 | 0 | 2/6 | 3/6 | 4/6 | 2/6 | 11/17 | 0/1 | 0/6 |
| Markov1(a=1,cut=24h,hl=24h)+Reserve(1)[VoIBudgetPriceSense(gamma=0.5,lambda0=0.05)] | 11/24 | 46% | 19 | 40.0 | 0 | 1/6 | 4/6 | 4/6 | 2/6 | 10/17 | 0/1 | 1/6 |

## Question difficulty (agents that got it right)

| q | object | truth | solved by |
|---|---|---|---|
| q01 | wallet_omar | entry_floor_e1 | 15/20 |
| q02 | snack_bowl_shared | counter_k1 | 20/20 |
| q03 | shoes_yuki | OUT_OF_HOUSE | 0/20 |
| q04 | handbag_omar | OUT_OF_HOUSE | 0/20 |
| q05 | scarf_omar | OUT_OF_HOUSE | 0/20 |
| q06 | shoes_omar | OUT_OF_HOUSE | 0/20 |
| q07 | phone_yuki | coffee_table_l1 | 1/20 |
| q08 | controller_omar | tv_stand_l1 | 20/20 |
| q09 | glass_omar | sink_k1 | 19/20 |
| q10 | razor_yuki | sink_ba_ba1 | 20/20 |
| q11 | glass_yuki | cupboard_k1 | 13/20 |
| q12 | pot_shared | cupboard_k1 | 16/20 |
| q13 | pen_omar | entry_hook_e1 | 19/20 |
| q14 | bike_lock_omar | entry_table_e1 | 20/20 |
| q15 | laptop_yuki | entry_hook_e1 | 20/20 |
| q16 | bowl_omar | cupboard_k1 | 20/20 |
| q17 | phone_yuki | OUT_OF_HOUSE | 0/20 |
| q18 | jacket_yuki | OUT_OF_HOUSE | 1/20 |
| q19 | wallet_yuki | entry_table_e1 | 19/20 |
| q20 | scarf_omar | wardrobe_b1 | 1/20 |
| q21 | razor_yuki | bathroom_shelf_ba1 | 4/20 |
| q22 | phone_yuki | ON_PERSON | 0/20 |
| q23 | glass_yuki | sink_k1 | 15/20 |
| q24 | wallet_yuki | entry_table_e1 | 20/20 |
