# p_b2c9 — Work kit travels; vitamins stay home; journal at desk (fork of p_9c2e)

Two residents run a conventional two-adult household. Marco leaves for his afternoon-to-night shift around 13:40 and returns around 23:00 on weekdays; on weekends he is home except for a midday errand run (11:30–14:00). Yuki is home most of the day, taking a morning walk (07:00–08:30 weekdays, 10:00–11:30 weekends) and a shorter afternoon errand (14:30–16:00 weekdays only). The dog is fed by Yuki at 07:00 and 18:00, walked at 08:00 and 16:45. Meals are at 07:30, 12:30, and 18:30; evening TV runs 19:30–22:00. Marco bakes on weekday mornings (06:30–08:30); Yuki bakes on weekend afternoons (14:00–16:30). Marco journals at the nightstand 22:30–00:00. Yuki plays guitar 17:30–19:00 on weekdays. Marco does yoga 06:00–06:45 weekdays.

What changed from the parent (p_9c2e): The parent claimed only the lunchbox goes to work and the journal stays at the nightstand. Two corrections are needed. First, the journal's resting spot is desk_b1, not nightstand_b1: the 16:00 weekday sighting found it at the desk, and the parent's nightstand claim took "against 2" hits. The nightstand is where Marco uses the journal in the evening, not where it rests between uses. Second, Marco takes his full personal kit to work—keys, jacket, backpack, notebook, phone, shoes, sunglasses, wallet, water bottle—all of which show empty looks at their resting spots during 9–17 h. The parent's "only the lunchbox" framing is too narrow. However, this fork retains the parent's claim that the vitamins stay at counter_k1: the evidence is mixed (2 for, 5 against on the in-home claim), and it is plausible that Marco takes his vitamins in the evening at home rather than packing them for work. If the vitamins are consistently found out of the house, this document loses on that point.

What sets this document apart from p_f3a7: between 14:00 and 23:00 on a weekday, vitamins_marco is at counter_k1 (in the house), while in p_f3a7 it is OUT_OF_HOUSE. Everything else—the full kit out, journal at desk, guitar on couch—is the same.

```json
{
 "claims": [
  {
   "claim": "Marco's journal is at the desk during his work shift",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's vitamins remain at the kitchen counter during his work shift",
   "target": "vitamins_marco",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's backpack is out of the house during his work shift",
   "target": "backpack_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "The guitar is on the couch during the afternoon before Yuki's practice",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
  "lunchbox_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "vitamins_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 7.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 22,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "journal_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_marco": [
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
    "to": 6.75,
    "at": "floor_l_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 7.75,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
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
    "from": 17.5,
    "to": 19,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "sunglasses_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
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
    "to": 8.5,
    "at": "counter_k1",
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
    "at": "kitchen_table_k1",
    "chance": "usually"
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
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
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
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
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
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:glass": [
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
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
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
    "from": 18,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:pan": [
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
  "class:kitchen_knife": [
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
    "at": "drawer_k_k1",
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
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:remote": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22,
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
    "from": 19.5,
    "to": 22,
    "at": "couch_l1",
    "chance": "almost_always"
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
    "from": 6.75,
    "to": 7.25,
    "at": "floor_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.75,
    "to": 18.25,
    "at": "floor_k_k1",
    "chance": "almost_always"
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
    "from": 7.75,
    "to": 8.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 16.5,
    "to": 17.25,
    "at": "entry_hook_e1",
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
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:book": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "tablet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "class:scarf": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:umbrella": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "class:shoes": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "class:medication": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "medicine_cabinet_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 7.5,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ],
  "class:razor": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 15,
    "to": 17,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "class:soap_dispenser": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "almost_always"
   }
  ],
  "class:toothbrush_holder": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "almost_always"
   }
  ],
  "class:laundry_basket": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:toaster": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:kettle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:knife_block": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:spatula": [
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
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:wall_clock": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:dog_food_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 15,
    "to": 19,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ],
  "class:dog_toy": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "class:doormat": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "class:first_aid_kit": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "medicine_cabinet_ba1",
    "chance": "almost_always"
   }
  ],
  "class:detergent": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:toiletry_bag": [
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
    "chance": "sometimes"
   }
  ],
  "class:ironing_board": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ],
  "class:vacuum_cleaner": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "class:toolbox": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   }
  ],
  "class:board_game": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "class:candle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:tissue_box": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:lamp": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "almost_always"
   }
  ],
  "class:baking_tray": [
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
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "class:mixing_bowl": [
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
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "class:serving_dish": [
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
   }
  ],
  "class:notebook": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "class:water_bottle": [
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
    "to": 8.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:wallet": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "class:keys": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "phone_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "sunglasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "class:backpack": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:jacket": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:phone": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:sunglasses": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
