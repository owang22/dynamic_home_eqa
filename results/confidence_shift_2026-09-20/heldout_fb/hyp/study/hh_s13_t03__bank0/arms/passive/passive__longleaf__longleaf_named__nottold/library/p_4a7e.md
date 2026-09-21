# p_4a7e — Desk Evening, No Counter Cook

Hana and Priya share the house. Hana works in town 8 to 5:30 on weekdays; Priya is retired and home most of the day. The critical difference this document makes: Hana's evening is a **desk session**, not a kitchen session. She comes home around 17:30, drops her coat at the entry, and goes to desk_b1 in bedroom-b1 to do evening work or study (laptop, pen, water bottle all travel with her to the desk). There is **no active cooking at the counter in the evening**: the pan stays in the cupboard, the knife stays in the drawer, the cutting board stays in the cupboard. Dinner is a simple affair—perhaps a pot Priya started in the afternoon, or a quick reheat at the stove that doesn't require the pan to sit on the counter during the 17:30–19:00 window the robot patrols.

What sets this apart: every other evening document (p_b9c4, p_c1d6, p_a9b4, p_d3e8) places either cooking items on the counter or Hana's laptop at the entry hook or kitchen table during 18–22 h. This document says neither. The laptop is at desk_b1; the pan is in cupboard_k1; the knife is in drawer_k_k1.

Refutation: if the robot finds laptop_hana at entry_hook_e1 or kitchen_table_k1 during 18–22 h on a weekday, or finds pan_shared on counter_k1 during 17.5–19 h, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at desk_b1 during the evening work session on a weekday",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The pan is in the cupboard (not on the counter) at 18:00 on a weekday",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The kitchen knife is in the drawer (not on the counter) at 18:00 on a weekday",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's water bottle is at desk_b1 at 20:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "desk_b1",
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
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 13,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
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
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "rarely"
   }
  ],
  "cutting_board_shared": [
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
    "chance": "rarely"
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
  ]
 }
}
```
