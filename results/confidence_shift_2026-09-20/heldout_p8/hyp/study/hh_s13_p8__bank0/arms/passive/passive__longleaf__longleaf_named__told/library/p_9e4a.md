# p_9e4a — Hana's Morning Base: Desk and Nightstand, Not the Hook

Hana's work items — laptop, pen, and charger — rest at desk_b1 overnight and in the morning (0:00–8:00). They are NOT at the entry hook during this window. The entry hook is only the 17:30–19:00 transit point when she walks in the door. Her glass, meanwhile, is at nightstand_b1 (by her bed) during the day, not in the pantry. The mixture has been repeatedly predicting entry_hook_e1 for the laptop and pen at 00:00 and 08:00, and pantry_shelf_k1 for the glass, when the sightings show desk_b1 and nightstand_b1.

What sets this apart: "The Entry Mess" (p_d3e8) implies Hana's objects linger at the hook well into the evening; this document says the hook is only a 90-minute stop. "Hana's Evening at the Desk" (p_9d3b) puts the laptop at desk_b1 at 20:00, which the evidence does not support (against 2). This document focuses on the 0–8 h window where the desk IS the resting place, and on the glass being at the nightstand rather than the pantry.

What would refute this document: finding the laptop or pen at the entry hook at 06:00, finding the charger at the entry hook at 07:00, or finding Hana's glass at the pantry shelf at 10:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at desk_b1 at 07:00 on a weekday",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 6,
   "to": 8
  },
  {
   "claim": "Hana's pen is at desk_b1 at 07:00 on a weekday",
   "target": "pen_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 6,
   "to": 8
  },
  {
   "claim": "Hana's glass is at the bedroom nightstand at 10:00 on a weekday",
   "target": "glass_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 8,
   "to": 14
  },
  {
   "claim": "Hana's charger is at desk_b1 at 07:00 on a weekday",
   "target": "charger_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 6,
   "to": 8
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
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
  "pen_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
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
  "charger_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
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
  "glass_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
