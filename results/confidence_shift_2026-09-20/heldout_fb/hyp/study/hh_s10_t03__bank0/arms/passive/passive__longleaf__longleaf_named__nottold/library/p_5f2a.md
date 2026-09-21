# p_5f2a — Omar's weekday kitchen-table breakfast, 10:00 to 12:00

Omar is home in the morning before his 1:40 shift. His breakfast routine centers on the kitchen table: by 10:00 his bowl, mug, and vitamins are all there (bowl 1/1, mug 2/2, vitamins 2/2 at the 10:00 pass). His tablet is also at the kitchen table at 10:00 (2/2 passes), having moved from the nightstand (where it sleeps overnight) sometime between 09:00 and 10:00. His bathroom routine (razor at the sink, glasses at the nightstand or bathroom shelf) happens earlier, around 08:00–09:00. By 12:00 the food items are cleared and the tablet moves toward the kitchen chair where it waits for his return at 23:00.

This document differs from p_3e8d, which claims the tablet is at the kitchen table from 09:00 (the 09:00 pass shows it at the nightstand on 2 of 3 occasions). It differs from p_c007, which places the vitamins at the kitchen table at 07:15 (no support; the 09:00 pass shows them at the kitchen table for the first time). The breakfast window here is 10:00–12:00, not 09:00–13:00.

Refutation: the bowl, mug, or vitamins NOT at the kitchen table at the 10:00 pass, or the tablet at the nightstand at 10:00.

```json
{
 "claims": [
  {
   "claim": "Omar's bowl is at the kitchen table at 10:30 on a weekday (breakfast in progress)",
   "target": "bowl_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Omar's mug is at the kitchen table at 10:30 on a weekday (breakfast in progress)",
   "target": "mug_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Omar's vitamins are at the kitchen table at 10:00 on a weekday (morning dose with breakfast)",
   "target": "vitamins_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9.5,
   "to": 11
  },
  {
   "claim": "Omar's tablet is at the kitchen table at 10:30 on a weekday (morning browsing before work)",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 10,
   "to": 11
  }
 ],
 "targets": {
  "bowl_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "vitamins_omar": [
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 24,
    "at": "chair_k1",
    "chance": "usually"
   }
  ],
  "razor_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
