# p_2e9f — Morning transition: bathroom ritual, kitchen breakfast, office settling (6–9h)

A fresh document focused on the 06:00–09:00 window, where the library's "worst objects" list is densest. The 07:00 and 08:00 passes reveal a clear transition sequence that no existing document captures well:

- **Elena's bathroom ritual (6:30–8:00):** Her towel is pulled from the towel_rack to the bathroom_shelf (07:00 pass: 3 sightings at shelf), her razor moves to the shelf (07:00: 1 at shelf, 1 at medicine_cabinet), and her water bottle is at the armchair (07:00: 2 sightings) — she sits and reads or scrolls before leaving.
- **Ines's breakfast and office settling (7:00–8:30):** Her mug is at the kitchen_table at 07:00 (1 sighting). By 08:00 her water bottle is at desk_o1 (1 sighting) and her laptop is at floor_o_o1 or desk_o1 (the 03:00 pass showed both). Her glass is at the kitchen_table at 12:00–13:00 (lunch) but at the sink or nightstand otherwise.
- **Yoga mat at the bed (6:00–8:00):** The 03:00 and 07:00 passes both caught it at bed_b1. It is unrolled on the living room floor only during the actual practice window (~7:00–7:45).

What sets this apart: it places Elena's water bottle at the armchair (not the entry floor) in the 7:00 hour, her razor and towel at the bathroom shelf (not the sink or rack) during the 6:30–8:00 window, and Ines's mug at the kitchen table at 7:00 (not the cupboard). The yoga mat is at bed_b1, not coffee_table.

What would refute it: finding Elena's water bottle at the entry floor at 07:00, her razor at the sink at 07:00, or Ines's mug at the cupboard at 07:00.

```json
{
 "claims": [
  {
   "claim": "Elena's water bottle is at the armchair at 07:00",
   "target": "water_bottle_elena",
   "expect": "armchair_l1",
   "days": "both",
   "from": 6.5,
   "to": 8
  },
  {
   "claim": "Elena's towel is on the bathroom shelf at 07:00",
   "target": "towel_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 6.5,
   "to": 8
  },
  {
   "claim": "Ines's mug is at the kitchen table at 07:00",
   "target": "mug_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 6.5,
   "to": 8
  },
  {
   "claim": "Elena's razor is on the bathroom shelf at 07:00",
   "target": "razor_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 6.5,
   "to": 7.5
  },
  {
   "claim": "Ines's water bottle is at the office desk by 08:00",
   "target": "water_bottle_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 8,
   "to": 17
  }
 ],
 "targets": {
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "towel_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "razor_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "razor_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
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
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_elena": [
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
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 7.75,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "glass_ines": [
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
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "laptop_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_o_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "floor_o_o1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
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
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_elena": [
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
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_elena": [
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
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:shoes": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "kettle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "toaster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
