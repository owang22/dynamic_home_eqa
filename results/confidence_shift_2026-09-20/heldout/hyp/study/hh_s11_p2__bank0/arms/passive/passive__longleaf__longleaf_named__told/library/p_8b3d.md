# p_8b3d — The Afternoon Living-Room Clean; Vacuum and Duster at the Coffee Table

The mixture's worst-object list shows vacuum_cleaner_shared predicted at storage_floor_s1 but actually at coffee_table_l1 fifteen times, and duster_shared predicted at storage_shelf_s1 but actually at coffee_table_l1 thirteen times. The clock-hour data reveals a consistent pattern: on weekdays, both objects sit in their storage spots for the first three-quarters of each hour (3 of 4 sightings) but appear at the coffee table for one-quarter (1 of 4) during the 00:00–16:00 window. From 18:00 onward they are back in storage 100% of the time. On weekends the split shifts: 00:00–10:00 they are fully in storage, but from 12:00 to 22:00 the coffee table gets one of every two sightings.

This is a cleaning session. Priya (who is home most of the day) pulls the vacuum and duster out to the living room, cleans around the coffee table, and returns them to storage. On weekdays the cleaning happens during the day while Hana is at work (or in the morning before Hana leaves); on weekends it happens in the afternoon when both residents are home and "around the house."

The key distinction from the statistical model: the model sees the vacuum at storage_floor_s1 75% of the time and predicts it there, missing the 25% coffee-table sightings. This document gives the coffee table a dedicated block during the cleaning window so the robot knows to look there.

What would refute this: vacuum_cleaner or duster found at coffee_table_l1 during 18:00–24:00 on a weekday (outside the cleaning window); both objects at the coffee table simultaneously at a time when no resident is in the living room.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is at the coffee table during the weekday afternoon cleaning window",
   "target": "vacuum_cleaner_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "The duster is at the coffee table during the weekend afternoon cleaning window",
   "target": "duster_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The vacuum cleaner is back in storage by the evening on weekdays",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The duster is in storage during the weekday evening",
   "target": "duster_shared",
   "expect": "storage_shelf_s1",
   "days": "weekday",
   "from": 18,
   "to": 22
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
    "from": 8,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "duster_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
