# p_4c9b — The TV stand remote: evening TV without the coffee table

The remote stays at the TV stand. It is sighted there on all four days the robot has looked, and every document in the library that places it on the coffee_table_l1 during evening TV has accumulated against-tallies (p_789a: against 5; p_f4a7: against 5; p_b2e9: against 5). The evening routine is: cooking in the kitchen around 18:30–19:30 (pan on the counter at 19:00, back in the cupboard by 20:00), then settling into the living room for TV with the remote at the TV stand. The snack bowl is on the kitchen counter during the evening (seen there at 18:00 twice and 20:00 three times), not on the coffee table. The guitar is in the bedroom until about 20:00, then Marco carries it to the couch for his evening playing (seen on couch_l1 at 21:00). The blanket stays on the couch throughout.

This document differs from p_789a and its forks by placing the remote at tv_stand_l1 (not coffee_table_l1) and the snack bowl at counter_k1 (not coffee_table_l1). It also captures the guitar's 21:00 migration to the couch, which p_789a misses.

What would refute this document: finding the remote on the coffee table or in a resident's hand during the 20:00–22:00 window, or finding the snack bowl on the coffee table during TV.

```json
{
 "claims": [
  {
   "claim": "The remote is on the TV stand during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the kitchen counter during the evening",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The pan is on the counter while cooking is in progress",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19,
   "to": 19.5
  },
  {
   "claim": "The guitar is on the couch during Marco's evening playing",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  }
 ],
 "targets": {
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
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
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
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
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
