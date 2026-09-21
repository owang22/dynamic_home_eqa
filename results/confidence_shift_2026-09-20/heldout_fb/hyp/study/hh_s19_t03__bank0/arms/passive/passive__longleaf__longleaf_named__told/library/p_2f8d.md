# p_2f8d — The evening: counter snacks, couch guitar, TV-stand remote, no coffee-table clutter

The remote is at the TV stand on all six sighted days with zero variation — it never migrates to the coffee table. The snack bowl is on the kitchen counter during the evening (18:00: counter x2; 20:00: counter x3), not on the coffee table. The guitar rests in the bedroom (bedroom_floor_b1) through the day and moves to the couch at 21:00 for Marco's evening playing session. The blanket is on the couch all day (6/6 days, 19 sightings) with a single 10:00 coffee-table exception. The knitting bag is on the couch all day (6/6 days). The candle is on the coffee table (6/6 days) and stays there.

This document is refuted if the remote is on the coffee table during the 20:00–22:00 TV window, if the snack bowl is on the coffee table at 20:00, or if the guitar is still in the bedroom at 21:00.

```json
{
 "claims": [
  {
   "claim": "The remote is on the TV stand at 21:00 during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20.75,
   "to": 21.25
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 20:00 during the evening, not on the coffee table",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19.75,
   "to": 20.25
  },
  {
   "claim": "The guitar is on the couch at 21:30 during Marco's evening playing session",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "both",
   "from": 21,
   "to": 22
  },
  {
   "claim": "The blanket is on the couch at 14:00 in its resting spot",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 13.75,
   "to": 14.25
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
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 22,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
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
  "knitting_bag_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "candle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
