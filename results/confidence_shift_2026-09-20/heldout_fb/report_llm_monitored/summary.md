# Same, confidence = top_prob x own running hit rate on today's feedback

8 households, 10 agents, 35840 agent-question records. Shift days per household (weekend + major event days): hh_s10 [4, 5]; hh_s11 [3, 4, 5, 7]; hh_s12 [4, 5, 7]; hh_s13 [1, 2, 4, 5]; hh_s14 [2, 3, 4, 5, 6]; hh_s18 [4, 5]; hh_s19 [2, 3, 4, 5]; hh_s25 [1, 4, 5].

Questions per household per agent: hh_s10 448, hh_s11 448, hh_s12 448, hh_s13 448, hh_s14 448, hh_s18 448, hh_s19 448, hh_s25 448.

Object classes in the questions: glass 11%, towel 7%, mug 6%, plate 5%, vacuum_cleaner 4%, blanket 4%, water_bottle 3%, glasses 3%, shopping_bag 3%, phone 3%, snack_bowl 3%, bowl 3%, dog_food_bag 3%, dog_bowl 3%, toiletry_bag 2%, laundry_basket 2%, duster 2%, detergent 2%, razor 2%, skincare 2%, charger 2%, laptop 2%, ironing_board 2%, remote 2%, iron 1%, watering_can 1%, headphones 1%, vitamins 1%, spatula 1%, pan 1%, tablet 1%, cutting_board 1%, kitchen_knife 1%, pen 1%, pot 1%, serving_dish 1%, notebook 1%, guitar 1%, hair_dryer 1%, recipe_book 1%, book 1%, mouse 0%, gardening_gloves 0%, journal 0%, yoga_mat 0%, toolbox 0%, board_game 0%, dog_toy 0%, meditation_cushion 0%, pencil_case 0%, sketchbook 0%, speaker 0%, magazine 0%, puzzle_box 0%, baking_tray 0%, mixing_bowl 0%, controller 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (2/8 shift) | Thu (3/8 shift) | Fri (3/8 shift) | Sat (8/8 shift) | Sun (8/8 shift) | Mon (1/8 shift) | Tue (2/8 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 54% | 55% | 56% | 49% | 50% | 49% | 55% | 53% |
| last seen | 54% | 57% | 55% | 51% | 52% | 54% | 56% | 54% |
| llm_longleaf/not_told/look_off | 54% | 55% | 58% | 54% | 53% | 60% | 64% | 57% |
| llm_longleaf/told/look_off | 54% | 55% | 58% | 53% | 53% | 59% | 64% | 57% |
| llm_naive/not_told/look_off | 55% | 59% | 61% | 52% | 52% | 58% | 68% | 58% |
| llm_naive/told/look_off | 55% | 59% | 60% | 52% | 53% | 57% | 65% | 57% |
| most frequent | 47% | 54% | 52% | 45% | 46% | 49% | 52% | 49% |
| periodic | 52% | 57% | 56% | 52% | 51% | 57% | 59% | 55% |
| timetable | 50% | 55% | 57% | 51% | 52% | 60% | 64% | 56% |
| timetable wd/we, honest empty bin | 55% | 56% | 58% | 50% | 56% | 58% | 63% | 57% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (2/8 shift) | Thu (3/8 shift) | Fri (3/8 shift) | Sat (8/8 shift) | Sun (8/8 shift) | Mon (1/8 shift) | Tue (2/8 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 50% / 64% | 54% / 74% | 43% / 71% | 35% / 66% | 32% / 63% | 32% / 69% | 40% / 73% | 41% / 69% |
| last seen | 68% / 54% | 94% / 56% | 88% / 55% | 69% / 52% | 68% / 51% | 88% / 52% | 82% / 54% | 80% / 53% |
| llm_longleaf/not_told/look_off | 0% / 0% | 0% / 100% | 3% / 100% | 0% / 100% | 0% / - | 1% / 100% | 3% / 100% | 1% / 97% |
| llm_longleaf/told/look_off | 0% / 0% | 0% / 100% | 3% / 100% | 0% / 100% | 0% / - | 0% / 100% | 3% / 100% | 1% / 97% |
| llm_naive/not_told/look_off | 47% / 60% | 71% / 66% | 72% / 68% | 54% / 57% | 46% / 54% | 64% / 63% | 78% / 71% | 62% / 64% |
| llm_naive/told/look_off | 44% / 62% | 71% / 66% | 68% / 66% | 53% / 59% | 45% / 57% | 60% / 64% | 73% / 70% | 59% / 64% |
| most frequent | 3% / 62% | 5% / 88% | 10% / 76% | 4% / 84% | 5% / 68% | 8% / 88% | 16% / 94% | 7% / 84% |
| periodic | 6% / 39% | 21% / 50% | 35% / 58% | 27% / 53% | 27% / 43% | 46% / 54% | 46% / 59% | 30% / 53% |
| timetable | 2% / 50% | 4% / 90% | 9% / 82% | 3% / 73% | 4% / 67% | 5% / 79% | 14% / 84% | 6% / 80% |
| timetable wd/we, honest empty bin | 2% / 55% | 3% / 93% | 6% / 72% | 2% / 38% | 2% / 30% | 4% / 73% | 6% / 75% | 4% / 69% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/8 shift) | Thu (3/8 shift) | Fri (3/8 shift) | Sat (8/8 shift) | Sun (8/8 shift) | Mon (1/8 shift) | Tue (2/8 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 6% / 58% | 7% / 59% | 6% / 75% | 1% / 50% | 0% / 50% | 0% / 100% | 6% / 80% | 4% / 67% |
| last seen | 8% / 50% | 5% / 41% | 15% / 55% | 4% / 43% | 1% / 0% | 4% / 52% | 16% / 61% | 8% / 52% |
| llm_longleaf/not_told/look_off | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| llm_longleaf/told/look_off | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| llm_naive/not_told/look_off | 3% / 73% | 5% / 65% | 10% / 81% | 2% / 33% | 0% / 0% | 4% / 63% | 17% / 83% | 6% / 75% |
| llm_naive/told/look_off | 3% / 65% | 1% / 75% | 11% / 78% | 1% / 57% | 0% / 100% | 4% / 77% | 18% / 77% | 5% / 76% |
| most frequent | 0% / - | 0% / 100% | 1% / 67% | 0% / - | 0% / - | 0% / - | 0% / 0% | 0% / 60% |
| periodic | 0% / 0% | 2% / 33% | 4% / 70% | 1% / 33% | 1% / 50% | 3% / 38% | 7% / 63% | 2% / 54% |
| timetable | 0% / - | 1% / 67% | 1% / 33% | 0% / - | 0% / - | 1% / 80% | 3% / 76% | 1% / 71% |
| timetable wd/we, honest empty bin | 0% / 0% | 1% / 67% | 1% / 57% | 0% / 50% | 0% / 0% | 1% / 100% | 2% / 62% | 1% / 62% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/8 shift) | Thu (3/8 shift) | Fri (3/8 shift) | Sat (8/8 shift) | Sun (8/8 shift) | Mon (1/8 shift) | Tue (2/8 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| last seen | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| llm_longleaf/not_told/look_off | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| llm_longleaf/told/look_off | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| llm_naive/not_told/look_off | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| llm_naive/told/look_off | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| most frequent | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| periodic | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| timetable | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| timetable wd/we, honest empty bin | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |

## Coverage-matched selective accuracy (each agent answers its most confident 25 / 50 / 75% of the day's questions)

The fixed thresholds above compare different confidence scales; this compares agents at equal coverage.

| agent (coverage 25%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 59% | 80% | 73% | 62% | 62% | 70% | 72% | 68% |
| last seen | 51% | 52% | 58% | 50% | 42% | 52% | 57% | 54% |
| llm_longleaf/not_told/look_off | 61% | 73% | 80% | 62% | 69% | 80% | 85% | 76% |
| llm_longleaf/told/look_off | 61% | 73% | 81% | 62% | 69% | 81% | 86% | 76% |
| llm_naive/not_told/look_off | 63% | 73% | 75% | 52% | 62% | 74% | 75% | 71% |
| llm_naive/told/look_off | 65% | 73% | 73% | 51% | 63% | 70% | 77% | 71% |
| most frequent | 62% | 83% | 77% | 64% | 74% | 78% | 90% | 78% |
| periodic | 55% | 49% | 62% | 54% | 45% | 55% | 58% | 55% |
| timetable | 61% | 79% | 72% | 64% | 66% | 75% | 82% | 74% |
| timetable wd/we, honest empty bin | 58% | 68% | 78% | 53% | 52% | 73% | 80% | 69% |

| agent (coverage 50%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 64% | 76% | 73% | 64% | 61% | 66% | 70% | 67% |
| last seen | 52% | 57% | 56% | 51% | 51% | 51% | 55% | 53% |
| llm_longleaf/not_told/look_off | 63% | 70% | 77% | 61% | 66% | 72% | 80% | 69% |
| llm_longleaf/told/look_off | 63% | 70% | 77% | 61% | 66% | 72% | 80% | 69% |
| llm_naive/not_told/look_off | 61% | 70% | 71% | 58% | 55% | 65% | 72% | 65% |
| llm_naive/told/look_off | 62% | 68% | 68% | 60% | 56% | 61% | 75% | 65% |
| most frequent | 61% | 77% | 71% | 58% | 60% | 66% | 75% | 65% |
| periodic | 58% | 52% | 55% | 48% | 47% | 54% | 61% | 54% |
| timetable | 57% | 70% | 69% | 61% | 57% | 71% | 79% | 66% |
| timetable wd/we, honest empty bin | 54% | 59% | 66% | 51% | 55% | 65% | 74% | 62% |

| agent (coverage 75%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 57% | 65% | 65% | 58% | 55% | 59% | 63% | 61% |
| last seen | 54% | 54% | 54% | 49% | 51% | 52% | 54% | 53% |
| llm_longleaf/not_told/look_off | 59% | 63% | 66% | 58% | 58% | 66% | 73% | 63% |
| llm_longleaf/told/look_off | 59% | 63% | 66% | 58% | 59% | 65% | 73% | 63% |
| llm_naive/not_told/look_off | 61% | 65% | 67% | 56% | 57% | 62% | 71% | 63% |
| llm_naive/told/look_off | 62% | 66% | 64% | 57% | 57% | 61% | 69% | 63% |
| most frequent | 56% | 63% | 61% | 50% | 51% | 56% | 61% | 57% |
| periodic | 55% | 57% | 57% | 50% | 50% | 55% | 58% | 55% |
| timetable | 57% | 61% | 63% | 57% | 55% | 65% | 72% | 61% |
| timetable wd/we, honest empty bin | 55% | 58% | 61% | 49% | 56% | 61% | 71% | 58% |

## Questions whose object moved since the robot's last round (52% of questions)

The robot's last full look is the patrol round before the question. 'still' questions are answered by recency almost by definition; the shift and the learning live in the 'moved' half. Cells: accuracy c=mean confidence.

| agent | Wed moved / still | Thu moved / still | Fri moved / still | Sat moved / still | Sun moved / still | Mon moved / still | Tue moved / still | moved all | still all |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 19% c48 / 92% c52 | 26% c43 / 83% c54 | 33% c40 / 84% c51 | 22% c37 / 81% c43 | 29% c36 / 74% c44 | 22% c36 / 80% c46 | 27% c38 / 82% c48 | 26% (n=1875, cov@0.7 3%, sel 13%) | 82% |
| last seen | 17% c56 / 95% c55 | 17% c61 / 95% c60 | 25% c60 / 92% c62 | 14% c55 / 94% c54 | 20% c55 / 89% c54 | 17% c58 / 93% c58 | 18% c60 / 95% c59 | 18% (n=1875, cov@0.7 7%, sel 9%) | 93% |
| llm_longleaf/not_told/look_off | 18% c16 / 94% c18 | 29% c18 / 80% c22 | 35% c20 / 85% c27 | 29% c18 / 83% c22 | 33% c18 / 76% c23 | 40% c20 / 82% c25 | 49% c21 / 80% c30 | 33% (n=1875, cov@0.7 0%, sel -) | 83% |
| llm_longleaf/told/look_off | 18% c16 / 94% c18 | 29% c18 / 80% c22 | 36% c20 / 85% c27 | 29% c18 / 82% c22 | 33% c19 / 77% c23 | 40% c20 / 81% c25 | 49% c21 / 80% c30 | 33% (n=1875, cov@0.7 0%, sel -) | 83% |
| llm_naive/not_told/look_off | 19% c48 / 95% c52 | 23% c51 / 94% c57 | 37% c53 / 89% c60 | 18% c48 / 92% c51 | 25% c47 / 84% c50 | 32% c51 / 88% c56 | 45% c56 / 91% c60 | 28% (n=1875, cov@0.7 4%, sel 32%) | 90% |
| llm_naive/told/look_off | 20% c48 / 94% c52 | 22% c51 / 94% c57 | 35% c52 / 89% c59 | 17% c48 / 92% c51 | 26% c47 / 85% c51 | 29% c51 / 89% c55 | 40% c55 / 90% c60 | 27% (n=1875, cov@0.7 3%, sel 30%) | 91% |
| most frequent | 7% c22 / 91% c25 | 19% c25 / 86% c33 | 25% c27 / 85% c37 | 14% c24 / 80% c32 | 21% c24 / 76% c32 | 24% c25 / 78% c36 | 25% c26 / 79% c39 | 19% (n=1875, cov@0.7 0%, sel 0%) | 82% |
| periodic | 11% c26 / 98% c24 | 20% c42 / 92% c35 | 29% c45 / 88% c43 | 18% c43 / 92% c38 | 23% c43 / 84% c39 | 26% c49 / 91% c46 | 26% c48 / 92% c47 | 22% (n=1875, cov@0.7 2%, sel 18%) | 91% |
| timetable | 14% c22 / 90% c23 | 29% c24 / 80% c28 | 35% c26 / 82% c32 | 31% c24 / 75% c29 | 38% c24 / 68% c28 | 51% c27 / 70% c30 | 57% c31 / 71% c37 | 36% (n=1875, cov@0.7 1%, sel 62%) | 77% |
| timetable wd/we, honest empty bin | 19% c20 / 95% c18 | 28% c22 / 83% c22 | 36% c25 / 85% c26 | 13% c19 / 94% c17 | 31% c21 / 86% c20 | 42% c25 / 77% c26 | 48% c27 / 78% c31 | 31% (n=1875, cov@0.7 1%, sel 55%) | 85% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 23% (n=330) | 39% (n=1134) | 55% (n=653) | 68% (n=828) | 71% (n=500) | 66% (n=137) | 100% (n=2) | - | - | 0.093 |
| last seen | - | 65% (n=48) | 56% (n=684) | 54% (n=1421) | 53% (n=1156) | 51% (n=251) | 67% (n=24) | - | - | 0.079 |
| llm_longleaf/not_told/look_off | 45% (n=1896) | 68% (n=1532) | 89% (n=122) | 96% (n=26) | 100% (n=8) | - | - | - | - | 0.357 |
| llm_longleaf/told/look_off | 45% (n=1902) | 68% (n=1531) | 89% (n=118) | 96% (n=25) | 100% (n=8) | - | - | - | - | 0.357 |
| llm_naive/not_told/look_off | 12% (n=26) | 36% (n=446) | 55% (n=904) | 60% (n=1220) | 67% (n=780) | 74% (n=189) | 84% (n=19) | - | - | 0.052 |
| llm_naive/told/look_off | 14% (n=14) | 32% (n=459) | 55% (n=988) | 59% (n=1125) | 68% (n=802) | 74% (n=180) | 94% (n=16) | - | - | 0.051 |
| most frequent | 27% (n=1026) | 51% (n=1886) | 76% (n=414) | 86% (n=183) | 80% (n=70) | 60% (n=5) | - | - | - | 0.205 |
| periodic | 51% (n=345) | 57% (n=1428) | 54% (n=740) | 51% (n=606) | 57% (n=376) | 51% (n=83) | 100% (n=6) | - | - | 0.181 |
| timetable | 42% (n=1169) | 58% (n=1894) | 75% (n=318) | 84% (n=121) | 74% (n=54) | 85% (n=20) | 38% (n=8) | - | - | 0.285 |
| timetable wd/we, honest empty bin | 52% (n=1934) | 60% (n=1383) | 81% (n=140) | 75% (n=59) | 64% (n=39) | 64% (n=25) | 50% (n=4) | - | - | 0.341 |

## Split by household kind (from the intro cards: any retired resident, or none)

Retired residents are home on weekdays too, so the weekend is not a routine shift for their household.

| household kind (n) | agent | Wed | Thu | Fri | Sat | Sun | Mon | Tue | weekday | weekend | drop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| working (13) | Perpetua* | 57% | 57% | 57% | 48% | 47% | 54% | 60% | 57% | 47% | +10 |
| working (13) | last seen | 59% | 58% | 55% | 50% | 48% | 57% | 60% | 58% | 49% | +9 |
| working (13) | llm_longleaf/not_told/look_off | 59% | 58% | 59% | 54% | 54% | 62% | 66% | 61% | 54% | +7 |
| working (13) | llm_longleaf/told/look_off | 59% | 58% | 60% | 53% | 54% | 62% | 66% | 61% | 54% | +7 |
| working (13) | llm_naive/not_told/look_off | 59% | 60% | 62% | 51% | 49% | 64% | 72% | 64% | 50% | +14 |
| working (13) | llm_naive/told/look_off | 59% | 59% | 61% | 52% | 47% | 62% | 69% | 62% | 49% | +13 |
| working (13) | most frequent | 51% | 53% | 55% | 44% | 46% | 52% | 58% | 54% | 45% | +9 |
| working (13) | periodic | 56% | 58% | 56% | 50% | 48% | 61% | 62% | 59% | 49% | +10 |
| working (13) | timetable | 53% | 57% | 62% | 50% | 50% | 64% | 66% | 60% | 50% | +10 |
| working (13) | timetable wd/we, honest empty bin | 58% | 56% | 61% | 50% | 54% | 63% | 69% | 61% | 52% | +10 |
| retired (7) | Perpetua* | 50% | 54% | 55% | 50% | 53% | 45% | 50% | 51% | 52% | -1 |
| retired (7) | last seen | 49% | 56% | 56% | 51% | 55% | 50% | 52% | 53% | 53% | -1 |
| retired (7) | llm_longleaf/not_told/look_off | 50% | 53% | 57% | 54% | 52% | 57% | 62% | 56% | 53% | +3 |
| retired (7) | llm_longleaf/told/look_off | 50% | 53% | 57% | 54% | 52% | 57% | 62% | 56% | 53% | +3 |
| retired (7) | llm_naive/not_told/look_off | 50% | 59% | 59% | 54% | 55% | 53% | 63% | 57% | 54% | +2 |
| retired (7) | llm_naive/told/look_off | 51% | 59% | 58% | 52% | 58% | 52% | 61% | 56% | 55% | +1 |
| retired (7) | most frequent | 43% | 54% | 49% | 45% | 47% | 47% | 47% | 48% | 46% | +2 |
| retired (7) | periodic | 49% | 56% | 56% | 54% | 54% | 53% | 56% | 54% | 54% | -0 |
| retired (7) | timetable | 48% | 54% | 52% | 52% | 53% | 55% | 62% | 54% | 53% | +1 |
| retired (7) | timetable wd/we, honest empty bin | 52% | 56% | 55% | 51% | 58% | 53% | 57% | 55% | 54% | +0 |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| Perpetua* | +2 | +7 | -5 (21) | 49 | 56 |
| last seen | +2 | +5 | -3 (21) | 51 | 57 |
| llm_longleaf/not_told/look_off | +4 | +4 | -4 (21) | 53 | 64 |
| llm_longleaf/told/look_off | +4 | +5 | -4 (21) | 53 | 64 |
| llm_naive/not_told/look_off | +6 | +8 | -4 (21) | 52 | 68 |
| llm_naive/told/look_off | +4 | +8 | -6 (21) | 52 | 65 |
| most frequent | +5 | +8 | -4 (21) | 45 | 54 |
| periodic | +4 | +4 | -6 (21) | 51 | 59 |
| timetable | +7 | +6 | -3 (21) | 50 | 64 |
| timetable wd/we, honest empty bin | +3 | +8 | -4 (21) | 50 | 63 |

Households with a major event on a scored day: 18/20; event days: {'hh_s10': [5], 'hh_s11': [3, 7], 'hh_s12': [4, 5, 7], 'hh_s13': [1, 2], 'hh_s14': [2, 3, 6], 'hh_s15': [1, 2, 3, 5], 'hh_s16': [4, 5, 6], 'hh_s17': [2, 6, 7], 'hh_s18': [], 'hh_s19': [2, 3, 4], 'hh_s20': [1, 3, 5], 'hh_s21': [5], 'hh_s22': [3], 'hh_s23': [6, 7], 'hh_s24': [1, 2, 4, 6], 'hh_s25': [1], 'hh_s26': [2, 3, 4, 6], 'hh_s27': [], 'hh_s28': [2, 7], 'hh_s29': [4, 5, 7]}

## Per household: Perpetua* (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 61% | 45% | 48% | **41%** | **47%** | 55% | 52% | [4, 5] | [5] |
| hh_s11 | 53% | 55% | **56%** | **48%** | **55%** | 47% | **47%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 45% | 50% | 59% | **59%** | **58%** | 41% | **69%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **58%** | **56%** | 52% | **52%** | **50%** | 38% | 39% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 45% | **53%** | **55%** | **41%** | **50%** | **55%** | 45% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 56% | 69% | 69% | **58%** | **44%** | 52% | 61% | [4, 5] | [] |
| hh_s19 | 58% | **53%** | **59%** | **52%** | **42%** | 44% | 69% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **55%** | 62% | 50% | **42%** | **55%** | 66% | 58% | [1, 4, 5] | [1] |

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 61% | 55% | 52% | **48%** | **47%** | 56% | 50% | [4, 5] | [5] |
| hh_s11 | 55% | 55% | **48%** | **50%** | **58%** | 47% | **50%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 47% | 58% | 59% | **55%** | **61%** | 45% | **53%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **48%** | **59%** | 58% | **58%** | **55%** | 53% | 53% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **53%** | **58%** | **42%** | **48%** | **55%** | 53% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 58% | 67% | 64% | **58%** | **56%** | 59% | 64% | [4, 5] | [] |
| hh_s19 | 59% | **52%** | **56%** | **50%** | **39%** | 48% | 66% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **56%** | 59% | 48% | **45%** | **50%** | 64% | 59% | [1, 4, 5] | [1] |

## Per household: llm_longleaf/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 64% | 53% | 48% | **48%** | **58%** | 70% | 55% | [4, 5] | [5] |
| hh_s11 | 48% | 56% | **45%** | **61%** | **45%** | 55% | **55%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 45% | 52% | 62% | **52%** | **70%** | 56% | **73%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **58%** | **59%** | 56% | **58%** | **52%** | 56% | 64% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **44%** | **62%** | **45%** | **41%** | **62%** | 58% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 53% | 64% | 73% | **53%** | **52%** | 66% | 69% | [4, 5] | [] |
| hh_s19 | 59% | **52%** | **64%** | **61%** | **45%** | 55% | 70% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **58%** | 62% | 52% | **52%** | **62%** | 59% | 72% | [1, 4, 5] | [1] |

## Per household: llm_longleaf/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 64% | 53% | 48% | **47%** | **58%** | 69% | 55% | [4, 5] | [5] |
| hh_s11 | 48% | 56% | **45%** | **61%** | **45%** | 55% | **55%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 45% | 52% | 62% | **52%** | **70%** | 56% | **73%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **58%** | **59%** | 56% | **58%** | **52%** | 56% | 64% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **44%** | **62%** | **45%** | **42%** | **59%** | 58% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 53% | 64% | 73% | **53%** | **52%** | 66% | 69% | [4, 5] | [] |
| hh_s19 | 59% | **52%** | **66%** | **59%** | **45%** | 55% | 70% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **58%** | 62% | 52% | **52%** | **62%** | 59% | 72% | [1, 4, 5] | [1] |

## Per household: llm_naive/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 61% | 58% | 59% | **47%** | **45%** | 69% | 61% | [4, 5] | [5] |
| hh_s11 | 55% | 56% | **48%** | **55%** | **55%** | 47% | **62%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 48% | 62% | 61% | **58%** | **66%** | 55% | **59%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **52%** | **61%** | 64% | **61%** | **55%** | 55% | 64% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **55%** | **61%** | **41%** | **47%** | **56%** | 67% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 59% | 67% | 70% | **58%** | **56%** | 64% | 75% | [4, 5] | [] |
| hh_s19 | 62% | **50%** | **59%** | **53%** | **45%** | 55% | 78% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **55%** | 66% | 61% | **45%** | **48%** | 67% | 75% | [1, 4, 5] | [1] |

## Per household: llm_naive/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 61% | 58% | 59% | **47%** | **42%** | 64% | 58% | [4, 5] | [5] |
| hh_s11 | 55% | 56% | **50%** | **52%** | **56%** | 45% | **66%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 48% | 62% | 61% | **59%** | **72%** | 52% | **62%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **55%** | **66%** | 62% | **58%** | **56%** | 58% | 62% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **53%** | **58%** | **41%** | **47%** | **53%** | 55% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 61% | 67% | 70% | **59%** | **53%** | 62% | 73% | [4, 5] | [] |
| hh_s19 | 61% | **50%** | **59%** | **53%** | **44%** | 56% | 75% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **55%** | 61% | 56% | **47%** | **50%** | 67% | 70% | [1, 4, 5] | [1] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 44% | 52% | **42%** | **47%** | 47% | 58% | [4, 5] | [5] |
| hh_s11 | 44% | 52% | **44%** | **53%** | **50%** | 41% | **47%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 41% | 55% | 53% | **47%** | **53%** | 47% | **58%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **47%** | **61%** | 52% | **44%** | **44%** | 47% | 50% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 39% | **50%** | **48%** | **38%** | **42%** | **53%** | 33% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 48% | 53% | 70% | **47%** | **42%** | 58% | 61% | [4, 5] | [] |
| hh_s19 | 53% | **48%** | **56%** | **44%** | **33%** | 45% | 56% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **45%** | 66% | 42% | **42%** | **61%** | 58% | 56% | [1, 4, 5] | [1] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 64% | 53% | 52% | **47%** | **50%** | 66% | 59% | [4, 5] | [5] |
| hh_s11 | 52% | 55% | **48%** | **56%** | **55%** | 45% | **52%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 48% | 53% | 56% | **59%** | **66%** | 48% | **61%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **48%** | **61%** | 56% | **59%** | **53%** | 58% | 58% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **55%** | **62%** | **42%** | **42%** | **59%** | 53% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 55% | 66% | 67% | **52%** | **55%** | 61% | 66% | [4, 5] | [] |
| hh_s19 | 53% | **52%** | **59%** | **55%** | **38%** | 56% | 67% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **52%** | 62% | 47% | **45%** | **50%** | 61% | 56% | [1, 4, 5] | [1] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 58% | 52% | 55% | **41%** | **52%** | 75% | 45% | [4, 5] | [5] |
| hh_s11 | 47% | 58% | **45%** | **61%** | **50%** | 56% | **50%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 47% | 53% | 58% | **48%** | **69%** | 56% | **78%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **53%** | **61%** | 48% | **56%** | **48%** | 55% | 72% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 44% | **44%** | **55%** | **44%** | **45%** | **53%** | 50% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 47% | 58% | 75% | **47%** | **50%** | 59% | 77% | [4, 5] | [] |
| hh_s19 | 58% | **50%** | **62%** | **56%** | **47%** | 66% | 72% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **48%** | 67% | 56% | **55%** | **53%** | 58% | 72% | [1, 4, 5] | [1] |

## Per household: timetable wd/we, honest empty bin (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 62% | 50% | 50% | **47%** | **58%** | 70% | 50% | [4, 5] | [5] |
| hh_s11 | 55% | 58% | **50%** | **50%** | **53%** | 56% | **58%** | [3, 4, 5, 7] | [3, 7] |
| hh_s12 | 48% | 52% | 55% | **53%** | **66%** | 53% | **61%** | [4, 5, 7] | [4, 5, 7] |
| hh_s13 | **58%** | **66%** | 55% | **58%** | **62%** | 53% | 64% | [1, 2, 4, 5] | [1, 2] |
| hh_s14 | 47% | **50%** | **61%** | **42%** | **52%** | **50%** | 45% | [2, 3, 4, 5, 6] | [2, 3, 6] |
| hh_s18 | 56% | 62% | 72% | **58%** | **56%** | 59% | 77% | [4, 5] | [] |
| hh_s19 | 58% | **50%** | **66%** | **50%** | **45%** | 64% | 78% | [2, 3, 4, 5] | [2, 3, 4] |
| hh_s25 | **56%** | 61% | 58% | **45%** | **56%** | 59% | 70% | [1, 4, 5] | [1] |
