# p_d9e6 — Ines never leaves; her pen stays at the desk; the office is her world all day

Ines works from home every day and never leaves the house. Her pen is at the office desk (desk_o1) throughout the day — it's her writing tool and stays at the desk even while she works from the floor. The pen is found at the desk 1 out of 4 times during 9–17h looks (the other 3 found nothing, suggesting it's sometimes on the floor with her or tucked into a notebook). Her jacket, shoes, and umbrella stay at the entry all day because she doesn't go out. Her keys remain at the entry table. Elena's laptop goes to her office and returns to the bedroom desk in the evening. The vacuum cleaner is at the entry floor in the morning (03:00, 09:00) and in the living room by 18:00, suggesting it's used or stored in the living room in the evening. The pot is in the cupboard at night and on the counter during cooking (19:00). This document is distinguished by asserting Ines never leaves the house and by placing her pen at the desk, her jacket at the entry hook, and her keys at the entry table throughout the work day.

What would refute it: If Ines's pen is found outside the office room during 9–17h on a weekday, or if Ines's jacket is found outside the entry during the day, or if Ines's keys are found outside the entry table during 9–17h.

```json
{
 "claims": [
  {
   "claim": "Ines's pen is at the office desk during weekday work hours",
   "target": "pen_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Ines's jacket is on the entry hook during weekday work hours",
   "target": "jacket_ines",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's laptop is at the bedroom desk in the evening",
   "target": "laptop_elena",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 23
  },
  {
   "claim": "Ines's keys are at the entry table during weekday work hours",
   "target": "keys_ines",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "pen_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "jacket_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "umbrella_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "keys_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
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
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
