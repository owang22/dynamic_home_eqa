# p_5d9b — Sick Day Morning: Yoga, Baking, Dog Walk, Both Home

The morning on a sick day follows the normal weekday pattern but with the added presence of Marco through midday. Marco does yoga at 6:00–6:45 (mat on the living room floor), then bakes from about 7:00 to 9:30 (baking tray, mixing bowl, and spatula on the kitchen counter). Yuki walks the dog at 7:00 (leash on her person) and feeds the dog at 7:15 (bowl on the kitchen floor, food bag pulled to the floor). After breakfast at the kitchen table, Marco journals at the bedroom desk from about 10:00 to 13:00 while Yuki reads her tablet at the kitchen table.

This document differs from the standard split by predicting the journal at the desk through 13:00 (on a normal weekday Marco packs up and leaves at 13:40, so the midday window is shorter and more rushed). The baking session may run longer because he has the whole morning. The tablet at the kitchen table during 8–10 h reflects Yuki reading while Marco bakes, rather than the tablet at the nightstand.

This document is refuted if the baking tray is not on the counter during 7–9 h, or if Marco's journal is not at the desk during 11–13 h, or if the dog leash is not on Yuki's person during 7–8 h.

```json
{
 "claims": [
  {
   "claim": "The baking tray is on the kitchen counter during Marco's morning baking session",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "The dog leash is on Yuki's person during her weekday morning walk",
   "target": "dog_leash_shared",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Marco's journal is at the bedroom desk during his midday writing session",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 11,
   "to": 13
  },
  {
   "claim": "The mixing bowl is on the kitchen counter during the morning baking",
   "target": "mixing_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "yoga_mat_marco": [
   {
    "days": "weekday",
    "from": 6,
    "to": 6.75,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 2,
    "to": 6,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
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
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "journal_marco": [
   {
    "days": "weekday",
    "from": 10,
    "to": 13,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "tablet_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "weekday",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "weekday",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
