# p_9d4b — object_33 is a kitchen-counter item, not a desk item

The mixture has been misplacing object_33 (class_31) at the desk (receptacle_12) or the entryway (receptacle_11), but recent sightings find it at the kitchen counter (receptacle_4) three times, most recently day 7 at 04:00. The per-object statistics show object_33 is at 4 distinct receptacles and was only at receptacle_12 on 2 of 8 sighted days — a weak association. During weekday 09:00–17:00, looks at receptacle_12 found object_33 zero times (5 empty), confirming it is not a desk item. The kitchen counter (receptacle_4) is where object_15 and object_16 live, and object_33 appears to belong there as well — perhaps a small kitchen tool or container used during meal prep.

This document places object_33 at receptacle_4 (the active counter) during waking hours, consistent with the other kitchen items. The rest of the house follows the standard home-based couple routine. Nothing leaves the house.

What sets this apart: it is the only document that places object_33 at receptacle_4 as its primary location. What would refute it: object_33 found at receptacle_12 on two or more occasions during weekday 09:00–17:00, or object_33 found at receptacle_11 on two or more occasions.

```json
{
 "claims": [
  {
   "claim": "object_33 (kitchen item) is at the active counter (receptacle_4) during weekday work hours",
   "target": "object_33",
   "expect": "receptacle_4",
   "days": "weekday",
   "from": 7,
   "to": 21
  },
  {
   "claim": "object_15 (kitchen item) is on the active counter (receptacle_4) during the day",
   "target": "object_15",
   "expect": "receptacle_4",
   "days": "both",
   "from": 7,
   "to": 21
  },
  {
   "claim": "object_4 (kitchen item) is on the kitchen shelf (receptacle_18) all day, not the counter",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_2 (keys) is always in the house because both residents work from home",
   "target": "object_2",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
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
  "object_33": [
   {
    "days": "both",
    "from": 6,
    "to": 22,
    "at": "receptacle_4",
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
  "object_17": [
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
  ],
  "object_21": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
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
