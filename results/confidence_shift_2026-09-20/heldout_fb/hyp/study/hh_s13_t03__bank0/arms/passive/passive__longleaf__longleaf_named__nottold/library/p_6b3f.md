# p_6b3f — Hana's 18:00 Arrival: Entry Hook, Then Dispersal

When Hana walks through the door at ~17:30–18:00, she carries her laptop, water bottle, pen, and charger, and wears her scarf and shoes. The 18:00 patrol catches the immediate aftermath: laptop at entry_hook_e1 (×1), water bottle at entry_hook_e1 (×1), pen at entry_hook_e1 (×1), charger at entry_hook_e1 (×1), scarf at entry_floor_e1 (×1), shoes at entry_floor_e1 (×1). By 20:00 the water bottle has moved to kitchen_table_k1 (×1). By 22:00–23:00 the laptop is at desk_b1 (×2) and the charger is at nightstand_b1 (×3).

This document models the *transit* phase: objects are at the entry for a brief window (17:30–19:00) before dispersing to their evening resting spots. It differs from p_d3e8 (Entry Mess, weight 0.044) which claims the laptop, water bottle, and pen are *still* at the entry hook at 20:00 (a claim that has gone against 7–8 times). Here the entry window closes by 19:00. It differs from p_1d9b (Brief Entry, Then the Desk) which places the laptop at desk_b1 by 19:00; here the laptop lingers at the entry until ~19:30 before moving to the desk.

Refutation: laptop or water bottle found at the entry hook at 20:00 or later on multiple days, or the laptop at desk_b1 at 18:00 (she just arrived).

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at the entry hook at 18:00 on a weekday (just arrived home)",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's water bottle is at the entry hook at 18:00 on a weekday (just arrived home)",
   "target": "water_bottle_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's laptop is at desk_b1 at 22:00 on a weekday (evening work session)",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 21,
   "to": 23.5
  },
  {
   "claim": "Hana's charger is at the nightstand at 23:00 on a weekday (bedtime charging)",
   "target": "charger_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22.5,
   "to": 24
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 23.5,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
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
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "sometimes"
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
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "nightstand_b1",
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
    "to": 19,
    "at": "entry_floor_e1",
    "chance": "sometimes"
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
    "to": 19,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
