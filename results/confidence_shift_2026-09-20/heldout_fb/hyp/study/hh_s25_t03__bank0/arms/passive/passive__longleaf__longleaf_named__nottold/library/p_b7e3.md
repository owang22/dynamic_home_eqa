# p_b7e3 — — Weekday cooking at 19:00; dinner at the dining table 20:00; TV wind-down to 22:30 (fork of p_6a1e)

The parent document p_6a1e specified the cooking-and-dinner sequence for "both" weekday and weekend, but the sightings show this is a weekday-only ritual. The pan is in the cupboard at 19:00 on weekends, Marco's water bottle is at the dish rack (not the dining table) at 20:00 on weekends, and Omar's plate is split between cupboard and dining table on weekend evenings. The fork restricts all cooking, dinner-table, and active-TV blocks to weekdays. On weekends the kitchen stays cold at 19:00 and the remote never leaves the TV stand.

What changed from the parent: every block that places the pan, spatula, plates, glasses, water bottle, mug, or remote at a "in-use" receptacle is now `weekday` instead of `both`. The blanket and recipe book remain `both` because they do migrate on weekend evenings as well (the recipe book to the counter at 20:00 on weekends, the blanket to the coffee table from 21:00). What would refute this fork: the pan on the counter at 19:00 on a Saturday, or the water bottle at the dining table at 20:00 on a Sunday.

```json
{
 "claims": [
  {
   "claim": "The pan is on the counter during the 19:00 cooking window on weekdays",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "Omar's plate is at the dining table during weekday dinner",
   "target": "plate_omar",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The remote is on the living-room floor during late weekday evening TV",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "Marco's water bottle is at the dining table during weekday dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The spatula is on the counter during the weekday cooking window",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
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
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
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
    "days": "weekday",
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
    "from": 18.5,
    "to": 20.5,
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
    "days": "weekday",
    "from": 19.5,
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
    "days": "weekday",
    "from": 19.5,
    "to": 21,
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
    "days": "weekday",
    "from": 21,
    "to": 23.5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 19,
    "to": 19.5,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "class:blanket": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
