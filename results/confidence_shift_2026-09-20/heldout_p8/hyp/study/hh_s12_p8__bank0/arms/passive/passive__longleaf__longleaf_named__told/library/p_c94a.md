# p_c94a — Dog feeding flux: food bag in motion at dawn, pantry by afternoon

The dog food bag is the one kitchen item that moves through the morning. At 00:00 and 08:00 it is found in three places — pantry shelf, kitchen table, and kitchen floor — reflecting the feeding routine: Priya (or Elena, on weekends) pulls it from the pantry, opens it at the table or on the floor to pour into the bowl, and sets it back. By 16:00 it is back in the pantry on both sightings. The dog bowl, by contrast, is a fixed fixture on the kitchen floor (4/4 days, found 2/2 weekday 9–17 h looks). The dog toy is a fixed fixture on the living room floor. This document addresses the mixture's worst prediction on dog_food_bag_shared (pantry predicted, floor found at 00:00) by modelling the morning flux explicitly. It also anchors the dog bowl and toy as stable, which the current library under-specifies.

What would refute it: if the dog food bag is found at the kitchen table or floor during the 12–16 h window (meaning it is not back in the pantry by midday), or if the dog bowl is ever off the kitchen floor during the day.

```json
{
 "claims": [
  {
   "claim": "The dog food bag is back in the pantry on a weekday afternoon",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "The dog bowl is on the kitchen floor at midday",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 12,
   "to": 16
  },
  {
   "claim": "The dog toy is on the living room floor in the afternoon",
   "target": "dog_toy_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 13,
   "to": 16
  },
  {
   "claim": "The dog leash hangs at the entry hook on a weekday morning",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
