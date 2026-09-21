# C_t03_sick15

10 households, 4 agents, 8960 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5, 7]; hh_s1 [1, 3, 4, 5, 7]; hh_s2 [4, 5, 7]; hh_s3 [2, 4, 5]; hh_s4 [3, 4, 5, 6, 7]; hh_s5 [1, 2, 4, 5]; hh_s6 [4, 5]; hh_s7 [2, 4, 5, 7]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 224, hh_s1 224, hh_s2 224, hh_s3 224, hh_s4 224, hh_s5 224, hh_s6 224, hh_s7 224, hh_s8 224, hh_s9 224.

Object classes in the questions: glass 5%, plate 4%, bowl 3%, towel 3%, book 3%, umbrella 3%, mug 3%, jacket 3%, skincare 2%, pen 2%, wallet 2%, water_bottle 2%, keys 2%, laptop 2%, shoes 2%, kitchen_knife 2%, shopping_bag 2%, pan 2%, remote 2%, speaker 2%, vacuum_cleaner 2%, spatula 2%, toiletry_bag 2%, laundry_basket 1%, notebook 1%, razor 1%, board_game 1%, dog_food_bag 1%, headphones 1%, blanket 1%, scarf 1%, snack_bowl 1%, tablet 1%, cutting_board 1%, medication 1%, magazine 1%, charger 1%, watering_can 1%, sunglasses 1%, glasses 1%, recipe_book 1%, duster 1%, vitamins 1%, dog_toy 1%, hair_dryer 1%, backpack 1%, ironing_board 1%, pot 1%, dog_leash 1%, hat 1%, gardening_gloves 1%, detergent 1%, dog_bowl 1%, first_aid_kit 1%, lunchbox 1%, serving_dish 1%, toolbox 1%, gym_bag 1%, running_shoes 1%, baking_tray 0%, meditation_cushion 0%, iron 0%, mouse 0%, camera 0%, controller 0%, mixing_bowl 0%, puzzle_box 0%, yoga_mat 0%, helmet 0%, phone 0%, bike_lock 0%, guitar 0%, pencil_case 0%, handbag 0%, spray_bottle 0%, textbook 0%, sketchbook 0%, headset 0%, knitting_bag 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (4/10 shift) | Thu (4/10 shift) | Fri (4/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (6/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 77% | 79% | 78% | 79% | 82% | 79% | 79% | 79% |
| most frequent | 77% | 79% | 78% | 80% | 82% | 76% | 79% | 79% |
| periodic | 77% | 79% | 78% | 79% | 82% | 79% | 79% | 79% |
| timetable | 77% | 78% | 78% | 80% | 82% | 75% | 79% | 78% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (4/10 shift) | Thu (4/10 shift) | Fri (4/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (6/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 77% | 100% / 79% | 100% / 78% | 100% / 79% | 100% / 82% | 100% / 79% | 100% / 79% | 100% / 79% |
| most frequent | 85% / 83% | 87% / 84% | 89% / 81% | 86% / 85% | 88% / 87% | 83% / 81% | 88% / 82% | 87% / 83% |
| periodic | 80% / 84% | 89% / 82% | 94% / 79% | 94% / 82% | 94% / 84% | 98% / 79% | 96% / 80% | 92% / 81% |
| timetable | 85% / 83% | 86% / 84% | 88% / 82% | 85% / 86% | 88% / 87% | 83% / 81% | 86% / 84% | 86% / 84% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (4/10 shift) | Thu (4/10 shift) | Fri (4/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (6/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 77% | 100% / 79% | 100% / 78% | 100% / 79% | 100% / 82% | 100% / 79% | 100% / 79% | 100% / 79% |
| most frequent | 62% / 86% | 71% / 89% | 70% / 85% | 71% / 89% | 74% / 89% | 71% / 85% | 72% / 87% | 70% / 87% |
| periodic | 31% / 87% | 38% / 86% | 52% / 78% | 59% / 80% | 65% / 83% | 70% / 75% | 70% / 77% | 55% / 80% |
| timetable | 58% / 86% | 64% / 89% | 67% / 85% | 66% / 90% | 71% / 89% | 68% / 85% | 69% / 87% | 66% / 87% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (4/10 shift) | Thu (4/10 shift) | Fri (4/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (6/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 77% | 100% / 79% | 100% / 78% | 100% / 79% | 100% / 82% | 100% / 79% | 100% / 79% | 100% / 79% |
| most frequent | 0% / 100% | 7% / 96% | 12% / 95% | 18% / 96% | 26% / 95% | 27% / 93% | 34% / 97% | 18% / 95% |
| periodic | 0% / - | 8% / 77% | 21% / 69% | 31% / 74% | 37% / 77% | 45% / 71% | 43% / 71% | 26% / 73% |
| timetable | 0% / 100% | 7% / 96% | 12% / 95% | 18% / 96% | 26% / 95% | 26% / 93% | 33% / 97% | 18% / 95% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| last seen | - | - | - | - | - | - | - | - | 79% (n=2240) | 0.205 |
| most frequent | - | 46% (n=105) | 51% (n=196) | 63% (n=156) | 71% (n=213) | 81% (n=415) | 86% (n=759) | 95% (n=348) | 98% (n=48) | 0.038 |
| periodic | - | 46% (n=70) | 54% (n=103) | 80% (n=360) | 86% (n=474) | 89% (n=363) | 83% (n=279) | 62% (n=113) | 76% (n=478) | 0.178 |
| timetable | - | 42% (n=132) | 50% (n=185) | 72% (n=222) | 71% (n=220) | 81% (n=375) | 87% (n=714) | 95% (n=344) | 98% (n=48) | 0.048 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| last seen | +1 | -2 | +5 (14) | 77 | 82 |
| most frequent | +1 | -2 | +3 (14) | 76 | 82 |
| periodic | +1 | -2 | +5 (14) | 77 | 82 |
| timetable | +1 | -3 | +3 (14) | 75 | 82 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2, 7], 'hh_s1': [1, 3, 4, 7], 'hh_s2': [7], 'hh_s3': [2, 5], 'hh_s4': [3, 4, 5, 6, 7], 'hh_s5': [1, 2], 'hh_s6': [], 'hh_s7': [2, 5, 7], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **69%** | **81%** | 75% | **72%** | **84%** | 84% | **94%** | [1, 2, 4, 5, 7] | [1, 2, 7] |
| hh_s1 | **84%** | 88% | **72%** | **88%** | **91%** | 91% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 4, 7] |
| hh_s2 | 84% | 59% | 88% | **69%** | **81%** | 69% | **75%** | [4, 5, 7] | [7] |
| hh_s3 | 75% | **88%** | 75% | **78%** | **78%** | 91% | 78% | [2, 4, 5] | [2, 5] |
| hh_s4 | 78% | 88% | **84%** | **84%** | **81%** | **78%** | **88%** | [3, 4, 5, 6, 7] | [3, 4, 5, 6, 7] |
| hh_s5 | **66%** | **66%** | 91% | **75%** | **66%** | 81% | 78% | [1, 2, 4, 5] | [1, 2] |
| hh_s6 | 69% | 78% | 69% | **88%** | **78%** | 75% | 94% | [4, 5] | [] |
| hh_s7 | 84% | **62%** | 75% | **78%** | **88%** | 78% | **53%** | [2, 4, 5, 7] | [2, 5, 7] |
| hh_s8 | **84%** | 94% | **72%** | **81%** | **91%** | 78% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 78% | 84% | **78%** | **81%** | **84%** | **62%** | 81% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **69%** | **81%** | 75% | **72%** | **84%** | 84% | **81%** | [1, 2, 4, 5, 7] | [1, 2, 7] |
| hh_s1 | **84%** | 88% | **72%** | **84%** | **88%** | 84% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 4, 7] |
| hh_s2 | 84% | 59% | 84% | **78%** | **81%** | 66% | **78%** | [4, 5, 7] | [7] |
| hh_s3 | 75% | **88%** | 75% | **84%** | **84%** | 84% | 78% | [2, 4, 5] | [2, 5] |
| hh_s4 | 78% | 88% | **84%** | **84%** | **91%** | **75%** | **84%** | [3, 4, 5, 6, 7] | [3, 4, 5, 6, 7] |
| hh_s5 | **66%** | **66%** | 97% | **75%** | **59%** | 84% | 78% | [1, 2, 4, 5] | [1, 2] |
| hh_s6 | 69% | 78% | 72% | **88%** | **81%** | 72% | 94% | [4, 5] | [] |
| hh_s7 | 84% | **62%** | 75% | **72%** | **84%** | 72% | **62%** | [2, 4, 5, 7] | [2, 5, 7] |
| hh_s8 | **84%** | 94% | **72%** | **81%** | **91%** | 72% | **78%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 78% | 84% | **78%** | **81%** | **78%** | **62%** | 84% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **69%** | **81%** | 75% | **72%** | **84%** | 84% | **94%** | [1, 2, 4, 5, 7] | [1, 2, 7] |
| hh_s1 | **84%** | 88% | **72%** | **88%** | **91%** | 91% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 4, 7] |
| hh_s2 | 84% | 59% | 88% | **69%** | **81%** | 69% | **75%** | [4, 5, 7] | [7] |
| hh_s3 | 75% | **88%** | 75% | **78%** | **78%** | 91% | 78% | [2, 4, 5] | [2, 5] |
| hh_s4 | 78% | 88% | **84%** | **84%** | **81%** | **78%** | **88%** | [3, 4, 5, 6, 7] | [3, 4, 5, 6, 7] |
| hh_s5 | **66%** | **66%** | 91% | **75%** | **66%** | 81% | 78% | [1, 2, 4, 5] | [1, 2] |
| hh_s6 | 69% | 78% | 69% | **88%** | **78%** | 75% | 94% | [4, 5] | [] |
| hh_s7 | 84% | **62%** | 75% | **78%** | **88%** | 78% | **53%** | [2, 4, 5, 7] | [2, 5, 7] |
| hh_s8 | **84%** | 94% | **72%** | **81%** | **91%** | 78% | **72%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 78% | 84% | **78%** | **81%** | **84%** | **62%** | 81% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **72%** | **81%** | 72% | **72%** | **84%** | 84% | **81%** | [1, 2, 4, 5, 7] | [1, 2, 7] |
| hh_s1 | **84%** | 91% | **75%** | **81%** | **88%** | 84% | **75%** | [1, 3, 4, 5, 7] | [1, 3, 4, 7] |
| hh_s2 | 78% | 62% | 78% | **78%** | **81%** | 66% | **78%** | [4, 5, 7] | [7] |
| hh_s3 | 75% | **84%** | 75% | **84%** | **84%** | 88% | 78% | [2, 4, 5] | [2, 5] |
| hh_s4 | 78% | 88% | **84%** | **84%** | **91%** | **75%** | **84%** | [3, 4, 5, 6, 7] | [3, 4, 5, 6, 7] |
| hh_s5 | **66%** | **66%** | 94% | **75%** | **59%** | 81% | 75% | [1, 2, 4, 5] | [1, 2] |
| hh_s6 | 69% | 75% | 72% | **88%** | **78%** | 72% | 94% | [4, 5] | [] |
| hh_s7 | 84% | **62%** | 75% | **72%** | **84%** | 69% | **62%** | [2, 4, 5, 7] | [2, 5, 7] |
| hh_s8 | **84%** | 91% | **72%** | **88%** | **91%** | 72% | **78%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 78% | 84% | **78%** | **81%** | **78%** | **62%** | 84% | [3, 4, 5, 6] | [3, 4, 6] |
