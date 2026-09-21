# p_c5d9 — Elena's full work kit out; charger and helmet stay home

This document isolates the question of exactly which of Elena's objects leave the house on a weekday and which stay. The evidence is unambiguous: her laptop, notebook, pen, backpack, keys, wallet, hat, jacket, shoes, and water bottle are all absent from the house between roughly 8:00 and 17:30 on weekdays. Her phone is at the nightstand in the evening, briefly at the entry table around 8:00, then out with her.

What stays: the phone charger at desk_b1 (found 6/6 times during 9–17h), the helmet at the entry hook (found 6/6), the bike lock at the entry table (found 6/6), the umbrella at the entry floor (found 6/6), the hair dryer at the bathroom shelf, the toiletry bag at the dresser, the skincare at the nightstand, and the towel at the bathroom shelf. These are home-base objects that do not travel with her.

The laptop, when in the house, rests at the coffee table (not the desk). It is seen at coffee_table_l1 at 00:00–08:00 and 18:00–22:00, with occasional sightings at entry_hook_e1 (perhaps she picks it up from the entry on the way out). The notebook and pen follow the same pattern: desk_b1 at night, absent during the workday.

On weekends the picture changes: Elena cycles (helmet and bike lock go out), bakes (baking tray at the counter), and the laptop stays at the coffee table.

What sets this hypothesis apart: the explicit full list of objects that go OUT (ten items) versus the explicit list that STAYS (charger, helmet, bike lock, umbrella). The laptop's in-house resting spot is coffee_table_l1, not desk_b1 or desk_o1.

Refutation: if any of the ten "out" objects are found inside the house during 9–17h on a weekday; if the charger, helmet, or bike lock are found out of the house on a weekday; if the laptop is found at desk_b1 or desk_o1 during its in-house hours.

```json
{
 "claims": [
  {
   "claim": "Elena's keys are out of the house during weekday work hours",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's charger is at desk_b1 during weekday work hours",
   "target": "charger_elena",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's helmet is at the entry hook during weekday work hours",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's phone is at the nightstand in the early morning",
   "target": "phone_elena",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 0,
   "to": 7
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
    "chance": "almost_always"
   }
  ],
  "pen_elena": [
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
  "shoes_elena": [
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
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
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
  "phone_elena": [
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 8.5,
    "at": "entry_table_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "helmet_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "umbrella_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "toiletry_bag_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dresser_b1",
    "chance": "usually"
   }
  ],
  "skincare_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
