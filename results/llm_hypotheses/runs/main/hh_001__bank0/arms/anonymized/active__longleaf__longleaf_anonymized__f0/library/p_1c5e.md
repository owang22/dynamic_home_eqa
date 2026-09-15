# p_1c5e — Storage-shelf cluster; object_7 and object_10 travel out on weekdays (fork of p_5c1b)

This fork corrects two failing weekday predictions from the parent p_5c1b. The parent placed object_7 at receptacle_10 (living room) and object_10 at receptacle_8 (bedroom) during weekday 09:00–17:00, but both claims have scored 0-for / 6-against. The per-object data is unambiguous: object_7 was found at receptacle_19 on 6/7 sighted days overall yet 0/7 times during weekday 9-17h looks at that shelf; object_10 was found at receptacle_17 on only 3/6 days and 0/4 times during weekday 9-17h looks. Neither object is in the house at its predicted weekday location.

The revised model: object_7 (a small tool or instrument) and object_10 (a personal item) are taken out of the house by the commuting resident during weekday work hours (receptacle_2). They return to their home receptacles in the evening and on weekends. Object_7's home is the storage shelf (receptacle_19); object_10's home is receptacle_17 (a secondary shelf or closet). The weekend parking-shelf pattern for object_6 at receptacle_19 is retained (it held at 0.96). The kitchen and entryway routines are unchanged.

What changed from p_5c1b: object_7's weekday 9-17h block now targets receptacle_2 instead of receptacle_10; object_10's weekday 9-17h block now targets receptacle_2 instead of receptacle_8. The object_7 and object_10 claims now expect receptacle_2. What would refute this fork: object_7 or object_10 sighted anywhere in the house during weekday 10:00–16:00 on two or more occasions.

_(targets the fork left unstated are inherited from p_5c1b)_

```json
{
 "claims": [
  {
   "claim": "object_7 (small tool) is out of the house during weekday work hours, taken by the commuting resident",
   "target": "object_7",
   "expect": "receptacle_2",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_10 (personal item) is out of the house during weekday work hours, taken by the commuting resident",
   "target": "object_10",
   "expect": "receptacle_2",
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
    "at": "receptacle_2",
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
    "at": "receptacle_2",
    "chance": "usually"
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
    "at": "receptacle_2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_17",
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
  ],
  "object_14": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_24": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_28": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ]
 }
}
```
