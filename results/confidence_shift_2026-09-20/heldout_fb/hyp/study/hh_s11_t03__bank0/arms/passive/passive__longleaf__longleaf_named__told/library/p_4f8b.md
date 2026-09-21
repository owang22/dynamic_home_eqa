# p_4f8b — Weekend Kitchen; Shared Meals at Relaxed Hours, Priya Cooks

On Saturday both residents are home for all three meals, so the kitchen table is the shared dining spot at relaxed hours: breakfast 8:30–10:00, lunch 12:30–14:00, dinner 18:30–20:00. Priya does the cooking (light meals: a pan on the counter, the knife and cutting board in use). Hana's and Priya's plates, bowls, mugs, and glasses are at the kitchen table during each meal window and return to the cupboard or sink between meals. The snack bowl migrates to the coffee table in the afternoon for grazing between meals. This differs from the weekday documents where Hana is at work during lunch and dinner, so meals are often solo or staggered.

What sets this apart: p_e8b2 and p_7a3e place weekday breakfast at 7:30–9:00 with both present, but on Saturday the timing is later and lunch is a genuine shared meal (Hana is home). The pan and knife are on the counter during lunch prep (12:00–13:00) and dinner prep (18:00–19:00), not just at one meal. Mugs are at the kitchen table during meals (not in the cupboard), matching the weekday 8:00 sightings where mugs were at the kitchen table.

What would refute it: if Hana's plate is sighted in the cupboard or at the sink during the 12:30–14:00 window, the shared-lunch claim fails. If the pan is in the cupboard or dish rack during 12:00–13:00, the cooking claim weakens. If mugs are in the cupboard during the breakfast window (8:30–10:00), the meal-at-table claim is contradicted. If the snack bowl stays on the counter all afternoon, the coffee-table migration is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's plate is at the kitchen table during Saturday lunch",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 12.5,
   "to": 14
  },
  {
   "claim": "Priya's mug is at the kitchen table during Saturday breakfast",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 8.5,
   "to": 10
  },
  {
   "claim": "The pan is on the counter during Saturday lunch cooking",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 12,
   "to": 13
  },
  {
   "claim": "The kitchen knife is on the counter during Saturday dinner prep",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Hana's bowl is at the kitchen table during Saturday lunch",
   "target": "bowl_hana",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 12.5,
   "to": 14
  }
 ],
 "targets": {
  "plate_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "bowl_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
