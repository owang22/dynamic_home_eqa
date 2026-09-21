# p_7f3a — Vacuum Full Cycle: Floor Storage, Midday Use, Shelf Afternoon

Marco and Yuki share a household with a dog. Marco works afternoon-to-night shifts (home mornings, out 13:40–23:00 weekdays); Yuki is retired and anchors the house. The vacuum cleaner follows a strict weekday rhythm that no single existing document captures in full: it rests on the storage floor overnight, is pulled onto the living room floor for a mid-morning-to-afternoon clean, then is set on the storage *shelf* (not the floor) in the late afternoon before being returned to the floor for the night. On weekends the vacuum stays on the shelf through the morning and is pulled out for an evening clean around 20:00–22:00.

This document differs from p_9e4b (which limits the clean to 09:30–11:30) and p_5c8e (which places it on the floor 13–15 h but ignores the shelf) and p_9a4e (which keeps it on the storage floor all afternoon). The 17:00 and 19:00 weekday sightings at storage_shelf_s1, and the 03:00/14:00 weekend sightings at storage_shelf_s1, are the distinguishing evidence. If the vacuum is found on the storage *floor* at 17:00 on a weekday, or on the living room floor at 14:00 on a weekend, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The vacuum is on the storage shelf at 17:00 on a weekday, after the midday clean is finished",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_shelf_s1",
   "days": "weekday",
   "from": 16,
   "to": 19
  },
  {
   "claim": "The vacuum is on the living room floor at 14:00 on a weekday, still in active use",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "The vacuum is on the storage shelf at 14:00 on a weekend, not yet pulled out for the evening clean",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_shelf_s1",
   "days": "weekend",
   "from": 13,
   "to": 15
  },
  {
   "claim": "The vacuum is on the living room floor at 21:00 on a weekend during the evening clean",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 15.5,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15.5,
    "to": 20,
    "at": "storage_shelf_s1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ]
 }
}
```
