# p_7f3a — Ines works with laptop in hand; desk objects rest between sessions

Ines works from the office room, seated at the desk. The critical difference from every other document in the library is this: during her active work stretches she holds the laptop in her lap or on her hands (ON_PERSON), so a look at desk_o1 finds the desk surface empty of the machine. The 24 empty weekday looks at desk_o1 during 9–17 h are the signature of this routine. The laptop only touches the desk surface during short breaks—around 10:00 and again from 16:00 to 17:30—when she sets it down to stretch, grab a drink, or take a call. After work she moves the laptop to the office floor (confirmed at 18:00) where it stays until the next morning.

The charger follows the laptop: while Ines is actively working (9–12 h) the charger is plugged into the laptop and travels with it (ON_PERSON); once she sets the laptop down at midday the charger plugs into the wall at the desk and stays there through the afternoon (confirmed at 12:00, 14:00, 15:00, 17:00). The headphones are worn during morning focus sessions (ON_PERSON 9–14 h) and rest on the desk in the afternoon (confirmed 14:00–17:00).

Elena commutes to her office in town as described: out from roughly 08:00 to 17:30 on weekdays, her keys, backpack, jacket, and laptop all leaving the house. Ines does not leave for lunch; the charger at desk_o1 at 12:00 and the water bottle at desk_o1 at 14:00 confirm she is in the office through midday.

What would refute this document: the laptop consistently found at desk_o1 during 9–16 h on multiple weekday mornings; Ines sighted leaving the house at midday (keys, charger, or water bottle OUT_OF_HOUSE 12–14 h); or the charger found at desk_o1 during 9–11 h (which would mean the laptop is also at the desk, not ON_PERSON).

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on her person during weekday morning work",
   "target": "laptop_ines",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Ines's laptop rests at the office desk during weekday late-afternoon wind-down",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 16,
   "to": 18
  },
  {
   "claim": "Ines's charger is at the office desk during weekday afternoon",
   "target": "charger_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Elena's keys are out of the house during her weekday work day",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Ines's headphones rest at the office desk during weekday late afternoon",
   "target": "headphones_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 16,
   "to": 18
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 10.5,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 16,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "floor_o_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "desk_o1",
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
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
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
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "keys_elena": [
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
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "jacket_elena": [
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
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
