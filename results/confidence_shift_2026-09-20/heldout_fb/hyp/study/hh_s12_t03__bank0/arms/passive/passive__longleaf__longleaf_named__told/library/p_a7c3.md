# p_a7c3 — The 19:30 dinner, 20:00 dog, 21:00 TV

Elena comes home at 5:30 and starts cooking by 6:30. The pot and recipe book go to the counter for a focused 18:30–19:30 cooking window, then the pot is put away. Dinner is set at the dining table at 19:30 and runs until about 21:00; plates, glasses, and water bottles are at the table at 20:00 (the robot's 20:00 pass confirms this). While the meal is being eaten, the dog gets its evening feed around 20:00–21:00 (food bag on the kitchen floor at 20:00 and 21:00). After dinner, the table is cleared and the evening shifts to the living room: TV starts around 21:00, the remote moves to the coffee table, and the blanket is pulled over by 22:00. Priya is home for the whole sequence; she has been in the house since her afternoon errands ended.

This document differs from p_a1b2 (dinner 18:30–20:00) and p_5f2b (cook 17:00–18:00) by pushing the entire evening later: cooking is 18:30–19:30, not 17:00–18:00; dinner is 19:30–21:00, not 18:30–20:00. It also pins the dog feeding to 20:00–21:00 (not 19:00–21:00 as in p_3e7a) and TV to 21:00–23:00 (not 18:00–19:00 as in p_9d4e's remote-at-tv-stand claim).

Refutation: if the pot is seen on the counter at 17:00 or 17:30, or if plates are at the dining table at 18:00, the cooking/dinner window is earlier than this document claims. If the remote is at the tv_stand at 22:00 (not the coffee table), TV has not started or the remote is not being used.

```json
{
 "claims": [
  {
   "claim": "The pot is on the kitchen counter during the 18:30\u201319:30 weekday cooking window",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "Elena's plate is at the dining table during the 19:30\u201321:00 dinner",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the 20:00\u201321:00 evening feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 20,
   "to": 21
  },
  {
   "claim": "The remote is on the coffee table when TV starts at 21:00",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The blanket is on the coffee table during late-evening TV at 22:00",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  }
 ],
 "targets": {
  "pot_shared": [
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "plate_elena": [
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 20,
    "to": 21.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 21.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
