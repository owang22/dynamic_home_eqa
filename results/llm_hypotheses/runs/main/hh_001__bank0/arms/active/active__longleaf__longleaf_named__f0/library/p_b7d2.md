# p_b7d2 — Mara works from the living room; kitchen table is the evening workspace (fork of p_e9c3)

This is a fork of p_e9c3 that corrects three major errors. First, the lunchbox does NOT sit at the counter 24/7 — it moves to the kitchen table at lunchtime (12:00–14:00) and to the sink for washing (14:00–16:00). The "lunchbox never leaves the house" claim went against 6 times because the robot found it at the kitchen table or sink, not the counter. Second, the laptop, charger, headphones, and water bottle are NOT at the kitchen table during weekday 9:00–17:00. The per-object data shows each of these found at kitchen_table_k1 only 1 out of 5 times during weekday 9–17h, but they are the "mostly" location overall (evening and weekend sightings). During weekday work hours, Mara works from the living room with the tablet, and the laptop/peripherals are stored in the bedroom. Third, the bowls are not in the cupboard — bowl_shared_1 is at entry_table_e1 (3/3 days) and bowl_shared_2 is at kitchen_table_k1.

What changed and why: (1) lunchbox_mara blocks now reflect its movement: counter → kitchen table at lunch → sink after. (2) laptop_mara, charger_mara, headphones_mara, and water_bottle_mara get a weekday 9–17 block at bedroom_floor_b1 (stored in the bedroom during work hours). (3) class:bowl is replaced with individual bowl targets. (4) The medication bottle remains at bathroom_shelf_ba1 (no counter block, consistent with evidence).

What sets this apart from p_e9c3: at 10:00 on a weekday, the laptop is in the bedroom (not the kitchen table), the tablet is at the coffee table, and the kitchen table is empty of tech objects. At 19:00 on a weekday, the laptop is at the kitchen table. At 12:30, the lunchbox is at the kitchen table (not the counter). What would refute it: the laptop found at the kitchen table during weekday 9–17, or the lunchbox found OUT_OF_HOUSE on a weekday.

_(targets the fork left unstated are inherited from p_e9c3)_

```json
{
 "claims": [
  {
   "claim": "The laptop is in the bedroom during weekday work hours (not the kitchen table)",
   "target": "laptop_mara",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The lunchbox is at the kitchen table at lunchtime (not the counter)",
   "target": "lunchbox_mara",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 12,
   "to": 14
  },
  {
   "claim": "The tablet is at the coffee table during weekday work hours (Mara works from the living room)",
   "target": "tablet_mara",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The medication bottle is at the bathroom shelf during the 8:00 dose window",
   "target": "medication_bottle_mara",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 7.5,
   "to": 8.5
  }
 ],
 "targets": {
  "tablet_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "yoga_mat_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "lunchbox_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 16,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "watering_can_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "suitcase_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "blanket_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "hairbrush_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "makeup_kit_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "medication_bottle_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "pen_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "umbrella_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
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
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:pan": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:pot": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "book_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "towel_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "laundry_basket_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "laptop_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "charger_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "headphones_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "notebook_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "bowl_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "bowl_shared_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
