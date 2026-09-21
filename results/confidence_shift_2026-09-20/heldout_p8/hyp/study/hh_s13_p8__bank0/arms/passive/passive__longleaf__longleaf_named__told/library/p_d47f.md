# p_d47f — Hana's 17:30 Homecoming: The Entry Dump and Kitchen Handoff

The 18:00 Wednesday pass caught Hana's things at the entry: water_bottle_hana at entry_hook_e1, charger_hana at entry_hook_e1, scarf_hana at entry_floor_e1, shoes_hana at entry_floor_e1. At 00:00 the water bottle was at sink_k1 and the charger at desk_b1, so the entry positions are the "just got home" state. By the next morning the water bottle is back at the sink and the charger back at the desk. This is a daily 17:30–18:00 routine: Hana walks in, hangs the scarf and kicks off her shoes at the entry floor, hooks the water bottle and charger on the entry hook, sets her keys and wallet on the entry table, then goes to the kitchen.

What sets this apart: p_d3e8 (the entry mess) predicted the laptop, pen, and water bottle all at the entry hook at 20:00 (against 7 each). This document says the dump is brief: the items are at the entry at 18:00 but are moved to their proper spots (desk, sink) by 20:00. The laptop and pen go to desk_b1, not the entry hook. The water bottle goes to the sink, not the hook. Only the charger, scarf, and shoes linger at the entry for the evening.

What would refute it: if the water bottle is still at entry_hook_e1 at 20:00, or if the laptop is at entry_hook_e1 at 20:00, or if the charger is at desk_b1 at 18:00 (not yet home).

```json
{
 "claims": [
  {
   "claim": "Hana's water bottle is at the entry hook at 18:00 on a weekday (just got home)",
   "target": "water_bottle_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's water bottle is at the kitchen sink at 20:00 on a weekday (moved from entry)",
   "target": "water_bottle_hana",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Hana's charger is at the entry hook at 18:00 on a weekday",
   "target": "charger_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's laptop is at the entry hook at 18:00 on a weekday (just set down)",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
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
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
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
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "scarf_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 22,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "shoes_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 22,
    "at": "entry_floor_e1",
    "chance": "usually"
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
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
