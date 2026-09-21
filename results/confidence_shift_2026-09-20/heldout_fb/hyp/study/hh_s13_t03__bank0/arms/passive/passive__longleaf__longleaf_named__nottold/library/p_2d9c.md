# p_2d9c — Weekend: Couch Afternoon, Armchair Evening, Vacuum All Day (fork of p_9e2b)

The parent (p_9e2b) predicted the blanket on the armchair all day and the vacuum on the floor 11:00–16:00. The Saturday evidence complicates both. The blanket was on the couch at 14:00, on the armchair at 18:00, 20:00, 21:00, and 23:00, and on the coffee table at 20:00, 21:00, and 22:00. It is not exclusively on the armchair. The vacuum was on the living room floor at 03:00 (left out from the prior day), 10:00, 12:00, 15:00, and 18:00 — a continuous presence from the early-morning patrol through the evening, not a 11:00–16:00 window. The guitar was on the couch at 16:00 (2×), not ON_PERSON.

What changed: (1) The blanket follows a three-position weekend arc: couch in the afternoon, armchair in the evening, coffee table during the TV window 20:00–22:00. (2) The vacuum is on the floor from 03:00 through 18:00 on weekends (a full-day cleaning or a session that started the prior evening). (3) The guitar rests on the couch in the Saturday afternoon rather than being played. (4) The remote on the coffee table in the evening is retained (strong evidence: 4× at 20:00).

What would refute this: the blanket on the armchair at 14:00 Saturday (afternoon, not evening), the vacuum in storage at 12:00 Saturday, or the guitar ON_PERSON at 16:00 Saturday.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch at 14:00 on a Saturday (afternoon rest)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "The remote is on the coffee table at 20:30 on a Saturday",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 19.5,
   "to": 21.5
  },
  {
   "claim": "The guitar is on the couch at 16:00 on a Saturday (not being played)",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 15,
   "to": 17.5
  },
  {
   "claim": "The vacuum is on the living room floor at 12:00 on a Saturday (all-day cleaning)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 9,
   "to": 17
  },
  {
   "claim": "The blanket is on the armchair at 22:00 on a Saturday (evening TV)",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 21,
   "to": 23.5
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23.5,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
