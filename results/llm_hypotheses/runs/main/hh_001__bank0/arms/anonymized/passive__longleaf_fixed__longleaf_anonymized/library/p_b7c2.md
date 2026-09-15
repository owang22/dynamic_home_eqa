# p_b7c2 — Two commuters, staggered departures; the entryway is the bottleneck

A couple lives here. The partner who leaves first (Partner A) departs around 07:15; Partner B leaves around 08:00 and returns around 19:00. Both carry their own keys and phones. The walkthrough at 15:08 on a Monday caught the home empty. The entryway (receptacle_7) is where both drop their coats, bags, and shoes before heading out. The kitchen (receptacle_4, receptacle_18, receptacle_19) sees two-person usage: mugs, a cutting board, a knife. The desk area (receptacle_12, receptacle_21) belongs to Partner B who works from home on Wednesdays. The bedroom (receptacle_8, receptacle_13) is shared; items on the nightstand shift as each partner uses them.

What sets this apart: on weekdays, object_3 (class_3, entryway item) is OUT_OF_HOUSE from 07:15 to 19:00 because both partners have left. The desk objects (class_13, class_21) are at receptacle_21 on Wednesdays (WFH day) but at receptacle_12 the rest of the week. What would refute it: object_3 found in the house between 09:00 and 17:00 on a weekday, or the desk objects at receptacle_21 on a Tuesday.

```json
{"claims": [
   {"claim": "object_3 (entryway item) is out of the house on weekdays when both partners are at work",
    "target": "object_3", "expect": "receptacle_2", "days": "weekday", "from": 8, "to": 18},
   {"claim": "object_14 (desk item) is at the desk on Wednesday (WFH day)",
    "target": "object_14", "expect": "receptacle_21", "days": "weekday", "from": 8, "to": 17},
   {"claim": "object_15 (kitchen item) is on the counter during both breakfast and dinner",
    "target": "object_15", "expect": "receptacle_4", "days": "both", "from": 6, "to": 9},
   {"claim": "object_18 (bedroom item) is at the nightstand in the evening",
    "target": "object_18", "expect": "receptacle_13", "days": "both", "from": 19, "to": 23}
 ],
 "targets": {
   "object_3": [
     {"days": "weekday", "from": 8, "to": 18, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_7", "chance": "usually"}
   ],
   "object_14": [
     {"days": "weekday", "from": 8, "to": 17, "at": "receptacle_21", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_12", "chance": "usually"}
   ],
   "object_15": [
     {"days": "both", "from": 6, "to": 9, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ],
   "object_18": [
     {"days": "both", "from": 19, "to": 23, "at": "receptacle_13", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_8", "chance": "usually"}
   ]
 }
}
```
