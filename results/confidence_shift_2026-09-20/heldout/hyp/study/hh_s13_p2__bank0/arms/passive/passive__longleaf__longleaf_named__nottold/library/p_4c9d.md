# p_4c9d — Hana's Evening Desk: work items go to desk_b1 when she comes home

The "worst objects" data is unambiguous: laptop_hana was predicted at entry_hook_e1 but actually found at desk_b1 six times, pen_hana five times, charger_hana three times. The clock-hour sightings confirm a split at 18:00–22:00 (one sighting at entry_hook_e1, one at desk_b1 per pass), but the recent trend favours desk_b1. At 08:00 the laptop is already at desk_b1 (Hana is about to leave and it's on her desk). This document says Hana is tidy enough to carry her laptop, pen, and charger from the entry to desk_b1 when she gets home at 17:30, and they stay there through the evening. She charges the laptop at the desk, writes in her notebook at the desk, and the pen lives with them.

What sets this apart from p_d3e8 (Entry Mess): at 20:00 on a weekday, laptop_hana is at desk_b1 (not entry_hook_e1), pen_hana is at desk_b1, charger_hana is at desk_b1. What would refute it: laptop_hana at entry_hook_e1 at 20:00 on a weekday, or pen_hana at entry_hook_e1 at 20:00.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at desk_b1 at 20:00 on a weekday",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's pen is at desk_b1 at 20:00 on a weekday",
   "target": "pen_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's charger is at desk_b1 at 20:00 on a weekday",
   "target": "charger_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's laptop is out of the house at noon on a weekday",
   "target": "laptop_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
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
  "charger_hana": [
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
  "pen_hana": [
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
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "handbag_hana": [
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
    "to": 20.5,
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
    "from": 20.5,
    "to": 22,
    "at": "couch_l1",
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
  ]
 }
}
```
