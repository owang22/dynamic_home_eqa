# p_3e7d — The 10-to-5 desk: coffee table bookends, remote never moves

Marco is a standard commuter: out by 8, home by 5:30 on weekdays, his keys and backpack at the entry in the morning and evening. Omar works from home, but his laptop is not at the desk for the entire 9-to-5 block. The patrol passes show it on the coffee table at 09:00 (three sightings), at the desk from 10:00 through 17:00 (eight sightings across five time points), and back on the coffee table by 18:00. The seventeen empty looks at desk_o1 during 9–17 h are concentrated in the 9–10 h window (laptop still at the coffee table) and a brief gap around 17 h (laptop drifting to the bookshelf). His water bottle follows the same arc: dish rack overnight, coffee table at 9, desk from 10 to 17, counter at 18, kitchen table at dinner.

This document sets itself apart from the desk-all-day hypotheses (p_a1b2, p_3a7f, p_8c2d, p_d8c3) by placing the laptop at the coffee table before 10 and after 17.5, and the water bottle at the desk (not the counter) during work. It also places the remote permanently on the tv_stand (the coffee-table remote claims in p_789a and p_f4a7 have been against five times each with zero for), the snack bowl on the kitchen counter during TV (not the coffee table), and Marco's guitar on the couch at 21:00 (the bedroom-floor claim was contradicted by the 21:00 couch sighting). The pan emerges from the cupboard at 18:30, not 17:50.

This document is refuted if: the laptop is found at the desk at 09:15 on multiple days; the remote is sighted on the coffee table during the 20–22 h window; the snack bowl appears on the coffee table during TV; or the guitar is in the bedroom at 21:00.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at his desk during core work hours",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 17
  },
  {
   "claim": "Omar's laptop is on the coffee table before his desk block starts",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 9,
   "to": 10
  },
  {
   "claim": "Omar's water bottle is at his desk during work, not the counter",
   "target": "water_bottle_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 17
  },
  {
   "claim": "The remote stays on the tv stand during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the kitchen counter during TV",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Marco's guitar is on the couch during the late evening",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "water_bottle_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
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
    "days": "both",
    "from": 18,
    "to": 18.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
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
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
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
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
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
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
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
