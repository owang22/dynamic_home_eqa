# p_3f8a — Both drive on weekdays; cycling gear stays home all day

Yuki and Omar both drive to work on weekdays. Neither cycles to the office or the afternoon shift, so their helmets hang at the entry hook and their bike locks sit on the entry table for the entire day, including the hours when the owner is out. What *does* leave the house is the personal carry-kit: Yuki's keys, laptop, notebook, water bottle, jacket, backpack, sunglasses, wallet, and shoes go out at roughly 08:00 and return by 17:30. Omar's handbag, lunchbox, notebook, pen, scarf, shoes, and wallet leave at about 13:40 and come back near 23:00. The bike locks and helmets are the tell: on any weekday the robot will find them at the entry whether or not the owner is home, because they are simply not part of the commute.

This hypothesis is set apart from p_a1b2 (dual cycling) and p_7a3f (Yuki cycles) by the in-house presence of both helmets and both bike locks during 09:00–17:00, and by the out-of-house absence of Yuki's personal items during the same window. It is set apart from p_c3d4 (WFH three days) by the fact that Yuki's laptop and notebook are *not* at the office desk on any weekday morning—they are gone with her to the office in town.

Refutation: sighting either helmet or either bike lock OUT_OF_HOUSE on a weekday; finding Yuki's laptop, notebook, or keys inside the house between 09:00 and 17:00; finding Omar's handbag or lunchbox inside the house between 14:00 and 22:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's helmet is at the entry hook on a weekday at 14:00 while she is at work",
   "target": "helmet_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Omar's bike lock is at the entry table on a weekday at 16:00 while he is at work",
   "target": "bike_lock_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Yuki's laptop is out of the house on a weekday at 12:00",
   "target": "laptop_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 11,
   "to": 13
  },
  {
   "claim": "Omar's handbag is out of the house on a weekday at 18:00",
   "target": "handbag_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Yuki's keys are at the entry floor on a weekday at 18:30 after she returns home",
   "target": "keys_yuki",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 18,
   "to": 19
  }
 ],
 "targets": {
  "helmet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "helmet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "laptop_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "sunglasses_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "handbag_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "pen_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "scarf_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "shoes_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
