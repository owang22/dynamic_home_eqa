# p_2e9c — Dinner at the Kitchen Table, Then the Couch

The 18:00–20:30 window is dinner time at the kitchen table. Evidence: plate_hana appears on kitchen_table_k1 at 20:00 (×2), plate_priya is on kitchen_table_k1 at 18:00 (×1), mug_hana is on kitchen_table_k1 at 18:00 (×1), and glass_hana is on counter_k1 at 18:00–20:00 (×3) before appearing at kitchen_table_k1 at 20:00. The snack bowl is on counter_k1 at 18:00 (×1) and 19:00 (×3), then moves to coffee_table_l1 at 21:00 (×2). After 20:30 the residents shift to the living room: mugs and glasses migrate to the coffee table, the remote is used, and the blanket is on the couch.

This document differs from p_6e3a (which also places dinner at the kitchen table but has very low weight and a pot-on-counter claim that keeps failing) by *not* claiming the pot is on the counter during dinner (it may be at the stove) and by explicitly modelling the 20:30 transition. It differs from p_c9d4 (Late Night) by starting the living-room phase at 20:30 rather than 20:00.

Refutation: plates consistently found in the cupboard or sink at 19:00–20:00 (not on the kitchen table), or the snack bowl on the coffee table before 20:00.

```json
{
 "claims": [
  {
   "claim": "Hana's plate is on the kitchen table at 19:30 on a weekday (dinner in progress)",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  },
  {
   "claim": "Hana's mug is on the kitchen table at 18:30 on a weekday (dinner drink)",
   "target": "mug_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 19.5
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 19:00 on a weekday (dinner side, not yet moved to TV area)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The snack bowl is on the coffee table at 21:00 on a weekday (TV session started)",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  }
 ],
 "targets": {
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
