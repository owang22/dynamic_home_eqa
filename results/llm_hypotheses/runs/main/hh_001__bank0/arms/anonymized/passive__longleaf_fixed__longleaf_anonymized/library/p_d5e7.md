# p_d5e7 — Couple, one works weekends (hospital); the house is busy on weekends, quiet on weekdays

A couple lives here. Partner A works weekends (Fri 16:00 – Sun 16:00) at a hospital. Partner B works weekdays (Mon-Fri 08:00–16:00) at an office. The walkthrough at 15:08 on a Monday caught Partner B at the office and Partner A at home (off shift, resting). The pattern is INVERTED from typical: on weekends, Partner A is out (hospital) and the house is empty; on weekdays, Partner B is out and the house is half-empty. The keys (class_2) go with Partner B on weekdays 08:00–16:00. The bag (class_32) goes with Partner A on weekends (Fri 16:00 – Sun 16:00). The kitchen (receptacle_4, receptacle_18, receptacle_19) is used for meals on both day types but at different times.

What sets this apart: on weekends, object_35 (bag) is OUT_OF_HOUSE from Friday 16:00 to Sunday 16:00 (Partner A's hospital shift). On weekdays, object_2 (keys) is OUT_OF_HOUSE 08:00–16:00 (Partner B's office). The two objects are NEVER out at the same time. The kitchen objects (class_4) are at receptacle_4 on weekday mornings (Partner A is home) and weekend evenings (Partner B is home). What would refute it: object_35 found in the house on a Saturday at 12:00, or object_2 found OUT_OF_HOUSE on a Saturday.

```json
{"claims": [
   {"claim": "object_35 (bag) is out of the house on weekends during Partner A's hospital shift",
    "target": "object_35", "expect": "receptacle_2", "days": "weekend", "from": 0, "to": 16},
   {"claim": "object_2 (keys) is out of the house on weekdays during Partner B's office hours",
    "target": "object_2", "expect": "receptacle_2", "days": "weekday", "from": 8, "to": 16},
   {"claim": "object_4 (kitchen item) is on the counter on weekday mornings when Partner A is home",
    "target": "object_4", "expect": "receptacle_4", "days": "weekday", "from": 7, "to": 10},
   {"claim": "object_4 (kitchen item) is on the counter on weekend evenings when Partner B is home",
    "target": "object_4", "expect": "receptacle_4", "days": "weekend", "from": 16, "to": 20}
 ],
 "targets": {
   "object_35": [
     {"days": "weekend", "from": 0, "to": 16, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_2": [
     {"days": "weekday", "from": 8, "to": 16, "at": "receptacle_2", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "usually"}
   ],
   "object_4": [
     {"days": "weekday", "from": 7, "to": 10, "at": "receptacle_4", "chance": "usually"},
     {"days": "weekend", "from": 16, "to": 20, "at": "receptacle_4", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ]
 }
}
```
