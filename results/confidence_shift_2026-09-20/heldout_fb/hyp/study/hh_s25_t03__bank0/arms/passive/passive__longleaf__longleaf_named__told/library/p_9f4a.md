# p_9f4a — Evening wind-down: remote migrates TV stand to coffee table to floor; snacks out; blanket placement by day type

The evening TV session (20:00–22:30) follows a consistent sequential pattern. The remote starts on the TV stand (seen there at 03:00 and 18:00), moves to the coffee table during active TV (seen at 21:00), and ends up on the living room floor after TV winds down (seen at 22:00). The snack bowl comes out of the cupboard or counter at 18:00 (evening prep) and is on the coffee table during the TV window (21:00–22:00, seen 3 times at 22:00). The blanket is on the couch during the pre-TV evening on weekdays (18:00–21:00) but shifts to the coffee table on weekends for the entire evening (18:00–23:00). Marco's water bottle is at the dining table during dinner (20:00, seen 2 times). Omar's glasses migrate to the armchair or TV stand during the TV session (seen at 21:00–22:00). Marco's mug appears at the coffee table during the later evening (21:00).

This document sets itself apart from p_6d1a and p_3630 (which place the remote on the floor for the full 21:00–23:00 window) by splitting the remote's evening into two phases: coffee table during active TV (20:00–22:00) and floor after TV ends (22:00–23:30). It differs from p_8a6b in that it places the blanket on the couch on weekdays (not just the coffee table) and specifies the sequential snack bowl movement.

This document is refuted if: the remote is never seen on the coffee table during 20:00–22:00; the snack bowl is never on the coffee table during the TV window; the blanket is on the couch during weekend evenings (20:00–23:00); or the water bottle is never at the dining table at 20:00.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table during the active evening TV window",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "The remote is on the living room floor after TV ends",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the coffee table during the TV window",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The blanket is on the coffee table during weekend evenings",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Marco's water bottle is at the dining table during dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19.5,
   "to": 21
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
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "floor_l_l1",
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
    "days": "weekend",
    "from": 18,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "days": "both",
    "from": 21,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22.5,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 22.5,
    "at": "tv_stand_l1",
    "chance": "rarely"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
