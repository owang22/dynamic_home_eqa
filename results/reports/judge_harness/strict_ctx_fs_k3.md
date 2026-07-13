# Judge harness — `strict_ctx_fs_k3`

- style: **strict**, thinking: **True**, temperature: **0.7**, k: **3**
- scored 48/48 EVAL candidates

## Headline

- **Spearman rank corr vs human band: 0.83**
- exact-band match: 0.62   within-one: 0.98
- **over-scored (judge > human): 0.23**   under: 0.15

## Band separation (judge score within each human band)

| human band | n | mean judge score | std |
|---|---|---|---|
| 3 typical | 12 | 0.80 | 0.13 |
| 2 plausible-uncommon | 13 | 0.55 | 0.16 |
| 1 contrived | 13 | 0.41 | 0.14 |
| 0 absurd | 10 | 0.18 | 0.13 |

## Confusion (rows = human band, cols = predicted band)

| human ↓ / pred → | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 3 | 0 | 0 | 3 | 9 |
| 2 | 0 | 3 | 9 | 1 |
| 1 | 1 | 6 | 6 | 0 |
| 0 | 6 | 3 | 1 | 0 |

## Dinner-laptop candidates (the case the judge should nail)

| id | object | anchor | activity | human | judge score | pred |
|---|---|---|---|---|---|---|
| c000 | laptop | kitchen.table_1 | breakfast | 2 | 0.7 | 2 |
| c001 | phone | kitchen.table_1 | snacking | 3 | 0.8 | 3 |
| c002 | phone | kitchen.table_1 | breakfast | 3 | 0.8 | 3 |
| c020 | laptop | dining_room.counter_2 | eating_breakfast | 2 | 0.8 | 3 |
| c021 | laptop | dining_room.counter_2 | lunch | 1 | 0.5 | 2 |
| c022 | phone | dining_room.counter_1 | lunch | 2 | 0.7 | 2 |
| c023 | laptop | kitchen.counter_1 | lunch_break | 2 | 0.6 | 2 |

## Worst disagreements

| id | object | rel | anchor | activity | human | judge | pred | gap | notes |
|---|---|---|---|---|---|---|---|---|---|
| c030 | keys | next_to | living_room.table_1 | watching_tv | 0 | 0.5 | 2 | +2 |  |
| c024 | drinkware | on_top | kitchen.counter_1 | lunch_break | 3 | 0.5 | 2 | -1 |  |
| c016 | wallet | on | tv.couch_1 | watching TV | 2 | 0.2 | 1 | -1 |  |
| c027 | drinkware | on | dining_room.counter_1 | snack | 3 | 0.6 | 2 | -1 |  |
| c053 | potted_plant | in_region | bedroom | organizing_workspace | 2 | 0.3 | 1 | -1 |  |
| c026 | bowl | on_top | kitchen.counter_1 | breakfast | 3 | 0.7 | 2 | -1 |  |
| c041 | potted_plant | in_region | bedroom | sleeping | 0 | 0.3 | 1 | +1 | plants are never moved for nightly sleeping ambience |
| c009 | tv | in_region | kitchen | eating_dinner | 1 | 0.05 | 0 | -1 | tv is not easily moved |
| c045 | keys | in_region | bedroom | waking_up | 1 | 0.6 | 2 | +1 | keys are retrieved and kept in a pocket and not left out |
| c056 | wallet | in_region | bedroom | wake_up | 1 | 0.6 | 2 | +1 | only likely if James is a messy person |
