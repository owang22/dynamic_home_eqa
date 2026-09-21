# p_9b2d — Weekend Brunch at Nine, Cook at Five, Dinner at Seven

The weekend kitchen runs on a different clock than the weekday. Both residents sleep in, then gather at the kitchen table around 09:00 for a leisurely brunch: Priya's bowl and mug appear at kitchen_table_k1 (bowl x3, mug x2 at 09:00), Hana's bowl and mug also show up (bowl x1 at 09:00 and 10:00, mug x1 at 09:00). Hana's plates sit at the kitchen table from 14:00 to 16:00 (x1 at 14:00, x3 at 16:00), suggesting a mid-afternoon snack or light meal. The real cooking window is 17:00-to-19:00: the kitchen knife is on the counter (x2 at 17:00, x1 at 18:00), the pan is on the counter (x1 at 17:00, x1 at 18:00), and the recipe book is on the counter (x1 at 17:00). Dinner is served at the kitchen table around 19:00-to-20:00 (Priya's plate x1 at 19:00 and 20:00, Hana's plate x1 at 19:00, Priya's glass x1 at 18:00, 19:00, 20:00).

What sets this apart from p_e5f0 (which puts plates at the table at noon for brunch and the guitar ON_PERSON at 16:00) and p_b9c4 (which puts the pan on the counter at 18:00 weekday): the weekend brunch is at 9, not noon, and the cooking starts at 17, not 18. If the robot finds the kitchen counter clear at 17:00 on a Saturday, or the bowls back in the cupboard at 09:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Priya's bowl is on the kitchen table during weekend brunch",
   "target": "bowl_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 9,
   "to": 10
  },
  {
   "claim": "The kitchen knife is on the counter during weekend dinner prep",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 17,
   "to": 18
  },
  {
   "claim": "Priya's plate is on the kitchen table during weekend dinner",
   "target": "plate_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 19,
   "to": 20
  }
 ],
 "targets": {
  "bowl_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
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
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
