# hh_s10 all agents

1 households, 9 agents, 4032 agent-question records. Shift days per household (weekend + major event days): hh_s10 [4, 5].

Questions per household per agent: hh_s10 448.

Object classes in the questions: glass 16%, towel 10%, mug 8%, vacuum_cleaner 6%, blanket 5%, plate 5%, razor 5%, snack_bowl 5%, toiletry_bag 4%, bowl 3%, duster 3%, laundry_basket 3%, glasses 3%, skincare 3%, detergent 2%, shopping_bag 2%, water_bottle 2%, remote 2%, journal 2%, kitchen_knife 2%, phone 2%, tablet 2%, pen 1%, vitamins 1%, pan 1%, cutting_board 1%, spatula 1%, controller 0%, pot 0%.

## Figure 1: accuracy per day (all questions)

| agent | Wed (0/1 shift) | Thu (0/1 shift) | Fri (0/1 shift) | Sat (1/1 shift) | Sun (1/1 shift) | Mon (0/1 shift) | Tue (0/1 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 72% | 56% | 52% | 55% | 53% | 45% | 45% | 54% |
| last seen | 72% | 61% | 55% | 55% | 55% | 72% | 53% | 60% |
| llm_longleaf/not_told/look_off | 72% | 61% | 55% | 55% | 61% | 70% | 53% | 61% |
| llm_longleaf/told/look_off | 72% | 61% | 55% | 55% | 61% | 70% | 53% | 61% |
| llm_naive/not_told/look_off | 72% | 61% | 55% | 55% | 55% | 59% | 53% | 58% |
| llm_naive/told/look_off | 72% | 61% | 55% | 55% | 58% | 66% | 53% | 60% |
| most frequent | 72% | 61% | 55% | 55% | 61% | 70% | 53% | 61% |
| periodic | 72% | 61% | 55% | 55% | 55% | 72% | 53% | 60% |
| timetable | 72% | 56% | 55% | 55% | 61% | 72% | 53% | 60% |

## Figure 2 (threshold 0.5): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.5; selective accuracy = accuracy on those.

| agent | Wed (0/1 shift) | Thu (0/1 shift) | Fri (0/1 shift) | Sat (1/1 shift) | Sun (1/1 shift) | Mon (0/1 shift) | Tue (0/1 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 100% / 72% | 97% / 58% | 97% / 53% | 92% / 53% | 94% / 57% | 84% / 54% | 95% / 48% | 94% / 56% |
| last seen | 100% / 72% | 100% / 61% | 100% / 55% | 100% / 55% | 100% / 55% | 100% / 72% | 100% / 53% | 100% / 60% |
| llm_longleaf/not_told/look_off | 100% / 72% | 100% / 61% | 100% / 55% | 100% / 55% | 95% / 59% | 100% / 70% | 100% / 53% | 99% / 61% |
| llm_longleaf/told/look_off | 100% / 72% | 100% / 61% | 100% / 55% | 100% / 55% | 95% / 59% | 100% / 70% | 100% / 53% | 99% / 61% |
| llm_naive/not_told/look_off | 100% / 72% | 100% / 61% | 100% / 55% | 100% / 55% | 95% / 57% | 100% / 59% | 100% / 53% | 99% / 59% |
| llm_naive/told/look_off | 100% / 72% | 100% / 61% | 100% / 55% | 100% / 55% | 94% / 58% | 100% / 66% | 100% / 53% | 99% / 60% |
| most frequent | 100% / 72% | 100% / 61% | 97% / 53% | 94% / 52% | 95% / 59% | 95% / 72% | 100% / 53% | 97% / 60% |
| periodic | 100% / 72% | 100% / 61% | 100% / 55% | 100% / 55% | 100% / 55% | 100% / 72% | 100% / 53% | 100% / 60% |
| timetable | 100% / 72% | 95% / 59% | 100% / 55% | 100% / 55% | 94% / 58% | 100% / 72% | 98% / 54% | 98% / 61% |

## Figure 2 (threshold 0.7): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.7; selective accuracy = accuracy on those.

| agent | Wed (0/1 shift) | Thu (0/1 shift) | Fri (0/1 shift) | Sat (1/1 shift) | Sun (1/1 shift) | Mon (0/1 shift) | Tue (0/1 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 100% / 72% | 97% / 58% | 97% / 53% | 88% / 55% | 89% / 60% | 78% / 58% | 83% / 51% | 90% / 58% |
| last seen | 100% / 72% | 100% / 61% | 100% / 55% | 100% / 55% | 100% / 55% | 100% / 72% | 100% / 53% | 100% / 60% |
| llm_longleaf/not_told/look_off | 100% / 72% | 95% / 59% | 97% / 53% | 94% / 52% | 88% / 55% | 92% / 69% | 100% / 53% | 95% / 59% |
| llm_longleaf/told/look_off | 100% / 72% | 95% / 59% | 97% / 53% | 94% / 52% | 88% / 55% | 94% / 70% | 100% / 53% | 95% / 59% |
| llm_naive/not_told/look_off | 100% / 72% | 95% / 59% | 100% / 55% | 100% / 55% | 95% / 57% | 100% / 59% | 100% / 53% | 99% / 59% |
| llm_naive/told/look_off | 100% / 72% | 95% / 59% | 100% / 55% | 100% / 55% | 91% / 60% | 100% / 66% | 100% / 53% | 98% / 60% |
| most frequent | 94% / 70% | 94% / 58% | 97% / 53% | 92% / 51% | 88% / 55% | 89% / 70% | 98% / 54% | 93% / 59% |
| periodic | 100% / 72% | 95% / 59% | 100% / 55% | 100% / 55% | 100% / 55% | 100% / 72% | 100% / 53% | 99% / 60% |
| timetable | 100% / 72% | 95% / 59% | 100% / 55% | 100% / 55% | 94% / 58% | 100% / 72% | 98% / 54% | 98% / 61% |

## Figure 2 (threshold 0.9): coverage / selective accuracy per day

Coverage = share of questions answered with confidence >= 0.9; selective accuracy = accuracy on those.

| agent | Wed (0/1 shift) | Thu (0/1 shift) | Fri (0/1 shift) | Sat (1/1 shift) | Sun (1/1 shift) | Mon (0/1 shift) | Tue (0/1 shift) | all |
|---|---|---|---|---|---|---|---|---|
| Perpetua* | 86% / 73% | 66% / 71% | 50% / 69% | 73% / 62% | 59% / 66% | 53% / 82% | 69% / 55% | 65% / 68% |
| last seen | 100% / 72% | 100% / 61% | 100% / 55% | 100% / 55% | 100% / 55% | 100% / 72% | 100% / 53% | 100% / 60% |
| llm_longleaf/not_told/look_off | 84% / 72% | 80% / 65% | 78% / 56% | 84% / 54% | 77% / 57% | 59% / 58% | 89% / 53% | 79% / 59% |
| llm_longleaf/told/look_off | 84% / 72% | 80% / 65% | 78% / 56% | 84% / 54% | 77% / 57% | 59% / 58% | 89% / 53% | 79% / 59% |
| llm_naive/not_told/look_off | 98% / 73% | 95% / 59% | 100% / 55% | 100% / 55% | 91% / 60% | 95% / 61% | 98% / 54% | 97% / 59% |
| llm_naive/told/look_off | 98% / 73% | 95% / 59% | 98% / 54% | 95% / 57% | 89% / 61% | 92% / 69% | 98% / 54% | 95% / 61% |
| most frequent | 84% / 72% | 81% / 65% | 81% / 58% | 81% / 54% | 78% / 56% | 56% / 64% | 81% / 58% | 78% / 61% |
| periodic | 100% / 72% | 94% / 58% | 97% / 56% | 100% / 55% | 98% / 54% | 100% / 72% | 100% / 53% | 98% / 60% |
| timetable | 94% / 75% | 89% / 61% | 86% / 51% | 88% / 52% | 84% / 57% | 91% / 78% | 88% / 57% | 88% / 62% |

## Reliability (stated confidence vs observed accuracy, pooled over the week)

| agent | [0,0.2) | [0.2,0.4) | [0.4,0.5) | [0.5,0.6) | [0.6,0.7) | [0.7,0.8) | [0.8,0.9) | [0.9,0.95) | [0.95,1) | ECE |
|---|---|---|---|---|---|---|---|---|---|---|
| Perpetua* | - | 0% (n=16) | 40% (n=10) | 11% (n=9) | 11% (n=9) | 20% (n=20) | 37% (n=92) | 47% (n=72) | 75% (n=220) | 0.347 |
| last seen | - | - | - | - | - | - | - | - | 60% (n=448) | 0.396 |
| llm_longleaf/not_told/look_off | - | - | 100% (n=3) | 100% (n=15) | 75% (n=4) | 79% (n=24) | 49% (n=49) | 35% (n=48) | 63% (n=305) | 0.359 |
| llm_longleaf/told/look_off | - | - | 100% (n=3) | 100% (n=14) | 75% (n=4) | 79% (n=24) | 50% (n=50) | 35% (n=48) | 63% (n=305) | 0.358 |
| llm_naive/not_told/look_off | - | - | 0% (n=3) | - | 100% (n=3) | - | 12% (n=8) | 0% (n=4) | 60% (n=430) | 0.369 |
| llm_naive/told/look_off | - | 0% (n=2) | 100% (n=2) | - | 60% (n=5) | - | 17% (n=12) | 20% (n=5) | 62% (n=422) | 0.351 |
| most frequent | - | 100% (n=3) | 78% (n=9) | 100% (n=10) | 89% (n=9) | 62% (n=24) | 40% (n=45) | 56% (n=27) | 61% (n=321) | 0.369 |
| periodic | - | - | - | - | 100% (n=3) | 100% (n=1) | 33% (n=3) | 75% (n=4) | 60% (n=437) | 0.394 |
| timetable | - | 0% (n=3) | 80% (n=5) | - | - | 33% (n=3) | 51% (n=41) | 51% (n=89) | 65% (n=307) | 0.348 |

## Split by household kind (from the intro cards: any retired resident, or none)

Retired residents are home on weekdays too, so the weekend is not a routine shift for their household.

| household kind (n) | agent | Wed | Thu | Fri | Sat | Sun | Mon | Tue | weekday | weekend | drop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| working (13) | Perpetua* | 72% | 56% | 52% | 55% | 53% | 45% | 45% | 54% | 54% | +0 |
| working (13) | last seen | 72% | 61% | 55% | 55% | 55% | 72% | 53% | 62% | 55% | +8 |
| working (13) | llm_longleaf/not_told/look_off | 72% | 61% | 55% | 55% | 61% | 70% | 53% | 62% | 58% | +4 |
| working (13) | llm_longleaf/told/look_off | 72% | 61% | 55% | 55% | 61% | 70% | 53% | 62% | 58% | +4 |
| working (13) | llm_naive/not_told/look_off | 72% | 61% | 55% | 55% | 55% | 59% | 53% | 60% | 55% | +5 |
| working (13) | llm_naive/told/look_off | 72% | 61% | 55% | 55% | 58% | 66% | 53% | 61% | 56% | +5 |
| working (13) | most frequent | 72% | 61% | 55% | 55% | 61% | 70% | 53% | 62% | 58% | +4 |
| working (13) | periodic | 72% | 61% | 55% | 55% | 55% | 72% | 53% | 62% | 55% | +8 |
| working (13) | timetable | 72% | 56% | 55% | 55% | 61% | 72% | 53% | 62% | 58% | +4 |
| retired (7) | Perpetua* | - | - | - | - | - | - | - | - | - | +nan |
| retired (7) | last seen | - | - | - | - | - | - | - | - | - | +nan |
| retired (7) | llm_longleaf/not_told/look_off | - | - | - | - | - | - | - | - | - | +nan |
| retired (7) | llm_longleaf/told/look_off | - | - | - | - | - | - | - | - | - | +nan |
| retired (7) | llm_naive/not_told/look_off | - | - | - | - | - | - | - | - | - | +nan |
| retired (7) | llm_naive/told/look_off | - | - | - | - | - | - | - | - | - | +nan |
| retired (7) | most frequent | - | - | - | - | - | - | - | - | - | +nan |
| retired (7) | periodic | - | - | - | - | - | - | - | - | - | +nan |
| retired (7) | timetable | - | - | - | - | - | - | - | - | - | +nan |

## Tuning criteria numbers

| agent | rise Wed->Fri | drop Fri->Sat | drop day-before->event (n event days) | min day | max day |
|---|---|---|---|---|---|
| Perpetua* | -20 | -3 | - (21) | 45 | 72 |
| last seen | -17 | +0 | - (21) | 53 | 72 |
| llm_longleaf/not_told/look_off | -17 | +0 | - (21) | 53 | 72 |
| llm_longleaf/told/look_off | -17 | +0 | - (21) | 53 | 72 |
| llm_naive/not_told/look_off | -17 | +0 | - (21) | 53 | 72 |
| llm_naive/told/look_off | -17 | +0 | - (21) | 53 | 72 |
| most frequent | -17 | +0 | - (21) | 53 | 72 |
| periodic | -17 | +0 | - (21) | 53 | 72 |
| timetable | -17 | +0 | - (21) | 53 | 72 |

Households with a major event on a scored day: 18/20; event days: {'hh_s10': [5], 'hh_s11': [3, 7], 'hh_s12': [4, 5, 7], 'hh_s13': [1, 2], 'hh_s14': [2, 3, 6], 'hh_s15': [1, 2, 3, 5], 'hh_s16': [4, 5, 6], 'hh_s17': [2, 6, 7], 'hh_s18': [], 'hh_s19': [2, 3, 4], 'hh_s20': [1, 3, 5], 'hh_s21': [5], 'hh_s22': [3], 'hh_s23': [6, 7], 'hh_s24': [1, 2, 4, 6], 'hh_s25': [1], 'hh_s26': [2, 3, 4, 6], 'hh_s27': [], 'hh_s28': [2, 7], 'hh_s29': [4, 5, 7]}

## Per household: Perpetua* (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 56% | 52% | **55%** | **53%** | 45% | 45% | [4, 5] | [5] |

## Per household: last seen (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **55%** | 72% | 53% | [4, 5] | [5] |

## Per household: llm_longleaf/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **61%** | 70% | 53% | [4, 5] | [5] |

## Per household: llm_longleaf/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **61%** | 70% | 53% | [4, 5] | [5] |

## Per household: llm_naive/not_told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **55%** | 59% | 53% | [4, 5] | [5] |

## Per household: llm_naive/told/look_off (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **58%** | 66% | 53% | [4, 5] | [5] |

## Per household: most frequent (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **61%** | 70% | 53% | [4, 5] | [5] |

## Per household: periodic (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 61% | 55% | **55%** | **55%** | 72% | 53% | [4, 5] | [5] |

## Per household: timetable (bold = shift day)

| household | Wed | Thu | Fri | Sat | Sun | Mon | Tue | shift days | event days |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 72% | 56% | 55% | **55%** | **61%** | 72% | 53% | [4, 5] | [5] |
