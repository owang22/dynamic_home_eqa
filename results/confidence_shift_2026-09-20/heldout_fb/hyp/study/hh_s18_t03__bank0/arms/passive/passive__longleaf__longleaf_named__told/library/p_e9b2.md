# p_e9b2 — Elena's full weekday commute: every personal object out 8:00–17:30, overnight at the entry and bedroom

Elena works in an office in town, leaving at about 8:00 and returning at about 17:30 on weekdays. She takes her laptop (laptop_elena), keys (keys_elena), backpack (backpack_elena), jacket (jacket_elena), headphones (headphones_elena), wallet (wallet_elena), sunglasses (sunglasses_elena), shoes (shoes_elena), hat (hat_elena), and scarf (scarf_elena) with her. All of these are OUT_OF_HOUSE from 08:00 to 17:30.

Overnight and in the early morning (02:00–07:00) and in the evening (18:00–23:00) her objects are at their home resting spots: keys and sunglasses on the entry table (entry_table_e1), backpack, headphones, and wallet on the entry floor (entry_floor_e1), laptop on the bedroom desk (desk_b1), jacket, hat, and scarf on the entry hook (entry_hook_e1), shoes at the entry hook or shoe rack.

On weekends both women sleep in and run errands around midday; Elena's objects follow the same weekend pattern (out midday, home the rest of the time).

What sets this apart from p_b8c2 (which claims nothing leaves the house and Elena's laptop is at desk_b1 all day): the per-object evidence shows laptop_elena at desk_b1 only at 03:00 (4/4 days) with zero 9–17 h looks at the desk, consistent with the laptop being out. The 03:00 and 18:00 sightings of her keys, backpack, and headphones at the entry confirm they are home only when she is home.

Refutation: if laptop_elena is found at desk_b1 at 10:00 or 14:00 on a weekday, the commute is wrong. If keys_elena are at the entry table at 09:00, the out-of-house block fails.

```json
{
 "claims": [
  {
   "claim": "Elena's keys are out of the house at 09:00 on weekdays",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Elena's laptop is out of the house at 14:00 on weekdays",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Elena's backpack is out of the house at 10:00 on weekdays",
   "target": "backpack_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Elena's keys are on the entry table at 03:00",
   "target": "keys_elena",
   "expect": "entry_table_e1",
   "days": "both",
   "from": 2,
   "to": 7
  }
 ],
 "targets": {
  "laptop_elena": [
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
  "backpack_elena": [
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
  "headphones_elena": [
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
  "wallet_elena": [
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
  "sunglasses_elena": [
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
  "shoes_elena": [
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
  "scarf_elena": [
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
  "phone_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "tablet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "yoga_mat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
