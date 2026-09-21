# p_7e4a — The Late Night: TV until 23, guitar until 23, bedtime at midnight (fork of p_c9d4)

This is a revision of p_c9d4. The snack bowl claim (coffee_table_l1, 20–23 h) took three "against" hits since the last call: the clock-hour log shows snack_bowl_shared at counter_k1 at 18:00 and 19:00 (three sightings) and only at coffee_table_l1 at 21:00. The bowl is still in the kitchen during the 20:00 hour—Hana is finishing dinner or both residents are still at the table—so the move to the living room happens at 21:00, not 20:00. I have split the snack bowl into two blocks: counter_k1 from 18 to 21, then coffee_table_l1 from 21 to 23. The claim window is tightened to 21–23. Everything else (remote on the couch 20–23, guitar on the coffee table 19–21 and ON_PERSON 21–23, blanket on the couch) is unchanged from the parent.

What sets this apart from p_c9d4: at 20:00 the snack bowl is still at counter_k1, not yet on the coffee table. What would refute it: snack_bowl_shared sighted at coffee_table_l1 before 21:00, or at counter_k1 after 21:30.

```json
{
 "claims": [
  {
   "claim": "The remote is still on the couch at 22:00 on a weekday",
   "target": "remote_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The guitar is on the coffee table or being played at 22:00 on a weekday",
   "target": "guitar_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The blanket is on the couch at 22:00 on a weekday",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the coffee table during the late TV session after 21:00",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The snack bowl is still on the kitchen counter at 20:00 on a weekday",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "laptop_hana": [
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
  "wallet_hana": [
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
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
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
  "blanket_shared": [
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
  "snack_bowl_shared": [
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
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
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
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
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
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
