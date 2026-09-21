# Held-out households hh_s10, hh_s11, hh_s12, hh_s13, hh_s14: every agent

5 households, 7 agents, 15680 agent-question records. Shift days per household (weekend + major event days): hh_s10 [4, 5]; hh_s11 [3, 4, 5, 7]; hh_s12 [4, 5, 7]; hh_s13 [1, 2, 4, 5]; hh_s14 [2, 3, 4, 5, 6].

Questions per household per agent: hh_s10 448, hh_s11 448, hh_s12 448, hh_s13 448, hh_s14 448.

Object classes in the questions: glass 12%, towel 7%, mug 6%, plate 5%, vacuum_cleaner 5%, blanket 4%, dog_food_bag 4%, snack_bowl 4%, dog_bowl 4%, phone 3%, shopping_bag 3%, bowl 3%, skincare 3%, laundry_basket 3%, toiletry_bag 3%, detergent 2%, glasses 2%, water_bottle 2%, duster 2%, razor 2%, tablet 2%, remote 2%, ironing_board 1%, kitchen_knife 1%, pot 1%, cutting_board 1%, pan 1%, watering_can 1%, spatula 1%, serving_dish 1%, vitamins 1%, recipe_book 1%, board_game 1%, book 1%, charger 1%, guitar 1%, toolbox 1%, iron 0%, journal 0%, dog_toy 0%, hair_dryer 0%, magazine 0%, pen 0%, baking_tray 0%, puzzle_box 0%, yoga_mat 0%, headphones 0%, laptop 0%, controller 0%, mixing_bowl 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 58% | 54% | 59% | 56% | 57% | 48% | 53% | 55% |
| last seen | 58% | 56% | 61% | 58% | 62% | 52% | 56% | 58% |
| llm_naive/not_told/look_off | 60% | 56% | 61% | 58% | 62% | 50% | 56% | 57% |
| llm_naive/told/look_off | 59% | 56% | 61% | 57% | 62% | 51% | 56% | 57% |
| most frequent | 58% | 56% | 60% | 58% | 63% | 52% | 56% | 58% |
| periodic | 58% | 56% | 61% | 58% | 62% | 52% | 56% | 58% |
| timetable | 58% | 55% | 61% | 58% | 62% | 52% | 56% | 57% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 100% / 58% | 96% / 55% | 92% / 61% | 93% / 57% | 95% / 60% | 91% / 51% | 95% / 55% | 95% / 57% |
| last seen | 100% / 58% | 100% / 56% | 100% / 61% | 100% / 58% | 100% / 62% | 100% / 52% | 100% / 56% | 100% / 58% |
| llm_naive/not_told/look_off | 97% / 59% | 100% / 56% | 100% / 61% | 100% / 58% | 99% / 63% | 99% / 50% | 100% / 56% | 99% / 58% |
| llm_naive/told/look_off | 98% / 59% | 100% / 56% | 100% / 61% | 99% / 58% | 98% / 62% | 99% / 51% | 99% / 56% | 99% / 58% |
| most frequent | 100% / 58% | 99% / 56% | 98% / 60% | 97% / 57% | 99% / 62% | 99% / 53% | 97% / 57% | 98% / 58% |
| periodic | 100% / 58% | 100% / 56% | 100% / 61% | 100% / 58% | 100% / 62% | 100% / 52% | 100% / 56% | 100% / 58% |
| timetable | 99% / 59% | 97% / 56% | 99% / 61% | 99% / 58% | 97% / 63% | 98% / 52% | 99% / 56% | 98% / 58% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 100% / 58% | 94% / 56% | 88% / 62% | 87% / 59% | 87% / 62% | 84% / 52% | 85% / 58% | 89% / 58% |
| last seen | 100% / 58% | 100% / 56% | 100% / 61% | 100% / 58% | 100% / 62% | 100% / 52% | 100% / 56% | 100% / 58% |
| llm_naive/not_told/look_off | 97% / 59% | 98% / 56% | 99% / 61% | 98% / 58% | 97% / 64% | 98% / 50% | 99% / 56% | 98% / 58% |
| llm_naive/told/look_off | 97% / 59% | 98% / 55% | 99% / 61% | 97% / 59% | 95% / 63% | 96% / 52% | 98% / 57% | 97% / 58% |
| most frequent | 95% / 58% | 95% / 55% | 96% / 60% | 94% / 58% | 93% / 62% | 92% / 53% | 95% / 56% | 94% / 57% |
| periodic | 99% / 58% | 98% / 55% | 99% / 61% | 100% / 58% | 99% / 62% | 100% / 52% | 100% / 56% | 99% / 58% |
| timetable | 98% / 59% | 97% / 56% | 98% / 61% | 99% / 58% | 97% / 63% | 98% / 52% | 97% / 56% | 98% / 58% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 84% / 58% | 68% / 64% | 59% / 68% | 58% / 67% | 62% / 66% | 56% / 65% | 62% / 64% | 64% / 64% |
| last seen | 100% / 58% | 100% / 56% | 100% / 61% | 100% / 58% | 100% / 62% | 100% / 52% | 100% / 56% | 100% / 58% |
| llm_naive/not_told/look_off | 93% / 61% | 93% / 58% | 98% / 60% | 96% / 59% | 93% / 65% | 93% / 50% | 96% / 57% | 95% / 59% |
| llm_naive/told/look_off | 92% / 61% | 92% / 58% | 95% / 60% | 93% / 60% | 90% / 65% | 92% / 52% | 93% / 57% | 92% / 59% |
| most frequent | 83% / 60% | 80% / 59% | 78% / 62% | 82% / 61% | 80% / 61% | 73% / 55% | 81% / 59% | 80% / 60% |
| periodic | 95% / 61% | 95% / 56% | 98% / 61% | 99% / 58% | 98% / 62% | 99% / 52% | 100% / 56% | 98% / 58% |
| timetable | 87% / 62% | 86% / 59% | 84% / 60% | 86% / 60% | 86% / 63% | 88% / 56% | 86% / 58% | 86% / 60% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | - | 26% (n=53) | 26% (n=68) | 24% (n=54) | 38% (n=61) | 34% (n=137) | 45% (n=428) | 49% (n=445) | 71% (n=994) | 0.331 |
| last seen | - | - | - | - | - | - | - | - | 58% (n=2240) | 0.424 |
| llm_naive/not_told/look_off | - | 0% (n=1) | 50% (n=14) | - | 54% (n=28) | - | 31% (n=77) | 49% (n=47) | 59% (n=2073) | 0.370 |
| llm_naive/told/look_off | - | 56% (n=9) | 36% (n=14) | - | 40% (n=40) | - | 37% (n=109) | 46% (n=52) | 59% (n=2016) | 0.365 |
| most frequent | - | 67% (n=9) | 56% (n=27) | 62% (n=39) | 58% (n=55) | 49% (n=94) | 42% (n=231) | 54% (n=179) | 61% (n=1606) | 0.367 |
| periodic | - | - | - | 29% (n=7) | 78% (n=9) | 29% (n=17) | 40% (n=20) | 95% (n=19) | 58% (n=2168) | 0.415 |
| timetable | - | 21% (n=24) | 50% (n=16) | 100% (n=4) | 56% (n=9) | 37% (n=38) | 46% (n=224) | 53% (n=450) | 62% (n=1475) | 0.368 |

## Split by household kind (from the intro cards: any retired resident, or none)

Retired residents are home on weekdays too, so the weekend is not a routine shift for their household.

| household kind (n) | agent | Wed | Thu | Fri | Sat | Sun | Mon | Tue | weekday | weekend | drop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| working (13) | Perpetua* | 72% | 56% | 52% | 55% | 53% | 45% | 45% | 54% | 54% | +0 |
| working (13) | last seen | 72% | 61% | 55% | 55% | 55% | 72% | 53% | 62% | 55% | +8 |
| working (13) | llm_naive/not_told/look_off | 72% | 61% | 55% | 55% | 55% | 59% | 53% | 60% | 55% | +5 |
| working (13) | llm_naive/told/look_off | 72% | 61% | 55% | 55% | 58% | 66% | 53% | 61% | 56% | +5 |
| working (13) | most frequent | 72% | 61% | 55% | 55% | 61% | 70% | 53% | 62% | 58% | +4 |
| working (13) | periodic | 72% | 61% | 55% | 55% | 55% | 72% | 53% | 62% | 55% | +8 |
| working (13) | timetable | 72% | 56% | 55% | 55% | 61% | 72% | 53% | 62% | 58% | +4 |
| retired (7) | Perpetua* | 55% | 54% | 61% | 56% | 58% | 49% | 55% | 55% | 57% | -3 |
| retired (7) | last seen | 55% | 55% | 62% | 59% | 64% | 47% | 57% | 55% | 61% | -6 |
| retired (7) | llm_naive/not_told/look_off | 57% | 55% | 62% | 59% | 64% | 47% | 57% | 56% | 61% | -6 |
| retired (7) | llm_naive/told/look_off | 56% | 54% | 62% | 58% | 63% | 48% | 57% | 55% | 61% | -5 |
| retired (7) | most frequent | 55% | 55% | 62% | 59% | 63% | 48% | 57% | 55% | 61% | -6 |
| retired (7) | periodic | 55% | 55% | 62% | 59% | 64% | 47% | 57% | 55% | 61% | -6 |
| retired (7) | timetable | 55% | 55% | 62% | 59% | 63% | 47% | 57% | 55% | 61% | -6 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| Perpetua* | +1 | +3 | -4 (21) | 48 | 59 |
| last seen | +3 | +3 | -4 (21) | 52 | 62 |
| llm_naive/not_told/look_off | +1 | +3 | -2 (21) | 50 | 62 |
| llm_naive/told/look_off | +2 | +3 | -3 (21) | 51 | 62 |
| most frequent | +2 | +2 | -3 (21) | 52 | 63 |
| periodic | +3 | +3 | -4 (21) | 52 | 62 |
| timetable | +3 | +3 | -4 (21) | 52 | 62 |

Households with a major event on a scored day: 18/20; event days: {'hh_s10': [5], 'hh_s11': [3, 7], 'hh_s12': [4, 5, 7], 'hh_s13': [1, 2], 'hh_s14': [2, 3, 6], 'hh_s15': [1, 2, 3, 5], 'hh_s16': [4, 5, 6], 'hh_s17': [2, 6, 7], 'hh_s18': [], 'hh_s19': [2, 3, 4], 'hh_s20': [1, 3, 5], 'hh_s21': [5], 'hh_s22': [3], 'hh_s23': [6, 7], 'hh_s24': [1, 2, 4, 6], 'hh_s25': [1], 'hh_s26': [2, 3, 4, 6], 'hh_s27': [], 'hh_s28': [2, 7], 'hh_s29': [4, 5, 7]}

## Per household: Perpetua* (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 56% | 52% | **55%** | **53%** | 45% | 45% | [4, 5] | [5] |
| hh_s11 | 56% | 59% | **52%** | **56%** | **56%** | 48% | **62%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 52% | 56% | 69% | **59%** | **61%** | 38% | **59%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **64%** | **47%** | 64% | **58%** | **62%** | 53% | 42% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **53%** | **58%** | **52%** | **53%** | **56%** | 55% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **55%** | 72% | 53% | [4, 5] | [5] |
| hh_s11 | 56% | 61% | **56%** | **56%** | **55%** | 47% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 52% | 61% | 69% | **61%** | **67%** | 38% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **64%** | **42%** | 67% | **62%** | **64%** | 44% | 48% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **55%** | **58%** | **55%** | **69%** | **61%** | 55% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: llm_naive/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **55%** | 59% | 53% | [4, 5] | [5] |
| hh_s11 | 55% | 61% | **56%** | **56%** | **55%** | 47% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 52% | 61% | 67% | **61%** | **67%** | 39% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **73%** | **44%** | 67% | **62%** | **64%** | 42% | 48% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **55%** | **58%** | **55%** | **70%** | **61%** | 55% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: llm_naive/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **58%** | 66% | 53% | [4, 5] | [5] |
| hh_s11 | 55% | 61% | **56%** | **56%** | **55%** | 48% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 52% | 61% | 67% | **59%** | **67%** | 38% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **70%** | **42%** | 67% | **62%** | **64%** | 44% | 48% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **53%** | **58%** | **55%** | **66%** | **61%** | 55% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **61%** | 70% | 53% | [4, 5] | [5] |
| hh_s11 | 56% | 61% | **55%** | **56%** | **55%** | 48% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 52% | 61% | 69% | **61%** | **66%** | 38% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **64%** | **42%** | 67% | **62%** | **64%** | 44% | 48% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **55%** | **56%** | **55%** | **69%** | **61%** | 55% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **55%** | 72% | 53% | [4, 5] | [5] |
| hh_s11 | 56% | 61% | **56%** | **56%** | **55%** | 47% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 52% | 61% | 69% | **61%** | **69%** | 38% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **64%** | **42%** | 67% | **62%** | **64%** | 44% | 48% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **55%** | **58%** | **55%** | **69%** | **61%** | 55% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 56% | 55% | **55%** | **61%** | 72% | 53% | [4, 5] | [5] |
| hh_s11 | 56% | 61% | **56%** | **56%** | **55%** | 48% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 52% | 61% | 69% | **61%** | **64%** | 34% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **64%** | **42%** | 67% | **62%** | **64%** | 44% | 50% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **55%** | **58%** | **55%** | **69%** | **61%** | 55% | [2, 3, 4, 5, 6] | [2, 3, 6] |
