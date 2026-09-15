# p_c4d1 — Storage-shelf cluster; only object_7 travels out, object_10 stays in-house (fork of p_1c5e)

This fork corrects p_1c5e's claim that object_10 goes out of the house with the commuter. The evidence against this is now clear: object_10 was sighted at receptacle_8 (a bedroom or secondary shelf) on day 8 at 19:00, twice, when the mixture expected it at receptacle_17. An object that is out of the house (receptacle_2) cannot be sighted at receptacle_8 in the evening. Furthermore, object_10's per-object data shows it at receptacle_17 on only 4/9 sighted days across 5 different receptacles, and weekday 9-17h looks at receptacle_17 found it only 1 time versus 4 empty. It is in the house but roams between receptacle_17 (its daytime home) and receptacle_8 (its evening/night location).

What changed from p_1c5e: object_10's weekday 9-17h block now targets receptacle_17 (chance "sometimes") instead of receptacle_2; a new evening block places it at receptacle_8 from 18:00 to 24:00. The object_10 claim now expects receptacle_17 during weekday work hours. Object_7's out-of-house block is retained unchanged—the 9/11 empty looks at receptacle_19 during weekday 9-17h remain strong evidence for absence. Object_6's block is also retained but its chance is lowered to "sometimes" given the 2 against sightings.

What would refute this fork: object_10 sighted at receptacle_2 (out of house) at any time; object_7 sighted anywhere in the house during weekday 10:00–16:00 on three or more occasions.

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
   "claim": "object_10 (personal item) is at the secondary shelf (receptacle_17) during weekday work hours, not out of the house",
   "target": "object_10",
   "expect": "receptacle_17",
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
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "receptacle_8",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_17",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "receptacle_12",
    "chance": "sometimes"
   },
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
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "receptacle_19",
    "chance": "usually"
   },
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
