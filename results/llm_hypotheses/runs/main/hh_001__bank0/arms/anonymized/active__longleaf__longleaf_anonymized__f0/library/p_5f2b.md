# p_5f2b — object_1 shuttles between receptacle_17 (morning/evening) and the desk (work hours)

Object_1 (class_1) is at receptacle_17 on 12 of 19 sighted days, but weekday 9-17h looks at receptacle_17 found it 0 times and found nothing 12 times. This is a clean split: during the work-day stretch it is NOT at receptacle_17. The mixture's worst-objects report caught it at receptacle_17 at 06:00 (day 18), confirming the early-morning presence. With 3 distinct receptacles and 43 sightings, the most parsimonious reading is a two-location shuttle: receptacle_17 in the early morning and evening, and the shared desk (receptacle_12) during the weekday work stretch when the residents are at the desk.

This document is distinct from p_e9a4, which places object_1 at receptacle_8 (bedroom shelf) during weekday 14-18h (for 3, against 4 — weak). I instead place it at the desk, consistent with the residents' work routine. It is also distinct from the stable-anchor documents (p_e8b2) which do not cover object_1's movement.

What would refute it: object_1 sighted at receptacle_17 during weekday 10:00–15:00 on two or more occasions; object_1 sighted at receptacle_12 during 02:00–05:00.

```json
{
 "claims": [
  {
   "claim": "object_1 (class_1 item) is at receptacle_17 during the early morning 4-7h, not at the desk",
   "target": "object_1",
   "expect": "receptacle_17",
   "days": "weekday",
   "from": 4,
   "to": 7
  },
  {
   "claim": "object_1 (class_1 item) is at the shared desk (receptacle_12) during weekday work hours 9-16h, not at receptacle_17",
   "target": "object_1",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "object_1 (class_1 item) is at receptacle_17 during the evening 18-22h, not at the desk",
   "target": "object_1",
   "expect": "receptacle_17",
   "days": "both",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "object_1": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "receptacle_17",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 17,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "receptacle_17",
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
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
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
  "object_29": [
   {
    "days": "both",
    "from": 6,
    "to": 22,
    "at": "receptacle_22",
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
