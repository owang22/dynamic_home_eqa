# p_3f8a — Afternoon Yoga; Mat Unrolls at 15:00 Weekdays and 20:00 Weekends

Priya does not just stretch in the early morning. The patrol passes show her yoga mat on the living room floor at 15:00 on weekdays (two separate sightings) and at 20:00 on weekends (one sighting). This is a second daily yoga or stretching session: an afternoon unroll on weekdays when she is home and the morning walk is done, and an evening unroll on weekends when the late-morning walk is behind her. The mat rests in wardrobe_b2 between sessions. This document differs from p_c9d4, which only places the mat on the floor at 06:00 and back in the wardrobe by 07:00; here the mat leaves the wardrobe a second time each day. On weekdays the afternoon session runs roughly 14:30 to 16:00; on weekends the evening session runs roughly 19:30 to 21:00. What would refute this document: the mat being sighted on the floor at 15:00 or 20:00 on multiple days (supporting it), or the mat being found on the floor at 10:00 or 22:00 (a time this document does not predict), or the mat never leaving wardrobe_b2 during the afternoon window.

```json
{
 "claims": [
  {
   "claim": "The yoga mat is on the living room floor during Priya's weekday afternoon session",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 14.5,
   "to": 16
  },
  {
   "claim": "The yoga mat is on the living room floor during the weekend evening session",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The yoga mat is back in wardrobe_b2 by 17:00 on weekdays after the afternoon session",
   "target": "yoga_mat_priya",
   "expect": "wardrobe_b2",
   "days": "weekday",
   "from": 16,
   "to": 23
  },
  {
   "claim": "The yoga mat is in wardrobe_b2 during the weekday midday hours",
   "target": "yoga_mat_priya",
   "expect": "wardrobe_b2",
   "days": "weekday",
   "from": 9,
   "to": 14
  }
 ],
 "targets": {
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
