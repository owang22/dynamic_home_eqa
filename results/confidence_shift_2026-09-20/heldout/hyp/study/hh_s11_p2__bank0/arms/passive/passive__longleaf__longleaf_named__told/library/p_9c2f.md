# p_9c2f — The 22:00 Couch; Shared Evening TV with Remote at the Coffee Table

Both residents watch television together in the evening. Around 21:30 the remote moves from the TV stand to the coffee table, the blanket is pulled over to the coffee table or couch, and the snack bowl comes out of the kitchen for the show. Priya is confirmed in the living room at 22:00 on day 0. After the programme ends near 23:30 the remote is dropped on the living-room floor, where it stays until morning. During the working day it rests on the TV stand. This document directly contradicts p_c3d4's "no shared TV, remote on the TV stand" claim: the 22:00 pass clearly shows the remote at coffee_table_l1, and the blanket and snack bowl are there too.

What would refute this document: a look at the TV stand at 22:00 that finds the remote; a look at the coffee table at 22:00 that finds neither the remote nor the blanket; a resident look showing only one person in the living room at 22:00.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table during the evening TV show",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The blanket is on the coffee table during evening TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the coffee table during evening TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
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
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "almost_always"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
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
  "class:bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
