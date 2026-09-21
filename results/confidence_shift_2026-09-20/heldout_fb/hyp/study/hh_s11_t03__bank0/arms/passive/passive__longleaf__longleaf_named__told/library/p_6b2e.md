# p_6b2e — The Evening Dog Feeding; Bag on the Floor from 19:00, Not 22:30

This document corrects the timing of the evening dog feeding that p_3c4d placed at 22:30–23:30. The sighting log shows the dog food bag on the kitchen floor at 19:00 on the weekend (day 5, three sightings) and at 23:00 on weekdays (two sightings), while the 18:00 pass still finds it on the pantry shelf. The feeding clearly begins around 19:00, not 22:30. The morning feeding (07:00–08:30, bag on the floor) and the midday storage (pantry shelf) are unchanged from the established pattern. The dog bowl remains permanently on the kitchen floor.

What sets this apart from p_3c4d: the evening window starts at 19:00 rather than 22:30, and the midday pantry window ends at 19:00 rather than 20:00, so there is no gap where the bag's location is unaccounted for between the 18:00 pantry pass and the 19:00 floor pass on weekends. A look at the pantry shelf at 19:00 or 20:00 that finds the bag there would refute this document; a look at the kitchen floor at 19:00 that finds nothing (while the bag is not on the pantry shelf) would also weaken it.

No objects leave the house in this document's scope. The dog leash and toy are handled by other documents.

```json
{
 "claims": [
  {
   "claim": "The dog food bag is on the kitchen floor during the 19:00 weekend pass, not on the pantry shelf",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekend",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The dog food bag is on the pantry shelf at the 18:00 pass on weekdays, before the evening feeding begins",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the 23:00 weekday pass after the evening feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 22.5,
   "to": 24
  },
  {
   "claim": "The dog bowl is on the kitchen floor at all times and never moves to the counter or table",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 19,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 24,
    "at": "floor_k_k1",
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
  ]
 }
}
```
