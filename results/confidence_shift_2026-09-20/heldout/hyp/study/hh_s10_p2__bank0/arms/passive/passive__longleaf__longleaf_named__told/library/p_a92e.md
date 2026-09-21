# p_a92e — Yuki's post-work evening: entry dump, kitchen, dining, living

Yuki arrives home around 17:30 on weekdays and dumps her bag, laptop, water bottle, and keys at the entry. She does not immediately sort them into their "proper" places. The laptop stays at the entry hook for the rest of the evening (the 18:00 pass shows it there 4×; it is not seen at the office desk or the coffee table in the evening). The water bottle goes from the entry hook to the dining table for dinner (20:00) and then to the dish rack by 22:00. Her keys settle on the entry table.

The evening sequence is: 17:30–18:30 entry (dumping), 18:00–20:00 kitchen (cooking), 20:00–21:00 dining (meal), 22:00–24:00 living (TV), 00:00 bedroom (sleep). This is a *progression*, not a single resting spot.

This differs from p_b2c8 (entry chaos: everything stays at the entry all evening) in that the water bottle and phone *do* move to the dining table at 20:00 and the water bottle ends up at the dish rack by 22:00. It agrees with p_b2c8 that the laptop and notebook remain at the entry hook.

Refuted if the robot finds the water bottle still at the entry hook at 20:00 (she did not move it to the table) or finds the laptop at the office desk at 20:00 (she sorted it in).

```json
{
 "claims": [
  {
   "claim": "Yuki's water bottle is at the entry hook at 18:00 on a weekday (just arrived, not yet moved)",
   "target": "water_bottle_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  },
  {
   "claim": "Yuki's water bottle is at the dining table during the 20:00 meal on weekdays",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Yuki's laptop is still at the entry hook at 20:00 on a weekday evening (she has not sorted it to the office desk)",
   "target": "laptop_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Yuki's phone is at the dining table during the 20:00 meal on weekdays",
   "target": "phone_yuki",
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
    "to": 17.5,
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
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
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
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
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
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "phone_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
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
