# p_b4e7 — — Snack Bowl: Kitchen Through 20, Coffee Table 21–23 (fork of p_3a7f)

This is a fork of p_3a7f (Evening Migration Confirmed). The parent places the snack bowl on the kitchen counter at 19:00 and on the coffee table during the evening. The evidence refines the timing: the snack bowl is on counter_k1 at 18:00 (1×) and 19:00 (3×), then on coffee_table_l1 at 21:00 (2×). At 03:00 it is in sink_k1 (2×).

The critical correction: the snack bowl is NOT on the coffee table at 20:00. It stays in the kitchen through the 19:00–20:00 dinner window and only migrates to the living room at 21:00, when TV starts. The parent's claim "snack bowl on kitchen counter at 19:00" is supported (4 for, 13 against in the parent's tally — the against count is from the broader 18–20 window where some looks at 18:00 caught it in the sink). This fork tightens the counter window to 18–20 and the coffee table window to 21–23.

What changed from the parent: the snack bowl's coffee table window is now 21–23 (not 20–23), and a sink block is added for 0–6 (washed overnight). The mug_hana and blanket blocks are retained from the parent.

What sets this apart from p_c9d4 (Late Night): p_c9d4 puts the snack bowl on the coffee table from 20:00. This document says 21:00. The 19:00 sightings (3× counter) and the absence of a 20:00 coffee table sighting are the distinguishing evidence.

_(targets the fork left unstated are inherited from p_3a7f)_

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the kitchen counter at 19:00 on a weekday (dinner in progress, not yet moved)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The snack bowl is on the coffee table at 21:00 on a weekday (TV session started)",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The snack bowl is in the kitchen sink at 03:00 on a weekday (washed after the evening)",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "both",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Hana's mug is on the coffee table at 21:00 on a weekday (evening TV session)",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "days": "both",
    "from": 6,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
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
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
