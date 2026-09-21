# p_5d4c — Omar works at the coffee table, not the desk; his desk is only for sketching

Omar's primary work surface is coffee_table_l1, where laptop_omar sits 09:00–17:30 on weekdays. His desk_o1 is reserved for sketching (weekend afternoons, weekday evenings). The mouse, pen, and notebook go to the coffee table during work. Marco is a standard commuter (08:00–17:30). Evening: cook 18:00–19:00, dinner 19:00–19:45, TV 20:00–22:00, hobbies 22:00–23:00. Weekend: sleep in to 10:30, errands 12:00–14:00, Omar sketches at desk_o1 15:00–17:00. What sets this apart: laptop_omar is at coffee_table_l1 (not desk_o1) during weekday work hours. What would refute it: laptop_omar sighted at desk_o1 between 10:00 and 16:00 on a Monday.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at the coffee table during his work block",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's mouse is at the coffee table during work",
   "target": "mouse_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's sketchbook is at his desk on weekend afternoons",
   "target": "sketchbook_omar",
   "expect": "desk_o1",
   "days": "weekend",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Marco's laptop stays at his desk all day",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
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
    "to": 17.5,
    "at": "coffee_table_l1",
    "chance": "almost_always"
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
    "to": 17.5,
    "at": "coffee_table_l1",
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
    "to": 17.5,
    "at": "coffee_table_l1",
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
    "to": 17.5,
    "at": "coffee_table_l1",
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
    "days": "weekend",
    "from": 15,
    "to": 17,
    "at": "desk_o1",
    "chance": "almost_always"
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
    "days": "weekend",
    "from": 15,
    "to": 17,
    "at": "desk_o1",
    "chance": "almost_always"
   }
  ],
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "class:keys": [
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
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "class:wallet": [
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
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "class:jacket": [
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
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ]
 }
}
```
