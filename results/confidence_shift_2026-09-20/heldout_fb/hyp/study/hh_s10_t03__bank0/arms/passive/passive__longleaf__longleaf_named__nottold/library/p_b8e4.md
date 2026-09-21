# p_b8e4 — Yuki's evening arrival arc: entry hook to dining table, 17:30 to 20:30

Yuki comes home around 17:30 on weekdays. Her water bottle is the first thing the robot catches in transit: at 18:00 it is still at the entry hook (1/1 pass), but by 19:00 it is at the dining table (4/4 passes) and stays there through 20:00 (2/2). Her glass follows a similar arc: at 18:00 it is on the kitchen counter (1/1, just taken out of the cupboard), and by 19:00 it is at the dining table (2/2), still there at 20:00 (3/3). Her plate is in the cupboard at 18:00 (1/1) and appears at the dining table by 19:00 (1/3, the others being sink or cupboard — the meal is just starting). By 22:00 the glass has migrated to the bedroom nightstand (3/3) for her bedtime water, and the water bottle is back in the dish rack by 03:00 (3/3).

This document is distinguished by tracking Yuki's personal items through the 17:30–21:00 window with specific receptacles at specific times, rather than the broad "dining table 18–20" of p_c007 or the "entry hook all evening" of p_b2c8. It agrees with p_3a7f (retired) on the dining-table dinner at 19:00 but adds the water bottle and glass as tracked items.

What would refute it: the water bottle at the entry hook at 19:00, the glass at the cupboard at 19:30, or the glass at the dining table at 22:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's water bottle is at the dining table at 19:30 on a weekday (dinner in progress)",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  },
  {
   "claim": "Yuki's glass is at the dining table at 19:30 on a weekday (dinner in progress)",
   "target": "glass_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  },
  {
   "claim": "Yuki's glass is at the bedroom nightstand at 22:30 on a weekday (taken to the bedroom for the night)",
   "target": "glass_yuki",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 23
  },
  {
   "claim": "Yuki's water bottle is at the dish rack at 03:00 on a weekday (washed and dried overnight)",
   "target": "water_bottle_yuki",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 2,
   "to": 6
  }
 ],
 "targets": {
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "plate_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
