# p_3f7a — Saturday: baking morning, friends at the table

Elena and Priya are both home all day Saturday. Elena bakes in the morning (her stated hobby) and does errands around midday. Priya takes her late-morning walk and spends the afternoon with guitar or reading. The residents' Saturday message confirms friends arrive in the evening. Dinner is later than the weekday norm—around 19:30 to 21:00—because the group assembles and chats first. After dinner the board game comes out, Priya plays guitar, and the evening stretches late. The dog is with Elena throughout; she handles the feedings.

What sets this apart: every commute object (laptop, backpack, helmet, bike lock, jacket, shoes) stays in the house all day. The dining table sees heavier traffic than any weekday—extra plates and glasses for the group. The board game leaves the bookshelf for the first time in the week. The guitar moves to the living-room floor for Priya to play for guests. Baking items (tray, mixing bowl) appear at the counter in the morning.

Refutation: if the laptop is sighted out of the house on Saturday, or the board game stays on the bookshelf through the evening, or the baking tray is never seen at the counter on a Saturday morning, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is at the coffee table on a Saturday afternoon because she is home",
   "target": "laptop_elena",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The board game is on the dining table during Saturday evening with friends",
   "target": "board_game_shared",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The guitar is on the living-room floor while Priya plays for guests on Saturday evening",
   "target": "guitar_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The baking tray is at the kitchen counter during Saturday morning baking",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Elena's helmet stays at the entry hook all Saturday since she does not commute",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "helmet_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "weekend",
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
    "chance": "usually"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "weekend",
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
  "board_game_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "plate_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
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
    "from": 19.5,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
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
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
