# p_8b4c — The 3 AM Armchair; Post-Shift TV Then a Kitchen Snack

Hana's shift ends at 23:00. She walks in, drops her bag and keys at the entry, and pads into the living room where she pulls the blanket off the coffee table and drapes it over the armchair. The remote goes from the TV stand to the floor. She settles in and watches something for a couple of hours. Around 03:00 she gets up, wanders into the kitchen for a glass of water or a quick snack, and the robot catches her there — resident_1 in the kitchen, resident_2 still asleep in bedroom_2. By 04:00 or 05:00 she's back in the living room, puts the blanket on the coffee table, returns the remote to the TV stand, and heads to her bedroom.

This document differs from p_4c9d in two ways. First, the armchair-TV window starts at 23:00 rather than 02:00, capturing the full post-shift session. Second, it does not make the 17:00–19:00 "blanket back on coffee table" claim that p_4c9d carries and that has been failing (against 7). The blanket's resting spot is the coffee table during the day, but the evening transition to the couch (19:00) is handled by a separate document.

This document is refuted if the robot finds the blanket on the coffee table or the remote on the TV stand during 00:00–04:00 on weekdays, or if Hana is not in the kitchen at 03:00. It is weakened if glass_hana is consistently in the pantry or cupboard rather than the counter during the 02:00–04:00 window.

Priya is in bed during this entire window (bedroom_2). Her book, tablet, and phone are at nightstand_b2 or bed_b2.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the armchair during Hana's post-shift TV session in the early morning",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "The remote is on the living room floor during the 3 AM TV session",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Hana's glass is on the kitchen counter during her 3 AM snack",
   "target": "glass_hana",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 2,
   "to": 4
  },
  {
   "claim": "Hana's tablet is at her nightstand during the early morning before her work block",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "The blanket is back on the coffee table by midday",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 4,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 4,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 4,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 4,
    "to": 23,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 2,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 2,
    "to": 4,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 4,
    "to": 23,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 8.5,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 12.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "phone_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
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
  "book_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 14,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 20,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
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
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
