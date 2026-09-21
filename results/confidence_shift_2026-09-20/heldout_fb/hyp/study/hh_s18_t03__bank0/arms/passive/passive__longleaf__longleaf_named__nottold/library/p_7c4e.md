# p_7c4e — Ines's three-session work day: laptop on the floor midday, accessories anchored at the desk (fork of p_4d7a)

Fork of p_4d7a. The parent placed Ines's laptop ON_PERSON during the midday mobile session (10:30–15:30). That claim has accumulated zero evidence in either direction over five days, while two concrete sightings put the laptop on floor_o_o1: at 03:00 (one of three overnight sightings) and at 18:00 (the wind-down after work). The floor is the natural resting surface in the office room when the laptop is off the desk. I therefore replace the ON_PERSON midday block with floor_o_o1 and relax the late-afternoon desk block from "usually" to "sometimes," because the 16:00–17:30 claim has resolved 3-for / 8-against: the laptop is at the desk on some afternoons but not all. Everything else in the parent is retained: the charger, headphones, pen, and water bottle stay at desk_o1 as anchor objects; Elena commutes 8:00–17:30 taking her keys, backpack, laptop, jacket, and headphones with her.

What sets this apart from p_4d7a (parent): the midday laptop is on the office floor, not on Ines's person. What sets it apart from p_3e7a and p_c4d9 (floor-workspace documents): the charger, headphones, and pen are NOT on the floor — they remain at the desk. What sets it apart from p_a3f7 (laptop at desk all day): the laptop is absent from the desk 10:30–15:30.

Refutation: if laptop_ines is sighted at desk_o1 during 11:00–15:00 on a weekday, or if charger_ines or pen_ines is sighted on floor_o_o1 during work hours, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on the office floor during the midday session on weekdays",
   "target": "laptop_ines",
   "expect": "floor_o_o1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Ines's charger stays at the office desk during the midday session when the laptop is off the desk",
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
    "at": "floor_o_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15.5,
    "to": 18,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "floor_o_o1",
    "chance": "usually"
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
    "to": 23,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "sometimes"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
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
