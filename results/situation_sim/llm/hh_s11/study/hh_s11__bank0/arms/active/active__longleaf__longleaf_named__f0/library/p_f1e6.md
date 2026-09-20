# p_f1e6 — Dog food bag lives in the pantry; floor only at the three meal times

This document refines the dog-feeding model. The per-object evidence shows dog_food_bag_shared in pantry_shelf_k1 on all 3 sighted days (3/3), with weekday 9–17 h looks at the pantry finding it 2 of 3 times (the one miss is presumably during the 11–12 h feeding when it is on the floor). The bag is a pantry resident that is briefly brought to the kitchen floor for the three daily meals (≈7:00, ≈11:30, ≈18:00) and immediately returned. Unlike p_d4e9, which gives the floor blocks "sometimes" and the pantry "usually" as a base, this document makes the pantry the near-certain default (almost_always) and narrows the floor appearances to tight 30-minute windows. The dog_bowl_shared, by contrast, is a permanent kitchen-floor fixture (2/3 sighted days at floor_k_k1, found 2/3 during 9–17 h) and is never moved to the pantry. What sets this apart: the dog_food_bag is almost_always in the pantry, and the floor blocks are narrow (7–7.5, 11.5–12, 18–18.5) rather than the wider 1-hour windows in p_d4e9. What would refute it: finding the dog food bag on the kitchen floor at 10:00 or 14:00 (outside any meal window), or finding it anywhere other than the pantry at 20:00.

```json
{
 "claims": [
  {
   "claim": "The dog food bag is in the pantry on weekday midday (not at feeding time)",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "The dog food bag is in the pantry on weekday afternoon (between meals)",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 13,
   "to": 17
  },
  {
   "claim": "The dog bowl is on the kitchen floor on weekday midday (permanent fixture)",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 7,
    "to": 7.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 11.5,
    "to": 12,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 18.5,
    "at": "floor_k_k1",
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
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
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
    "days": "weekend",
    "from": 8,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "tablet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "desk_b2",
    "chance": "sometimes"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   }
  ]
 }
}
```
