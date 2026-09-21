# p_7a3c — Saturday at Home; Guitar, Yoga, and Board Games

It is Saturday. The message says "we're off our usual routine and around the house more," and the evidence from the four weekday passes confirms both residents are home all day with no work departure. Hana, still recovering from Friday's sick day, keeps to the bedroom through the morning and drifts into the living room by midday; her guitar stays on the bedroom floor where the robot has found it on all four sighted days. Priya follows her weekend pattern: a late-morning walk (roughly 10:00–11:00, later than her weekday 7:00–9:00 walk), yoga in the early morning with the mat on the living-room floor, photography in the afternoon, and board games in the evening. The puzzle box, which sits on the bookshelf every weekday pass, comes out to the dining table for the evening game.

This document sets itself apart by modelling the *weekend* specifically: Priya's walk shifts to late morning, Hana's tablet moves from the desk to the bed and then the coffee table (she is not working), the entry set stays put because nobody is commuting, and the evening brings a shared TV-and-board-game session with the remote at the coffee table. It also corrects two persistent errors: medication_priya lives in the medicine cabinet, not the coffee table, and tablet_priya spends its daytime hours on the bedroom floor, not the nightstand.

What would refute this: Hana seen out of the house in the afternoon (she is still recovering); Priya's walk at 7:00 instead of 10:00; the puzzle box remaining on the bookshelf all evening; the remote staying on the TV stand or the floor rather than moving to the coffee table for TV.

```json
{
 "claims": [
  {
   "claim": "Priya's yoga mat is unrolled on the living room floor for her weekend morning yoga",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 6,
   "to": 7
  },
  {
   "claim": "The puzzle box is out on the dining table for the evening board-game session",
   "target": "puzzle_box_shared",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 19,
   "to": 23
  },
  {
   "claim": "The remote is at the coffee table during the weekend evening TV session",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Priya's keys are out of the house during her late-morning weekend walk",
   "target": "keys_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 10,
   "to": 11
  },
  {
   "claim": "Hana's guitar stays on the bedroom floor all weekend",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 6,
    "to": 7,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "tablet_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 18,
    "at": "bedroom_floor_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "medication_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "medicine_cabinet_ba1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
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
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "notebook_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ],
  "watering_can_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
    "chance": "almost_always"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
