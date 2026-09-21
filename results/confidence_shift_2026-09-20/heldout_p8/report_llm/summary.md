# 8 h patrol protocol (secondary, sealed 2026-09-20), households s10-14

5 households, 8 agents, 17920 agent-question records. Shift days per household (weekend + major event days): hh_s10 [4, 5]; hh_s11 [3, 4, 5, 7]; hh_s12 [4, 5, 7]; hh_s13 [1, 2, 4, 5]; hh_s14 [2, 3, 4, 5, 6].

Questions per household per agent: hh_s10 448, hh_s11 448, hh_s12 448, hh_s13 448, hh_s14 448.

Object classes in the questions: glass 12%, towel 7%, mug 6%, plate 5%, vacuum_cleaner 5%, blanket 4%, dog_food_bag 4%, snack_bowl 4%, dog_bowl 4%, phone 3%, shopping_bag 3%, bowl 3%, skincare 3%, laundry_basket 3%, toiletry_bag 3%, detergent 2%, glasses 2%, water_bottle 2%, duster 2%, razor 2%, tablet 2%, remote 2%, ironing_board 1%, kitchen_knife 1%, pot 1%, cutting_board 1%, pan 1%, watering_can 1%, spatula 1%, serving_dish 1%, vitamins 1%, recipe_book 1%, board_game 1%, book 1%, charger 1%, guitar 1%, toolbox 1%, iron 0%, journal 0%, dog_toy 0%, hair_dryer 0%, magazine 0%, pen 0%, baking_tray 0%, puzzle_box 0%, yoga_mat 0%, headphones 0%, laptop 0%, controller 0%, mixing_bowl 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 48% | 49% | 51% | 46% | 55% | 43% | 46% | 48% |
| last seen | 49% | 49% | 50% | 52% | 57% | 45% | 48% | 50% |
| llm_longleaf/told/look_off | 45% | 46% | 44% | 48% | 51% | 41% | 46% | 46% |
| llm_naive/not_told/look_off | 48% | 51% | 49% | 52% | 57% | 47% | 49% | 50% |
| llm_naive/told/look_off | 48% | 50% | 50% | 51% | 57% | 45% | 49% | 50% |
| most frequent | 45% | 45% | 43% | 47% | 48% | 35% | 42% | 44% |
| periodic | 47% | 49% | 48% | 51% | 56% | 45% | 48% | 49% |
| timetable | 48% | 46% | 45% | 48% | 50% | 38% | 44% | 45% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 100% / 48% | 92% / 52% | 87% / 55% | 87% / 52% | 85% / 62% | 80% / 48% | 87% / 49% | 88% / 52% |
| last seen | 100% / 49% | 100% / 49% | 100% / 50% | 100% / 52% | 100% / 57% | 100% / 45% | 100% / 48% | 100% / 50% |
| llm_longleaf/told/look_off | 60% / 57% | 56% / 60% | 60% / 62% | 64% / 60% | 70% / 62% | 55% / 55% | 71% / 54% | 62% / 59% |
| llm_naive/not_told/look_off | 96% / 49% | 95% / 52% | 97% / 51% | 98% / 52% | 99% / 57% | 95% / 48% | 97% / 50% | 97% / 51% |
| llm_naive/told/look_off | 96% / 49% | 95% / 50% | 97% / 51% | 98% / 52% | 100% / 58% | 98% / 46% | 96% / 50% | 97% / 51% |
| most frequent | 52% / 61% | 57% / 60% | 63% / 58% | 67% / 55% | 70% / 60% | 68% / 46% | 74% / 48% | 65% / 55% |
| periodic | 43% / 54% | 85% / 47% | 91% / 48% | 97% / 52% | 94% / 54% | 98% / 44% | 98% / 47% | 87% / 49% |
| timetable | 1% / 100% | 25% / 54% | 45% / 67% | 53% / 63% | 61% / 60% | 53% / 53% | 61% / 52% | 43% / 58% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 84% / 51% | 73% / 58% | 68% / 61% | 68% / 58% | 68% / 62% | 63% / 53% | 64% / 60% | 70% / 57% |
| last seen | 100% / 49% | 100% / 49% | 100% / 50% | 100% / 52% | 100% / 57% | 100% / 45% | 100% / 48% | 100% / 50% |
| llm_longleaf/told/look_off | 7% / 65% | 28% / 73% | 30% / 75% | 38% / 71% | 34% / 77% | 31% / 67% | 32% / 73% | 29% / 72% |
| llm_naive/not_told/look_off | 89% / 50% | 81% / 56% | 84% / 57% | 91% / 54% | 89% / 61% | 79% / 53% | 82% / 56% | 85% / 56% |
| llm_naive/told/look_off | 86% / 51% | 84% / 55% | 82% / 57% | 88% / 56% | 87% / 62% | 80% / 52% | 86% / 54% | 85% / 55% |
| most frequent | 1% / 100% | 29% / 72% | 38% / 69% | 41% / 70% | 38% / 73% | 37% / 61% | 39% / 64% | 32% / 68% |
| periodic | 9% / 30% | 33% / 19% | 51% / 34% | 55% / 39% | 62% / 48% | 68% / 34% | 65% / 39% | 49% / 37% |
| timetable | 1% / 100% | 0% / - | 0% / 100% | 0% / 100% | 19% / 67% | 27% / 69% | 28% / 66% | 11% / 68% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 66% / 60% | 51% / 68% | 48% / 65% | 43% / 66% | 37% / 72% | 34% / 69% | 32% / 63% | 45% / 66% |
| last seen | 100% / 49% | 100% / 49% | 100% / 50% | 100% / 52% | 100% / 57% | 100% / 45% | 100% / 48% | 100% / 50% |
| llm_longleaf/told/look_off | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| llm_naive/not_told/look_off | 61% / 60% | 62% / 64% | 57% / 65% | 64% / 64% | 68% / 67% | 55% / 59% | 61% / 65% | 61% / 64% |
| llm_naive/told/look_off | 61% / 61% | 61% / 66% | 54% / 66% | 63% / 63% | 64% / 70% | 58% / 59% | 64% / 64% | 61% / 64% |
| most frequent | 1% / 100% | 0% / - | 0% / 100% | 0% / 100% | 0% / - | 0% / 100% | 0% / 100% | 0% / 100% |
| periodic | 1% / 100% | 11% / 20% | 33% / 39% | 37% / 43% | 46% / 52% | 42% / 36% | 49% / 47% | 31% / 43% |
| timetable | 1% / 100% | 0% / - | 0% / 100% | 0% / 100% | 0% / - | 0% / 100% | 0% / 100% | 0% / 100% |

## Coverage-matched selective accuracy (each agent answers its most confident 25 / 50 / 75% of the day's questions)

The fixed thresholds above compare different confidence scales; this compares agents at equal coverage.

| agent (coverage 25%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 64% | 65% | 71% | 69% | 76% | 72% | 70% | 65% |
| last seen | 55% | 41% | 55% | 51% | 55% | 62% | 48% | 52% |
| llm_longleaf/told/look_off | 56% | 75% | 78% | 65% | 78% | 74% | 69% | 74% |
| llm_naive/not_told/look_off | 70% | 79% | 68% | 68% | 70% | 65% | 66% | 68% |
| llm_naive/told/look_off | 70% | 79% | 64% | 69% | 70% | 68% | 65% | 69% |
| most frequent | 50% | 69% | 70% | 66% | 76% | 75% | 68% | 71% |
| periodic | 46% | 19% | 46% | 49% | 61% | 36% | 52% | 46% |
| timetable | 51% | 55% | 64% | 68% | 69% | 69% | 70% | 65% |

| agent (coverage 50%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 60% | 68% | 66% | 63% | 66% | 58% | 62% | 63% |
| last seen | 52% | 50% | 49% | 52% | 51% | 50% | 48% | 50% |
| llm_longleaf/told/look_off | 61% | 64% | 65% | 66% | 69% | 56% | 58% | 62% |
| llm_naive/not_told/look_off | 66% | 68% | 64% | 64% | 74% | 61% | 66% | 66% |
| llm_naive/told/look_off | 66% | 70% | 65% | 66% | 74% | 66% | 67% | 67% |
| most frequent | 63% | 66% | 64% | 65% | 64% | 57% | 59% | 60% |
| periodic | 56% | 32% | 34% | 41% | 52% | 37% | 46% | 37% |
| timetable | 53% | 57% | 63% | 64% | 67% | 56% | 59% | 55% |

| agent (coverage 75%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 55% | 57% | 60% | 57% | 65% | 48% | 56% | 56% |
| last seen | 53% | 47% | 54% | 53% | 56% | 47% | 52% | 51% |
| llm_longleaf/told/look_off | 50% | 54% | 52% | 57% | 61% | 49% | 54% | 54% |
| llm_naive/not_told/look_off | 55% | 59% | 58% | 59% | 65% | 53% | 59% | 59% |
| llm_naive/told/look_off | 56% | 60% | 60% | 58% | 66% | 52% | 59% | 58% |
| most frequent | 49% | 53% | 51% | 54% | 56% | 44% | 48% | 51% |
| periodic | 50% | 46% | 45% | 46% | 50% | 38% | 42% | 47% |
| timetable | 57% | 53% | 52% | 55% | 58% | 44% | 48% | 50% |

## Questions whose object moved since the robot's last round (50% of questions)

The robot's last full look is the patrol round before the question. 'still' questions are answered by recency almost by definition; the shift and the learning live in the 'moved' half. Cells: accuracy c=mean confidence.

| agent | Wed moved / still | Thu moved / still | Fri moved / still | Sat moved / still | Sun moved / still | Mon moved / still | Tue moved / still | moved all | still all |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 2% c85 / 100% c93 | 2% c75 / 100% c90 | 6% c72 / 97% c88 | 1% c72 / 90% c86 | 6% c70 / 92% c82 | 5% c68 / 92% c82 | 6% c70 / 90% c83 | 4% (n=1143, cov@0.7 58%, sel 2%) | 94% |
| last seen | 4% c98 / 100% c98 | 2% c98 / 100% c98 | 2% c98 / 100% c98 | 1% c98 / 100% c98 | 1% c98 / 100% c98 | 2% c98 / 100% c98 | 1% c98 / 100% c98 | 2% (n=1143, cov@0.7 100%, sel 2%) | 100% |
| llm_longleaf/told/look_off | 8% c50 / 87% c57 | 11% c47 / 85% c60 | 10% c49 / 80% c63 | 5% c52 / 90% c65 | 8% c54 / 85% c66 | 4% c50 / 87% c63 | 8% c55 / 88% c65 | 8% (n=1143, cov@0.7 16%, sel 1%) | 86% |
| llm_naive/not_told/look_off | 2% c83 / 100% c91 | 7% c80 / 98% c91 | 3% c80 / 97% c91 | 1% c85 / 100% c92 | 4% c84 / 99% c92 | 5% c79 / 99% c91 | 7% c80 / 95% c92 | 4% (n=1143, cov@0.7 75%, sel 2%) | 98% |
| llm_naive/told/look_off | 2% c82 / 100% c91 | 5% c80 / 100% c92 | 3% c79 / 98% c91 | 1% c83 / 100% c92 | 2% c83 / 100% c91 | 3% c81 / 99% c91 | 6% c81 / 96% c92 | 3% (n=1143, cov@0.7 75%, sel 1%) | 99% |
| most frequent | 5% c48 / 90% c54 | 11% c50 / 83% c62 | 10% c53 / 78% c67 | 6% c55 / 87% c68 | 10% c56 / 78% c68 | 4% c56 / 74% c68 | 8% c59 / 79% c69 | 8% (n=1143, cov@0.7 19%, sel 4%) | 81% |
| periodic | 4% c49 / 96% c50 | 5% c70 / 97% c59 | 5% c79 / 94% c71 | 2% c80 / 99% c74 | 2% c84 / 97% c77 | 2% c85 / 100% c77 | 2% c86 / 99% c79 | 3% (n=1143, cov@0.7 62%, sel 1%) | 97% |
| timetable | 6% c33 / 94% c35 | 7% c40 / 89% c45 | 12% c43 / 79% c52 | 7% c46 / 88% c55 | 12% c50 / 80% c58 | 6% c49 / 79% c59 | 10% c51 / 82% c61 | 8% (n=1143, cov@0.7 7%, sel 3%) | 84% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | - | 22% (n=92) | 19% (n=171) | 21% (n=213) | 43% (n=200) | 42% (n=276) | 44% (n=291) | 48% (n=113) | 68% (n=884) | 0.313 |
| last seen | - | - | - | - | - | - | - | - | 50% (n=2240) | 0.482 |
| llm_longleaf/told/look_off | 17% (n=6) | 21% (n=450) | 30% (n=389) | 44% (n=351) | 50% (n=403) | 72% (n=469) | 73% (n=172) | - | - | 0.105 |
| llm_naive/not_told/look_off | - | 33% (n=3) | 15% (n=68) | - | 22% (n=265) | 27% (n=26) | 35% (n=509) | 49% (n=187) | 66% (n=1182) | 0.361 |
| llm_naive/told/look_off | 0% (n=2) | 33% (n=9) | 21% (n=57) | - | 21% (n=273) | 14% (n=36) | 33% (n=500) | 50% (n=207) | 67% (n=1156) | 0.362 |
| most frequent | 0% (n=3) | 21% (n=365) | 25% (n=426) | 38% (n=397) | 47% (n=339) | 61% (n=314) | 73% (n=390) | - | 100% (n=6) | 0.157 |
| periodic | 0% (n=1) | 56% (n=114) | 45% (n=184) | 68% (n=304) | 64% (n=535) | 26% (n=148) | 25% (n=253) | 34% (n=225) | 47% (n=476) | 0.298 |
| timetable | 4% (n=54) | 34% (n=751) | 42% (n=482) | 45% (n=326) | 64% (n=387) | 67% (n=234) | - | - | 100% (n=6) | 0.048 |

## Split by household kind (from the intro cards: any retired resident, or none)

Retired residents are home on weekdays too, so the weekend is not a routine shift for their household.

| household kind (n) | agent | Wed | Thu | Fri | Sat | Sun | Mon | Tue | weekday | weekend | drop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| working (13) | Perpetua* | 58% | 55% | 48% | 45% | 41% | 39% | 45% | 49% | 43% | +6 |
| working (13) | last seen | 58% | 55% | 48% | 45% | 45% | 41% | 44% | 49% | 45% | +4 |
| working (13) | llm_longleaf/told/look_off | 58% | 52% | 44% | 44% | 41% | 38% | 44% | 47% | 42% | +5 |
| working (13) | llm_naive/not_told/look_off | 58% | 55% | 47% | 47% | 45% | 45% | 44% | 50% | 46% | +4 |
| working (13) | llm_naive/told/look_off | 58% | 55% | 47% | 45% | 47% | 41% | 45% | 49% | 46% | +3 |
| working (13) | most frequent | 58% | 53% | 45% | 44% | 42% | 36% | 44% | 47% | 43% | +4 |
| working (13) | periodic | 58% | 52% | 45% | 45% | 42% | 41% | 44% | 48% | 44% | +4 |
| working (13) | timetable | 58% | 55% | 47% | 44% | 42% | 34% | 47% | 48% | 43% | +5 |
| retired (7) | Perpetua* | 45% | 48% | 51% | 46% | 58% | 45% | 46% | 47% | 52% | -5 |
| retired (7) | last seen | 46% | 48% | 51% | 53% | 60% | 46% | 49% | 48% | 57% | -9 |
| retired (7) | llm_longleaf/told/look_off | 42% | 45% | 45% | 50% | 54% | 41% | 47% | 44% | 52% | -8 |
| retired (7) | llm_naive/not_told/look_off | 45% | 50% | 50% | 53% | 61% | 47% | 50% | 48% | 57% | -8 |
| retired (7) | llm_naive/told/look_off | 45% | 49% | 50% | 53% | 60% | 46% | 50% | 48% | 56% | -8 |
| retired (7) | most frequent | 41% | 43% | 43% | 48% | 50% | 35% | 41% | 41% | 49% | -8 |
| retired (7) | periodic | 44% | 48% | 49% | 53% | 59% | 46% | 49% | 47% | 56% | -9 |
| retired (7) | timetable | 45% | 44% | 44% | 49% | 52% | 39% | 43% | 43% | 51% | -8 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| Perpetua* | +3 | +5 | +2 (21) | 43 | 55 |
| last seen | +2 | -1 | +1 (21) | 45 | 57 |
| llm_longleaf/told/look_off | -1 | -4 | +1 (21) | 41 | 51 |
| llm_naive/not_told/look_off | +1 | -2 | +0 (21) | 47 | 57 |
| llm_naive/told/look_off | +2 | -2 | +1 (21) | 45 | 57 |
| most frequent | -2 | -4 | +1 (21) | 35 | 48 |
| periodic | +2 | -3 | +2 (21) | 45 | 56 |
| timetable | -3 | -3 | +5 (21) | 38 | 50 |

Households with a major event on a scored day: 18/20; event days: {'hh_s10': [5], 'hh_s11': [3, 7], 'hh_s12': [4, 5, 7], 'hh_s13': [1, 2], 'hh_s14': [2, 3, 6], 'hh_s15': [1, 2, 3, 5], 'hh_s16': [4, 5, 6], 'hh_s17': [2, 6, 7], 'hh_s18': [], 'hh_s19': [2, 3, 4], 'hh_s20': [1, 3, 5], 'hh_s21': [5], 'hh_s22': [3], 'hh_s23': [6, 7], 'hh_s24': [1, 2, 4, 6], 'hh_s25': [1], 'hh_s26': [2, 3, 4, 6], 'hh_s27': [], 'hh_s28': [2, 7], 'hh_s29': [4, 5, 7]}

## Per household: Perpetua* (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 55% | 48% | **45%** | **41%** | 39% | 45% | [4, 5] | [5] |
| hh_s11 | 45% | 59% | **44%** | **41%** | **52%** | 45% | **44%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 45% | 55% | 61% | **52%** | **69%** | 39% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **44%** | **39%** | 59% | **50%** | **66%** | 41% | 38% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **38%** | **41%** | **42%** | **47%** | **53%** | 45% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 55% | 48% | **45%** | **45%** | 41% | 44% | [4, 5] | [5] |
| hh_s11 | 45% | 59% | **41%** | **48%** | **55%** | 45% | **44%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 50% | 55% | 62% | **55%** | **69%** | 39% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **44%** | **39%** | 55% | **56%** | **62%** | 42% | 45% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **38%** | **45%** | **53%** | **55%** | **58%** | 50% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: llm_longleaf/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 52% | 44% | **44%** | **41%** | 38% | 44% | [4, 5] | [5] |
| hh_s11 | 41% | 58% | **41%** | **50%** | **55%** | 45% | **44%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 44% | 48% | 50% | **50%** | **66%** | 39% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **45%** | **36%** | 47% | **50%** | **55%** | 36% | 36% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 38% | **38%** | **41%** | **48%** | **41%** | **45%** | 50% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: llm_naive/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 55% | 47% | **47%** | **45%** | 45% | 44% | [4, 5] | [5] |
| hh_s11 | 45% | 58% | **38%** | **48%** | **55%** | 47% | **48%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 45% | 59% | 61% | **53%** | **69%** | 39% | **61%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **44%** | **41%** | 55% | **56%** | **66%** | 42% | 39% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **41%** | **45%** | **53%** | **53%** | **59%** | 52% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: llm_naive/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 55% | 47% | **45%** | **47%** | 41% | 45% | [4, 5] | [5] |
| hh_s11 | 45% | 59% | **39%** | **48%** | **55%** | 47% | **42%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 45% | 59% | 59% | **52%** | **69%** | 38% | **64%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **44%** | **39%** | 58% | **56%** | **62%** | 42% | 44% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **39%** | **45%** | **55%** | **55%** | **58%** | 48% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 53% | 45% | **44%** | **42%** | 36% | 44% | [4, 5] | [5] |
| hh_s11 | 36% | 52% | **39%** | **48%** | **45%** | 38% | **42%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 45% | 53% | 47% | **50%** | **62%** | 33% | **45%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **45%** | **31%** | 44% | **47%** | **52%** | 36% | 39% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 39% | **38%** | **41%** | **45%** | **41%** | **34%** | 38% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 52% | 45% | **45%** | **42%** | 41% | 44% | [4, 5] | [5] |
| hh_s11 | 44% | 59% | **39%** | **48%** | **53%** | 45% | **44%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 47% | 55% | 62% | **53%** | **66%** | 39% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **44%** | **39%** | 55% | **56%** | **62%** | 42% | 47% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 42% | **41%** | **41%** | **53%** | **55%** | **58%** | 47% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 55% | 47% | **44%** | **42%** | 34% | 47% | [4, 5] | [5] |
| hh_s11 | 45% | 58% | **47%** | **41%** | **48%** | 44% | **44%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 39% | 50% | 48% | **48%** | **62%** | 33% | **42%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **53%** | **30%** | 45% | **59%** | **56%** | 42% | 41% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 42% | **38%** | **36%** | **48%** | **41%** | **38%** | 47% | [2, 3, 4, 5, 6] | [2, 3, 6] |
