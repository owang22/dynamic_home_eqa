# p_d3e5 — Business traveler; the house is empty for 2-3 days a week

One adult is a sales professional who travels for work 2-3 days per week. The walkthrough at 15:08 on a Monday caught the home empty (the resident is on a business trip or at the airport). On travel days (typically Tuesday-Thursday), the keys (class_2), bag (class_32), and laptop (class_13) are OUT_OF_HOUSE for the entire day. On non-travel days (Friday, Saturday, Sunday, Monday), the resident is home and the objects are in their normal places. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used for quick meals on non-travel days. The desk (receptacle_12, receptacle_21) is used on non-travel days for email catch-up.

What sets this apart: on Tue/Wed/Thu, object_2, object_35, AND object_14 are ALL out of the house for the full day. On Fri/Sat/Sun/Mon, they are all in the house. The pattern is binary: either the resident is home all day or gone all day. What would refute it: object_2 found in the house on a Wednesday afternoon, or object_14 found OUT_OF_HOUSE on a Saturday.

```json
{"claims": [
   {"claim": "object_2 (keys) is out of the house on business travel days (Tue-Thu)",
    "target": "object_2", "expect": "receptacle_2", "days": "weekday", "from": 7, "to": 22},
   {"claim": "object_35 (bag) is out of the house on business travel days",
    "target": "object_35", "expect": "receptacle_2", "days": "weekday", "from": 7, "to": 22},
   {"claim": "object_14 (laptop) is out of the house on business travel days",
    "target": "object_14", "expect": "receptacle_2", "days": "weekday", "from": 7, "to": 22},
   {"claim": "object_2 (keys) is in the house on weekends",
    "target": "object_2", "expect": "receptacle_11", "days": "weekend", "from": 0, "to": 24}
 ],
 "targets": {
   "object_2": [
     {"days": "weekday", "from": 7, "to": 22, "at": "receptacle_2", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_35": [
     {"days": "weekday", "from": 7, "to": 22, "at": "receptacle_2", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_14": [
     {"days": "weekday", "from": 7, "to": 22, "at": "receptacle_2", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_12", "chance": "usually"}
   ]
 }
}
```
