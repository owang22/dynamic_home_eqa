# p_3f6a — Weekend dog routine: bag stays on the pantry shelf, bowl on the floor, brief floor visits for feeding

This document captures the weekend dog-feeding pattern, which is noticeably different from the weekday two-feeding cycle. On weekends, Yuki is home all day and the dog's feeding is less rigid. The food bag stays on the pantry_shelf_k1 for the vast majority of the weekend day, with only brief forays to the kitchen floor for the actual pour (roughly 07:00–09:00 in the morning and 19:00–22:00 in the evening). The dog bowl, by contrast, is a permanent fixture on the kitchen floor: it is at floor_k_k1 on all six sighted weekend days, at every hour from 03:00 through 23:00.

The weekend 03:00 patrol shows the bag at pantry_shelf_k1 (two sightings) and the bowl at floor_k_k1 (one) or kitchen_table_k1 (one). The 08:00 pass shows the bag at floor_k_k1 (two) or pantry_shelf_k1 (one), confirming the brief floor visit for morning feeding. By 11:00 and 14:00 the bag is back on the pantry shelf (one and two sightings respectively). The 20:00 pass shows the bag at pantry_shelf_k1 (two) or floor_k_k1 (one), with the floor sighting consistent with the evening feeding.

The dog leash on weekends follows the p_f3a9 pattern: entry_hook_e1 or entry_table_e1 overnight, ON_PERSON during the late-morning walk (10:00–11:00), back at the entry afterward. The 03:00 weekend sightings show the leash at entry_hook_e1 (one) or entry_table_e1 (one).

What sets this apart from p_f3a9 and p_3e7a: on weekends the food bag is at pantry_shelf_k1 at 14:00 (not on the floor), and the bowl is at floor_k_k1 at 13:00 (not the kitchen table). The weekend feeding is a quick pour-and-return, not a prolonged floor presence.

What would refute it: the dog food bag on the kitchen floor at 14:00 on a weekend (it should be on the pantry shelf); the dog bowl on the kitchen table at 13:00 on a weekend (it should be on the floor).

```json
{
 "claims": [
  {
   "claim": "The dog food bag is on the pantry shelf at 14:00 on a weekend, not on the kitchen floor",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 13,
   "to": 15
  },
  {
   "claim": "The dog bowl is on the kitchen floor at 13:00 on a weekend",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "weekend",
   "from": 12,
   "to": 14
  },
  {
   "claim": "The dog leash is on Yuki's person during her weekend late-morning walk",
   "target": "dog_leash_shared",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 10,
   "to": 11
  },
  {
   "claim": "The dog food bag is on the pantry shelf at 07:00 on a weekend, before the morning feeding",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 6.5,
   "to": 7.5
  }
 ],
 "targets": {
  "dog_food_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "ON_PERSON",
    "chance": "almost_always"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ],
  "jacket_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ]
 }
}
```
