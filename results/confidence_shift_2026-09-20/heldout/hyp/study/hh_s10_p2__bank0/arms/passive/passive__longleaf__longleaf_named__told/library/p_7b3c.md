# p_7b3c — Yuki's weekday commute: ten items leave at 8:00, return at 18:00

Yuki leaves for her office at roughly 8:00 on weekdays, carrying her laptop, notebook, keys, jacket, shoes, backpack, water bottle, sunglasses, wallet, and phone. The robot sees none of these ten items anywhere in the house between 08:00 and 18:00 on weekdays — every look at their usual resting spots comes up empty. When she returns at 18:00, the items reappear: laptop and notebook at the entry hook, keys and wallet at the entry table, jacket at the entry hook, shoes at the shoe rack, backpack at the entry hook, water bottle at the entry hook (shifting to the dining table by 20:00 for the meal), sunglasses at the entry table, and phone at the dining table or coffee table.

On weekends the pattern changes: the laptop and notebook move to the bedroom desk (desk_b1) from about 12:00 through 22:00, where Yuki does her work and study sessions. All other items stay at their entry or kitchen resting spots all day.

This document differs from p_f8b2 in that the out-of-house window is 8:00–18:00 (not 9:00–16:00) and explicitly covers all ten items rather than a subset. It differs from p_3e7a, which focuses on the no-cycling claim and only tracks the helmet and laptop. It differs from p_a1b2, which predicts Yuki cycles and therefore expects her helmet and bike lock to be out of the house.

Refutation: if any of the ten items is sighted inside the house during 08:00–18:00 on a weekday, or if the laptop and notebook are not at desk_b1 during weekend afternoons (12:00–22:00).

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is out of the house during her work hours on weekdays",
   "target": "laptop_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 18
  },
  {
   "claim": "Yuki's keys are out of the house during her work hours on weekdays",
   "target": "keys_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 18
  },
  {
   "claim": "Yuki's shoes are out of the house during her work hours on weekdays",
   "target": "shoes_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 18
  },
  {
   "claim": "Yuki's laptop is at the bedroom desk during weekend afternoons",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 12,
   "to": 22
  },
  {
   "claim": "Yuki's water bottle is at the dining table during the 20:00 meal on weekdays",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  }
 ],
 "targets": {
  "laptop_yuki": [
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
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "notebook_yuki": [
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
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
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
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_yuki": [
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
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_yuki": [
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
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
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
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
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
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_yuki": [
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
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "phone_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ]
 }
}
```
