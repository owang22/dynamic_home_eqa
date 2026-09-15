# p_7d2b — Storage-shelf cluster: object_23, object_12, object_5 anchored at receptacle_19

The mixture has been repeatedly misplacing object_23: three consecutive looks (e.g. day 12, 07:00) predicted receptacle_21 but found it at receptacle_19. No document in the current library specifically targets object_23, so it falls through to the statistical model, which is being pulled toward receptacle_21 by other objects. The per-object data is clear: object_23 is mostly at receptacle_19 (8/15 sighted days, 44 sightings, 4 distinct receptacles). During weekday 09:00–17:00 looks at receptacle_19, it was found 3 times and not found 8 times, suggesting it is at the shelf about a third of the time during the work stretch but is there more often in the early morning and evening.

This document anchors the storage-shelf cluster: object_23, object_12 (12/14 days at receptacle_19, 0.92 block-hold), object_5 (12/15 days, 0.89 block-hold), and object_9 (11/14 days) all live at receptacle_19 as their primary home. object_12 and object_5 are "usually" there; object_23 is "sometimes" because it wanders more (4 receptacles vs. 3 for object_12). object_9 is "sometimes" as well (4 receptacles).

This document is distinct from p_5c1b and p_7f3a in that it specifically calls out object_23, which those documents do not target, and from p_b8e2 in that it does not assign object_20 to receptacle_19 as a default (p_b8e2 does, but object_20 is only at receptacle_19 on 6/15 days). What would refute this document: object_23 found at receptacle_21 on more than 60% of sighted days over the next week, or object_12 found away from receptacle_19 during 09:00–17:00 on more than 40% of weekday looks.

```json
{
 "claims": [
  {
   "claim": "object_23 (storage item) is at the storage shelf (receptacle_19) during weekday morning hours 6-10h",
   "target": "object_23",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 6,
   "to": 10
  },
  {
   "claim": "object_12 (storage item) is at the storage shelf (receptacle_19) during weekday work hours",
   "target": "object_12",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_5 (storage item) is at the storage shelf (receptacle_19) during weekday work hours",
   "target": "object_5",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_9 (storage item) is at the storage shelf (receptacle_19) during weekday work hours",
   "target": "object_9",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "object_23": [
   {
    "days": "both",
    "from": 6,
    "to": 10,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 16,
    "to": 22,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "sometimes"
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
  "object_5": [
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
    "chance": "sometimes"
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
  ]
 }
}
```
