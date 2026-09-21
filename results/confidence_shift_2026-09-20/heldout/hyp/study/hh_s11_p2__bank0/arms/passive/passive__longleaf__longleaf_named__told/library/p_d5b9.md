# p_d5b9 — Priya's Routine Holds; Yoga, Walk, and the Dog Continue

Hana's illness and the friends' visit do not disrupt Priya's day. She is retired and anchored to her own rhythm: early-morning yoga with the mat on the living room floor, a morning walk with the dog (leash, keys, and jacket going out and coming back), tending the plants on the balcony, feeding the dog, and keeping the camera on the bookshelf between photography sessions. The dog food bag is at the pantry shelf or the kitchen floor where the bowl is. The watering can stays on the balcony floor, where it has been seen on all four sighted days.

This document is refuted if Priya's routine is visibly altered: the yoga mat is not on the floor in the early morning, the dog leash is not at the entry hook outside the walk window, the camera is off the bookshelf for the whole day, or the watering can has been moved off the balcony. If Priya has taken over Hana's chores or skipped the walk to look after Hana, the entry set and the leash would not follow the pattern here.

```json
{
 "claims": [
  {
   "claim": "Priya's camera stays on the bookshelf all day; her routine is unaffected by Hana's illness",
   "target": "camera_priya",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 8,
   "to": 20
  },
  {
   "claim": "The dog bowl is at the kitchen floor; Priya still feeds the dog on schedule",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 8,
   "to": 20
  },
  {
   "claim": "The dog leash is at the entry hook outside the morning walk window",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The watering can stays on the balcony floor; Priya tends the plants as usual",
   "target": "watering_can_shared",
   "expect": "balcony_floor_y1",
   "days": "weekday",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "camera_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 7,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "keys_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "watering_can_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
    "chance": "almost_always"
   }
  ]
 }
}
```
