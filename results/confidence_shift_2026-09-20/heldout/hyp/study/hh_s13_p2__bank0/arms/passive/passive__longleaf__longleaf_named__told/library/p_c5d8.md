# p_c5d8 — Weekend Cleaning and Kitchen Afternoon: Vacuum Out, Groceries Sorted, Long Meal

The residents said on Saturday and Sunday that they are "off our usual routine and around the house more." The data confirms this: the vacuum cleaner is out on the living room floor (floor_l_l1) for the entire weekend day, every hour from 00:00 to 22:00, both days. It is not in storage. The house is being cleaned, or at least the vacuum is deployed and left out.

In the kitchen, the shopping bags move from the pantry shelf (where they rest overnight, 00:00–10:00) to the kitchen table (12:00–22:00), indicating that groceries are unpacked and sorted at the table in the afternoon. Priya's plate is at the cupboard in the morning, moves to the kitchen table from 14:00 to 20:00 (a long afternoon meal or series of snacks), and returns to the cupboard at 22:00. Her glass follows: sink in the morning, kitchen table at 20:00, coffee table at 22:00. Hana's plate is at the cupboard until 14:00, in the sink at 16:00–18:00 (washed from a midday meal), and at the kitchen table at 20:00 (dinner).

This document is set apart from p_9b6e (which puts plates at the kitchen table 10–13h for brunch — the data shows the table clear until 14:00) and from the plain statistical model (which puts the vacuum at storage_floor_s1 and the shopping bag at pantry_shelf_k1). The weekend is a cleaning-and-sorting day, not a brunch day.

This document is refuted if a weekend look at 10:00–14:00 finds the vacuum at storage_floor_s1, the shopping bag at pantry_shelf_k1 after 12:00, or Priya's plate at the kitchen table before 13:00.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 10 AM on a Saturday because the house is being cleaned on weekends",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The shopping bag is on the kitchen table at 2 PM on a Saturday because groceries are being sorted",
   "target": "shopping_bag_shared",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Priya's plate is on the kitchen table at 4 PM on a Saturday because the afternoon meal is in progress",
   "target": "plate_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 6 PM on a Saturday, still out from cleaning",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 17,
   "to": 20
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "plate_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
