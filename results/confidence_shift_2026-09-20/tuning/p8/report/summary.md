# p8

10 households, 4 agents, 8960 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5]; hh_s1 [3, 4, 5]; hh_s2 [4, 5, 7]; hh_s3 [4, 5]; hh_s4 [4, 5, 6, 7]; hh_s5 [2, 4, 5]; hh_s6 [4, 5]; hh_s7 [4, 5]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 224, hh_s1 224, hh_s2 224, hh_s3 224, hh_s4 224, hh_s5 224, hh_s6 224, hh_s7 224, hh_s8 224, hh_s9 224.

Object classes in the questions: glass 4%, bowl 3%, mug 3%, plate 3%, book 3%, towel 3%, umbrella 3%, jacket 2%, laptop 2%, shoes 2%, pen 2%, skincare 2%, water_bottle 2%, wallet 2%, remote 2%, kitchen_knife 2%, shopping_bag 2%, keys 2%, pan 2%, vacuum_cleaner 2%, headphones 2%, blanket 2%, razor 2%, charger 2%, snack_bowl 2%, spatula 2%, cutting_board 1%, notebook 1%, speaker 1%, toolbox 1%, laundry_basket 1%, tablet 1%, toiletry_bag 1%, dog_food_bag 1%, magazine 1%, scarf 1%, sunglasses 1%, board_game 1%, recipe_book 1%, dog_leash 1%, glasses 1%, backpack 1%, dog_bowl 1%, medication 1%, dog_toy 1%, gym_bag 1%, pot 1%, vitamins 1%, watering_can 1%, detergent 1%, duster 1%, hair_dryer 1%, hat 1%, lunchbox 1%, running_shoes 1%, gardening_gloves 1%, first_aid_kit 1%, ironing_board 1%, puzzle_box 1%, baking_tray 1%, mixing_bowl 1%, serving_dish 0%, mouse 0%, bike_lock 0%, guitar 0%, helmet 0%, meditation_cushion 0%, iron 0%, handbag 0%, pencil_case 0%, yoga_mat 0%, camera 0%, phone 0%, textbook 0%, knitting_bag 0%, sketchbook 0%, spray_bottle 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 87% | 88% | 89% | 87% | 89% | 86% | 85% | 87% |
| most frequent | 87% | 88% | 88% | 87% | 87% | 86% | 84% | 87% |
| periodic | 87% | 88% | 89% | 87% | 89% | 86% | 85% | 87% |
| timetable | 85% | 88% | 88% | 86% | 86% | 85% | 82% | 86% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 87% | 100% / 88% | 100% / 89% | 100% / 87% | 100% / 89% | 100% / 86% | 100% / 85% | 100% / 87% |
| most frequent | 98% / 88% | 98% / 89% | 96% / 91% | 97% / 87% | 95% / 89% | 97% / 88% | 92% / 88% | 96% / 89% |
| periodic | 94% / 88% | 97% / 89% | 99% / 89% | 100% / 87% | 100% / 89% | 100% / 86% | 99% / 85% | 99% / 88% |
| timetable | 96% / 88% | 97% / 90% | 95% / 90% | 95% / 87% | 93% / 90% | 96% / 88% | 90% / 88% | 95% / 89% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 87% | 100% / 88% | 100% / 89% | 100% / 87% | 100% / 89% | 100% / 86% | 100% / 85% | 100% / 87% |
| most frequent | 92% / 88% | 94% / 90% | 89% / 93% | 88% / 90% | 89% / 90% | 89% / 91% | 83% / 92% | 89% / 91% |
| periodic | 92% / 88% | 96% / 89% | 97% / 90% | 98% / 87% | 97% / 89% | 98% / 87% | 98% / 85% | 96% / 88% |
| timetable | 90% / 89% | 93% / 90% | 88% / 93% | 87% / 90% | 88% / 91% | 89% / 90% | 82% / 92% | 88% / 91% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 87% | 100% / 88% | 100% / 89% | 100% / 87% | 100% / 89% | 100% / 86% | 100% / 85% | 100% / 87% |
| most frequent | 57% / 93% | 77% / 92% | 75% / 96% | 70% / 91% | 71% / 93% | 69% / 93% | 67% / 96% | 69% / 93% |
| periodic | 48% / 95% | 71% / 91% | 80% / 91% | 86% / 87% | 91% / 89% | 92% / 87% | 89% / 86% | 80% / 89% |
| timetable | 53% / 93% | 73% / 91% | 71% / 95% | 66% / 92% | 67% / 93% | 66% / 93% | 64% / 96% | 66% / 93% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| last seen | - | - | - | - | - | - | - | - | 87% (n=2240) | 0.126 |
| most frequent | - | 29% (n=28) | 43% (n=61) | 55% (n=78) | 71% (n=77) | 74% (n=148) | 84% (n=294) | 86% (n=401) | 96% (n=1153) | 0.030 |
| periodic | - | 31% (n=13) | 75% (n=20) | 68% (n=19) | 89% (n=28) | 67% (n=64) | 85% (n=310) | 92% (n=527) | 87% (n=1259) | 0.074 |
| timetable | - | 25% (n=65) | 41% (n=54) | 53% (n=73) | 73% (n=75) | 73% (n=134) | 86% (n=365) | 87% (n=405) | 96% (n=1069) | 0.028 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| last seen | +3 | +3 | -0 (8) | 85 | 89 |
| most frequent | +2 | +2 | +1 (8) | 84 | 88 |
| periodic | +3 | +3 | -0 (8) | 85 | 89 |
| timetable | +2 | +2 | +2 (8) | 82 | 88 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2], 'hh_s1': [3, 4], 'hh_s2': [7], 'hh_s3': [5], 'hh_s4': [4, 5, 6, 7], 'hh_s5': [2], 'hh_s6': [], 'hh_s7': [5], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **84%** | 81% | **81%** | **97%** | 94% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 84% | **91%** | **84%** | **81%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 88% | 84% | 81% | **88%** | **91%** | 75% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 88% | 97% | 88% | **97%** | **84%** | 94% | 88% | [4, 5] | [5] |
| hh_s4 | 91% | 91% | 94% | **72%** | **91%** | **88%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **81%** | 94% | **88%** | **91%** | 91% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 78% | 88% | 97% | **91%** | **94%** | 84% | 94% | [4, 5] | [] |
| hh_s7 | 94% | 97% | 94% | **88%** | **78%** | 81% | 88% | [4, 5] | [5] |
| hh_s8 | **91%** | 88% | **88%** | **97%** | **94%** | 84% | **84%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 84% | 81% | **88%** | **81%** | **91%** | **78%** | 78% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **84%** | 78% | **78%** | **97%** | 91% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 88% | **91%** | **84%** | **78%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 88% | 84% | 78% | **88%** | **84%** | 75% | **72%** | [4, 5, 7] | [7] |
| hh_s3 | 88% | 97% | 88% | **94%** | **84%** | 97% | 84% | [4, 5] | [5] |
| hh_s4 | 91% | 91% | 94% | **75%** | **91%** | **88%** | **84%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **81%** | 94% | **91%** | **88%** | 91% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 78% | 88% | 97% | **91%** | **94%** | 84% | 94% | [4, 5] | [] |
| hh_s7 | 94% | 97% | 91% | **88%** | **78%** | 81% | 84% | [4, 5] | [5] |
| hh_s8 | **91%** | 88% | **84%** | **97%** | **91%** | 84% | **81%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 84% | 81% | **88%** | **81%** | **88%** | **78%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **84%** | 81% | **81%** | **97%** | 94% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 84% | **91%** | **84%** | **81%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 88% | 84% | 81% | **88%** | **91%** | 75% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 88% | 97% | 88% | **97%** | **84%** | 94% | 88% | [4, 5] | [5] |
| hh_s4 | 91% | 91% | 94% | **72%** | **91%** | **88%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **81%** | 94% | **88%** | **91%** | 91% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 78% | 88% | 97% | **91%** | **94%** | 84% | 97% | [4, 5] | [] |
| hh_s7 | 94% | 97% | 94% | **88%** | **78%** | 81% | 88% | [4, 5] | [5] |
| hh_s8 | **91%** | 88% | **88%** | **97%** | **94%** | 84% | **84%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 84% | 81% | **88%** | **81%** | **91%** | **78%** | 78% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **81%** | 78% | **78%** | **91%** | 91% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 91% | **91%** | **88%** | **78%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 84% | 84% | 78% | **84%** | **81%** | 75% | **66%** | [4, 5, 7] | [7] |
| hh_s3 | 88% | 97% | 84% | **91%** | **81%** | 97% | 84% | [4, 5] | [5] |
| hh_s4 | 88% | 91% | 94% | **75%** | **91%** | **88%** | **84%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 91% | **81%** | 91% | **88%** | **84%** | 91% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 78% | 84% | 97% | **91%** | **91%** | 81% | 91% | [4, 5] | [] |
| hh_s7 | 88% | 97% | 91% | **88%** | **78%** | 78% | 84% | [4, 5] | [5] |
| hh_s8 | **91%** | 88% | **84%** | **97%** | **94%** | 84% | **78%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 84% | 81% | **88%** | **81%** | **88%** | **78%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |
