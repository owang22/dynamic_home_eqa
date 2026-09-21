# p_7f3e — Ines works from the office floor with two desk visits; Elena commutes; 21:00 TV shift

Ines (resident_1) works from home but her primary work surface is the office floor (floor_o_o1), not the desk. She settles onto the floor around 9:00 and works there for the bulk of the day, pulling the laptop up to desk_o1 for two focused blocks: roughly 10:00–11:00 and 16:00–17:30. Between those blocks (12:00–14:00) she takes a kitchen lunch and the laptop stays on the floor. The charger and headphones remain on desk_o1 throughout the work day because they are stored there (plugged in / kept in the desk drawer area); the 12:00, 14:00, 15:00, 17:00, and 18:00 sightings at desk_o1 confirm the charger never leaves the desk even while the laptop is on the floor. After 18:00 the laptop stays on the floor for casual browsing. At 21:00 the headphones go to bed_b1 for the evening.

Elena (resident_2) commutes to her office in town, out from about 08:00 to 17:30 on weekdays. Her keys, backpack, jacket, laptop, phone, and headphones are OUT_OF_HOUSE during that window. In the evening they return to the entry (keys, backpack, jacket) and bedroom (laptop, phone, headphones).

The 21:00 TV migration is consistent on both weekdays and weekends: the remote moves from tv_stand_l1 to coffee_table_l1, the blanket moves from couch_l1 to coffee_table_l1, and the speaker stays on couch_l1. The snack bowl reaches the coffee table by 23:00.

Weekends: both residents are home (seen in the bedroom at 03:00). They sleep in, take a midday errand (keys out ~12:00–15:00), and are home the rest of the day. The laundry basket appears on the bedroom floor in the evening (19:00–21:00). The shopping bag is on the kitchen counter after the errand (~16:00).

What sets this document apart: it places Ines's laptop on the office floor as the default work position (not the desk), with only two brief desk visits. The charger and headphones are at desk_o1 all day (not on the floor, not out of the house). This differs from the full-day desk documents (p_a3f7, p_d1e5) and the full-day floor documents (p_3e7a, p_c4d9) by splitting the laptop's position into floor-default with desk overrides.

Refutation: if the laptop is found at floor_o_o1 during 16:00–17:00 on a weekday (when this doc says desk), or if the charger is found at floor_o_o1 during 14:00–17:00, the core claim is wrong. If Elena's keys or laptop are sighted in the house during 10:00–15:00 on a weekday, the commute claim fails.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on the office floor at 13:00 on weekdays, not at the desk",
   "target": "laptop_ines",
   "expect": "floor_o_o1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Ines's charger is on the office desk at 15:00 on weekdays",
   "target": "charger_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Elena's laptop is out of the house at 12:00 on weekdays",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "The remote is on the coffee table at 22:00 on both weekdays and weekends",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Ines's headphones are on the office desk at 16:00 on weekdays",
   "target": "headphones_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 15,
   "to": 17.5
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "floor_o_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 11,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 17.5,
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
    "days": "both",
    "from": 0,
    "to": 9,
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
    "days": "both",
    "from": 22,
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
    "days": "both",
    "from": 21,
    "to": 24,
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
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
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
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "to": 23.5,
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
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "laundry_basket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ],
  "keys_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
