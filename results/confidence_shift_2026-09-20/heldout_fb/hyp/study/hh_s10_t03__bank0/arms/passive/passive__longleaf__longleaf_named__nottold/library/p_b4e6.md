# p_b4e6 — Weekday dinner is light assembly at the dining table, not full cooking

Yuki's weekday dinner is not a from-scratch cooking session. At 18:00 the cutting board is on the counter (she is doing some prep—chopping vegetables, assembling a salad), but the pan is in the cupboard and the pot is in the cupboard. There is no active stovetop cooking. The dinner is assembled (maybe a salad, reheated leftovers, or a simple cold dish) and eaten at the dining table around 19:00. The knife stays in the drawer (the 18:00 sighting confirms drawer_k_k1). The shopping bag, which was on the counter at 11:00 (Omar unpacking groceries during his morning at home), is back in the pantry by 18:00.

What sets this apart: it explicitly places the pan and pot in the cupboard during the 18:00–20:00 window (no cooking), while the cutting board IS on the counter (some prep). This distinguishes it from p_c007 (shared dinner cooking with pan on counter) and p_8d2c (solo kitchen-table meal). The dinner is at the *dining* table, not the kitchen table.

Refutation: if the robot finds the pan on the counter or stovetop at 18:30, or the pot on the counter, or the cutting board in the sink at 18:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The shared cutting board is on the counter at 18:30 on a weekday (light prep for dinner)",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The shared pan is in the cupboard at 18:30 on a weekday (no active cooking)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The shared pot is in the cupboard at 18:30 on a weekday (not used for dinner)",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The kitchen knife stays in the drawer at 18:30 on a weekday (no knife-based cooking)",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  }
 ],
 "targets": {
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "plate_yuki": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekday",
    "from": 11,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ]
 }
}
```
