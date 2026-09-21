# p_c4e8 — Weekend TV: Remote and Blanket Migrate to the Seating Area

On weekdays the remote stays at tv_stand_l1 through the evening and the blanket rests on couch_l1 until the 21:00 coffee-table shift. On weekends the pattern is different: the remote moves to coffee_table_l1 for the 20:00-to-22:00 TV window (seen there 4 times at 20:00, once at 21:00), and the blanket shifts to armchair_l1 for the long evening stretch (seen at 18:00, 20:00, 21:00, and 23:00 on the weekend). The snack bowl also appears on the coffee table at 21:00 on the weekend. This document captures that the weekend TV session is a more relaxed, spread-out affair: the remote is within reach on the coffee table, the blanket is draped over the armchair where someone sits for hours, and the snack bowl is brought over for grazing.

What sets this apart from p_c9d4 (which keeps the remote at the couch) and p_9d4e (which puts the blanket on the coffee table): on weekends the remote is on the coffee table, not the couch or TV stand, and the blanket is on the armchair, not the couch or coffee table. If the robot sees the remote at tv_stand_l1 during the weekend 20-22h window, or the blanket on couch_l1 at 22:00 weekend, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table during the weekend evening TV session",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20,
   "to": 21
  },
  {
   "claim": "The blanket is on the armchair during the weekend evening",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table during the weekend late-evening TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 22
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
    "days": "weekend",
    "from": 20,
    "to": 22,
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
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
