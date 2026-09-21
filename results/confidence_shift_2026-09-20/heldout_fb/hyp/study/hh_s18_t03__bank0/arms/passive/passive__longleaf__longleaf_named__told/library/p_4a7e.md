# p_4a7e — Midday floor: laptop drops to the office floor 11–15, charger stays at the desk

Ines works from the office room, but her workstation is not fixed to the desk. In the morning she sits at desk_o1 with the laptop, charger, and pen. Around 11 she moves the laptop to the office floor for a midday block—perhaps a different kind of task, or she simply finds the floor more comfortable for a stretch. The charger stays plugged in at the desk because it is tethered to the wall outlet; the laptop runs on battery during the floor block. Headphones are at the bedroom in the morning (Ines uses them in bed or they rest there overnight-to-9) and return to the desk for the afternoon. In the late afternoon the laptop comes back to the desk, and by 18 it goes to the floor again for the evening.

Elena commutes to her office in town from about 8 to 17:30. Her laptop stays at the bedroom desk (she uses the office's computer); her keys and backpack leave with her and return in the evening.

Evening follows the familiar pattern: the remote, blanket, and speaker migrate toward the coffee table and couch around 21:00 for TV.

**What sets this apart:** the laptop is on floor_o_o1 during 11–15 h on weekdays, not at the desk. The charger remains at desk_o1 throughout the workday (it is plugged in). Headphones are at bed_b1 from 9 to 14 h.

**What would refute it:** repeated sightings of laptop_ines at desk_o1 during 11–15 h on weekdays, or charger_ines on the floor during that window.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on the office floor during the midday block on weekdays",
   "target": "laptop_ines",
   "expect": "floor_o_o1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Ines's laptop is at the office desk at 10:00 on weekdays",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 11
  },
  {
   "claim": "Ines's charger stays at the office desk during the midday floor block",
   "target": "charger_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Ines's headphones are on the bed in the morning before the afternoon work block",
   "target": "headphones_ines",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Elena's keys are out of the house during her weekday work day",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 0,
    "to": 11,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 15,
    "at": "floor_o_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
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
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "usually"
   }
  ],
  "headphones_ines": [
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
    "to": 14,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 21,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "bed_b1",
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
  "pen_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "almost_always"
   }
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
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
    "chance": "usually"
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
    "chance": "usually"
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
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ]
 }
}
```
