# p_5da3 — Yuki's Laptop Never Leaves: Pure work-from-home, no café

Yuki's laptop, charger, and water bottle are at desk_b1 at all times on weekdays (and most of the time on weekends). Yuki never works from a café. The laptop is the anchor of Yuki's workday. On weekends, the laptop may be closed and the desk cleared, but the laptop stays in the bedroom. The charger stays plugged in at the desk.

What sets this hypothesis apart: laptop_yuki is at desk_b1 on ALL weekdays, including Tuesday and Thursday. This directly contradicts p_c9d4 where the laptop is OUT_OF_HOUSE on Tue/Thu. The charger is also always at the desk.

What would refute it: laptop_yuki sighted OUT_OF_HOUSE or on a person on any weekday.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is at the desk on Tuesday midday",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Yuki's laptop is at the desk on Thursday midday",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Yuki's charger is at the desk on Tuesday midday",
   "target": "charger_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Yuki's water bottle is at the desk on Thursday midday",
   "target": "water_bottle_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "laptop_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "charger_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "pen_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "tablet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
