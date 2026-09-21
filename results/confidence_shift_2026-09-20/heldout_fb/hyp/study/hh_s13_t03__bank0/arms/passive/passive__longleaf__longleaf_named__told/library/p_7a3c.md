# p_7a3c — Vacuum on Three Passes: 10, 15, 18

Priya vacuums the living room three times on a weekday: a morning pass around 10:00, an afternoon pass around 15:00, and an evening pass around 18:00. Between passes the vacuum sits back in storage on the floor of the storage room. The robot's worst-object list flags the vacuum three times at floor_l_l1 where the mixture predicted storage_floor_s1, and the sightings confirm it: 10:00 floor_l_l1, 15:00 floor_l_l1, 18:00 floor_l_l1 (x2), with storage_floor_s1 at 03:00, 09:00, and 14:00. This is a chore rhythm, not a single afternoon tidy. Hana is at work during all three passes, so Priya does the vacuuming alone. The shopping bag on the counter at 12:00–13:00 (seen 8 times) fits: Priya returns from errands, puts the bag down, then vacuums the afternoon pass at 15:00.

What sets this apart: p_4e1b captures only the 15:00 pass and the 18:00 return to storage. This document extends the pattern to three distinct in-use windows and predicts the vacuum is *out* at 18:00, not back in storage.

What would refute it: if the vacuum is found in storage at 10:00 or 15:00 on multiple weekday mornings/afternoons, or if it is seen on the kitchen floor rather than the living room floor.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 10:00 on a weekday (morning pass)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 9.5,
   "to": 11
  },
  {
   "claim": "The vacuum cleaner is back in storage at 12:00 on a weekday (between morning and afternoon passes)",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 15:00 on a weekday (afternoon pass)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 14.5,
   "to": 16
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 18:00 on a weekday (evening pass)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
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
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
