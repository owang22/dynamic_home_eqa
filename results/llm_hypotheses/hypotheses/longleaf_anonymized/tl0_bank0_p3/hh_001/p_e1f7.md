# p_e1f7 — Night-shift worker; the house is empty at night, alive at midday

One adult works nights (22:00–06:00). The walkthrough at 15:08 on a Monday caught the resident in their off-hours, resting or doing errands. The house is QUIET from 06:00 to 20:00 (resident sleeping or out). The house is ACTIVE from 20:00 to 06:00 (resident awake, cooking, cleaning). The keys (class_2) and bag (class_32) leave the house at 21:00 and return at 07:00. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used in the evening (20:00–23:00) for the resident's dinner and in the early morning (05:00–07:00) for breakfast before bed. The desk (receptacle_12, receptacle_21) is used only in the evening for emails.

What sets this apart: on weekdays, object_2 and object_35 are OUT_OF_HOUSE from 21:00 to 07:00 (inverted from normal). The kitchen objects (class_4) are at receptacle_4 in the evening (20:00–23:00) rather than the morning. The house is empty of the resident 06:00–20:00. What would refute it: object_2 found in the house between 22:00 and 05:00 on a weekday, or class_4 objects at receptacle_4 between 07:00 and 19:00 on a weekday.

```json
{"claims": [
   {"claim": "object_2 (keys) is out of the house during the night shift on weekdays",
    "target": "object_2", "expect": "receptacle_2", "days": "weekday", "from": 21, "to": 24},
   {"claim": "object_35 (bag) is out of the house during the night shift",
    "target": "object_35", "expect": "receptacle_2", "days": "weekday", "from": 21, "to": 24},
   {"claim": "object_4 (kitchen item) is on the counter in the evening for dinner",
    "target": "object_4", "expect": "receptacle_4", "days": "weekday", "from": 20, "to": 23},
   {"claim": "object_14 (desk item) is at the desk in the evening for emails",
    "target": "object_14", "expect": "receptacle_21", "days": "weekday", "from": 20, "to": 23}
 ],
 "targets": {
   "object_2": [
     {"days": "weekday", "from": 21, "to": 24, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_35": [
     {"days": "weekday", "from": 21, "to": 24, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_4": [
     {"days": "weekday", "from": 20, "to": 23, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ],
   "object_14": [
     {"days": "weekday", "from": 20, "to": 23, "at": "receptacle_21", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_12", "chance": "usually"}
   ]
 }
}
```
