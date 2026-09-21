# act_p2

10 households, 4 agents, 8960 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5]; hh_s1 [3, 4, 5]; hh_s2 [4, 5, 7]; hh_s3 [4, 5]; hh_s4 [4, 5, 6, 7]; hh_s5 [2, 4, 5]; hh_s6 [4, 5]; hh_s7 [4, 5]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 224, hh_s1 224, hh_s2 224, hh_s3 224, hh_s4 224, hh_s5 224, hh_s6 224, hh_s7 224, hh_s8 224, hh_s9 224.

Object classes in the questions: glass 9%, towel 8%, mug 6%, plate 5%, glasses 4%, water_bottle 4%, vacuum_cleaner 4%, blanket 4%, dog_bowl 3%, dog_food_bag 3%, phone 3%, snack_bowl 3%, skincare 3%, bowl 3%, charger 2%, shopping_bag 2%, watering_can 2%, laptop 2%, duster 2%, laundry_basket 2%, pen 2%, tablet 1%, gardening_gloves 1%, toiletry_bag 1%, cutting_board 1%, headphones 1%, razor 1%, detergent 1%, ironing_board 1%, serving_dish 1%, toolbox 1%, remote 1%, spatula 1%, kitchen_knife 1%, book 1%, iron 1%, pan 1%, dog_toy 1%, hair_dryer 1%, pot 1%, recipe_book 1%, mouse 1%, board_game 1%, vitamins 0%, guitar 0%, spray_bottle 0%, meditation_cushion 0%, yoga_mat 0%, baking_tray 0%, magazine 0%, notebook 0%, speaker 0%, headset 0%, mixing_bowl 0%, textbook 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 67% | 61% | 63% | 52% | 56% | 58% | 57% | 59% |
| most frequent | 67% | 61% | 63% | 52% | 56% | 58% | 57% | 59% |
| periodic | 67% | 61% | 63% | 52% | 56% | 58% | 57% | 59% |
| timetable | 67% | 61% | 63% | 52% | 56% | 58% | 57% | 59% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 67% | 100% / 61% | 100% / 63% | 100% / 52% | 100% / 56% | 100% / 58% | 100% / 57% | 100% / 59% |
| most frequent | 100% / 67% | 100% / 61% | 98% / 64% | 98% / 53% | 99% / 56% | 99% / 59% | 98% / 57% | 99% / 60% |
| periodic | 99% / 67% | 100% / 61% | 100% / 63% | 100% / 52% | 100% / 56% | 100% / 58% | 100% / 57% | 100% / 59% |
| timetable | 100% / 67% | 99% / 61% | 99% / 64% | 99% / 52% | 99% / 57% | 99% / 58% | 99% / 58% | 99% / 60% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 67% | 100% / 61% | 100% / 63% | 100% / 52% | 100% / 56% | 100% / 58% | 100% / 57% | 100% / 59% |
| most frequent | 96% / 67% | 97% / 62% | 96% / 64% | 93% / 53% | 94% / 58% | 94% / 60% | 95% / 58% | 95% / 60% |
| periodic | 98% / 67% | 99% / 61% | 99% / 64% | 99% / 52% | 100% / 56% | 100% / 58% | 99% / 58% | 99% / 59% |
| timetable | 98% / 67% | 99% / 61% | 98% / 64% | 97% / 53% | 98% / 57% | 98% / 60% | 97% / 59% | 98% / 60% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/10 shift) | Thu (2/10 shift) | Fri (3/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (3/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| last seen | 100% / 67% | 100% / 61% | 100% / 63% | 100% / 52% | 100% / 56% | 100% / 58% | 100% / 57% | 100% / 59% |
| most frequent | 89% / 67% | 89% / 62% | 89% / 65% | 82% / 53% | 81% / 60% | 79% / 63% | 76% / 63% | 84% / 62% |
| periodic | 98% / 67% | 99% / 62% | 98% / 63% | 99% / 52% | 100% / 56% | 97% / 59% | 99% / 58% | 98% / 60% |
| timetable | 88% / 68% | 93% / 62% | 90% / 66% | 86% / 55% | 83% / 59% | 81% / 64% | 83% / 63% | 86% / 62% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| last seen | - | - | - | - | - | - | - | - | 59% (n=2240) | 0.405 |
| most frequent | - | 40% (n=5) | 25% (n=20) | 41% (n=39) | 41% (n=46) | 44% (n=73) | 49% (n=181) | 43% (n=203) | 64% (n=1673) | 0.353 |
| periodic | - | - | 100% (n=4) | 33% (n=3) | 29% (n=7) | 71% (n=7) | 19% (n=16) | 41% (n=22) | 60% (n=2181) | 0.399 |
| timetable | - | 25% (n=12) | 25% (n=4) | 43% (n=14) | 6% (n=17) | 37% (n=65) | 45% (n=192) | 52% (n=393) | 65% (n=1543) | 0.351 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| last seen | -4 | +12 | +3 (8) | 52 | 67 |
| most frequent | -4 | +11 | +3 (8) | 52 | 67 |
| periodic | -4 | +12 | +3 (8) | 52 | 67 |
| timetable | -4 | +12 | +3 (8) | 52 | 67 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2], 'hh_s1': [3, 4], 'hh_s2': [7], 'hh_s3': [5], 'hh_s4': [4, 5, 6, 7], 'hh_s5': [2], 'hh_s6': [], 'hh_s7': [5], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **62%** | **75%** | 56% | **56%** | **78%** | 69% | 72% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 62% | 81% | **50%** | **31%** | **59%** | 53% | 59% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 66% | 62% | **72%** | **66%** | 66% | **50%** | [4, 5, 7] | [7] |
| hh_s3 | 75% | 84% | 69% | **47%** | **59%** | 41% | 81% | [4, 5] | [5] |
| hh_s4 | 62% | 41% | 66% | **44%** | **44%** | **38%** | **50%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 69% | **56%** | 72% | **50%** | **47%** | 50% | 44% | [2, 4, 5] | [2] |
| hh_s6 | 62% | 41% | 59% | **69%** | **41%** | 66% | 62% | [4, 5] | [] |
| hh_s7 | 75% | 66% | 72% | **34%** | **47%** | 81% | 44% | [4, 5] | [5] |
| hh_s8 | **62%** | 50% | **53%** | **62%** | **53%** | 72% | **56%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 59% | 50% | **75%** | **53%** | **69%** | **50%** | 56% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **62%** | **75%** | 56% | **56%** | **78%** | 69% | 72% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 62% | 81% | **50%** | **31%** | **59%** | 53% | 56% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 66% | 62% | **72%** | **66%** | 66% | **50%** | [4, 5, 7] | [7] |
| hh_s3 | 75% | 84% | 69% | **47%** | **59%** | 38% | 78% | [4, 5] | [5] |
| hh_s4 | 62% | 41% | 66% | **44%** | **44%** | **38%** | **50%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 69% | **56%** | 72% | **50%** | **47%** | 50% | 44% | [2, 4, 5] | [2] |
| hh_s6 | 62% | 44% | 59% | **66%** | **41%** | 66% | 62% | [4, 5] | [] |
| hh_s7 | 75% | 66% | 69% | **38%** | **47%** | 81% | 44% | [4, 5] | [5] |
| hh_s8 | **62%** | 50% | **53%** | **62%** | **53%** | 72% | **56%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 59% | 50% | **75%** | **53%** | **69%** | **50%** | 56% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **62%** | **75%** | 56% | **56%** | **78%** | 69% | 72% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 62% | 81% | **50%** | **31%** | **59%** | 53% | 59% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 66% | 62% | **72%** | **66%** | 66% | **50%** | [4, 5, 7] | [7] |
| hh_s3 | 75% | 84% | 69% | **47%** | **59%** | 41% | 81% | [4, 5] | [5] |
| hh_s4 | 62% | 41% | 66% | **44%** | **44%** | **38%** | **50%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 69% | **56%** | 72% | **50%** | **47%** | 50% | 44% | [2, 4, 5] | [2] |
| hh_s6 | 62% | 41% | 59% | **69%** | **41%** | 66% | 62% | [4, 5] | [] |
| hh_s7 | 75% | 66% | 72% | **34%** | **47%** | 81% | 44% | [4, 5] | [5] |
| hh_s8 | **62%** | 50% | **53%** | **62%** | **53%** | 72% | **56%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 59% | 50% | **75%** | **53%** | **69%** | **50%** | 56% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **62%** | **75%** | 56% | **56%** | **78%** | 69% | 72% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 62% | 81% | **50%** | **31%** | **59%** | 53% | 56% | [3, 4, 5] | [3, 4] |
| hh_s2 | 81% | 66% | 62% | **72%** | **66%** | 66% | **50%** | [4, 5, 7] | [7] |
| hh_s3 | 75% | 84% | 69% | **47%** | **59%** | 41% | 81% | [4, 5] | [5] |
| hh_s4 | 62% | 41% | 66% | **44%** | **44%** | **38%** | **50%** | [4, 5, 6, 7] | [4, 5, 6, 7] |
| hh_s5 | 69% | **56%** | 72% | **50%** | **47%** | 50% | 44% | [2, 4, 5] | [2] |
| hh_s6 | 62% | 41% | 59% | **66%** | **41%** | 66% | 62% | [4, 5] | [] |
| hh_s7 | 75% | 66% | 72% | **38%** | **47%** | 81% | 44% | [4, 5] | [5] |
| hh_s8 | **62%** | 50% | **53%** | **62%** | **53%** | 72% | **56%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 59% | 50% | **75%** | **53%** | **69%** | **50%** | 56% | [3, 4, 5, 6] | [3, 4, 6] |
