# p_5c4d — Evening Service: Cupboard to Kitchen Table to Coffee Table

The serving dish follows a clear evening path visible in the patrol passes: it rests in the cupboard through the day, appears on the kitchen table at 20:00 (just after dinner plates are cleared), and then travels to the coffee table for the 21:00–23:30 TV period. The snack bowl follows a similar but later path: cupboard through the evening, counter at 22:00 (being filled), coffee table at 23:00. This is distinct from p_f6d2, which uses wider windows (21–23.5 h for the serving dish, 22–24 h for the snack bowl) and accumulates mixed for/against votes. The tighter, sequenced windows here match the actual transition times seen in the passes. It would be refuted if the serving dish is found in the cupboard at 21:00 or the snack bowl is found in the cupboard at 23:00.

```json
{
 "claims": [
  {
   "claim": "The serving dish is on the coffee table during the evening TV period",
   "target": "serving_dish_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The serving dish is on the kitchen table just after dinner before moving to the living room",
   "target": "serving_dish_shared",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 20,
   "to": 21
  },
  {
   "claim": "The snack bowl is on the kitchen counter being filled for evening snacks",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the coffee table during late-evening TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 23,
   "to": 24
  }
 ],
 "targets": {
  "serving_dish_shared": [
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
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
