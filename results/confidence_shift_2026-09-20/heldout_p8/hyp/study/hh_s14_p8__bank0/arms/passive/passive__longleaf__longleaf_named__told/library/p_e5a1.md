# p_e5a1 — Weekend kitchen: snack bowl on the counter, baking at the table

On weekends the household is "around the house more" (the residents' own Saturday and Sunday messages) and the kitchen takes on a social and baking role. The snack bowl, which sits in the cupboard on weekdays (3/3 at cupboard at the 16:00 pass), is found on the kitchen counter at all three weekend passes (00:00, 08:00, 16:00) — it is set out for grazing. The baking tray, normally at the pantry shelf, appears at the kitchen table in one sighting per weekday pass (baking in progress) but stays at the pantry on weekends. The cutting board shifts to the kitchen table on weekend mornings (00:00, 08:00) before returning to the counter by 16:00. This document is refuted if the snack bowl is found in the cupboard on a weekend afternoon, or if the cutting board is on the kitchen table at 16:00 on a weekend.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the kitchen counter on a weekend afternoon",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "The snack bowl is in the cupboard on a weekday afternoon",
   "target": "snack_bowl_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The cutting board is on the kitchen table during weekend morning baking",
   "target": "cutting_board_shared",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
