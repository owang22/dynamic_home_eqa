# p_f1b4 — Weekday Evening Settle: Blanket to the Coffee Table, Remote to the TV Stand by 17:00

This document models the weekday evening transition in the living room. The patrol passes show the blanket on the armchair or couch at 00:00 and 08:00, still mostly there at 16:00, but on the coffee table by 18:00. The remote is on the living room floor at 00:00 and 08:00, in transition at 16:00, and on the TV stand by 18:00. The transition happens between the 16:00 and 18:00 passes, when Priya is settling in for the evening and Hana is either still at work or just arriving.

This document differs from p_4f8a (which places the transition at 18:00 and gets 7 against on the blanket) by putting the cut at 17:00, and from p_c4f8 (which keeps the remote on the floor all day) by asserting the remote is on the TV stand from 17:00 onward. It also differs from p_4b7c (the weekend doc) which correctly keeps the blanket on the bed and remote on the TV stand all weekend.

Priya's water bottle is on the dining table through the weekday day and moves to the coffee table in the evening. On weekends both water bottles are at the dish rack.

What would refute this: a weekday 17–24 h sighting of blanket_shared on armchair_l1, or remote_shared on floor_l_l1 after 17:00.

```json
{
 "claims": [
  {
   "claim": "The shared blanket is on the coffee table on weekday evenings after 17:00, not on the armchair",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 17,
   "to": 23
  },
  {
   "claim": "The remote is on the TV stand on weekday evenings after 17:00, not on the living room floor",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 17,
   "to": 23
  },
  {
   "claim": "Priya's water bottle is on the dining table during the weekday day, not at the dish rack",
   "target": "water_bottle_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 8,
   "to": 16
  },
  {
   "claim": "The shared blanket is on the bed on weekend mornings, not on the armchair",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 8,
   "to": 16
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
