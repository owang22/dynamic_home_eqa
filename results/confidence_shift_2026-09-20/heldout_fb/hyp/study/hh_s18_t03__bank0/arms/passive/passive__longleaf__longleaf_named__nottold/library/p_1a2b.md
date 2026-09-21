# p_1a2b — Ines's three-session day: desk-morning, mobile-midday, desk-afternoon

Ines works from home in the office room on a three-session rhythm. The morning session (9–11) is at the desk. Around 11 she picks up the laptop and moves through the house—balcony, kitchen, hallway—working in short bursts while carrying it, so it is on her person from roughly 11 to 15. By 15 she is back at the desk for the late-afternoon push, and after 17:30 she sets the laptop on the office floor while she winds down. The charger, headphones, pen, and water bottle stay anchored at the desk throughout the workday; the mug moves from the kitchen table in the morning to the desk by 9 and to the coffee table after 21. Elena commutes to her office in town, leaving at 8 and returning at 5:30, taking her keys, laptop, backpack, jacket, and sunglasses with her. In the evening the household converges on the coffee table: the remote and blanket migrate from the TV stand and couch around 21, the speaker moves to the couch by 20, and the snack bowl reaches the coffee table by 22:30.

What sets this apart from the library: the laptop is ON_PERSON during 11–15, not at the desk (which explains the 24 empty looks at desk_o1 in that window) and not on the floor (which explains the zero sightings at floor_o_o1). The charger and headphones remain at the desk even while the laptop is mobile, matching the charger sightings at desk_o1 at 12, 14, 15 and the headphones sightings at desk_o1 from 14 onward.

What would refute it: a sighting of laptop_ines at desk_o1 or floor_o_o1 during 11–15 on a weekday; a look at Ines that shows she is not carrying the laptop; the charger or headphones found away from desk_o1 during 9–17.5 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on her person during the midday mobile session",
   "target": "laptop_ines",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Ines's laptop is at the office desk during the late-afternoon session",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 15,
   "to": 17.5
  },
  {
   "claim": "Ines's charger stays at the office desk during the midday mobile session",
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
  },
  {
   "claim": "The remote is on the coffee table during the 21-to-23h TV window",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
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
    "at": "ON_PERSON",
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
  "mug_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
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
    "chance": "usually"
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
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22.5,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
