# hh_s10,11,13 all agents (agreement)

3 households, 9 agents, 12096 agent-question records. Shift days per household (weekend + major event days): hh_s10 [4, 5]; hh_s11 [3, 4, 5, 7]; hh_s13 [1, 2, 4, 5].

Questions per household per agent: hh_s10 448, hh_s11 448, hh_s13 448.

Object classes in the questions: glass 14%, towel 9%, mug 7%, plate 6%, vacuum_cleaner 5%, snack_bowl 5%, blanket 4%, skincare 4%, bowl 3%, laundry_basket 3%, duster 3%, phone 3%, shopping_bag 3%, detergent 2%, dog_bowl 2%, razor 2%, toiletry_bag 2%, dog_food_bag 2%, tablet 2%, water_bottle 2%, watering_can 2%, pot 1%, ironing_board 1%, kitchen_knife 1%, remote 1%, glasses 1%, cutting_board 1%, spatula 1%, charger 1%, pan 1%, recipe_book 1%, serving_dish 1%, book 1%, journal 1%, magazine 0%, pen 0%, vitamins 0%, board_game 0%, puzzle_box 0%, dog_toy 0%, guitar 0%, laptop 0%, yoga_mat 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (1/3 shift) | Thu (1/3 shift) | Fri (1/3 shift) | Sat (3/3 shift) | Sun (3/3 shift) | Mon (0/3 shift) | Tue (1/3 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 64% | 54% | 56% | 56% | 57% | 49% | 50% | 55% |
| last seen | 64% | 55% | 59% | 58% | 58% | 54% | 56% | 58% |
| llm_longleaf/not_told/look_off | 52% | 52% | 45% | 50% | 52% | 42% | 46% | 48% |
| llm_longleaf/told/look_off | 51% | 52% | 45% | 48% | 52% | 40% | 43% | 47% |
| llm_naive/not_told/look_off | 64% | 56% | 59% | 57% | 58% | 55% | 58% | 58% |
| llm_naive/told/look_off | 62% | 54% | 59% | 57% | 60% | 56% | 56% | 58% |
| most frequent | 48% | 46% | 41% | 46% | 45% | 35% | 41% | 43% |
| periodic | 64% | 54% | 57% | 58% | 56% | 54% | 56% | 57% |
| timetable | 56% | 51% | 48% | 51% | 49% | 50% | 51% | 51% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (1/3 shift) | Thu (1/3 shift) | Fri (1/3 shift) | Sat (3/3 shift) | Sun (3/3 shift) | Mon (0/3 shift) | Tue (1/3 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 100% / 64% | 95% / 55% | 90% / 58% | 90% / 59% | 94% / 61% | 87% / 53% | 96% / 52% | 93% / 57% |
| last seen | 100% / 64% | 100% / 55% | 100% / 59% | 100% / 58% | 100% / 58% | 100% / 54% | 100% / 56% | 100% / 58% |
| llm_longleaf/not_told/look_off | 95% / 51% | 83% / 55% | 88% / 47% | 88% / 52% | 95% / 51% | 85% / 44% | 89% / 45% | 89% / 49% |
| llm_longleaf/told/look_off | 93% / 50% | 91% / 53% | 86% / 48% | 89% / 50% | 96% / 51% | 94% / 41% | 93% / 43% | 92% / 48% |
| llm_naive/not_told/look_off | 99% / 64% | 97% / 56% | 99% / 59% | 99% / 58% | 98% / 59% | 99% / 55% | 99% / 58% | 99% / 58% |
| llm_naive/told/look_off | 99% / 63% | 97% / 54% | 99% / 59% | 98% / 57% | 98% / 60% | 99% / 55% | 99% / 57% | 99% / 58% |
| most frequent | 90% / 51% | 63% / 61% | 71% / 53% | 68% / 58% | 73% / 57% | 62% / 52% | 76% / 52% | 72% / 55% |
| periodic | 98% / 64% | 98% / 54% | 100% / 57% | 99% / 58% | 99% / 56% | 99% / 54% | 98% / 56% | 99% / 57% |
| timetable | 6% / 45% | 22% / 57% | 45% / 79% | 43% / 72% | 51% / 66% | 48% / 66% | 64% / 64% | 40% / 68% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (1/3 shift) | Thu (1/3 shift) | Fri (1/3 shift) | Sat (3/3 shift) | Sun (3/3 shift) | Mon (0/3 shift) | Tue (1/3 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 100% / 64% | 93% / 56% | 88% / 59% | 83% / 62% | 84% / 64% | 82% / 53% | 84% / 56% | 88% / 59% |
| last seen | 100% / 64% | 100% / 55% | 100% / 59% | 100% / 58% | 100% / 58% | 100% / 54% | 100% / 56% | 100% / 58% |
| llm_longleaf/not_told/look_off | 92% / 51% | 77% / 55% | 82% / 50% | 85% / 52% | 91% / 51% | 75% / 49% | 84% / 47% | 84% / 51% |
| llm_longleaf/told/look_off | 91% / 50% | 78% / 55% | 79% / 52% | 89% / 50% | 95% / 51% | 90% / 42% | 91% / 43% | 88% / 49% |
| llm_naive/not_told/look_off | 96% / 65% | 94% / 57% | 95% / 62% | 95% / 59% | 95% / 60% | 94% / 56% | 95% / 59% | 95% / 60% |
| llm_naive/told/look_off | 96% / 64% | 94% / 55% | 93% / 62% | 95% / 59% | 97% / 61% | 94% / 57% | 95% / 57% | 95% / 59% |
| most frequent | 66% / 62% | 51% / 68% | 46% / 70% | 41% / 75% | 45% / 70% | 39% / 67% | 47% / 63% | 48% / 67% |
| periodic | 82% / 63% | 91% / 54% | 95% / 58% | 99% / 58% | 97% / 56% | 99% / 55% | 97% / 55% | 94% / 57% |
| timetable | 5% / 40% | 1% / 50% | 0% / - | 1% / 100% | 8% / 100% | 19% / 97% | 26% / 78% | 9% / 83% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (1/3 shift) | Thu (1/3 shift) | Fri (1/3 shift) | Sat (3/3 shift) | Sun (3/3 shift) | Mon (0/3 shift) | Tue (1/3 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 80% / 67% | 65% / 66% | 55% / 69% | 66% / 66% | 60% / 68% | 53% / 69% | 60% / 66% | 63% / 67% |
| last seen | 100% / 64% | 100% / 55% | 100% / 59% | 100% / 58% | 100% / 58% | 100% / 54% | 100% / 56% | 100% / 58% |
| llm_longleaf/not_told/look_off | 80% / 56% | 73% / 57% | 68% / 60% | 71% / 60% | 79% / 58% | 56% / 60% | 76% / 51% | 72% / 57% |
| llm_longleaf/told/look_off | 76% / 59% | 67% / 62% | 65% / 61% | 74% / 58% | 84% / 55% | 64% / 58% | 75% / 51% | 72% / 58% |
| llm_naive/not_told/look_off | 85% / 66% | 81% / 60% | 79% / 68% | 88% / 63% | 82% / 62% | 82% / 61% | 89% / 59% | 83% / 63% |
| llm_naive/told/look_off | 81% / 66% | 79% / 60% | 80% / 66% | 86% / 62% | 83% / 64% | 82% / 63% | 88% / 60% | 83% / 63% |
| most frequent | 2% / 100% | 3% / 100% | 25% / 92% | 32% / 82% | 31% / 80% | 22% / 93% | 21% / 88% | 19% / 87% |
| periodic | 26% / 69% | 41% / 42% | 62% / 48% | 57% / 45% | 60% / 45% | 63% / 47% | 66% / 50% | 54% / 48% |
| timetable | 2% / 100% | 0% / - | 0% / - | 1% / 100% | 1% / 100% | 1% / 100% | 1% / 100% | 1% / 100% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | - | 24% (n=45) | 31% (n=48) | 18% (n=38) | 34% (n=32) | 32% (n=84) | 41% (n=256) | 47% (n=226) | 75% (n=615) | 0.320 |
| last seen | - | - | - | - | - | - | - | - | 58% (n=1344) | 0.405 |
| llm_longleaf/not_told/look_off | 21% (n=42) | 53% (n=72) | 43% (n=35) | 29% (n=31) | 24% (n=38) | 8% (n=51) | 13% (n=110) | 8% (n=65) | 61% (n=900) | 0.421 |
| llm_longleaf/told/look_off | 34% (n=41) | 33% (n=42) | 54% (n=28) | 33% (n=33) | 25% (n=24) | 14% (n=70) | 6% (n=139) | 14% (n=92) | 62% (n=875) | 0.435 |
| llm_naive/not_told/look_off | - | 20% (n=5) | 27% (n=11) | - | 30% (n=54) | 25% (n=4) | 38% (n=148) | 60% (n=40) | 63% (n=1082) | 0.337 |
| llm_naive/told/look_off | - | 67% (n=3) | 36% (n=14) | - | 27% (n=51) | - | 34% (n=164) | 51% (n=47) | 63% (n=1065) | 0.342 |
| most frequent | 0% (n=2) | 9% (n=217) | 20% (n=158) | 30% (n=161) | 30% (n=162) | 44% (n=199) | 65% (n=185) | 85% (n=201) | 92% (n=59) | 0.232 |
| periodic | - | - | 54% (n=13) | 53% (n=15) | 63% (n=49) | 61% (n=137) | 71% (n=408) | 47% (n=181) | 48% (n=541) | 0.318 |
| timetable | 6% (n=47) | 36% (n=469) | 50% (n=292) | 57% (n=213) | 70% (n=208) | 82% (n=106) | 100% (n=2) | - | 100% (n=7) | 0.051 |

## Split by household kind (from the intro cards: any retired resident, or none)

Retired residents are home on weekdays too, so the weekend is not a routine shift for their household.

| household kind (n) | agent | Wed | Thu | Fri | Sat | Sun | Mon | Tue | weekday | weekend | drop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| working (13) | Perpetua* | 72% | 56% | 52% | 55% | 53% | 45% | 45% | 54% | 54% | +0 |
| working (13) | last seen | 72% | 61% | 55% | 55% | 55% | 72% | 53% | 62% | 55% | +8 |
| working (13) | llm_longleaf/not_told/look_off | 58% | 61% | 47% | 44% | 47% | 41% | 47% | 51% | 45% | +5 |
| working (13) | llm_longleaf/told/look_off | 58% | 61% | 47% | 44% | 47% | 36% | 44% | 49% | 45% | +4 |
| working (13) | llm_naive/not_told/look_off | 72% | 59% | 55% | 55% | 53% | 67% | 55% | 62% | 54% | +8 |
| working (13) | llm_naive/told/look_off | 72% | 59% | 55% | 55% | 56% | 73% | 55% | 63% | 55% | +7 |
| working (13) | most frequent | 58% | 48% | 44% | 44% | 42% | 38% | 44% | 46% | 43% | +3 |
| working (13) | periodic | 72% | 58% | 52% | 55% | 52% | 72% | 53% | 61% | 53% | +8 |
| working (13) | timetable | 58% | 50% | 47% | 44% | 50% | 56% | 52% | 52% | 47% | +6 |
| retired (7) | Perpetua* | 60% | 53% | 58% | 57% | 59% | 51% | 52% | 55% | 58% | -3 |
| retired (7) | last seen | 60% | 52% | 62% | 59% | 59% | 45% | 57% | 55% | 59% | -4 |
| retired (7) | llm_longleaf/not_told/look_off | 48% | 48% | 45% | 53% | 55% | 42% | 46% | 46% | 54% | -8 |
| retired (7) | llm_longleaf/told/look_off | 48% | 47% | 45% | 50% | 55% | 41% | 43% | 45% | 52% | -8 |
| retired (7) | llm_naive/not_told/look_off | 59% | 54% | 61% | 59% | 60% | 49% | 59% | 57% | 59% | -3 |
| retired (7) | llm_naive/told/look_off | 58% | 51% | 61% | 59% | 62% | 47% | 57% | 55% | 60% | -5 |
| retired (7) | most frequent | 43% | 45% | 40% | 47% | 47% | 34% | 40% | 40% | 47% | -7 |
| retired (7) | periodic | 60% | 52% | 59% | 59% | 59% | 45% | 58% | 55% | 59% | -4 |
| retired (7) | timetable | 55% | 52% | 49% | 54% | 48% | 47% | 50% | 51% | 51% | -1 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| Perpetua* | -8 | -1 | +4 (21) | 49 | 64 |
| last seen | -5 | +2 | +3 (21) | 54 | 64 |
| llm_longleaf/not_told/look_off | -6 | -5 | +7 (21) | 42 | 52 |
| llm_longleaf/told/look_off | -6 | -3 | +8 (21) | 40 | 52 |
| llm_naive/not_told/look_off | -5 | +2 | +3 (21) | 55 | 64 |
| llm_naive/told/look_off | -4 | +2 | +3 (21) | 54 | 62 |
| most frequent | -7 | -5 | +5 (21) | 35 | 48 |
| periodic | -7 | -1 | +4 (21) | 54 | 64 |
| timetable | -8 | -2 | +9 (21) | 48 | 56 |

Households with a major event on a scored day: 18/20; event days: {'hh_s10': [5], 'hh_s11': [3, 7], 'hh_s12': [4, 5, 7], 'hh_s13': [1, 2], 'hh_s14': [2, 3, 6], 'hh_s15': [1, 2, 3, 5], 'hh_s16': [4, 5, 6], 'hh_s17': [2, 6, 7], 'hh_s18': [], 'hh_s19': [2, 3, 4], 'hh_s20': [1, 3, 5], 'hh_s21': [5], 'hh_s22': [3], 'hh_s23': [6, 7], 'hh_s24': [1, 2, 4, 6], 'hh_s25': [1], 'hh_s26': [2, 3, 4, 6], 'hh_s27': [], 'hh_s28': [2, 7], 'hh_s29': [4, 5, 7]}

## Per household: Perpetua* (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 56% | 52% | **55%** | **53%** | 45% | 45% | [4, 5] | [5] |
| hh_s11 | 56% | 59% | **52%** | **56%** | **56%** | 48% | **62%** | [3, 4, 5, 7] | [3, 7] |
| hh_s13 | **64%** | **47%** | 64% | **58%** | **62%** | 53% | 42% | [1, 2, 4, 5] | [1, 2] |

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **55%** | 72% | 53% | [4, 5] | [5] |
| hh_s11 | 56% | 61% | **56%** | **56%** | **55%** | 47% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s13 | **64%** | **42%** | 67% | **62%** | **64%** | 44% | 48% | [1, 2, 4, 5] | [1, 2] |

## Per household: llm_longleaf/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 61% | 47% | **44%** | **47%** | 41% | 47% | [4, 5] | [5] |
| hh_s11 | 52% | 59% | **44%** | **52%** | **55%** | 48% | **53%** | [3, 4, 5, 7] | [3, 7] |
| hh_s13 | **45%** | **36%** | 45% | **55%** | **55%** | 36% | 39% | [1, 2, 4, 5] | [1, 2] |

## Per household: llm_longleaf/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 61% | 47% | **44%** | **47%** | 36% | 44% | [4, 5] | [5] |
| hh_s11 | 52% | 59% | **44%** | **50%** | **55%** | 47% | **47%** | [3, 4, 5, 7] | [3, 7] |
| hh_s13 | **44%** | **34%** | 45% | **50%** | **55%** | 36% | 39% | [1, 2, 4, 5] | [1, 2] |

## Per household: llm_naive/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 59% | 55% | **55%** | **53%** | 67% | 55% | [4, 5] | [5] |
| hh_s11 | 55% | 61% | **55%** | **56%** | **55%** | 50% | **64%** | [3, 4, 5, 7] | [3, 7] |
| hh_s13 | **64%** | **47%** | 67% | **61%** | **66%** | 48% | 55% | [1, 2, 4, 5] | [1, 2] |

## Per household: llm_naive/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 59% | 55% | **55%** | **56%** | 73% | 55% | [4, 5] | [5] |
| hh_s11 | 55% | 61% | **55%** | **56%** | **56%** | 48% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s13 | **61%** | **41%** | 67% | **61%** | **67%** | 45% | 48% | [1, 2, 4, 5] | [1, 2] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 48% | 44% | **44%** | **42%** | 38% | 44% | [4, 5] | [5] |
| hh_s11 | 41% | 55% | **38%** | **47%** | **42%** | 31% | **44%** | [3, 4, 5, 7] | [3, 7] |
| hh_s13 | **45%** | **34%** | 42% | **47%** | **52%** | 36% | 36% | [1, 2, 4, 5] | [1, 2] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 58% | 52% | **55%** | **52%** | 72% | 53% | [4, 5] | [5] |
| hh_s11 | 56% | 61% | **52%** | **56%** | **53%** | 47% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s13 | **64%** | **42%** | 67% | **62%** | **64%** | 44% | 50% | [1, 2, 4, 5] | [1, 2] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 50% | 47% | **44%** | **50%** | 56% | 52% | [4, 5] | [5] |
| hh_s11 | 50% | 59% | **42%** | **47%** | **44%** | 47% | **55%** | [3, 4, 5, 7] | [3, 7] |
| hh_s13 | **61%** | **44%** | 56% | **61%** | **53%** | 47% | 45% | [1, 2, 4, 5] | [1, 2] |
