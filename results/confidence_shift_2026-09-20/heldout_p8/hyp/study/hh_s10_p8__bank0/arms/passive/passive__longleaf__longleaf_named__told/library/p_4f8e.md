# p_4f8e — Yuki's laptop and notebook rest at desk_b1 in the evening and all weekend

Yuki brings her laptop and notebook home from the office each weekday evening. The 18:00 patrol catches them at the entry hook (she sets them down on arrival), but by the 19:00–22:00 window they have migrated to the bedroom desk (desk_b1), where they stay overnight. On weekends the pattern is even stronger: the 16:00 patrol finds both objects at desk_b1 on 2 out of 2 occasions, and the overnight position is split between the entry hook and the desk (she sometimes works late into the night and leaves them at the desk). During weekday work hours (9–17h) the laptop is out of the house — four looks at the entry hook in that window found nothing, supporting an OUT_OF_HOUSE block. Neither object is ever sighted at desk_o1 (the office desk), which contradicts the documents that place Yuki's work there. The notebook follows the laptop exactly: same two receptacles, same timing.

What sets this apart: p_b2c8 puts the laptop at the entry hook all evening (18–22h) and has accumulated 6 against on that claim; p_b8c2 puts it at desk_o1 and has 2 against. This document says desk_b1 for the evening and the full weekend, and OUT_OF_HOUSE for weekday 9–17h (narrowed from 8–17h to avoid the 08:00 patrol that catches it before Yuki leaves).

Refutation: if the laptop is found at the entry hook at 20:00–22:00 on multiple weekday evenings, or at desk_o1 at any time, or at the entry hook on a weekend afternoon, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is at the bedroom desk at 20:00 on a weekday evening after she has moved it from the entry",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 19,
   "to": 23
  },
  {
   "claim": "Yuki's notebook is at the bedroom desk at 20:00 on a weekday evening, kept with the laptop",
   "target": "notebook_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 19,
   "to": 23
  },
  {
   "claim": "Yuki's laptop is at the bedroom desk on a weekend afternoon during her work or journaling session",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Yuki's laptop is at the entry hook overnight on a weekday, hung up from the previous evening",
   "target": "laptop_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 0,
   "to": 6
  }
 ],
 "targets": {
  "laptop_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "desk_b1",
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
  "notebook_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
