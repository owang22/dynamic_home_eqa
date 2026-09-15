# p_c7d2 — Single parent with a toddler; objects are everywhere, high churn

One adult and a toddler (under 3) live here. The walkthrough at 15:08 on a Monday caught the parent napping or the toddler in a nap (12:00–15:30). The home is a chaos zone: the toddler's items (class_16, class_22) are scattered between the living room (receptacle_10), the bedroom (receptacle_8, receptacle_13), and the kitchen (receptacle_4). The parent does errands in the late morning (10:00–12:00) and the toddler goes to daycare on alternating days. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used constantly: formula, snacks, meals. The bathroom (receptacle_6, receptacle_22) is used for diaper changes and baths. The desk (receptacle_12, receptacle_21) is barely used; the parent works from home in short bursts.

What sets this apart: on weekdays, object_17 (class_16) and object_25 (class_22) are found at MULTIPLE locations throughout the day (receptacle_10 in the morning, receptacle_4 at midday, receptacle_13 in the evening). The parent is out for errands 10:00–12:00 on weekdays (object_2, object_35 are OUT_OF_HOUSE then). The kitchen objects (class_4) are at receptacle_4 for most of the day (07:00–21:00) due to constant toddler feeding. What would refute it: the toddler items (class_16, class_22) found at only one location all day, or the parent's keys in the house at 11:00 on a weekday.

```json
{"claims": [
   {"claim": "object_17 (toddler item) is in the living room in the morning",
    "target": "object_17", "expect": "receptacle_10", "days": "weekday", "from": 7, "to": 10},
   {"claim": "object_25 (toddler item) is at the kitchen counter at midday",
    "target": "object_25", "expect": "receptacle_4", "days": "weekday", "from": 11, "to": 14},
   {"claim": "object_2 (keys) is out of the house for errands on weekday late mornings",
    "target": "object_2", "expect": "receptacle_2", "days": "weekday", "from": 10, "to": 12},
   {"claim": "object_4 (kitchen item) is on the counter for most of the day due to toddler feeding",
    "target": "object_4", "expect": "receptacle_4", "days": "both", "from": 7, "to": 21}
 ],
 "targets": {
   "object_17": [
     {"days": "weekday", "from": 7, "to": 10, "at": "receptacle_10", "chance": "usually"},
     {"days": "weekday", "from": 10, "to": 14, "at": "receptacle_4", "chance": "sometimes"},
     {"days": "weekday", "from": 14, "to": 22, "at": "receptacle_13", "chance": "usually"}
   ],
   "object_25": [
     {"days": "weekday", "from": 11, "to": 14, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_10", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_8", "chance": "sometimes"}
   ],
   "object_2": [
     {"days": "weekday", "from": 10, "to": 12, "at": "receptacle_2", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_4": [
     {"days": "both", "from": 7, "to": 21, "at": "receptacle_4", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ]
 }
}
```
