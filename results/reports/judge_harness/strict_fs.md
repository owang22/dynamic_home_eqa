# Judge harness — `strict_fs`

- style: **strict**, thinking: **False**, temperature: **0.7**, k: **1**
- scored 48/48 EVAL candidates

## Headline

- **Spearman rank corr vs human band: 0.73**
- exact-band match: 0.50   within-one: 0.92
- **over-scored (judge > human): 0.33**   under: 0.17

## Band separation (judge score within each human band)

| human band | n | mean judge score | std |
|---|---|---|---|
| 3 typical | 12 | 0.83 | 0.08 |
| 2 plausible-uncommon | 13 | 0.57 | 0.19 |
| 1 contrived | 13 | 0.43 | 0.25 |
| 0 absurd | 10 | 0.26 | 0.18 |

## Confusion (rows = human band, cols = predicted band)

| human ↓ / pred → | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 3 | 0 | 0 | 2 | 10 |
| 2 | 0 | 4 | 6 | 3 |
| 1 | 2 | 4 | 5 | 2 |
| 0 | 4 | 4 | 2 | 0 |

## Dinner-laptop candidates (the case the judge should nail)

| id | object | anchor | activity | human | judge score | pred |
|---|---|---|---|---|---|---|
| c000 | laptop | kitchen.table_1 | breakfast | 2 | 0.6 | 2 |
| c001 | phone | kitchen.table_1 | snacking | 3 | 0.85 | 3 |
| c002 | phone | kitchen.table_1 | breakfast | 3 | 0.7 | 2 |
| c020 | laptop | dining_room.counter_2 | eating_breakfast | 2 | 0.6 | 2 |
| c021 | laptop | dining_room.counter_2 | lunch | 1 | 0.4 | 1 |
| c022 | phone | dining_room.counter_1 | lunch | 2 | 0.5 | 2 |
| c023 | laptop | kitchen.counter_1 | lunch_break | 2 | 0.7 | 2 |

## Worst disagreements

| id | object | rel | anchor | activity | human | judge | pred | gap | notes |
|---|---|---|---|---|---|---|---|---|---|
| c041 | potted_plant | in_region | bedroom | sleeping | 0 | 0.6 | 2 | +2 | plants are never moved for nightly sleeping ambience |
| c059 | keys | in_region | living_room | light_housework | 1 | 0.9 | 3 | +2 | unusual for keys to be stored in either the living room or bathroom and should instead be kept in a pocket or bedroom |
| c050 | vase | in_region | kitchen | clean_up_after_dinner | 0 | 0.5 | 2 | +2 | dinner cleanup would not involve moving the vase |
| c045 | keys | in_region | bedroom | waking_up | 1 | 0.75 | 3 | +2 | keys are retrieved and kept in a pocket and not left out |
| c053 | potted_plant | in_region | bedroom | organizing_workspace | 2 | 0.25 | 1 | -1 |  |
| c008 | bowl | on_top | bedroom_1.bed_1 | reorganizing bedroom | 1 | 0.7 | 2 | +1 | bowls are not used for organizing |
| c013 | laptop | in_region | bedroom | preparing_for_bed | 2 | 0.3 | 1 | -1 |  |
| c016 | wallet | on | tv.couch_1 | watching TV | 2 | 0.3 | 1 | -1 |  |
| c010 | potted_plant | in_region | outdoor | reading | 0 | 0.35 | 1 | +1 |  |
| c009 | tv | in_region | kitchen | eating_dinner | 1 | 0.0 | 0 | -1 | tv is not easily moved |
