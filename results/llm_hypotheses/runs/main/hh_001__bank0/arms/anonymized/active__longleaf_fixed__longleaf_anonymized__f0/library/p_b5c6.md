# p_b5c6 — Couple, one gym-goer; the gym bag and towel cycle daily

A couple lives here. Partner A works a normal office job (08:00–17:30). Partner B works from home but goes to the gym every weekday at 18:00–19:30. The walkthrough at 15:08 on a Monday caught the home with Partner A out and Partner B at the desk. The gym bag (class_32, object_35) and a towel (class_26, object_29) go to the gym with Partner B on weekdays 18:00–20:00. The keys (class_2, object_2) go with Partner A to the office. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used for Partner A's lunch prep in the morning and dinner for both in the evening. The bathroom (receptacle_6, receptacle_22) is used by Partner B after the gym (19:30–20:30).

What sets this apart: on weekdays, object_35 (gym bag) and object_29 (towel) are OUT_OF_HOUSE from 18:00 to 20:00 specifically (gym window), while object_2 (keys) is out 08:00–17:30 (work). The bathroom objects (class_26) are at receptacle_6 in the evening (19:30–21:00) for the post-gym shower. What would refute it: object_35 found in the house at 19:00 on a weekday, or object_2 found OUT_OF_HOUSE after 18:00 on a weekday.

```json
{"claims": [
   {"claim": "object_35 (gym bag) is out of the house at the gym on weekday evenings",
    "target": "object_35", "expect": "receptacle_2", "days": "weekday", "from": 18, "to": 20},
   {"claim": "object_29 (towel) is out of the house at the gym on weekday evenings",
    "target": "object_29", "expect": "receptacle_2", "days": "weekday", "from": 18, "to": 20},
   {"claim": "object_2 (keys) is out of the house at the office on weekday mornings",
    "target": "object_2", "expect": "receptacle_2", "days": "weekday", "from": 8, "to": 17},
   {"claim": "object_29 (towel) is at the bathroom shelf after the post-gym shower",
    "target": "object_29", "expect": "receptacle_22", "days": "weekday", "from": 20, "to": 22}
 ],
 "targets": {
   "object_2": [
     {"days": "weekday", "from": 8, "to": 17, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_35": [
     {"days": "weekday", "from": 18, "to": 20, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_29": [
     {"days": "weekday", "from": 18, "to": 20, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "weekday", "from": 20, "to": 22, "at": "receptacle_22", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_6", "chance": "usually"}
   ]
 }
}
```
