# p_6e2c — Marco's morning desk: items visible 8–14, then in active use

Marco's desk (desk_b1) holds his laptop, notebook, mug, charger, pen, and water bottle. In the morning (8–14) these items are in a visible resting state: the laptop is open, the notebook is flat, the mug is full. The robot can see and register them. After 14:00, Marco is in active work mode — the laptop is open and being typed on (screen lit, not a "resting" state the robot registers), the notebook is in use, and the water bottle has been carried to the kitchen. The items return to visible resting state at 17:00 when work ends.

What sets this apart: p_a1b2 and p_c3d4 claim the laptop is at desk_b1 for the full 9–17 window, earning 30 "against" votes because the robot looks at the desk mid-day and doesn't register the laptop. My document limits the laptop claim to 8–11 (when it IS found) and the notebook to 9–12 (when it IS found), avoiding the 12–17 window where the robot consistently fails to find them. The mug stays visible longer (through 14) because it's a passive object that doesn't change appearance when "in use."

What would refute it: finding the laptop at a receptacle other than desk_b1 during 8–11, finding the notebook at the bedroom floor during 9–12 (it IS seen there at 11 once, but mostly at desk), or finding the water bottle at the desk at 14:00.

```json
{
 "claims": [
  {
   "claim": "Marco's laptop is open and visible at his desk in the morning",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 11
  },
  {
   "claim": "Marco's notebook is flat and visible at his desk during morning work",
   "target": "notebook_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Marco's mug is at his desk during the morning work session",
   "target": "mug_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Marco's charger is at his desk in the early morning before work begins",
   "target": "charger_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 11,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 12,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 9,
    "to": 14,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "charger_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 10,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 10,
    "to": 17,
    "at": "desk_b1",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ],
  "pen_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
