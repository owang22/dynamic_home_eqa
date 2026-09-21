# p_8e4d — No-Cook Weekday Evening: The Pan Stays in the Cupboard

The sightings are unambiguous: on both sighted weekdays the pan is in cupboard_k1, and the 9-17h looks at the counter found the cutting board, kettle, knife block, and snack bowl absent five times each. p_b9c4's claim of the pan on the counter at 18:00 has accumulated 9 against-counts; p_c1d6's has 13. The weekday evening meal is a no-stove affair. The kitchen counter holds glasses (glass_hana at counter 18:00, 19:00, 20:00), the snack bowl (counter 18:00, 19:00), and plates at the kitchen table (plate_priya at 18:00, plate_hana at 20:00), but the pan, pot, and kitchen knife remain in their storage.

What sets this apart: at 18:00 on a weekday, pan_shared is at cupboard_k1 and kitchen_knife_shared is at drawer_k_k1. The cutting board is NOT at the counter during 9-17h (five empty looks) but returns to the counter in the evening. The dinner is assembled, not cooked: sandwiches, salads, or reheated food that bypasses the stove entirely.

What would refute it: pan_shared sighted at counter_k1 at 18:00 on a weekday, or kitchen_knife_shared sighted at counter_k1 at 18:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday (no stove cooking for dinner)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 20
  },
  {
   "claim": "The kitchen knife is in the drawer at 18:00 on a weekday (no knife work for dinner)",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17,
   "to": 20
  },
  {
   "claim": "Hana's glass is on the kitchen counter at 19:00 on a weekday (drinks during no-cook dinner)",
   "target": "glass_hana",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The pot is in the cupboard at 18:00 on a weekday (no pot cooking)",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 20
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
