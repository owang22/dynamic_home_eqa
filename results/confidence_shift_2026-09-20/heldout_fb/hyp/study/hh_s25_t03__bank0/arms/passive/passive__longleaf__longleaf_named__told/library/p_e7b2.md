# p_e7b2 — p_9t4w — Weekend evening: no TV ritual, long dinner, remote stays at the stand

The weekend evening is structurally different from the weekday. On weekdays the remote migrates from the TV stand to the coffee table at 21:00 and to the floor at 22:00; the snack bowl appears at the coffee table at 21–22. On weekends, the remote is at the TV stand at 03:00 and still at the TV stand at 23:00 — it never moves to the coffee table or the floor. The snack bowl is at the sink at 03:00 and 23:00 on weekends, never at the coffee table. Meanwhile the serving dish is at the dining table at 20:00 (twice), 21:00, and 22:00 on a weekend, indicating a long, relaxed dinner that runs two hours versus the brief 20:00 appearance on weekdays. The blanket is on the coffee table at 21:00 and 23:00 on weekends (reading or napping, not TV).

What sets this apart: p_a1b2 and p_c3d4 apply the same remote-to-coffee-table and snack-bowl-to-coffee-table blocks on both day types. p_8a6b and p_9f4a capture the weekday remote migration but do not explicitly suppress it on weekends. This document says: on weekends there is NO TV ritual, the dinner is longer, and the blanket goes to the coffee table for quiet evening use.

What would refute it: finding the remote at the coffee table or the living room floor on a weekend between 20:00 and 23:00, finding the snack bowl at the coffee table on a weekend, or finding the serving dish back in the cupboard before 21:00 on a weekend.

```json
{
 "claims": [
  {
   "claim": "The remote stays at the TV stand throughout the weekend evening",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 20,
   "to": 23
  },
  {
   "claim": "The serving dish is at the dining table during the extended weekend dinner",
   "target": "serving_dish_shared",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The snack bowl remains at the kitchen sink during the weekend evening",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "weekend",
   "from": 20,
   "to": 23
  },
  {
   "claim": "The blanket is on the coffee table during the weekend evening",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 23.5
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 22.5,
    "at": "dining_table_d1",
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
    "days": "weekday",
    "from": 20.5,
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
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
