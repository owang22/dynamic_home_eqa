# p_9dd2 — p_s9t0 — Minimal travelers; both work from home, nothing leaves but the phone

Both Hana and Priya work from home. Hana is a data analyst; Priya is a graphic designer. They work 9:00–17:00 but never leave the house. The only things that leave are their phones (for a quick walk with the dog or a short errand) and occasionally keys (if they walk to a nearby café). The 18:00 walkthrough: both are home, working or winding down. Priya's keys, wallet, sunglasses, jacket, and shoes at the entry are simply her permanent storage system—she has not been out and will not be out. Hana's umbrella is stored at the entry for rainy days (rarely used). The dog is home all day. What sets this apart: NO object is OUT_OF_HOUSE for more than 2 hours on any day. Priya's keys are IN the house 9:00–17:00 on weekdays. What would refute it: finding Priya's keys out of the house for more than 2 consecutive hours on a weekday, or finding Hana's tablet out of the house at any time.

```json
{
 "claims": [
  {
   "claim": "Priya's keys are in the house on weekday midday (work from home)",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Hana's tablet is at her desk on weekday midday",
   "target": "tablet_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's tablet is at her desk on weekday midday",
   "target": "tablet_priya",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Hana's guitar is in her bedroom on weekday midday",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
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
    "days": "both",
    "from": 8,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
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
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "desk_b2",
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
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
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
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
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
    "days": "both",
    "from": 14,
    "to": 16,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 10,
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
   },
   {
    "days": "both",
    "from": 9,
    "to": 10,
    "at": "balcony_table_y1",
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
    "from": 8,
    "to": 9,
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
    "from": 7,
    "to": 8,
    "at": "bedroom_floor_b2",
    "chance": "sometimes"
   }
  ]
 }
}
```
