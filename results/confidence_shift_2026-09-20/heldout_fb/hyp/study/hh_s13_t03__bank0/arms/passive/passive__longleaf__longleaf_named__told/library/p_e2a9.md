# p_e2a9 — — Entry Dump, Then Desk Reset by 22 (fork of p_d3e8)

This is a fork of p_d3e8 (The Entry Mess). The parent says Hana dumps everything at the entry hook at 17:30 and leaves it there. The evidence shows this is only half the story. At 18:00 the laptop, pen, charger, and water bottle ARE at the entry hook. But by 22:00 the laptop is at desk_b1 (seen twice at 22:00 and 23:00), the pen is at desk_b1 (seen at 03:00), the charger is at nightstand_b1 (seen 3 times at 23:00), and the water bottle is at kitchen_table_k1 (seen at 20:00).

The mixture's worst-objects list confirms this: laptop_hana was predicted at entry_hook_e1 but actually found at desk_b1 twice. The entry hook dump is real but temporary (18:00–20:00). Between 20:00 and 22:00, Hana does a "desk reset": she takes the laptop and pen to the desk, plugs the charger into the nightstand, and sets the water bottle on the kitchen table.

What changed from the parent: the base resting place for laptop, pen, and charger is now desk_b1 / desk_b1 / nightstand_b1 respectively (not entry_hook). The entry hook is only a transient 18:00–20:00 stop. The water bottle's evening resting place is kitchen_table_k1, not entry_hook.

What sets this apart from p_9d3b (Evening Reset): p_9d3b says items go to desk and kitchen but NOT the hook. This document says they DO go to the hook first (18:00–20:00) and THEN migrate. The 18:00 sightings at entry_hook_e1 are the distinguishing evidence.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at the desk at 22:00 on a weekday (moved from entry hook)",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 21,
   "to": 24
  },
  {
   "claim": "Hana's charger is at the nightstand at 23:00 on a weekday (plugged in for the night)",
   "target": "charger_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Hana's water bottle is at the kitchen table at 20:00 on a weekday (moved from entry hook)",
   "target": "water_bottle_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Hana's laptop is at the entry hook at 18:00 on a weekday (just arrived, not yet moved)",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
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
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "charger_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "entry_hook_e1",
    "chance": "usually"
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
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
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
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
