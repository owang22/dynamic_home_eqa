# p_c6a1 — Evening sequence: cook at 19:00, dinner at 20:00, TV winds down to 22:30

This document captures the full evening arc on both weekdays and weekends. Cooking starts at 19:00: the pan comes out of the cupboard and the spatula out of the drawer onto the counter; the recipe book is pulled from the pantry shelf to the counter. Dinner is served at 20:00 at the dining table: plates, glasses, and Marco's water bottle migrate from the kitchen to the table. By 21:00 the dishes are being cleared and the residents move to the living room for TV: the remote goes from the TV stand to the coffee table, the blanket shifts from the couch to the coffee table, and the snack bowl appears on the coffee table. By 22:00–22:30 the TV winds down and the remote is dropped on the living-room floor. The cooking window (19:00–20:00) is confirmed by the pan at counter_k1 at 19:00 and the spatula at counter_k1 at 19:00 (×3) and 20:00. The dinner window (20:00–21:00) is confirmed by plate_omar at dining_table_d1 at 20:00 (×2), glass_omar at dining_table_d1 at 20:00, and water_bottle_marco at dining_table_d1 at 20:00 (×2). The TV window (21:00–22:30) is confirmed by remote_shared at coffee_table_l1 at 21:00, snack_bowl_shared at coffee_table_l1 at 21:00 and 22:00 (×3), and blanket_shared at coffee_table_l1 at 22:00 (×2).

What would refute this: a look at the counter at 19:30 that finds neither pan nor spatula; a look at the dining table at 20:30 that finds no plates or glasses; or a look at the coffee table at 21:30 that finds no remote or snack bowl.

```json
{
 "claims": [
  {
   "claim": "The pan is on the counter during the 19:00 cooking window",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Omar's plate is at the dining table during dinner",
   "target": "plate_omar",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 20,
   "to": 21
  },
  {
   "claim": "The remote is on the coffee table during active TV watching",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22
  },
  {
   "claim": "Marco's water bottle is at the dining table during dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 20,
   "to": 21
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "counter_k1",
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
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 20,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
