# p_5c1b — Receptacle_19 is the morning-and-evening parking shelf for a cluster of objects

Seven objects—object_5, object_6, object_7, object_9, object_10, object_12, and object_23—are "mostly" at receptacle_19 in the per-object statistics, yet weekday 09:00–17:00 looks at receptacle_19 find most of them absent (object_7: 0 found / 4 empty; object_10: 0 found / 4 empty; object_6: 1 found / 3 empty; object_9: 1 found / 3 empty; object_12: 1 found / 3 empty; object_23: 1 found / 3 empty). The pattern is consistent: these items are stored at receptacle_19 (a large multi-shelf unit in the hallway or living room) in the morning before 09:00, in the evening after 17:00, and all weekend. During weekday 09:00–17:00 the residents take them out for use—object_5 and object_9 to the desk area, object_6 and object_12 to the living room, object_7 to the living room (confirmed by a day-2 18:00 sighting at receptacle_10), object_10 to the bedroom, object_23 to the desk.

The rest of the house follows the standard home-based couple routine: object_4 on the kitchen shelf, object_15 and object_16 on the counter, object_2 and object_35 at the entryway shelf, bathroom items at receptacle_6, bedroom items at receptacle_8 and receptacle_13. Nothing leaves the house.

What sets this apart: it gives a single unified explanation for why seven objects are "mostly" at receptacle_19 yet absent there during weekday work hours. What would refute it: object_6 or object_9 found at receptacle_19 during weekday 09:00–17:00 on two or more occasions, or object_7 found at receptacle_19 during weekday 09:00–17:00.

```json
{
 "claims": [
  {
   "claim": "object_7 (small tool) is in the living room (receptacle_10) during weekday work hours, not at the storage shelf",
   "target": "object_7",
   "expect": "receptacle_10",
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
