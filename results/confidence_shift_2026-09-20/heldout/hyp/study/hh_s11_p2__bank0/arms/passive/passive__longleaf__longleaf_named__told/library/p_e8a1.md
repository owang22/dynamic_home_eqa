# p_e8a1 — Weekend Dog & Balcony: The Routine Holds

The dog's routine is largely unchanged on weekends. The dog bowl stays on the kitchen floor all day (Priya feeds on schedule). The dog food bag is on the chair overnight (Priya sits there in the morning to prepare the food), moves to the pantry shelf during the day, and ends up on the kitchen floor in the evening (after the last feeding). The dog toy stays on the living room floor, as it does every day. The dog leash stays on the entry hook all day on weekends—there is no set morning walk like on weekdays, and the leash is not carried out. The watering can stays on the balcony floor, and Priya tends the plants as usual. The three plant pots remain on the side table, counter, and desk respectively. The vacuum cleaner stays in storage.

This document differs from p_3b8d (leash and keys out of house for weekday walk) and p_bcd1 (twice-daily walk with leash and toy out) by keeping the leash in the house all weekend. It would be refuted if the dog leash is found out of the house, the dog bowl is off the kitchen floor, or the watering can is off the balcony.

```json
{
 "claims": [
  {
   "claim": "The dog bowl is on the kitchen floor all day on the weekend",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The dog leash stays on the entry hook all day on the weekend, not out of the house",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The watering can stays on the balcony floor on the weekend",
   "target": "watering_can_shared",
   "expect": "balcony_floor_y1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The dog food bag is on the pantry shelf during the weekend daytime",
   "target": "dog_food_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekend",
   "from": 8,
   "to": 20
  },
  {
   "claim": "The puzzle box stays on the bookshelf on the weekend, not out on the dining table",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "dog_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 20,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
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
  "class:plant_pot": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ],
  "plant_pot_2_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "plant_pot_3_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   }
  ],
  "vase_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "almost_always"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
