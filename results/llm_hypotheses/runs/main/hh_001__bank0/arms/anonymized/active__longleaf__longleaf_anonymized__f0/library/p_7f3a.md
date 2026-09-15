# p_7f3a — Receptacle_19 parking shelf; object_7 at the desk during work (fork of p_5c1b)

This fork corrects the weekday work-hours location of object_7. The parent p_5c1b placed object_7 in the living room (receptacle_10) during weekday 09:00–17:00, but the claim has now gone against twice with zero for-scores since the last call. The per-object statistics confirm: object_7 was found at receptacle_19 zero times during weekday 9–17h looks (5 empty), so it is out of the storage shelf, but it is also not in the living room. Given that object_7 is a small tool (class_6) and the residents work from home at the shared desk (receptacle_12), the more natural location during work hours is the desk, where small tools and accessories are kept within reach. The rest of the model is unchanged: the seven-object cluster parks at receptacle_19 outside work hours, kitchen and bathroom routines are standard, and nothing leaves the house.

What changed from p_5c1b: object_7's weekday 09:00–17:00 block moves from receptacle_10 to receptacle_12; the corresponding claim is updated. What would refute this fork: object_7 found at receptacle_10 during weekday 09:00–17:00 on two or more occasions, or object_7 found at receptacle_19 during weekday 09:00–17:00.

```json
{
 "claims": [
  {
   "claim": "object_7 (small tool) is at the shared desk (receptacle_12) during weekday work hours, not at the storage shelf or living room",
   "target": "object_7",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_10 (personal item) is out of the storage shelf (receptacle_19) during weekday work hours",
   "target": "object_10",
   "expect": "receptacle_8",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_6 (storage item) is at the storage shelf (receptacle_19) on weekends during the day",
   "target": "object_6",
   "expect": "receptacle_19",
   "days": "weekend",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_4 (kitchen item) is on the kitchen shelf (receptacle_18) all day",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "object_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_35": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_3": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_7",
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
  "object_5": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_12",
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
    "at": "receptacle_12",
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
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_12",
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
  "object_10": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_8",
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
  "object_12": [
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
  "object_23": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_21",
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
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
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
  "object_16": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_4",
    "chance": "usually"
   }
  ],
  "object_26": [
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ]
 }
}
```
