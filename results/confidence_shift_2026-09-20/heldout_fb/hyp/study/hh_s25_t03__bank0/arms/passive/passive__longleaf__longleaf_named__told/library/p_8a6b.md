# p_8a6b — Evening wind-down: remote to coffee table, blanket on couch, snacks out

The evening TV ritual (roughly 20:00–23:00) follows a consistent sequence. The remote starts the evening on the TV stand, moves to the coffee table around 21:00 (when someone picks it up to change channels), and ends up on the living room floor by 22:00 (dropped after use). The blanket is on the couch throughout the evening but briefly appears on the coffee table at 16:00 (afternoon) and 22:00 (after TV ends, tossed aside). The snack bowl is at the coffee table during the TV window (21–23) and in the kitchen (sink or cupboard) before and after.

What sets this apart: p_a1b2 claims the blanket is on the couch 20–22.5 (which the data partially supports but the 22:00 coffee_table sighting contradicts). p_7e3a claims the remote is on the floor 21–23 (but the data shows it at the coffee table at 21 and only at the floor at 22). My document captures the progression: remote at coffee_table at 21, then floor at 22; blanket at couch 18–21, then coffee_table at 22.

What would refute it: finding the remote on the TV stand at 21:30 (never picked up), finding the blanket on the couch at 22:30 (never tossed), or finding the snack bowl in the kitchen at 21:30 (not brought out for TV).

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table during the active TV window",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22
  },
  {
   "claim": "The blanket is on the couch during the pre-TV evening",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 18,
   "to": 21
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
   "claim": "The remote is on the living room floor after TV ends",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 22,
   "to": 23
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 16,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 16,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
