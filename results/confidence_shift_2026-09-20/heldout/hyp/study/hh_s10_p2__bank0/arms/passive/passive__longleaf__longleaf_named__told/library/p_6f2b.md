# p_6f2b — No weekday cycling: both helmets and bike locks stay home all day

Every weekday pass from 00:00 to 22:00 finds Yuki's helmet at entry_hook_e1 (11/11 during 9–17h) and Omar's helmet at entry_hook_e1 (11/11 during 9–17h). Both bike locks sit at entry_table_e1 (11/11 each during 9–17h). Neither resident cycles to work on weekdays. Yuki drives or takes transit (her full bag of items leaves at 8:00 and returns at 18:00); Omar walks or drives to his afternoon shift (his work items — handbag, jacket, lunchbox, notebook, pen, scarf, shoes, wallet, keys — are at the entry area through 12:00, then disappear by 14:00).

This document refutes any model in which a helmet or bike lock is OUT_OF_HOUSE on a weekday. It is confirmed by the 11/11 finds at the entry hook/table during work hours. Cycling, if it happens, is a weekend-only activity.

```json
{
 "claims": [
  {
   "claim": "Omar's helmet is at the entry hook during his work shift on weekdays (he does not cycle to work)",
   "target": "helmet_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Yuki's helmet is at the entry hook during her work hours on weekdays (she does not cycle to work)",
   "target": "helmet_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's bike lock is at the entry table during his work shift on weekdays",
   "target": "bike_lock_omar",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Yuki's bike lock is at the entry table during her work hours on weekdays",
   "target": "bike_lock_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "helmet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "helmet_yuki": [
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
  ],
  "bike_lock_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "handbag_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.7,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ]
 }
}
```
