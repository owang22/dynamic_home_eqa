# p_9d3b — Hana's Evening Reset: items go to desk and kitchen, not the hook

The robot saw Hana's laptop, water bottle, pen, charger, handbag, hat, and jacket all at the entry hook — but only once each, and the 20:00 claims at the hook failed seven times. The entry hook is a *morning* staging area: Hana grabs her keys, jacket, handbag, and laptop at 7:30–8:00 and leaves. By the time she walks back in at 5:30, she hangs the jacket, sets the keys on the table, and the laptop goes to desk_b1 where she checks email or does a bit of work before bed. The water bottle goes to the kitchen counter (she refills it) or the desk. The pen goes in the desk drawer.

This document is distinguished from p_d3e8 (Entry Mess), which places all of Hana's items at the hook at 20:00, and from p_a9b4 (Kitchen Social Hub), which puts the laptop at the kitchen table. It predicts that by 19:00 on a weekday, the laptop is at desk_b1, the water bottle is at the kitchen counter, and the pen is at desk_b1. The entry hook at 20:00 holds only the jacket and hat (things you hang), not the laptop or water bottle.

What would refute it: a sighting of the laptop at the entry hook after 18:00 on a weekday, or the water bottle at the hook at 20:00. If Hana simply dumps everything at the hook and goes to the couch, this is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at desk_b1 at 20:00 on a weekday (not the entry hook)",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's water bottle is at the kitchen counter at 20:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's pen is at desk_b1 at 20:00 on a weekday",
   "target": "pen_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's jacket is at the entry hook at 20:00 on a weekday (hung up when she arrives)",
   "target": "jacket_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 22,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pen_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "charger_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 23,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
