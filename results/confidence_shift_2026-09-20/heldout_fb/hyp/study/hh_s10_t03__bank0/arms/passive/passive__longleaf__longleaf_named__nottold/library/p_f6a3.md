# p_f6a3 — Mug_yuki's daily cycle: sink overnight, kitchen table for breakfast, coffee table for TV

Yuki's mug follows a clear daily arc that no existing document captures in full. Overnight (03:00) it is in the kitchen sink (2/2 weekday passes, 2/2 weekend) — dirty from the previous evening's use, waiting to be washed. By 07:00 on weekdays it is at the kitchen table (1/1) or still in the sink (1/1) — she is having breakfast. By 18:00 it is back in the cupboard (1/1) — washed and put away after breakfast. The critical evening window: at 21:00 it is at the coffee table (3/3) or the bedroom desk (3/3) — she has brought it to the living room for her evening TV. At 22:00 it is at the coffee table (2/2), and at 23:00 still there (1/1). On weekends the pattern shifts: at 09:00 it is at the kitchen table (2/2, weekend breakfast), and at 20:00 it is in the cupboard (1/1, not yet out for TV).

This document sets itself apart from p_8f2a (retired, "mug_yuki's daily arc: sink overnight, cupboard by day, coffee table for TV") by adding the 21:00 bedroom-desk sighting and the specific weekend morning pattern. It differs from p_c007, which puts mugs at the dining table 18–20h (Yuki's mug is not at the dining table for dinner; it is at the coffee table for TV).

What would refute it: the mug at the dining table at 19:00 on a weekday, or the mug at the coffee table at 03:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's mug is in the kitchen sink at 03:00 on a weekday (dirty overnight, not yet washed)",
   "target": "mug_yuki",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Yuki's mug is at the coffee table at 21:30 on a weekday (brought to the living room for TV)",
   "target": "mug_yuki",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "Yuki's mug is at the kitchen table at 09:00 on a weekend (weekend breakfast)",
   "target": "mug_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 8.5,
   "to": 10
  }
 ],
 "targets": {
  "mug_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
