# p_8f2a — Priya's 12:00 Grocery: the Bag Dominates the Counter

Priya leaves the house around 10:30 for a midday grocery run and returns by 12:00. The shopping bag then sits on the kitchen counter while she unpacks, visible at the 12:00 patrol (×5) and the 13:00 patrol (×3)—a total of 8 sightings on the counter, far more than any other object at any other time. By 18:00 the bag is stored on the pantry shelf. Priya's keys and jacket are out of the house during the 10:30–12:00 window; they reappear at the entry table by 13:00.

This document is distinguished by the *magnitude* of the counter presence: no other hypothesis explains 8 consecutive sightings of the shopping bag on counter_k1 in a two-hour span. If the bag is found in the pantry or on the floor at 12:00 on multiple days, this is wrong. If Priya's keys are sighted at the entry table at 11:00, the out-of-house claim fails.

```json
{
 "claims": [
  {
   "claim": "The shopping bag is on the kitchen counter at 12:00 on a weekday (Priya unpacking groceries)",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  },
  {
   "claim": "Priya's keys are out of the house at 11:00 on a weekday (she is at the store)",
   "target": "keys_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 10.5,
   "to": 12
  },
  {
   "claim": "The shopping bag is in the pantry shelf at 18:00 on a weekday (stored after unpacking)",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Priya's jacket is out of the house at 11:00 on a weekday (she is at the store)",
   "target": "jacket_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 10.5,
   "to": 12
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
    "from": 11.5,
    "to": 13.5,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ]
 }
}
```
