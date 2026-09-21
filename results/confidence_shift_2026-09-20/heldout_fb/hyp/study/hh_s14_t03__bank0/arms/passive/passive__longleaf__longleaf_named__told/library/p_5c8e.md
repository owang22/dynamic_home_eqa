# p_5c8e — Vacuum Afternoon: Pulled Out 09:30, Back in Storage 16:30

Marco and Yuki share the midweek vacuuming. The vacuum cleaner lives on the storage floor overnight and in the early morning, but is pulled into the living room around 09:30 on weekdays and stays out on the living room floor through the afternoon, until roughly 16:30 when it is returned to storage. The 14:00 pass consistently finds it on the living room floor (five sightings), and the 10:00 pass catches it in transition (two in storage, two on the floor). By 17:00 it is back in the storage area, briefly on the shelf before settling on the floor for the night.

This hypothesis differs from p_9e4b, which confines the vacuum's floor time to 09:30–11:30. The evidence at 14:00 (five sightings on the living room floor) makes clear the cleaning session extends well into the afternoon. It also differs from p_9a4e, which predicts the vacuum is in storage at 18:00 (against 8); the 17:00 and 19:00 passes show it on the storage *shelf*, not the floor, suggesting a two-step return.

What would refute this: a weekday pass at 12:00 or 14:00 finding the vacuum in storage (floor or shelf), or a pass at 08:00 finding it already on the living room floor.

```json
{
 "claims": [
  {
   "claim": "The vacuum is on the living room floor at 14:00 on a weekday, mid-cleaning",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "The vacuum is in storage on the floor at 07:00 on a weekday, before being pulled out",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 6.5,
   "to": 8.5
  },
  {
   "claim": "The vacuum is back on the storage floor by 23:00 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "The vacuum is on the living room floor at 10:00 on a weekday, just after being pulled out",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 9.5,
   "to": 11
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9.5,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 16.5,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16.5,
    "to": 17.5,
    "at": "storage_shelf_s1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ]
 }
}
```
