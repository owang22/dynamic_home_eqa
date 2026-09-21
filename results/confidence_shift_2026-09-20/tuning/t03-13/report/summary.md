# t03-13

10 households, 4 agents, 8960 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5]; hh_s1 [3, 4, 5]; hh_s2 [4, 5, 7]; hh_s3 [4, 5]; hh_s4 [4, 5, 6, 7]; hh_s5 [2, 4, 5]; hh_s6 [4, 5]; hh_s7 [4, 5]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 224, hh_s1 224, hh_s2 224, hh_s3 224, hh_s4 224, hh_s5 224, hh_s6 224, hh_s7 224, hh_s8 224, hh_s9 224.

Object classes in the questions: glass 4%, bowl 3%, mug 3%, plate 3%, book 3%, towel 3%, umbrella 3%, jacket 2%, laptop 2%, shoes 2%, pen 2%, skincare 2%, water_bottle 2%, wallet 2%, remote 2%, kitchen_knife 2%, shopping_bag 2%, keys 2%, pan 2%, vacuum_cleaner 2%, headphones 2%, blanket 2%, razor 2%, charger 2%, snack_bowl 2%, spatula 2%, cutting_board 1%, notebook 1%, speaker 1%, toolbox 1%, laundry_basket 1%, tablet 1%, toiletry_bag 1%, dog_food_bag 1%, magazine 1%, scarf 1%, sunglasses 1%, board_game 1%, recipe_book 1%, dog_leash 1%, glasses 1%, backpack 1%, dog_bowl 1%, medication 1%, dog_toy 1%, gym_bag 1%, pot 1%, vitamins 1%, watering_can 1%, detergent 1%, duster 1%, hair_dryer 1%, hat 1%, lunchbox 1%, running_shoes 1%, gardening_gloves 1%, first_aid_kit 1%, ironing_board 1%, puzzle_box 1%, baking_tray 1%, mixing_bowl 1%, serving_dish 0%, mouse 0%, bike_lock 0%, guitar 0%, helmet 0%, meditation_cushion 0%, iron 0%, handbag 0%, pencil_case 0%, yoga_mat 0%, camera 0%, phone 0%, textbook 0%, knitting_bag 0%, sketchbook 0%, spray_bottle 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 84% | 88% | 86% | 85% | 86% | 87% | 84% | 86% |
| most frequent | 84% | 88% | 85% | 84% | 86% | 87% | 82% | 85% |
| periodic | 84% | 88% | 86% | 85% | 87% | 87% | 84% | 86% |
| timetable | 83% | 88% | 85% | 83% | 86% | 87% | 82% | 85% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 84% | 100% / 88% | 100% / 86% | 100% / 85% | 100% / 86% | 100% / 87% | 100% / 84% | 100% / 86% |
| most frequent | 93% / 86% | 96% / 91% | 91% / 89% | 94% / 87% | 95% / 87% | 92% / 90% | 90% / 88% | 93% / 88% |
| periodic | 92% / 86% | 97% / 89% | 96% / 87% | 98% / 86% | 98% / 88% | 97% / 88% | 98% / 85% | 96% / 87% |
| timetable | 92% / 86% | 96% / 91% | 91% / 90% | 92% / 87% | 92% / 89% | 91% / 90% | 88% / 88% | 92% / 89% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 84% | 100% / 88% | 100% / 86% | 100% / 85% | 100% / 86% | 100% / 87% | 100% / 84% | 100% / 86% |
| most frequent | 81% / 89% | 87% / 92% | 82% / 92% | 84% / 89% | 82% / 91% | 82% / 92% | 80% / 92% | 82% / 91% |
| periodic | 80% / 88% | 94% / 90% | 93% / 88% | 96% / 86% | 96% / 88% | 95% / 90% | 97% / 85% | 93% / 88% |
| timetable | 80% / 89% | 86% / 92% | 82% / 92% | 83% / 89% | 82% / 92% | 81% / 92% | 79% / 93% | 82% / 91% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 84% | 100% / 88% | 100% / 86% | 100% / 85% | 100% / 86% | 100% / 87% | 100% / 84% | 100% / 86% |
| most frequent | 24% / 96% | 51% / 95% | 62% / 97% | 59% / 94% | 61% / 95% | 59% / 96% | 59% / 96% | 54% / 96% |
| periodic | 20% / 94% | 39% / 92% | 48% / 84% | 63% / 83% | 63% / 86% | 71% / 88% | 72% / 84% | 54% / 86% |
| timetable | 22% / 96% | 48% / 95% | 57% / 97% | 57% / 94% | 57% / 95% | 57% / 96% | 55% / 96% | 51% / 95% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| last seen | - | - | - | - | - | - | - | - | 86% (n=2240) | 0.139 |
| most frequent | 0% (n=2) | 40% (n=57) | 48% (n=96) | 62% (n=107) | 71% (n=132) | 78% (n=210) | 84% (n=435) | 92% (n=500) | 98% (n=701) | 0.018 |
| periodic | 50% (n=2) | 53% (n=49) | 62% (n=29) | 65% (n=31) | 64% (n=50) | 83% (n=206) | 92% (n=666) | 89% (n=315) | 85% (n=892) | 0.092 |
| timetable | 0% (n=2) | 37% (n=98) | 48% (n=86) | 65% (n=99) | 73% (n=124) | 84% (n=289) | 84% (n=410) | 92% (n=473) | 98% (n=659) | 0.029 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| last seen | +2 | +1 | +1 (8) | 84 | 88 |
| most frequent | +2 | +1 | +2 (8) | 82 | 88 |
| periodic | +2 | +1 | +1 (8) | 84 | 88 |
| timetable | +2 | +2 | +3 (8) | 82 | 88 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2], 'hh_s1': [3, 4], 'hh_s2': [7], 'hh_s3': [5], 'hh_s4': [4, 5, 6, 7], 'hh_s5': [2], 'hh_s6': [], 'hh_s7': [5], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **78%** | **91%** | 75% | **75%** | **94%** | 94% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 84% | **94%** | **84%** | **81%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 84% | 84% | 69% | **81%** | **97%** | 84% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 91% | 88% | **84%** | **88%** | 94% | 84% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 94% | **75%** | **84%** | **88%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **84%** | 94% | **88%** | **75%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 66% | 88% | 88% | **88%** | **100%** | 88% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 91% | 97% | **94%** | **62%** | 88% | 88% | [4, 5] | [5] |
| hh_s8 | **84%** | 88% | **84%** | **91%** | **94%** | 78% | **78%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 84% | 84% | **81%** | **91%** | **88%** | **81%** | 78% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **78%** | **91%** | 72% | **69%** | **91%** | 84% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 88% | **94%** | **88%** | **78%** | 91% | 78% | [3, 4, 5] | [3, 4] |
| hh_s2 | 84% | 84% | 69% | **81%** | **88%** | 84% | **75%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 91% | 88% | **84%** | **88%** | 94% | 72% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 94% | **78%** | **84%** | **88%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 97% | **84%** | 91% | **84%** | **78%** | 91% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 66% | 88% | 84% | **88%** | **97%** | 88% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 91% | 97% | **88%** | **75%** | 94% | 88% | [4, 5] | [5] |
| hh_s8 | **81%** | 88% | **84%** | **91%** | **91%** | 81% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 84% | 84% | **81%** | **91%** | **88%** | **78%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **78%** | **91%** | 75% | **75%** | **94%** | 94% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 84% | **94%** | **84%** | **81%** | 91% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 84% | 84% | 69% | **81%** | **97%** | 84% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 91% | 88% | **88%** | **88%** | 94% | 84% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 94% | **75%** | **84%** | **88%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **84%** | 94% | **88%** | **75%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 66% | 88% | 88% | **88%** | **100%** | 88% | 97% | [4, 5] | [] |
| hh_s7 | 88% | 91% | 97% | **94%** | **66%** | 88% | 88% | [4, 5] | [5] |
| hh_s8 | **84%** | 88% | **84%** | **91%** | **94%** | 78% | **78%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 84% | 84% | **81%** | **91%** | **88%** | **81%** | 78% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **78%** | **88%** | 72% | **69%** | **88%** | 84% | 84% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 84% | 91% | **94%** | **91%** | **78%** | 91% | 78% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 84% | 75% | **78%** | **88%** | 84% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 91% | 84% | **81%** | **88%** | 94% | 75% | [4, 5] | [5] |
| hh_s4 | 88% | 97% | 94% | **78%** | **88%** | **88%** | **88%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **84%** | 88% | **81%** | **78%** | 91% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 66% | 84% | 84% | **84%** | **94%** | 84% | 91% | [4, 5] | [] |
| hh_s7 | 88% | 91% | 97% | **88%** | **78%** | 91% | 88% | [4, 5] | [5] |
| hh_s8 | **81%** | 88% | **84%** | **91%** | **94%** | 81% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 84% | 84% | **81%** | **91%** | **88%** | **78%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |
