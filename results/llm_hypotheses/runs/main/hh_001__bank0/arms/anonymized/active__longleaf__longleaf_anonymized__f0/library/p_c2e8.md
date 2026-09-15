# p_c2e8 — Desk-shelf swap: object_28 moved to the desk, object_21 moved to the storage shelf

The mixture's worst-objects list since the last call reveals a consistent swap: object_28 (class_25) was predicted at receptacle_10 (living room) but found at receptacle_12 (desk) five times, most recently day 5 at 13:00. Meanwhile object_21 (class_19) was predicted at receptacle_12 (desk) but found at receptacle_19 (storage shelf) three times, most recently day 6 at 09:00. The per-object statistics confirm the shift: object_28 is now at 3 distinct receptacles with receptacle_12 appearing prominently in recent sightings, and object_21 has 4 distinct receptacles with receptacle_19 as a recent location.

This document posits that a reorganization occurred around day 4–5: the residents moved object_28 from the living room to the shared desk (perhaps it is a desk accessory or reference item they now keep at hand), and moved object_21 from the desk to the storage shelf (perhaps it is a project item no longer in active use). The rest of the house follows the standard home-based couple routine: object_4 on the kitchen shelf, object_15 and object_16 on the counter, object_2 and object_35 at the entryway, bathroom items at receptacle_6. Nothing leaves the house.

What sets this apart: it is the only document that places object_28 at receptacle_12 and object_21 at receptacle_19 as their primary daytime locations. What would refute it: object_28 found at receptacle_10 on two or more occasions during weekday 09:00–17:00, or object_21 found at receptacle_12 on two or more occasions during weekday 09:00–17:00.

```json
{
 "claims": [
  {
   "claim": "object_28 (living room item) is now at the shared desk (receptacle_12) during weekday work hours",
   "target": "object_28",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_21 (desk item) is now at the storage shelf (receptacle_19) during weekday work hours",
   "target": "object_21",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_4 (kitchen item) is on the kitchen shelf (receptacle_18) all day",
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
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_21": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_7": [
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
