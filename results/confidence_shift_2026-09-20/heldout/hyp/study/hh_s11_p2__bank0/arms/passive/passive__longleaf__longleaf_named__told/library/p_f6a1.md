# p_f6a1 — Duster and Vacuum at the Coffee Table; a Standing Living-Room Presence

The worst-objects list flags duster_shared (predicted storage_shelf_s1, actually coffee_table_l1, 3×) and vacuum_cleaner_shared (predicted storage_floor_s1, actually coffee_table_l1, 3×), both on day 6 at 18:00. The hourly sightings reveal a strikingly consistent pattern: at every single hour on weekdays, the duster is at storage_shelf_s1 in 3 of 4 passes and at coffee_table_l1 in 1. The vacuum is at storage_floor_s1 in 3 of 4 and coffee_table_l1 in 1. This is not a brief afternoon cleaning spike (as p_8b3d hypothesised for 12–16h) — the 3:1 ratio is flat from 00:00 to 22:00.

The most parsimonious explanation: the duster and vacuum have a secondary resting position at or near the coffee table. Perhaps the duster leans against the coffee table between uses, or the vacuum is parked there with its cord draped over the table edge. They are in storage 75% of the time (the robot's most common find) but at the coffee table 25% of the time, consistently, at all hours. On weekends the pattern is similar: duster at storage_shelf_s1 x1 and coffee_table_l1 x1 (a 1:1 split in the 2-pass weekend data), vacuum at storage_floor_s1 x1 and coffee_table_l1 x1.

This document does not predict a specific cleaning event. It says the duster and vacuum are always partly at the coffee table. What would refute it: the duster or vacuum found exclusively in storage across a full day with zero coffee-table sightings.

```json
{
 "claims": [
  {
   "claim": "The duster is at the coffee table during the weekday evening, not only in storage",
   "target": "duster_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The vacuum cleaner is at the coffee table during the weekday evening, not only in storage",
   "target": "vacuum_cleaner_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The duster is at the coffee table during the weekend afternoon",
   "target": "duster_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 14,
   "to": 20
  }
 ],
 "targets": {
  "duster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
