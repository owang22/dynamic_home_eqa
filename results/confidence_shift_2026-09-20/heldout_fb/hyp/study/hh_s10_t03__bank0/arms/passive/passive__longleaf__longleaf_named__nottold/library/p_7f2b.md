# p_7f2b — Glass_yuki's evening migration: counter to dining table to nightstand, 18:00 to 23:00

Yuki's glass follows a precise three-stop evening path on weekdays. At 18:00 it is on the kitchen counter (1/1) — just taken out of the cupboard as she arrives home and starts dinner prep. By 19:00 it is at the dining table (2/2) — dinner is in progress. At 20:00 it is still at the dining table (3/3) — she is finishing or lingering. By 22:00 it has migrated to the bedroom nightstand (3/3) — she has carried it upstairs for her bedtime water. At 23:00 it is at the nightstand (3/3) or in the cupboard (2/3, possibly washed and put back). Overnight (03:00) it is in the kitchen sink (3/4) or on the dish rack (1/4) — dirty from the night's use.

On weekends the pattern is different: at 13:00 it is in the cupboard (1/1), at 19:00 at the kitchen table (1/1, weekend meal), at 20:00 in the sink (1/1, washed early), at 22:00 at the nightstand (2/2), and at 23:00 at the coffee table (1/1, a late-night drink in the living room).

This document is distinguished by the specific three-stop weekday path (counter → dining table → nightstand) with the 18:00 counter stop that no other document tracks. It differs from p_b8e4 (which tracks the glass as part of Yuki's broader evening arc) by focusing exclusively on the glass and adding the 23:00 and 03:00 endpoints.

What would refute it: the glass at the cupboard at 19:00 on a weekday, or the glass at the dining table at 22:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's glass is on the kitchen counter at 18:00 on a weekday (just taken out for dinner)",
   "target": "glass_yuki",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Yuki's glass is at the dining table at 19:30 on a weekday (dinner in progress)",
   "target": "glass_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Yuki's glass is at the bedroom nightstand at 22:30 on a weekday (carried upstairs for the night)",
   "target": "glass_yuki",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 23
  },
  {
   "claim": "Yuki's glass is in the kitchen sink at 03:00 on a weekday (dirty overnight)",
   "target": "glass_yuki",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 2,
   "to": 6
  }
 ],
 "targets": {
  "glass_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
