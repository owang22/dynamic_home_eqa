# p_4c8f — No Weekday Cook at Six: the kitchen stays cold until late

The evidence is unambiguous: across multiple recent passes, the pan, pot, cutting board, and kitchen knife were *not* on the kitchen counter at 18:00 on weekdays. They sat in the cupboard and drawer where they rest. Both residents were in the kitchen at 18:00 on Tuesday, but they were there for drinks, a quick snack, or conversation — not to fire up the stove. Hana comes home at 5:30 from a full office day; she is not cooking a three-course meal at 6. If dinner is cooked at all, it happens at 19:30 or later, and on some weekdays they simply order in or eat cereal.

This document directly contradicts p_b9c4 and p_c1d6, which place the pan and pot on the counter at 18:00. It predicts the cooking implements stay in their storage locations through the 17:00–19:30 window on weekdays. The kitchen table holds the fruit bowl and mugs (drinks), not plates and serving dishes.

What would refute it: a sighting of the pan or pot on the counter between 17:00 and 19:00 on a weekday, or the cutting board out of the drawer in that window. If the robot sees Hana actively cooking at 18:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday (no cooking at six)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The kitchen knife is in the drawer at 18:00 on a weekday",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The cutting board is in the drawer at 18:00 on a weekday",
   "target": "cutting_board_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Hana's mug is on the kitchen table at 18:00 on a weekday (drinks, not dinner)",
   "target": "mug_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 19.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 19.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "weekday",
    "from": 7,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekday",
    "from": 14,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "both",
    "from": 7,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
