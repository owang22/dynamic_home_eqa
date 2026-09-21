# p_4e9a — The 19:00 Cook, 20:00 Dinner, 20:30 Coffee Table Migration

Hana comes home at 18:00 and starts cooking immediately, but the tools don't all hit the counter at once. The knife comes out first (visible on the counter by 18:00), then the pan and pot follow around 18:30–19:00. The cutting board is a permanent counter resident — it's there at 03:00, 18:00, and 19:00 alike. Dinner is eaten at the kitchen table from roughly 19:00 to 20:30. The snack bowl sits on the counter as a side during dinner prep (17:00–20:00) and only migrates to the coffee table at 20:00 when TV starts. The remote and blanket follow the same 20:00 migration. This document corrects the earlier "17:30 cook" documents (p_b9c4, p_c1d6) that placed the pan and pot on the counter too early, and the "late night" document (p_c9d4) that had the snack bowl on the coffee table until 23:00.

What sets this apart: the cooking window is 18:30–20:30 (not 17:30–19:00), the snack bowl's coffee-table window is 20:00–22:30 (not 20:00–23:00), and the remote leaves the TV stand at 19:30 (not 21:00). If the pan is found on the counter before 18:30, or the snack bowl is found on the coffee table after 22:30, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter at 19:30 on a weekday (cooking in progress)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 18:30 on a weekday (dinner side, not yet moved)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The snack bowl is on the coffee table at 21:00 on a weekday (TV session)",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "The remote is on the coffee table at 20:30 on a weekday (moved from TV stand for evening)",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 21
  },
  {
   "claim": "The blanket is on the coffee table at 21:30 on a weekday (TV session, not the couch)",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 17.5,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 16.5,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19.5,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19.5,
    "at": "couch_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 13,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 18,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23.5,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ]
 }
}
```
