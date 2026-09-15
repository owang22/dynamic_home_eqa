# p_a3f1 — Single commuter; the kitchen and desk anchor the week

One adult lives here, an office worker who leaves the house around 07:45 on weekdays and returns near 18:30. The walkthrough at 15:08 caught the home empty of the resident; everything is in its resting place. The keys (class_2, object_2) and a small bag (class_32, object_35) sit on the kitchen shelf (receptacle_11) because the resident already left and the robot found them where they were set down the night before. In fact, under this hypothesis the resident is already out by 15:08, so those objects should be OUT_OF_HOUSE during weekday work hours. The desk area (receptacle_12, receptacle_21) holds work-related items that stay put. The kitchen counter (receptacle_4, receptacle_18, receptacle_19) holds mugs, a cutting board, and a knife that get used in the morning and evening. The bathroom (receptacle_6, receptacle_22) holds toiletries that never move.

What sets this hypothesis apart: object_2 and object_35 are OUT_OF_HOUSE on weekdays 08:00–18:00. The kitchen objects (class_4: object_4, object_5) cycle to the counter (receptacle_4) in the morning and return to their shelves by evening. What would refute it: object_2 or object_35 sighted in the house between 09:00 and 17:00 on a weekday, or the kitchen objects found at receptacle_4 during midday weekdays.

```json
{"claims": [
   {"claim": "object_2 (keys) is out of the house with the resident on weekday mornings",
    "target": "object_2", "expect": "receptacle_2", "days": "weekday", "from": 8, "to": 18},
   {"claim": "object_35 (bag) is out of the house on weekdays during work hours",
    "target": "object_35", "expect": "receptacle_2", "days": "weekday", "from": 8, "to": 18},
   {"claim": "object_4 (kitchen item) is on the kitchen counter in the morning",
    "target": "object_4", "expect": "receptacle_4", "days": "both", "from": 6, "to": 9},
   {"claim": "object_13 (bathroom item) stays at the bathroom sink all week",
    "target": "object_13", "expect": "receptacle_6", "days": "both", "from": 0, "to": 24}
 ],
 "targets": {
   "object_2": [
     {"days": "weekday", "from": 8, "to": 18, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_35": [
     {"days": "weekday", "from": 8, "to": 18, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_4": [
     {"days": "both", "from": 6, "to": 9, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ],
   "object_13": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_6", "chance": "almost_always"}
   ]
 }
}
```
