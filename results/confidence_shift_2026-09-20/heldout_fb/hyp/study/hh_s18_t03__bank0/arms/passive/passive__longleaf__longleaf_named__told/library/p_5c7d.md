# p_5c7d — The desk holds: Ines at desk_o1, Elena out 8–17:30, 21:00 TV shift

Ines works from the office desk (desk_o1) every weekday from roughly 9 to 5:30. Her laptop, charger, headphones, and pen all live at that desk during work hours: the robot's positive sightings place the laptop at the desk at 10:00, 16:00, and 17:00; the charger at the desk at 12:00, 14:00, 15:00, 17:00, and 18:00; and the headphones at the desk at 14:00, 15:00, 16:00, 17:00, and 18:00. After 18:00 the laptop moves to the office floor (floor_o_o1), where it is seen at 18:00. The charger migrates to the office shelf at 23:00, and the headphones go to the bed at 21:00. Ines's water bottle sits at the desk from 08:00 through 17:00, with a refill stop at the kitchen sink around 14:00. Her mug is at the kitchen table at 07:00 for breakfast, at the desk from 14:00 through 18:00, and at the coffee table at 22:00 during evening TV.

Elena commutes to her office in town from about 8:00 to 17:30 on weekdays. Her keys, backpack, headphones, wallet, laptop, jacket, shoes, and sunglasses all leave the house with her and return at 18:00. Her water bottle is at the armchair at 07:00 (seen twice), her towel is on the bathroom shelf at 07:00 (seen three times), and her razor is in the bathroom at 07:00. By 08:00 she is out the door. On weekends both women sleep in and run errands around midday; nothing is out of the house for a full day.

Ines never leaves the house. Her keys stay at the entry table, her jacket on the entry hook, her shoes on the shoe rack, her umbrella on the entry floor, and her sunglasses and wallet at the entry table, all day, every day.

The evening TV shift happens at 21:00: the remote moves from the TV stand to the coffee table, the blanket moves from the couch to the coffee table, and the speaker settles on the couch. The snack bowl, which rests in the kitchen sink overnight, appears at the coffee table by 23:00.

This document sets itself apart by placing Ines's laptop, charger, headphones, and pen at the desk during work hours (not the floor, not out of the house), by specifying the 18:00 laptop-to-floor migration, and by timing the TV-object migration at 21:00 rather than 20:00 or 22:00. It is refuted if the laptop is consistently found on the office floor during 9–17:30, if Elena's personal items are sighted inside the house during 9–17:30, or if the remote and blanket are still at the TV stand and couch respectively at 22:00.

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is at the office desk at 10:00 on weekdays",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 11
  },
  {
   "claim": "Ines's laptop is on the office floor at 18:00 on weekdays",
   "target": "laptop_ines",
   "expect": "floor_o_o1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Elena's keys are out of the house at 10:00 on weekdays",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "The remote is on the coffee table at 22:00",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Ines's mug is at the office desk at 16:00 on weekdays",
   "target": "mug_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Ines's water bottle is at the kitchen sink at 14:00 on weekdays",
   "target": "water_bottle_ines",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 14,
   "to": 15
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "floor_o_o1",
    "chance": "usually"
   }
  ],
  "charger_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "usually"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "pen_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 14,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 15,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
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
  "mug_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 14,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "glass_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13.5,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "headphones_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "wallet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "hat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "scarf_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 6.5,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "towel_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "razor_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ],
  "keys_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_ines": [
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
  "umbrella_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "yoga_mat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
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
  "class:blanket": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
