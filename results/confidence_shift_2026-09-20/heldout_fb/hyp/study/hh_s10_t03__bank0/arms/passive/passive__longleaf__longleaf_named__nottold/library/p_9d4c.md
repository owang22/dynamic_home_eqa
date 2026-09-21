# p_9d4c — The 21:00 wind-down: blanket to coffee table, snack bowl to cupboard, glass to nightstand

After dinner the household settles into its evening routine. By 21:00 the shared blanket has left the couch (where it rests all day) and is on the coffee table for TV. The snack bowl, which sits on the kitchen counter through the afternoon, goes into the cupboard at 21:00 and stays there through 22:00, returning to the counter at 23:00. Yuki's glass moves from the dining table to the nightstand by 22:00 (3 of 3 passes at 22:00 show nightstand). The remote stays at the TV stand until 23:00, when it migrates to the coffee table. Yuki's mug is at the coffee table by 22:00, though at 21:00 it is sometimes at the bedroom desk (3 of 6 passes), suggesting a brief stop before settling in.

This document differs from p_9c82, which claims the mug is at the coffee table from 20:5 (the 21:00 passes show it at desk_b1 on half the occasions). It differs from p_f1a6 and p_a3f7, which cover the 21:30 snapshot but do not track the 23:00 return of the snack bowl to the counter or the remote's migration. The blanket's all-day couch resting spot (confirmed by 8 of 13 daytime sightings) is explicit here.

Refutation: the snack bowl on the coffee table during 21–22h, the remote at the coffee table before 22:30, or the glass still at the dining table at 22:00.

```json
{
 "claims": [
  {
   "claim": "The shared blanket is on the coffee table at 21:30 on a weekday (TV time)",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22
  },
  {
   "claim": "The snack bowl is in the kitchen cupboard at 21:30 on a weekday (stored during TV)",
   "target": "snack_bowl_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 21,
   "to": 22
  },
  {
   "claim": "Yuki's glass is at the bedroom nightstand at 22:30 on a weekday (taken to the bedroom)",
   "target": "glass_yuki",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The remote is at the coffee table at 23:00 on a weekday (migrated from the TV stand)",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22.5,
   "to": 23.5
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20.5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 16,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 22.5,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekday",
    "from": 21,
    "to": 21.5,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
