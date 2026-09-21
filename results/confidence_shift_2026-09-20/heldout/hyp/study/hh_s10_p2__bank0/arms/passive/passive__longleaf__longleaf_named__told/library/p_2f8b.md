# p_2f8b — Weekend kitchen: midday cooking at the counter, 20:00 dinner at the table

On weekends the kitchen routine shifts. Both residents are home, and the cooking happens earlier and more leisurely. Omar's bowl appears at the kitchen counter from midday through the evening (he is cooking, not just eating at the table). The pan, knife, and spatula all appear at the counter around 20:00 on weekends (active cooking for dinner), then return to the drawer/cupboard by 22:00. The dinner itself is at the dining table at 20:00: Yuki's plate, glass, and water bottle are there, and Omar's plate appears at the dining table slightly later (22:00 on Saturday, suggesting he eats a bit after Yuki or the meal runs long with friends on Sunday).

In the morning (around 10:00), the kitchen table is the breakfast spot: both mugs, both bowls, and Omar's vitamins all appear there. This is the same as the weekday 10:00 pattern for Omar, but on weekends Yuki is also present and uses the kitchen table for her morning bowl.

The shopping bag moves to the pantry shelf on weekends (stored after the midday errand) rather than sitting on the counter as it does on weekdays. Omar's lunchbox goes to the cupboard on weekends (not needed for a work shift) rather than hanging at the entry hook.

This document is refuted if the pan is in the cupboard during the 20:00 weekend window (no cooking happening), or if the plates are at the kitchen table rather than the dining table at 20:00.

```json
{
 "claims": [
  {
   "claim": "Omar's bowl is on the kitchen counter during weekend midday cooking",
   "target": "bowl_omar",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 12,
   "to": 20
  },
  {
   "claim": "The pan is on the counter during weekend dinner cooking at 20:00",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Yuki's plate is at the dining table during the weekend 20:00 meal",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Omar's lunchbox is in the cupboard on weekends (no work shift)",
   "target": "lunchbox_omar",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "bowl_omar": [
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
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pan_shared": [
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
    "to": 19,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 19,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "plate_yuki": [
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
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "mug_omar": [
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
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "vitamins_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "bowl_yuki": [
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
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
