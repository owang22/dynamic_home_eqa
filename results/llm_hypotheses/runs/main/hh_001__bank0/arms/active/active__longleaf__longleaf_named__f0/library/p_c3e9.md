# p_c3e9 — Mara works from a co-working space; lunchbox travels; plates at table and counter (fork of p_b7d2)

This is a fork of p_b7d2 that corrects three major errors identified by the latest claim results and per-object data. First, the lunchbox does NOT sit at the kitchen table at lunchtime — the claim "lunchbox at kitchen_table_k1, both 12–14h" went against 2 times since the last call. The per-object data shows the lunchbox at counter_k1 (3/5 days) with weekday 9–17h looks finding it 3 times and nothing 3 times, consistent with it being OUT_OF_HOUSE during 9–14 (the 3 "found" instances falling in the 14–17h window after it returns). Second, the class:plate at cupboard_k1 block failed (0.19 on 22 sightings). The per-object data shows plate_shared_1 mostly at kitchen_table_k1 (4/7 days) and plate_shared_2 mostly at counter_k1 (4/7 days) — the plates are not stored in the cupboard. Third, the laptop, charger, headphones, and water bottle are NOT in the bedroom during weekday work hours. The per-object data shows the laptop at 3 receptacles (not just kitchen_table and bedroom), and the mixture flagged "laptop at bookshelf_l1 2x, e.g. day 5 11:00." The simplest explanation consistent with p_e7a3's strong performance is that these items travel OUT_OF_HOUSE during weekday 9–14, not that they are stored in the bedroom.

What changed and why: (1) lunchbox_mara: removed kitchen_table_k1 12–14 and sink_k1 14–16 blocks; added OUT_OF_HOUSE weekday 8.5–14.5. (2) class:plate replaced with individual plate targets: plate_shared_1 at kitchen_table_k1, plate_shared_2 at counter_k1. (3) laptop_mara, charger_mara, headphones_mara, water_bottle_mara: weekday 9–17 block changed from bedroom_floor_b1 to OUT_OF_HOUSE. (4) water_bottle_mara default changed from kitchen_table_k1 to couch_l1 (per-object data: "mostly couch_l1 4/7 days").

What sets this apart from p_b7d2: at 12:30 on a weekday, the lunchbox is OUT_OF_HOUSE (not at the kitchen table); the laptop is OUT_OF_HOUSE (not in the bedroom); plate_shared_1 is at kitchen_table_k1 (not the cupboard). What sets this apart from p_e7a3: the work window is 9–14 (not 8.5–14.5); the water bottle is at couch_l1 with a morning counter block; the plates are split into individual targets. What would refute it: the lunchbox found at the kitchen table at 12:30 on a weekday, the laptop found in the bedroom during weekday 9–14, or plate_shared_1 found in the cupboard.

_(targets the fork left unstated are inherited from p_b7d2)_

```json
{
 "claims": [
  {
   "claim": "The lunchbox is out of the house during weekday work hours (not at the kitchen table at lunchtime)",
   "target": "lunchbox_mara",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 14
  },
  {
   "claim": "Plate shared 1 is at the kitchen table during dinner (not the cupboard)",
   "target": "plate_shared_1",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 18,
   "to": 21
  },
  {
   "claim": "The laptop is out of the house during weekday work hours (not in the bedroom)",
   "target": "laptop_mara",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 14
  },
  {
   "claim": "The tablet is at the coffee table during weekday work hours",
   "target": "tablet_mara",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 9,
   "to": 14
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
    "from": 22,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "couch_l1",
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
    "days": "weekday",
    "from": 8.5,
    "to": 14.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 7,
    "to": 9,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "to": 14,
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
    "from": 9,
    "to": 14,
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
    "from": 9,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
  ]
 }
}
```
