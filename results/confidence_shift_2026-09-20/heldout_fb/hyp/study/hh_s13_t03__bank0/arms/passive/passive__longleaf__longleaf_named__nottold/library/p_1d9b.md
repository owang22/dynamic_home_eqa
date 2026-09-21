# p_1d9b — Brief Entry, Then the Desk

This document refines the "entry mess" idea (p_d3e8) by **compressing the time window**. Hana arrives home at 17:30 and for roughly 15 minutes her things (laptop, water bottle, pen, handbag) are piled at entry_hook_e1 while she takes off shoes, hangs her jacket, and grabs a drink. But by 17:45 she has moved to desk_b1 in bedroom-b1 for her evening session. The entry hook is **not** where her things sit for four hours.

What sets this apart: p_d3e8 claims laptop, water bottle, and pen are at entry_hook_e1 from 18 to 22 h. The evidence (against 7 for each) says they are not. This document says the entry dump is real but brief (17:30–17:45), and the objects are at desk_b1 from 17:45 onward.

Refutation: if the robot finds laptop_hana at entry_hook_e1 at 19:00 or 20:00 on a weekday, this document is wrong. If it finds the laptop at desk_b1 during 18–22 h, this document is supported.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at desk_b1 at 20:00 on a weekday (not at the entry hook)",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Hana's water bottle is at desk_b1 at 20:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Hana's pen is at desk_b1 at 20:00 on a weekday",
   "target": "pen_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Hana's handbag stays at the entry hook at 20:00 on a weekday",
   "target": "handbag_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 19,
   "to": 22
  }
 ],
 "targets": {
  "laptop_hana": [
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
    "to": 17.75,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.75,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 21,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_hana": [
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
    "to": 17.75,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.75,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 21,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "pen_hana": [
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
    "to": 17.75,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.75,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 21,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "handbag_hana": [
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
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 22,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
