# p_9b1c — Omar's weekday arc: tablet migrates nightstand to kitchen table to chair; lunch at 12:30

Omar is home from roughly 6:00 until he leaves for his afternoon shift at 13:40. His tablet starts the night on the nightstand (charging), moves to the kitchen table around 9:00 when he's having coffee and browsing, and by 18:00 it is in the kitchen chair where it stays while he is at work (he leaves it there rather than taking it to the office). His weekday lunch is a proper sit-down at the kitchen table around 12:15–13:15: glass of water, a plate, sometimes a bowl. He leaves for work at 13:40 and does not return until 23:00.

What sets this apart: p_3d8e covers only the lunch window; p_7e5b (retired) and p_c4d9 (retired) attempted the tablet migration but were retired. This document unifies the full 06:00–13:40 home block with the tablet's three positions and the lunch items. The tablet sightings (03:00 nightstand, 09:00 kitchen_table, 10:00 kitchen_table, 18:00 chair_k1) and the glass/plate at kitchen_table at 12:00–13:00 are the core support.

What would refute it: if the tablet is consistently found at the nightstand during 09:00–13:00 (not migrated), or if Omar's lunch items are at the dining table rather than the kitchen table, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the kitchen table at 10:00 on a weekday (morning browsing with coffee)",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Omar's tablet is in the kitchen chair at 18:00 on a weekday (he left for work and it stayed there)",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Omar's glass is at the kitchen table at 12:30 on a weekday (lunch in progress)",
   "target": "glass_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13.5
  },
  {
   "claim": "Omar's tablet is on the nightstand at 03:00 on a weekday (charging overnight)",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 7
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "glass_omar": [
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 1,
    "to": 7,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "plate_omar": [
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
