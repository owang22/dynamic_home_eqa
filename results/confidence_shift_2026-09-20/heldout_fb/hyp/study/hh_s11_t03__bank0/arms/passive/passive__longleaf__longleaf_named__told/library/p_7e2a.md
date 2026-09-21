# p_7e2a — The Kitchen-Table Morning, Coffee-Table Afternoon; Tablet Stays Home

Hana (resident_1) works afternoon-to-night shifts, home sick on Friday. On a normal weekday she rises around 07:00, has breakfast at the kitchen table, then works from the kitchen table until about 10:00. At 10:00 she migrates to the living room: her tablet, mug, book, and water bottle all move to the coffee table for the late morning and early afternoon. Around 13:00 she heads back to her bedroom to change, the tablet goes to the nightstand, and she leaves at 13:40 for her shift. She does NOT take the tablet to work; it rests at the nightstand from 13:00 until she returns at 23:00. On the sick day (Friday) the tablet may linger at the kitchen table or coffee table longer because she never leaves.

Priya (resident_2) is retired, home all day. She does a morning walk around 07:00–08:00 (keys, leash, jacket out of the house), does light errands in the afternoon, reads in the armchair at 15:00 (magazine, water bottle), and has dinner at the dining table at 19:00. Her camera stays on the bookshelf. The yoga mat stays in wardrobe_b2 except for a brief early-morning unroll.

What sets this document apart: the tablet is at the **kitchen table** at 09:00 (not the desk, not the coffee table yet), then at the **coffee table** at 10:00–12:00, then at the **nightstand** from 13:00 onward. The mug, book, and water bottle follow the tablet to the coffee table by 10:00. Hana's notebook, by contrast, stays at desk_b1 all day (it is her work notebook, left at the desk). The tablet is never out of the house.

Refutation: if the tablet is sighted at desk_b1 during the 09:00–12:00 window, or at the coffee table before 10:00, or out of the house during the 13:40–23:00 shift, this document is wrong. If the mug is at the cupboard (not the coffee table) at 12:00–17:00 on a weekday when Hana is home, the coffee-table afternoon claim fails.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table during her weekday morning work block",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Hana's tablet is at the coffee table during the weekday late-morning lounge",
   "target": "tablet_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Hana's tablet is at her nightstand while she is out at work",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Hana's mug is at the coffee table during the weekday afternoon",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 17
  },
  {
   "claim": "Hana's water bottle is at the coffee table during the weekday afternoon",
   "target": "water_bottle_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 17
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 13,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "book_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "entry_table_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "class:dog_bowl": [
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
    "from": 7,
    "to": 8.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8.5,
    "to": 22.5,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "keys_priya": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
