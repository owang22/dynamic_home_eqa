# p_5d9e — Blanket to Coffee Table by 21

The blanket sits on the couch from 03:00 through 18:00 every weekday (sightings at 03, 08, 09, 11, 15, 18 all confirm couch_l1). Then, between 18:00 and 21:00, it migrates to the coffee table, where it is found at 21:00 (x2) and 22:00 (x1). This is the TV-session migration: when the evening TV starts, the blanket is pulled off the couch and draped over the coffee table (or the residents shift to a more casual arrangement). This directly contradicts p_c9d4's claim that the blanket is on the couch at 22:00, which has already scored against 1.

What sets this apart: p_c9d4 and p_3a7f both place the blanket on the couch at 21:00–23:00. This document places it on the coffee table. The couch is its resting spot all day; the coffee table is its evening spot.

What would refute it: if the blanket is found on the couch at 21:00 or 22:00 on multiple weekday evenings, or if it is found on the coffee table before 20:00.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch at 18:00 on a weekday (resting all day)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The blanket is on the coffee table at 21:00 on a weekday (TV session started)",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "The blanket is on the coffee table at 22:00 on a weekday (still in TV use)",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
