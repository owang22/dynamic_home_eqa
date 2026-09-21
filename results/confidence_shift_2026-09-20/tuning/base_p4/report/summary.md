# base p4

10 households, 4 agents, 8960 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5]; hh_s1 [3, 4, 5]; hh_s2 [4, 5, 7]; hh_s3 [4, 5]; hh_s4 [4, 5, 6, 7]; hh_s5 [2, 4, 5]; hh_s6 [4, 5]; hh_s7 [4, 5]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 224, hh_s1 224, hh_s2 224, hh_s3 224, hh_s4 224, hh_s5 224, hh_s6 224, hh_s7 224, hh_s8 224, hh_s9 224.

Object classes in the questions: glass 4%, bowl 3%, mug 3%, plate 3%, book 3%, towel 3%, umbrella 3%, jacket 2%, laptop 2%, shoes 2%, pen 2%, skincare 2%, water_bottle 2%, wallet 2%, remote 2%, kitchen_knife 2%, shopping_bag 2%, keys 2%, pan 2%, vacuum_cleaner 2%, headphones 2%, blanket 2%, razor 2%, charger 2%, snack_bowl 2%, spatula 2%, cutting_board 1%, notebook 1%, speaker 1%, toolbox 1%, laundry_basket 1%, tablet 1%, toiletry_bag 1%, dog_food_bag 1%, magazine 1%, scarf 1%, sunglasses 1%, board_game 1%, recipe_book 1%, dog_leash 1%, glasses 1%, backpack 1%, dog_bowl 1%, medication 1%, dog_toy 1%, gym_bag 1%, pot 1%, vitamins 1%, watering_can 1%, detergent 1%, duster 1%, hair_dryer 1%, hat 1%, lunchbox 1%, running_shoes 1%, gardening_gloves 1%, first_aid_kit 1%, ironing_board 1%, puzzle_box 1%, baking_tray 1%, mixing_bowl 1%, serving_dish 0%, mouse 0%, bike_lock 0%, guitar 0%, helmet 0%, meditation_cushion 0%, iron 0%, handbag 0%, pencil_case 0%, yoga_mat 0%, camera 0%, phone 0%, textbook 0%, knitting_bag 0%, sketchbook 0%, spray_bottle 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 89% | 92% | 94% | 91% | 93% | 89% | 89% | 91% |
| TimetableLookup(bin=1h,days=all) | 87% | 92% | 92% | 88% | 92% | 88% | 88% | 90% |
| last seen | 89% | 92% | 94% | 91% | 93% | 89% | 89% | 91% |
| most frequent | 88% | 92% | 93% | 89% | 92% | 89% | 90% | 90% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 99% / 90% | 99% / 92% | 100% / 94% | 100% / 91% | 100% / 93% | 100% / 89% | 100% / 89% | 100% / 91% |
| TimetableLookup(bin=1h,days=all) | 97% / 89% | 97% / 92% | 98% / 94% | 97% / 90% | 97% / 94% | 98% / 90% | 96% / 91% | 97% / 91% |
| last seen | 100% / 89% | 100% / 92% | 100% / 94% | 100% / 91% | 100% / 93% | 100% / 89% | 100% / 89% | 100% / 91% |
| most frequent | 99% / 89% | 98% / 92% | 98% / 94% | 98% / 89% | 99% / 93% | 99% / 90% | 98% / 91% | 98% / 91% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 97% / 90% | 98% / 92% | 99% / 94% | 99% / 91% | 100% / 93% | 100% / 90% | 100% / 90% | 99% / 91% |
| TimetableLookup(bin=1h,days=all) | 94% / 90% | 96% / 92% | 92% / 95% | 91% / 93% | 92% / 95% | 93% / 92% | 92% / 92% | 93% / 93% |
| last seen | 100% / 89% | 100% / 92% | 100% / 94% | 100% / 91% | 100% / 93% | 100% / 89% | 100% / 89% | 100% / 91% |
| most frequent | 95% / 90% | 96% / 92% | 92% / 95% | 92% / 93% | 93% / 94% | 93% / 93% | 92% / 93% | 93% / 93% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% / 90% | 97% / 92% | 96% / 95% | 97% / 91% | 98% / 93% | 99% / 90% | 98% / 91% | 96% / 92% |
| TimetableLookup(bin=1h,days=all) | 82% / 91% | 85% / 93% | 78% / 97% | 74% / 97% | 76% / 95% | 76% / 94% | 75% / 97% | 78% / 95% |
| last seen | 100% / 89% | 100% / 92% | 100% / 94% | 100% / 91% | 100% / 93% | 100% / 89% | 100% / 89% | 100% / 91% |
| most frequent | 86% / 92% | 88% / 93% | 81% / 98% | 77% / 96% | 79% / 95% | 78% / 95% | 77% / 98% | 81% / 95% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | - | 0% (n=2) | 0% (n=3) | 83% (n=12) | 70% (n=10) | 76% (n=25) | 79% (n=29) | 88% (n=116) | 92% (n=2043) | 0.069 |
| TimetableLookup(bin=1h,days=all) | - | 22% (n=41) | 61% (n=28) | 50% (n=40) | 65% (n=52) | 78% (n=96) | 84% (n=235) | 87% (n=260) | 96% (n=1488) | 0.029 |
| last seen | - | - | - | - | - | - | - | - | 91% (n=2240) | 0.088 |
| most frequent | - | 0% (n=3) | 54% (n=35) | 53% (n=45) | 64% (n=66) | 78% (n=112) | 78% (n=171) | 86% (n=247) | 97% (n=1561) | 0.030 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | +5 | +3 | -4 (8) | 89 | 94 |
| TimetableLookup(bin=1h,days=all) | +5 | +4 | -2 (8) | 87 | 92 |
| last seen | +5 | +3 | -4 (8) | 89 | 94 |
| most frequent | +4 | +4 | -3 (8) | 88 | 93 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2], 'hh_s1': [3, 4], 'hh_s2': [7], 'hh_s3': [5], 'hh_s4': [4, 5, 6, 7], 'hh_s5': [2], 'hh_s6': [], 'hh_s7': [5], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: PeriodicPersistence(min_dep=2,bin=1h,hl=24h) (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **81%** | **91%** | 81% | **88%** | **100%** | 94% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 91% | 97% | **97%** | **91%** | **84%** | 97% | 88% | [3, 4, 5] | [3, 4] |
| hh_s2 | 88% | 88% | 91% | **91%** | **91%** | 84% | **78%** | [4, 5, 7] | [7] |
| hh_s3 | 91% | 94% | 94% | **97%** | **94%** | 94% | 97% | [4, 5] | [5] |
| hh_s4 | 94% | 97% | 97% | **81%** | **94%** | **94%** | **94%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 91% | **94%** | 97% | **91%** | **94%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 84% | 91% | 97% | **97%** | **97%** | 84% | 97% | [4, 5] | [] |
| hh_s7 | 94% | 97% | 97% | **88%** | **94%** | 91% | 94% | [4, 5] | [5] |
| hh_s8 | **91%** | 91% | **91%** | **97%** | **97%** | 84% | **91%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 88% | 81% | **97%** | **88%** | **91%** | **84%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: TimetableLookup(bin=1h,days=all) (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **81%** | **88%** | 81% | **88%** | **94%** | 91% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 91% | 100% | **94%** | **94%** | **84%** | 97% | 91% | [3, 4, 5] | [3, 4] |
| hh_s2 | 78% | 88% | 91% | **88%** | **84%** | 84% | **72%** | [4, 5, 7] | [7] |
| hh_s3 | 91% | 94% | 91% | **94%** | **91%** | 97% | 94% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 97% | **81%** | **94%** | **91%** | **94%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 88% | **94%** | 94% | **81%** | **91%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 84% | 88% | 97% | **94%** | **94%** | 81% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 97% | 94% | **84%** | **94%** | 88% | 94% | [4, 5] | [5] |
| hh_s8 | **91%** | 91% | **91%** | **97%** | **100%** | 84% | **88%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 88% | 81% | **94%** | **84%** | **91%** | **84%** | 78% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **81%** | **91%** | 81% | **88%** | **100%** | 94% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 91% | 94% | **97%** | **91%** | **84%** | 97% | 88% | [3, 4, 5] | [3, 4] |
| hh_s2 | 88% | 88% | 91% | **91%** | **91%** | 84% | **78%** | [4, 5, 7] | [7] |
| hh_s3 | 91% | 94% | 94% | **97%** | **94%** | 94% | 97% | [4, 5] | [5] |
| hh_s4 | 94% | 97% | 97% | **81%** | **94%** | **94%** | **94%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 91% | **94%** | 97% | **91%** | **94%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 84% | 91% | 97% | **97%** | **97%** | 84% | 97% | [4, 5] | [] |
| hh_s7 | 94% | 97% | 97% | **88%** | **94%** | 91% | 94% | [4, 5] | [5] |
| hh_s8 | **91%** | 91% | **91%** | **97%** | **97%** | 84% | **91%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 88% | 81% | **97%** | **88%** | **91%** | **84%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **81%** | **91%** | 81% | **88%** | **100%** | 91% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 91% | 97% | **94%** | **91%** | **84%** | 97% | 91% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 88% | 91% | **91%** | **88%** | 84% | **78%** | [4, 5, 7] | [7] |
| hh_s3 | 91% | 94% | 94% | **97%** | **91%** | 97% | 94% | [4, 5] | [5] |
| hh_s4 | 94% | 97% | 97% | **81%** | **94%** | **91%** | **94%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 91% | **94%** | 97% | **84%** | **91%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 84% | 91% | 97% | **94%** | **97%** | 84% | 97% | [4, 5] | [] |
| hh_s7 | 94% | 97% | 94% | **84%** | **94%** | 91% | 94% | [4, 5] | [5] |
| hh_s8 | **91%** | 91% | **91%** | **97%** | **97%** | 84% | **91%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 88% | 81% | **94%** | **84%** | **91%** | **84%** | 78% | [3, 4, 5, 6] | [3, 4, 6] |
