# p_5e8b — Snack bowl reaches the coffee table only after 22:00, not at the start of TV

The snack bowl spends the day and early evening in the kitchen: the sink, the counter, or the cupboard. It is not at the coffee table when TV starts at 20:00–21:00. At 21:00 on weekdays the sightings are scattered across four receptacles (kitchen_table ×1, cupboard ×1, coffee_table ×1, counter ×1), suggesting the bowl is being carried around but has not yet settled. By 23:00 on weekdays it is at the coffee table (×2), and on weekends at 22:00 (×1). This document corrects the 20:00–22:00 or 21:00–23:00 coffee-table windows in p_a3f7 (couch: against 3), p_7d4e (kitchen table: against 6), and p_4f8a (coffee table 21–23 h: against 2, for 1), all of which place the bowl at the coffee table too early.

The snack bowl's overnight resting spot is the kitchen sink (03:00 sink ×2) or the counter (03:00 counter ×1). During work hours the robot checked the cupboard three times and found the bowl none of them, so it is not in the cupboard during 9–17 h; it is more likely in the sink or on the counter. In the early evening (18:00) it appears in the cupboard (×1), and by 22:00–23:00 it has migrated to the coffee table for late-night snacking.

This document would be refuted if the snack bowl is consistently found on the couch or the kitchen table during 20:00–22:00, or if it is at the coffee table before 22:00 on multiple occasions.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the coffee table at 23:00 on weekdays",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22.5,
   "to": 24
  },
  {
   "claim": "The snack bowl is in the kitchen at 21:00 on weekdays, not yet at the coffee table",
   "target": "snack_bowl_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table at 22:30 on weekends",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 22,
   "to": 24
  },
  {
   "claim": "The snack bowl is in the kitchen at 21:00 on weekends, not yet at the coffee table",
   "target": "snack_bowl_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
