# p_5d7f — Ines's floor workspace: full-day object tracking

Ines works from the office room but her laptop lives on the floor beside the desk, not on the desk surface itself. The robot's 9–17 h looks at desk_o1 find the laptop only 1 out of 9 times, while the 03:00 and 18:00 passes catch it on floor_o_o1. Her mug follows a clear arc: kitchen table for breakfast (03:00, 07:00 passes), office desk for the afternoon (14:00, 17:00, 18:00 passes), and coffee table for the evening (22:00 pass). Her water bottle sits at the desk from 08:00 through 18:00 and moves to the kitchen table at 19:00. Headphones rest at the desk from early morning through 18:00 and shift to the bed at 21:00. The charger stays at the desk essentially all day, occasionally seen at the dresser or nightstand at the extremes of the day.

Elena commutes to her office in town, leaving around 08:00 and returning around 17:30. During those hours her laptop, keys, backpack, jacket, hat, headphones, wallet, and sunglasses are all out of the house. In the evening her laptop returns to the bedroom desk, keys to the entry table, backpack to the entry floor.

This document sets itself apart from p_a3f7 and p_d1e5 (which place Ines's laptop at desk_o1 during work) by putting it on the floor, and from p_b8c2 (nothing leaves) by tracking Elena's objects out of the house. It also differs from the partial floor-workspace documents (p_3e7a, p_c4d9, p_e4a1) by adding the full-day mug, water-bottle, and headphone trajectories.

Refutation: finding Ines's laptop at desk_o1 during 9–17 h on a weekday, or finding Elena's laptop/keys/backpack inside the house during 9–17 h on a weekday.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is on the office floor during weekday work hours",
   "target": "laptop_ines",
   "expect": "floor_o_o1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Ines's mug is at the office desk in the afternoon on weekdays",
   "target": "mug_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Elena's laptop is out of the house during weekday work hours",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Ines's headphones are at the office desk during weekday work",
   "target": "headphones_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Ines's water bottle is at the office desk during weekday work",
   "target": "water_bottle_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "floor_o_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 18,
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
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "headphones_ines": [
   {
    "days": "weekday",
    "from": 7,
    "to": 19,
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
  "charger_ines": [
   {
    "days": "both",
    "from": 7,
    "to": 23,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 23,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
