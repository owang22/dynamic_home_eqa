# p_d8e3 — Work-from-home professional; the desk never empties

One adult works from home full-time. The walkthrough at 15:08 caught them mid-afternoon at the desk (receptacle_12 or receptacle_21). The home is their office: the desk area is occupied 08:00–18:00 on weekdays. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used for quick meals and coffee breaks. The bedroom (receptacle_8, receptacle_13) is quiet. The bathroom (receptacle_6, receptacle_22) is used at irregular intervals. Crucially, NOTHING leaves the house on weekdays: the resident never commutes. The keys (class_2) and bag (class_32) stay on the kitchen shelf. The entryway item (class_3) stays at receptacle_7.

What sets this apart: on weekdays 09:00–17:00, object_2, object_35, and object_3 are ALL in the house (not out). The desk objects (class_13, class_21, class_18, class_31) are at receptacle_21 during work hours. What would refute it: object_2 or object_35 found OUT_OF_HOUSE on a weekday between 09:00 and 17:00, or the desk objects at receptacle_12 during weekday work hours.

```json
{"claims": [
   {"claim": "object_2 (keys) remains in the house on weekdays because the resident works from home",
    "target": "object_2", "expect": "receptacle_11", "days": "weekday", "from": 9, "to": 17},
   {"claim": "object_35 (bag) remains in the house on weekdays",
    "target": "object_35", "expect": "receptacle_11", "days": "weekday", "from": 9, "to": 17},
   {"claim": "object_14 (desk item) is at the work desk during weekday work hours",
    "target": "object_14", "expect": "receptacle_21", "days": "weekday", "from": 8, "to": 18},
   {"claim": "object_3 (entryway item) stays at the entryway all week since no one commutes",
    "target": "object_3", "expect": "receptacle_7", "days": "both", "from": 0, "to": 24}
 ],
 "targets": {
   "object_2": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "almost_always"}
   ],
   "object_35": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "almost_always"}
   ],
   "object_14": [
     {"days": "weekday", "from": 8, "to": 18, "at": "receptacle_21", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_12", "chance": "usually"}
   ],
   "object_3": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_7", "chance": "almost_always"}
   ]
 }
}
```
