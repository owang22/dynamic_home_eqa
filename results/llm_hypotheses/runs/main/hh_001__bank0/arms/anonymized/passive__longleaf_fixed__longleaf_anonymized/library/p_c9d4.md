# p_c9d4 — Very organized single person; objects have fixed homes and never stray

One adult lives here with a strict organizational system. Every object has exactly one home location and is returned there after each use. The walkthrough at 15:08 on a Monday caught the home in its perfectly organized state. The resident works from home (no commuting) and follows a rigid schedule: wake 06:30, work 09:00–17:00, exercise 17:30–18:30, dinner 19:00–20:00, bed 22:30. The keys (class_2) and bag (class_32) stay on the kitchen shelf (receptacle_11) always. The entryway item (class_3) stays at receptacle_7. The bathroom items (class_12, class_24, class_28) are at receptacle_6 always. The kitchen items (class_4) are at receptacle_18 (their shelf) except during the 30-minute cooking windows. The desk items (class_13, class_21, class_18, class_31) are at receptacle_21 during work hours and receptacle_12 otherwise.

What sets this apart: NOTHING is ever OUT_OF_HOUSE. The resident never leaves the house (works from home, exercises in the living room). Every object is at its "home" receptacle except during brief, predictable use windows. The chance for objects at their home location is "almost_always." What would refute it: any object found OUT_OF_HOUSE at any time, or any object found at a receptacle other than its assigned home outside its brief use window.

```json
{"claims": [
   {"claim": "object_2 (keys) is always at the kitchen shelf, never leaves the house",
    "target": "object_2", "expect": "receptacle_11", "days": "both", "from": 0, "to": 24},
   {"claim": "object_14 (desk item) is at the work desk during weekday work hours",
    "target": "object_14", "expect": "receptacle_21", "days": "weekday", "from": 9, "to": 17},
   {"claim": "object_4 (kitchen item) is at its shelf except during the 30-minute cooking window",
    "target": "object_4", "expect": "receptacle_18", "days": "both", "from": 10, "to": 18},
   {"claim": "object_13 (bathroom item) is at the bathroom sink at all times",
    "target": "object_13", "expect": "receptacle_6", "days": "both", "from": 0, "to": 24}
 ],
 "targets": {
   "object_2": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "almost_always"}
   ],
   "object_14": [
     {"days": "weekday", "from": 9, "to": 17, "at": "receptacle_21", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_12", "chance": "almost_always"}
   ],
   "object_4": [
     {"days": "both", "from": 10, "to": 18, "at": "receptacle_18", "chance": "almost_always"},
     {"days": "both", "from": 18, "to": 19, "at": "receptacle_4", "chance": "usually"}
   ],
   "object_13": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_6", "chance": "almost_always"}
   ]
 }
}
```
