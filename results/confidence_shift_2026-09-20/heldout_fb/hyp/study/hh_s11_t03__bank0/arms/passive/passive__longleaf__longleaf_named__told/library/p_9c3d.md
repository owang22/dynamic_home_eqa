# p_9c3d — The 08:00 Kitchen Table; Staggered Breakfast, Dog Fed at 07:30

Both residents are present in the kitchen in the early morning. Priya (resident_2) has her breakfast at the kitchen table around 08:00: her bowl and mug are at the table. Hana (resident_1) follows a few minutes later, around 08:30–09:00, with her bowl at the kitchen table. The dog is fed at 07:30 by Priya: the dog food bag is on the kitchen floor and the dog bowl is always on the kitchen floor. After breakfast (by 09:30), the bowls and mugs go back to the cupboard.

This is a staggered breakfast, not a simultaneous one. Priya's items are at the table at 08:00; Hana's bowl is at the table at 09:00. Hana's mug, however, is already at the coffee table by 10:00 (she takes it with her to the living room for her work/lounge session), so the mug is NOT at the kitchen table at 09:00.

What sets this document apart: it pins the breakfast window to 07:30–09:30 with both residents' bowls at the kitchen table, and it distinguishes the dog feeding (07:00–08:30, bag on floor) from the breakfast. It also predicts the dog bowl is on the kitchen floor at ALL times (it is a permanent fixture). The mug_priya is at the kitchen table at 08:00 but back in the cupboard by 13:00.

Refutation: if the bowls are in the cupboard at 08:00 or 09:00 (not at the kitchen table), or if the dog food bag is on the pantry shelf at 07:30 (not on the floor), or if the dog bowl is off the kitchen floor, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Priya's bowl is at the kitchen table during the 08:00 breakfast",
   "target": "bowl_priya",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 7.5,
   "to": 9
  },
  {
   "claim": "Priya's mug is at the kitchen table during the 08:00 breakfast",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 7.5,
   "to": 9
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the 07:30 morning feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 7,
   "to": 8.5
  },
  {
   "claim": "Hana's bowl is at the kitchen table at 09:00",
   "target": "bowl_hana",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 8.5,
   "to": 10
  }
 ],
 "targets": {
  "bowl_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 10,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 7.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 7.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "cupboard_k1",
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
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8.5,
    "to": 22.5,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22.5,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
