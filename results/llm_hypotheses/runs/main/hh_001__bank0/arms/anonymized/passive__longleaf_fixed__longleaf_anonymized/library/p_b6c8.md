# p_b6c8 — Couple, both work but one is a teacher (school hours + evening prep)

A couple lives here. Partner A is a teacher: at school 08:00–15:30, then at home doing grading and prep 16:00–22:00. Partner B works a normal office job 09:00–17:00. The walkthrough at 15:08 on a Monday caught Partner A still at school (just about to leave) and Partner B at the office. The teacher's items (class_13, class_21) go to the school on weekdays 08:00–15:30, then return home. The teacher uses the desk (receptacle_21) in the evening for grading. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used for dinner 18:00–20:00. The bathroom (receptacle_6, receptacle_22) is used in the morning (06:30–07:30) and evening (21:00–22:00).

What sets this apart: on weekdays, object_14 (class_13) is OUT_OF_HOUSE from 08:00 to 15:30 (at school) but then at receptacle_21 from 16:00 to 22:00 (grading). This is a two-phase pattern: out in the morning/afternoon, in the evening at the desk. Partner B's items (class_2, class_32) are out 09:00–17:00. What would refute it: object_14 found in the house at 10:00 on a weekday, or object_14 at receptacle_12 (not receptacle_21) during the evening grading window.

```json
{"claims": [
   {"claim": "object_14 (teacher's materials) is out of the house at school on weekday mornings and afternoons",
    "target": "object_14", "expect": "receptacle_2", "days": "weekday", "from": 8, "to": 15},
   {"claim": "object_14 (teacher's materials) is at the desk in the evening for grading",
    "target": "object_14", "expect": "receptacle_21", "days": "weekday", "from": 16, "to": 22},
   {"claim": "object_2 (keys) is out of the house on weekdays during office hours",
    "target": "object_2", "expect": "receptacle_2", "days": "weekday", "from": 9, "to": 17},
   {"claim": "object_4 (kitchen item) is on the counter during dinner on weekdays",
    "target": "object_4", "expect": "receptacle_4", "days": "weekday", "from": 18, "to": 20}
 ],
 "targets": {
   "object_14": [
     {"days": "weekday", "from": 8, "to": 15, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "weekday", "from": 16, "to": 22, "at": "receptacle_21", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_12", "chance": "usually"}
   ],
   "object_2": [
     {"days": "weekday", "from": 9, "to": 17, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_4": [
     {"days": "weekday", "from": 18, "to": 20, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ]
 }
}
```
