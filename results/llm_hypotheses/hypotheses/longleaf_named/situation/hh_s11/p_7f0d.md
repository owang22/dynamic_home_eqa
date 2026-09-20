# p_7f0d — p_w3x4 — Evening yoga for Priya, guitar practice for Hana; both work 9-to-5

Both Hana and Priya work 9:00–17:00 office jobs. The 18:00 walkthrough catches Priya arriving (entry items). The defining evening routine: from 19:00 to 20:00, Priya does yoga in her bedroom (mat comes out of the wardrobe to the bedroom floor), and Hana practices guitar in the living room or her bedroom. This happens every day, weekday and weekend. The yoga mat is at the wardrobe 0:00–19:00 and at bedroom_floor_b2 19:00–20:00. The guitar is at bedroom_floor_b1 most of the day and moves to floor_l_l1 for evening practice. On weekdays, both are out 9:00–17:00. What sets this apart: the yoga mat is at bedroom_floor_b2 at 19:30 every day, and the guitar is at floor_l_l1 at 19:30 on most days. What would refute it: finding the yoga mat at the wardrobe at 19:30, or finding the guitar at bedroom_floor_b1 at 19:30 on a weekday evening.

```json
{
 "claims": [
  {
   "claim": "The yoga mat is on Priya's bedroom floor at 19:30 (yoga time)",
   "target": "yoga_mat_priya",
   "expect": "bedroom_floor_b2",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The guitar is in the living room at 19:30 (practice time)",
   "target": "guitar_hana",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Priya's keys are out of the house on weekday midday",
   "target": "keys_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Hana's tablet is out of the house on weekday midday",
   "target": "tablet_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "bedroom_floor_b2",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "floor_l_l1",
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
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
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
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
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
    "to": 17,
    "at": "OUT_OF_HOUSE",
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
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_hana": [
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
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "umbrella_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
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
  "watering_can_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
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
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ]
 }
}
```
