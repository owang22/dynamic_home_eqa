# p_4e2a — Omar's two-phase desk day: coffee table before ten, desk ten to five, coffee table after; evening counter is the snack station

Marco commutes to his office 8:00–17:30 on weekdays (out with his keys, backpack, notebook, and jacket). Omar works from home at desk_o1, but his laptop does not sit at the desk for the full nine-to-five block. The sightings show the laptop at the coffee table at 03:00 (2 of 3 passes) and at 09:00 (3 of 6 passes), then firmly at desk_o1 from 10:00 through 17:00, and back at the coffee table by 18:00. A minority of passes (03:00, 09:00, 17:00, weekend 03:00) find it on bookshelf_l1, suggesting it is sometimes shelved overnight or at the end of a long day. The evening routine is anchored by the kitchen counter, not the coffee table: the snack bowl is on counter_k1 at both 18:00 and 20:00 passes, the pan moves from cupboard to counter between 18:00 and 19:00 (cooking 18:30–20:00), and the remote stays at tv_stand_l1 throughout. Marco's guitar is on the bedroom floor at 18:00 and migrates to the couch by 21:00 for his evening playing. Omar's water bottle is a mobile object: dish rack overnight, coffee table in the morning, desk during the afternoon work block, kitchen table at dinner.

This document differs from p_a1b2 (laptop at desk 9–17.5) by splitting the morning: the laptop is at the coffee table until 10:00, not the desk. It differs from p_789a by putting the snack bowl on the kitchen counter (not the coffee table) and the remote at the TV stand (not the coffee table). It differs from p_c3d4 by keeping the laptop in the house all day (no lunch run). If the laptop is found at desk_o1 before 10:00 on multiple weekday mornings, or if the snack bowl is consistently on the coffee table at 19:00–21:00, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at the coffee table before he starts desk work on weekday mornings",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Omar's laptop is at his desk during the main work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 17
  },
  {
   "claim": "The snack bowl is on the kitchen counter during the evening, not the coffee table",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18,
   "to": 21
  },
  {
   "claim": "The remote stays on the TV stand during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The pan is on the counter while cooking is in progress",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18.5,
   "to": 20
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
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
    "from": 18,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 11,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 15,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
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
  "backpack_marco": [
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
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
