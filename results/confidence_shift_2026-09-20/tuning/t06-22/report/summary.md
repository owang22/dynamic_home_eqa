# t06-22

10 households, 4 agents, 8960 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5]; hh_s1 [3, 4, 5]; hh_s2 [4, 5, 7]; hh_s3 [4, 5]; hh_s4 [4, 5, 6, 7]; hh_s5 [2, 4, 5]; hh_s6 [4, 5]; hh_s7 [4, 5]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 224, hh_s1 224, hh_s2 224, hh_s3 224, hh_s4 224, hh_s5 224, hh_s6 224, hh_s7 224, hh_s8 224, hh_s9 224.

Object classes in the questions: glass 4%, bowl 3%, mug 3%, plate 3%, book 3%, towel 3%, umbrella 3%, jacket 2%, laptop 2%, shoes 2%, pen 2%, skincare 2%, water_bottle 2%, wallet 2%, remote 2%, kitchen_knife 2%, shopping_bag 2%, keys 2%, pan 2%, vacuum_cleaner 2%, headphones 2%, blanket 2%, razor 2%, charger 2%, snack_bowl 2%, spatula 2%, cutting_board 1%, notebook 1%, speaker 1%, toolbox 1%, laundry_basket 1%, tablet 1%, toiletry_bag 1%, dog_food_bag 1%, magazine 1%, scarf 1%, sunglasses 1%, board_game 1%, recipe_book 1%, dog_leash 1%, glasses 1%, backpack 1%, dog_bowl 1%, medication 1%, dog_toy 1%, gym_bag 1%, pot 1%, vitamins 1%, watering_can 1%, detergent 1%, duster 1%, hair_dryer 1%, hat 1%, lunchbox 1%, running_shoes 1%, gardening_gloves 1%, first_aid_kit 1%, ironing_board 1%, puzzle_box 1%, baking_tray 1%, mixing_bowl 1%, serving_dish 0%, mouse 0%, bike_lock 0%, guitar 0%, helmet 0%, meditation_cushion 0%, iron 0%, handbag 0%, pencil_case 0%, yoga_mat 0%, camera 0%, phone 0%, textbook 0%, knitting_bag 0%, sketchbook 0%, spray_bottle 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 82% | 82% | 85% | 82% | 83% | 83% | 82% | 83% |
| most frequent | 82% | 81% | 85% | 82% | 84% | 82% | 81% | 82% |
| periodic | 82% | 82% | 85% | 82% | 83% | 83% | 82% | 83% |
| timetable | 81% | 81% | 86% | 82% | 84% | 82% | 81% | 82% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 82% | 100% / 82% | 100% / 85% | 100% / 82% | 100% / 83% | 100% / 83% | 100% / 82% | 100% / 83% |
| most frequent | 95% / 84% | 98% / 82% | 94% / 88% | 94% / 84% | 92% / 87% | 91% / 85% | 92% / 86% | 94% / 85% |
| periodic | 96% / 83% | 99% / 82% | 100% / 85% | 100% / 82% | 100% / 83% | 99% / 83% | 99% / 82% | 99% / 83% |
| timetable | 95% / 83% | 97% / 82% | 93% / 88% | 92% / 85% | 91% / 88% | 90% / 85% | 90% / 86% | 93% / 85% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 82% | 100% / 82% | 100% / 85% | 100% / 82% | 100% / 83% | 100% / 83% | 100% / 82% | 100% / 83% |
| most frequent | 86% / 87% | 83% / 87% | 86% / 90% | 81% / 87% | 79% / 89% | 82% / 87% | 78% / 92% | 82% / 88% |
| periodic | 78% / 89% | 88% / 84% | 96% / 85% | 96% / 83% | 94% / 85% | 95% / 84% | 96% / 83% | 92% / 85% |
| timetable | 81% / 87% | 79% / 87% | 81% / 90% | 77% / 88% | 75% / 90% | 78% / 87% | 73% / 92% | 78% / 88% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 82% | 100% / 82% | 100% / 85% | 100% / 82% | 100% / 83% | 100% / 83% | 100% / 82% | 100% / 83% |
| most frequent | 30% / 93% | 44% / 94% | 57% / 94% | 58% / 91% | 59% / 93% | 61% / 90% | 58% / 95% | 53% / 93% |
| periodic | 26% / 94% | 43% / 82% | 44% / 84% | 55% / 84% | 62% / 86% | 63% / 86% | 66% / 81% | 51% / 84% |
| timetable | 30% / 93% | 44% / 94% | 55% / 94% | 57% / 92% | 57% / 93% | 59% / 90% | 56% / 94% | 51% / 93% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| last seen | - | - | - | - | - | - | - | - | 83% (n=2240) | 0.170 |
| most frequent | - | 42% (n=36) | 48% (n=103) | 58% (n=124) | 62% (n=138) | 73% (n=187) | 84% (n=472) | 90% (n=567) | 96% (n=613) | 0.024 |
| periodic | - | 70% (n=10) | 58% (n=12) | 39% (n=51) | 68% (n=108) | 83% (n=421) | 86% (n=487) | 79% (n=321) | 87% (n=830) | 0.086 |
| timetable | - | 37% (n=75) | 48% (n=91) | 68% (n=151) | 72% (n=183) | 74% (n=170) | 82% (n=427) | 90% (n=534) | 96% (n=609) | 0.037 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| last seen | +3 | +3 | +2 (8) | 82 | 85 |
| most frequent | +3 | +4 | +2 (8) | 81 | 85 |
| periodic | +3 | +3 | +2 (8) | 82 | 85 |
| timetable | +5 | +4 | +4 (8) | 81 | 86 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2], 'hh_s1': [3, 4], 'hh_s2': [7], 'hh_s3': [5], 'hh_s4': [4, 5, 6, 7], 'hh_s5': [2], 'hh_s6': [], 'hh_s7': [5], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **78%** | 69% | **75%** | **94%** | 88% | 91% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 91% | 84% | **91%** | **94%** | **78%** | 88% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 59% | 72% | **78%** | **94%** | 78% | **66%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 91% | 81% | **84%** | **84%** | 100% | 84% | [4, 5] | [5] |
| hh_s4 | 81% | 84% | 91% | **78%** | **81%** | **72%** | **84%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **72%** | 91% | **81%** | **69%** | 88% | 84% | [2, 4, 5] | [2] |
| hh_s6 | 72% | 84% | 88% | **78%** | **81%** | 84% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 94% | 97% | **75%** | **72%** | 81% | 88% | [4, 5] | [5] |
| hh_s8 | **84%** | 84% | **88%** | **91%** | **91%** | 78% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 72% | 88% | **84%** | **81%** | **84%** | **72%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **78%** | 66% | **75%** | **91%** | 88% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 91% | 81% | **94%** | **94%** | **78%** | 88% | 84% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 59% | 75% | **78%** | **88%** | 75% | **66%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 88% | 81% | **84%** | **94%** | 94% | 84% | [4, 5] | [5] |
| hh_s4 | 81% | 81% | 91% | **78%** | **84%** | **69%** | **72%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 94% | **72%** | 91% | **81%** | **75%** | 91% | 88% | [2, 4, 5] | [2] |
| hh_s6 | 72% | 84% | 88% | **78%** | **84%** | 84% | 97% | [4, 5] | [] |
| hh_s7 | 88% | 94% | 97% | **75%** | **72%** | 84% | 91% | [4, 5] | [5] |
| hh_s8 | **84%** | 84% | **88%** | **91%** | **91%** | 81% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 72% | 88% | **84%** | **81%** | **84%** | **69%** | 69% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **78%** | 69% | **75%** | **94%** | 88% | 91% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 91% | 84% | **91%** | **94%** | **78%** | 88% | 81% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 59% | 72% | **78%** | **94%** | 78% | **66%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 91% | 81% | **84%** | **84%** | 100% | 84% | [4, 5] | [5] |
| hh_s4 | 81% | 84% | 91% | **78%** | **81%** | **72%** | **84%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 91% | **72%** | 91% | **81%** | **69%** | 88% | 84% | [2, 4, 5] | [2] |
| hh_s6 | 72% | 84% | 88% | **78%** | **81%** | 84% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 94% | 97% | **75%** | **72%** | 81% | 88% | [4, 5] | [5] |
| hh_s8 | **84%** | 84% | **88%** | **91%** | **91%** | 78% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 72% | 88% | **84%** | **81%** | **84%** | **72%** | 75% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **75%** | **75%** | 66% | **75%** | **91%** | 88% | 88% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 91% | 88% | **94%** | **94%** | **81%** | 88% | 84% | [3, 4, 5] | [3, 4] |
| hh_s2 | 78% | 62% | 78% | **81%** | **88%** | 75% | **66%** | [4, 5, 7] | [7] |
| hh_s3 | 84% | 88% | 81% | **81%** | **91%** | 94% | 88% | [4, 5] | [5] |
| hh_s4 | 78% | 81% | 91% | **78%** | **84%** | **69%** | **72%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 91% | **72%** | 91% | **81%** | **75%** | 91% | 88% | [2, 4, 5] | [2] |
| hh_s6 | 72% | 81% | 88% | **75%** | **84%** | 81% | 94% | [4, 5] | [] |
| hh_s7 | 88% | 94% | 97% | **78%** | **72%** | 81% | 91% | [4, 5] | [5] |
| hh_s8 | **81%** | 84% | **88%** | **91%** | **94%** | 81% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 72% | 88% | **84%** | **81%** | **84%** | **69%** | 69% | [3, 4, 5, 6] | [3, 4, 6] |
