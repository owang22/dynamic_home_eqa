# p_5b8e — Weekend Brunch at 15:00, Dinner Cook at 17:30

A fresh document focused on the weekend meal and cooking pattern, which no existing document captures well. The Saturday evidence shows: plates at the kitchen table at 14:00 and 16:00 (a late brunch or lunch, not the weekday 12:00 lunch); the pan, kitchen knife, and recipe book on the counter at 17:00–18:00 (dinner cooking begins); the spatula on the counter at 19:00 (cooking in progress); glass_priya at the kitchen table 18:00–20:00 then the coffee table 21:00–22:00 (dinner, then TV); and the snack bowl on the coffee table at 21:00 (TV session).

What sets this apart: on a Saturday at 15:00, plates and mugs are at the kitchen table (brunch in progress), whereas weekday documents put them in the cupboard at that hour. At 17:30 Saturday, the pan and knife are on the counter (cooking has started), whereas the weekday cooking window is 18:30–19:30. The weekend dinner is an hour earlier than the weekday dinner. At 19:30, glasses are at the kitchen table (dinner in progress), then by 21:00 they migrate to the coffee table (TV).

What would refute it: plates in the cupboard at 15:00 Saturday, the pan in the cupboard at 17:30 Saturday, or glass_priya at the nightstand at 19:00 Saturday.

```json
{
 "claims": [
  {
   "claim": "Hana's plate is on the kitchen table at 15:00 on a Saturday (late brunch)",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 14,
   "to": 16.5
  },
  {
   "claim": "The pan is on the kitchen counter at 17:30 on a Saturday (dinner cooking started)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 17,
   "to": 18.5
  },
  {
   "claim": "Priya's glass is on the kitchen table at 19:00 on a Saturday (dinner in progress)",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The kitchen knife is on the counter at 17:30 on a Saturday (prep for dinner)",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 17,
   "to": 18.5
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
    "from": 14,
    "to": 16.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20.5,
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
    "from": 14,
    "to": 16.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
    "from": 9,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
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
    "from": 9,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "from": 9,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
    "from": 9,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
    "from": 17,
    "to": 19.5,
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
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20.5,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
