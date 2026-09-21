# p_9d4e — The 21:00 Living Room Shift: Blanket, Snacks, and Mugs Migrate

On weekday evenings the living room is quiet until about 20:30. The blanket rests on the couch all day (confirmed by 5 finds at the couch during 9-17h looks). The snack bowl is in the kitchen (sink at 03:00 after washing, counter at 18-19 during dinner prep). The remote stays at the TV stand — on weekdays it does NOT move to the coffee table (all weekday sightings show tv_stand_l1). At 21:00 the TV session begins: the blanket is pulled from the couch to the coffee table, the snack bowl is carried from the kitchen to the coffee table, and Priya's mug is brought from the cupboard to the coffee table. By 22:00 the blanket and mug are still at the coffee table; by 23:00 things start going back.

What sets this apart: p_c9d4 (Late Night) puts the remote on the couch at 22:00 and the guitar on the coffee table at 22:00 — both are wrong (the remote is at the TV stand, the guitar never leaves the bedroom floor). p_5d9e and p_b4e7 capture the blanket and snack bowl migration but with windows that are too broad (20-23h) and miss the 21:00 transition point. This document pins the shift to 20.5-21h and keeps the remote at the TV stand on weekdays.

Refutation: if the blanket is seen on the coffee table at the 19:00 or 20:00 pass on multiple weekday evenings, the 21:00 shift is too late. If the remote is seen at the coffee table on a weekday evening, the "remote stays at TV stand" claim is wrong.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the coffee table at 21:00 on a weekday because the TV session has started",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table at 21:00 on a weekday because it was brought from the kitchen for TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22
  },
  {
   "claim": "The remote is at the TV stand at 21:00 on a weekday because it does not migrate on weekdays",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Priya's mug is on the coffee table at 22:00 on a weekday during the evening TV session",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
