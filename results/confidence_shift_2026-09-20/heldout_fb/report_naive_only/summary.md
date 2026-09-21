# Households hh_s12, hh_s13: naive LLM and classical agents (no mixture run)

2 households, 7 agents, 6272 agent-question records. Shift days per household (weekend + major event days): hh_s12 [4, 5, 7]; hh_s13 [1, 2, 4, 5].

Questions per household per agent: hh_s12 448, hh_s13 448.

Object classes in the questions: glass 11%, mug 9%, towel 7%, vacuum_cleaner 6%, plate 5%, blanket 4%, skincare 4%, remote 4%, shopping_bag 4%, dog_food_bag 3%, bowl 3%, dog_bowl 3%, phone 3%, duster 3%, toiletry_bag 3%, water_bottle 3%, ironing_board 2%, glasses 2%, laundry_basket 2%, detergent 2%, pot 2%, snack_bowl 2%, razor 2%, charger 1%, watering_can 1%, pan 1%, iron 1%, kitchen_knife 1%, recipe_book 1%, guitar 1%, hair_dryer 1%, spatula 1%, board_game 1%, cutting_board 1%, headphones 1%, puzzle_box 0%, book 0%, laptop 0%, dog_toy 0%, yoga_mat 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (1/2 shift) | Thu (1/2 shift) | Fri (0/2 shift) | Sat (2/2 shift) | Sun (2/2 shift) | Mon (0/2 shift) | Tue (1/2 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 52% | 53% | 55% | 55% | 54% | 39% | 54% | 52% |
| last seen | 48% | 59% | 59% | 56% | 58% | 49% | 53% | 54% |
| llm_naive/not_told/look_off | 50% | 62% | 62% | 59% | 60% | 55% | 62% | 59% |
| llm_naive/told/look_off | 52% | 64% | 62% | 59% | 64% | 55% | 62% | 60% |
| most frequent | 44% | 58% | 52% | 45% | 48% | 47% | 54% | 50% |
| periodic | 48% | 57% | 56% | 59% | 59% | 53% | 59% | 56% |
| timetable | 50% | 57% | 53% | 52% | 59% | 55% | 75% | 57% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (1/2 shift) | Thu (1/2 shift) | Fri (0/2 shift) | Sat (2/2 shift) | Sun (2/2 shift) | Mon (0/2 shift) | Tue (1/2 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 95% / 54% | 84% / 60% | 82% / 65% | 81% / 63% | 81% / 61% | 77% / 47% | 75% / 67% | 82% / 59% |
| last seen | 100% / 48% | 100% / 59% | 100% / 59% | 100% / 56% | 100% / 58% | 100% / 49% | 100% / 53% | 100% / 54% |
| llm_naive/not_told/look_off | 99% / 50% | 96% / 64% | 98% / 64% | 98% / 61% | 99% / 61% | 98% / 56% | 100% / 62% | 98% / 60% |
| llm_naive/told/look_off | 96% / 53% | 95% / 67% | 98% / 63% | 93% / 61% | 100% / 64% | 98% / 55% | 98% / 63% | 97% / 61% |
| most frequent | 24% / 84% | 52% / 76% | 51% / 71% | 62% / 56% | 56% / 68% | 52% / 55% | 52% / 71% | 50% / 67% |
| periodic | 32% / 63% | 65% / 46% | 84% / 57% | 84% / 59% | 88% / 60% | 89% / 54% | 93% / 58% | 76% / 56% |
| timetable | 16% / 75% | 30% / 84% | 30% / 69% | 48% / 59% | 33% / 67% | 30% / 72% | 51% / 80% | 34% / 72% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (1/2 shift) | Thu (1/2 shift) | Fri (0/2 shift) | Sat (2/2 shift) | Sun (2/2 shift) | Mon (0/2 shift) | Tue (1/2 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 73% / 59% | 62% / 75% | 60% / 71% | 66% / 65% | 64% / 70% | 59% / 49% | 56% / 68% | 63% / 65% |
| last seen | 100% / 48% | 100% / 59% | 100% / 59% | 100% / 56% | 100% / 58% | 100% / 49% | 100% / 53% | 100% / 54% |
| llm_naive/not_told/look_off | 85% / 54% | 84% / 69% | 81% / 69% | 90% / 60% | 90% / 63% | 84% / 59% | 89% / 64% | 86% / 62% |
| llm_naive/told/look_off | 80% / 57% | 83% / 70% | 82% / 68% | 86% / 63% | 85% / 64% | 86% / 57% | 88% / 65% | 84% / 63% |
| most frequent | 6% / 75% | 10% / 85% | 23% / 79% | 26% / 88% | 35% / 87% | 27% / 74% | 29% / 89% | 22% / 84% |
| periodic | 19% / 38% | 33% / 26% | 51% / 54% | 52% / 55% | 56% / 56% | 64% / 51% | 61% / 55% | 48% / 50% |
| timetable | 6% / 75% | 4% / 80% | 10% / 62% | 12% / 88% | 14% / 72% | 8% / 70% | 19% / 83% | 10% / 77% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (1/2 shift) | Thu (1/2 shift) | Fri (0/2 shift) | Sat (2/2 shift) | Sun (2/2 shift) | Mon (0/2 shift) | Tue (1/2 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 68% / 60% | 49% / 81% | 48% / 80% | 49% / 68% | 48% / 79% | 43% / 60% | 43% / 71% | 50% / 71% |
| last seen | 100% / 48% | 100% / 59% | 100% / 59% | 100% / 56% | 100% / 58% | 100% / 49% | 100% / 53% | 100% / 54% |
| llm_naive/not_told/look_off | 64% / 61% | 55% / 80% | 50% / 80% | 71% / 64% | 59% / 74% | 57% / 66% | 54% / 71% | 59% / 70% |
| llm_naive/told/look_off | 58% / 65% | 51% / 83% | 51% / 75% | 63% / 68% | 54% / 80% | 56% / 67% | 56% / 74% | 56% / 73% |
| most frequent | 5% / 67% | 2% / 67% | 3% / 75% | 2% / 100% | 1% / 0% | 5% / 57% | 12% / 73% | 4% / 69% |
| periodic | 15% / 47% | 10% / 31% | 27% / 63% | 32% / 54% | 31% / 57% | 39% / 54% | 47% / 62% | 29% / 56% |
| timetable | 5% / 67% | 2% / 67% | 3% / 75% | 2% / 100% | 1% / 0% | 3% / 25% | 7% / 56% | 3% / 60% |

## Coverage-matched selective accuracy (each agent answers its most confident 25 / 50 / 75% of the day's questions)

The fixed thresholds above compare different confidence scales; this compares agents at equal coverage.

| agent (coverage 25%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 50% | 88% | 88% | 84% | 84% | 78% | 84% | 76% |
| last seen | 47% | 69% | 69% | 59% | 62% | 59% | 53% | 55% |
| llm_naive/not_told/look_off | 69% | 84% | 84% | 75% | 78% | 69% | 75% | 76% |
| llm_naive/told/look_off | 72% | 84% | 81% | 75% | 84% | 59% | 88% | 77% |
| most frequent | 81% | 81% | 81% | 91% | 88% | 75% | 88% | 81% |
| periodic | 53% | 22% | 66% | 50% | 62% | 59% | 69% | 57% |
| timetable | 56% | 88% | 72% | 69% | 75% | 72% | 78% | 75% |

| agent (coverage 50%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 56% | 80% | 78% | 69% | 77% | 56% | 70% | 71% |
| last seen | 47% | 56% | 61% | 55% | 59% | 47% | 55% | 54% |
| llm_naive/not_told/look_off | 67% | 81% | 80% | 73% | 78% | 67% | 70% | 75% |
| llm_naive/told/look_off | 67% | 83% | 77% | 75% | 80% | 66% | 75% | 73% |
| most frequent | 58% | 80% | 70% | 67% | 75% | 55% | 72% | 67% |
| periodic | 52% | 34% | 55% | 53% | 53% | 53% | 62% | 50% |
| timetable | 56% | 66% | 61% | 61% | 66% | 69% | 80% | 67% |

| agent (coverage 75%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 57% | 68% | 69% | 65% | 62% | 47% | 67% | 62% |
| last seen | 53% | 64% | 61% | 59% | 64% | 55% | 59% | 55% |
| llm_naive/not_told/look_off | 58% | 75% | 71% | 65% | 68% | 61% | 64% | 64% |
| llm_naive/told/look_off | 58% | 72% | 69% | 62% | 69% | 60% | 66% | 65% |
| most frequent | 55% | 66% | 66% | 54% | 60% | 54% | 64% | 60% |
| periodic | 57% | 51% | 55% | 58% | 61% | 54% | 55% | 56% |
| timetable | 57% | 59% | 61% | 57% | 61% | 64% | 76% | 62% |

## Questions whose object moved since the robot's last round (52% of questions)

The robot's last full look is the patrol round before the question. 'still' questions are answered by recency almost by definition; the shift and the learning live in the 'moved' half. Cells: accuracy c=mean confidence.

| agent | Wed moved / still | Thu moved / still | Fri moved / still | Sat moved / still | Sun moved / still | Mon moved / still | Tue moved / still | moved all | still all |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 19% c82 / 93% c92 | 22% c65 / 76% c87 | 31% c70 / 79% c81 | 27% c73 / 85% c84 | 27% c68 / 79% c85 | 13% c68 / 71% c81 | 36% c66 / 76% c81 | 25% (n=456, cov@0.7 53%, sel 32%) | 80% |
| last seen | 11% c98 / 95% c98 | 13% c98 / 92% c98 | 23% c98 / 92% c98 | 20% c98 / 95% c98 | 21% c98 / 92% c98 | 13% c98 / 93% c98 | 26% c98 / 86% c98 | 18% (n=456, cov@0.7 100%, sel 18%) | 92% |
| llm_naive/not_told/look_off | 15% c83 / 95% c91 | 22% c79 / 91% c91 | 37% c81 / 86% c89 | 26% c86 / 95% c92 | 27% c84 / 91% c91 | 29% c82 / 86% c91 | 47% c86 / 79% c90 | 29% (n=456, cov@0.7 78%, sel 29%) | 89% |
| llm_naive/told/look_off | 18% c80 / 95% c91 | 26% c77 / 92% c91 | 37% c82 / 85% c88 | 24% c82 / 95% c91 | 34% c82 / 92% c91 | 27% c83 / 88% c91 | 49% c83 / 79% c91 | 31% (n=456, cov@0.7 74%, sel 29%) | 90% |
| most frequent | 8% c41 / 89% c49 | 15% c46 / 89% c56 | 26% c50 / 77% c58 | 21% c45 / 71% c65 | 15% c45 / 80% c65 | 26% c45 / 72% c64 | 33% c49 / 79% c64 | 21% (n=456, cov@0.7 10%, sel 35%) | 80% |
| periodic | 11% c48 / 96% c46 | 19% c72 / 85% c54 | 21% c74 / 89% c69 | 27% c77 / 94% c66 | 26% c78 / 91% c70 | 24% c75 / 88% c79 | 40% c81 / 83% c76 | 24% (n=456, cov@0.7 58%, sel 30%) | 89% |
| timetable | 19% c42 / 89% c43 | 31% c42 / 76% c46 | 31% c46 / 74% c46 | 36% c47 / 69% c54 | 39% c43 / 77% c50 | 44% c43 / 69% c50 | 76% c50 / 74% c57 | 40% (n=456, cov@0.7 8%, sel 47%) | 75% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 0% (n=1) | 16% (n=101) | 18% (n=57) | 34% (n=79) | 46% (n=94) | 40% (n=45) | 47% (n=74) | 43% (n=44) | 74% (n=401) | 0.256 |
| last seen | - | - | - | - | - | - | - | - | 54% (n=896) | 0.437 |
| llm_naive/not_told/look_off | - | - | 0% (n=16) | 100% (n=1) | 39% (n=106) | 50% (n=12) | 46% (n=235) | 43% (n=69) | 74% (n=457) | 0.284 |
| llm_naive/told/look_off | - | - | 15% (n=27) | - | 45% (n=114) | 64% (n=14) | 44% (n=243) | 56% (n=63) | 75% (n=435) | 0.263 |
| most frequent | 18% (n=17) | 22% (n=252) | 49% (n=180) | 46% (n=142) | 65% (n=105) | 79% (n=91) | 97% (n=70) | 100% (n=9) | 60% (n=30) | 0.072 |
| periodic | 32% (n=25) | 48% (n=85) | 67% (n=102) | 70% (n=165) | 61% (n=90) | 39% (n=87) | 45% (n=84) | 43% (n=61) | 60% (n=197) | 0.263 |
| timetable | 9% (n=11) | 47% (n=366) | 57% (n=215) | 66% (n=128) | 74% (n=82) | 82% (n=44) | 90% (n=20) | - | 60% (n=30) | 0.132 |

## Split by household kind (from the intro cards: any retired resident, or none)

Retired residents are home on weekdays too, so the weekend is not a routine shift for their household.

| household kind (n) | agent | Wed | Thu | Fri | Sat | Sun | Mon | Tue | weekday | weekend | drop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| working (13) | Perpetua* | - | - | - | - | - | - | - | - | - | +nan |
| working (13) | last seen | - | - | - | - | - | - | - | - | - | +nan |
| working (13) | llm_naive/not_told/look_off | - | - | - | - | - | - | - | - | - | +nan |
| working (13) | llm_naive/told/look_off | - | - | - | - | - | - | - | - | - | +nan |
| working (13) | most frequent | - | - | - | - | - | - | - | - | - | +nan |
| working (13) | periodic | - | - | - | - | - | - | - | - | - | +nan |
| working (13) | timetable | - | - | - | - | - | - | - | - | - | +nan |
| retired (7) | Perpetua* | 52% | 53% | 55% | 55% | 54% | 39% | 54% | 51% | 55% | -4 |
| retired (7) | last seen | 48% | 59% | 59% | 56% | 58% | 49% | 53% | 53% | 57% | -4 |
| retired (7) | llm_naive/not_told/look_off | 50% | 62% | 62% | 59% | 60% | 55% | 62% | 58% | 60% | -2 |
| retired (7) | llm_naive/told/look_off | 52% | 64% | 62% | 59% | 64% | 55% | 62% | 59% | 61% | -2 |
| retired (7) | most frequent | 44% | 58% | 52% | 45% | 48% | 47% | 54% | 51% | 47% | +4 |
| retired (7) | periodic | 48% | 57% | 56% | 59% | 59% | 53% | 59% | 55% | 59% | -5 |
| retired (7) | timetable | 50% | 57% | 53% | 52% | 59% | 55% | 75% | 58% | 55% | +3 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| Perpetua* | +4 | +0 | -13 (21) | 39 | 55 |
| last seen | +11 | +2 | -9 (21) | 48 | 59 |
| llm_naive/not_told/look_off | +12 | +3 | -7 (21) | 50 | 62 |
| llm_naive/told/look_off | +10 | +3 | -11 (21) | 52 | 64 |
| most frequent | +9 | +7 | -12 (21) | 44 | 58 |
| periodic | +8 | -3 | -12 (21) | 48 | 59 |
| timetable | +3 | +1 | -15 (21) | 50 | 75 |

Households with a major event on a scored day: 18/20; event days: {'hh_s10': [5], 'hh_s11': [3, 7], 'hh_s12': [4, 5, 7], 'hh_s13': [1, 2], 'hh_s14': [2, 3, 6], 'hh_s15': [1, 2, 3, 5], 'hh_s16': [4, 5, 6], 'hh_s17': [2, 6, 7], 'hh_s18': [], 'hh_s19': [2, 3, 4], 'hh_s20': [1, 3, 5], 'hh_s21': [5], 'hh_s22': [3], 'hh_s23': [6, 7], 'hh_s24': [1, 2, 4, 6], 'hh_s25': [1], 'hh_s26': [2, 3, 4, 6], 'hh_s27': [], 'hh_s28': [2, 7], 'hh_s29': [4, 5, 7]}

## Per household: Perpetua* (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s12 | 45% | 50% | 59% | **59%** | **58%** | 41% | **69%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **58%** | **56%** | 52% | **52%** | **50%** | 38% | 39% | [1, 2, 4, 5] | [1, 2] |

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s12 | 47% | 58% | 59% | **55%** | **61%** | 45% | **53%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **48%** | **59%** | 58% | **58%** | **55%** | 53% | 53% | [1, 2, 4, 5] | [1, 2] |

## Per household: llm_naive/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s12 | 48% | 62% | 61% | **58%** | **66%** | 55% | **59%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **52%** | **61%** | 64% | **61%** | **55%** | 55% | 64% | [1, 2, 4, 5] | [1, 2] |

## Per household: llm_naive/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s12 | 48% | 62% | 61% | **59%** | **72%** | 52% | **62%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **55%** | **66%** | 62% | **58%** | **56%** | 58% | 62% | [1, 2, 4, 5] | [1, 2] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s12 | 41% | 55% | 53% | **47%** | **53%** | 47% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **47%** | **61%** | 52% | **44%** | **44%** | 47% | 50% | [1, 2, 4, 5] | [1, 2] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s12 | 48% | 53% | 56% | **59%** | **66%** | 48% | **61%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **48%** | **61%** | 56% | **59%** | **53%** | 58% | 58% | [1, 2, 4, 5] | [1, 2] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s12 | 47% | 53% | 58% | **48%** | **69%** | 56% | **78%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **53%** | **61%** | 48% | **56%** | **48%** | 55% | 72% | [1, 2, 4, 5] | [1, 2] |
