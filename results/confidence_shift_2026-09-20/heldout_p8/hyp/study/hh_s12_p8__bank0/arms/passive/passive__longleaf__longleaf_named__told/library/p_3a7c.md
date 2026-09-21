# p_3a7c — Elena's overnight entry pack: work items staged at the hook

Elena is a full commuter who drives to her office. The decisive evidence is that her helmet and bike lock never leave the entry area during weekday work hours — she is not cycling. She packs her bag the night before, so her laptop, notebook, and pen sit at the entry hook overnight (0–7 h), ready to grab. In the 8 a.m. pass they are in transition (half still at the hook, half already at the coffee table or desk as she's getting ready). From roughly 8 to 17 they are OUT_OF_HOUSE with her. By the 18 h pass they are back at their evening resting spots: laptop at the coffee table, notebook and pen at the bedroom desk. Her phone, keys, wallet, hat, jacket, shoes, and backpack follow the same out-during-work pattern. This document separates itself from p_b4e8 and p_a3f7 by making the overnight staging at the entry hook an explicit, testable prediction (0–7 h) rather than leaving those hours to the statistical fallback, and by covering the full set of her personal items in one coherent routine.

What would refute it: if the laptop or notebook is found at the coffee table or desk during the 0–7 h window on multiple occasions (meaning she does not pack the night before), or if the helmet is ever OUT_OF_HOUSE during weekday work hours (meaning she cycles on some days).

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is staged at the entry hook overnight on a weekday",
   "target": "laptop_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Elena's notebook is staged at the entry hook overnight on a weekday",
   "target": "notebook_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Elena's phone is on the nightstand overnight on a weekday",
   "target": "phone_elena",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Elena's helmet stays at the entry hook during weekday work hours (she drives)",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's keys are out of the house during weekday work hours",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "notebook_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "phone_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "hat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "helmet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
