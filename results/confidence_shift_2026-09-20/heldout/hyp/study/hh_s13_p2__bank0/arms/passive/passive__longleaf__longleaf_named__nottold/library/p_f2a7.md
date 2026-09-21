# p_f2a7 — Weekend Corrections: No Guitar, Couch Not Coffee Table (fork of p_e5f0)

This fork fixes three claims in p_e5f0 that the evidence has now refuted repeatedly. First, the guitar is **never** ON_PERSON on weekends either — the clock-hour data shows it at bedroom_floor_b1 at every single pass, all 12 weekend hours, just as on weekdays. The 14:00–17:00 ON_PERSON block produced zero positive sightings and four "against" tallies. Hana's guitar hobby is either very brief (a few minutes of strumming that the robot never catches) or she simply does not play it during the observed window. Second, the puzzle box is at **couch_l1** on weekend afternoons (14:00–22:00 passes show couch_l1 x1 alongside bookshelf_l1 x1), not at coffee_table_l1. The p_e5f0 claim "puzzle box on coffee table at 14:00 Saturday" went against 8 times. Third, the weekend brunch plate claim is unsupported: the 12:00 weekend pass shows plate_hana at cupboard_k1 x2, not kitchen_table_k1.

What I keep from the parent: Hana's keys at entry_table_e1 in the weekend morning (scored for 2, against 0), and the general concept that weekends have a different rhythm. I add the weekend-specific resting places that the "mixture's worst objects" list exposes: blanket at armchair_l1, jacket_priya at entry_floor_e1, shopping_bag at kitchen_table_k1, vacuum at floor_l_l1.

What sets this apart from p_e5f0: at 16:00 on a Saturday, the guitar is at bedroom_floor_b1 (not ON_PERSON), the puzzle box is at couch_l1 (not coffee_table_l1), and the blanket is at armchair_l1 (not couch_l1). What would refute it: the guitar sighted ON_PERSON at any weekend hour, or the puzzle box at coffee_table_l1 at 16:00 on a Saturday.

_(targets the fork left unstated are inherited from p_e5f0)_

```json
{
 "claims": [
  {
   "claim": "Hana's keys are at the entry table at 8:00 on a Saturday",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 7,
   "to": 10
  },
  {
   "claim": "The puzzle box is on the couch at 16:00 on a Saturday",
   "target": "puzzle_box_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The guitar is on the bedroom floor at 16:00 on a Saturday",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The blanket is on the armchair at 12:00 on a Saturday",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 10,
   "to": 14
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
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
  ],
  "puzzle_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
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
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "plate_hana": [
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 22,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ]
 }
}
```
