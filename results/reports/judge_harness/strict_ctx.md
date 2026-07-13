# Judge harness — `strict_ctx`

- style: **strict**, thinking: **False**, temperature: **0.7**, k: **1**
- scored 48/48 EVAL candidates

## Headline

- **Spearman rank corr vs human band: 0.73**
- exact-band match: 0.54   within-one: 0.92
- **over-scored (judge > human): 0.38**   under: 0.08

## Band separation (judge score within each human band)

| human band | n | mean judge score | std |
|---|---|---|---|
| 3 typical | 12 | 0.83 | 0.12 |
| 2 plausible-uncommon | 13 | 0.65 | 0.16 |
| 1 contrived | 13 | 0.50 | 0.22 |
| 0 absurd | 10 | 0.27 | 0.22 |

## Confusion (rows = human band, cols = predicted band)

| human ↓ / pred → | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 3 | 0 | 0 | 2 | 10 |
| 2 | 0 | 1 | 8 | 4 |
| 1 | 1 | 4 | 6 | 2 |
| 0 | 4 | 4 | 1 | 1 |

## Dinner-laptop candidates (the case the judge should nail)

| id | object | anchor | activity | human | judge score | pred |
|---|---|---|---|---|---|---|
| c000 | laptop | kitchen.table_1 | breakfast | 2 | 0.7 | 2 |
| c001 | phone | kitchen.table_1 | snacking | 3 | 0.8 | 3 |
| c002 | phone | kitchen.table_1 | breakfast | 3 | 0.8 | 3 |
| c020 | laptop | dining_room.counter_2 | eating_breakfast | 2 | 0.6 | 2 |
| c021 | laptop | dining_room.counter_2 | lunch | 1 | 0.6 | 2 |
| c022 | phone | dining_room.counter_1 | lunch | 2 | 0.8 | 3 |
| c023 | laptop | kitchen.counter_1 | lunch_break | 2 | 0.7 | 2 |

## Worst disagreements

| id | object | rel | anchor | activity | human | judge | pred | gap | notes |
|---|---|---|---|---|---|---|---|---|---|
| c041 | potted_plant | in_region | bedroom | sleeping | 0 | 0.8 | 3 | +3 | plants are never moved for nightly sleeping ambience |
| c037 | vase | on | bedroom_1.cabinet_1 | sleeping | 0 | 0.5 | 2 | +2 | vase should not be moved every night and should never be on bed |
| c045 | keys | in_region | bedroom | waking_up | 1 | 0.8 | 3 | +2 | keys are retrieved and kept in a pocket and not left out |
| c056 | wallet | in_region | bedroom | wake_up | 1 | 0.8 | 3 | +2 | only likely if James is a messy person |
| c024 | drinkware | on_top | kitchen.counter_1 | lunch_break | 3 | 0.5 | 2 | -1 |  |
| c030 | keys | next_to | living_room.table_1 | watching_tv | 0 | 0.4 | 1 | +1 |  |
| c016 | wallet | on | tv.couch_1 | watching TV | 2 | 0.3 | 1 | -1 |  |
| c033 | stool | next_to | living_room.fireplace_1 | relaxing_watching_tv | 1 | 0.7 | 2 | +1 |  less likely if there already is seating or a couch there |
| c039 | keys | near | bedroom_1.cabinet_1 | relaxing_in_bed | 1 | 0.65 | 2 | +1 | keys should be put in one spot in the house out of routine |
| c026 | bowl | on_top | kitchen.counter_1 | breakfast | 3 | 0.7 | 2 | -1 |  |
