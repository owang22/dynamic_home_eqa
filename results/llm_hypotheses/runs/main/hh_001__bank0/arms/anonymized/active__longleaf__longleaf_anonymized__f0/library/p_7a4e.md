# p_7a4e — Storage-shelf split: object_5 stays, object_6 and object_7 leave during work hours

The storage-shelf cluster at receptacle_19 is not uniform. Object_5 is at receptacle_19 on 15/22 sighted days, with weekday 9-17h looks finding it there 10 of 15 times, and multiple documents' blocks holding at 0.86 on 76 sightings. It is a true storage-shelf resident. But object_6 (14/21 days at receptacle_19) and object_7 (13/19 days) show weekday 9-17h looks finding them there only 2 of 15 times each. They are NOT at the storage shelf during work hours.

The commuting documents (p_d6c3, p_a3f7, p_1c5e) claim object_6 and object_7 leave the house (receptacle_2) during work hours. Their claims show "for 0, against 3, weak for 13" — the 13 empty looks at receptacle_19 are consistent with the objects being elsewhere, but the 3 in-house sightings rule out consistent absence. The mixture's worst-objects report caught object_7 at receptacle_10 (living room) on day 17 at 19:00. I hypothesize that object_6 and object_7 are at the living room (receptacle_10) during the weekday work stretch, not out of the house. They return to the storage shelf in the evening and on weekends.

This document is distinct from the commuting documents in that nothing leaves the house. It is distinct from p_f4a9 and p_8e1c in that it explicitly splits the storage-shelf cluster. What would refute it: object_5 sighted anywhere other than receptacle_19 during weekday 9-17h; object_6 or object_7 sighted at receptacle_19 during weekday 10:00–15:00 on two or more occasions.

```json
{
 "claims": [
  {
   "claim": "object_5 (storage item) is at the storage shelf (receptacle_19) during weekday work hours 9-17h",
   "target": "object_5",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_7 (small tool) is at the living room (receptacle_10) during weekday work hours 9-17h, not at the storage shelf",
   "target": "object_7",
   "expect": "receptacle_10",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_6 (storage item) is at the living room (receptacle_10) during weekday work hours 9-17h, not at the storage shelf",
   "target": "object_6",
   "expect": "receptacle_10",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_7 (small tool) is back at the storage shelf (receptacle_19) on weekends during the day 8-20h",
   "target": "object_7",
   "expect": "receptacle_19",
   "days": "weekend",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "object_5": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_6": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_10",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_7": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_10",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_9": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_12": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_23": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
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
  ]
 }
}
```
