# p_5e9b — Yuki's evening items migrate from the entry to the dining table, then to the sink

Yuki's personal items follow a clear evening path on weekdays. They sit at the entry (hook, table, floor) through the morning and afternoon, but when she comes home at 5:30 and sits down to dinner she brings her water bottle to the dining table. The Tuesday evidence traces the water bottle through all three stages: entry hook at 18:00, dining table at 20:00, sink at 22:00. The laptop and notebook may also be brought to the table or to the living room, but the water bottle's migration is the most clearly confirmed.

This directly contradicts p_b2c8, which claims the water bottle, laptop, and notebook all remain at the entry hook through the evening (19–23 h). The water bottle clearly moves to the dining table for the meal and then to the sink for washing. It also differs from p_4e91 and p_7a3f, which focus on the morning commute and do not address the evening migration. The entry hook is a morning-and-afternoon resting place, not an all-day one.

Refutation: if the water bottle is found at the entry hook at 20:00 on a weekday (not at the dining table), or if it is found at the dining table at 18:00 (before the meal has started), or if the laptop is consistently at the dining table rather than the entry hook.

```json
{
 "claims": [
  {
   "claim": "Yuki's water bottle is at the dining table during the weekday meal",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Yuki's water bottle is still at the entry hook before the weekday meal",
   "target": "water_bottle_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Yuki's water bottle is at the sink after the weekday meal",
   "target": "water_bottle_yuki",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
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
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "notebook_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "backpack_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "wallet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:razor": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
