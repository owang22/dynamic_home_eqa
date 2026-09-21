# p_6d1a — Weekend: no commute, all gear stays home; midday errand takes Yuki out briefly

On weekends neither resident commutes to work. Both helmets stay at the entry hook, both bike locks stay at the entry table, and both sets of keys stay at the entry (table in the morning, floor in the afternoon for Yuki). Omar's jacket, shoes, and handbag all remain at the entry all day. The only time anyone leaves is the midday errand: Yuki's shoes briefly appear at the entry floor at 14:00 on Saturday (she was out), and Omar's shoes are at the shoe rack at 12:00 (he stepped out). But this is a 30-minute errand, not a 9-hour work day, so the "out of house" pattern that dominates weekdays simply does not apply.

This document's key claim is the *absence* of the weekday out-of-house pattern: on weekends, the helmets, bike locks, keys, jackets, and shoes are all present in the house at all hours. The midday errand is brief and does not remove items for the full 8-17h or 14-22h windows that the weekday documents predict.

This document is refuted if a helmet or bike lock is sighted out of the house on a weekend, or if Yuki's keys are absent from the entry for more than an hour on a weekend.

```json
{
 "claims": [
  {
   "claim": "Omar's helmet is at the entry hook all day on weekends (no cycling commute)",
   "target": "helmet_omar",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Yuki's bike lock is at the entry table all day on weekends (no cycling commute)",
   "target": "bike_lock_yuki",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Yuki's keys are on the entry floor in the weekend afternoon (she is home, not at work)",
   "target": "keys_yuki",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Omar's jacket is at the entry hook all day on weekends (no work shift)",
   "target": "jacket_omar",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "helmet_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "helmet_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "keys_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "jacket_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "shoes_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "handbag_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "backpack_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
