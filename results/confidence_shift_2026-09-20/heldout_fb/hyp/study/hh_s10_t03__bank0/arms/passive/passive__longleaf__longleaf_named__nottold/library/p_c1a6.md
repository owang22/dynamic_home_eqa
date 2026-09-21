# p_c1a6 — Snack bowl: sink overnight, counter by day, coffee table for evening TV

The shared snack bowl follows a predictable daily cycle tied to the household's TV-watching habit. Overnight (03:00: sink 2×, counter 1×, armchair 1× on weekdays; sink 1×, kitchen_table 1× on weekends) it sits in the kitchen sink, dirty from the previous evening's TV session. By the late morning it has been washed and is resting on the kitchen counter (17:00: counter 1×; 18:00: counter 2× on weekdays). The bowl stays on the counter through the afternoon. The key event is the evening TV window: at 21:00–23:00 on weekdays the bowl appears at the coffee table (22:00: coffee_table 2×, cupboard 3×; 23:00: coffee_table 2×, counter 3×) or is briefly tucked into the cupboard between uses. On weekends the TV window shifts slightly later: 21:00 coffee_table 3×; 22:00 couch 2×, coffee_table 2×.

This document is distinguished by the sink-overnight resting spot and the 21:00–23:00 coffee-table window. It would be refuted if the bowl were consistently at the cupboard or counter during the 21:00–23:00 window, or if it were found at the coffee table during the daytime.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is in the kitchen sink at 04:00 on a weekday (dirty from previous night's TV)",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 3,
   "to": 5
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 14:00 on a weekday (clean, resting, not yet in use)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "The snack bowl is at the coffee table at 21:30 on a weekend (evening TV in progress)",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 22
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 6,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
