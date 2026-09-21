# p_7e5b — Omar's tablet: nightstand overnight, kitchen table mid-morning, chair in the evening

Omar's tablet follows a three-position arc on weekdays. Overnight and early morning (03:00, 09:00 passes), it is at the bedroom nightstand (2 sightings each hour), not the kitchen chair as p_3e8d and p_e5f6 predict. By mid-morning (10:00 pass), it has moved to the kitchen table (2 sightings) — Omar is home before his 13:40 departure and is using the tablet at the kitchen table. By 18:00 (when he is at work), it is at the kitchen chair (1 sighting). The 09:00 pass also shows 1 sighting at the kitchen table, suggesting the move from nightstand to kitchen table happens around 09:00–10:00.

What sets this apart: p_e5f6 places the tablet at chair_k1 during the morning (7:00–13:00), but the 09:00 and 10:00 passes show it at nightstand_b1 and kitchen_table_k1, not chair_k1. p_3e8d places it at kitchen_table_k1 at 10:00 (matching) but at chair_k1 overnight (not matching — it is at nightstand_b1). p_7a3f and p_4e91 place it at chair_k1 on weekday evenings (matching the 18:00 pass). This document corrects the overnight and early-morning position to nightstand_b1.

What would refute it: the tablet consistently at chair_k1 at 03:00 or 09:00 on weekdays, or at the kitchen table at 03:00.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 03:00 on a weekday (overnight resting spot)",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 1,
   "to": 6
  },
  {
   "claim": "Omar's tablet is at the kitchen table at 10:00 on a weekday (mid-morning use while he is home)",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9.5,
   "to": 13
  },
  {
   "claim": "Omar's tablet is at the kitchen chair at 18:00 on a weekday (he is at work, tablet rests in the chair)",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 14,
   "to": 23
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
