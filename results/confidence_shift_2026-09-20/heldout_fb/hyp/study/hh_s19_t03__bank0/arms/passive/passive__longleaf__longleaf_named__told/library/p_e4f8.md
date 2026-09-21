# p_e4f8 — Omar's desk is for deep focus only: peripherals follow the laptop, personal items do not

This document isolates a pattern the library has been getting wrong: during Omar's work hours (weekday 09:00–17:00), desk_o1 holds the laptop, mouse, headphones, and notebook in two blocks (≈09–11 and ≈13–15), but the pencil case, sketchbook, and plant pot are NOT at the desk. All three show 0/16 weekday 9–17 h looks finding them at desk_o1. They are personal items that live at the desk in the evenings and on weekends but get stowed or moved during the workday.

The laptop and its immediate peripherals (mouse, headphones, notebook) follow Omar: desk during focus blocks, kitchen table during the midday break (≈11–13) and late-afternoon wind-down (≈15–17). The pencil case and sketchbook go to desk_b1 (Marco's desk, which is free during work hours) or to the coffee table. The plant pot moves to the side table.

What sets this apart from p_f3e1: this document makes the negative claim explicit — the pencil case, sketchbook, and plant pot are NOT at desk_o1 during 09–17 h on weekdays. p_f3e1 places them at desk_b1 as a fallback; this document also allows the coffee table for the sketchbook (Omar may sketch during his break).

What would refute it: pencil_case_omar at desk_o1 at 10:00 or 14:00 on a weekday; sketchbook_omar at desk_o1 at 11:00 on a weekday; plant_pot_3_shared at desk_o1 at 16:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Omar's pencil case is NOT at his desk during weekday work hours",
   "target": "pencil_case_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's sketchbook is NOT at his desk during weekday work hours",
   "target": "sketchbook_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's laptop is at the kitchen table during his midday break",
   "target": "laptop_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  },
  {
   "claim": "The plant pot 3 is NOT at Omar's desk during weekday work hours",
   "target": "plant_pot_3_shared",
   "expect": "side_table_l1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "pencil_case_omar": [
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
    "to": 17.5,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "sketchbook_omar": [
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
    "to": 17.5,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "plant_pot_3_shared": [
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
    "to": 17.5,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ],
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 11,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mouse_omar": [
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
    "to": 11,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "headphones_omar": [
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
    "to": 11,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "notebook_omar": [
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
    "to": 11,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "desk_o1",
    "chance": "almost_always"
   }
  ],
  "pen_omar": [
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
    "to": 11,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
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
  "laptop_marco": [
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
  ]
 }
}
```
