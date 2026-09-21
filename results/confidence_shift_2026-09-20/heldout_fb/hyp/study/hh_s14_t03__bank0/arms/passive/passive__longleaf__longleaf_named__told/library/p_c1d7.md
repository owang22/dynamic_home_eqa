# p_c1d7 — Night Resting v2: Corrected Knife in Drawer, Pan in Cupboard, Added Objects (fork of p_5f1a)

This fork of p_5f1a corrects two failed nighttime claims and adds objects whose 03:00 resting places are now confirmed by multiple patrol passes. The kitchen knife is in the drawer (drawer_k_k1), not the cupboard: the 03:00 sightings show drawer_k_k1 ×1 and cupboard_k1 ×1, and the 18:00 sighting is at drawer_k_k1. The p_5f1a claim (cupboard, 2–5 h) scored for 1, against 2, so the drawer is the better bet. The pan is in the cupboard (cupboard_k1), not the pantry shelf: the 03:00 sightings show pantry_shelf_k1 ×1 and cupboard_k1 ×1, and the 18:00 sighting is at cupboard_k1. The p_5f1a claim (pantry shelf, 2–5 h) scored for 1, against 2, so the cupboard is the better resting spot.

New objects added with confirmed 03:00 locations: serving_dish_shared at cupboard_k1 (×2 at 03:00), snack_bowl_shared at cupboard_k1 (×1 at 03:00, also counter_k1 ×1), mixing_bowl_shared at pantry_shelf_k1 (×1 at 03:00), baking_tray_shared at pantry_shelf_k1 (×1 at 03:00). The guitar (couch_l1 ×2) and dog leash (entry_hook_e1 ×2) are retained from the parent.

What sets this document apart from p_5f1a: at 03:00, the kitchen knife is at drawer_k_k1 (not cupboard_k1) and the pan is at cupboard_k1 (not pantry_shelf_k1). If the robot finds the knife in the cupboard or the pan on the pantry shelf at 03:00, this document is refuted on those points.

```json
{
 "claims": [
  {
   "claim": "Yuki's guitar is on the living room couch at 03:00 overnight",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The kitchen knife is in the kitchen drawer at 03:00 overnight",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The pan is in the kitchen cupboard at 03:00 overnight",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The serving dish is in the kitchen cupboard at 03:00 overnight",
   "target": "serving_dish_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "guitar_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 16.5,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 13.5,
    "to": 16,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
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
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "mixing_bowl_shared": [
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
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "baking_tray_shared": [
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
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
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
   }
  ]
 }
}
```
