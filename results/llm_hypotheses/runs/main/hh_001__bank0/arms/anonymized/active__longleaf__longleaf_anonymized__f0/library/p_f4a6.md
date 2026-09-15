# p_f4a6 — Multi-generational: grandparents and a visiting grandchild

Two elderly adults (grandparents) and one young grandchild (age 5) live here temporarily. The grandchild stays on weekdays (the parents work) and leaves on Friday afternoons. The walkthrough at 15:08 on a Monday caught the home with the grandchild present (nap time) and the grandparents in the living room. The grandchild's items (class_16, class_22) are in the living room (receptacle_10) and bedroom (receptacle_8, receptacle_13) on weekdays but GONE on weekends (the child goes back to the parents). The grandparents' items (class_2, class_32, class_3) stay in the house always. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used for the grandchild's meals (07:00–08:00, 12:00–13:00, 17:00–18:00). The bathroom (receptacle_6, receptacle_22) is used for the grandchild's toileting.

What sets this apart: on weekends, object_17 (class_16) and object_25 (class_22) are OUT_OF_HOUSE (the grandchild has left). On weekdays, they are in the house. The grandparents' keys (object_2) never leave. The kitchen objects (class_4) are at receptacle_4 during the grandchild's meal times (three windows). What would refute it: object_17 or object_25 found in the house on a Saturday, or object_2 found OUT_OF_HOUSE at any time.

```json
{"claims": [
   {"claim": "object_17 (grandchild item) is out of the house on weekends when the child leaves",
    "target": "object_17", "expect": "receptacle_2", "days": "weekend", "from": 0, "to": 24},
   {"claim": "object_25 (grandchild item) is out of the house on weekends",
    "target": "object_25", "expect": "receptacle_2", "days": "weekend", "from": 0, "to": 24},
   {"claim": "object_2 (grandparent keys) is always in the house",
    "target": "object_2", "expect": "receptacle_11", "days": "both", "from": 0, "to": 24},
   {"claim": "object_4 (kitchen item) is on the counter during the grandchild's lunch",
    "target": "object_4", "expect": "receptacle_4", "days": "weekday", "from": 12, "to": 13}
 ],
 "targets": {
   "object_17": [
     {"days": "weekend", "from": 0, "to": 24, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "weekday", "from": 0, "to": 24, "at": "receptacle_10", "chance": "usually"}
   ],
   "object_25": [
     {"days": "weekend", "from": 0, "to": 24, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "weekday", "from": 0, "to": 24, "at": "receptacle_8", "chance": "usually"}
   ],
   "object_2": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "almost_always"}
   ],
   "object_4": [
     {"days": "weekday", "from": 7, "to": 8, "at": "receptacle_4", "chance": "usually"},
     {"days": "weekday", "from": 12, "to": 13, "at": "receptacle_4", "chance": "usually"},
     {"days": "weekday", "from": 17, "to": 18, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ]
 }
}
```
