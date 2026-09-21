# p12

10 households, 4 agents, 8960 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5]; hh_s1 [3, 4, 5]; hh_s2 [4, 5, 7]; hh_s3 [4, 5]; hh_s4 [4, 5, 6, 7]; hh_s5 [2, 4, 5]; hh_s6 [4, 5]; hh_s7 [4, 5]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 224, hh_s1 224, hh_s2 224, hh_s3 224, hh_s4 224, hh_s5 224, hh_s6 224, hh_s7 224, hh_s8 224, hh_s9 224.

Object classes in the questions: glass 4%, bowl 3%, mug 3%, plate 3%, book 3%, towel 3%, umbrella 3%, jacket 2%, laptop 2%, shoes 2%, pen 2%, skincare 2%, water_bottle 2%, wallet 2%, remote 2%, kitchen_knife 2%, shopping_bag 2%, keys 2%, pan 2%, vacuum_cleaner 2%, headphones 2%, blanket 2%, razor 2%, charger 2%, snack_bowl 2%, spatula 2%, cutting_board 1%, notebook 1%, speaker 1%, toolbox 1%, laundry_basket 1%, tablet 1%, toiletry_bag 1%, dog_food_bag 1%, magazine 1%, scarf 1%, sunglasses 1%, board_game 1%, recipe_book 1%, dog_leash 1%, glasses 1%, backpack 1%, dog_bowl 1%, medication 1%, dog_toy 1%, gym_bag 1%, pot 1%, vitamins 1%, watering_can 1%, detergent 1%, duster 1%, hair_dryer 1%, hat 1%, lunchbox 1%, running_shoes 1%, gardening_gloves 1%, first_aid_kit 1%, ironing_board 1%, puzzle_box 1%, baking_tray 1%, mixing_bowl 1%, serving_dish 0%, mouse 0%, bike_lock 0%, guitar 0%, helmet 0%, meditation_cushion 0%, iron 0%, handbag 0%, pencil_case 0%, yoga_mat 0%, camera 0%, phone 0%, textbook 0%, knitting_bag 0%, sketchbook 0%, spray_bottle 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 83% | 88% | 87% | 85% | 87% | 87% | 84% | 86% |
| most frequent | 83% | 88% | 86% | 84% | 83% | 85% | 83% | 85% |
| periodic | 83% | 88% | 87% | 85% | 87% | 87% | 84% | 86% |
| timetable | 82% | 88% | 86% | 83% | 84% | 84% | 83% | 84% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 83% | 100% / 88% | 100% / 87% | 100% / 85% | 100% / 87% | 100% / 87% | 100% / 84% | 100% / 86% |
| most frequent | 92% / 86% | 95% / 90% | 91% / 90% | 93% / 88% | 94% / 86% | 92% / 89% | 90% / 89% | 92% / 88% |
| periodic | 88% / 86% | 96% / 89% | 98% / 87% | 97% / 86% | 98% / 87% | 98% / 88% | 98% / 85% | 96% / 87% |
| timetable | 91% / 86% | 94% / 90% | 90% / 90% | 91% / 88% | 91% / 88% | 91% / 89% | 88% / 89% | 91% / 89% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 83% | 100% / 88% | 100% / 87% | 100% / 85% | 100% / 87% | 100% / 87% | 100% / 84% | 100% / 86% |
| most frequent | 80% / 88% | 84% / 91% | 83% / 92% | 83% / 89% | 79% / 92% | 80% / 93% | 80% / 93% | 81% / 91% |
| periodic | 70% / 88% | 91% / 89% | 93% / 88% | 95% / 86% | 95% / 89% | 95% / 90% | 97% / 85% | 91% / 88% |
| timetable | 78% / 87% | 82% / 91% | 82% / 93% | 81% / 90% | 78% / 92% | 79% / 93% | 79% / 93% | 80% / 91% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 83% | 100% / 88% | 100% / 87% | 100% / 85% | 100% / 87% | 100% / 87% | 100% / 84% | 100% / 86% |
| most frequent | 23% / 95% | 41% / 93% | 64% / 96% | 56% / 96% | 61% / 93% | 55% / 96% | 59% / 96% | 51% / 95% |
| periodic | 18% / 90% | 38% / 92% | 43% / 86% | 57% / 84% | 58% / 87% | 64% / 89% | 68% / 85% | 49% / 87% |
| timetable | 22% / 94% | 38% / 92% | 59% / 96% | 54% / 96% | 57% / 93% | 53% / 96% | 56% / 96% | 48% / 95% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| last seen | - | - | - | - | - | - | - | - | 86% (n=2240) | 0.138 |
| most frequent | 0% (n=2) | 38% (n=65) | 48% (n=103) | 59% (n=118) | 75% (n=132) | 81% (n=247) | 87% (n=426) | 92% (n=526) | 98% (n=621) | 0.022 |
| periodic | 20% (n=5) | 59% (n=49) | 68% (n=34) | 72% (n=36) | 69% (n=81) | 86% (n=321) | 91% (n=606) | 92% (n=285) | 85% (n=823) | 0.093 |
| timetable | 0% (n=2) | 36% (n=103) | 47% (n=96) | 62% (n=109) | 77% (n=142) | 85% (n=311) | 87% (n=395) | 92% (n=492) | 97% (n=590) | 0.031 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| last seen | +3 | +2 | +2 (8) | 83 | 88 |
| most frequent | +3 | +2 | +2 (8) | 83 | 88 |
| periodic | +3 | +1 | +2 (8) | 83 | 88 |
| timetable | +4 | +3 | +4 (8) | 82 | 88 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2], 'hh_s1': [3, 4], 'hh_s2': [7], 'hh_s3': [5], 'hh_s4': [4, 5, 6, 7], 'hh_s5': [2], 'hh_s6': [], 'hh_s7': [5], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **78%** | **91%** | 75% | **78%** | **94%** | 94% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 84% | **94%** | **88%** | **81%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 81% | 75% | **84%** | **97%** | 88% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 88% | 84% | **84%** | **94%** | 94% | 88% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 97% | **81%** | **88%** | **84%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **84%** | 94% | **84%** | **75%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 69% | 88% | 88% | **88%** | **97%** | 88% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 94% | 94% | **81%** | **66%** | 91% | 91% | [4, 5] | [5] |
| hh_s8 | **84%** | 91% | **84%** | **91%** | **94%** | 78% | **78%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 81% | 84% | **81%** | **91%** | **84%** | **75%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **78%** | **91%** | 75% | **75%** | **91%** | 81% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 88% | **94%** | **91%** | **78%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 81% | 78% | **81%** | **84%** | 84% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 88% | 84% | **88%** | **88%** | 91% | 75% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 97% | **81%** | **84%** | **84%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 97% | **84%** | 91% | **81%** | **78%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 69% | 88% | 84% | **88%** | **91%** | 88% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 94% | 94% | **78%** | **66%** | 91% | 91% | [4, 5] | [5] |
| hh_s8 | **81%** | 91% | **84%** | **91%** | **91%** | 78% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 81% | 84% | **81%** | **91%** | **84%** | **75%** | 84% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **78%** | **91%** | 75% | **78%** | **94%** | 94% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 84% | **94%** | **88%** | **81%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 81% | 75% | **84%** | **97%** | 88% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 88% | 84% | **88%** | **94%** | 94% | 88% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 97% | **81%** | **88%** | **84%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **84%** | 94% | **84%** | **75%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 69% | 88% | 88% | **88%** | **97%** | 88% | 97% | [4, 5] | [] |
| hh_s7 | 88% | 94% | 94% | **81%** | **66%** | 91% | 91% | [4, 5] | [5] |
| hh_s8 | **84%** | 91% | **84%** | **91%** | **94%** | 78% | **78%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 81% | 84% | **81%** | **91%** | **84%** | **75%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **78%** | **88%** | 75% | **75%** | **88%** | 81% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 91% | **94%** | **94%** | **78%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 78% | 81% | 81% | **78%** | **84%** | 84% | **66%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 88% | 84% | **84%** | **88%** | 91% | 78% | [4, 5] | [5] |
| hh_s4 | 88% | 97% | 97% | **81%** | **88%** | **84%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **84%** | 88% | **78%** | **78%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 69% | 84% | 84% | **84%** | **88%** | 84% | 91% | [4, 5] | [] |
| hh_s7 | 88% | 94% | 94% | **78%** | **69%** | 88% | 91% | [4, 5] | [5] |
| hh_s8 | **81%** | 91% | **84%** | **91%** | **94%** | 78% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 81% | 84% | **81%** | **91%** | **84%** | **75%** | 84% | [3, 4, 5, 6] | [3, 4, 6] |
