# p_d5f2 — Mara's hybrid work week: co-working most days with 1–2 home-work days; morning counter routine; late-night couch TV

Mara lives alone and works 9:00–14:00 on weekdays. Most days she goes to a co-working space (laptop, charger, and lunchbox travel OUT_OF_HOUSE), but one or two days per week she works from home, setting up at the kitchen table or occasionally the bookshelf in the living room. On home-work days the laptop is in the house during 9–14; on co-working days it is not. The tablet is always at the coffee table — it is her leisure device, not her work device.

The morning routine (6:00–9:00) is kitchen-counter centred: the water bottle is at the counter while she makes coffee, the pan is at the counter for breakfast cooking, and the watering can is at the counter before it goes back to the sink. The medication bottle is at the bathroom shelf for the 8:00 dose but moves to the counter around 17:00–19:00 for the evening dose, which she takes while preparing dinner.

In the evening and late at night (22:00–06:00), the remote is at the couch — Mara watches TV or video content lying on the couch, sometimes into the early morning (the 04:00 sighting supports this). The blanket is at the couch for this period. The yoga mat is on the couch during the day and is used on weekend mornings.

What sets this apart from p_e7a3 and p_a1c7: on some weekday mornings (roughly 1–2 per week) the laptop is IN the house at the kitchen table or bookshelf during 9–14, not OUT_OF_HOUSE. The laptop's per-object data shows "3/6 sighted days" at kitchen_table_k1 and "3 receptacles" — the third receptacle (bookshelf_l1) and the 2 sightings at bookshelf_l1 at 11:00 are explained by a home-work day. The remote is at the couch 22:00–06:00 (not just 19:00–22:00), accounting for the 04:00 sighting. What sets this apart from p_c3e9: the work window is 9:00–14:00 (not 8.5–14.5); the laptop has an explicit "sometimes at kitchen_table" block for home-work days rather than a blanket OUT_OF_HOUSE. What would refute it: the laptop found OUT_OF_HOUSE on a day when the charger is also OUT_OF_HOUSE but the lunchbox is at the counter (indicating a home-work day where only the laptop went out, which would be inconsistent), or the remote found at the coffee table at 03:00.

```json
{
 "claims": [
  {
   "claim": "The laptop is in the house (kitchen table or bookshelf) on at least one weekday 9\u201314 per week (home-work day)",
   "target": "laptop_mara",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 14
  },
  {
   "claim": "The water bottle is at the kitchen counter during the 7:00 morning routine",
   "target": "water_bottle_mara",
   "expect": "counter_k1",
   "days": "both",
   "from": 6.5,
   "to": 8
  },
  {
   "claim": "The remote is at the couch during late-night hours (Mara watches TV on the couch)",
   "target": "remote_shared_1",
   "expect": "couch_l1",
   "days": "both",
   "from": 23,
   "to": 24
  },
  {
   "claim": "The pan is at the kitchen counter during morning cooking (7:00\u20139:00)",
   "target": "pan_shared_1",
   "expect": "counter_k1",
   "days": "both",
   "from": 7,
   "to": 9
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
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "rarely"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
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
  "pen_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
  "yoga_mat_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "couch_l1",
    "chance": "usually"
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
    "from": 21,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "couch_l1",
    "chance": "almost_always"
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
    "from": 22,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "couch_l1",
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
    "to": 8,
    "at": "counter_k1",
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
  "umbrella_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
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
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_shared_1": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
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
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "sink_k1",
    "chance": "sometimes"
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
    "from": 7,
    "to": 9,
    "at": "counter_k1",
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
  ]
 }
}
```
