# p_7f2a — Mara works in healthcare (rotating shifts); medication is taken at the bathroom shelf (fork of p_3b8a)

This is a fork of p_3b8a with one correction driven by the evidence: the medication bottle does NOT go to the counter for a 7:00 dose. The robot found the bottle at bathroom_shelf_ba1 on 3 of 4 weekday 9–17 h looks, and the 7:00 counter claim has gone against twice. The revised model is that Mara takes her medication at the bathroom shelf (she's already in the bathroom getting ready) and the bottle simply stays there. The rest of the healthcare-rotating-shift structure is unchanged: day-shift week means she leaves at 6:45, the lunchbox goes out with her, the tablet stays home, and the yoga mat is used on days off.

What changed and why: the two `counter_k1` blocks for medication_bottle_mara (weekday 6.5–7.5 and 15–16) are removed; the bottle is now at bathroom_shelf_ba1 around the clock. The claim is updated to expect the bathroom shelf. Everything else (lunchbox out of house 7–15, tablet at coffee table, yoga mat on Saturday) is inherited unchanged.

What would refute this fork: the medication bottle found at the counter during a weekday morning, or the lunchbox found in the house at 10:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The tablet is in the house at 10:00 on weekdays (hospital provides its own tech)",
   "target": "tablet_mara",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "The lunchbox is out of the house during work hours on weekdays",
   "target": "lunchbox_mara",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7,
   "to": 15
  },
  {
   "claim": "The medication bottle stays on the bathroom shelf even during the morning routine",
   "target": "medication_bottle_mara",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 6.5,
   "to": 8
  },
  {
   "claim": "The yoga mat is on the floor on Saturday (day off)",
   "target": "yoga_mat_mara",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 10,
   "to": 11
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
    "from": 6.5,
    "to": 15.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
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
    "from": 10,
    "to": 11,
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
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
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
    "days": "weekday",
    "from": 6,
    "to": 7.5,
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
    "days": "weekday",
    "from": 6,
    "to": 7.5,
    "at": "nightstand_b1",
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
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 15.5,
    "at": "OUT_OF_HOUSE",
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
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "counter_k1",
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
   },
   {
    "days": "both",
    "from": 16,
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
    "from": 6.5,
    "to": 7.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 16,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
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
    "from": 6.5,
    "to": 7.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
    "from": 6.5,
    "to": 7.5,
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
    "from": 6.5,
    "to": 15.5,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
   }
  ]
 }
}
```
