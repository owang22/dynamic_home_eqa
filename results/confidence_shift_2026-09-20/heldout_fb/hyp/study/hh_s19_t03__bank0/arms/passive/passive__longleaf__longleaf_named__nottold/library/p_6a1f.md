# p_6a1f — Marco's laptop and charger stay at his desk, even on office days

Marco's laptop is at desk_b1 on 5/5 sighted days (03:00 ×3, 18:00 ×1, weekend 03:00 ×1). His charger is at desk_b1 on 4/5 days. The one anomaly is a weekday 10:00 sighting of the laptop at coffee_table_l1, which is consistent with a WFH day (p_e5f6's hybrid pattern) or a brief morning use before heading out. The two weekday 9–17h looks at desk_b1 that found nothing are the key tension: they suggest the laptop is occasionally NOT at the desk during the workday, but the overwhelming pattern (5/5 days) is that it stays home.

This document differs from p_8c2d (Marco takes his laptop to the office) by asserting the laptop NEVER leaves the house on weekdays. It differs from p_3a7f and p_f3a7 (which also say it stays home) by adding the charger as a co-traveller and by explicitly placing the laptop at the coffee table on the rare WFH morning. The 10:00 coffee-table sighting is the seed for that block.

Refutation: if Marco's laptop is sighted out of the house on a weekday, or if it is consistently at the coffee table during 9–17h (meaning he's WFH most days), or if his charger is not at the desk at 03:00.

```json
{
 "claims": [
  {
   "claim": "Marco's laptop is at his desk at 03:00 overnight",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "both",
   "from": 3,
   "to": 3.5
  },
  {
   "claim": "Marco's laptop is at his desk when he returns home at 18:00",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 18.5
  },
  {
   "claim": "Marco's charger is at his desk at 03:00 overnight",
   "target": "charger_marco",
   "expect": "desk_b1",
   "days": "both",
   "from": 3,
   "to": 3.5
  },
  {
   "claim": "Marco's sketchbook is on the coffee table during the late evening",
   "target": "sketchbook_marco",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  }
 ],
 "targets": {
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "rarely"
   }
  ],
  "charger_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pencil_case_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "rarely"
   }
  ],
  "sketchbook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
