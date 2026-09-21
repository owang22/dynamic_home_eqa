# p_3a8d — Dinner cooking is real: pan and cutting board on the counter at 19:00

The 19:00 patrol passes show the shared pan on the counter (2 sightings) and the cutting board on the counter (2 sightings), while at 18:00 the pan is still in the cupboard (1 sighting) and the cutting board is on the counter (1 sighting). This means actual cooking happens between 18:00 and 19:00 on weekdays: the pan comes out of the cupboard, the cutting board is used for prep, and both end up on the counter during the cooking window. The kitchen knife is mostly in the drawer (1 at 18:00, 1 at 19:00) with one sighting on the counter at 19:00, suggesting the knife is used briefly but returned to the drawer. The pot stays in the cupboard (1 sighting at 18:00), so dinner uses the pan, not the pot.

What sets this apart: p_8d2c, p_7b3e, and p_b4e6 all claim the pan stays in the cupboard during the 18:00–19:00 window. p_c007 puts the pan on the counter but also the cutting board, and its claims have been against 10 and 12 times respectively. This document agrees the pan is on the counter at 19:00 but narrows the window: the pan is in the cupboard at 18:00 and on the counter by 19:00, so the cooking window is 18:30–19:30, not the full 18:00–19:00. If the robot finds the pan in the cupboard at 19:00 on a weekday, this document is wrong.

What would refute it: the pan consistently in the cupboard at 19:00 on weekdays, or the cutting board in the sink at 19:00.

```json
{
 "claims": [
  {
   "claim": "The shared pan is on the kitchen counter at 19:00 on a weekday (active cooking)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The shared cutting board is on the kitchen counter at 19:00 on a weekday (prep in progress)",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19.5
  },
  {
   "claim": "The shared pot stays in the cupboard at 19:00 on a weekday (dinner uses the pan, not the pot)",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The shared pan is in the cupboard at 18:00 on a weekday (not yet taken out for cooking)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0.5,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0.5,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0.5,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "rarely"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0.5,
    "to": 6,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
