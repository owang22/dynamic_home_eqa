# p_b7c2 — Yuki's Midday Escape: Lunch out 12 to 14 on weekdays

Nora commutes as usual (out 8:00–17:30). Yuki works from home but takes a regular lunch break outdoors, leaving the house around 12:00 and returning by 14:00 on weekdays. During that window, Yuki's keys, wallet, jacket, hat, scarf, and shoes are all OUT_OF_HOUSE. By 14:00 they are back on the entry hook and table. The 18:00 walkthrough caught Yuki already home, which is why all those items were at the entry.

What sets this hypothesis apart: the entry hook is bare of jacket_yuki, hat_yuki, scarf_yuki, and shoes_yuki between 12:00 and 14:00 on weekdays, and keys_yuki and wallet_yuki are absent from the entry table in that window.

What would refute it: jacket_yuki or keys_yuki sighted in the house at 12:00 or 13:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Yuki's keys are out of the house at midday on weekdays",
   "target": "keys_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Yuki's jacket is out of the house at midday on weekdays",
   "target": "jacket_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Yuki's shoes are out of the house at midday on weekdays",
   "target": "shoes_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Yuki's wallet is out of the house at midday on weekdays",
   "target": "wallet_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 12,
   "to": 14
  }
 ],
 "targets": {
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
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "hat_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "scarf_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "laptop_yuki": [
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
    "to": 18,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
