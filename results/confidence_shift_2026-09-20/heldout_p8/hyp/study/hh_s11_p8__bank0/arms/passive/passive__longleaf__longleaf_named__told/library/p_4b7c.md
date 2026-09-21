# p_4b7c — Weekend Both-Home: Blanket on the Bed, Pen at the Desk, Medication in the Cabinet

Hana and Priya are both home all day on Saturday and Sunday. Neither goes to work, so the objects that travel with them on weekdays stay put. The weekend routine is looser: Hana sleeps in, does errands around midday, and spends afternoons at her desk or in the living room. Priya takes a late-morning walk, tends the dog, and settles into the living room by early afternoon. Because both residents are present and the house is "lived in" rather than "transitioned through," objects rest in their true home positions instead of the in-between spots the weekday passes catch.

What sets this document apart: on weekends the shared blanket is on **bed_b1** (not the armchair), Hana's pen is at **desk_b1** (not the entry table or hook), Priya's medication is in the **medicine_cabinet_ba1** (not the coffee table), Priya's water bottle is at the **dish_rack_k1** (not the dining table), Hana's water bottle is also at the **dish_rack_k1**, the remote stays on the **tv_stand_l1** all day (it never drops to the floor), Hana's book is on the **bookshelf_l1** (not the nightstand), the cutting board rests on the **counter_k1** (not the sink), and Priya's plate is in the **cupboard_k1** overnight (not left on the dining table). The laundry basket and Hana's towel are in **bedroom_floor_b1**, suggesting weekend laundry is done in the bedroom. Hana's jacket sits on the **entry_floor_e1** rather than the hook, and her handbag hangs on the **entry_hook_e1** all day because she doesn't leave for a shift.

This document is refuted if, on a weekend day, the blanket is found on the armchair or couch, the pen is at the entry table, the medication is on the coffee table, the water bottles are at the dining table, or the remote is on the living room floor.

```json
{
 "claims": [
  {
   "claim": "The shared blanket is on the bed on weekend mornings, not on the armchair",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 8,
   "to": 16
  },
  {
   "claim": "Hana's pen is at her desk all day on weekends, not at the entry table",
   "target": "pen_hana",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 8,
   "to": 16
  },
  {
   "claim": "Priya's medication is in the medicine cabinet on weekends, not on the coffee table",
   "target": "medication_priya",
   "expect": "medicine_cabinet_ba1",
   "days": "weekend",
   "from": 8,
   "to": 16
  },
  {
   "claim": "Priya's water bottle is at the dish rack on weekends, not on the dining table",
   "target": "water_bottle_priya",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 8,
   "to": 16
  },
  {
   "claim": "The remote stays on the TV stand all day on weekends and never drops to the floor",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 8,
   "to": 16
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "pen_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "medication_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "medicine_cabinet_ba1",
    "chance": "usually"
   }
  ],
  "tablet_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "bedroom_floor_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "desk_b2",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ],
  "glass_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "counter_k1",
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
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "laundry_basket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "towel_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "book_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "sometimes"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "chair_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "magazine_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "hat_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "sometimes"
   }
  ],
  "shoes_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "shoe_rack_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 16,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "sometimes"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "class:skincare": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "class:plant_pot": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
