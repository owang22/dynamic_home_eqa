# p_9e4b — Mid-Morning Vacuum: Living Room Floor 09:30–11:30 Weekdays

The vacuum cleaner is pulled from its storage-floor resting spot and used in the living room around 10:00 on weekdays. The Thursday (day 2) 10:00 patrol caught it on the living room floor (two sightings at floor_l_l1 alongside two at storage_floor_s1, suggesting the robot saw it in transition or just after it was set down). On a normal weekday this is most likely Marco doing a quick vacuum before his 1:40 departure, or Yuki running a mid-morning clean while Marco is still home. On the sick Friday, Yuki may skip this to care for Marco, leaving the vacuum in storage all day.

The vacuum's resting place is the storage floor (storage_floor_s1), confirmed by sightings at 03:00, 08:00, 18:00, and 23:00. It is off the storage floor only during the roughly 09:30–11:30 vacuuming window. The ironing board also rests on the storage floor (storage_floor_s1) and is not part of this routine.

This sets itself apart from the mixture's default prediction of storage_floor_s1 at all times. The 10:00 sightings at floor_l_l1 are the distinguishing evidence, and the "mixture's worst objects" list flags vacuum_cleaner_shared as predicted at storage_floor_s1 but actually at floor_l_l1 on two occasions.

What would refute: if the vacuum is seen on the living room floor at a time outside 09:00–12:00, or if it is never seen off the storage floor in a full week of patrols.

```json
{
 "claims": [
  {
   "claim": "The vacuum is on the living room floor at 10:00 on a weekday, in use",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 9.5,
   "to": 11
  },
  {
   "claim": "The vacuum is in storage at 08:00 on a weekday, before being pulled out for the mid-morning clean",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "The vacuum is back in storage at 18:00 on a weekday, after the mid-morning vacuuming is done",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 12,
   "to": 18
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9.5,
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
    "days": "weekday",
    "from": 11.5,
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
