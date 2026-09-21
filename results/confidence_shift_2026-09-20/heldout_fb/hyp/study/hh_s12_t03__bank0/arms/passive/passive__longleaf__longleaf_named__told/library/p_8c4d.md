# p_8c4d — Weekend home: both in, the slower clock

On both Saturday and Sunday the fundamental shift is that Elena is home. Her commute objects—laptop, backpack, helmet, bike lock, jacket, shoes, keys, wallet—remain at their entry or desk locations all day. Priya's rhythm loosens: her walk moves from 7-8 to 10-11, her afternoon errands are lighter or absent, and she spends more time with guitar, yoga, or reading in the living room. The kitchen is busier: Elena bakes or cooks, and the two of them share meals at the dining table or kitchen table. The living room is the social centre: TV, guitar, board games, the dog lounging.

What sets this apart from the weekday documents: no object is OUT_OF_HOUSE with Elena during 9-17. The office desk (desk_o1) is inert. The bedroom desk (desk_b1) holds Elena's laptop and charger when she does casual work. Priya's yoga mat comes out later (10-12) than on weekdays. The dog food bag stays on the pantry shelf longer because Elena handles the evening feeding (she is home, so the 19-21 feeding is her, not Priya's).

Refutation: if Elena's laptop or backpack is sighted out of the house on a weekend, or if Priya's walk objects (sunglasses, water bottle) are out before 9:30 on a weekend, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is at the coffee table on a weekend midday because she is home",
   "target": "laptop_elena",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's yoga mat is on the living-room floor during her late-morning weekend yoga",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Priya's guitar is on the living-room floor during her weekend afternoon practice",
   "target": "guitar_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Elena's bike lock stays at the entry table on a weekend since she does not cycle to work",
   "target": "bike_lock_elena",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 8,
   "to": 20
  },
  {
   "claim": "Priya's sunglasses are out of the house during her weekend morning walk",
   "target": "sunglasses_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 10,
   "to": 12
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "charger_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "helmet_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "keys_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 8,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
