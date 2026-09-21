# p_3e7a — Dog feeding: bag to the kitchen floor twice daily

Elena looks after the household's dog, and the feeding routine is the same on weekdays and weekends. The dog food bag lives on the pantry shelf between meals but is carried to the kitchen floor for a morning feed (roughly 7:00–8:30) and an evening feed (roughly 19:00–21:30), then put back. On weekdays Elena handles the morning feed before her 8:00 departure for work; on weekends she is home and feeds at a similar early hour. The dog bowl never leaves the kitchen floor—it is a fixed fixture. The dog leash hangs at the entry hook, ready for a walk, and the dog toy rests on the living-room floor where the dog naps.

What sets this document apart: it pins the dog food bag to the kitchen floor in two specific daily windows rather than leaving it at the pantry shelf all day. The mixture's worst miss is exactly this: predicting pantry_shelf_k1 when the bag is actually on the floor at 07:00 (day 4, Saturday). This document also asserts the bag is back on the pantry shelf at midday, which the 09:00, 13:00, and 18:00 weekday sightings confirm.

Refutation: if the dog food bag is sighted on the kitchen floor outside the 6:30–8:30 and 18:30–21:30 windows on multiple occasions, or if it is absent from the pantry shelf at midday on several days, the two-feeding model is wrong.

```json
{
 "claims": [
  {
   "claim": "The dog food bag is on the kitchen floor during the morning feed",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 7,
   "to": 8
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the evening feed",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The dog food bag is back on the pantry shelf at midday",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 12,
   "to": 14
  },
  {
   "claim": "The dog bowl is on the kitchen floor at the morning feed",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 7,
   "to": 8
  }
 ],
 "targets": {
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8.5,
    "to": 18.5,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 21.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
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
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ]
 }
}
```
