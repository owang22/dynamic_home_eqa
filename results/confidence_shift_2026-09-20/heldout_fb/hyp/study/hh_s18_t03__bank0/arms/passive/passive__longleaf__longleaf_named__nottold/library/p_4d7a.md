# p_4d7a — Ines's three-session work day: laptop mobile midday, accessories anchored at the desk

Ines works from the office room at the desk (desk_o1), but not continuously. The evidence shows her laptop at the desk at 10:00, 16:00, and 17:00 on weekdays, yet 24 out of 26 targeted looks at desk_o1 during 9–17 h found nothing. The resolution: she works in three sessions. Morning session (9–10:30) at the desk; a midday mobile session (10:30–15:30) where she picks the laptop up and works from the office floor or with it in her lap, taking calls and breaks; a late-afternoon session (15:30–18:00) back at the desk; and by 18:00 the laptop is set on the office floor as she winds down. Crucially, her charger, headphones, pen, and water bottle stay at the desk throughout — they are the "anchor" objects that never move. This is why the charger is found at desk_o1 in 5 of 26 looks (the rest being brief absences when she unplugs it) while the laptop is found in only 2 of 26. Elena commutes to her office in town as usual, taking her keys, backpack, laptop, jacket, and headphones with her.

What sets this apart from p_a3f7 (laptop at desk all day) and p_7f3a (laptop ON_PERSON 9–16 h): here the laptop is at the desk for defined morning and late-afternoon windows, and ON_PERSON only during the midday gap. It also refutes the floor-workspace documents (p_3e7a, p_c4d9, p_e6b1) because the charger, headphones, and pen are NOT on the floor — they stay at the desk.

Refutation: if the laptop is sighted at desk_o1 during 11:00–15:00 on a weekday, or if the charger is sighted on the office floor during work hours, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on her person during the midday mobile session on weekdays",
   "target": "laptop_ines",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Ines's charger stays at the office desk during the midday session when the laptop is mobile",
   "target": "charger_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Ines's headphones are at the office desk during the midday session",
   "target": "headphones_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Ines's laptop is back at the desk during the late-afternoon session",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 16,
   "to": 17.5
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 9,
    "to": 10.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 15.5,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15.5,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "floor_o_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "charger_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "almost_always"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "pen_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "keys_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
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
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_floor_e1",
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
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
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
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
