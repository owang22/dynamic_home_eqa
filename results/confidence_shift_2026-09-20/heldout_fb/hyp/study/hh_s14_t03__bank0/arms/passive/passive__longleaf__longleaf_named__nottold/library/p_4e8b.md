# p_4e8b — 10:00 Vacuum: Yuki Cleans the Living Room

The vacuum cleaner is at storage_floor_s1 at 03:00, 08:00, 18:00, and 23:00 — its resting place. But at 10:00 on a weekday it was found on floor_l_l1 (the living room floor) on two separate occasions, while on the same 10:00 pass it was also at storage_floor_s1 on two other occasions. This means Yuki vacuums the living room around 10:00 on some weekdays, not all. She is home (retired, no work), and the late-morning slot fits between her morning walk (07:00–08:30) and her afternoon errands (14:30–16:00).

This document predicts the vacuum on the living room floor during the 09:30–11:00 window on weekdays, with a "sometimes" chance because it was only 2 out of 4 passes at 10:00 that found it on the floor. The other 2 passes found it in storage, consistent with days when she does not vacuum.

Refutation: if the vacuum is found on the living room floor at 14:00 or 16:00 (outside this window), or if it is never on the floor again in 10+ weekday passes in the 09:30–11:00 window, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor during Yuki's weekday late-morning cleaning",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 9.5,
   "to": 11
  },
  {
   "claim": "The vacuum cleaner is in storage at 03:00",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The vacuum cleaner is in storage in the evening after cleaning is done",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "both",
   "from": 17,
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
    "to": 11,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
