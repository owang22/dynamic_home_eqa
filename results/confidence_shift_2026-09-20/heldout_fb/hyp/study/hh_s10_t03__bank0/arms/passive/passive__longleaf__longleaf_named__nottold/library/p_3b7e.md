# p_3b7e — The 19:00 quick cook: pan emerges at 19, dinner at the dining table

Yuki arrives home at 17:30 and dumps her water bottle at the entry hook. By 19:00 it has migrated to the dining table, where she eats. The cook is brief: the pan is still in the cupboard at 18:00 and only appears on the counter at 19:00. The cutting board is already on the counter at 18:00 (perhaps set out in anticipation), and the kitchen knife stays in the drawer throughout — no heavy chopping. Dinner is eaten at the dining table with her glass and water bottle; by 20:00 the glass is still there (3 of 3 passes) and the water bottle is still there (2 of 2).

This document differs from p_c007, which places the pan and cutting board on the counter from 18:00 (the pan is in the cupboard at 18:00 in the evidence). It also differs from p_8d2c and p_7b3e, which deny any cooking at all (the pan does come out at 19:00). The cook window is 19:00–19:30, not 18:00–19:30.

Refutation: the pan sighted on the counter at 18:00, or the glass/water bottle absent from the dining table during 19–20h on multiple passes.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter at 19:15 on a weekday (just emerged from the cupboard)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 19.5
  },
  {
   "claim": "Yuki's glass is at the dining table at 19:30 on a weekday (dinner in progress)",
   "target": "glass_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Yuki's water bottle is at the dining table at 19:30 on a weekday (dinner in progress)",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The kitchen knife stays in the drawer at 18:30 on a weekday (no knife-based prep before 19)",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
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
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
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
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
