# p_6f4a — Night-time repositioning: Omar's phone and glasses shift to bedside, razor to shelf

This document addresses the "worst objects" the mixture has been getting wrong at night. The sightings show three consistent night-time shifts that the current library does not model:

1. **phone_omar**: The mixture predicted coffee_table_l1, but the robot found it at nightstand_b1 on two occasions (day 3, 00:00). The phone is a bedside object at night — Omar charges it on the nightstand after his gaming session ends and before bed. During the day it bounces between counter_k1, coffee_table_l1, and nightstand_b1 (1/3 each at 00:00 and 08:00), but the 00:00–07:00 window is when it settles at nightstand_b1.

2. **glasses_omar**: The mixture predicted nightstand_b1, but the robot found it at desk_b1 on two occasions (day 3, 00:00). Omar's glasses go to the bedroom desk at night — he likely reads or works at the desk before bed, and the glasses end up there. During the day they are at nightstand_b1 (3/3 in the 9–17h window), but the 22:00–07:00 window sees them at desk_b1.

3. **razor_omar**: The mixture predicted sink_ba_ba1, but the robot found it at bathroom_shelf_ba1 on two occasions (day 3, 16:00). After Omar's morning shave (he is home 23:00–13:40, so his shaving window is roughly 06:00–08:00), the razor is put away on the bathroom shelf rather than left at the sink. The 14:00–22:00 window (after his morning routine, before his next morning) sees the razor at bathroom_shelf_ba1.

This document sets itself apart from p_4e91 and p_f3a7, which place glasses_omar at nightstand_b1 0–24h and do not model the phone or razor night-time shifts. It is complementary to those documents: it does not change the weekday driving, tablet, or kitchen schedules, only the three objects the mixture has been misplacing at night.

What would refute this document: finding phone_omar at coffee_table_l1 at 02:00, or glasses_omar at nightstand_b1 at 02:00, or razor_omar at sink_ba_ba1 at 16:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Omar's phone is at the bedroom nightstand at 02:00 on a weekday, charging overnight",
   "target": "phone_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Omar's glasses are at the bedroom desk at 02:00 on a weekday, left there after his pre-bed reading",
   "target": "glasses_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Omar's razor is at the bathroom shelf at 16:00 on a weekday, put away after his morning shave",
   "target": "razor_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "phone_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 12,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 22,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "razor_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "phone_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
