# p_9e1f — Dog Morning: Bowl to Counter, Bag to Floor, 07:00–08:30

Yuki feeds the dog at 07:00 on weekdays. The routine: she brings the dog food bag from the pantry shelf down to the kitchen floor, opens it, and pours food into the bowl. The bowl is temporarily on the counter during the pour (sighted at counter_k1 at 08:00) before being placed on the floor for the dog. The food bag sits on the kitchen floor during the feeding window (06:30–08:30) while she measures and pours, then goes back to the pantry shelf by 18:00. The dog leash is on the entry hook overnight and moves to the entry table by early morning for the 08:00 walk.

This document is more specific than p_f3a9 about the feeding mechanics: the bowl is at the COUNTER during the pour (not on the floor), and the food bag is at the FLOOR (not the counter) during the active feeding window. The 08:00 sighting of dog_bowl at counter_k1 and the 07:00–08:00 sightings of dog_food_bag at floor_k_k1 are the key data points.

What sets this apart: at 07:30 on a weekday, dog_bowl_shared is at counter_k1 (being filled) and dog_food_bag_shared is at floor_k_k1 (in use). If the robot finds the bowl on the floor and the bag on the pantry shelf at 07:30, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The dog bowl is at the kitchen counter during the 08:00 feeding pour",
   "target": "dog_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the 07:00 feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 6.5,
   "to": 8.5
  },
  {
   "claim": "The dog leash is on the entry hook overnight at 03:00",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "both",
   "from": 2,
   "to": 6
  },
  {
   "claim": "The dog food bag is on the pantry shelf at 18:00 after morning feeding is done",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 8.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 18.5,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 8.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.75,
    "to": 8.5,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "ON_PERSON",
    "chance": "sometimes"
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
