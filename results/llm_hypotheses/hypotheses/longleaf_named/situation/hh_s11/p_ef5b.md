# p_ef5b — p_k1l2 — Irregular creative hours; no fixed 9-to-5

Both Hana and Priya are freelancers with irregular schedules. Priya is a photographer (the camera on the bookshelf is her work tool); Hana is a musician/songwriter (the guitar is her instrument). There is no fixed weekday/weekend pattern. Priya goes out for shoots on unpredictable days—her camera, keys, wallet, and phone leave together. Hana mostly stays home to practice and compose; her guitar, tablet, and notebook rarely leave. The 18:00 Wednesday snapshot: Priya is at the entry about to go out for an evening shoot (or just got back from a daytime one). Her items are at the entry in transition. Hana's umbrella is just stored there. The key difference from commuter hypotheses: there is no consistent 9–17 OUT_OF_HOUSE window. Instead, "sometimes" blocks on various days. What sets this apart: Priya's camera is OUT_OF_HOUSE on some weekdays but not others; Hana's guitar is almost always in the house. What would refute it: finding a consistent pattern of Priya's keys being out 9–17 every single weekday for two weeks, or finding Hana's guitar out of the house.

```json
{
 "claims": [
  {
   "claim": "Priya's camera is out of the house on some weekday afternoons (shoots)",
   "target": "camera_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 20
  },
  {
   "claim": "Hana's guitar is in her bedroom on weekday mornings",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 8,
   "to": 14
  },
  {
   "claim": "Priya's keys are in the house on weekday mornings (irregular schedule)",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 7,
   "to": 10
  },
  {
   "claim": "Hana's tablet is at her desk on weekday afternoons",
   "target": "tablet_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 14,
   "to": 20
  }
 ],
 "targets": {
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 20,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 14,
    "to": 20,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 14,
    "to": 20,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 14,
    "to": 20,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 14,
    "to": 20,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 14,
    "to": 20,
    "at": "OUT_OF_HOUSE",
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
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 20,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "tablet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bed_b2",
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
   },
   {
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "sometimes"
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
  "umbrella_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 10,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
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
    "from": 8,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16,
    "to": 20,
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
    "chance": "rarely"
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
    "chance": "rarely"
   }
  ]
 }
}
```
