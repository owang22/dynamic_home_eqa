# Judge harness — `strict_ctx_fs`

- style: **strict**, thinking: **False**, temperature: **0.7**, k: **1**
- scored 48/48 EVAL candidates

## Headline

- **Spearman rank corr vs human band: 0.79**
- exact-band match: 0.67   within-one: 0.94
- **over-scored (judge > human): 0.15**   under: 0.19

## Band separation (judge score within each human band)

| human band | n | mean judge score | std |
|---|---|---|---|
| 3 typical | 12 | 0.80 | 0.14 |
| 2 plausible-uncommon | 13 | 0.50 | 0.17 |
| 1 contrived | 13 | 0.36 | 0.26 |
| 0 absurd | 10 | 0.11 | 0.10 |

## Confusion (rows = human band, cols = predicted band)

| human ↓ / pred → | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 3 | 0 | 1 | 1 | 10 |
| 2 | 0 | 4 | 8 | 1 |
| 1 | 3 | 7 | 1 | 2 |
| 0 | 7 | 3 | 0 | 0 |

## Dinner-laptop candidates (the case the judge should nail)

| id | object | anchor | activity | human | judge score | pred |
|---|---|---|---|---|---|---|
| c000 | laptop | kitchen.table_1 | breakfast | 2 | 0.4 | 1 |
| c001 | phone | kitchen.table_1 | snacking | 3 | 0.75 | 3 |
| c002 | phone | kitchen.table_1 | breakfast | 3 | 0.8 | 3 |
| c020 | laptop | dining_room.counter_2 | eating_breakfast | 2 | 0.8 | 3 |
| c021 | laptop | dining_room.counter_2 | lunch | 1 | 0.4 | 1 |
| c022 | phone | dining_room.counter_1 | lunch | 2 | 0.6 | 2 |
| c023 | laptop | kitchen.counter_1 | lunch_break | 2 | 0.6 | 2 |

## Worst disagreements

| id | object | rel | anchor | activity | human | judge | pred | gap | notes |
|---|---|---|---|---|---|---|---|---|---|
| c024 | drinkware | on_top | kitchen.counter_1 | lunch_break | 3 | 0.4 | 1 | -2 |  |
| c045 | keys | in_region | bedroom | waking_up | 1 | 0.85 | 3 | +2 | keys are retrieved and kept in a pocket and not left out |
| c059 | keys | in_region | living_room | light_housework | 1 | 0.8 | 3 | +2 | unusual for keys to be stored in either the living room or bathroom and should instead be kept in a pocket or bedroom |
| c006 | bottle | on_top | kitchen.table_1 | snack | 2 | 0.15 | 1 | -1 |  |
| c053 | potted_plant | in_region | bedroom | organizing_workspace | 2 | 0.2 | 1 | -1 |  |
| c056 | wallet | in_region | bedroom | wake_up | 1 | 0.7 | 2 | +1 | only likely if James is a messy person |
| c027 | drinkware | on | dining_room.counter_1 | snack | 3 | 0.7 | 2 | -1 |  |
| c030 | keys | next_to | living_room.table_1 | watching_tv | 0 | 0.3 | 1 | +1 |  |
| c009 | tv | in_region | kitchen | eating_dinner | 1 | 0.05 | 0 | -1 | tv is not easily moved |
| c000 | laptop | on_top | kitchen.table_1 | breakfast | 2 | 0.4 | 1 | -1 |  |
