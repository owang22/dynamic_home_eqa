# Judge harness — `moe_strict_thinking`

- style: **strict**, thinking: **True**, temperature: **0.7**, k: **1**
- scored 48/48 EVAL candidates

## Headline

- **Spearman rank corr vs human band: 0.66**
- exact-band match: 0.52   within-one: 0.90
- **over-scored (judge > human): 0.29**   under: 0.19

## Band separation (judge score within each human band)

| human band | n | mean judge score | std |
|---|---|---|---|
| 3 typical | 12 | 0.83 | 0.12 |
| 2 plausible-uncommon | 13 | 0.58 | 0.20 |
| 1 contrived | 13 | 0.39 | 0.24 |
| 0 absurd | 10 | 0.34 | 0.27 |

## Confusion (rows = human band, cols = predicted band)

| human ↓ / pred → | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 3 | 0 | 0 | 2 | 10 |
| 2 | 0 | 4 | 7 | 2 |
| 1 | 3 | 5 | 3 | 2 |
| 0 | 3 | 4 | 1 | 2 |

## Dinner-laptop candidates (the case the judge should nail)

| id | object | anchor | activity | human | judge score | pred |
|---|---|---|---|---|---|---|
| c000 | laptop | kitchen.table_1 | breakfast | 2 | 0.7 | 2 |
| c001 | phone | kitchen.table_1 | snacking | 3 | 0.7 | 2 |
| c002 | phone | kitchen.table_1 | breakfast | 3 | 0.9 | 3 |
| c020 | laptop | dining_room.counter_2 | eating_breakfast | 2 | 0.7 | 2 |
| c021 | laptop | dining_room.counter_2 | lunch | 1 | 0.2 | 1 |
| c022 | phone | dining_room.counter_1 | lunch | 2 | 0.2 | 1 |
| c023 | laptop | kitchen.counter_1 | lunch_break | 2 | 0.8 | 3 |

## Worst disagreements

| id | object | rel | anchor | activity | human | judge | pred | gap | notes |
|---|---|---|---|---|---|---|---|---|---|
| c018 | book | in_region | kitchen | organizing_recipes | 0 | 0.8 | 3 | +3 |  |
| c041 | potted_plant | in_region | bedroom | sleeping | 0 | 0.8 | 3 | +3 | plants are never moved for nightly sleeping ambience |
| c043 | potted_plant | in_region | kitchen | clean_up_after_dinner | 0 | 0.5 | 2 | +2 |  |
| c034 | bottle | on | living_room.counter_1 | toys_cleaning_intervention | 1 | 0.8 | 3 | +2 | bottles aren't usually toys |
| c042 | wallet | in_region | bedroom | go_to_bed | 1 | 0.8 | 3 | +2 |  |
| c040 | drinkware | in_region | kitchen | helping_with_dishes | 3 | 0.5 | 2 | -1 |  |
| c022 | phone | on | dining_room.counter_1 | lunch | 2 | 0.2 | 1 | -1 |  |
| c016 | wallet | on | tv.couch_1 | watching TV | 2 | 0.3 | 1 | -1 |  |
| c001 | phone | on_top | kitchen.table_1 | snacking | 3 | 0.7 | 2 | -1 |  |
| c030 | keys | next_to | living_room.table_1 | watching_tv | 0 | 0.3 | 1 | +1 |  |
