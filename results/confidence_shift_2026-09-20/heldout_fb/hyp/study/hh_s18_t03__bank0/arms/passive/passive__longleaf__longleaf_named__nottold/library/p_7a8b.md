# p_7a8b — Ines's midday in the bedroom: laptop on the bed 11–15h

Ines takes her midday work session to the bedroom. Around 11 she carries the laptop to the bed and works from there—half reclining, maybe with a snack—until about 15, when she brings it back to the office desk. The charger stays at the office desk (the laptop is on battery during the midday). The headphones are at the desk. In the late afternoon the laptop returns to the desk, and after 17:30 it moves to the office floor. Elena commutes to her office in town with keys, laptop, backpack, and jacket. The evening migration to the coffee table follows the standard pattern.

What sets this apart: the laptop is at bed_b1 during 11–15, a location the robot rarely inspects during work hours, which explains the absence of sightings in that window. Unlike the ON_PERSON or balcony hypotheses, the laptop is set down on a fixed surface in a different room.

What would refute it: a sighting of laptop_ines at desk_o1 or floor_o_o1 during 11–15 on a weekday; a look at bed_b1 in that window that finds nothing; Ines being seen in the office without the laptop.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on the bed during the midday session",
   "target": "laptop_ines",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Ines's laptop is at the office desk during the morning session",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Ines's charger stays at the office desk during the midday bedroom session",
   "target": "charger_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Elena's keys are out of the house during her weekday work day",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "laptop_ines": [
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
    "to": 15,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "floor_o_o1",
    "chance": "sometimes"
   }
  ],
  "charger_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
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
    "days": "both",
    "from": 20,
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
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
