# t03

10 households, 4 agents, 8960 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5]; hh_s1 [3, 4, 5]; hh_s2 [4, 5, 7]; hh_s3 [4, 5]; hh_s4 [4, 5, 6, 7]; hh_s5 [2, 4, 5]; hh_s6 [4, 5]; hh_s7 [4, 5]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 224, hh_s1 224, hh_s2 224, hh_s3 224, hh_s4 224, hh_s5 224, hh_s6 224, hh_s7 224, hh_s8 224, hh_s9 224.

Object classes in the questions: glass 4%, bowl 3%, mug 3%, plate 3%, book 3%, towel 3%, umbrella 3%, jacket 2%, laptop 2%, shoes 2%, pen 2%, skincare 2%, water_bottle 2%, wallet 2%, remote 2%, kitchen_knife 2%, shopping_bag 2%, keys 2%, pan 2%, vacuum_cleaner 2%, headphones 2%, blanket 2%, razor 2%, charger 2%, snack_bowl 2%, spatula 2%, cutting_board 1%, notebook 1%, speaker 1%, toolbox 1%, laundry_basket 1%, tablet 1%, toiletry_bag 1%, dog_food_bag 1%, magazine 1%, scarf 1%, sunglasses 1%, board_game 1%, recipe_book 1%, dog_leash 1%, glasses 1%, backpack 1%, dog_bowl 1%, medication 1%, dog_toy 1%, gym_bag 1%, pot 1%, vitamins 1%, watering_can 1%, detergent 1%, duster 1%, hair_dryer 1%, hat 1%, lunchbox 1%, running_shoes 1%, gardening_gloves 1%, first_aid_kit 1%, ironing_board 1%, puzzle_box 1%, baking_tray 1%, mixing_bowl 1%, serving_dish 0%, mouse 0%, bike_lock 0%, guitar 0%, helmet 0%, meditation_cushion 0%, iron 0%, handbag 0%, pencil_case 0%, yoga_mat 0%, camera 0%, phone 0%, textbook 0%, knitting_bag 0%, sketchbook 0%, spray_bottle 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 81% | 81% | 83% | 81% | 81% | 80% | 81% | 81% |
| most frequent | 81% | 81% | 82% | 81% | 83% | 80% | 78% | 81% |
| periodic | 81% | 81% | 83% | 81% | 81% | 80% | 81% | 81% |
| timetable | 79% | 81% | 83% | 81% | 83% | 79% | 78% | 81% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 81% | 100% / 81% | 100% / 83% | 100% / 81% | 100% / 81% | 100% / 80% | 100% / 81% | 100% / 81% |
| most frequent | 88% / 85% | 88% / 84% | 89% / 88% | 88% / 83% | 85% / 87% | 88% / 83% | 88% / 84% | 88% / 85% |
| periodic | 82% / 87% | 90% / 83% | 94% / 84% | 97% / 82% | 93% / 85% | 97% / 81% | 98% / 82% | 93% / 83% |
| timetable | 88% / 85% | 87% / 84% | 88% / 88% | 85% / 85% | 84% / 88% | 88% / 83% | 88% / 84% | 87% / 85% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 81% | 100% / 81% | 100% / 83% | 100% / 81% | 100% / 81% | 100% / 80% | 100% / 81% | 100% / 81% |
| most frequent | 63% / 90% | 75% / 89% | 75% / 92% | 73% / 88% | 70% / 90% | 75% / 86% | 73% / 91% | 72% / 90% |
| periodic | 30% / 91% | 45% / 85% | 48% / 82% | 62% / 80% | 65% / 84% | 68% / 83% | 73% / 77% | 56% / 82% |
| timetable | 59% / 90% | 71% / 89% | 70% / 91% | 70% / 88% | 66% / 90% | 72% / 86% | 68% / 91% | 68% / 89% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 81% | 100% / 81% | 100% / 83% | 100% / 81% | 100% / 81% | 100% / 80% | 100% / 81% | 100% / 81% |
| most frequent | 0% / 100% | 7% / 96% | 13% / 98% | 19% / 98% | 28% / 97% | 29% / 94% | 33% / 96% | 19% / 96% |
| periodic | 0% / - | 7% / 68% | 14% / 73% | 29% / 76% | 32% / 78% | 41% / 80% | 47% / 73% | 24% / 76% |
| timetable | 0% / 100% | 7% / 96% | 13% / 98% | 19% / 98% | 28% / 97% | 29% / 93% | 32% / 96% | 18% / 96% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| last seen | - | - | - | - | - | - | - | - | 81% (n=2240) | 0.184 |
| most frequent | - | 38% (n=90) | 59% (n=187) | 59% (n=158) | 67% (n=193) | 86% (n=413) | 88% (n=784) | 96% (n=360) | 98% (n=55) | 0.051 |
| periodic | - | 36% (n=59) | 60% (n=101) | 81% (n=367) | 88% (n=463) | 88% (n=397) | 86% (n=308) | 53% (n=104) | 81% (n=441) | 0.174 |
| timetable | - | 38% (n=126) | 60% (n=171) | 71% (n=223) | 70% (n=193) | 85% (n=383) | 88% (n=735) | 96% (n=354) | 98% (n=55) | 0.064 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| last seen | +2 | +2 | +1 (8) | 80 | 83 |
| most frequent | +2 | +2 | +2 (8) | 78 | 83 |
| periodic | +2 | +2 | +1 (8) | 80 | 83 |
| timetable | +4 | +2 | +2 (8) | 78 | 83 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2], 'hh_s1': [3, 4], 'hh_s2': [7], 'hh_s3': [5], 'hh_s4': [4, 5, 6, 7], 'hh_s5': [2], 'hh_s6': [], 'hh_s7': [5], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **78%** | 69% | **75%** | **91%** | 88% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 84% | **88%** | **94%** | **78%** | 88% | 78% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 59% | 72% | **75%** | **91%** | 78% | **66%** | [4, 5, 7] | [7] |
| hh_s3 | 81% | 84% | 78% | **84%** | **84%** | 97% | 81% | [4, 5] | [5] |
| hh_s4 | 81% | 84% | 91% | **78%** | **81%** | **72%** | **84%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **72%** | 91% | **81%** | **66%** | 84% | 91% | [2, 4, 5] | [2] |
| hh_s6 | 66% | 84% | 84% | **75%** | **81%** | 81% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 91% | 91% | **75%** | **66%** | 81% | 81% | [4, 5] | [5] |
| hh_s8 | **84%** | 84% | **88%** | **91%** | **91%** | 66% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 72% | 84% | **81%** | **78%** | **84%** | **69%** | 72% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **78%** | 69% | **75%** | **84%** | 88% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 84% | **88%** | **94%** | **78%** | 88% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 59% | 69% | **75%** | **81%** | 78% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 81% | 84% | 78% | **88%** | **91%** | 91% | 75% | [4, 5] | [5] |
| hh_s4 | 81% | 84% | 88% | **78%** | **84%** | **66%** | **75%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **72%** | 91% | **81%** | **78%** | 84% | 88% | [2, 4, 5] | [2] |
| hh_s6 | 66% | 84% | 84% | **75%** | **84%** | 84% | 88% | [4, 5] | [] |
| hh_s7 | 88% | 91% | 94% | **75%** | **78%** | 88% | 84% | [4, 5] | [5] |
| hh_s8 | **84%** | 84% | **88%** | **91%** | **88%** | 69% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 72% | 84% | **78%** | **75%** | **84%** | **66%** | 66% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **78%** | 69% | **75%** | **91%** | 88% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 84% | **88%** | **94%** | **78%** | 88% | 78% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 59% | 72% | **75%** | **91%** | 78% | **66%** | [4, 5, 7] | [7] |
| hh_s3 | 81% | 84% | 78% | **84%** | **84%** | 97% | 81% | [4, 5] | [5] |
| hh_s4 | 81% | 84% | 91% | **78%** | **81%** | **72%** | **84%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **72%** | 91% | **81%** | **66%** | 84% | 91% | [2, 4, 5] | [2] |
| hh_s6 | 66% | 84% | 84% | **75%** | **81%** | 81% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 91% | 91% | **75%** | **66%** | 81% | 81% | [4, 5] | [5] |
| hh_s8 | **84%** | 84% | **88%** | **91%** | **91%** | 66% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 72% | 84% | **81%** | **78%** | **84%** | **69%** | 72% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **75%** | 69% | **75%** | **84%** | 88% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 91% | **91%** | **94%** | **81%** | 88% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 78% | 62% | 72% | **78%** | **81%** | 78% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 81% | 84% | 78% | **84%** | **88%** | 91% | 78% | [4, 5] | [5] |
| hh_s4 | 78% | 84% | 88% | **78%** | **84%** | **66%** | **75%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 91% | **72%** | 91% | **81%** | **78%** | 84% | 88% | [2, 4, 5] | [2] |
| hh_s6 | 66% | 81% | 84% | **72%** | **84%** | 81% | 88% | [4, 5] | [] |
| hh_s7 | 88% | 91% | 94% | **78%** | **78%** | 84% | 84% | [4, 5] | [5] |
| hh_s8 | **81%** | 84% | **88%** | **91%** | **91%** | 69% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 72% | 84% | **78%** | **75%** | **84%** | **66%** | 66% | [3, 4, 5, 6] | [3, 4, 6] |
