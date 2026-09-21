# p_6f4b — Shopping Bag Evening Residual: Still on the Counter at 19–20

The shopping bag does not go fully back to the pantry shelf at 18:00 on weekdays. After Priya unpacks at 12:00–13:00 (counter ×5, ×3) and the bag is briefly in the pantry at 18:00 (×1), it reappears on the counter at 19:00 (×1) and 20:00 (×1). This suggests either a second small unpacking (Hana brings something home from work) or the bag was never fully put away and is just sitting on the counter through the evening. By 03:00 it is back in the pantry shelf (×3). On weekends the bag shows a similar midday counter appearance (12:00 ×1) but no evening residual.

What sets this apart: p_6c1f says the bag goes back to the pantry by 18:00, but the 19:00 and 20:00 counter sightings contradict a clean 18:00 reset. p_4e1b (retired) captured the bag but also misplaced glass_priya. This document isolates the evening residual as a distinct prediction.

What would refute it: if the bag is in the pantry shelf at 19:00 and 20:00 on multiple weekday evenings, the residual is an anomaly, not a pattern.

```json
{
 "claims": [
  {
   "claim": "The shopping bag is on the kitchen counter at 19:00 on a weekday because it was not fully put away",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The shopping bag is on the kitchen counter at 12:00 on a weekday because Priya just returned from errands",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 12,
   "to": 13
  },
  {
   "claim": "The shopping bag is in the pantry shelf at 03:00 on a weekday (overnight resting place)",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 3,
   "to": 7
  }
 ],
 "targets": {
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 13,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
