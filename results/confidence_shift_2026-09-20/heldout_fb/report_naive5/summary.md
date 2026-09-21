# hh_s10-14, feedback protocol: classical + naive

5 households, 7 agents, 15680 agent-question records. Shift days per household (weekend + major event days): hh_s10 [4, 5]; hh_s11 [3, 4, 5, 7]; hh_s12 [4, 5, 7]; hh_s13 [1, 2, 4, 5]; hh_s14 [2, 3, 4, 5, 6].

Questions per household per agent: hh_s10 448, hh_s11 448, hh_s12 448, hh_s13 448, hh_s14 448.

Object classes in the questions: glass 12%, mug 7%, towel 6%, plate 5%, vacuum_cleaner 5%, dog_food_bag 5%, dog_bowl 4%, blanket 4%, shopping_bag 3%, snack_bowl 3%, phone 3%, bowl 3%, glasses 3%, skincare 3%, toiletry_bag 3%, duster 3%, laundry_basket 2%, water_bottle 2%, detergent 2%, razor 2%, remote 2%, tablet 2%, ironing_board 1%, pot 1%, pan 1%, kitchen_knife 1%, spatula 1%, guitar 1%, watering_can 1%, cutting_board 1%, serving_dish 1%, vitamins 1%, book 1%, charger 1%, recipe_book 1%, iron 0%, journal 0%, toolbox 0%, board_game 0%, dog_toy 0%, hair_dryer 0%, headphones 0%, magazine 0%, pen 0%, yoga_mat 0%, puzzle_box 0%, baking_tray 0%, laptop 0%, mixing_bowl 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 52% | 52% | 54% | 48% | 52% | 47% | 50% | 51% |
| last seen | 52% | 56% | 55% | 51% | 54% | 51% | 52% | 53% |
| llm_naive/not_told/look_off | 52% | 58% | 59% | 52% | 53% | 56% | 63% | 56% |
| llm_naive/told/look_off | 53% | 59% | 58% | 51% | 55% | 54% | 61% | 56% |
| most frequent | 46% | 52% | 50% | 45% | 47% | 47% | 49% | 48% |
| periodic | 52% | 55% | 55% | 53% | 53% | 55% | 57% | 54% |
| timetable | 50% | 53% | 52% | 50% | 53% | 59% | 59% | 54% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 97% / 54% | 82% / 59% | 78% / 62% | 73% / 58% | 72% / 57% | 70% / 57% | 70% / 63% | 77% / 59% |
| last seen | 100% / 52% | 100% / 56% | 100% / 55% | 100% / 51% | 100% / 54% | 100% / 51% | 100% / 52% | 100% / 53% |
| llm_naive/not_told/look_off | 99% / 53% | 96% / 60% | 95% / 61% | 97% / 54% | 97% / 55% | 95% / 59% | 98% / 64% | 97% / 58% |
| llm_naive/told/look_off | 98% / 54% | 95% / 61% | 96% / 60% | 95% / 53% | 98% / 56% | 98% / 55% | 98% / 62% | 97% / 57% |
| most frequent | 23% / 77% | 49% / 78% | 49% / 69% | 50% / 57% | 49% / 62% | 49% / 60% | 48% / 66% | 45% / 66% |
| periodic | 29% / 59% | 65% / 52% | 78% / 57% | 84% / 52% | 90% / 53% | 93% / 55% | 92% / 55% | 76% / 54% |
| timetable | 15% / 73% | 29% / 86% | 29% / 69% | 37% / 63% | 33% / 61% | 34% / 72% | 45% / 78% | 32% / 71% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 76% / 60% | 61% / 71% | 57% / 70% | 53% / 63% | 53% / 63% | 52% / 61% | 51% / 64% | 57% / 65% |
| last seen | 100% / 52% | 100% / 56% | 100% / 55% | 100% / 51% | 100% / 54% | 100% / 51% | 100% / 52% | 100% / 53% |
| llm_naive/not_told/look_off | 88% / 56% | 81% / 65% | 78% / 67% | 88% / 54% | 87% / 57% | 84% / 61% | 84% / 66% | 84% / 61% |
| llm_naive/told/look_off | 86% / 57% | 81% / 66% | 78% / 66% | 84% / 57% | 81% / 58% | 85% / 59% | 85% / 66% | 83% / 61% |
| most frequent | 5% / 65% | 14% / 85% | 24% / 79% | 25% / 80% | 30% / 76% | 28% / 83% | 27% / 92% | 22% / 82% |
| periodic | 14% / 40% | 32% / 39% | 49% / 57% | 56% / 48% | 60% / 53% | 66% / 55% | 61% / 52% | 48% / 51% |
| timetable | 4% / 69% | 6% / 95% | 9% / 64% | 12% / 78% | 12% / 68% | 10% / 77% | 15% / 85% | 10% / 77% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (1/5 shift) | Thu (2/5 shift) | Fri (2/5 shift) | Sat (5/5 shift) | Sun (5/5 shift) | Mon (1/5 shift) | Tue (2/5 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 70% / 61% | 50% / 76% | 43% / 75% | 38% / 64% | 38% / 68% | 36% / 64% | 39% / 64% | 45% / 67% |
| last seen | 100% / 52% | 100% / 56% | 100% / 55% | 100% / 51% | 100% / 54% | 100% / 51% | 100% / 52% | 100% / 53% |
| llm_naive/not_told/look_off | 62% / 64% | 54% / 77% | 51% / 77% | 60% / 61% | 57% / 66% | 56% / 71% | 52% / 71% | 56% / 69% |
| llm_naive/told/look_off | 60% / 65% | 52% / 77% | 52% / 74% | 55% / 64% | 51% / 70% | 56% / 72% | 53% / 73% | 54% / 71% |
| most frequent | 3% / 64% | 3% / 91% | 4% / 62% | 2% / 60% | 2% / 43% | 5% / 69% | 7% / 73% | 4% / 68% |
| periodic | 10% / 53% | 12% / 46% | 30% / 66% | 35% / 49% | 36% / 56% | 42% / 61% | 41% / 60% | 30% / 57% |
| timetable | 3% / 64% | 3% / 91% | 4% / 62% | 2% / 60% | 2% / 43% | 4% / 62% | 5% / 62% | 3% / 64% |

## Coverage-matched selective accuracy (each agent answers its most confident 25 / 50 / 75% of the day's questions)

The fixed thresholds above compare different confidence scales; this compares agents at equal coverage.

| agent (coverage 25%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 65% | 78% | 80% | 76% | 79% | 75% | 76% | 74% |
| last seen | 52% | 56% | 61% | 44% | 51% | 55% | 55% | 54% |
| llm_naive/not_told/look_off | 81% | 82% | 78% | 64% | 68% | 82% | 78% | 75% |
| llm_naive/told/look_off | 81% | 82% | 76% | 68% | 71% | 81% | 84% | 77% |
| most frequent | 75% | 86% | 80% | 80% | 79% | 85% | 91% | 80% |
| periodic | 56% | 36% | 64% | 50% | 60% | 64% | 65% | 58% |
| timetable | 60% | 86% | 69% | 66% | 66% | 78% | 80% | 75% |

| agent (coverage 50%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 63% | 76% | 71% | 64% | 64% | 63% | 64% | 66% |
| last seen | 53% | 58% | 58% | 48% | 50% | 56% | 52% | 52% |
| llm_naive/not_told/look_off | 70% | 78% | 77% | 65% | 69% | 75% | 71% | 71% |
| llm_naive/told/look_off | 71% | 79% | 74% | 66% | 71% | 74% | 75% | 72% |
| most frequent | 60% | 79% | 68% | 57% | 62% | 60% | 64% | 64% |
| periodic | 58% | 47% | 57% | 49% | 52% | 60% | 58% | 50% |
| timetable | 59% | 66% | 64% | 62% | 58% | 72% | 76% | 65% |

| agent (coverage 75%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 60% | 62% | 64% | 58% | 57% | 56% | 60% | 60% |
| last seen | 55% | 59% | 58% | 52% | 53% | 54% | 55% | 53% |
| llm_naive/not_told/look_off | 59% | 68% | 68% | 58% | 61% | 65% | 66% | 63% |
| llm_naive/told/look_off | 60% | 68% | 66% | 58% | 59% | 64% | 68% | 63% |
| most frequent | 57% | 64% | 58% | 49% | 57% | 55% | 57% | 57% |
| periodic | 56% | 55% | 56% | 51% | 52% | 55% | 52% | 54% |
| timetable | 58% | 57% | 58% | 55% | 57% | 64% | 66% | 59% |

## Questions whose object moved since the robot's last round (52% of questions)

The robot's last full look is the patrol round before the question. 'still' questions are answered by recency almost by definition; the shift and the learning live in the 'moved' half. Cells: accuracy c=mean confidence.

| agent | Wed moved / still | Thu moved / still | Fri moved / still | Sat moved / still | Sun moved / still | Mon moved / still | Tue moved / still | moved all | still all |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 20% c83 / 91% c91 | 17% c67 / 82% c85 | 33% c65 / 80% c82 | 22% c65 / 79% c77 | 32% c64 / 72% c78 | 21% c62 / 80% c79 | 25% c63 / 78% c78 | 24% (n=1183, cov@0.7 47%, sel 28%) | 81% |
| last seen | 16% c98 / 94% c98 | 12% c98 / 94% c98 | 25% c98 / 93% c98 | 12% c98 / 95% c98 | 21% c98 / 88% c98 | 18% c98 / 94% c98 | 15% c98 / 93% c98 | 17% (n=1183, cov@0.7 100%, sel 17%) | 93% |
| llm_naive/not_told/look_off | 17% c85 / 94% c91 | 19% c79 / 93% c90 | 34% c79 / 89% c89 | 16% c85 / 94% c90 | 24% c84 / 84% c89 | 31% c81 / 89% c91 | 40% c82 / 88% c89 | 26% (n=1183, cov@0.7 77%, sel 26%) | 90% |
| llm_naive/told/look_off | 18% c83 / 94% c91 | 19% c78 / 94% c90 | 34% c80 / 89% c88 | 15% c83 / 93% c89 | 27% c82 / 83% c88 | 27% c83 / 89% c91 | 36% c82 / 88% c91 | 25% (n=1183, cov@0.7 75%, sel 26%) | 90% |
| most frequent | 8% c42 / 90% c49 | 18% c44 / 82% c57 | 24% c46 / 82% c59 | 20% c45 / 74% c61 | 22% c47 / 74% c61 | 26% c44 / 74% c65 | 24% c46 / 76% c65 | 20% (n=1183, cov@0.7 10%, sel 35%) | 79% |
| periodic | 12% c48 / 99% c43 | 15% c67 / 91% c56 | 29% c73 / 88% c68 | 18% c77 / 93% c70 | 26% c79 / 82% c73 | 26% c78 / 92% c79 | 26% c78 / 90% c76 | 22% (n=1183, cov@0.7 56%, sel 27%) | 91% |
| timetable | 16% c42 / 90% c44 | 28% c41 / 75% c47 | 31% c44 / 78% c48 | 33% c43 / 70% c52 | 40% c43 / 67% c50 | 51% c44 / 70% c50 | 55% c48 / 63% c55 | 36% (n=1183, cov@0.7 7%, sel 49%) | 73% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 0% (n=13) | 22% (n=305) | 30% (n=188) | 37% (n=244) | 46% (n=202) | 54% (n=138) | 56% (n=143) | 46% (n=102) | 70% (n=905) | 0.231 |
| last seen | - | - | - | - | - | - | - | - | 53% (n=2240) | 0.454 |
| llm_naive/not_told/look_off | - | 0% (n=1) | 13% (n=76) | 100% (n=1) | 40% (n=275) | 48% (n=25) | 43% (n=608) | 51% (n=158) | 72% (n=1096) | 0.295 |
| llm_naive/told/look_off | 0% (n=1) | - | 15% (n=71) | - | 33% (n=310) | 58% (n=31) | 43% (n=615) | 51% (n=156) | 73% (n=1056) | 0.295 |
| most frequent | 9% (n=58) | 26% (n=658) | 44% (n=505) | 40% (n=284) | 66% (n=244) | 78% (n=240) | 95% (n=166) | 100% (n=9) | 64% (n=76) | 0.063 |
| periodic | 30% (n=37) | 49% (n=263) | 63% (n=241) | 65% (n=353) | 53% (n=265) | 42% (n=206) | 41% (n=214) | 50% (n=176) | 60% (n=485) | 0.258 |
| timetable | 7% (n=30) | 42% (n=954) | 53% (n=544) | 62% (n=287) | 79% (n=205) | 79% (n=107) | 95% (n=37) | - | 64% (n=76) | 0.102 |

## Split by household kind (from the intro cards: any retired resident, or none)

Retired residents are home on weekdays too, so the weekend is not a routine shift for their household.

| household kind (n) | agent | Wed | Thu | Fri | Sat | Sun | Mon | Tue | weekday | weekend | drop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| working (13) | Perpetua* | 61% | 45% | 48% | 41% | 47% | 55% | 52% | 52% | 44% | +8 |
| working (13) | last seen | 61% | 55% | 52% | 48% | 47% | 56% | 50% | 55% | 48% | +7 |
| working (13) | llm_naive/not_told/look_off | 61% | 58% | 59% | 47% | 45% | 69% | 61% | 62% | 46% | +15 |
| working (13) | llm_naive/told/look_off | 61% | 58% | 59% | 47% | 42% | 64% | 58% | 60% | 45% | +15 |
| working (13) | most frequent | 58% | 44% | 52% | 42% | 47% | 47% | 58% | 52% | 45% | +7 |
| working (13) | periodic | 64% | 53% | 52% | 47% | 50% | 66% | 59% | 59% | 48% | +10 |
| working (13) | timetable | 58% | 52% | 55% | 41% | 52% | 75% | 45% | 57% | 46% | +11 |
| retired (7) | Perpetua* | 50% | 54% | 55% | 50% | 53% | 45% | 50% | 51% | 52% | -1 |
| retired (7) | last seen | 49% | 56% | 56% | 51% | 55% | 50% | 52% | 53% | 53% | -1 |
| retired (7) | llm_naive/not_told/look_off | 50% | 59% | 59% | 54% | 55% | 53% | 63% | 57% | 54% | +2 |
| retired (7) | llm_naive/told/look_off | 51% | 59% | 58% | 52% | 58% | 52% | 61% | 56% | 55% | +1 |
| retired (7) | most frequent | 43% | 54% | 49% | 45% | 47% | 47% | 47% | 48% | 46% | +2 |
| retired (7) | periodic | 49% | 56% | 56% | 54% | 54% | 53% | 56% | 54% | 54% | -0 |
| retired (7) | timetable | 48% | 54% | 52% | 52% | 53% | 55% | 62% | 54% | 53% | +1 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| Perpetua* | +2 | +6 | -6 (21) | 47 | 54 |
| last seen | +3 | +4 | -4 (21) | 51 | 56 |
| llm_naive/not_told/look_off | +6 | +7 | -6 (21) | 52 | 63 |
| llm_naive/told/look_off | +5 | +7 | -8 (21) | 51 | 61 |
| most frequent | +4 | +5 | -5 (21) | 45 | 52 |
| periodic | +3 | +2 | -7 (21) | 52 | 57 |
| timetable | +2 | +2 | -4 (21) | 50 | 59 |

Households with a major event on a scored day: 18/20; event days: {'hh_s10': [5], 'hh_s11': [3, 7], 'hh_s12': [4, 5, 7], 'hh_s13': [1, 2], 'hh_s14': [2, 3, 6], 'hh_s15': [1, 2, 3, 5], 'hh_s16': [4, 5, 6], 'hh_s17': [2, 6, 7], 'hh_s18': [], 'hh_s19': [2, 3, 4], 'hh_s20': [1, 3, 5], 'hh_s21': [5], 'hh_s22': [3], 'hh_s23': [6, 7], 'hh_s24': [1, 2, 4, 6], 'hh_s25': [1], 'hh_s26': [2, 3, 4, 6], 'hh_s27': [], 'hh_s28': [2, 7], 'hh_s29': [4, 5, 7]}

## Per household: Perpetua* (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 61% | 45% | 48% | **41%** | **47%** | 55% | 52% | [4, 5] | [5] |
| hh_s11 | 53% | 55% | **56%** | **48%** | **55%** | 47% | **47%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 45% | 50% | 59% | **59%** | **58%** | 41% | **69%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **58%** | **56%** | 52% | **52%** | **50%** | 38% | 39% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 45% | **53%** | **55%** | **41%** | **50%** | **55%** | 45% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 61% | 55% | 52% | **48%** | **47%** | 56% | 50% | [4, 5] | [5] |
| hh_s11 | 55% | 55% | **48%** | **50%** | **58%** | 47% | **50%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 47% | 58% | 59% | **55%** | **61%** | 45% | **53%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **48%** | **59%** | 58% | **58%** | **55%** | 53% | 53% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **53%** | **58%** | **42%** | **48%** | **55%** | 53% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: llm_naive/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 61% | 58% | 59% | **47%** | **45%** | 69% | 61% | [4, 5] | [5] |
| hh_s11 | 55% | 56% | **48%** | **55%** | **55%** | 47% | **62%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 48% | 62% | 61% | **58%** | **66%** | 55% | **59%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **52%** | **61%** | 64% | **61%** | **55%** | 55% | 64% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **55%** | **61%** | **41%** | **47%** | **56%** | 67% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: llm_naive/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 61% | 58% | 59% | **47%** | **42%** | 64% | 58% | [4, 5] | [5] |
| hh_s11 | 55% | 56% | **50%** | **52%** | **56%** | 45% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 48% | 62% | 61% | **59%** | **72%** | 52% | **62%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **55%** | **66%** | 62% | **58%** | **56%** | 58% | 62% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **53%** | **58%** | **41%** | **47%** | **53%** | 55% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 44% | 52% | **42%** | **47%** | 47% | 58% | [4, 5] | [5] |
| hh_s11 | 44% | 52% | **44%** | **53%** | **50%** | 41% | **47%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 41% | 55% | 53% | **47%** | **53%** | 47% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **47%** | **61%** | 52% | **44%** | **44%** | 47% | 50% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 39% | **50%** | **48%** | **38%** | **42%** | **53%** | 33% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 64% | 53% | 52% | **47%** | **50%** | 66% | 59% | [4, 5] | [5] |
| hh_s11 | 52% | 55% | **48%** | **56%** | **55%** | 45% | **52%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 48% | 53% | 56% | **59%** | **66%** | 48% | **61%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **48%** | **61%** | 56% | **59%** | **53%** | 58% | 58% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **55%** | **62%** | **42%** | **42%** | **59%** | 53% | [2, 3, 4, 5, 6] | [2, 3, 6] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 52% | 55% | **41%** | **52%** | 75% | 45% | [4, 5] | [5] |
| hh_s11 | 47% | 58% | **45%** | **61%** | **50%** | 56% | **50%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 47% | 53% | 58% | **48%** | **69%** | 56% | **78%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **53%** | **61%** | 48% | **56%** | **48%** | 55% | 72% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 44% | **44%** | **55%** | **44%** | **45%** | **53%** | 50% | [2, 3, 4, 5, 6] | [2, 3, 6] |
