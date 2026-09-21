# p_4e7a — Omar's two-block desk day with a kitchen-table lunch gap

Marco commutes to his office (out 8–17:30 weekdays); Omar works from home but not in one continuous sit. The clock-hour data is unambiguous: Omar's laptop, mouse, notebook, and pen are at desk_o1 at 09:00 and 10:00, then absent from the desk at 11:00 and 12:00, then back at 13:00 and 15:00, then absent again at 16:00 and 17:00. The 12:00 pass shows his glass and plate at kitchen_table_k1, placing him at the kitchen table for lunch. His headphones follow the same two-block pattern (desk at 10, 11, 14; couch at 18). Critically, his pencil case, sketchbook, and plant pot 3 are at desk_o1 on 0 of 16 weekday 9–17h looks—these personal items never share the desk with the active work set.

This document differs from p_a1b2 and p_8c2d (which assume a continuous 9–17:30 desk presence) by splitting the day into two focus blocks with a real gap. It differs from p_f3e1 (which puts the midday gap at the kitchen table with the laptop open) by closing the laptop and moving to the kitchen table for a meal. It differs from p_c3d4 (laptop out of the house at lunch) because the 13:00 sighting at desk_o1 rules out a full out-of-house lunch; the gap is in-house at the kitchen table.

Refutation: if the robot finds laptop_omar at desk_o1 at 11:00 or 12:00 on a weekday, the two-block model collapses. If pencil_case_omar or sketchbook_omar appears at desk_o1 during 9–17h on a weekday, the "clean desk" claim fails.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at his desk during the morning focus block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Omar's laptop is at the kitchen table during his midday lunch",
   "target": "laptop_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 12.5
  },
  {
   "claim": "Omar's laptop is back at his desk during the afternoon focus block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Omar's pencil case is not at his desk during weekday work hours",
   "target": "pencil_case_omar",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's keys are out of the house during his workday",
   "target": "keys_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
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
    "chance": "usually"
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "desk_o1",
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
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
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
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "from": 11,
    "to": 13,
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
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
    "to": 17,
    "at": "drawer_k_k1",
    "chance": "sometimes"
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
    "to": 17,
    "at": "desk_b1",
    "chance": "rarely"
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
    "to": 17,
    "at": "side_table_l1",
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
    "chance": "usually"
   }
  ],
  "backpack_marco": [
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
    "chance": "usually"
   }
  ]
 }
}
```
