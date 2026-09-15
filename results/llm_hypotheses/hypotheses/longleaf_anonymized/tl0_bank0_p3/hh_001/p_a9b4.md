# p_a9b4 — University student; irregular hours, objects travel to campus

One adult is a graduate student. They leave for the university around 09:00 on weekdays and return around 18:00, but their schedule is irregular: sometimes they go at 07:00, sometimes they skip a day. The walkthrough at 15:08 on a Monday caught the home empty (student is at the university). The laptop and books (class_13, class_21) travel to campus. The keys (class_2) and bag (class_32) travel with the student. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used for quick meals: breakfast 07:00–09:00, dinner 18:00–20:00. The bathroom (receptacle_6, receptacle_22) is used in the morning and evening. The living room (receptacle_10) is used for studying on weekends and evenings.

What sets this apart: on weekdays, object_14 (class_13) and object_24 (class_21) are OUT_OF_HOUSE from 09:00 to 18:00 (they go to campus). The keys and bag are also out. On weekends, the desk objects return to receptacle_12 and the student studies in the living room. What would refute it: object_14 or object_24 found in the house between 10:00 and 16:00 on a weekday, or the keys found OUT_OF_HOUSE on a Saturday.

```json
{"claims": [
   {"claim": "object_14 (laptop/books) is out of the house at the university on weekdays",
    "target": "object_14", "expect": "receptacle_2", "days": "weekday", "from": 9, "to": 18},
   {"claim": "object_24 (classmate item) is out of the house at the university on weekdays",
    "target": "object_24", "expect": "receptacle_2", "days": "weekday", "from": 9, "to": 18},
   {"claim": "object_2 (keys) is out of the house on weekdays during university hours",
    "target": "object_2", "expect": "receptacle_2", "days": "weekday", "from": 9, "to": 18},
   {"claim": "object_26 (living room item) is in the living room on weekend evenings for studying",
    "target": "object_26", "expect": "receptacle_10", "days": "weekend", "from": 15, "to": 22}
 ],
 "targets": {
   "object_2": [
     {"days": "weekday", "from": 9, "to": 18, "at": "receptacle_2", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_14": [
     {"days": "weekday", "from": 9, "to": 18, "at": "receptacle_2", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_12", "chance": "usually"}
   ],
   "object_24": [
     {"days": "weekday", "from": 9, "to": 18, "at": "receptacle_2", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_12", "chance": "usually"}
   ],
   "object_26": [
     {"days": "weekend", "from": 15, "to": 22, "at": "receptacle_10", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_10", "chance": "usually"}
   ]
 }
}
```
