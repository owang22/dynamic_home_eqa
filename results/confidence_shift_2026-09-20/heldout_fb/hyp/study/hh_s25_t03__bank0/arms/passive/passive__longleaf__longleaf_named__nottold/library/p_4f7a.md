# p_4f7a — The contained workday: laptops in hand and at coffee table; the house is a closed system

Omar and Marco are a dual-work-from-home couple. Nothing in this household ever leaves: no lunch outings, no morning runs, no errands during work hours. Both sets of keys, wallets, and jackets stay at the entry from the moment they come in until the moment they leave in the evening (after the robot's observation window). The evidence is unambiguous: five consecutive days of entry-table and entry-hook looks find both key sets, both wallets, both jackets, both hats, and Marco's running shoes in their resting spots with zero exceptions. The running-shoe hypothesis and the lunch-outing hypothesis are dead.

What sets this document apart is the *work-position* of the laptops. Marco's laptop is not on the desk surface during the core 10–16 h block; it is on his lap, in his hands, plugged in via the charger which is also in his hands. The 30 empty desk looks versus 8 positive finds during 9–17 h confirm the laptop is off the surface for most of the working day. It returns to the desk by 17:00 when he closes out. Omar's laptop, by contrast, is a nomad: it starts at his office desk, migrates to the living-room coffee table around 11:00 for the midday block (where he works more casually, perhaps with a mug), and returns to the office desk by 16:30–17:00. His charger follows the laptop; his mouse and headphones stay at the office desk.

This document refutes any hypothesis in which Marco's laptop rests on the desk surface during 10–16 h, or in which any object is OUT_OF_HOUSE during weekday work hours. It would be refuted if the robot found Marco's laptop on the desk at 12:00 or 14:00 on a weekday, or if either set of keys was missing from the entry table.

```json
{
 "claims": [
  {
   "claim": "Marco's laptop is in his hands on his lap during the core weekday work block, not on the desk surface",
   "target": "laptop_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's charger is in his hands plugged into the laptop during the core weekday work block",
   "target": "charger_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Omar's laptop is on the living-room coffee table during his midday weekday work block",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Marco's keys are at the entry table during weekday work hours and never leave the house",
   "target": "keys_marco",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's keys are at the entry table during weekday work hours and never leave the house",
   "target": "keys_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 10,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 16,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "charger_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 10,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "ON_PERSON",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 16,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 11,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "charger_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 12,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "keys_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "running_shoes_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
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
  ],
  "mouse_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "headphones_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
