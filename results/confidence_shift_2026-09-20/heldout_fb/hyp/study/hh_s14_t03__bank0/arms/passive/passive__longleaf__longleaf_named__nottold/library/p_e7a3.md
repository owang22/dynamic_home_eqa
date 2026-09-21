# p_e7a3 — Dog Food Bag: Floor During Feeding, Pantry Between Meals

Marco and Yuki share a dog that is fed twice a day by Yuki, who handles all the dog's care. The food bag lives on the kitchen floor during each feeding window and is returned to the pantry shelf between meals. On weekdays the morning feeding is around 7:00–8:00 (Yuki's walk is at 7, so she feeds the dog just before or just after); the bag sits on the floor from roughly 6:30 until about 11:00 (the dog finishes eating, Yuki leaves the bag out). The afternoon sees the bag back in the pantry from 11:00 through 18:00. The evening feeding is around 19:00–20:00, and the bag is on the floor from 18:30 through 22:30. On weekends the rhythm is slightly later and less consistent: the bag is in the pantry overnight and through the morning, comes to the floor briefly around 7:30–9:00 for the morning feed, returns to the pantry, and may come out again around 19:00–20:30 for the evening feed. The 03:00 weekday sightings show a split (floor and pantry) because on some nights Yuki forgets to put the bag back after the evening feeding.

This document sets itself apart by pinning the bag to the kitchen floor during both feeding windows on weekdays and to the pantry shelf in the gap between them, rather than to the counter (as p_f3a9 does for the 6:75–7:25 window) or to a single resting spot. It would be refuted if the bag were consistently found on the counter during feeding, or if it were seen on the floor at 14:00 on a weekday (the between-meals window).

```json
{
 "claims": [
  {
   "claim": "The dog food bag is on the kitchen floor during the weekday morning feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 7,
   "to": 8.5
  },
  {
   "claim": "The dog food bag is in the pantry shelf at midday on a weekday between meals",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the weekday evening feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The dog food bag is in the pantry shelf during the weekend midday",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 10,
   "to": 17
  }
 ],
 "targets": {
  "dog_food_bag_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 6.5,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 11,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 18.5,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 22.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
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
    "from": 9,
    "to": 19,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "floor_k_k1",
    "chance": "rarely"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ]
 }
}
```
