# p_9c1b — Omar's weekday departure: seven items leave at 13:00, return at 23:00

Omar leaves for his afternoon-to-night shift at approximately 13:00–14:00 on weekdays, taking his keys, jacket, shoes, scarf, lunchbox, handbag, and wallet. The robot sees none of these seven items in the house between roughly 13:00 and 23:00 on weekdays. His helmet and bike lock, however, remain at the entry hook and entry table respectively throughout the entire day — he drives to work, not cycles.

When Omar returns at 23:00, the seven items reappear at their entry spots. On weekends, all items stay in the house. The scarf shifts from the entry hook to the wardrobe on weekends (it is not needed for the work commute). The lunchbox moves from the entry hook to the kitchen cupboard on weekends (no work shift to pack for). The handbag and wallet remain at the entry hook and entry table.

This document differs from p_3e7a, which focuses on the no-cycling claim and tracks only the helmet and bike lock. It differs from p_7d6c, which covers Omar's morning routine (6:00–13:30) but does not specify which items leave with him. The key prediction is that seven specific items are OUT_OF_HOUSE from 13:00 to 23:00 on weekdays, while the helmet and bike lock remain home.

Refutation: if any of the seven items is sighted inside the house during 14:00–22:00 on a weekday, or if the helmet or bike lock are found out of the house on weekdays.

```json
{
 "claims": [
  {
   "claim": "Omar's keys are out of the house during his work shift on weekdays",
   "target": "keys_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Omar's jacket is out of the house during his work shift on weekdays",
   "target": "jacket_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Omar's lunchbox is in the kitchen cupboard on weekends (no work shift)",
   "target": "lunchbox_omar",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 12,
   "to": 22
  },
  {
   "claim": "Omar's helmet stays at the entry hook during his work shift on weekdays (he drives, not cycles)",
   "target": "helmet_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Omar's scarf is in the wardrobe on weekends",
   "target": "scarf_omar",
   "expect": "wardrobe_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "keys_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "scarf_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "handbag_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "helmet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
