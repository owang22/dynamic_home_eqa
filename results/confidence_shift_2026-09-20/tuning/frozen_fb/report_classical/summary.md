# Tuning set (seeds 0-9), classical agents

10 households, 5 agents, 22400 agent-question records. Shift days per household (weekend + major event days): hh_s0 [1, 2, 4, 5]; hh_s1 [3, 4, 5, 7]; hh_s2 [4, 5, 7]; hh_s3 [2, 4, 5, 7]; hh_s4 [3, 4, 5, 6, 7]; hh_s5 [1, 2, 3, 4, 5]; hh_s6 [4, 5]; hh_s7 [2, 4, 5]; hh_s8 [1, 3, 4, 5, 7]; hh_s9 [3, 4, 5, 6].

Questions per household per agent: hh_s0 448, hh_s1 448, hh_s2 448, hh_s3 448, hh_s4 448, hh_s5 448, hh_s6 448, hh_s7 448, hh_s8 448, hh_s9 448.

Object classes in the questions: glass 10%, towel 7%, mug 7%, plate 5%, water_bottle 4%, blanket 4%, dog_food_bag 4%, glasses 4%, vacuum_cleaner 3%, dog_bowl 3%, phone 3%, skincare 3%, shopping_bag 3%, bowl 2%, laundry_basket 2%, snack_bowl 2%, charger 2%, laptop 2%, watering_can 2%, tablet 2%, pen 1%, headphones 1%, razor 1%, remote 1%, gardening_gloves 1%, spatula 1%, detergent 1%, pan 1%, toiletry_bag 1%, toolbox 1%, book 1%, kitchen_knife 1%, ironing_board 1%, serving_dish 1%, cutting_board 1%, duster 1%, recipe_book 1%, pot 1%, dog_toy 1%, vitamins 1%, board_game 1%, iron 0%, mouse 0%, yoga_mat 0%, notebook 0%, hair_dryer 0%, guitar 0%, spray_bottle 0%, knitting_bag 0%, meditation_cushion 0%, magazine 0%, controller 0%, headset 0%, medication 0%, speaker 0%, textbook 0%, baking_tray 0%, mixing_bowl 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (3/10 shift) | Thu (4/10 shift) | Fri (5/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (5/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 57% | 53% | 53% | 46% | 53% | 56% | 53% | 53% |
| last seen | 55% | 52% | 54% | 47% | 53% | 52% | 52% | 52% |
| most frequent | 48% | 48% | 53% | 42% | 48% | 53% | 51% | 49% |
| periodic | 53% | 53% | 55% | 45% | 56% | 55% | 59% | 54% |
| timetable | 50% | 52% | 58% | 47% | 58% | 59% | 63% | 55% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (3/10 shift) | Thu (4/10 shift) | Fri (5/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (5/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 97% / 58% | 89% / 57% | 82% / 60% | 75% / 53% | 69% / 62% | 77% / 64% | 74% / 60% | 80% / 59% |
| last seen | 100% / 55% | 100% / 52% | 100% / 54% | 100% / 47% | 100% / 53% | 100% / 52% | 100% / 52% | 100% / 52% |
| most frequent | 30% / 66% | 53% / 72% | 57% / 68% | 52% / 56% | 53% / 61% | 57% / 64% | 54% / 71% | 51% / 65% |
| periodic | 25% / 62% | 67% / 52% | 76% / 55% | 84% / 44% | 85% / 55% | 86% / 53% | 91% / 58% | 73% / 53% |
| timetable | 20% / 65% | 34% / 68% | 34% / 70% | 38% / 56% | 35% / 70% | 38% / 74% | 40% / 75% | 34% / 68% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (3/10 shift) | Thu (4/10 shift) | Fri (5/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (5/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 82% / 62% | 66% / 62% | 59% / 66% | 50% / 62% | 45% / 72% | 54% / 68% | 54% / 68% | 58% / 65% |
| last seen | 100% / 55% | 100% / 52% | 100% / 54% | 100% / 47% | 100% / 53% | 100% / 52% | 100% / 52% | 100% / 52% |
| most frequent | 2% / 69% | 11% / 78% | 22% / 79% | 24% / 71% | 24% / 85% | 30% / 78% | 30% / 88% | 20% / 80% |
| periodic | 15% / 56% | 33% / 43% | 49% / 49% | 55% / 42% | 55% / 57% | 61% / 55% | 62% / 57% | 47% / 51% |
| timetable | 2% / 69% | 4% / 68% | 8% / 63% | 15% / 63% | 13% / 90% | 10% / 76% | 11% / 86% | 9% / 75% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (3/10 shift) | Thu (4/10 shift) | Fri (5/10 shift) | Sat (10/10 shift) | Sun (10/10 shift) | Mon (2/10 shift) | Tue (5/10 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 71% / 65% | 52% / 68% | 47% / 68% | 36% / 63% | 29% / 74% | 33% / 69% | 31% / 74% | 43% / 68% |
| last seen | 100% / 55% | 100% / 52% | 100% / 54% | 100% / 47% | 100% / 53% | 100% / 52% | 100% / 52% | 100% / 52% |
| most frequent | 2% / 67% | 1% / 25% | 2% / 62% | 3% / 47% | 1% / 100% | 2% / 46% | 2% / 67% | 2% / 59% |
| periodic | 10% / 63% | 18% / 48% | 26% / 59% | 32% / 53% | 32% / 63% | 42% / 63% | 41% / 67% | 29% / 60% |
| timetable | 2% / 67% | 1% / 25% | 2% / 62% | 3% / 47% | 1% / 100% | 2% / 46% | 2% / 64% | 2% / 58% |

## Coverage-matched selective accuracy (each agent answers its most confident 25 / 50 / 75% of the day's questions)

The fixed thresholds above compare different confidence scales; this compares agents at equal coverage.

| agent (coverage 25%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 54% | 77% | 72% | 67% | 76% | 69% | 77% | 72% |
| last seen | 52% | 42% | 49% | 50% | 55% | 56% | 54% | 50% |
| most frequent | 71% | 82% | 79% | 71% | 84% | 78% | 89% | 77% |
| periodic | 62% | 42% | 59% | 54% | 67% | 68% | 70% | 63% |
| timetable | 64% | 69% | 71% | 62% | 79% | 76% | 82% | 72% |

| agent (coverage 50%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 62% | 69% | 68% | 62% | 69% | 70% | 69% | 66% |
| last seen | 50% | 49% | 53% | 49% | 54% | 54% | 50% | 51% |
| most frequent | 64% | 73% | 71% | 57% | 63% | 68% | 72% | 66% |
| periodic | 65% | 46% | 49% | 43% | 58% | 59% | 63% | 50% |
| timetable | 64% | 62% | 67% | 53% | 68% | 70% | 72% | 66% |

| agent (coverage 75%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 64% | 60% | 62% | 53% | 60% | 64% | 60% | 60% |
| last seen | 54% | 52% | 54% | 48% | 55% | 55% | 52% | 53% |
| most frequent | 59% | 58% | 61% | 48% | 56% | 60% | 61% | 58% |
| periodic | 61% | 53% | 54% | 44% | 55% | 52% | 57% | 54% |
| timetable | 60% | 55% | 63% | 50% | 62% | 65% | 69% | 60% |

## Questions whose object moved since the robot's last round (54% of questions)

The robot's last full look is the patrol round before the question. 'still' questions are answered by recency almost by definition; the shift and the learning live in the 'moved' half. Cells: accuracy c=mean confidence.

| agent | Wed moved / still | Thu moved / still | Fri moved / still | Sat moved / still | Sun moved / still | Mon moved / still | Tue moved / still | moved all | still all |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 28% c85 / 92% c93 | 27% c73 / 82% c88 | 25% c69 / 82% c82 | 24% c64 / 75% c77 | 30% c60 / 80% c74 | 30% c64 / 84% c79 | 30% c63 / 82% c80 | 28% (n=2399, cov@0.7 47%, sel 29%) | 82% |
| last seen | 22% c98 / 93% c98 | 17% c98 / 93% c98 | 15% c98 / 94% c98 | 12% c98 / 91% c98 | 17% c98 / 94% c98 | 15% c98 / 93% c98 | 17% c98 / 96% c98 | 16% (n=2399, cov@0.7 100%, sel 16%) | 93% |
| most frequent | 11% c40 / 92% c47 | 11% c44 / 90% c59 | 18% c46 / 89% c61 | 14% c48 / 78% c60 | 26% c46 / 71% c62 | 29% c48 / 79% c65 | 27% c47 / 82% c65 | 19% (n=2399, cov@0.7 10%, sel 29%) | 83% |
| periodic | 16% c47 / 96% c41 | 20% c65 / 92% c58 | 20% c73 / 91% c66 | 14% c75 / 86% c71 | 23% c74 / 93% c73 | 23% c76 / 88% c78 | 32% c76 / 93% c80 | 21% (n=2399, cov@0.7 52%, sel 26%) | 91% |
| timetable | 17% c38 / 89% c43 | 24% c40 / 86% c47 | 33% c42 / 83% c47 | 28% c44 / 71% c51 | 46% c41 / 72% c50 | 51% c44 / 68% c49 | 55% c45 / 74% c50 | 36% (n=2399, cov@0.7 6%, sel 37%) | 78% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 20% (n=10) | 22% (n=540) | 41% (n=327) | 42% (n=481) | 42% (n=502) | 59% (n=410) | 56% (n=303) | 56% (n=206) | 70% (n=1701) | 0.213 |
| last seen | - | - | - | - | - | - | - | - | 52% (n=4480) | 0.460 |
| most frequent | 14% (n=37) | 25% (n=1309) | 44% (n=861) | 50% (n=714) | 62% (n=651) | 79% (n=507) | 88% (n=311) | 100% (n=1) | 58% (n=89) | 0.049 |
| periodic | 20% (n=44) | 47% (n=610) | 66% (n=537) | 62% (n=684) | 49% (n=490) | 39% (n=383) | 37% (n=451) | 49% (n=308) | 64% (n=973) | 0.258 |
| timetable | 10% (n=39) | 45% (n=2039) | 59% (n=874) | 62% (n=698) | 73% (n=423) | 79% (n=226) | 82% (n=92) | - | 58% (n=89) | 0.123 |

## Split by household kind (from the intro cards: any retired resident, or none)

Retired residents are home on weekdays too, so the weekend is not a routine shift for their household.

| household kind (n) | agent | Wed | Thu | Fri | Sat | Sun | Mon | Tue | weekday | weekend | drop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| working (7) | Perpetua* | 58% | 53% | 53% | 46% | 51% | 57% | 53% | 55% | 48% | +7 |
| working (7) | last seen | 56% | 52% | 54% | 46% | 52% | 52% | 53% | 53% | 49% | +4 |
| working (7) | most frequent | 48% | 47% | 54% | 41% | 46% | 52% | 49% | 50% | 43% | +7 |
| working (7) | periodic | 53% | 55% | 55% | 44% | 54% | 53% | 59% | 55% | 49% | +6 |
| working (7) | timetable | 50% | 51% | 58% | 47% | 56% | 58% | 61% | 56% | 52% | +4 |
| retired (3) | Perpetua* | 55% | 52% | 52% | 48% | 59% | 53% | 52% | 53% | 53% | -1 |
| retired (3) | last seen | 54% | 52% | 54% | 48% | 56% | 53% | 50% | 53% | 52% | +1 |
| retired (3) | most frequent | 48% | 49% | 52% | 45% | 51% | 55% | 56% | 52% | 48% | +4 |
| retired (3) | periodic | 53% | 51% | 54% | 48% | 60% | 57% | 59% | 55% | 54% | +1 |
| retired (3) | timetable | 51% | 55% | 57% | 47% | 61% | 61% | 68% | 58% | 54% | +4 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| Perpetua* | -5 | +6 | +2 (14) | 46 | 57 |
| last seen | -1 | +7 | +0 (14) | 47 | 55 |
| most frequent | +5 | +11 | -1 (14) | 42 | 53 |
| periodic | +2 | +10 | -0 (14) | 45 | 59 |
| timetable | +7 | +11 | -2 (14) | 47 | 63 |

Households with a major event on a scored day: 9/10; event days: {'hh_s0': [1, 2], 'hh_s1': [3, 4, 7], 'hh_s2': [7], 'hh_s3': [2, 5, 7], 'hh_s4': [3, 4, 5, 6, 7], 'hh_s5': [1, 2, 3], 'hh_s6': [], 'hh_s7': [2, 5], 'hh_s8': [1, 3, 7], 'hh_s9': [3, 4, 6]}

## Per household: Perpetua* (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **67%** | **62%** | 56% | **33%** | **42%** | 61% | 64% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 47% | 64% | **66%** | **52%** | **48%** | 48% | **55%** | [3, 4, 5, 7] | [3, 4, 7] |
| hh_s2 | 62% | 59% | 52% | **52%** | **55%** | 55% | **50%** | [4, 5, 7] | [7] |
| hh_s3 | 62% | **58%** | 58% | **47%** | **47%** | 53% | **52%** | [2, 4, 5, 7] | [2, 5, 7] |
| hh_s4 | 69% | 47% | **50%** | **38%** | **61%** | **47%** | **48%** | [3, 4, 5, 6, 7] | [3, 4, 5, 6, 7] |
| hh_s5 | **48%** | **42%** | **39%** | **39%** | **59%** | 62% | 53% | [1, 2, 3, 4, 5] | [1, 2, 3] |
| hh_s6 | 55% | 52% | 50% | **53%** | **47%** | 64% | 47% | [4, 5] | [] |
| hh_s7 | 59% | **45%** | 55% | **59%** | **53%** | 64% | 55% | [2, 4, 5] | [2, 5] |
| hh_s8 | **48%** | 55% | **47%** | **53%** | **61%** | 62% | **52%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 55% | 42% | **56%** | **39%** | **61%** | **42%** | 55% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **66%** | **62%** | 55% | **42%** | **55%** | 61% | 59% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 48% | 69% | **66%** | **56%** | **56%** | 41% | **47%** | [3, 4, 5, 7] | [3, 4, 7] |
| hh_s2 | 61% | 59% | 53% | **48%** | **58%** | 56% | **55%** | [4, 5, 7] | [7] |
| hh_s3 | 61% | **59%** | 62% | **48%** | **45%** | 50% | **59%** | [2, 4, 5, 7] | [2, 5, 7] |
| hh_s4 | 62% | 45% | **45%** | **39%** | **61%** | **38%** | **44%** | [3, 4, 5, 6, 7] | [3, 4, 5, 6, 7] |
| hh_s5 | **50%** | **45%** | **44%** | **42%** | **55%** | 52% | 59% | [1, 2, 3, 4, 5] | [1, 2, 3] |
| hh_s6 | 45% | 36% | 50% | **47%** | **44%** | 61% | 52% | [4, 5] | [] |
| hh_s7 | 56% | **45%** | 53% | **45%** | **52%** | 64% | 48% | [2, 4, 5] | [2, 5] |
| hh_s8 | **47%** | 50% | **47%** | **55%** | **56%** | 56% | **44%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 53% | 47% | **62%** | **42%** | **53%** | **47%** | 52% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **66%** | **66%** | 56% | **31%** | **50%** | 52% | 59% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 44% | 59% | **53%** | **45%** | **48%** | 50% | **41%** | [3, 4, 5, 7] | [3, 4, 7] |
| hh_s2 | 61% | 52% | 50% | **44%** | **48%** | 73% | **55%** | [4, 5, 7] | [7] |
| hh_s3 | 52% | **47%** | 64% | **39%** | **28%** | 39% | **56%** | [2, 4, 5, 7] | [2, 5, 7] |
| hh_s4 | 52% | 45% | **53%** | **41%** | **53%** | **38%** | **47%** | [3, 4, 5, 6, 7] | [3, 4, 5, 6, 7] |
| hh_s5 | **34%** | **34%** | **48%** | **47%** | **47%** | 59% | 56% | [1, 2, 3, 4, 5] | [1, 2, 3] |
| hh_s6 | 39% | 34% | 52% | **47%** | **39%** | 59% | 39% | [4, 5] | [] |
| hh_s7 | 52% | **44%** | 52% | **34%** | **56%** | 67% | 45% | [2, 4, 5] | [2, 5] |
| hh_s8 | **36%** | 50% | **47%** | **55%** | **62%** | 53% | **53%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 48% | 47% | **58%** | **38%** | **42%** | **39%** | 61% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **66%** | **61%** | 55% | **45%** | **55%** | 67% | 69% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 44% | 70% | **59%** | **45%** | **59%** | 44% | **56%** | [3, 4, 5, 7] | [3, 4, 7] |
| hh_s2 | 61% | 55% | 53% | **52%** | **62%** | 59% | **58%** | [4, 5, 7] | [7] |
| hh_s3 | 59% | **64%** | 67% | **45%** | **45%** | 55% | **67%** | [2, 4, 5, 7] | [2, 5, 7] |
| hh_s4 | 55% | 50% | **50%** | **39%** | **64%** | **42%** | **52%** | [3, 4, 5, 6, 7] | [3, 4, 5, 6, 7] |
| hh_s5 | **48%** | **42%** | **44%** | **42%** | **59%** | 55% | 61% | [1, 2, 3, 4, 5] | [1, 2, 3] |
| hh_s6 | 39% | 48% | 53% | **48%** | **41%** | 53% | 53% | [4, 5] | [] |
| hh_s7 | 59% | **47%** | 59% | **45%** | **58%** | 58% | 53% | [2, 4, 5] | [2, 5] |
| hh_s8 | **50%** | 53% | **48%** | **53%** | **62%** | 67% | **52%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 47% | 44% | **61%** | **39%** | **55%** | **45%** | 67% | [3, 4, 5, 6] | [3, 4, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s0 | **66%** | **72%** | 55% | **52%** | **61%** | 53% | 70% | [1, 2, 4, 5] | [1, 2] |
| hh_s1 | 45% | 59% | **58%** | **56%** | **62%** | 58% | **64%** | [3, 4, 5, 7] | [3, 4, 7] |
| hh_s2 | 61% | 61% | 59% | **53%** | **56%** | 70% | **62%** | [4, 5, 7] | [7] |
| hh_s3 | 53% | **56%** | 73% | **45%** | **50%** | 61% | **58%** | [2, 4, 5, 7] | [2, 5, 7] |
| hh_s4 | 52% | 56% | **62%** | **45%** | **55%** | **56%** | **61%** | [3, 4, 5, 6, 7] | [3, 4, 5, 6, 7] |
| hh_s5 | **38%** | **31%** | **52%** | **38%** | **62%** | 62% | 61% | [1, 2, 3, 4, 5] | [1, 2, 3] |
| hh_s6 | 47% | 42% | 52% | **55%** | **50%** | 61% | 56% | [4, 5] | [] |
| hh_s7 | 52% | **42%** | 55% | **39%** | **55%** | 56% | 56% | [2, 4, 5] | [2, 5] |
| hh_s8 | **41%** | 53% | **58%** | **52%** | **69%** | 59% | **66%** | [1, 3, 4, 5, 7] | [1, 3, 7] |
| hh_s9 | 52% | 50% | **55%** | **36%** | **59%** | **53%** | 77% | [3, 4, 5, 6] | [3, 4, 6] |
