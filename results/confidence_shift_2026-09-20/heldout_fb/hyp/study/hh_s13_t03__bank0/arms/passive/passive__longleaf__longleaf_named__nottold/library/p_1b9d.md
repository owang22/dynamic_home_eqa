# p_1b9d — Priya's Midday Grocery: the shopping bag dominates the counter at noon

Priya goes to the grocery store around 10:30–11:00 on weekdays and returns around 12:00–12:30. She brings the shopping bag to the kitchen counter to unpack groceries, and the bag sits on counter_k1 from about 11:30 to 13:00. By 18:00 the bag is back in the pantry shelf (stored or reused). The evidence is strong: 5 sightings of the shopping bag at counter_k1 at 12:00, 3 more at 13:00, and 2 at pantry_shelf_k1 at 03:00. Priya's keys and jacket are out of the house during the trip (10:30–12:00).

What sets this apart: at 12:00 on a weekday, shopping_bag_shared is at counter_k1 (not pantry_shelf_k1). Priya's keys are OUT_OF_HOUSE at 11:00. In the standard hypothesis Priya's errands are 14:00–16:00, so the bag would not be at the counter at noon. What would refute it: shopping_bag_shared at pantry_shelf_k1 at 12:00 on a weekday, or keys_priya at entry_table_e1 at 11:00 on a weekday.

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
    "to": 13,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
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
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
