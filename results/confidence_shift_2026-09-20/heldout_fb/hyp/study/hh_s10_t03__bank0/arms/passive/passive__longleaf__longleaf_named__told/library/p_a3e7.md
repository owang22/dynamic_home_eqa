# p_a3e7 — Weekend Saturday: both home, joint cycling, errands midday

It is Saturday. Both Yuki and Omar are off work. Yuki sleeps in — no 6:15 journaling, no 8:00 departure for the office. Omar is home all day; no 1:40 shift. Around 10:00–11:00 they both get ready for a joint cycling ride: helmets come off the entry hook, bike locks are grabbed from the entry table, and they head out. They ride together until roughly 13:00, then return home. In the midday-to-afternoon window (12:00–15:00), one or both of them goes on errands — Yuki's stated weekend pattern is "errands around midday, home the rest of the day." The rest of the afternoon and evening they are home: Omar may game at the TV stand, they may cook together, and the evening settles into the usual TV-and-blanket routine.

What sets this hypothesis apart: on Saturday, both helmets and both bike locks are OUT_OF_HOUSE from about 10 to 13, and the laptop stays at the entry hook (no work to do). Omar's tablet is not in the kitchen chair (he is home, using it at the kitchen table). The backpack and handbag may briefly leave with a resident on errands but are back by 15:00.

This is refuted if: (a) either helmet or bike lock is sighted in the house during 10:00–13:00 on Saturday; (b) the laptop is at the office desk or bedroom desk on Saturday (implying she is working); (c) Omar's tablet is at the kitchen chair during 10:00–14:00 on Saturday (implying he left for work).

```json
{
 "claims": [
  {
   "claim": "Yuki's helmet is out of the house on Saturday morning during the joint cycling ride",
   "target": "helmet_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 10,
   "to": 13
  },
  {
   "claim": "Omar's helmet is out of the house on Saturday morning during the joint cycling ride",
   "target": "helmet_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 10,
   "to": 13
  },
  {
   "claim": "Yuki's laptop stays at the entry hook all day Saturday (no work)",
   "target": "laptop_yuki",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 10,
   "to": 20
  },
  {
   "claim": "Omar's tablet is at the kitchen table on Saturday midday (he is home, not at work)",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 10,
   "to": 14
  }
 ],
 "targets": {
  "helmet_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "helmet_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "bike_lock_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "bike_lock_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "laptop_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "tablet_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "chair_k1",
    "chance": "sometimes"
   }
  ],
  "backpack_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "handbag_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
