# p_4f8e — Marco's water bottle: desk to sink to dinner table

Marco works from his bedroom desk (desk_b1) on weekdays. His water bottle sits beside the laptop in the morning while he works, but around mid-day he carries it to the kitchen to refill it, and it lingers in the sink or dish-rack area for several hours. By dinner time (around 20:00) he brings it to the dining table where he and Omar eat together. The bottle is NOT at the desk during the 12–17 window; it is in the kitchen. This explains the 32 empty looks at desk_b1 during work hours: the bottle is simply not there.

What sets this apart: p_2d6e and p_8f4c place the bottle at the desk or at the sink during mid-day, but the data shows a clear three-phase cycle (desk → kitchen → dining table) with the kitchen phase lasting the longest. The bottle is at the dish_rack at 18:00, at the sink at 19:00, and at the dining table at 20:00 — a progression, not a single resting spot.

What would refute it: finding the water bottle at desk_b1 during 12–17 on a weekday, or finding it at the dining table before 19:00, or finding it at a receptacle other than sink/dish_rack during the 12–18 window.

```json
{
 "claims": [
  {
   "claim": "Marco's water bottle is at his desk during the morning work window",
   "target": "water_bottle_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 11
  },
  {
   "claim": "Marco's water bottle is at the dining table during dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21.5
  },
  {
   "claim": "Marco's water bottle is in the kitchen sink area during the mid-day gap",
   "target": "water_bottle_marco",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "Marco's water bottle is at the dish rack just before dinner",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 18,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
