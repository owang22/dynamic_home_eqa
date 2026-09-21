# p_9d2c — Evening triptych: cook at 19, eat at 20, watch at 21

The evening follows a tight three-act structure on both weekdays and weekends. Act one (19:00–20:00): cooking at the kitchen counter. The pan comes out of the cupboard, the spatula out of the drawer, the knife out of the drawer, the recipe book off the pantry shelf, and the cutting board is already on the counter. Everything migrates to the counter surface for the cooking window. Act two (20:00–21:00): dinner at the dining table. Plates come out of the cupboard, glasses from the cupboard or counter, the water bottle from the dish rack or sink, the serving dish from the cupboard. The residents sit at the dining table for the meal. Act three (21:00–22:30): TV in the living room. The remote leaves the TV stand for the coffee table, the blanket shifts from the couch to the coffee table, the snack bowl appears on the coffee table, and Marco's mug moves from the desk to the coffee table. By 22:00–22:30 the remote drops to the living-room floor as attention wanders.

This document is distinguished by its precise timing: the pan is on the counter at 19:00 (confirmed by the weekday sighting), the plates are at the dining table by 20:00 (confirmed), and the remote is at the coffee table at 21:00 (confirmed). It would be refuted if the pan were still in the cupboard at 19:30, if plates were at the dining table before 19:30, or if the remote were on the floor before 21:30.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter during the 19:00 cooking window on weekdays",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Omar's plate is at the dining table during the 20:00 dinner window",
   "target": "plate_omar",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 20,
   "to": 21
  },
  {
   "claim": "The remote is on the coffee table during active TV watching at 21:00",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22
  },
  {
   "claim": "The spatula is on the counter during the 19:00 cooking window",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The blanket is on the coffee table during the late-evening TV wind-down",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22,
   "to": 23
  }
 ],
 "targets": {
  "pan_shared": [
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
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
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
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.5,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "plate_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "plate_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "glass_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20.5,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21.5,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20.5,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
