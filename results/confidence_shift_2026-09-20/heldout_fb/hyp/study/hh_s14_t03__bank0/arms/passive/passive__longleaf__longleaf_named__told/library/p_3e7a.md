# p_3e7a — Weekend Dog: Late-Morning Walk, Feeding on the Floor

On weekends Yuki's walk with the dog shifts to the late morning (10:00–11:00) rather than the early morning (07:00–08:00) she does on weekdays. The dog's feeding still happens in the morning, but the food bag stays on the kitchen floor during the feeding pour and is then stored on the pantry shelf for the rest of the day. The dog bowl is always on the kitchen floor. The leash rests on the entry hook overnight and in the early morning, goes on Yuki's person during the 10–11 walk, and returns to the hook afterward. An evening feeding may bring the food bag back to the floor briefly.

What sets this apart from p_f3a9 (weekday dog walk at 7–8): the walk window is 10–11, and the food bag's floor window is 6:30–9:00 (feeding) rather than 7:00–8:00. The leash is on the hook from 0–10 (longer morning period) rather than 0–7.

This is refuted if the leash is on Yuki's person before 09:00 on a weekend (early walk, contradicting the late-morning pattern), or if the dog food bag is on the pantry shelf at 07:30 (feeding not yet done).

```json
{
 "claims": [
  {
   "claim": "The dog leash is on Yuki's person during her weekend late-morning walk",
   "target": "dog_leash_shared",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 10,
   "to": 11
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the weekend morning feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekend",
   "from": 7,
   "to": 8
  },
  {
   "claim": "The dog bowl is on the kitchen floor during the weekend morning feeding",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "weekend",
   "from": 7,
   "to": 8
  },
  {
   "claim": "The dog leash is on the entry hook overnight before the weekend walk",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 3,
   "to": 6
  }
 ],
 "targets": {
  "dog_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "weekend",
    "from": 6.5,
    "to": 9,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 18,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 21,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 6.5,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
