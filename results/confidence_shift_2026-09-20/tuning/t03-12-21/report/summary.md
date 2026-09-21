# t03-12-21

10 households, 4 agents, 8960 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5]; hh_s1 [3, 4, 5]; hh_s2 [4, 5, 7]; hh_s3 [4, 5]; hh_s4 [4, 5, 6, 7]; hh_s5 [2, 4, 5]; hh_s6 [4, 5]; hh_s7 [4, 5]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 224, hh_s1 224, hh_s2 224, hh_s3 224, hh_s4 224, hh_s5 224, hh_s6 224, hh_s7 224, hh_s8 224, hh_s9 224.

Object classes in the questions: glass 4%, bowl 3%, mug 3%, plate 3%, book 3%, towel 3%, umbrella 3%, jacket 2%, laptop 2%, shoes 2%, pen 2%, skincare 2%, water_bottle 2%, wallet 2%, remote 2%, kitchen_knife 2%, shopping_bag 2%, keys 2%, pan 2%, vacuum_cleaner 2%, headphones 2%, blanket 2%, razor 2%, charger 2%, snack_bowl 2%, spatula 2%, cutting_board 1%, notebook 1%, speaker 1%, toolbox 1%, laundry_basket 1%, tablet 1%, toiletry_bag 1%, dog_food_bag 1%, magazine 1%, scarf 1%, sunglasses 1%, board_game 1%, recipe_book 1%, dog_leash 1%, glasses 1%, backpack 1%, dog_bowl 1%, medication 1%, dog_toy 1%, gym_bag 1%, pot 1%, vitamins 1%, watering_can 1%, detergent 1%, duster 1%, hair_dryer 1%, hat 1%, lunchbox 1%, running_shoes 1%, gardening_gloves 1%, first_aid_kit 1%, ironing_board 1%, puzzle_box 1%, baking_tray 1%, mixing_bowl 1%, serving_dish 0%, mouse 0%, bike_lock 0%, guitar 0%, helmet 0%, meditation_cushion 0%, iron 0%, handbag 0%, pencil_case 0%, yoga_mat 0%, camera 0%, phone 0%, textbook 0%, knitting_bag 0%, sketchbook 0%, spray_bottle 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 86% | 89% | 89% | 87% | 89% | 91% | 87% | 88% |
| most frequent | 86% | 90% | 89% | 87% | 86% | 89% | 85% | 87% |
| periodic | 86% | 90% | 89% | 88% | 89% | 91% | 87% | 88% |
| timetable | 84% | 89% | 89% | 86% | 87% | 88% | 85% | 87% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 86% | 100% / 89% | 100% / 89% | 100% / 87% | 100% / 89% | 100% / 91% | 100% / 87% | 100% / 88% |
| most frequent | 95% / 88% | 96% / 91% | 94% / 91% | 94% / 89% | 96% / 88% | 95% / 91% | 93% / 90% | 95% / 90% |
| periodic | 93% / 88% | 98% / 91% | 99% / 90% | 98% / 88% | 99% / 89% | 100% / 91% | 100% / 87% | 98% / 89% |
| timetable | 94% / 88% | 95% / 91% | 93% / 92% | 93% / 89% | 93% / 89% | 94% / 92% | 92% / 90% | 93% / 90% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 86% | 100% / 89% | 100% / 89% | 100% / 87% | 100% / 89% | 100% / 91% | 100% / 87% | 100% / 88% |
| most frequent | 85% / 91% | 88% / 91% | 87% / 93% | 86% / 91% | 86% / 91% | 86% / 94% | 86% / 93% | 86% / 92% |
| periodic | 88% / 90% | 96% / 91% | 97% / 91% | 96% / 89% | 99% / 89% | 99% / 91% | 98% / 88% | 96% / 90% |
| timetable | 83% / 91% | 87% / 91% | 86% / 93% | 84% / 91% | 84% / 92% | 85% / 94% | 84% / 94% | 85% / 92% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 86% | 100% / 89% | 100% / 89% | 100% / 87% | 100% / 89% | 100% / 91% | 100% / 87% | 100% / 88% |
| most frequent | 48% / 94% | 68% / 94% | 73% / 96% | 64% / 96% | 66% / 95% | 68% / 96% | 66% / 95% | 65% / 95% |
| periodic | 40% / 92% | 65% / 92% | 73% / 92% | 79% / 88% | 83% / 90% | 90% / 91% | 87% / 90% | 74% / 91% |
| timetable | 45% / 94% | 65% / 94% | 69% / 96% | 62% / 96% | 62% / 95% | 66% / 96% | 63% / 95% | 62% / 95% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| last seen | - | - | - | - | - | - | - | - | 88% (n=2240) | 0.115 |
| most frequent | - | 48% (n=40) | 41% (n=75) | 64% (n=80) | 67% (n=114) | 83% (n=162) | 83% (n=315) | 92% (n=401) | 97% (n=1053) | 0.024 |
| periodic | - | 38% (n=24) | 65% (n=17) | 67% (n=24) | 56% (n=25) | 69% (n=62) | 90% (n=435) | 94% (n=458) | 89% (n=1195) | 0.066 |
| timetable | - | 38% (n=77) | 42% (n=69) | 65% (n=71) | 70% (n=125) | 88% (n=222) | 83% (n=292) | 91% (n=375) | 97% (n=1009) | 0.033 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| last seen | +4 | +2 | +2 (8) | 86 | 91 |
| most frequent | +3 | +2 | +4 (8) | 85 | 90 |
| periodic | +4 | +2 | +3 (8) | 86 | 91 |
| timetable | +4 | +3 | +4 (8) | 84 | 89 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2], 'hh_s1': [3, 4], 'hh_s2': [7], 'hh_s3': [5], 'hh_s4': [4, 5, 6, 7], 'hh_s5': [2], 'hh_s6': [], 'hh_s7': [5], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **81%** | **91%** | 75% | **84%** | **97%** | 94% | 91% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 97% | 84% | **97%** | **88%** | **81%** | 94% | 84% | [3, 4, 5] | [3, 4] |
| hh_s2 | 84% | 81% | 75% | **88%** | **100%** | 91% | **75%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 88% | 88% | **84%** | **94%** | 94% | 91% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 100% | **84%** | **88%** | **91%** | **91%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **88%** | 94% | **81%** | **81%** | 91% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 72% | 88% | 91% | **91%** | **97%** | 94% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 97% | 97% | **84%** | **72%** | 91% | 100% | [4, 5] | [5] |
| hh_s8 | **84%** | 94% | **88%** | **94%** | **94%** | 91% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 81% | 88% | **91%** | **94%** | **84%** | **78%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **81%** | **91%** | 75% | **84%** | **94%** | 81% | 91% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 97% | 91% | **97%** | **94%** | **78%** | 94% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 84% | 81% | 75% | **84%** | **94%** | 91% | **72%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 84% | 84% | **88%** | **91%** | 94% | 78% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 100% | **84%** | **88%** | **88%** | **91%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **88%** | 91% | **78%** | **81%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 72% | 88% | 88% | **88%** | **91%** | 94% | 97% | [4, 5] | [] |
| hh_s7 | 88% | 97% | 97% | **81%** | **72%** | 91% | 100% | [4, 5] | [5] |
| hh_s8 | **84%** | 94% | **91%** | **94%** | **91%** | 91% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 81% | 91% | **91%** | **94%** | **84%** | **78%** | 78% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **81%** | **91%** | 75% | **84%** | **97%** | 94% | 91% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 97% | 88% | **97%** | **88%** | **81%** | 94% | 84% | [3, 4, 5] | [3, 4] |
| hh_s2 | 84% | 81% | 75% | **88%** | **100%** | 91% | **75%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 88% | 88% | **88%** | **94%** | 94% | 91% | [4, 5] | [5] |
| hh_s4 | 91% | 97% | 100% | **84%** | **88%** | **91%** | **91%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **88%** | 94% | **81%** | **81%** | 91% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 72% | 88% | 91% | **91%** | **97%** | 94% | 97% | [4, 5] | [] |
| hh_s7 | 88% | 97% | 97% | **84%** | **72%** | 91% | 100% | [4, 5] | [5] |
| hh_s8 | **84%** | 94% | **88%** | **94%** | **94%** | 91% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 81% | 88% | **91%** | **94%** | **84%** | **78%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **81%** | **88%** | 75% | **84%** | **91%** | 81% | 91% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 97% | 91% | **97%** | **97%** | **78%** | 94% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 81% | 78% | **81%** | **94%** | 91% | **69%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 84% | 84% | **84%** | **91%** | 94% | 81% | [4, 5] | [5] |
| hh_s4 | 88% | 97% | 100% | **84%** | **91%** | **88%** | **91%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 91% | **88%** | 88% | **75%** | **81%** | 88% | 94% | [2, 4, 5] | [2] |
| hh_s6 | 72% | 84% | 88% | **84%** | **88%** | 91% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 97% | 97% | **81%** | **75%** | 88% | 100% | [4, 5] | [5] |
| hh_s8 | **81%** | 94% | **91%** | **94%** | **94%** | 91% | **69%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 81% | 91% | **91%** | **94%** | **84%** | **78%** | 78% | [3, 4, 5, 6] | [3, 4, 6] |
