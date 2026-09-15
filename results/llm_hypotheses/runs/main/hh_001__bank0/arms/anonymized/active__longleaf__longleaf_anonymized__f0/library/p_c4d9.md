# p_c4d9 — Family of four; school run chaos, evening kitchen marathon

Two parents and two school-age children live here. The walkthrough at 15:08 on a Monday caught the home in its mid-afternoon lull: kids are at school (back by 15:30), parents are at work (back by 17:30). The entryway (receptacle_7) is a magnet for shoes, backpacks, and coats that get dumped and forgotten. The kitchen (receptacle_4, receptacle_18, receptacle_19) is the family hub: the cutting board (class_4) lives on the counter from 16:00 to 21:00 during dinner prep. The children's items (class_16, class_22) scatter between the bedroom (receptacle_8, receptacle_13) and the living room (receptacle_10) throughout the day. The bathroom (receptacle_6, receptacle_22) sees heavy morning use (06:00–08:00) and evening use (20:00–22:00).

What sets this apart: on weekday mornings 06:30–08:00, the kitchen counter (receptacle_4) is crowded with class_4 objects AND the bathroom (receptacle_6) is in active use. On weekends, the living room (receptacle_10) objects shift to the kitchen for family meals. What would refute it: the bathroom objects (class_12, class_24, class_28) found anywhere other than receptacle_6, or the kitchen objects at receptacle_18 during dinner hours on a weekday.

```json
{"claims": [
   {"claim": "object_4 (cutting board) is on the kitchen counter during dinner prep on weekdays",
    "target": "object_4", "expect": "receptacle_4", "days": "weekday", "from": 16, "to": 21},
   {"claim": "object_13 (bathroom item) is at the bathroom sink during the morning rush",
    "target": "object_13", "expect": "receptacle_6", "days": "weekday", "from": 6, "to": 8},
   {"claim": "object_3 (entryway item) is at the entryway when the family is home in the evening",
    "target": "object_3", "expect": "receptacle_7", "days": "both", "from": 18, "to": 22},
   {"claim": "object_26 (living room item) moves to the kitchen on weekends for family meals",
    "target": "object_26", "expect": "receptacle_4", "days": "weekend", "from": 11, "to": 20}
 ],
 "targets": {
   "object_4": [
     {"days": "weekday", "from": 16, "to": 21, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ],
   "object_13": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_6", "chance": "almost_always"}
   ],
   "object_3": [
     {"days": "both", "from": 18, "to": 22, "at": "receptacle_7", "chance": "usually"},
     {"days": "weekday", "from": 8, "to": 17, "at": "receptacle_2", "chance": "sometimes"}
   ],
   "object_26": [
     {"days": "weekend", "from": 11, "to": 20, "at": "receptacle_4", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_10", "chance": "usually"}
   ]
 }
}
```
