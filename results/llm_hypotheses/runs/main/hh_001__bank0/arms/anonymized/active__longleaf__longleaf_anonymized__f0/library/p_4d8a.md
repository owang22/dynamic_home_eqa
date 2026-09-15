# p_4d8a — object_11 is a bedroom appliance; parked at receptacle_8 during weekday work and evening hours

Object_11 (class_10) is mostly seen at receptacle_18 (13/18 sighted days), but weekday 9-17h looks at receptacle_18 found it only 1 time while 13 looks found nothing. The mixture's worst-objects report since the last call caught object_11 at receptacle_8 three times (day 22, 22:00). The competing documents that tried to explain this gap all failed: p_e4b7 placed it at receptacle_13 (1 for, 40 against), p_3a7d at receptacle_4 (0 for, 18 against), and p_d6c3 claimed it was out of the house (0 for, 1 against, 13 weak for). The consistent pattern is that object_11 leaves receptacle_18 during the weekday work stretch and reappears at receptacle_8 in the evening.

This document hypothesizes that object_11 is a small personal appliance (perhaps a hair dryer, electric shaver, or compact massager) that is stored in the kitchen area (receptacle_18) on weekends and weekday mornings before the resident leaves for work, but is moved to the bedroom shelf (receptacle_8) during the work day when the resident uses it at the desk or in the bedroom, and remains there through the evening. It is NOT carried out of the house; the 13 empty looks at receptacle_18 during work hours are explained by its presence at receptacle_8, not by absence from the home.

This document is distinct from p_e4b7 (which wrongly places it at receptacle_13) and p_d6c3 (which claims it leaves the house). It also differs from p_3a7d (which places it at the counter). The keys (object_2) remain at receptacle_11 24/7 as in most documents.

What would refute this document: object_11 sighted at receptacle_18 during weekday 10:00-15:00 on two or more occasions; object_11 sighted out of the house (receptacle_2) at any time.

```json
{
 "claims": [
  {
   "claim": "object_11 (class_10 appliance) is at the bedroom shelf (receptacle_8) during weekday work hours 9-17h, not at receptacle_18",
   "target": "object_11",
   "expect": "receptacle_8",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_11 (class_10 appliance) is at the bedroom shelf (receptacle_8) during the evening 18-23h",
   "target": "object_11",
   "expect": "receptacle_8",
   "days": "both",
   "from": 18,
   "to": 23
  },
  {
   "claim": "object_11 (class_10 appliance) is at receptacle_18 on weekends during the day 8-18h, not at receptacle_8",
   "target": "object_11",
   "expect": "receptacle_18",
   "days": "weekend",
   "from": 8,
   "to": 18
  }
 ],
 "targets": {
  "object_11": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_18",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 23,
    "at": "receptacle_8",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 18,
    "at": "receptacle_18",
    "chance": "usually"
   }
  ],
  "object_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_4": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_18",
    "chance": "almost_always"
   }
  ],
  "object_15": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_4",
    "chance": "usually"
   }
  ],
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
    "chance": "almost_always"
   }
  ],
  "object_34": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
    "chance": "almost_always"
   }
  ]
 }
}
```
