# p_9b3c — Weekend friends: dinner at 20, living room after

Both Saturday and Sunday evenings have friends coming over, as the residents confirmed. The weekend day runs slow: both residents are home, Elena bakes on Saturday morning (tray at the kitchen counter 9–12), then does midday errands (keys and wallet out 12–15) on both days. Dinner is at the dining table around 19:30–21:00 with plates, glasses, and water bottles. After dinner the group settles into the living room from about 21:00 to 23:30: the board game comes out to the coffee table, Priya's guitar is in the living room for guests, and the blanket is on the couch or coffee table. The dog is with whoever is home; the food bag goes to the kitchen floor for the evening feed around 19–21.

This document differs from p_3f7a, which places the board game at the dining table (five against-sightings), and from p_9c1d, which is sparser on the full weekend-day pattern. The key prediction is the board game at coffee_table_l1 during the friends evening, not at the dining table.

What would refute it: the board game at dining_table_d1 during a weekend evening; the guitar not in the living room on a weekend evening; Elena's keys found at the entry table during 12–15 on a weekend (she'd be out).

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table during the weekend friends evening",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Priya's guitar is on the living-room floor during the weekend friends evening",
   "target": "guitar_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Elena's plate is at the dining table during weekend dinner",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Elena's keys are out of the house during her weekend midday errands",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 15
  },
  {
   "claim": "The baking tray is at the kitchen counter during Saturday morning baking",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
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
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "plate_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
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
    "chance": "usually"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "wallet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "helmet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
