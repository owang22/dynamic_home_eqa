# p_9a4c — 20:00 dinner at the dining table; pan and board go to the sink, not the counter

The passes show a clear 20:00 meal: Yuki's plate, glass, water bottle, and phone all appear at dining_table_d1 at the 20:00 pass (2 sightings each for plate, glass, bottle; 1 for phone), and resident_1 is in the dining room at 20:00 on days 0 and 1. By 22:00 everything is back in the cupboard or sink. Crucially, the pan and cutting board do NOT sit on the counter during dinner — the pan goes cupboard → sink (20:00: sink 2, cupboard 1), and the cutting board goes counter → sink (20:00: sink 2, counter 1). The "pan on counter during cooking" model (p_c007) has been contradicted 13 times total.

This document predicts the 20:00 dining-table cluster and the post-dinner sink location for cookware. It is refuted if the pan is found on the counter at 20:00, or if Yuki's plate is in the cupboard at 20:00, or if the dinner cluster shifts to 18:00–19:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's plate is at the dining table during the 20:00 meal on weekdays",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The pan is at the sink (washed) by 20:00 on weekdays, not on the counter",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 22
  },
  {
   "claim": "Yuki's water bottle is at the dining table during the 20:00 meal on weekdays",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The cutting board is at the sink by 20:00 on weekdays, not on the counter",
   "target": "cutting_board_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 22
  }
 ],
 "targets": {
  "plate_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   }
  ]
 }
}
```
