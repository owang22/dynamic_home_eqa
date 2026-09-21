# p_9b4a — Ines at the desk 14–18 h only; morning work on the floor; 21:00 TV shift

This document proposes a split-day pattern: Ines works from the office floor (floor_o_o1) in the morning (09:00–12:00) and then moves to the desk (desk_o1) for the afternoon block (14:00–18:00). The 12:00–14:00 gap is a kitchen lunch. This explains why the laptop is at desk_o1 at 16:00 and 17:00 (afternoon block) but NOT at 10:00 (morning, still on floor). The 10:00 desk sighting is an anomaly (perhaps she briefly used the desk for a phone call).

The charger is at desk_o1 during the afternoon block (14:00–18:00) because she moves it with her. In the morning the charger is on the floor with the laptop. The headphones follow the same pattern: floor in the morning, desk in the afternoon, bed at 21:00.

Elena commutes as usual. The 21:00 TV migration is standard.

What sets this apart: the laptop is at desk_o1 for the full 14–18h block (not just 16–17.5h). If the laptop is found at desk_o1 at 14:00 or 15:00 on a weekday, this document is supported; if it is at floor_o_o1 at those times, it is refuted.

Refutation: laptop_ines at floor_o_o1 during 14:00–17:00 on a weekday would contradict the afternoon-desk claim.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on the office floor at 10:00 on weekdays",
   "target": "laptop_ines",
   "expect": "floor_o_o1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Ines's laptop is on the office desk at 15:00 on weekdays",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 17
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
   "claim": "Elena's backpack is out of the house at 10:00 on weekdays",
   "target": "backpack_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "The blanket is on the coffee table at 22:00 on both days",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "floor_o_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
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
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "charger_ines": [
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "floor_o_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 9,
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
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "floor_o_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 9,
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
  "mug_ines": [
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 15,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
