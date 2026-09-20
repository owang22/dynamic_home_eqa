# p_7fc7 — Weekend Errands: Both out 11 to 14, shopping bag returns

On weekends both residents leave the house together for errands from about 11:00 to 14:00. They are out, so no resident is listed in any room. The shopping bag (if they bought anything) reappears at pantry_shelf_k1 or entry_table_e1 by 15:00. The dog is home (with a neighbor or in the house). On weekdays, only Nora is out (8:00–17:30); Yuki stays.

What sets this hypothesis apart: on Saturday and Sunday between 11:00 and 14:00, NO resident is in any room (the house is empty of people). The shopping bag appears at the pantry or entry after 14:00. This is a joint absence pattern.

What would refute it: a resident sighted in any room at 12:00 on a Saturday, or the shopping bag never seen after 14:00 on weekends.

```json
{
 "claims": [
  {
   "claim": "The shopping bag is at the pantry shelf on Saturday afternoon after errands",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The shopping bag is at the pantry shelf on Sunday afternoon after errands",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The dog bowl is on the kitchen floor at midday on weekends (dog is home)",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "weekend",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The dog food bag is at the pantry on weekends",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 11,
   "to": 14
  }
 ],
 "targets": {
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
