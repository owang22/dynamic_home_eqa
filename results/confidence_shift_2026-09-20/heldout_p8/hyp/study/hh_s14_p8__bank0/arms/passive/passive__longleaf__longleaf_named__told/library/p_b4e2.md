# p_b4e2 — Remote: coffee table overnight, TV stand by evening

After evening TV (roughly 20:00–22:00 on weekdays), the remote gets set down on the coffee table and nobody picks it up. It stays there through the night and into the next morning and midday. By the 18:00 patrol it has been retrieved and placed back on the TV stand for the evening. On weekends the pattern is absent: the remote stays on the TV stand at every patrol, suggesting a tidier weekend or different viewing schedule. This document is distinguished by predicting coffee_table_l1 for the remote during the 00:00–17:00 weekday window (the overnight carryover) and tv_stand_l1 from 17:00 onward. If the robot finds the remote on the TV stand at 08:00 or 16:00 on a weekday, this document is weakened.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table in the weekday morning after last night's TV",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 0,
   "to": 9
  },
  {
   "claim": "The remote is back on the TV stand by the weekday evening",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 17,
   "to": 22
  },
  {
   "claim": "The remote stays on the TV stand on the weekend",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
