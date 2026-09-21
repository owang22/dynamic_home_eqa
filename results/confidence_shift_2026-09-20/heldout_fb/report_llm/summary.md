# Held-out households hh_s10, hh_s11, hh_s12, hh_s13, hh_s14, hh_s18, hh_s19, hh_s25: every agent (found-it feedback protocol)

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
| Perpetua* | 97% / 55% | 85% / 62% | 79% / 63% | 76% / 58% | 75% / 56% | 73% / 59% | 73% / 67% | 80% / 60% |
| last seen | 100% / 54% | 100% / 57% | 100% / 55% | 100% / 51% | 100% / 52% | 100% / 54% | 100% / 56% | 100% / 54% |
| llm_longleaf/not_told/look_off | 6% / 83% | 11% / 80% | 15% / 85% | 12% / 75% | 15% / 74% | 15% / 87% | 21% / 91% | 13% / 83% |
| llm_longleaf/told/look_off | 6% / 83% | 11% / 80% | 15% / 86% | 12% / 76% | 15% / 74% | 15% / 87% | 20% / 91% | 13% / 83% |
| llm_naive/not_told/look_off | 99% / 55% | 97% / 61% | 96% / 63% | 97% / 54% | 97% / 53% | 96% / 60% | 98% / 68% | 97% / 59% |
| llm_naive/told/look_off | 97% / 56% | 97% / 61% | 96% / 61% | 96% / 53% | 98% / 53% | 98% / 58% | 98% / 66% | 97% / 58% |
| most frequent | 24% / 76% | 50% / 79% | 49% / 72% | 55% / 59% | 54% / 58% | 54% / 62% | 52% / 70% | 48% / 67% |
| periodic | 26% / 57% | 66% / 56% | 80% / 57% | 79% / 50% | 85% / 51% | 92% / 56% | 92% / 58% | 74% / 55% |
| timetable | 14% / 71% | 26% / 82% | 30% / 72% | 39% / 64% | 36% / 60% | 32% / 73% | 45% / 81% | 32% / 72% |
| timetable wd/we, honest empty bin | 4% / 58% | 7% / 78% | 14% / 77% | 2% / 45% | 5% / 42% | 19% / 79% | 32% / 81% | 12% / 75% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (2/8 shift) | Thu (3/8 shift) | Fri (3/8 shift) | Sat (8/8 shift) | Sun (8/8 shift) | Mon (1/8 shift) | Tue (2/8 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 80% / 60% | 63% / 72% | 57% / 71% | 54% / 65% | 52% / 61% | 53% / 65% | 55% / 70% | 59% / 66% |
| last seen | 100% / 54% | 100% / 57% | 100% / 55% | 100% / 51% | 100% / 52% | 100% / 54% | 100% / 56% | 100% / 54% |
| llm_longleaf/not_told/look_off | 0% / - | 0% / - | 1% / 100% | 1% / 100% | 1% / 100% | 1% / 100% | 1% / 100% | 1% / 100% |
| llm_longleaf/told/look_off | 0% / - | 0% / - | 1% / 100% | 1% / 100% | 1% / 100% | 1% / 100% | 1% / 100% | 1% / 100% |
| llm_naive/not_told/look_off | 87% / 59% | 82% / 67% | 80% / 68% | 87% / 56% | 86% / 56% | 85% / 63% | 86% / 72% | 85% / 63% |
| llm_naive/told/look_off | 86% / 60% | 84% / 66% | 81% / 67% | 85% / 56% | 82% / 56% | 86% / 62% | 86% / 71% | 84% / 63% |
| most frequent | 4% / 65% | 13% / 88% | 25% / 83% | 26% / 76% | 29% / 73% | 28% / 86% | 30% / 92% | 22% / 82% |
| periodic | 12% / 38% | 34% / 47% | 50% / 56% | 54% / 46% | 60% / 49% | 64% / 55% | 62% / 57% | 48% / 51% |
| timetable | 4% / 67% | 5% / 92% | 9% / 70% | 14% / 76% | 15% / 67% | 10% / 76% | 15% / 86% | 10% / 76% |
| timetable wd/we, honest empty bin | 3% / 60% | 3% / 92% | 4% / 63% | 2% / 38% | 2% / 25% | 4% / 67% | 9% / 80% | 4% / 67% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (2/8 shift) | Thu (3/8 shift) | Fri (3/8 shift) | Sat (8/8 shift) | Sun (8/8 shift) | Mon (1/8 shift) | Tue (2/8 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 72% / 61% | 51% / 76% | 44% / 75% | 41% / 66% | 38% / 68% | 37% / 69% | 40% / 70% | 46% / 69% |
| last seen | 100% / 54% | 100% / 57% | 100% / 55% | 100% / 51% | 100% / 52% | 100% / 54% | 100% / 56% | 100% / 54% |
| llm_longleaf/not_told/look_off | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| llm_longleaf/told/look_off | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - | 0% / - |
| llm_naive/not_told/look_off | 62% / 67% | 58% / 76% | 56% / 78% | 61% / 62% | 57% / 63% | 57% / 73% | 57% / 78% | 58% / 71% |
| llm_naive/told/look_off | 60% / 68% | 56% / 77% | 57% / 74% | 56% / 63% | 51% / 67% | 57% / 73% | 58% / 79% | 56% / 72% |
| most frequent | 3% / 60% | 3% / 92% | 3% / 59% | 2% / 38% | 2% / 25% | 4% / 68% | 6% / 76% | 3% / 64% |
| periodic | 8% / 50% | 15% / 61% | 33% / 65% | 33% / 50% | 37% / 54% | 42% / 61% | 42% / 66% | 30% / 59% |
| timetable | 3% / 60% | 3% / 92% | 3% / 59% | 2% / 38% | 2% / 25% | 3% / 62% | 4% / 67% | 3% / 60% |
| timetable wd/we, honest empty bin | 3% / 60% | 3% / 92% | 3% / 59% | 2% / 38% | 2% / 25% | 3% / 62% | 4% / 67% | 3% / 60% |

## Coverage-matched selective accuracy (each agent answers its most confident 25 / 50 / 75% of the day's questions)

The fixed thresholds above compare different confidence scales; this compares agents at equal coverage.

| agent (coverage 25%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 66% | 83% | 80% | 73% | 75% | 77% | 79% | 75% |
| last seen | 59% | 60% | 67% | 49% | 48% | 61% | 62% | 56% |
| llm_longleaf/not_told/look_off | 73% | 75% | 83% | 66% | 70% | 81% | 89% | 77% |
| llm_longleaf/told/look_off | 73% | 75% | 83% | 67% | 70% | 80% | 88% | 77% |
| llm_naive/not_told/look_off | 76% | 81% | 77% | 67% | 70% | 75% | 70% | 73% |
| llm_naive/told/look_off | 76% | 80% | 74% | 70% | 71% | 72% | 77% | 74% |
| most frequent | 74% | 89% | 84% | 77% | 77% | 88% | 93% | 81% |
| periodic | 55% | 52% | 68% | 54% | 55% | 64% | 76% | 61% |
| timetable | 59% | 84% | 73% | 65% | 65% | 77% | 83% | 75% |
| timetable wd/we, honest empty bin | 63% | 61% | 76% | 50% | 59% | 80% | 82% | 70% |

| agent (coverage 50%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 64% | 77% | 74% | 66% | 62% | 66% | 71% | 68% |
| last seen | 54% | 59% | 59% | 50% | 50% | 54% | 55% | 55% |
| llm_longleaf/not_told/look_off | 66% | 72% | 78% | 66% | 66% | 74% | 83% | 72% |
| llm_longleaf/told/look_off | 66% | 71% | 77% | 65% | 65% | 73% | 82% | 71% |
| llm_naive/not_told/look_off | 73% | 77% | 78% | 65% | 64% | 76% | 79% | 73% |
| llm_naive/told/look_off | 73% | 79% | 76% | 65% | 68% | 76% | 83% | 74% |
| most frequent | 61% | 79% | 71% | 62% | 61% | 65% | 72% | 66% |
| periodic | 58% | 52% | 55% | 46% | 49% | 59% | 62% | 51% |
| timetable | 57% | 66% | 70% | 62% | 58% | 73% | 79% | 66% |
| timetable wd/we, honest empty bin | 60% | 59% | 65% | 50% | 59% | 68% | 76% | 61% |

| agent (coverage 75%) | Wed | Thu | Fri | Sat | Sun | Mon | Tue | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 61% | 66% | 66% | 59% | 56% | 58% | 65% | 61% |
| last seen | 54% | 59% | 57% | 51% | 53% | 55% | 56% | 55% |
| llm_longleaf/not_told/look_off | 60% | 63% | 67% | 59% | 60% | 67% | 72% | 64% |
| llm_longleaf/told/look_off | 60% | 64% | 67% | 58% | 60% | 67% | 73% | 64% |
| llm_naive/not_told/look_off | 61% | 69% | 69% | 58% | 58% | 65% | 72% | 65% |
| llm_naive/told/look_off | 63% | 69% | 68% | 58% | 58% | 64% | 73% | 65% |
| most frequent | 57% | 64% | 62% | 51% | 52% | 58% | 61% | 58% |
| periodic | 57% | 58% | 55% | 49% | 49% | 55% | 57% | 55% |
| timetable | 59% | 60% | 62% | 57% | 57% | 63% | 70% | 61% |
| timetable wd/we, honest empty bin | 57% | 59% | 60% | 51% | 59% | 62% | 66% | 59% |

## Questions whose object moved since the robot's last round (52% of questions)

The robot's last full look is the patrol round before the question. 'still' questions are answered by recency almost by definition; the shift and the learning live in the 'moved' half. Cells: accuracy c=mean confidence.

| agent | Wed moved / still | Thu moved / still | Fri moved / still | Sat moved / still | Sun moved / still | Mon moved / still | Tue moved / still | moved all | still all |
|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 19% c84 / 92% c93 | 26% c69 / 83% c87 | 33% c66 / 84% c83 | 22% c67 / 81% c78 | 29% c65 / 74% c78 | 22% c63 / 80% c79 | 27% c64 / 82% c80 | 26% (n=1875, cov@0.7 48%, sel 29%) | 82% |
| last seen | 17% c98 / 95% c98 | 17% c98 / 95% c98 | 25% c98 / 92% c98 | 14% c98 / 94% c98 | 20% c98 / 89% c98 | 17% c98 / 93% c98 | 18% c98 / 95% c98 | 18% (n=1875, cov@0.7 100%, sel 18%) | 93% |
| llm_longleaf/not_told/look_off | 18% c28 / 94% c32 | 29% c30 / 80% c36 | 35% c30 / 85% c41 | 29% c32 / 83% c38 | 33% c33 / 76% c40 | 40% c32 / 82% c40 | 49% c32 / 80% c44 | 33% (n=1875, cov@0.7 0%, sel -) | 83% |
| llm_longleaf/told/look_off | 18% c28 / 94% c32 | 29% c30 / 80% c36 | 36% c30 / 85% c41 | 29% c32 / 82% c38 | 33% c33 / 77% c40 | 40% c32 / 81% c40 | 49% c32 / 80% c44 | 33% (n=1875, cov@0.7 0%, sel -) | 83% |
| llm_naive/not_told/look_off | 19% c84 / 95% c91 | 23% c80 / 94% c91 | 37% c81 / 89% c90 | 18% c84 / 92% c90 | 25% c84 / 84% c89 | 32% c81 / 88% c91 | 45% c82 / 91% c91 | 28% (n=1875, cov@0.7 77%, sel 29%) | 90% |
| llm_naive/told/look_off | 20% c83 / 94% c91 | 22% c80 / 94% c91 | 35% c81 / 89% c90 | 17% c83 / 92% c89 | 26% c83 / 85% c89 | 29% c83 / 89% c90 | 40% c82 / 90% c91 | 27% (n=1875, cov@0.7 76%, sel 28%) | 91% |
| most frequent | 7% c42 / 91% c48 | 19% c43 / 86% c58 | 25% c45 / 85% c61 | 14% c47 / 80% c63 | 21% c49 / 76% c62 | 24% c45 / 78% c65 | 25% c46 / 79% c68 | 19% (n=1875, cov@0.7 10%, sel 27%) | 82% |
| periodic | 11% c46 / 98% c43 | 20% c68 / 92% c57 | 29% c74 / 88% c68 | 18% c76 / 92% c67 | 23% c79 / 84% c71 | 26% c79 / 91% c77 | 26% c78 / 92% c78 | 22% (n=1875, cov@0.7 56%, sel 28%) | 91% |
| timetable | 14% c40 / 90% c43 | 29% c39 / 80% c46 | 35% c42 / 82% c49 | 31% c44 / 75% c53 | 38% c43 / 68% c51 | 51% c43 / 70% c49 | 57% c46 / 71% c55 | 36% (n=1875, cov@0.7 7%, sel 38%) | 77% |
| timetable wd/we, honest empty bin | 19% c35 / 95% c32 | 28% c36 / 83% c36 | 36% c38 / 85% c39 | 13% c33 / 94% c31 | 31% c35 / 86% c33 | 42% c39 / 77% c41 | 48% c41 / 78% c47 | 31% (n=1875, cov@0.7 4%, sel 54%) | 85% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | 0% (n=13) | 22% (n=430) | 29% (n=287) | 40% (n=407) | 44% (n=326) | 54% (n=231) | 59% (n=233) | 53% (n=167) | 71% (n=1490) | 0.224 |
| last seen | - | - | - | - | - | - | - | - | 54% (n=3584) | 0.441 |
| llm_longleaf/not_told/look_off | 33% (n=411) | 52% (n=2067) | 68% (n=625) | 78% (n=333) | 92% (n=126) | 100% (n=20) | 100% (n=2) | - | - | 0.223 |
| llm_longleaf/told/look_off | 32% (n=406) | 52% (n=2078) | 68% (n=618) | 79% (n=335) | 92% (n=125) | 100% (n=20) | 100% (n=2) | - | - | 0.222 |
| llm_naive/not_told/look_off | - | 0% (n=2) | 16% (n=102) | 100% (n=1) | 35% (n=447) | 43% (n=37) | 45% (n=916) | 55% (n=258) | 73% (n=1821) | 0.283 |
| llm_naive/told/look_off | 0% (n=1) | - | 18% (n=97) | - | 31% (n=470) | 60% (n=45) | 43% (n=952) | 53% (n=247) | 74% (n=1772) | 0.287 |
| most frequent | 7% (n=74) | 27% (n=1005) | 43% (n=776) | 44% (n=471) | 64% (n=458) | 79% (n=424) | 95% (n=263) | 100% (n=11) | 60% (n=102) | 0.060 |
| periodic | 30% (n=47) | 49% (n=441) | 65% (n=432) | 65% (n=539) | 55% (n=406) | 37% (n=314) | 38% (n=326) | 49% (n=278) | 63% (n=801) | 0.260 |
| timetable | 10% (n=50) | 44% (n=1575) | 58% (n=822) | 66% (n=432) | 74% (n=346) | 78% (n=189) | 94% (n=68) | - | 60% (n=102) | 0.123 |
| timetable wd/we, honest empty bin | 10% (n=10) | 53% (n=2774) | 67% (n=376) | 75% (n=189) | 87% (n=106) | 92% (n=25) | 100% (n=2) | - | 60% (n=102) | 0.221 |

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
