# p_b8e2 — Daily desk cycle: storage-shelf items pulled to the desk at 07:00, parked back at 15:00

Two residents work from home at the shared desk (receptacle_12) on weekdays. Their routine is a tight daily cycle: in the early morning (06:00–08:00) they gather working materials from the storage shelf (receptacle_19) and the kitchen counter (receptacle_4) and lay them out at the desk. The work stretch runs roughly 08:00–15:00. At 15:00 the session ends and the items are returned: desk items go back to the storage shelf, kitchen items go back to the counter.

The objects in this cycle: object_17 (a desk item, mostly at receptacle_12 but sighted at receptacle_19 on day 9 at 06:00), object_20 (a storage item, mostly at receptacle_19 but sighted at receptacle_12 on day 11 at 08:00 twice), object_21 (a desk item, mostly at receptacle_12, sighted at receptacle_12 on day 9 at 06:00 when the mixture expected receptacle_19), and object_16 (a kitchen item, mostly at receptacle_4 but sighted at receptacle_12 on day 11 at 07:00 three times).

This document is distinct from p_d6c3 and p_a3f7 in that it treats the desk cycle as the primary daily structure rather than a secondary detail. It also covers object_17, which no other live document places at receptacle_19 in the early morning. The "blocks that failed" list shows object_17 at receptacle_8 failing across ten documents (0.17 on 26 sightings), confirming it is NOT at receptacle_8. Its true home is receptacle_12 during the day, with a nightly/early-morning park at receptacle_19.

What would refute this document: object_20 or object_17 sighted at receptacle_19 during weekday 08:00–14:00 (the active work stretch) on two or more occasions; object_16 sighted at receptacle_4 during weekday 07:00–08:00 on two or more occasions.

```json
{
 "claims": [
  {
   "claim": "object_20 (storage item) is at the shared desk (receptacle_12) during weekday morning setup 7-9h",
   "target": "object_20",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "object_17 (desk item) is at the storage shelf (receptacle_19) during weekday early morning before the desk is set up",
   "target": "object_17",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 5,
   "to": 8
  },
  {
   "claim": "object_16 (kitchen item) is at the shared desk (receptacle_12) during weekday early morning 7-9h",
   "target": "object_16",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "object_21 (desk item) is at the shared desk (receptacle_12) during weekday early morning 6-8h",
   "target": "object_21",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 6,
   "to": 8
  }
 ],
 "targets": {
  "object_17": [
   {
    "days": "weekday",
    "from": 5,
    "to": 8,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 22,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 5,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_20": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "receptacle_12",
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
  "object_21": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
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
