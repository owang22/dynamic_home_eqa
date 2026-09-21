# p_f2b8 — Hana Works Late, Laptop Out Until 19

A variant of the commuter routine where Hana's workday runs longer than the standard 5:30 finish. On weekdays she is out until **19:00** (overtime, a meeting, a commute delay). Her laptop, keys, jacket, water bottle, and pen are all OUT_OF_HOUSE from 8 to 19 h. She arrives home at 19:00, so the "evening desk session" (p_4a7e) or "brief entry" (p_1d9b) windows shift later: 19:00–22:00. This means the robot's 18:00 looks in the kitchen find both residents (Priya home, Hana not yet back) and the laptop is simply not in the house.

What sets this apart: p_a3f1 and p_4a7e have Hana home by 17:30–17:50. This document says she is out until 19:00. The guitar claim from p_a3f1 (bedroom_floor_b1 at 17–19 h) is consistent (Hana isn't home to play it). The p_e3f8 document (out until 19, no guitar) is close but also says no guitar on weekdays; this document allows guitar after 19:30.

Refutation: if the robot finds Hana (resident_1) in any room before 19:00 on a weekday, or finds laptop_hana in the house during 8–19 h, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is out of the house at 18:00 on a weekday (she is still at work)",
   "target": "laptop_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Hana's keys are out of the house at 18:00 on a weekday",
   "target": "keys_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Hana's jacket is out of the house at 18:00 on a weekday",
   "target": "jacket_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The guitar is on the bedroom floor at 18:00 on a weekday (Hana not home to play)",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
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
  "keys_hana": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
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
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
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
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
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
    "from": 7.5,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
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
    "from": 19.5,
    "to": 21.5,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
