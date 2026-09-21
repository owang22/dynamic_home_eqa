# p_8c2e — Vacuum Out All Weekend: Saturday Midnight Through Sunday Night

The vacuum cleaner is not a quick-task object in this house. On weekdays it sits in storage (storage_floor_s1) from midnight through the morning, with a brief appearance on the living room floor in the afternoon (12:00–16:00, 1–2 sightings). But on weekends the picture is completely different: from Saturday 00:00 through at least Saturday 10:00, the vacuum is on the living room floor every single patrol pass (2/2 sightings at floor_l_l1). It stays out at a 1/2 rate from noon through Sunday evening.

This hypothesis says the residents do a full weekend clean that starts Saturday morning (or even Friday night) and the vacuum is left out on the living room floor for the entire weekend. It is not put back in storage between rooms or between sessions. The 1/2 split in the afternoon and evening suggests one of two things: the vacuum is occasionally moved to storage briefly, or the robot is catching it in transit between the living room and the hallway.

What would refute this: if on a Saturday morning (08:00–12:00) the robot finds the vacuum in storage_floor_s1, the "out all weekend" claim is wrong. If the vacuum is found on the living room floor on a weekday morning (before 10:00), the weekend-specificity fails.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 08:00 on a Saturday because the weekend clean started early",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 6,
   "to": 12
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 10:00 on a Sunday, still out from the weekend clean",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 8,
   "to": 14
  },
  {
   "claim": "The vacuum cleaner is in storage at 08:00 on a Tuesday, not on the living room floor",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 6,
   "to": 10
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 11,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ]
 }
}
```
