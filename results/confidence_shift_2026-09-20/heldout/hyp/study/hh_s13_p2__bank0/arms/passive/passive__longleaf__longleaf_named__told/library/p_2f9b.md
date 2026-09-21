# p_2f9b — The Kitchen-to-Living-Room Transition: two-phase evening confirmed by Tuesday

The Tuesday patrol passes (18:00, 20:00, 22:00) reveal a clean two-phase evening that several existing documents get wrong. Phase one, the kitchen phase (roughly 18:00–21:00): both residents are in the kitchen, dinner is prepared and eaten at the kitchen table, and cooking implements cycle through counter → sink → cupboard/drawer. At 20:00 the plates, glasses, and mugs are on the kitchen table (dinner in progress), while the pan, knife, spatula, and cutting board are in the sink (being washed). Phase two, the living-room phase (roughly 21:00–23:00): both residents move to the living room, the blanket and remote shift from the couch/TV-stand to the coffee table, the snack bowl appears on the coffee table, and Priya's headphones move from the bed to her desk (she's settling in to watch or listen). The guitar stays on the bedroom floor throughout — it is not played on a quiet Tuesday evening.

What sets this apart: p_c9d4 (The Late Night) places the remote and blanket on the *couch* at 22:00, but the Tuesday pass found both on the *coffee table*. p_c9d4 also has the guitar on the coffee table at 22:00, but the guitar was sighted only on the bedroom floor across all three passes. p_b1c6 (Guitar is the Evening Anchor) has the guitar on her person at 20:00, but the Tuesday pass at 20:00 shows both residents in the kitchen with no guitar sighting. This document is the only one that places the blanket and remote on the coffee table (not the couch) in the 21–23 h window and keeps the guitar on the bedroom floor all evening.

What would refute it: if on a weekday the blanket is on the couch at 22:00 (not the coffee table), or the remote is on the TV stand at 22:00, or the guitar is on the coffee table or on a person at 21:00, the two-phase transition model is wrong. If the residents are still in the kitchen at 22:00, the living-room phase hasn't started.

Travelling objects: Hana's laptop, jacket, keys, handbag, wallet, pen, and water bottle are out with her at work 8:00–17:30. Priya's keys and jacket are out on the afternoon errand 14:00–16:00. Nothing else leaves the house on a typical weekday.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table at 22:00 on a weekday, not the couch or TV stand",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The blanket is on the coffee table at 22:00 on a weekday, not the couch",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The guitar stays on the bedroom floor at 22:00 on a weekday (not played, not on the coffee table)",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Priya's headphones are on her desk at 22:00 on a weekday",
   "target": "headphones_priya",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
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
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
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
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "desk_b2",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 22.5,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
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
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
