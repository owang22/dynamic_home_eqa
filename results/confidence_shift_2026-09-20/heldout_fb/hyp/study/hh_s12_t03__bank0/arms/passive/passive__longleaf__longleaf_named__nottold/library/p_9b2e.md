# p_9b2e — Standard split, dinner at 20:30 (fork of p_4c7d)

Forked from p_4c7d to correct two errors flagged by the evidence. First, the dinner window for plates and glasses was 19.5–21; the 19:00 pass shows plate_elena in the cupboard and glass_priya in the sink, while the 20:00 pass shows both at the dining table (×3 each). The window now starts at 20:00. Second, the glasses_priya ON_PERSON block (7–22h) has failed (0.13 on 3 sightings); the passes show the glasses on the nightstand or coffee table, never worn. Replaced with the coffee-table pattern.

What changed from the parent: (1) class:plate, class:glass, class:bowl dinner window moved from 19.5–21 to 20–21.5; (2) glasses_priya ON_PERSON block removed, replaced with coffee_table_l1 for 15–18 and 20–23; (3) mug_elena and class:mug dinner block moved from 19.5–21 to 20–21.5 (sightings show mugs at coffee table, not dining table, in the evening — but the 20:00 pass does show mug_elena at coffee_table_l1, so the mugs are at the coffee table during the TV window, not the dining table). Actually, re-examining: mug_elena at 20:00 is coffee_table_l1, not dining_table_d1. The mugs do NOT go to the dining table. Removing the dining table block for mugs.

Refutation: if plate_elena is at the dining table at 19:00 on a weekday (before the 20:00 start), or if glasses_priya is sighted ON_PERSON at any hour.

_(targets the fork left unstated are inherited from p_4c7d)_

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is out of the house on weekdays during work hours",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's plate is at the dining table at 20:00 on a weekday",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21.5
  },
  {
   "claim": "Priya's glass is at the dining table at 19:00 on a weekday",
   "target": "glass_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Baking tray is at the counter during Saturday morning baking",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
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
  "hat_elena": [
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
  "helmet_elena": [
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
  "bike_lock_elena": [
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
  "umbrella_elena": [
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
    "chance": "sometimes"
   }
  ],
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
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
    "from": 7,
    "to": 9,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "notebook_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "pen_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "usually"
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
    "from": 12,
    "to": 13.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "usually"
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
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:water_bottle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 8,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 21.5,
    "at": "floor_k_k1",
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
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 3,
    "to": 9,
    "at": "armchair_l1",
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
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 8,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 10,
    "at": "floor_l_l1",
    "chance": "sometimes"
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
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
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
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 17.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
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
    "from": 12,
    "to": 13.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
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
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
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
    "from": 12,
    "to": 13.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "knife_block_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
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
   }
  ],
  "wall_clock_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
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
  "plant_pot_3_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 22.5,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ],
  "skincare_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ],
  "razor_priya": [
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
    "at": "sink_ba_ba1",
    "chance": "almost_always"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 22.5,
    "at": "sink_ba_ba1",
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
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 22.5,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dresser_b1",
    "chance": "usually"
   }
  ],
  "toiletry_bag_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "soap_dispenser_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "almost_always"
   }
  ],
  "toothbrush_holder_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "almost_always"
   }
  ],
  "detergent_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "laundry_basket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:book": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 15,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:cushion": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "cushion_2_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "picture_frame_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "lamp_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ],
  "doormat_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15.5,
    "to": 17.5,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10.5,
    "to": 12,
    "at": "floor_l_l1",
    "chance": "sometimes"
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
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "duster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 17,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ]
 }
}
```
