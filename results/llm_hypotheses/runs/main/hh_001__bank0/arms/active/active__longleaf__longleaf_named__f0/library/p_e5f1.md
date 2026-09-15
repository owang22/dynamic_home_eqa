# p_e5f1 — Book at the Coffee Table in the Afternoon, Nightstand at Bedtime; Tablet at the Counter (fork of p_7e4a)

This fork of p_7e4a addresses the book's mobile behaviour and the tablet's misplacement. The worst-objects log shows the book predicted at couch_l1 but actually at coffee_table_l1 three times (day 13, 15:00), and predicted at coffee_table_l1 but actually at nightstand_b1 twice (day 15, 00:00). The per-object stats confirm: book_mara is at 5 distinct receptacles, with couch_l1 on only 7/16 sighted days. The pattern is clear: during the afternoon (14:00–18:00) Mara reads at the coffee table in the living room; at bedtime (23:00–01:00) the book moves to the nightstand. The bookshelf is where it is stored when not in use.

The tablet change is straightforward: the coffee_table prediction has 1 for and 8 against, while the per-object stats show the tablet at counter_k1 on 10/16 days. The counter is the tablet's home during work hours.

What changed from p_7e4a: (1) The book gains a "both 14–18h at coffee_table_l1, sometimes" block (afternoon reading) and a "both 23–24h / 0–1h at nightstand_b1, sometimes" block (bedtime reading). The bookshelf base is retained. (2) The tablet's base changes from coffee_table_l1 to counter_k1. (3) The tablet claim now tests the counter. (4) A new claim tests the book at the coffee table in the afternoon.

What sets this apart from p_7e4a: at 15:00, the book is at the coffee table (not the bookshelf, not the couch); at 00:00, the book is at the nightstand; at 11:00 on a weekday, the tablet is at the counter (not the coffee table). What would refute it: the book found at the bookshelf at 15:00 on most days, or the tablet found at the coffee table at 11:00 consistently.

```json
{
 "claims": [
  {
   "claim": "The book is at the coffee table during the afternoon (14:00\u201318:00) while Mara reads in the living room",
   "target": "book_mara",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The tablet is at the kitchen counter during weekday work hours (not the coffee table, not the kitchen table)",
   "target": "tablet_mara",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 9,
   "to": 14
  },
  {
   "claim": "The book is at the nightstand during the late-night window (23:00\u201324:00) while Mara reads in bed",
   "target": "book_mara",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 23,
   "to": 24
  },
  {
   "claim": "The book is at the nightstand just after midnight (00:00\u201301:00) while Mara reads in bed",
   "target": "book_mara",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 0,
   "to": 1
  },
  {
   "claim": "The glasses are out of the house during weekday work hours (travels with Mara to the co-working space)",
   "target": "glasses_mara",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 14
  }
 ],
 "targets": {
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
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
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
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
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
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
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
  "glasses_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "notebook_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "pen_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "water_bottle_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 4,
    "to": 5.5,
    "at": "nightstand_b1",
    "chance": "rarely"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "keys_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "wallet_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "backpack_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "tablet_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
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
  "remote_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
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
  "blanket_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
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
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 1,
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
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
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
    "from": 7,
    "to": 8.5,
    "at": "nightstand_b1",
    "chance": "sometimes"
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
    "from": 7,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
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
  "lunchbox_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
  "suitcase_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
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
    "from": 13,
    "to": 15,
    "at": "couch_l1",
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
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
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
  ],
  "class:pan": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9.5,
    "at": "sink_k1",
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
   },
   {
    "days": "both",
    "from": 11,
    "to": 15,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "plate_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_shared_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
