# p_4f6a — Dog Objects on the Floor: Bag, Bowl, Leash, Toy

This document focuses exclusively on the four dog-related objects and their actual resting and in-use locations, correcting the pantry-shelf assumption that several other documents carry for the food bag. The evidence is unambiguous: the dog food bag is on the kitchen floor (floor_k_k1) at 03:00 (×2), 07:00 (×1), 08:00 (×3), 19:00 (×2), and 22:00 (×2). It appears at pantry_shelf_k1 only at 18:00 (×1) and 22:00 (×1) — a brief post-feeding reposition, not a resting spot. The bag lives on the floor where Yuki can reach it for the 07:00 and 18:00 feedings without bending to a shelf.

The dog bowl is permanently on the kitchen floor (13 sightings, 3/3 days at floor_k_k1). The dog leash hangs on the entry hook overnight (03:00: entry_hook_e1 ×2) and moves to the entry table during the day when Yuki walks the dog (18:00: entry_table_e1 ×1). The dog toy is on the living-room floor (3/3 days, floor_l_l1).

What sets this document apart: at 07:00 on a weekday, the dog food bag is at floor_k_k1 (not pantry_shelf_k1), and at 03:00 the leash is at entry_hook_e1 (not entry_table_e1). If the robot finds the food bag on the pantry shelf at 07:00 or the leash on the entry table at 03:00, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "The dog food bag is on the kitchen floor at 07:00 during the morning feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 6.5,
   "to": 8.5
  },
  {
   "claim": "The dog leash is on the entry hook at 03:00 overnight",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "both",
   "from": 2,
   "to": 6
  },
  {
   "claim": "The dog bowl is on the kitchen floor at 07:15 during the morning pour",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 7,
   "to": 7.5
  },
  {
   "claim": "The dog food bag is on the kitchen floor at 19:00 after the evening feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 18.5,
   "to": 20
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
    "from": 6.5,
    "to": 8.5,
    "at": "floor_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 18.5,
    "at": "floor_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
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
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 6.75,
    "to": 7.25,
    "at": "floor_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.75,
    "to": 18.25,
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
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16.5,
    "to": 17.5,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8.5,
    "to": 16.5,
    "at": "entry_table_e1",
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
