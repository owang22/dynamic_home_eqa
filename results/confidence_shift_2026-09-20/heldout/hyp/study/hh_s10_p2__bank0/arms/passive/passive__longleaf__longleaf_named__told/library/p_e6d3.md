# p_e6d3 — Yuki's weekday evening: entry dump at 18:00, dining table by 20:00

When Yuki arrives home at 18:00 on weekdays, her items cluster at the entry area: laptop and notebook at the entry hook, water bottle at the entry hook, keys at the entry table. She does not immediately sort these items to their "proper" locations (the office desk, the kitchen, etc.). By 20:00, she has moved to the dining area for the evening meal: the water bottle is at the dining table, and her phone is at the dining table as well. By 22:00, the water bottle is back at the dish rack (washed and dried), and the laptop and notebook remain at the entry hook — she does not move them to the office desk on weekday evenings.

This document differs from p_b2c8, which claims the entry is a "permanent chaos zone" where nothing gets sorted until Sunday. The evidence shows the water bottle does move from the entry hook to the dining table by 20:00, and back to the dish rack by 22:00 — a small but consistent sorting step. It differs from p_a92e, which has overlapping claims but a narrower focus on the water bottle and phone only.

Refutation: if the laptop or notebook are at the office desk (desk_o1) on weekday evenings (18:00–22:00), or if the water bottle is not at the dining table at 20:00 on weekdays, or if the water bottle is still at the entry hook at 22:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is at the entry hook on weekday evenings after she arrives home",
   "target": "laptop_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 22
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
   "claim": "Yuki's notebook is at the entry hook on weekday evenings (not sorted to the office desk)",
   "target": "notebook_yuki",
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
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
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
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "phone_yuki": [
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
