# p_f6b2 — Dog Food Bag on the Kitchen Floor; Feeding at 7–8 AM and 23:00

The dog food bag (dog_food_bag_shared) follows a clear pattern: it is brought from the pantry shelf to the kitchen floor for feeding. The 07:00 and 08:00 passes show it at floor_k_k1 (×1 at 07:00, ×4 at 08:00), with the 08:00 pass also catching it at counter_k1 ×2 (Priya is mid-feeding, moving it around). By 18:00 it is back at pantry_shelf_k1 ×2. At 23:00 it is at floor_k_k1 ×2 again (evening feeding, or Hana feeds the dog after coming home). The dog bowl (dog_bowl_shared) is at floor_k_k1 on all 13 sightings — it never moves.

What sets this apart from documents that keep the food bag at the pantry shelf all day: this document places it on the kitchen floor during the 07:00–09:00 and 23:00–00:30 feeding windows. What would refute it: a look at floor_k_k1 at 08:00 that finds no dog food bag, or a look at pantry_shelf_k1 at 08:00 that finds the bag.

Priya (resident_2) does the morning feeding during or just after her walk (she brings the dog in, feeds it, then goes about her day). The evening feeding at 23:00 may be done by Hana (resident_1) when she comes home, or by Priya before bed.

```json
{
 "claims": [
  {
   "claim": "The dog food bag is on the kitchen floor during the morning feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 7.5,
   "to": 8.5
  },
  {
   "claim": "The dog food bag is back on the pantry shelf during the midday",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The dog bowl is on the kitchen floor at all times",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The watering can is on the balcony floor at all times",
   "target": "watering_can_shared",
   "expect": "balcony_floor_y1",
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
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 9,
    "at": "floor_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 0.5,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ],
  "class:dog_bowl": [
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11.5,
    "at": "OUT_OF_HOUSE",
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
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
  "watering_can_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
    "chance": "almost_always"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
