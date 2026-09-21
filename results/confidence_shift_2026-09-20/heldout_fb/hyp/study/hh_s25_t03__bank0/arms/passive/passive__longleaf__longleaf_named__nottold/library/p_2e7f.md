# p_2e7f — Evening TV: the coffee table is the centre; the remote ends up on the floor

The household's evening TV ritual (roughly 20:00–22:30) is anchored at the coffee table, not the couch or the TV stand. The blanket starts draped over the couch but gets pulled onto the coffee table as the residents settle in; by 22:00 it is at coffee_table_l1. The remote is picked up from the TV stand and used at the coffee table (21:00 sighting), then dropped on the living-room floor by 22:00. The snack bowl comes out of the cupboard or is still in the sink at 21:00 but is at the coffee table by 22:00. This document corrects p_a1b2's blanket-on-couch claim (which has taken 2 against hits) and the remote-on-TV-stand assumption. What sets this apart: the blanket, remote, and snack bowl are all at coffee_table_l1 during the 21–22 h window, and the remote migrates to floor_l_l1 after 22:00. What would refute it: the blanket sighted at couch_l1 at 22:00, or the remote at tv_stand_l1 after 21:00.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the coffee table during the later part of evening TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "The remote is on the coffee table during active TV watching",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "The remote is on the living-room floor after TV winds down",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 22,
   "to": 23.5
  },
  {
   "claim": "The snack bowl is on the coffee table during evening TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "class:blanket": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21.5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:remote": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "class:snack_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
