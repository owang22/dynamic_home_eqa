# p_c6d9 — Evening Migration: Kitchen to Coffee Table by 21

The clock-hour data reveals a clear evening choreography. At 18:00, kitchen items are in the sink (post-lunch wash) or on the counter (pre-dinner). By 19:00, plates and glasses are at the kitchen table for dinner. Then, between 19:00 and 21:00, the residents move to the living room and bring their drinks and snacks with them: mug_hana appears at coffee_table_l1 at 20:00, mug_priya and glass_priya arrive by 21:00–23:00, and the snack bowl shifts from counter to coffee table by 21:00. The blanket is already on the couch (5/5 sightings). This document places the coffee-table gathering at 21:00 rather than 20:00, correcting p_c9d4's 20–23h window which has taken three against-counts (the snack bowl is still at the counter at 20:00).

What sets this apart: the precise 21:00 arrival time for the coffee-table cluster, and the prediction that the kitchen table is clear by 21:00 (dinner done, dishes started). If the snack bowl or mugs are sighted on the coffee table at 19:00, or if the kitchen table still has plates at 21:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's mug is on the coffee table at 21:00 on a weekday (evening TV session underway)",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The snack bowl is still on the kitchen counter at 20:00 on a weekday (dinner just finished, not yet moved)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Priya's mug is in the kitchen sink at 18:00 on a weekday (washed after afternoon tea)",
   "target": "mug_priya",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The blanket is on the couch at 21:00 on a weekday (TV time)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 20,
   "to": 23
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
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
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
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
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
