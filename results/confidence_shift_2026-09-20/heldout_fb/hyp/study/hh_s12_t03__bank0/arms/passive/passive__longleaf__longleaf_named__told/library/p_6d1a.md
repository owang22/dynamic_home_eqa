# p_6d1a — Elena's weekday: out 8–17:30, kit at the entry, laptop gone

Elena commutes to her office in town every weekday, leaving around 8:00 and returning around 17:30. Her laptop, keys, and wallet are out of the house during work hours. Her cycling kit (helmet, bike lock, jacket, shoes) stays at the entry: the helmet and jacket at the hook, the bike lock at the entry table, the shoes on the rack. The backpack also stays at the entry hook (she grabs it as she leaves and it's back by the time the robot looks at 18:00). On weekends she is home: the bike gear stays put, the laptop is at the coffee table or entry, and she does midday errands. Priya is home most of the day on weekdays.

This document differs from p_c3d4, which says Elena works from desk_o1 on Monday and Wednesday (laptop at the office desk those days). The evidence here is that the laptop is at entry_hook_e1 at 03:00 on all weekday mornings and at coffee_table_l1 at 18:00, consistent with a full commute. It also differs from p_7ef3 and p_d2f8, which focus on the cycling gear but are sparse on the laptop and work items.

What would refute it: the laptop found at desk_o1 during 9–17 on a weekday; Elena's keys found at the entry table during 10–15 on a weekday; the helmet found at the entry during 9–17 on a weekday (she'd be wearing it on the bike).

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is out of the house on weekdays during work hours",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's keys are out of the house on weekdays during work hours",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's wallet is out of the house on weekdays during work hours",
   "target": "wallet_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Elena's helmet stays at the entry hook on a weekend since she does not commute",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Elena's backpack stays at the entry hook on weekdays",
   "target": "backpack_elena",
   "expect": "entry_hook_e1",
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
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "chance": "usually"
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
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
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
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
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
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "sometimes"
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
  "jacket_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "hat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
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
  ]
 }
}
```
