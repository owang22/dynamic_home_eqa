# p_c3d4 — Hana at her desk, Priya at the office

Hana is a remote software designer who works from her bedroom desk 9:00–17:00. Priya commutes to a downtown office 8:00–17:00. The 18:00 snapshot catches Priya arriving: her keys, wallet, sunglasses, jacket, and shoes are still at the entry because she has just walked in. Hana has been home since 17:00 and her tablet, notebook, and guitar are in their usual spots. Hana's umbrella at the entry is simply where she stores it (she rarely goes out on foot). On weekdays, Priya's keys, wallet, phone, tablet, sunglasses, jacket, and shoes are OUT_OF_HOUSE from 8:00 to 17:00. Hana's personal items (tablet, notebook, phone) never leave the house. The dog is home all day with Hana. What sets this apart: Hana's tablet and notebook are IN the house 9–17 on weekdays while Priya's are OUT. What would refute it: finding Hana's tablet or notebook out of the house on a weekday afternoon, or finding Priya's keys in the house at 12:00 on a Tuesday.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at her desk on weekday afternoons",
   "target": "tablet_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
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
   "claim": "Hana's notebook is at her desk on weekday mornings",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Priya's jacket is out of the house on weekday mornings",
   "target": "jacket_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17
  }
 ],
 "targets": {
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
    "from": 8,
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
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 24,
    "at": "entry_hook_e1",
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
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
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
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
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
   },
   {
    "days": "weekday",
    "from": 8,
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
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
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
    "from": 8,
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
    "from": 8,
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
    "chance": "almost_always"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
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
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "umbrella_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
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
    "to": 10,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_b1",
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
  ],
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
    "chance": "sometimes"
   }
  ]
 }
}
```
