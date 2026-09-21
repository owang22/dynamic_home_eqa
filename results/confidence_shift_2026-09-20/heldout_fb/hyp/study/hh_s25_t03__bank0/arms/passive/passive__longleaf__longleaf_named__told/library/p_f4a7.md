# p_f4a7 — Marco's laptop in a bag at the desk during work (fork of p_a1b2)

Two remote workers share this home. Both sit at their desks from 9 to 17:30 on weekdays and never leave during work hours. Keys, wallets, and jackets stay at the entry all day. Meals happen at the kitchen table for breakfast and lunch, at the dining table for dinner. In the evening both settle onto the couch for TV from 20:00 to 22:30. On weekends they sleep in until about 10:30, do errands together around midday, and are home the rest of the day. Nothing in this household travels.

What changed from the parent (p_a1b2): The parent predicted laptop_marco at desk_b1 "almost_always" all day. The evidence is damning: 19 empty looks at desk_b1 during 9–17 versus only 4 finds. The sightings place the laptop at the desk at 03:00, 09:00, 17:00, and 18:00 — the boundaries of the work day — but not in the middle. I now predict the laptop is at desk_b1 in a closed bag during 10–17 (the robot cannot see through the bag), open and visible only in the morning (7–10) and late afternoon (17–19). The same pattern applies to water_bottle_marco (at the desk 8–10, then in a bag or carried to the dining table at dinner) and charger_marco (at the desk 0–9 and 17–24, in a bag 9–17, on the bedroom floor after 23). The notebook and pen remain visible on the desk throughout because they are loose items, not bagged.

What would refute this fork: laptop_marco sighted at a receptacle other than desk_b1 during 10–16 on a weekday (it should be in a bag at the desk), or water_bottle_marco sighted at desk_b1 at 13:00 on a weekday (it should be bagged or at the dining table).

_(targets the fork left unstated are inherited from p_a1b2)_

```json
{
 "claims": [
  {
   "claim": "Marco's laptop is open and visible at his desk in the morning before the work day",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 7,
   "to": 10
  },
  {
   "claim": "Marco's water bottle is at his desk in the morning",
   "target": "water_bottle_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Marco's charger is at his desk in the late afternoon after work ends",
   "target": "charger_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Marco's water bottle is at the dining table during dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 19.5,
   "to": 20.5
  }
 ],
 "targets": {
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 10,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 16.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "keys_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "class:blanket": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22.5,
    "at": "couch_l1",
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
    "from": 20,
    "to": 22.5,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "class:snack_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22.5,
    "at": "coffee_table_l1",
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
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12.5,
    "to": 14,
    "at": "kitchen_table_k1",
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
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
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
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
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
    "from": 9,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "class:charger": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "class:headphones": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "class:jacket": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "class:shoes": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "class:running_shoes": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "class:water_bottle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "class:cutting_board": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
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
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "class:kitchen_knife": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:meditation_cushion": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "class:watering_can": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
    "chance": "usually"
   }
  ],
  "class:vacuum_cleaner": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
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
  "class:fruit_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
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
    "chance": "almost_always"
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
  "class:wall_clock": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:vitamins": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
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
   }
  ],
  "class:glasses": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "class:iron": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "almost_always"
   }
  ],
  "class:ironing_board": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "class:board_game": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
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
  "class:cushion": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
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
  "class:umbrella": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "class:hat": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
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
  "class:sunglasses": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "class:vase": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "almost_always"
   }
  ],
  "class:gardening_gloves": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "balcony_table_y1",
    "chance": "usually"
   }
  ],
  "class:shopping_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "class:recipe_book": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "class:medication": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "medicine_cabinet_ba1",
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
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
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
  "class:hair_dryer": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
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
  "class:pen": [
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
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "class:mouse": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
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
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
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
    "to": 10,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "charger_marco": [
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
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
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
    "from": 7,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
