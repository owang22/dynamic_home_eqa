# p_9a4e — Vacuum in Storage: Mid-Morning Floor Visit, Not Every Day

This document addresses the vacuum cleaner's actual pattern, which the existing p_9e4b document (weight 0.022) captures partially but with a "sometimes" confidence that the evidence now refines. The 03:00, 08:00, 18:00, and 23:00 sightings all place the vacuum at storage_floor_s1. The 10:00 pass shows it at BOTH storage_floor_s1 (×2) and floor_l_l1 (×2) across different days — meaning the mid-morning vacuuming happens on some weekdays but not all. On the days it does not vacuum, the machine stays in storage the entire day.

The pattern: storage from 00:00 through 09:30. On vacuuming days (roughly 2 of 5 weekdays), the vacuum is pulled to the living-room floor from about 09:30 to 11:30. On non-vacuuming days it remains in storage. After 11:30 it returns to storage regardless. The weekend shows no floor sightings in the data, so weekend vacuuming is either absent or at a different hour.

What sets this document apart from p_9e4b: the chance of finding the vacuum on the living-room floor at 10:00 is "sometimes" (about 40% of weekdays), not "usually." If the robot finds the vacuum on the living-room floor at 10:00 on three consecutive weekdays, this document is refuted (the vacuuming is more frequent than modeled). If it finds the vacuum in storage at 10:00 on a weekday, this document is supported.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is in storage at 08:00 on a weekday, before any mid-morning clean",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "The vacuum cleaner is in storage at 18:00 on a weekday, after the mid-morning clean is done",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 12,
   "to": 18
  },
  {
   "claim": "The vacuum cleaner is in storage at 23:00 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "both",
   "from": 22,
   "to": 24
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 11.5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "floor_l_l1",
    "chance": "rarely"
   }
  ]
 }
}
```
