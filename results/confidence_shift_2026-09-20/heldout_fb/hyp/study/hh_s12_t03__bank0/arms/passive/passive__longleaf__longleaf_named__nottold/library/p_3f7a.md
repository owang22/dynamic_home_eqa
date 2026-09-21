# p_3f7a — Evening living room: remote on the coffee table, glasses set down, blanket pulled close

Elena and Priya share the living room for the evening wind-down. After dinner is cleared (roughly 19:00–19:30), both settle into the couch and armchair. Priya takes off her reading glasses and sets them on the coffee table beside the remote; she does not keep them on her face while watching TV. The remote lives on the coffee table for the whole TV window (19:00–23:00), not on the TV stand—the TV stand is only where it rests overnight. The blanket is pulled from the couch onto the coffee table or draped over the armchair once it gets past 20:00. Priya's mug ends up on the coffee table for her evening tea. Elena's water bottle stays at the dining table through dinner and is only picked up when she moves to the couch.

What sets this apart: p_9d4e places the remote on the tv_stand at 18–19 h; the sightings show it on the coffee table from 20:00 onward (22:00 × 4, 23:00 × 1). p_a1b2 and p_4c7d put Priya's glasses ON_PERSON 7–22 h, which failed (0.14 on 3 sightings); the glasses are actually set on the coffee table from about 15:00 through 23:00. This document pins the remote, glasses, blanket, and mug to the coffee table as a cluster during the TV window.

Refutation: if the remote is found on the tv_stand during 20:00–23:00 on multiple evenings, or if Priya's glasses are sighted ON_PERSON or on the nightstand during the 15:00–22:00 window on more than one day, the core cluster claim falls.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table at 21:00 on a weekday evening",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 21.5
  },
  {
   "claim": "Priya's glasses are set on the coffee table at 21:00, not worn",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 20.5,
   "to": 21.5
  },
  {
   "claim": "The blanket is on the coffee table at 22:00 during late TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21.5,
   "to": 22.5
  },
  {
   "claim": "Priya's mug is on the coffee table at 20:30 during evening TV",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
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
    "from": 19,
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
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
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
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
