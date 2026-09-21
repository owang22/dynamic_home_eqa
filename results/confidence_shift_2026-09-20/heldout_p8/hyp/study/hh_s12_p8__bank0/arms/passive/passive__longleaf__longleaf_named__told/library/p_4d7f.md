# p_4d7f — Elena's driver commute: full kit out, coffee table overnight

Elena drives to her office in town; she does not cycle. The helmet and bike lock remain at the entry hook and entry table respectively, confirmed 7/7 days. Around 8 a.m. she leaves with her full work kit—laptop, notebook, pen, phone, keys, wallet, jacket, shoes—and returns around 5:30. Overnight the laptop is not consistently staged at the entry hook (as p_3a7c claims); the 00:00 passes show it split across entry hook, coffee table, and dresser, with the coffee table as the general resting spot when it isn't staged. The notebook stays at the bedroom desk overnight. The charger remains plugged in at the desk regardless of whether she's home.

Priya's glasses rest on the nightstand throughout the day. They are not anchored at the bedroom desk as p_b4e8, p_c5d9, and p_4c2a claim; the 6/7-day majority is nightstand, with only occasional desk or bed appearances. Priya's water bottle stays at the dish rack even during her weekday afternoon errands—she does not take it out.

This document is refuted if: the laptop is found at entry_hook_e1 on more than half of overnight passes; Priya's glasses are found at desk_b1 during midday on a majority of days; Elena's helmet is sighted out of the house on weekday mornings; or the water bottle is found out of the house during her errand window.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop rests at the coffee table overnight on a weekday, not staged at the entry hook",
   "target": "laptop_elena",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Elena's phone is out of the house during weekday work hours (she takes it to the office)",
   "target": "phone_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17
  },
  {
   "claim": "Priya's glasses are on the nightstand during midday, not at the bedroom desk",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Elena's notebook is at the bedroom desk overnight on a weekday",
   "target": "notebook_elena",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Priya's water bottle is at the dish rack during her weekday afternoon errands (she does not take it out)",
   "target": "water_bottle_priya",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 13,
   "to": 16
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "to": 17,
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
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "phone_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
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
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
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
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
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
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_elena": [
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
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
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
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ]
 }
}
```
