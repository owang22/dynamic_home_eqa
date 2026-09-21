# p_6f7a — The shopping bag is a pantry staple; it only leaves for grocery runs

The shopping_bag_shared lives in the pantry shelf permanently. It is only taken OUT_OF_HOUSE on grocery shopping days, roughly once a week (Saturday or Sunday midday, 11:00–14:00). On all other days it is in the pantry. What sets this hypothesis apart: the shopping bag is in the pantry 6 days a week. What would refute it: shopping_bag_shared sighted OUT_OF_HOUSE on a Tuesday or Wednesday.

```json
{
 "claims": [
  {
   "claim": "The shopping bag is in the pantry on a Wednesday",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The shopping bag is in the pantry on a Thursday",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The shopping bag may be out of the house on Saturday midday for groceries",
   "target": "shopping_bag_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The kettle is always on the kitchen counter",
   "target": "kettle_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "kettle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "toaster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "knife_block_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
