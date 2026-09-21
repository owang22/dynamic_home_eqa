# p_c5d7 — Hana's 18:00 Entry Drop, 19:00 Kitchen Table, 22:00 Desk

Hana arrives home at 18:00 and drops her laptop, pen, water bottle, and charger at the entry hook. This is a brief stop — by 19:00 the water bottle has moved to the kitchen table (for dinner), and by 22:00 the laptop and pen are at desk_b1 (evening work session) while the charger migrates to the nightstand (overnight charging). The p_d3e8 document claimed the water bottle stays at the entry hook from 18:00 to 22:00, but sightings show it at the kitchen table by 19:00–20:00. The laptop's entry-hook stop is real but brief (18:00–21:00), after which it goes to the desk. If the water bottle is found at the entry hook after 19:30, or the laptop is still at the entry hook after 21:30, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's water bottle is on the kitchen table at 20:00 on a weekday (moved from entry after dinner starts)",
   "target": "water_bottle_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Hana's laptop is at desk_b1 at 22:30 on a weekday (evening work session)",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 22,
   "to": 23.5
  },
  {
   "claim": "Hana's charger is at the nightstand at 23:00 on a weekday (overnight charging)",
   "target": "charger_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22.5,
   "to": 24
  },
  {
   "claim": "Hana's water bottle is at the entry hook at 18:15 on a weekday (just arrived, brief stop)",
   "target": "water_bottle_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 18.5
  }
 ],
 "targets": {
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "pen_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   }
  ],
  "charger_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 18,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
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
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
