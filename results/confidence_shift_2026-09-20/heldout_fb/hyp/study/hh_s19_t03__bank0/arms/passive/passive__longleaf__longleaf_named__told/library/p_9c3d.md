# p_9c3d — The evening counter: kitchen is the snack station, remote stays at the TV

The evening routine keeps the snack bowl on the kitchen counter, not the coffee table. At 18:00 the snack bowl is already on the counter (dinner prep or first snack), and it stays there through the evening — confirmed at both 18:00 and 20:00. The remote never leaves the TV stand: it is there at 03:00, during the day, and during evening TV. No document in the library should place the remote at the coffee table. The pan is in the cupboard until about 18:30, moves to the counter for cooking (confirmed at 19:00), and returns to the cupboard by 20:00.

This document corrects the persistent error in p_789a, p_f4a7, and p_b2e9 of placing the snack bowl and remote at the coffee table during TV time. The snack bowl has 9 sightings on 2 of 3 days, all at counter_k1 or cupboard_k1 — never at the coffee table. The remote has 3 sightings on 3 of 3 days, all at tv_stand_l1 — never at the coffee table.

What would refute this: finding the snack bowl at the coffee table during 18:00–22:00, or the remote anywhere other than the TV stand during an evening TV window.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the kitchen counter during the evening",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The remote is on the TV stand during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The pan is on the counter while cooking is in progress",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19,
   "to": 19.5
  },
  {
   "claim": "The pan is still in the cupboard at 18:00 before cooking starts",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 18,
   "to": 18.5
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 17,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 23,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
