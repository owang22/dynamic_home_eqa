# p_1d5f — Priya's 8 AM Kitchen Table

On weekdays Priya has her morning tea or coffee at the kitchen table. Her bowl and mug are both at the kitchen_table_k1 at the 08:00 patrol, seen three times each across the weekday passes. By the 16:00 patrol the bowl is back at the sink (x3) and the mug is at the sink (x2) or the pantry shelf (x1). The resting place for both objects is the cupboard_k1, confirmed at 00:00 and 08:00 on weekends when the kitchen table is not in use. This is a weekday-morning-only window: the kitchen table is the active spot from roughly 07:00 to 09:00, then the objects return to their resting places.

This document differs from p_a9b4, which places mugs and glasses at the kitchen table throughout the day, and from p_2e8c, which focuses on Saturday brunch at the kitchen table. The distinguishing feature is the tight 07:00–09:00 weekday window for both bowl_priya and mug_priya together, followed by a return to the sink by mid-afternoon. On weekends the pattern shifts: the bowl and mug are at the cupboard or dish rack, not the kitchen table.

This hypothesis is refuted if the bowl or mug is found at the sink, cupboard, or counter at 08:00 on a weekday, or if they are at the kitchen table at 16:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Priya's bowl is at the kitchen table at 8:00 on a weekday for her morning tea",
   "target": "bowl_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Priya's mug is at the kitchen table at 8:00 on a weekday for her morning tea",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Priya's bowl is back at the sink by 16:00 on a weekday",
   "target": "bowl_priya",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 15,
   "to": 18
  },
  {
   "claim": "Priya's mug is at the sink by 16:00 on a weekday",
   "target": "mug_priya",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 15,
   "to": 18
  }
 ],
 "targets": {
  "bowl_priya": [
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
    "from": 15,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
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
    "from": 15,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
