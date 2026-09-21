# p_2f8c — Elena's Saturday: morning bake, midday errands, evening host

Elena's weekend routine per her profile: sleeps in, errands around midday, home the rest of the day. With friends coming in the evening, she bakes in the morning (her stated hobby) and then drives out for errands around noon. This means the baking tray and mixing bowl are at the kitchen counter between 9 and 12, her backpack/keys/wallet are out of the house between 12 and 15, and her laptop stays at the coffee table all day (no work commute). In the afternoon she returns and preps dinner, so kitchen items (cutting board, pan, knife) are at the counter. This document is distinct from the weekday commuter documents because nothing is staged at the entry hook overnight and the laptop never leaves the house.

What would refute it: if the baking tray is still in the pantry at 10:00 on Saturday (no baking), if the backpack is at the entry hook at 13:00 (no errands), or if the laptop is at the office desk (she went in to work anyway).

```json
{
 "claims": [
  {
   "claim": "The baking tray is at the kitchen counter on Saturday morning while Elena bakes",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Elena's backpack is out of the house on Saturday midday during her errand run",
   "target": "backpack_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Elena's laptop is at the coffee table on Saturday morning (home, not at work)",
   "target": "laptop_elena",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Elena's keys are out of the house on Saturday midday (driving errands)",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 15
  }
 ],
 "targets": {
  "baking_tray_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 13,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 13,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 11,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 11,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 11,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "phone_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 11,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
