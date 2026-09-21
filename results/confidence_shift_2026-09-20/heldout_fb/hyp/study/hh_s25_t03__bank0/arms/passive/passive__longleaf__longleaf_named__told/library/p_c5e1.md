# p_c5e1 — Evening cooking at 19:00 and shared dinner at 20:00

Both residents cook and eat together in the evening. The cooking window is narrow: the pan and spatula come out of the cupboard/drawer at around 18:30 and are on the counter by 19:00, used for about an hour. Dinner is served at the dining table around 20:00, where both residents' plates, glasses, and the serving dish appear. The recipe book is pulled from the pantry shelf at 19:00 (seen there alongside the counter). By 22:00 the table is cleared and everything returns to the cupboard.

What sets this apart: p_9e3f claims cooking at 19:00 but also claims the pan is in the cupboard at 18:00 (which the data supports) AND at the counter at 19:00 (which the data supports). My document adds the full dinner sequence: plates and glasses at the dining table 20–22, which p_9e3f does not cover. The serving dish also appears at the dining table at 20:00, confirming a shared meal.

What would refute it: finding the pan in the cupboard at 19:30 (cooking not yet started or already done), finding plates still in the cupboard at 20:30 (dinner not yet served), or finding the serving dish at the counter rather than the dining table at 20:00.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter during the cooking window",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Omar's plate is at the dining table during dinner",
   "target": "plate_omar",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21.5
  },
  {
   "claim": "The serving dish is at the dining table during dinner",
   "target": "serving_dish_shared",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 20,
   "to": 21.5
  },
  {
   "claim": "Omar's glass is at the dining table during dinner",
   "target": "glass_omar",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "plate_omar": [
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
    "to": 20,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "plate_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 12,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
