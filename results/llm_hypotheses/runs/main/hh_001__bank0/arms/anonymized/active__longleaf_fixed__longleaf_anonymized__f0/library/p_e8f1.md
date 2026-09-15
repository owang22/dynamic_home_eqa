# p_e8f1 — Couple, one works early shift (05:00-13:00); the house is active at odd hours

A couple lives here. Partner A works an early shift (05:00–13:00) at a hospital or factory. Partner B works a normal office job (09:00–17:00). The walkthrough at 15:08 on a Monday caught Partner A home (off shift) and Partner B still at work. Partner A leaves at 04:15 and returns at 13:30. Partner B leaves at 08:30 and returns at 17:30. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used at 04:00–05:00 (Partner A's pre-shift meal) and 17:00–20:00 (dinner). The bathroom (receptacle_6, receptacle_22) is used at 04:00–05:00 and 20:00–22:00. The bedroom (receptacle_8, receptacle_13) is where Partner A sleeps 14:00–23:00.

What sets this apart: on weekdays, object_2 (keys) is OUT_OF_HOUSE from 04:15 to 13:30 (Partner A's shift) AND from 08:30 to 17:30 (Partner B's shift) — effectively out 04:15 to 17:30 with a brief overlap. The kitchen objects (class_4) are at receptacle_4 at 04:00–05:00 (unusual early morning). The bedroom items (class_16) are at receptacle_8 from 14:00 to 23:00 (Partner A's sleep). What would refute it: class_4 objects at receptacle_4 at 07:00 on a weekday (no one is home then for a meal), or object_2 found in the house at 06:00 on a weekday.

```json
{"claims": [
   {"claim": "object_2 (keys) is out of the house from early morning through afternoon on weekdays",
    "target": "object_2", "expect": "receptacle_2", "days": "weekday", "from": 4, "to": 17},
   {"claim": "object_4 (kitchen item) is on the counter at 4 AM for Partner A's pre-shift meal",
    "target": "object_4", "expect": "receptacle_4", "days": "weekday", "from": 4, "to": 5},
   {"claim": "object_17 (bedroom item) is at the bedroom shelf during Partner A's afternoon sleep",
    "target": "object_17", "expect": "receptacle_8", "days": "weekday", "from": 14, "to": 23},
   {"claim": "object_13 (bathroom item) is at the bathroom sink in the early morning",
    "target": "object_13", "expect": "receptacle_6", "days": "weekday", "from": 4, "to": 6}
 ],
 "targets": {
   "object_2": [
     {"days": "weekday", "from": 4, "to": 17, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_4": [
     {"days": "weekday", "from": 4, "to": 5, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 17, "to": 20, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ],
   "object_17": [
     {"days": "weekday", "from": 14, "to": 23, "at": "receptacle_8", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_13", "chance": "usually"}
   ],
   "object_13": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_6", "chance": "almost_always"}
   ]
 }
}
```
