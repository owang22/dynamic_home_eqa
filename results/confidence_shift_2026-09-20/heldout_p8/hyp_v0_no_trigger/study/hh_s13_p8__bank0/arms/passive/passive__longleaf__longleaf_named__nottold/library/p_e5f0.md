# p_e5f0 — Weekend Transformation: the weekend is a completely different rhythm

Weekdays follow the standard pattern (Hana commutes 8–17:30, Priya walks and does errands). But weekends are radically different. Hana sleeps in until 10:00. Brunch is 11:00–13:00 (plates, mugs, glasses on the kitchen table). Hana plays guitar 14:00–17:00 (guitar on the coffee table or ON_PERSON). They watch a movie together 19:00–22:00 (remote on couch, blanket on couch, snack bowl on coffee table). Priya does a jigsaw puzzle 10:00–14:00 (puzzle box on the coffee table or floor). No work objects are in play. Hana's keys, wallet, and laptop stay at the entry all weekend.

What sets this apart: on a Saturday at 8:00, Hana's keys are at entry_table_e1 (she's not at work; in the weekday pattern they'd be OUT_OF_HOUSE). At 12:00 on a Saturday, plates and mugs are on kitchen_table_k1 (brunch). At 16:00 on a Saturday, the guitar is ON_PERSON or at coffee_table_l1. At 14:00 on a Saturday, the puzzle box is at coffee_table_l1. What would refute it: Hana's keys OUT_OF_HOUSE at 8:00 on a Saturday, or the guitar on bedroom_floor_b1 at 16:00 on a Saturday.

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
   "claim": "Plates are on the kitchen table at noon on a Saturday (brunch)",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 11,
   "to": 13
  },
  {
   "claim": "The guitar is being played at 16:00 on a Saturday",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The puzzle box is on the coffee table at 14:00 on a Saturday",
   "target": "puzzle_box_shared",
   "expect": "coffee_table_l1",
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20.5,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "ON_PERSON",
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
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 14,
    "at": "coffee_table_l1",
    "chance": "almost_always"
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
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
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
    "days": "weekend",
    "from": 19,
    "to": 22,
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
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
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
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
