# p_7a4f — Mara works from a co-working space; plates at table/counter (no cupboard); pen at kitchen table; tablet sometimes at counter (fork of p_c3e9)

This fork of p_c3e9 addresses three persistent errors in the parent. First, the `class:plate` block at cupboard_k1 has failed repeatedly across the library (0.15–0.17 on 24–26 sightings in p_b7d2, p_e7a3, p_3b8a, p_b4c9, p_f8d2, and p_c3e9 itself). The per-object data is unambiguous: plate_shared_1 is at kitchen_table_k1 (4/8 days) and plate_shared_2 is at counter_k1 (4/8 days). The cupboard is not where plates live in this household. This fork removes the `class:plate` block entirely, leaving the individual plate targets (already present in p_c3e9) to govern.

Second, the pen was predicted at counter_k1 but actually sighted at kitchen_table_k1 three times (e.g., day 6 09:00). The pen belongs at the kitchen table — it is the "workspace pen" that sits with the notebook and laptop during evening/weekend work sessions. This fork moves pen_mara to kitchen_table_k1.

Third, the mixture's worst-objects list flagged the tablet: predicted coffee_table_l1, actually counter_k1, 4× (e.g., day 6 10:00). While the tablet is still mostly at the coffee table (6/8 sighted days), there is a recurring pattern of it being at the kitchen counter during weekday daytime — perhaps Mara sets it up there for reference while the laptop is out, or uses it for recipes and quick tasks at the counter. This fork adds a "sometimes" block for tablet_mara at counter_k1 during weekday 9–14.

What changed from p_c3e9: (1) removed `class:plate` target entirely. (2) pen_mara default changed from counter_k1 to kitchen_table_k1. (3) tablet_mara gained a weekday 9–14 block at counter_k1 (sometimes). (4) Updated claims to test the new predictions.

What sets this apart from p_c3e9: at 10:00 on a weekday, the tablet may be at the kitchen counter (not just the coffee table); the pen is at the kitchen table (not the counter); plates have no cupboard default. What would refute it: the pen found at the counter during weekday morning, the tablet found at the coffee table every single weekday morning (no counter sightings), or a plate found in the cupboard.

_(targets the fork left unstated are inherited from p_c3e9)_

```json
{
 "claims": [
  {
   "claim": "The pen is at the kitchen table during weekday morning (not the counter)",
   "target": "pen_mara",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 12
  },
  {
   "claim": "The tablet is at the kitchen counter during weekday work hours (not the coffee table)",
   "target": "tablet_mara",
   "expect": "counter_k1",
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
   "claim": "The lunchbox is out of the house during weekday work hours (not at the kitchen table at lunchtime)",
   "target": "lunchbox_mara",
   "expect": "OUT_OF_HOUSE",
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
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "counter_k1",
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
    "at": "counter_k1",
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
  "notebook_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
