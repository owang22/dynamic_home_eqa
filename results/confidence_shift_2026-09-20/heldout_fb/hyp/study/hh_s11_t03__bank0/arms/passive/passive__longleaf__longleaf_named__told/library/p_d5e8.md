# p_d5e8 — Priya's Armchair Hours; Water Bottle at 09:00, Magazine at 15:00

Two distinct sightings anchor Priya's armchair routine. At 09:00 on weekdays, water_bottle_priya is at armchair_l1 (sighted x2), and at 15:00, magazine_priya is at armchair_l1 (sighted x3). These are not coincidental: Priya settles into the armchair in the late morning with her water bottle (perhaps after her morning walk, returning around 08:30–09:00) and again in the mid-afternoon with her magazine for a reading break.

The 09:00 water-bottle-at-armchair sighting is missed by every current document. p_c3d4 puts water_bottle_priya at coffee_table_l1 (0–24 h) with an OUT_OF_HOUSE block 13.5–23 h. p_f3a7 puts it at dining_table_d1 (2–6 h). None place it at the armchair. The 15:00 magazine-at-armchair is partially captured by p_2d8c (weight 0.009), which puts magazine_priya at armchair_l1 14:00–17:00, but that document is very low-weight and does not connect the water bottle to the same routine.

Priya's day in this document: morning walk 07:00–08:30 (leash, jacket, keys, camera out), returns and settles in the armchair 09:00–11:00 with water bottle, lunch 12:00–13:00, afternoon errands 14:00–15:00 (keys, jacket out), returns and reads in the armchair 15:00–17:00 with magazine, dinner 18:00–19:00, evening TV or reading 19:00–21:00, bed 22:00.

This document is refuted if water_bottle_priya is at coffee_table_l1 or dining_table_d1 at 09:00, or if magazine_priya is at coffee_table_l1 at 15:00.

```json
{
 "claims": [
  {
   "claim": "Priya's water bottle is at the armchair at 09:00 on weekdays, not the coffee table or dining table",
   "target": "water_bottle_priya",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 8.5,
   "to": 11
  },
  {
   "claim": "Priya's magazine is at the armchair during the weekday afternoon reading block",
   "target": "magazine_priya",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's water bottle is at the dining table at 03:00 in the early morning",
   "target": "water_bottle_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 2,
   "to": 6
  }
 ],
 "targets": {
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 11,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "magazine_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
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
   },
   {
    "days": "both",
    "from": 5.5,
    "to": 6.5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
