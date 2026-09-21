# p_4c7a — — Contained dual-WFH; Marco's laptop and charger in hand 10–16 h; Omar's laptop and charger at coffee table 11–16 h; evening TV centred on coffee table (fork of p_a1b2)

This is a fork of p_a1b2 that keeps the "nothing leaves the house" claim (all personal items—keys, wallets, jackets, shoes—were sighted at their usual entry spots on 6/6 days with zero OUT_OF_HOUSE sightings) but corrects the work-hour object placements that the evidence has been contradicting. Marco's laptop was found at desk_b1 only 8 times in 38 weekday 9–17 h looks (30 empty), and his charger only 1 time in 38 looks (37 empty); the 21 weak-for and 27 weak-for tallies on the ON_PERSON forks confirm the desk is empty because the objects are in his hands. Omar's laptop and charger, by contrast, were sighted at coffee_table_l1 at 11:00, 13:00, and 16:00 on weekdays, indicating a midday migration to the living room. The evening TV sequence is also corrected: the blanket moves from couch to coffee_table by 22:00 (sighted there x2), and the remote goes to the coffee_table at 21:00 and to the floor by 22:00. What changed from the parent: laptop_marco and charger_marco gain ON_PERSON blocks for 10–16 h weekdays; laptop_omar and charger_omar gain coffee_table_l1 blocks for 11–16 h weekdays; the blanket and remote targets are restructured for the evening migration. What would refute this: any personal object sighted OUT_OF_HOUSE on a weekday, or Marco's laptop found resting flat on the desk surface during 10–16 h on more than a couple of occasions.

_(targets the fork left unstated are inherited from p_a1b2)_

```json
{
 "claims": [
  {
   "claim": "Marco's laptop is in his hands on his lap during core weekday work hours, not on the desk surface",
   "target": "laptop_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's charger is in his hands plugged into the laptop during core weekday work hours",
   "target": "charger_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Omar's laptop is on the living-room coffee table during his midday weekday work block",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 11,
   "to": 16
  },
  {
   "claim": "The blanket is on the coffee table during the later part of evening TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The remote is on the living-room floor after TV winds down",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "both",
   "from": 22,
   "to": 24
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
    "from": 10,
    "to": 16,
    "at": "ON_PERSON",
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
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
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
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
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
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "sometimes"
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
    "from": 21,
    "to": 23,
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
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
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
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
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
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 7.5,
    "at": "sink_ba_ba1",
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
    "from": 9,
    "to": 17.5,
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
    "to": 17.5,
    "at": "desk_o1",
    "chance": "almost_always"
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
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "almost_always"
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
    "from": 18.5,
    "to": 19.5,
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
    "chance": "almost_always"
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
    "from": 10,
    "to": 16,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "charger_omar": [
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
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
