# p_b8c2 — Yuki's work stuff goes to the office desk, not the entry hook

When Yuki walks in at 17:30 she hangs her jacket on the entry hook and sets her water bottle on the entry table, but she does not leave her laptop and notebook there. She carries them straight to the office desk in the home office, where she might do a short evening review, file notes, or simply have them ready for the next morning. The entry hook is a brief staging point for the jacket only; the water bottle gets moved to the kitchen within twenty minutes.

This document is a direct counter to p_b2c8's "entry chaos zone" hypothesis. p_b2c8's claims that the laptop and notebook sit at the entry hook on weekday evenings have each been scored against 6 times and for only 1. The objects are being sorted. Yuki works in an office in town, so on most weekdays her laptop is out of the house from about 8:00 to 17:30; in the evening it lives at the office desk. What would refute this: a sighting of the laptop or notebook at the entry hook after 18:00 on a weekday, or the laptop found in the bedroom rather than the office.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is at the office desk at 20:00 on a weekday after she has brought it home from the office",
   "target": "laptop_yuki",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Yuki's notebook is at the office desk at 20:00 on a weekday, kept with the laptop",
   "target": "notebook_yuki",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Yuki's laptop is out of the house at 10:00 on a weekday because she took it to the office",
   "target": "laptop_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17
  },
  {
   "claim": "Yuki's jacket is at the entry hook at 19:00 on a weekday, hung up on arrival",
   "target": "jacket_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "laptop_yuki": [
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
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "notebook_yuki": [
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
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "jacket_yuki": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 22,
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
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
