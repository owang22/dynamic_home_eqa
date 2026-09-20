# p_4cf1 — The Minimalist Kitchen: Dishes stay in the cupboard

This household is tidy: after each meal, dishes go straight back into the cupboard. At any given patrol time, the kitchen table holds only the fruit bowl (and perhaps a bowl_yuki for the dog or a snack). The mugs, plates, glasses, and bowls are in cupboard_k1 except during the 30 minutes of actual eating. The counter holds the kettle and cutting board as a permanent setup. The drawer holds the knife and spatula.

What sets this hypothesis apart: at the 16:00 or 20:00 patrol, the kitchen table has at most 1–2 items (fruit bowl, maybe one bowl). The cupboard is full. This directly contradicts p_06b3 where the table is full of mugs and plates in the evening.

What would refute it: three or more mugs/plates/bowls sighted on the kitchen table at 20:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Yuki's mug is in the cupboard at midday on weekdays",
   "target": "mug_yuki",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Nora's mug is in the cupboard at midday on weekdays",
   "target": "mug_nora",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Nora's plate is in the cupboard in the evening",
   "target": "plate_nora",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Yuki's plate is in the cupboard in the evening",
   "target": "plate_yuki",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 20,
   "to": 23
  }
 ],
 "targets": {
  "mug_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
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
   }
  ],
  "bowl_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "bowl_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "glass_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
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
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ]
 }
}
```
